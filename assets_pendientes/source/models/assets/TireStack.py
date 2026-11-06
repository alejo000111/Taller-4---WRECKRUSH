import numpy as np

from wr3d import Asset, Material, T, R, S, compose, register
from wr3d import shapes as sh
from wr3d.materials import Surface, rgb, grime_amount
from wr3d.noise import smoothstep
from _destructible import destructible, collider

YELLOW = (255, 210, 31)
RUBBER = (34, 34, 38)
TIRE_H = 1.15
OUTER = 2.3
SEGMENTS = 20

PROFILE = [
    (1.28, 0.12), (1.70, 0.02), (2.08, 0.03), (2.26, 0.18), (2.30, 0.575), (2.26, 0.97),
    (2.08, 1.12), (1.70, 1.13), (1.28, 1.03), (1.20, 0.82), (1.20, 0.33),
]

RIM = [(0.0, 0.40), (1.18, 0.40), (1.22, 0.92), (1.12, 0.95), (1.02, 0.66), (0.44, 0.62), (0.36, 0.75), (0.0, 0.77)]


def profile_v(profile, closed):
    pts = np.asarray(profile, dtype=np.float64)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(seg)])
    total = arc[-1] + (np.linalg.norm(pts[0] - pts[-1]) if closed else 0.0)
    return total - arc


TIRE_V = profile_v(PROFILE, True)
RIM_V = profile_v(RIM, False)
RING = 2 * np.pi * OUTER
FRONT_U = np.pi / 2 * OUTER


@register("tirestack_rubber")
def tire_rubber(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", RUBBER))
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    t0, t1 = p["tread"]
    band = smoothstep(t0 - 0.02, t0 + 0.04, v) * (1 - smoothstep(t1 - 0.04, t1 + 0.02, v))
    lane = (v - t0) / (t1 - t0)
    pitch = p.get("pitch", 0.46)
    side = (lane > 0.5).astype(np.float64)
    phase = (u / pitch + 0.5 * side) % 1.0
    lateral = 1 - smoothstep(0.035, 0.06, np.abs(phase - 0.5) * pitch)
    zig = 0.05 * (np.abs(((u / pitch) % 1.0) - 0.5) * 4 - 1)
    center = 1 - smoothstep(0.035, 0.06, np.abs((lane - 0.5) * (t1 - t0) - zig))
    groove = np.maximum(lateral * (np.abs(lane - 0.5) > 0.06), center) * band
    ribs = (0.5 + 0.5 * np.sin(v * 70.0)) * (1 - band) * smoothstep(0.3, 0.6, np.abs(ctx.N[:, 1]))
    var = ctx.noise(5.0, 3, 41)
    worn = smoothstep(0.3, 1.0, np.clip(ctx.E, 0, 1)) * 0.35 + band * (1 - groove) * 0.12
    tone = 0.92 + 0.1 * var + worn * 0.6 - groove * 0.45 - ribs * 0.05
    s.base = np.clip(color[None, :] * tone[:, None], 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.86 - worn * 0.3 + groove * 0.08 + 0.05 * var, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = band * (1 - groove) * 0.022 + ribs * 0.0012 + var * 0.0005
    low = 1 - smoothstep(0.0, p.get("mud", 1.7), ctx.P[:, 1])
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.4)) + low * 0.5 + groove * 0.25, 0, 0.85)
    return s


def tire_material(decals, dirt=0.4, mud=1.7):
    return Material("tirestack_rubber", tread=(TIRE_V[5], TIRE_V[3]), decals=decals, dirt=dirt, mud=mud, dirt_color=(92, 80, 64), gradient=0.08, highlight=0.35)


def ring_stripe(v, width, wear=0.45):
    return {"type": "rect", "center": (RING / 2, v), "size": (RING + 0.4, width), "color": YELLOW, "wear": wear, "rough": 0.6}


def tread_v(t):
    return TIRE_V[5] + (TIRE_V[3] - TIRE_V[5]) * t


def side_v(t):
    return TIRE_V[8] + (TIRE_V[6] - TIRE_V[8]) * t


def tire(mat, scale=1.0):
    mesh = sh.lathe(PROFILE, SEGMENTS, mat, closed=True, smooth_angle=60, r_ref=OUTER, start=7)
    return mesh.transformed(S(scale, 1.0, scale))


def rim(mat):
    return sh.lathe(RIM, 12, mat, smooth_angle=35, start=7)


def build():
    a = Asset("TireStack", budget=2000, atlas=512, ao_radius=0.45, edge_width=0.04, preview_radius=3.6,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")

    bottom = tire_material([
        ring_stripe(side_v(0.82), 0.08, 0.55),
        {"type": "text", "text": "SCRAP", "center": (FRONT_U - 0.6, tread_v(0.5)), "height": 0.34, "color": YELLOW, "font": "impact", "wear": 0.55, "angle": -4},
        {"type": "rect", "center": (FRONT_U + 0.5, tread_v(0.5)), "size": (0.5, 0.06), "angle": 38, "color": YELLOW, "wear": 0.5},
        {"type": "rect", "center": (FRONT_U + 0.5, tread_v(0.5)), "size": (0.5, 0.06), "angle": -38, "color": YELLOW, "wear": 0.5},
    ], dirt=0.55, mud=1.9)
    second = tire_material([
        {"type": "text", "text": "07", "center": (FRONT_U + 2.2, tread_v(0.5)), "height": 0.42, "color": YELLOW, "font": "impact", "wear": 0.45},
        {"type": "rect", "center": (FRONT_U - 1.4, tread_v(0.5)), "size": (0.9, 0.12), "color": YELLOW, "wear": 0.6, "angle": 3},
    ])
    third = tire_material([
        ring_stripe(side_v(0.82), 0.08),
        ring_stripe(tread_v(0.02) - 0.05, 0.05, 0.6),
        {"type": "text", "text": "SOLD", "center": (FRONT_U - 3.6, tread_v(0.5)), "height": 0.3, "color": YELLOW, "font": "impact", "wear": 0.5},
    ], dirt=0.35)
    top = tire_material([
        ring_stripe(side_v(0.82), 0.08, 0.35),
        {"type": "text", "text": "X", "center": (FRONT_U + 1.4, tread_v(0.5)), "height": 0.4, "color": YELLOW, "font": "impact", "wear": 0.5},
    ], dirt=0.3, mud=1.2)

    lugs = [{"type": "rect", "center": (k * 2 * np.pi / 5 * 1.22, (RIM_V[4] + RIM_V[5]) / 2 + 0.05), "size": (0.3, 0.13), "radius": 0.065, "darken": 0.85, "raise": -0.01} for k in range(5)]
    vents = [{"type": "rect", "center": ((k + 0.5) * 2 * np.pi / 5 * 1.22, (RIM_V[4] + RIM_V[5]) / 2 - 0.1), "size": (0.55, 0.12), "radius": 0.06, "darken": 0.7, "raise": -0.012} for k in range(5)]
    hub_hole = {"type": "rect", "center": (np.pi * 1.22, RIM_V[-1] + 0.06), "size": (2 * np.pi * 1.22 + 0.4, 0.14), "darken": 0.9, "raise": -0.01}
    wheel = Material("rust", steel=(128, 126, 122), amount=0.55, decals=lugs + vents + [hub_hole])

    stack = [
        (bottom, 1.0, (0.05, 0.0, -0.06), 4.0, 0.0),
        (second, 0.985, (-0.12, TIRE_H, 0.1), -14.0, 0.0),
        (third, 1.0, (0.14, 2 * TIRE_H, 0.02), 9.0, 0.0),
        (top, 0.97, (-0.06, 3 * TIRE_H, -0.08), 0.0, 1.2),
    ]
    for mat, scale, (x, y, z), yaw, tilt in stack:
        edge = OUTER * scale
        place = compose(T(x, y, z), T(0, 0, edge), R(tilt, 0, 0), T(0, 0, -edge), R(0, yaw, 0))
        a.add("Body", tire(mat, scale).transformed(place))
        if mat is top:
            a.add("Body", rim(wheel).transformed(compose(place, S(scale, 1.0, scale))))

    destructible(a, "ScrapYard")
    collider(a, "Hitbox", (4.8, 4.7, 4.8), (0.0, 2.35, 0.0), shape="Cylinder")
    return a
