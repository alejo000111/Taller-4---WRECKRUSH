import numpy as np

from wr3d import Asset, Material, register, T, R, compose, align_y
from wr3d import shapes as sh
from wr3d.materials import REGISTRY, rgb
from wr3d.noise import smoothstep, mix
from _destructible import destructible, collider

YELLOW = (255, 180, 20)
CHARCOAL = (30, 30, 34)
STEEL = (120, 124, 132)
RUST = (150, 62, 24)
RUST_DARK = (92, 38, 18)
HAZARD = (255, 210, 31)
GLOW = (255, 170, 40)
INK = (26, 24, 24)

SIDEWAYS = R(0, -90, 0)
FRONT_AXLE = (-1.05, 1.0)
REAR_AXLE = (3.05, 0.78)
FRONT_ARCH = 1.12
REAR_ARCH = 0.9
WHEEL_X = 2.45
BODY_W = 4.4
WEIGHT_W = 4.7
CHAIN_X = 0.44


@register("forklift_paint")
def forklift_paint(ctx, p):
    s = REGISTRY["paint"](ctx, p)
    P, N = ctx.P, ctx.N
    rust_col = mix(rgb(RUST), rgb(RUST_DARK), smoothstep(-0.4, 0.5, ctx.noise(7.0, 3, 71)))
    s.base = mix(s.base, rust_col, smoothstep(-0.15, 0.35, ctx.noise(4.0, 3, 73)) * p.get("chip_rust", 0.6))
    amount = p.get("rust", 0.3)
    patch = smoothstep(0.62 - amount * 0.5, 0.7 - amount * 0.5, ctx.noise(1.8, 4, 74) + 0.3 * ctx.E + 0.35 * (1 - ctx.AO))
    s.paint = s.paint * (1 - patch)
    s.base = mix(s.base, rust_col, patch)
    s.rough = mix(s.rough, 0.85, patch)
    s.metal = mix(s.metal, 0.1, patch)
    s.height = s.height + patch * ctx.noise(30.0, 2, 78) * 0.002
    s.tint = s.tint * (0.93 + 0.1 * ctx.noise(0.9, 3, 79))
    vertical = 1 - np.abs(N[:, 1])
    drip = smoothstep(0.15, 0.55, ctx.noise_aniso(np.array([16.0, 0.8, 16.0]), 3, 75)) * smoothstep(0.0, 0.5, ctx.noise(1.4, 2, 76)) * vertical * p.get("streaks", 0.4)
    s.paint = s.paint * (1 - drip * 0.55)
    s.base = mix(s.base, rust_col, np.clip(drip * 2, 0, 1))
    low = 1 - smoothstep(p.get("oil_low", 0.7), p.get("oil_high", 2.4), P[:, 1])
    oil = (low * (0.35 + 0.65 * smoothstep(-0.25, 0.35, ctx.noise(2.6, 3, 77))) + drip * 0.4) * p.get("oil", 0.0)
    s.dirt = np.clip(s.dirt + oil, 0, 0.9)
    s.rough = mix(s.rough, 0.22, np.clip(oil, 0, 1) * 0.6)
    hazard = p.get("hazard")
    if hazard:
        region = smoothstep(hazard["z"] - 0.02, hazard["z"] + 0.02, P[:, 2]) * smoothstep(0.2, 0.45, N[:, 2]) * smoothstep(hazard["y"], hazard["y"] + 0.03, P[:, 1])
        t = (P[:, 0] - P[:, 1]) / hazard["width"]
        stripe = smoothstep(0.45, 0.55, np.abs((t % 2.0) - 1.0))
        s.tint = s.tint * (1 - 0.88 * stripe * region)
    for cx, cy, cz, r, depth in p.get("dents", ()):
        d = np.linalg.norm(P - np.array([cx, cy, cz]), axis=1) / r
        bowl = np.clip(1 - d * d, 0, 1) ** 2
        s.height = s.height - bowl * depth
        s.tint = s.tint * (1 - bowl * 0.1)
    for start, end, width in p.get("seams", ()):
        a, b = np.asarray(start, dtype=np.float64), np.asarray(end, dtype=np.float64)
        ab = b - a
        t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
        d = np.linalg.norm(P - (a + t[:, None] * ab), axis=1)
        groove = 1 - smoothstep(width * 0.5, width, d)
        s.tint = s.tint * (1 - 0.55 * groove)
        s.base = s.base * (1 - 0.5 * groove)[:, None]
        s.height = s.height - groove * 0.006
        s.dirt = np.clip(s.dirt + groove * 0.3, 0, 0.9)
    for cx, cy, cz, r in p.get("studs", ()):
        d = np.linalg.norm(P - np.array([cx, cy, cz]), axis=1) / r
        cov = 1 - smoothstep(0.8, 1.0, d)
        s.height = s.height + np.sqrt(np.clip(1 - d * d, 0, 1)) * r * 0.4
        s.paint = s.paint * (1 - cov * 0.8)
        s.base = mix(s.base, rgb(STEEL) * 0.9, cov)
        s.metal = mix(s.metal, 1.0, cov)
    return s


@register("forklift_tread")
def forklift_tread(ctx, p):
    s = REGISTRY["rubber"](ctx, dict(color=p.get("color", (32, 32, 34)), pattern="none", dirt=p.get("dirt", 0.4)))
    tread = 1 - smoothstep(0.45, 0.7, np.abs(ctx.N[:, 0]))
    across = np.abs(np.abs(ctx.P[:, 0]) - WHEEL_X)
    phase = ctx.U[:, 0] / p.get("pitch", 0.34) + across * p.get("chevron", 1.4)
    lug = smoothstep(-0.3, 0.3, np.sin(2 * np.pi * phase))
    groove = tread * (1 - lug)
    s.base = s.base * (1 - 0.5 * groove)[:, None]
    s.height = s.height + tread * lug * 0.022
    s.rough = np.clip(s.rough + 0.08 * groove - 0.1 * tread * lug, 0, 1)
    ring = 1 - smoothstep(0.004, 0.012, np.abs(np.linalg.norm(ctx.P[:, 1:] - np.array(p.get("hub", (1.0, -1.05))), axis=1) - p.get("ring", 0.8)))
    s.height = s.height + (1 - tread) * ring * 0.006
    return s


@register("forklift_chain")
def forklift_chain(ctx, p):
    s = REGISTRY["metal"](ctx, dict(color=p.get("color", (84, 86, 92)), rough=0.45, polish=0.6, dirt=p.get("dirt", 0.55)))
    pitch = p.get("pitch", 0.15)
    along = ctx.U[:, 1] / pitch
    k = np.floor(along)
    f = along - k
    across = np.abs(np.abs(ctx.P[:, 0]) - CHAIN_X)
    gap = 1 - smoothstep(0.03, 0.08, np.abs(f - 0.5))
    pin = 1 - smoothstep(0.02, 0.03, np.hypot(np.minimum(f, 1 - f) * pitch, across))
    plate = k % 2
    s.base = s.base * (1 - 0.55 * gap + 0.25 * pin - 0.08 * plate)[:, None]
    s.height = s.height + plate * 0.004 - gap * 0.006 + pin * 0.008
    s.rough = np.clip(s.rough + 0.2 * gap - 0.15 * pin, 0, 1)
    return s


def arc(center, radius, a0, a1, count):
    cz, cy = center
    return [(cz + radius * np.cos(a), cy + radius * np.sin(a)) for a in np.radians(np.linspace(a0, a1, count + 1))]


def outline(points, radii, segments):
    return sh.round_polyline(np.asarray(points, dtype=np.float64), np.asarray(radii, dtype=np.float64), segments, closed=True)


def body_outline():
    front_start = np.degrees(np.arcsin((1.2 - FRONT_AXLE[1]) / FRONT_ARCH))
    front_end = np.degrees(np.arccos((-1.85 - FRONT_AXLE[0]) / FRONT_ARCH))
    rear_start = np.degrees(np.arccos((3.7 - REAR_AXLE[0]) / REAR_ARCH))
    rear_end = 180 - np.degrees(np.arcsin((1.2 - REAR_AXLE[1]) / REAR_ARCH))
    top = [(-1.85, 2.95), (-1.62, 3.32), (-0.98, 3.4), (-0.72, 3.2), (-0.6, 2.3), (0.72, 2.3), (0.8, 3.08), (1.0, 3.25), (3.7, 3.25)]
    radii = [0.16, 0.14, 0.14, 0.06, 0.06, 0.06, 0.08, 0.08, 0.0]
    arches = arc(REAR_AXLE, REAR_ARCH, rear_start, rear_end, 6) + arc(FRONT_AXLE, FRONT_ARCH, front_start, front_end, 7)
    return outline(top + arches, radii + [0.0] * len(arches), 2)


def weight_outline():
    low = np.degrees(np.arcsin((0.45 - REAR_AXLE[1]) / REAR_ARCH))
    high = np.degrees(np.arccos((3.55 - REAR_AXLE[0]) / REAR_ARCH))
    pts = [(3.55, 3.84), (4.3, 3.9), (5.0, 3.55), (5.0, 0.45)] + arc(REAR_AXLE, REAR_ARCH, low, high, 4)
    radii = [0.1, 0.0, 0.8, 0.42] + [0.0] * 5
    return outline(pts, radii, 3)


def fork_outline():
    pts = [(-2.75, 0.0), (-2.75, 2.35), (-2.52, 2.35), (-2.52, 2.55), (-2.97, 2.55), (-2.97, 0.22), (-4.72, 0.17), (-5.0, 0.05), (-4.96, 0.0)]
    radii = [0.0, 0.0, 0.0, 0.0, 0.05, 0.2, 0.06, 0.03, 0.0]
    return outline(pts, radii, 1)


def side_extrude(points, width, mat, bevel, cap_mats=None, x=0.0):
    m = sh.extrude(points, width, mat, bevel=bevel, corner_radius=0.0, cap_mats=cap_mats)
    return m.transformed(compose(T(x, 0, 0), SIDEWAYS))


def rect(w, h):
    return [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]


def block(size, mat, center, faces=None, rot=None, face_mats=None):
    m = sh.rounded_box(size, 0.0, 1, mat, faces=faces, face_mats=face_mats)
    return m.transformed(compose(T(*center), rot if rot is not None else np.eye(4)))


def bar(size, mat, center, axis="y", caps=True, rot=None):
    sx, sy, sz = size
    if axis == "x":
        m = sh.extrude(rect(sz, sy), sx, mat, bevel=0.0, corner_radius=0.0, caps=caps).transformed(R(0, 90, 0))
    elif axis == "y":
        m = sh.extrude(rect(sx, sz), sy, mat, bevel=0.0, corner_radius=0.0, caps=caps).transformed(R(-90, 0, 0))
    else:
        m = sh.extrude(rect(sx, sy), sz, mat, bevel=0.0, corner_radius=0.0, caps=caps)
    return m.transformed(compose(T(*center), rot if rot is not None else np.eye(4)))


def strut(a, b, thickness, mat, caps=False):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    d = b - a
    return bar((thickness, np.linalg.norm(d), thickness), mat, (0, 0, 0), "y", caps).transformed(compose(T(*((a + b) / 2)), align_y(d)))


def i_beam(height, mat, w=0.2, d=0.3, f=0.075, t=0.055):
    poly = [(-w, -d), (w, -d), (w, -d + f), (t, -d + f), (t, d - f), (w, d - f), (w, d), (-w, d), (-w, d - f), (-t, d - f), (-t, -d + f), (-w, -d + f)]
    return sh.extrude(poly, height, mat, bevel=0.0, corner_radius=0.0).transformed(R(-90, 0, 0))


def wheel(radius, width, hub, tire_mat, rim_mat, segments, side, center):
    h = width / 2
    rr = radius * 0.62
    tire = sh.lathe([(0.0, -h), (radius, -h + 0.1), (radius, h - 0.14), (radius - 0.12, h), (rr, h)], segments, tire_mat, smooth_angle=50)
    rim = sh.lathe([(rr + 0.02, h - 0.06), (rr - 0.08, h + 0.03), (hub + 0.05, h - 0.1), (hub, h + 0.06), (0.0, h + 0.08)], segments, rim_mat, smooth_angle=40)
    parts = []
    for m in (tire, rim):
        m = m.transformed(R(0, 0, -90))
        if side < 0:
            m = sh.mirrored(m, "x")
        parts.append(m.transformed(T(side * WHEEL_X, center[1], center[0])))
    return parts


def lug_studs(center, width, hub):
    out = []
    for side in (-1, 1):
        x = side * (WHEEL_X + width / 2 + 0.07)
        for k in range(5):
            a = np.radians(90 + k * 72)
            out.append((x, center[1] + np.sin(a) * hub * 0.62, center[0] + np.cos(a) * hub * 0.62, 0.05))
    return out


def side_decals(sign, items):
    out = []
    for d in items:
        d = dict(d)
        z, y = d.pop("at")
        d["center"] = (z * sign, -y)
        if "points" in d:
            d["points"] = [(pz * sign, -py) for pz, py in d["points"]]
        out.append(d)
    return out


def body_materials(paint):
    panel = [
        {"type": "rect", "at": (2.17, 2.5), "size": (2.5, 1.18), "radius": 0.12, "outline": 0.035, "darken": 0.55, "raise": -0.005},
        {"type": "text", "text": "WRK-LIFT 3T", "at": (2.17, 2.46), "height": 0.42, "color": INK, "font": "impact", "wear": 0.45},
        {"type": "rect", "at": (2.17, 2.86), "size": (2.1, 0.06), "color": INK, "wear": 0.4},
        {"type": "rect", "at": (1.15, 1.55), "size": (1.6, 0.04), "darken": 0.4, "raise": -0.004},
        {"type": "rivets", "at": (0.0, 0.0), "points": [(z, 1.42) for z in np.linspace(0.3, 2.0, 5)] + [(-1.6, 2.15), (-0.8, 2.15)], "radius": 0.045, "height": 0.012},
    ]
    plate = [
        {"type": "rect", "at": (-1.22, 2.72), "size": (0.7, 0.46), "radius": 0.04, "color": (196, 198, 204), "metal": 0.7, "rough": 0.35, "wear": 0.15},
        {"type": "rect", "at": (-1.22, 2.6), "size": (0.6, 0.12), "color": (40, 40, 44), "wear": 0.1},
        {"type": "text", "text": "3000 KG", "at": (-1.22, 2.6), "height": 0.08, "color": (220, 222, 226), "font": "bold", "wear": 0.1},
        {"type": "rect", "at": (-1.22, 2.78), "size": (0.54, 0.03), "color": (60, 60, 66), "wear": 0.0},
        {"type": "rect", "at": (-1.22, 2.84), "size": (0.54, 0.03), "color": (60, 60, 66), "wear": 0.0},
    ]
    fuel = [
        {"type": "circle", "at": (3.3, 2.05), "radius": 0.17, "color": (40, 40, 44), "outline": 0.05, "wear": 0.2},
        {"type": "circle", "at": (3.3, 2.05), "radius": 0.08, "color": (60, 60, 66), "wear": 0.2},
        {"type": "rect", "at": (3.3, 1.72), "size": (0.06, 0.38), "darken": 0.5, "raise": 0.0},
    ]
    return paint.but(decals=side_decals(1, panel + plate)), paint.but(decals=side_decals(-1, panel + fuel))


def weight_materials(paint):
    items = [
        {"type": "rect", "at": (4.25, 1.6), "size": (1.5, 0.05), "darken": 0.5, "raise": -0.005},
        {"type": "rect", "at": (4.25, 2.95), "size": (1.5, 0.05), "darken": 0.5, "raise": -0.005},
        {"type": "text", "text": "3T", "at": (4.28, 2.28), "height": 0.62, "color": INK, "font": "impact", "wear": 0.5},
        {"type": "rivets", "at": (0.0, 0.0), "points": [(4.0, 1.35), (4.6, 1.35), (4.0, 3.25), (4.6, 3.25)], "radius": 0.07, "height": 0.02, "color": (90, 92, 98)},
    ]
    return paint.but(decals=side_decals(1, items)), paint.but(decals=side_decals(-1, items))


def build():
    a = Asset("Forklift", budget=3000, atlas=1024, ao_radius=0.8, edge_width=0.07, preview_radius=6.6,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=GLOW)

    dents = [(-2.2, 2.7, 2.9, 0.45, 0.03), (2.2, 2.2, 1.4, 0.5, 0.035), (-1.2, 3.3, 5.0, 0.55, 0.035), (2.35, 1.2, 4.6, 0.4, 0.03)]
    seams = [((-1.95, 3.26, 1.08), (1.95, 3.26, 1.08), 0.035), ((-1.95, 3.26, 3.5), (1.95, 3.26, 3.5), 0.035), ((-1.95, 3.26, 1.08), (-1.95, 3.26, 3.5), 0.035), ((1.95, 3.26, 1.08), (1.95, 3.26, 3.5), 0.035),
             ((-2.0, 3.39, -1.25), (2.0, 3.39, -1.25), 0.035), ((-2.36, 3.9, 4.2), (2.36, 3.9, 4.2), 0.035)]
    yellow = Material("forklift_paint", color=YELLOW, under=STEEL, wear=0.5, scratches=0.45, rough=0.42, dirt=0.4, dirt_color=(34, 28, 22), rust=0.32, streaks=0.45, oil=0.6, dents=dents, seams=seams)
    charcoal = Material("forklift_paint", color=CHARCOAL, under=STEEL, wear=0.42, scratches=0.4, rough=0.55, dirt=0.3, dirt_color=(60, 44, 30), rust=0.5, streaks=0.35, oil=0.25)
    fork_paint = charcoal.but(wear=0.65, rust=0.6, chip_rust=0.3)
    guard = charcoal.but(wear=0.45, rust=0.55)

    a.add("Body", side_extrude(body_outline(), BODY_W, yellow, 0.09, cap_mats=list(body_materials(yellow))))
    weight = yellow.but(hazard={"z": 4.45, "y": 0.75, "width": 0.36})
    a.add("Body", side_extrude(weight_outline(), WEIGHT_W, weight, 0.12, cap_mats=list(weight_materials(weight))))
    a.add("Body", block((3.9, 1.2, 6.15), charcoal, (0, 0.95, 1.125), faces=["+x", "-x", "-z"]))

    tire = Material("forklift_tread", color=(34, 33, 35), dirt=0.45, dirt_color=(78, 66, 52), pitch=0.36)
    studs = lug_studs(FRONT_AXLE, 0.9, 0.26) + lug_studs(REAR_AXLE, 0.8, 0.2)
    rim = Material("forklift_paint", color=YELLOW, under=STEEL, wear=0.45, scratches=0.3, dirt=0.55, dirt_color=(70, 56, 40), rust=0.45, streaks=0.2, studs=studs)
    for side in (-1, 1):
        a.add("Body", wheel(1.0, 0.9, 0.26, tire.but(hub=(FRONT_AXLE[1], FRONT_AXLE[0]), ring=0.82), rim, 14, side, FRONT_AXLE))
        a.add("Body", wheel(0.78, 0.8, 0.2, tire.but(hub=(REAR_AXLE[1], REAR_AXLE[0]), ring=0.62), rim, 12, side, REAR_AXLE))

    mast_z = -2.15
    for side in (-1, 1):
        a.add("Body", i_beam(6.25, charcoal).transformed(T(side * 1.55, 3.55, mast_z)))
        a.add("Body", bar((0.22, 6.95, 0.3), charcoal, (side * 1.2, 3.92, -2.25), "y"))
    a.add("Body", bar((2.8, 0.3, 0.45), charcoal, (0, 0.72, mast_z), "x", caps=False))
    a.add("Body", bar((2.78, 0.24, 0.16), charcoal, (0, 6.42, -1.97), "x", caps=False))
    a.add("Body", bar((2.62, 0.26, 0.36), charcoal, (0, 7.2, -2.13), "x"))

    chrome = Material("chrome", color=(214, 218, 226), rough=0.12)
    a.add("Body", sh.lathe([(0.21, 0.87), (0.21, 5.3), (0.25, 5.34), (0.25, 5.52), (0.0, 5.55)], 10, charcoal, smooth_angle=40).transformed(T(0, 0, -2.17)))
    a.add("Body", sh.lathe([(0.12, 5.5), (0.12, 7.08)], 8, chrome).transformed(T(0, 0, -2.17)))
    chain = Material("forklift_chain", color=(84, 86, 92))
    for side in (-1, 1):
        x = side * CHAIN_X
        a.add("Body", bar((0.16, 5.12, 0.05), chain, (x, 4.86, -2.37), "y", caps=False))
        a.add("Body", bar((0.16, 2.84, 0.05), chain, (x, 6.0, -1.96), "y", caps=False))
        a.add("Body", sh.cylinder(0.2, 0.2, charcoal, bevel=0.0, segments=8).transformed(compose(T(x, 7.42, -2.165), R(0, 0, 90))))
        a.add("Body", bar((0.3, 0.14, 0.16), charcoal, (x * 0.62, 4.58, -1.98), "x", caps=False))

    carriage_face = charcoal.but(decals=[
        {"type": "stripes", "center": (0.0, 0.62), "size": (3.4, 0.36), "width": 0.22, "color": HAZARD, "wear": 0.45},
    ])
    bar_face = charcoal.but(decals=[
        {"type": "text", "text": "MAX 3000 KG", "center": (0.0, 0.0), "height": 0.2, "color": HAZARD, "font": "impact", "wear": 0.4},
    ])
    a.add("Body", block((3.5, 2.1, 0.2), charcoal, (0, 1.3, -2.52), faces=["+x", "-x", "-z", "+z"], face_mats={"-z": carriage_face}))
    a.add("Body", block((3.7, 0.36, 0.34), charcoal, (0, 2.18, -2.58), face_mats={"-z": bar_face}))
    a.add("Body", bar((3.7, 0.3, 0.3), charcoal, (0, 0.42, -2.57), "x"))
    for side in (-1, 1):
        a.add("Body", bar((0.14, 2.1, 0.14), charcoal, (side * 1.72, 3.41, -2.55), "y", caps=False))
    a.add("Body", bar((3.6, 0.16, 0.16), charcoal, (0, 4.48, -2.55), "x"))
    a.add("Body", bar((3.3, 0.1, 0.1), charcoal, (0, 3.45, -2.55), "x", caps=False))
    for x in (-1.08, -0.4, 0.4, 1.08):
        a.add("Body", bar((0.08, 2.05, 0.08), charcoal, (x, 3.43, -2.55), "y", caps=False))

    for side in (-1, 1):
        a.add("Body", side_extrude(fork_outline(), 0.42, fork_paint, 0.025, x=side * 0.85))

    lamp = sh.lathe([(0.0, -0.12), (0.16, -0.1), (0.2, 0.1), (0.16, 0.13)], 8, charcoal, smooth_angle=50)
    lens = sh.lathe([(0.165, 0.11), (0.0, 0.15)], 8, None)
    for side in (-1, 1):
        x = side * 1.99
        a.add("Body", lamp.transformed(compose(T(x, 5.6, -2.25), R(-90, 0, 0))))
        a.add("Glow", lens.transformed(compose(T(x, 5.6, -2.25), R(-90, 0, 0))))
        a.add("Body", bar((0.14, 0.12, 0.12), charcoal, (side * 1.79, 5.6, -2.2), "x", caps=False))

    grip = Material("rubber", color=(26, 26, 30), pattern="knurl", freq=14.0)
    a.add("Body", sh.sweep([(-2.16, 4.1, -1.17), (-2.38, 4.24, -1.13), (-2.38, 5.5, -1.0), (-2.16, 5.66, -0.96)], 0.045, 4, grip, samples=6))
    hazard_bar = Material("hazard", color=HAZARD, color2=(24, 24, 28), width=0.22, wear=0.45, scratches=0.4, dirt=0.35)
    for side in (-1, 1):
        a.add("Body", strut((side * 2.06, 3.3, -1.3), (side * 2.18, 7.2, -0.9), 0.24, guard))
        a.add("Body", strut((side * 2.1, 3.8, 4.05), (side * 2.18, 7.2, 3.72), 0.24, guard))
        a.add("Body", bar((0.2, 0.24, 5.1), guard, (side * 2.22, 7.27, 1.45), "z"))
    a.add("Body", bar((4.24, 0.24, 0.22), hazard_bar, (0, 7.27, -1.0), "x", caps=False))
    a.add("Body", bar((4.24, 0.24, 0.22), guard, (0, 7.27, 3.88), "x", caps=False))
    for x in (-1.65, -0.99, -0.33, 0.33, 0.99, 1.65):
        a.add("Body", bar((0.3, 0.1, 4.66), guard, (x, 7.3, 1.44), "z", caps=False))

    a.add("Body", sh.lathe([(0.24, 0.0), (0.24, 0.12), (0.0, 0.16)], 10, charcoal).transformed(T(0, 7.38, 3.88)))
    a.add("Glow", sh.lathe([(0.19, 0.0), (0.19, 0.16), (0.14, 0.33), (0.0, 0.4)], 10, None, smooth_angle=60).transformed(T(0, 7.53, 3.88)))

    vinyl = Material("plastic", color=(42, 40, 44), rough=0.55, scuff=0.6, dirt=0.3)
    cushion_top = vinyl.but(decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (1.2, 0.92), "radius": 0.1, "outline": 0.025, "darken": 0.5, "raise": -0.006},
        {"type": "rect", "center": (-0.22, 0.0), "size": (0.025, 0.9), "darken": 0.45, "raise": -0.008},
        {"type": "rect", "center": (0.22, 0.0), "size": (0.025, 0.9), "darken": 0.45, "raise": -0.008},
    ])
    back_face = vinyl.but(decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (1.2, 1.1), "radius": 0.1, "outline": 0.025, "darken": 0.5, "raise": -0.006},
        {"type": "rect", "center": (0.0, -0.2), "size": (1.18, 0.025), "darken": 0.45, "raise": -0.008},
        {"type": "rect", "center": (0.0, 0.2), "size": (1.18, 0.025), "darken": 0.45, "raise": -0.008},
    ])
    a.add("Body", bar((1.4, 0.12, 1.1), charcoal, (0, 3.3, 1.75), "x"))
    a.add("Body", sh.rounded_box((1.55, 0.36, 1.22), 0.14, 1, vinyl, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"+y": cushion_top}).transformed(T(0, 3.54, 1.72)))
    a.add("Body", sh.rounded_box((1.6, 1.45, 0.42), 0.16, 1, vinyl, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"-z": back_face}).transformed(compose(T(0, 4.36, 2.54), R(10, 0, 0))))

    vent = charcoal.but(decals=[
        {"type": "rect", "center": (0.0, -0.22 + k * 0.11), "size": (1.8, 0.05), "radius": 0.02, "darken": 0.75, "raise": -0.008} for k in range(5)
    ])
    a.add("Body", block((2.2, 0.1, 0.66), charcoal, (0, 3.3, 3.1), faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"+y": vent}))

    floor = Material("rubber", color=(36, 36, 40), pattern="dots", freq=7.0, depth=0.008, dirt=0.5)
    a.add("Body", block((3.9, 0.04, 1.22), floor, (0, 2.32, 0.06), faces=["+y"]))
    step = Material("diamondplate", color=(150, 154, 162), pitch=0.22, dirt=0.5)
    a.add("Body", bar((0.5, 0.12, 0.9), step, (-2.2, 1.05, 0.95), "z"))

    dash_face = Material("plastic", color=(30, 30, 34), rough=0.45, decals=[
        {"type": "circle", "center": (-0.42, 0.0), "radius": 0.13, "color": (12, 12, 14), "wear": 0.0},
        {"type": "circle", "center": (-0.42, 0.0), "radius": 0.13, "color": (200, 200, 205), "outline": 0.02, "wear": 0.1},
        {"type": "rect", "center": (-0.42, -0.04), "size": (0.02, 0.1), "angle": 35, "color": (255, 90, 40), "wear": 0.0},
        {"type": "circle", "center": (0.0, 0.0), "radius": 0.13, "color": (12, 12, 14), "wear": 0.0},
        {"type": "circle", "center": (0.0, 0.0), "radius": 0.13, "color": (200, 200, 205), "outline": 0.02, "wear": 0.1},
        {"type": "rect", "center": (0.0, -0.04), "size": (0.02, 0.1), "angle": -20, "color": (255, 90, 40), "wear": 0.0},
        {"type": "rect", "center": (0.4, -0.06), "size": (0.12, 0.08), "radius": 0.02, "color": (255, 60, 50), "wear": 0.1},
        {"type": "rect", "center": (0.4, 0.07), "size": (0.12, 0.08), "radius": 0.02, "color": (90, 220, 90), "wear": 0.1},
    ])
    a.add("Body", block((1.5, 0.1, 0.42), charcoal, (0, 3.42, -1.0), rot=R(22, 0, 0), faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"+y": dash_face}))
    column_base = np.array([0.0, 3.2, -0.72])
    column_top = np.array([0.0, 3.92, -0.34])
    axis = column_top - column_base
    a.add("Body", sh.cylinder(0.07, np.linalg.norm(axis), charcoal, bevel=0.0, segments=8).transformed(compose(T(*((column_base + column_top) / 2)), align_y(axis))))
    tilt = compose(T(*column_top), align_y(axis))
    a.add("Body", sh.torus(0.4, 0.055, grip, segments=10, sides=5).transformed(tilt))
    a.add("Body", bar((0.76, 0.04, 0.08), charcoal, (0, 0, 0), "x", caps=False).transformed(tilt))
    knob = Material("plastic", color=(200, 40, 34), rough=0.35)
    a.add("Body", sh.cylinder(0.045, 0.14, knob, bevel=0.0, segments=6).transformed(compose(tilt, T(0.28, 0.08, 0.28))))
    black_knob = Material("plastic", color=(28, 28, 32), rough=0.35)
    for k, x in enumerate((0.7, 0.92)):
        a.add("Body", strut((x, 3.22, -0.82), (x, 3.62, -0.68), 0.045, charcoal))
        a.add("Body", sh.sphere(0.065, knob if k == 0 else black_knob, segments=6, rings=3).transformed(T(x, 3.65, -0.67)))

    exhaust = charcoal.but(rust=0.75, streaks=0.6, chip_rust=0.9, wear=0.55, dirt=0.6, dirt_color=(14, 12, 12), oil=0.0, seams=[((1.45, 5.2, 4.05), (1.45, 5.5, 4.3), 0.4)])
    a.add("Body", sh.sweep([(1.45, 3.75, 3.95), (1.45, 4.6, 3.95), (1.45, 5.15, 4.0), (1.45, 5.45, 4.25)], 0.09, 6, exhaust, samples=6))
    bumper = Material("rubber", color=(30, 30, 33), pattern="ribs", freq=6.0, depth=0.006, dirt=0.4)
    for side in (-1, 1):
        a.add("Body", bar((0.12, 0.22, 2.0), bumper, (side * 2.24, 1.36, 1.15), "z"))
    a.add("Body", bar((0.7, 0.3, 0.2), charcoal, (0, 0.8, 5.08), "x"))
    a.add("Body", sh.cylinder(0.08, 0.55, Material("metal", color=(150, 152, 158), rough=0.35, dirt=0.4), bevel=0.0, segments=6).transformed(T(0, 0.92, 5.1)))
    tail = Material("plastic", color=(210, 36, 30), rough=0.25)
    for side in (-1, 1):
        a.add("Body", bar((0.36, 0.22, 0.06), tail, (side * 1.7, 3.0, 5.02), "z"))

    destructible(a, "ScrapYard")
    collider(a, "Hitbox", (5.2, 3.8, 6.85), (0, 1.9, 1.575))
    collider(a, "Mast", (3.9, 7.4, 1.0), (0, 3.85, -2.3))
    collider(a, "Guard", (4.6, 0.3, 5.1), (0, 7.27, 1.45))
    collider(a, "Forks", (2.1, 0.3, 2.1), (0, 0.15, -3.95))
    return a
