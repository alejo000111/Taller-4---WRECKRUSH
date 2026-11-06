import numpy as np

from wr3d import Asset, Material, Mesh, register, T
from wr3d import shapes as sh
from wr3d.materials import REGISTRY, apply_decals, rgb
from wr3d.noise import smoothstep, mix
from _destructible import destructible, collider

ORANGE = (255, 122, 26)
CHARCOAL = (60, 60, 66)
YELLOW = (255, 210, 31)
INK = (22, 22, 26)
RUST = (150, 62, 24)
RUST_DARK = (92, 38, 18)
STEEL = (120, 124, 132)

SEGMENTS = 20
START = 270.0
R_REF = 1.95
FRONT_U = np.pi * R_REF

BOTTOM = [(1.88, 0.0), (1.95, 0.07), (1.95, 0.25), (1.84, 0.33)]
TOP = [(1.84, 4.62), (1.95, 4.72), (1.95, 4.93), (1.88, 5.0), (1.77, 4.97), (1.72, 4.82), (1.62, 4.78)]
LID_Y = 4.78
LID_R = 1.62
DENT = (216.0, 2.5, 1.1, 0.62, 0.36)


def hoop(yc):
    return [(1.84, yc - 0.19), (1.91, yc - 0.12), (1.95, yc), (1.91, yc + 0.12), (1.84, yc + 0.19)]


BODY = [(1.84, 0.33)] + hoop(1.71) + [(1.84, 2.2), (1.84, 2.5), (1.84, 2.8)] + hoop(3.29) + [(1.84, 4.62)]


def v_at(profile, y):
    pts = np.asarray(profile, dtype=np.float64)
    arc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    return float(arc[-1] - np.interp(y, pts[:, 1], arc))


def u_at(theta):
    return np.radians((theta - START) % 360.0) * R_REF


def polar(pos):
    return np.arctan2(-pos[:, 2], pos[:, 0]), np.hypot(pos[:, 0], pos[:, 2])


def dent_weight(pos, dent):
    theta, yc, width, height, _ = dent
    ang, r = polar(pos)
    da = (ang - np.radians(theta) + np.pi) % (2 * np.pi) - np.pi
    d = np.sqrt((da * r / width) ** 2 + ((pos[:, 1] - yc) / height) ** 2)
    return d, ang


def dented(mesh, dent):
    d, ang = dent_weight(mesh.pos, dent)
    push = np.clip(1 - d * d, 0, 1) ** 2 * dent[4]
    out = mesh.copy()
    out.pos = mesh.pos - np.column_stack([np.cos(ang), np.zeros(len(ang)), -np.sin(ang)]) * push[:, None]
    sh.recompute_normals(out)
    keep = push <= 0
    out.nrm[keep] = mesh.nrm[keep]
    return out


def crumpled(mesh, theta=315.0, spread=42.0, drop=0.13):
    ang, _ = polar(mesh.pos)
    da = np.degrees((ang - np.radians(theta) + np.pi) % (2 * np.pi) - np.pi)
    w = np.clip(1 - (da / spread) ** 2, 0, 1) ** 2 * (0.75 + 0.25 * np.sin(np.radians(da) * 9))
    t = np.clip((mesh.pos[:, 1] - TOP[0][1]) / (TOP[3][1] - TOP[0][1]), 0, 1)
    out = mesh.copy()
    out.pos[:, 1] -= drop * w * t
    out.pos[:, [0, 2]] *= (1 - 0.035 * w * t)[:, None]
    return out


def lid_disc(radius, y, mat):
    t = np.radians(START) + np.linspace(0, 2 * np.pi, SEGMENTS, endpoint=False)
    ring = np.column_stack([radius * np.cos(t), np.full(SEGMENTS, y), -radius * np.sin(t)])
    pos = np.vstack([[0.0, y, 0.0], ring])
    k = np.arange(1, SEGMENTS + 1)
    tri = np.column_stack([np.zeros(SEGMENTS, dtype=np.int64), k, np.roll(k, -1)])
    mesh = Mesh(pos, np.tile([0.0, 1.0, 0.0], (len(pos), 1)), pos[:, [0, 2]], tri)
    sh.orient(mesh)
    return mesh.material(mat).seeded(sh.next_seed())


@register("scrapbarrel_drum")
def _drum(ctx, p):
    s = REGISTRY["paint"](ctx, p)
    y = ctx.P[:, 1]
    bare = 1 - np.clip(s.paint, 0, 1)
    rusty = smoothstep(-0.2, 0.15, ctx.noise(4.5, 4, 61) + 0.3 * (1 - ctx.AO)) * p.get("rust", 0.85)
    rust = mix(rgb(RUST), rgb(RUST_DARK), smoothstep(-0.25, 0.3, ctx.noise(13.0, 3, 62)))
    s.base = mix(s.base, rust, rusty)
    s.metal = s.metal * (1 - rusty * 0.85)
    s.rough = mix(s.rough, 0.86, rusty * bare)
    s.height = s.height + rusty * bare * ctx.noise(34.0, 2, 63) * 0.004
    under = s.base.copy()
    apply_decals(ctx, s, p.get("stencils", []))
    keep = np.zeros(ctx.n)
    for (cu, cv), (su, sv) in p.get("keep", []):
        keep = np.maximum(keep, (np.abs(ctx.U[:, 0] - cu) < su / 2) & (np.abs(ctx.U[:, 1] - cv) < sv / 2))
    if p.get("chips"):
        flake = ctx.noise(3.4, 5, 70) + 0.3 * ctx.noise(11.0, 3, 71)
        cluster = smoothstep(-0.12, 0.18, ctx.noise(0.9, 2, 72))
        limit = p["chips"] + 0.09 - 0.18 * cluster
        chip = smoothstep(limit, limit + 0.02, flake) * (1 - keep * 0.85)
        lip = smoothstep(limit - 0.035, limit, flake) * (1 - chip)
        s.paint = s.paint * (1 - chip) * (1 - lip * 0.75)
        s.base = mix(s.base, rgb(STEEL) * 1.1, lip)
        s.base = mix(s.base, mix(under, rust, 0.55), chip)
        s.metal = mix(s.metal, 0.2, chip)
        s.rough = mix(s.rough, 0.8, chip)
        s.height = s.height - chip * 0.005
    drips = np.zeros(ctx.n)
    if p.get("drips"):
        streak = smoothstep(0.07, 0.2, ctx.noise_aniso(np.array([7.5, 0.45, 7.5]), 3, 64))
        reach = 0.35 + 1.5 * smoothstep(-0.25, 0.25, ctx.noise_aniso(np.array([2.2, 0.08, 2.2]), 2, 65))
        for y0, scale in p["drips"]:
            below = y0 - y
            fade = np.clip(1 - below / (reach * scale), 0, 1) ** 0.8 * (below >= -0.02)
            drips = np.maximum(drips, streak * fade)
        drips = drips * (0.75 + 0.25 * smoothstep(-0.2, 0.2, ctx.noise(20.0, 2, 66))) * (1 - keep * 0.7)
        s.paint = s.paint * (1 - drips * 0.92)
        s.base = mix(s.base, rust * 0.9, drips)
        s.metal = s.metal * (1 - drips)
        s.rough = mix(s.rough, 0.8, drips)
    if p.get("pool"):
        puddle = smoothstep(0.0, 0.18, ctx.noise(2.4, 4, 67) + 0.25 * (1 - ctx.AO)) * smoothstep(0.6, 0.9, ctx.N[:, 1]) * p["pool"]
        s.paint = s.paint * (1 - puddle * 0.9)
        s.base = mix(s.base, rust * 0.7, puddle)
        s.rough = mix(s.rough, 0.9, puddle)
        s.metal = s.metal * (1 - puddle)
    if p.get("dent"):
        d, _ = dent_weight(ctx.P, p["dent"])
        rim = smoothstep(0.35, 0.7, d) * (1 - smoothstep(0.8, 1.15, d))
        chips = smoothstep(-0.02, 0.12, ctx.noise(15.0, 3, 68)) * rim
        s.paint = s.paint * (1 - chips * 0.9)
        s.base = mix(s.base, rgb(STEEL) * 0.95, chips * 0.6)
        s.metal = mix(s.metal, 0.9, chips * 0.6)
        s.dirt = np.clip(s.dirt + np.clip(1 - d, 0, 1) * 0.3, 0, 0.85)
    dust = smoothstep(0.55, 0.95, ctx.N[:, 1]) * smoothstep(-0.25, 0.2, ctx.noise(3.0, 3, 69)) * p.get("dust", 0.0)
    s.dirt = np.clip(s.dirt + smoothstep(1.1, 0.0, y) * p.get("ground", 0.0) + dust, 0, 0.85)
    return s


def build():
    a = Asset("ScrapBarrel", budget=1200, atlas=512, ao_radius=0.4, edge_width=0.05, preview_radius=3.7,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")

    band_v = v_at(BODY, 2.5)
    upper_v = v_at(BODY, 4.04)
    lower_v = v_at(BODY, 0.95)
    plate_w, plate_h = 3.0, 0.8
    plate_rivets = [(FRONT_U + sx * (plate_w / 2 - 0.12), upper_v + sy * (plate_h / 2 - 0.12)) for sx in (-1, 1) for sy in (-1, 1)]
    diamond_u = FRONT_U + 1.0
    side_u = u_at(0.0)
    left_u = u_at(180.0)
    body_decals = [
        {"type": "rect", "center": (6.2, band_v), "size": (12.6, 1.12), "color": YELLOW, "wear": 0.45},
        {"type": "stripes", "center": (6.2, band_v), "size": (12.6, 1.12), "width": 0.34, "color": INK, "wear": 0.45},
        {"type": "rect", "center": (FRONT_U + 0.03, upper_v + 0.04), "size": (plate_w, plate_h), "radius": 0.1, "darken": 0.45, "raise": -0.002},
        {"type": "rect", "center": (FRONT_U, upper_v), "size": (plate_w, plate_h), "radius": 0.1, "color": CHARCOAL, "wear": 0.3, "metal": 0.5, "rough": 0.45},
        {"type": "rect", "center": (FRONT_U, upper_v), "size": (plate_w - 0.1, plate_h - 0.1), "radius": 0.07, "outline": 0.035, "color": (150, 150, 156), "wear": 0.3},
        {"type": "text", "text": "SALVAGE", "center": (FRONT_U, upper_v + 0.02), "height": 0.5, "color": YELLOW, "font": "impact", "wear": 0.35},
        {"type": "rivets", "points": plate_rivets, "radius": 0.05, "height": 0.012, "color": (150, 152, 160)},
        {"type": "rect", "center": (diamond_u, lower_v - 0.02), "size": (0.86, 0.86), "angle": 45, "radius": 0.04, "color": (238, 232, 218), "wear": 0.4},
        {"type": "rect", "center": (diamond_u, lower_v - 0.02), "size": (0.74, 0.74), "angle": 45, "radius": 0.03, "color": (206, 40, 32), "wear": 0.4},
        {"type": "text", "text": "!", "center": (diamond_u, lower_v - 0.1), "height": 0.34, "color": (238, 232, 218), "font": "black", "wear": 0.3},
        {"type": "text", "text": "3", "center": (diamond_u, lower_v + 0.28), "height": 0.13, "color": (238, 232, 218), "font": "black", "wear": 0.3},
        {"type": "text", "text": "FLAMMABLE", "center": (FRONT_U - 0.42, lower_v - 0.02), "height": 0.3, "color": (238, 232, 218), "font": "impact", "wear": 0.45},
        {"type": "text", "text": "55 GAL", "center": (side_u, upper_v), "height": 0.42, "color": (238, 232, 218), "font": "impact", "wear": 0.5},
        {"type": "text", "text": "07", "center": (left_u + 0.2, upper_v), "height": 0.6, "color": INK, "font": "impact", "wear": 0.5},
        {"type": "rect", "center": (0.9, v_at(BODY, 2.5)), "size": (0.06, 5.0), "darken": 0.35, "raise": 0.004},
    ]
    drips = [(4.62, 1.0), (3.1, 0.7), (1.52, 0.6)]
    paint = Material("scrapbarrel_drum", color=ORANGE, under=STEEL, wear=0.62, wear_scale=0.8, scratches=0.45, chip_depth=0.005,
                     rough=0.48, dirt=0.4, drips=drips, ground=0.6, dent=DENT, chips=0.19, stencils=body_decals,
                     keep=[((FRONT_U, upper_v), (plate_w + 0.2, plate_h + 0.2)), ((side_u, upper_v), (2.0, 0.7)), ((FRONT_U - 0.42, lower_v), (1.7, 0.5))])
    rim = Material("scrapbarrel_drum", color=CHARCOAL, under=STEEL, wear=0.6, scratches=0.4, rough=0.45, dirt=0.4, ground=0.55, chips=0.2)
    lid = Material("scrapbarrel_drum", color=(226, 102, 22), under=STEEL, wear=0.5, scratches=0.4, rough=0.5, dirt=0.5, pool=0.8, dust=0.35, chips=0.21, stencils=[
        {"type": "circle", "center": (0.0, 0.0), "radius": 1.32, "outline": 0.05, "darken": 0.12, "raise": 0.006},
        {"type": "circle", "center": (0.0, 0.0), "radius": 0.72, "outline": 0.05, "darken": 0.12, "raise": 0.006},
    ])
    cap = Material("scrapbarrel_drum", color=CHARCOAL, under=STEEL, wear=0.5, scratches=0.3, rough=0.4, dirt=0.35, rust=0.6)

    a.add("Body", sh.lathe(BOTTOM, SEGMENTS, rim, start=START, r_ref=R_REF))
    body = sh.lathe(BODY, SEGMENTS, paint, start=START, r_ref=R_REF)
    a.add("Body", dented(body, DENT))
    a.add("Body", crumpled(sh.lathe(TOP, SEGMENTS, rim, start=START, r_ref=R_REF)))
    a.add("Body", crumpled(lid_disc(LID_R, LID_Y, lid)))

    bung_at = np.array([0.84, LID_Y, -0.71])
    bung = sh.lathe([(0.34, 0.0), (0.34, 0.09), (0.27, 0.13), (0.0, 0.13)], 10, cap)
    a.add("Body", bung.transformed(T(*bung_at)))
    key = sh.rounded_box((0.42, 0.09, 0.1), 0.0, 1, cap, faces=["+x", "-x", "+y", "+z", "-z"])
    a.add("Body", key.transformed(T(bung_at[0], LID_Y + 0.175, bung_at[2])))
    vent = sh.lathe([(0.22, 0.0), (0.22, 0.09), (0.13, 0.13), (0.13, 0.21), (0.0, 0.21)], 10, cap)
    a.add("Body", vent.transformed(T(-0.88, LID_Y, 0.74)))

    destructible(a, "ScrapYard")
    collider(a, "Hitbox", (3.9, 5.0, 3.9), (0, 2.5, 0), shape="Cylinder")
    a.point("label", (0, 5.8, 0))
    return a
