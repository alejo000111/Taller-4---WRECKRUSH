import numpy as np

from wr3d import Asset, Material, Mesh, register, T, R, compose
from wr3d import shapes as sh
from wr3d.materials import Surface, rgb, wear_mask, scratch_mask, grime_amount
from wr3d.noise import fbm, smoothstep, mix
from _destructible import destructible, collider

PAINT = (150, 82, 48)
PRIMER = (124, 122, 114)
FADED_YELLOW = (214, 172, 66)
TRIM = (90, 96, 104)
GLASS = (150, 185, 200)
RUST = (150, 62, 24)
RUST_DARK = (92, 38, 18)
STEEL = (120, 124, 132)

HALF_W = 3.3
AXLE_Y = 1.16
FRONT_AXLE = -4.2
REAR_AXLE = 4.0
TRACK = 2.74
ARCH_R = 1.36
SAG = (-0.026, -0.0175)
CABIN_Y = 2.86
SILL_Y = 3.06
ROOF_Y = 4.5

TIRE = [(0.72, -0.41), (0.98, -0.46), (1.12, -0.37), (1.16, -0.2), (1.16, 0.3), (1.08, 0.42), (0.62, 0.42)]
RIM = [(0.0, -0.26), (0.2, -0.26), (0.26, -0.2), (0.52, -0.2), (0.63, -0.32), (0.76, -0.37)]
HUBCAP = [(0.0, -0.45), (0.24, -0.44), (0.45, -0.4), (0.55, -0.36), (0.57, -0.3), (0.63, -0.32), (0.76, -0.37)]
BEZEL = [(0.46, -0.02), (0.46, 0.08), (0.41, 0.13), (0.34, 0.07), (0.0, 0.07)]
LUG_R = 0.14


def field(P, scale, seed, octaves=4):
    return fbm(P * scale + seed * 7.31, octaves, 2.0, 0.5, seed)


def unsag(P, sag):
    out = P.copy()
    out[:, 1] -= sag[0] * P[:, 0] + sag[1] * P[:, 2]
    return out


def band(a, lo, hi, soft=0.02):
    return smoothstep(lo - soft, lo + soft, a) * (1 - smoothstep(hi - soft, hi + soft, a))


@register("rustycar_paint")
def rustycar_paint(ctx, p):
    s = Surface(ctx.n)
    P = unsag(ctx.P, p.get("sag", (0.0, 0.0)))
    N = ctx.N
    up = N[:, 1]
    side = 1 - np.abs(up)
    E = np.clip(ctx.E, 0, 1)
    base = np.tile(rgb(p.get("color", PAINT)), (ctx.n, 1))
    for lo, hi, col in p.get("panels", ()):
        inside = np.all((P >= np.asarray(lo)) & (P <= np.asarray(hi)), axis=1)
        base[inside] = rgb(col)
    base = mix(base, base.mean(1, keepdims=True), 0.12)
    sun = smoothstep(0.4, 0.85, up) * smoothstep(-0.25, 0.3, field(P, 0.7, 3))
    base = mix(base, base * 0.6 + rgb((196, 160, 128)) * 0.4, sun * 0.45)
    base = base * (0.84 + 0.38 * field(P, 2.2, 4))[:, None]
    stripes = p.get("stripes", ())
    if stripes:
        dx = np.min([np.abs(P[:, 0] - x) for x in stripes], axis=0)
        width = p.get("stripe_width", 0.22)
        mask = (1 - smoothstep(width - 0.02, width + 0.02, dx)) * smoothstep(0.45, 0.7, up) * smoothstep(2.88, 2.95, P[:, 1])
        mask *= 1 - smoothstep(-0.05, 0.25, field(P, 1.6, 5)) * 0.8
        mask *= 1 - smoothstep(0.1, 0.2, field(P, 7.0, 18, 3)) * 0.9
        base = mix(base, rgb(p.get("stripe_color", FADED_YELLOW)) * (0.88 + 0.25 * field(P, 6.0, 6))[:, None], mask * 0.82)
    primer = smoothstep(0.22, 0.26, field(P, 0.5, 7)) * p.get("primer", 1.0)
    wear = wear_mask(ctx, p.get("wear", 0.5))
    scr = scratch_mask(ctx, p.get("scratches", 0.35))
    low = 1 - smoothstep(0.8, 1.9, P[:, 1])
    arch_gap = np.full(ctx.n, 9.0)
    for cz in p.get("arches", ()):
        arch_gap = np.minimum(arch_gap, np.abs(np.hypot(P[:, 2] - cz, P[:, 1] - AXLE_Y) - ARCH_R))
    near_arch = 1 - smoothstep(0.05, 0.5, arch_gap)
    level = field(P, 0.8, 8) + 0.12 * field(P, 6.0, 9, 3) + 0.42 * low + 0.3 * E + 0.25 * (1 - ctx.AO) + 0.35 * near_arch + p.get("rust", 0.0)
    rust = smoothstep(0.27, 0.32, level)
    blister = smoothstep(0.17, 0.27, level) * (1 - rust)
    flake = smoothstep(0.27, 0.3, level) * (1 - smoothstep(0.3, 0.36, level))
    specks = smoothstep(0.29, 0.33, field(P, 10.0, 17, 2)) * (0.2 + low) * (1 - rust)
    rust = np.maximum(rust, specks)
    above = P + np.array([0.0, 0.55, 0.0])
    source = field(above, 0.8, 8) + 0.42 * (1 - smoothstep(0.8, 1.9, above[:, 1]))
    drip = smoothstep(0.02, 0.32, fbm(P * np.array([7.0, 0.35, 7.0]) + 3.1, 3, 2.0, 0.5, 10))
    streak = drip * smoothstep(0.12, 0.28, source) * smoothstep(0.3, 0.6, side) * (1 - rust)
    dent = np.zeros(ctx.n)
    for center, radius, depth in p.get("dents", ()):
        d = np.linalg.norm(P - np.asarray(center), axis=1) / radius
        dent += depth * np.clip(1 - d * d, 0, 1) ** 2
    rust_col = mix(rgb(RUST_DARK), rgb(RUST), smoothstep(-0.25, 0.3, field(P, 3.0, 11)) * 0.75)
    rust_col = rust_col * (0.8 + 0.35 * field(P, 9.0, 12, 3))[:, None]
    bare = np.maximum(wear, scr * 0.7)
    col = mix(base, rgb(PRIMER) * (0.9 + 0.2 * field(P, 5.0, 13, 3))[:, None], primer * 0.92)
    col = mix(col, rgb(STEEL) * 0.85, bare * (1 - primer * 0.5))
    col = mix(col, col * 0.62 + rgb(RUST_DARK) * 0.3, blister * 0.55)
    col = mix(col, rust_col, rust)
    col = mix(col, rgb((176, 84, 34)), flake * 0.7)
    col = mix(col, rgb(RUST_DARK) * 0.9, streak * 0.45)
    col = col * (1 - 0.12 * np.clip(dent / 0.1, 0, 1))[:, None]
    s.base = np.clip(col, 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.62 + 0.08 * field(P, 3.0, 14, 3) + 0.12 * primer, 0, 1)
    s.rough = mix(s.rough, 0.38, bare * (1 - rust))
    s.rough = mix(s.rough, 0.9, rust)
    s.metal = np.clip(bare * 0.8 * (1 - rust) * (1 - primer * 0.6), 0, 1)
    pits = field(P, 22.0, 15, 3)
    s.height = rust * (0.002 + pits * 0.005) + blister * 0.0015 - wear * 0.003 - scr * 0.001 - dent
    mud = (1 - smoothstep(0.55, 1.5, P[:, 1])) * (0.45 + 0.6 * field(P, 2.0, 16))
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.4)) + mud * 0.6 + streak * 0.1, 0, 0.85)
    return s


@register("rustycar_chrome")
def rustycar_chrome(ctx, p):
    s = Surface(ctx.n)
    P = ctx.P
    E = np.clip(ctx.E, 0, 1)
    var = field(P, 3.0, 41, 3)
    level = field(P, 1.3, 42) + 0.12 * field(P, 7.0, 43, 3) + 0.3 * E + 0.3 * (1 - ctx.AO) + 0.25 * smoothstep(0.2, 0.8, -ctx.N[:, 1]) + p.get("rust", 0.0)
    rust = smoothstep(0.26, 0.31, level)
    stain = smoothstep(0.1, 0.26, level) * (1 - rust)
    rust_col = mix(rgb(RUST_DARK), rgb(RUST), smoothstep(-0.25, 0.3, field(P, 4.0, 44)) * 0.8)
    col = rgb(p.get("color", (176, 180, 188))) * (0.86 + 0.25 * var + 0.12 * smoothstep(0.3, 0.9, E))[:, None]
    col = mix(col, col * 0.55 + rgb((120, 84, 50)) * 0.35, stain * 0.6)
    col = mix(col, rust_col, rust)
    s.base = np.clip(col, 0, 1)
    s.rough = mix(np.clip(0.22 + 0.1 * var + 0.3 * stain, 0, 1), 0.88, rust)
    s.metal = mix(np.full(ctx.n, 1.0), 0.1, rust)
    s.height = rust * (0.002 + 0.004 * field(P, 24.0, 45, 3)) - scratch_mask(ctx, p.get("scratches", 0.3)) * 0.001
    s.dirt = grime_amount(ctx, p.get("dirt", 0.35))
    return s


@register("rustycar_cabin")
def rustycar_cabin(ctx, p):
    s = Surface(ctx.n)
    P = unsag(ctx.P, p.get("sag", (0.0, 0.0)))
    N = ctx.N
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    seat = np.zeros(ctx.n)
    lateral = smoothstep(0.4, 0.6, np.abs(N[:, 0]))
    ahead = smoothstep(-0.4, -0.6, N[:, 2])
    behind = smoothstep(0.4, 0.6, N[:, 2])
    for zc in (-0.05, 1.7):
        back = band(z, zc - 0.4, zc + 0.4) * band(y, 2.8, 3.95)
        rest = band(z, zc - 0.25, zc + 0.2) * band(y, 4.02, 4.32)
        seat = np.maximum(seat, np.maximum(back, rest) * lateral)
    for xc in (-1.3, 1.3):
        back = band(x, xc - 0.8, xc + 0.8) * band(y, 3.15, 3.98)
        rest = band(x, xc - 0.32, xc + 0.32) * band(y, 4.06, 4.36)
        seat = np.maximum(seat, np.maximum(back, rest) * ahead)
        seat = np.maximum(seat, band(x, xc - 0.3, xc + 0.3) * band(y, 3.42, 3.68) * behind)
    seat = np.maximum(seat, band(x, -2.2, 2.2) * band(y, 2.9, 3.34) * behind)
    wheel = 1 - smoothstep(0.035, 0.06, np.abs(np.hypot(x + 1.3, y - 3.45) - 0.4))
    wheel *= smoothstep(-0.4, -0.6, N[:, 2])
    dash = (1 - smoothstep(3.12, 3.18, y)) * smoothstep(-0.4, -0.6, N[:, 2])
    shade = 0.85 + 0.35 * field(P, 3.0, 21)
    col = np.tile(rgb((28, 26, 28)), (ctx.n, 1)) * shade[:, None]
    col = mix(col, rgb((54, 50, 48)), dash)
    col = mix(col, rgb((92, 64, 46)) * (0.85 + 0.4 * field(P, 7.0, 22, 3))[:, None], seat)
    col = mix(col, rgb((16, 16, 18)), wheel)
    s.base = np.clip(col, 0, 1)
    s.rough = np.clip(0.78 - 0.2 * seat, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = seat * 0.004 + wheel * 0.006
    s.dirt = grime_amount(ctx, p.get("dirt", 0.3))
    return s


@register("rustycar_tire")
def rustycar_tire(ctx, p):
    s = Surface(ctx.n)
    axis = np.asarray(p.get("axis", (1.0, 0.0, 0.0)))
    tread = smoothstep(0.5, 0.8, 1 - np.abs(ctx.N @ axis))
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    t = (u / p.get("pitch", 0.34)) % 1.0
    lo, hi = p.get("tread_v", (0.0, 1.0))
    mid = (lo + hi) / 2 + 0.07 * np.sign(t - 0.5)
    lateral = 1 - smoothstep(0.06, 0.1, np.abs(t - 0.5))
    center = 1 - smoothstep(0.025, 0.045, np.abs(v - mid))
    groove = np.maximum(lateral * band(v, lo + 0.08, hi - 0.08, 0.01), center) * tread
    ring = (1 - smoothstep(0.012, 0.025, np.abs(v - p.get("ring_v", -1.0)))) * (1 - tread)
    age = field(ctx.P, 4.0, 31, 3)
    col = mix(rgb((48, 46, 45)), rgb((30, 30, 32)), tread)
    col = col * (0.9 + 0.3 * age)[:, None]
    col = mix(col, rgb((14, 14, 16)), np.maximum(groove, ring))
    s.base = np.clip(col, 0, 1)
    s.rough = np.clip(0.86 - 0.12 * tread * (1 - groove), 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = (1 - groove) * tread * 0.02 - ring * 0.006 + age * 0.0005
    dust = 1 - smoothstep(0.05, 0.9, ctx.P[:, 1])
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.3)) + dust * 0.55 + tread * 0.15, 0, 0.85)
    return s


def side_extrude(points, width, mat, bevel=0.0, bevel_segments=1, cap_mats=None, smooth=50.0):
    m = sh.extrude(np.asarray(points, dtype=np.float64), width, mat, bevel=bevel, bevel_segments=bevel_segments, corner_radius=0.0, cap_mats=cap_mats, smooth_angle=smooth)
    return m.transformed(R(0, -90, 0))


def top_extrude(points, height, mat, bevel=0.0):
    m = sh.extrude(np.asarray(points, dtype=np.float64), height, mat, bevel=bevel, corner_radius=0.0)
    return m.transformed(R(90, 0, 0))


def plate_box(size, mat, face, front_mat=None):
    faces = [face, "+x", "-x", "+y", "-y"]
    return sh.rounded_box(size, 0.0, 1, mat, faces=faces, face_mats={face: front_mat} if front_mat else None)


def sheet(poly):
    poly = np.asarray(poly, dtype=np.float64)
    x, y = poly[:, 0], poly[:, 1]
    if np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y) < 0:
        poly = poly[::-1]
    tri = sh.triangulate(poly)
    pos = np.column_stack([poly, np.zeros(len(poly))])
    faces = [sh.orient(Mesh(pos, np.tile([0.0, 0.0, sign], (len(poly), 1)), poly, tri)) for sign in (1.0, -1.0)]
    return Mesh.merge(faces)


def side_sheet(poly, x):
    return sheet(poly).transformed(compose(T(x, 0, 0), R(0, -90, 0)))


def slanted_sheet(width, base_y, base_z, slope, outward):
    angle = np.degrees(np.arctan(slope))
    length = (ROOF_Y - base_y) / np.cos(np.radians(angle))
    normal = np.array([0.0, np.sin(np.radians(angle)), outward * np.cos(np.radians(angle))])
    origin = np.array([0.0, base_y, base_z]) + normal * 0.035
    half = width / 2
    return sheet([(-half, 0.0), (half, 0.0), (half, length), (-half, length)]).transformed(compose(T(*origin), R(-outward * angle, 0, 0)))


def arc(cz, radius, start_y, end_y, count):
    a0 = np.pi - np.arcsin((start_y - AXLE_Y) / radius)
    a1 = np.arcsin((end_y - AXLE_Y) / radius)
    return [(cz + radius * np.cos(t), AXLE_Y + radius * np.sin(t)) for t in np.linspace(a0, a1, count)]


def body_outline():
    pts = [(-6.42, 0.9, 0.12)]
    pts += [(z, y, 0.0) for z, y in arc(FRONT_AXLE, ARCH_R, 0.9, 0.74, 9)]
    pts += [(z, y, 0.0) for z, y in arc(REAR_AXLE, ARCH_R, 0.74, 0.9, 9)]
    pts += [(6.42, 0.9, 0.12), (6.62, 1.1, 0.1), (6.62, 2.48, 0.12), (6.46, 2.74, 0.16), (3.56, 2.84, 0.1), (3.3, CABIN_Y + 0.02, 0.0),
            (-2.4, CABIN_Y + 0.02, 0.0), (-2.62, 2.78, 0.1), (-6.3, 2.74, 0.16), (-6.6, 2.5, 0.12), (-6.62, 1.1, 0.1)]
    pts = np.asarray(pts)
    return sh.round_polyline(pts[:, :2], pts[:, 2], 1, closed=True)


def arch_lip(cz):
    return arc(cz, ARCH_R + 0.13, 0.92, 0.92, 9) + arc(cz, ARCH_R - 0.03, 0.92, 0.92, 9)[::-1]


def windshield_z(y):
    return -2.35 + (y - 2.82) * 0.891


def rear_glass_z(y):
    return 3.45 - (y - 2.82) * 0.718


def c_pillar_z(y):
    return 2.05 - (y - 2.84) / 1.72 * 0.25


def arc_from_end(profile, index):
    pts = np.asarray(profile, dtype=np.float64)
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1)[index:].sum())


def side_decals(sign):
    def at(z, y):
        return (z if sign < 0 else -z, -y)

    out = []
    for z0, z1 in ((-2.3, 0.6), (0.62, 2.6)):
        out.append({"type": "rect", "center": at((z0 + z1) / 2, 2.05), "size": (z1 - z0, 2.14), "outline": 0.035, "darken": 0.65, "raise": -0.008})
        out.append({"type": "rect", "center": at(z1 - 0.36, 2.41), "size": (0.52, 0.2), "radius": 0.06, "darken": 0.45, "raise": -0.006})
        out.append({"type": "rect", "center": at(z1 - 0.36, 2.38), "size": (0.42, 0.08), "radius": 0.03, "color": (196, 198, 204), "metal": 1.0, "rough": 0.3, "wear": 0.4, "raise": 0.004})
        out.append({"type": "circle", "center": at(z1 - 0.72, 2.38), "radius": 0.035, "color": (40, 40, 44), "wear": 0.0})
    out.append({"type": "circle", "center": at(-0.85, 1.72), "radius": 0.62, "color": (226, 212, 178), "wear": 0.6})
    out.append({"type": "text", "text": "77", "center": at(-0.85, 1.74), "height": 0.66, "color": (40, 32, 28), "font": "impact", "wear": 0.55})
    out.append({"type": "rect", "center": at(-6.08, 1.95), "size": (0.38, 0.14), "radius": 0.03, "color": (232, 140, 40), "rough": 0.2, "wear": 0.2})
    out.append({"type": "rect", "center": at(6.12, 1.95), "size": (0.38, 0.14), "radius": 0.03, "color": (176, 32, 26), "rough": 0.2, "wear": 0.2})
    if sign < 0:
        out.append({"type": "circle", "center": at(5.75, 2.2), "radius": 0.19, "darken": 0.6, "raise": -0.006})
        out.append({"type": "circle", "center": at(5.75, 2.2), "radius": 0.15, "color": (150, 152, 158), "metal": 1.0, "rough": 0.4, "wear": 0.5})
    return out


def materials():
    dents = [((-3.35, 1.9, -5.3), 0.8, 0.12), ((-3.35, 1.55, 1.6), 0.62, 0.1), ((0.7, 4.8, 0.7), 0.95, 0.08),
             ((3.35, 2.15, -1.3), 0.55, 0.08), ((3.35, 1.8, 5.8), 0.6, 0.1), ((-1.1, 3.2, -4.4), 0.75, 0.06), ((2.2, 2.0, 6.75), 0.5, 0.08)]
    panels = [((-3.6, 0.5, -6.8), (-2.98, 3.0, -2.32), PRIMER), ((2.98, 0.9, 0.64), (3.6, 3.0, 2.58), FADED_YELLOW)]
    paint = Material("rustycar_paint", color=PAINT, sag=SAG, panels=panels, dents=dents, arches=(FRONT_AXLE, REAR_AXLE), stripes=(-0.62, 0.62), wear=0.5, scratches=0.35, dirt=0.4, dirt_color=(70, 54, 40))
    m = {"paint": paint, "left": paint.but(decals=side_decals(-1)), "right": paint.but(decals=side_decals(1))}
    m["fascia"] = paint.but(decals=[
        {"type": "rect", "center": (0.0, -0.02), "size": (3.1, 0.74), "radius": 0.08, "color": (22, 22, 24), "wear": 0.15, "raise": -0.02},
        *[{"type": "rect", "center": (0.0, -0.27 + k * 0.135), "size": (2.96, 0.05), "color": (168, 170, 176), "metal": 1.0, "rough": 0.35, "wear": 0.45, "raise": 0.004} for k in range(5)],
        {"type": "circle", "center": (0.0, -0.02), "radius": 0.17, "color": (200, 202, 208), "metal": 1.0, "rough": 0.3, "wear": 0.3},
        {"type": "text", "text": "W", "center": (0.0, -0.02), "height": 0.18, "color": (40, 40, 44), "font": "black", "wear": 0.2},
        {"type": "rect", "center": (2.3, 0.46), "size": (0.6, 0.14), "radius": 0.04, "color": (232, 140, 40), "rough": 0.2, "wear": 0.25},
        {"type": "rect", "center": (-2.3, 0.46), "size": (0.6, 0.14), "radius": 0.04, "color": (232, 140, 40), "rough": 0.2, "wear": 0.25},
    ])
    m["tail"] = paint.but(decals=[
        {"type": "text", "text": "BRUISER", "center": (0.0, 0.02), "height": 0.26, "color": (196, 198, 204), "font": "black", "metal": 1.0, "rough": 0.3, "wear": 0.45},
        {"type": "circle", "center": (0.0, 0.3), "radius": 0.06, "color": (40, 40, 44), "wear": 0.0},
    ])
    m["interior"] = Material("rustycar_cabin", sag=SAG, dirt=0.3)
    m["trim"] = Material("metal", color=TRIM, rough=0.45, polish=0.5, dirt=0.4, scratches=0.3)
    m["chrome"] = Material("rustycar_chrome", color=(170, 174, 182))
    m["liner"] = Material("rubber", color=(28, 26, 26), pattern="dots", freq=5.0, depth=0.004, dirt=0.5)
    m["tail_lens"] = Material("glossy", color=(168, 22, 20), rough=0.18, dirt=0.25, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (1.4, 0.04), "darken": 0.6, "raise": -0.004},
        {"type": "rect", "center": (0.0, 0.0), "size": (0.36, 0.38), "color": (232, 228, 214), "rough": 0.2, "wear": 0.2},
    ])
    m["plate"] = Material("paint", color=(236, 226, 190), under=(150, 152, 158), wear=0.4, scratches=0.4, dirt=0.5, rough=0.5, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (1.24, 0.5), "radius": 0.05, "outline": 0.035, "color": (40, 52, 96), "wear": 0.3},
        {"type": "text", "text": "WRK-77", "center": (0.0, 0.04), "height": 0.27, "color": (36, 46, 92), "font": "black", "wear": 0.3},
        {"type": "text", "text": "SCRAPYARD", "center": (0.0, -0.17), "height": 0.07, "color": (176, 50, 36), "font": "bold", "wear": 0.3},
        {"type": "rivets", "points": [(-0.45, -0.17), (0.45, -0.17)], "radius": 0.03, "color": (150, 150, 156), "height": 0.008},
    ])
    m["tire"] = Material("rustycar_tire", tread_v=(arc_from_end(TIRE, 4), arc_from_end(TIRE, 3)), ring_v=arc_from_end(TIRE, 1) + 0.06, pitch=0.34, dirt=0.35, dirt_color=(104, 88, 68))
    rim_total = arc_from_end(RIM, 0)
    lugs = [(LUG_R * (0.3 + k * 2 * np.pi / 5), rim_total - LUG_R) for k in range(5)]
    m["rim"] = Material("rustycar_chrome", color=(98, 100, 108), rust=0.1, decals=[
        {"type": "rivets", "points": lugs, "radius": 0.035, "color": (130, 132, 138), "height": 0.012},
        {"type": "rect", "center": (np.pi * LUG_R, rim_total - 0.035), "size": (2 * np.pi * LUG_R + 0.2, 0.07), "darken": 0.75, "raise": -0.01},
    ])
    cap_total = arc_from_end(HUBCAP, 0)
    m["hubcap"] = Material("rustycar_chrome", color=(206, 210, 218), rust=-0.06, decals=[
        {"type": "rect", "center": (2.0, cap_total - 0.12), "size": (5.0, 0.02), "darken": 0.5, "raise": -0.004},
        {"type": "rect", "center": (2.0, cap_total - 0.4), "size": (5.0, 0.025), "darken": 0.45, "raise": -0.004},
    ])
    m["lamp"] = Material("rustycar_chrome", color=(196, 200, 208), rust=-0.05)
    m["lamp_broken"] = Material("rustycar_chrome", color=(170, 174, 182), rust=0.1, decals=[
        {"type": "rect", "center": (1.5, 0.17), "size": (3.4, 0.34), "darken": 0.82, "raise": -0.01},
    ])
    m["exhaust"] = Material("rustycar_chrome", color=(90, 90, 96), rust=0.25, decals=[
        {"type": "rect", "center": (0.4, 0.04), "size": (1.0, 0.08), "darken": 0.85, "raise": -0.01},
    ])
    return m


def lower_body(m):
    parts = [side_extrude(body_outline(), 2 * HALF_W, m["paint"], bevel=0.14, cap_mats=[m["left"], m["right"]])]
    for sx in (-1, 1):
        for cz in (FRONT_AXLE, REAR_AXLE):
            parts.append(side_extrude(arch_lip(cz), 0.14, m["chrome"]).transformed(T(sx * 3.28, 0, 0)))
        face = "+x" if sx > 0 else "-x"
        parts.append(sh.rounded_box((0.05, 0.07, 12.8), 0.0, 1, m["trim"], faces=[face, "+y", "-y", "+z", "-z"]).transformed(T(sx * 3.31, 2.6, 0.0)))
        parts.append(sh.rounded_box((0.06, 0.18, 5.2), 0.0, 1, m["trim"], faces=[face, "+y", "-y", "+z", "-z"]).transformed(T(sx * 3.31, 0.86, -0.12)))
    parts.append(plate_box((6.0, 1.08, 0.1), m["paint"], "-z", m["fascia"]).transformed(T(0, 1.96, -6.67)))
    parts.append(plate_box((5.8, 0.7, 0.08), m["paint"], "+z", m["tail"]).transformed(T(0, 2.08, 6.66)))
    for x in (-2.3, 2.3):
        parts.append(plate_box((1.3, 0.48, 0.1), m["tail_lens"], "+z").transformed(T(x, 2.06, 6.7)))
    for x, mat in ((2.3, m["lamp"]), (-2.3, m["lamp_broken"])):
        parts.append(sh.lathe(BEZEL, 12, mat, smooth_angle=40).transformed(compose(T(x, 2.04, -6.7), R(-90, 0, 0))))
    outline = [(-3.0, 6.95), (3.0, 6.95), (3.3, 6.78), (3.36, 6.2), (3.24, 6.2), (3.2, 6.62), (2.95, 6.66), (-2.95, 6.66), (-3.2, 6.62), (-3.24, 6.2), (-3.36, 6.2), (-3.3, 6.78)]
    front = top_extrude([(x, -z) for x, z in outline], 0.44, m["chrome"], bevel=0.05)
    rear = top_extrude(outline, 0.44, m["chrome"], bevel=0.05)
    parts.append(front.transformed(compose(T(-3.3, 1.18, -6.8), R(0, -1.2, -3.0), T(3.3, 0, 6.8))))
    parts.append(rear.transformed(compose(T(0, 1.16, 0), R(0, -0.8, 1.2))))
    parts.append(plate_box((1.3, 0.52, 0.04), m["plate"], "+z").transformed(T(0, 1.18, 6.97)))
    hood = side_extrude([(-2.55, 2.8), (-4.6, 3.04), (-6.46, 2.9), (-6.43, 3.01), (-4.6, 3.16), (-2.5, 2.91)], 6.0, m["paint"], bevel=0.05, smooth=30)
    lift = np.clip((-2.55 - hood.pos[:, 2]) / 3.9, 0, 1)
    hood.pos[:, 1] += 0.07 * (-hood.pos[:, 0] / 3.0) * lift
    parts.append(hood)
    parts.append(side_extrude([(3.62, 2.86), (6.38, 3.0), (6.5, 2.86), (6.55, 2.94), (6.43, 3.12), (3.62, 2.97)], 6.0, m["paint"], bevel=0.05, smooth=30))
    for z in (FRONT_AXLE, REAR_AXLE):
        parts.append(sh.rounded_box((4.4, 1.4, 2.5), 0.0, 1, m["liner"], faces=["+x", "-x", "-y", "+z", "-z"]).transformed(T(0, 1.8, z)))
    head = sh.rounded_box((0.16, 0.3, 0.42), 0.0, 1, m["trim"], face_mats={"+z": m["chrome"]})
    arm = sh.rounded_box((0.2, 0.07, 0.08), 0.0, 1, m["trim"])
    parts.append(arm.transformed(compose(T(3.36, 2.86, -2.0), R(0, 0, 35))))
    parts.append(head.transformed(T(3.42, 3.06, -2.0)))
    parts.append(arm.transformed(compose(T(-3.34, 2.78, -2.0), R(0, 0, 20))))
    parts.append(head.transformed(compose(T(-3.4, 2.56, -2.04), R(8, 0, -28))))
    parts.append(sh.cylinder(0.1, 0.8, m["exhaust"], bevel=0.0, segments=8).transformed(compose(T(1.9, 0.66, 6.5), R(90, 0, 0))))
    return parts


def cabin(m):
    core = [(-2.35, 2.82), (3.45, 2.82), (rear_glass_z(4.56), 4.56), (windshield_z(4.56), 4.56)]
    roof = [(windshield_z(ROOF_Y) - 0.12, ROOF_Y), (rear_glass_z(ROOF_Y) + 0.1, ROOF_Y), (rear_glass_z(4.78) + 0.02, 4.78), (windshield_z(4.78) + 0.06, 4.78)]
    parts = [side_extrude(core, 5.12, m["interior"]), side_extrude(roof, 5.86, m["paint"], bevel=0.12, bevel_segments=2)]
    a_pillar = [(windshield_z(2.84) - 0.07, 2.84), (windshield_z(2.84) + 0.25, 2.84), (windshield_z(4.56) + 0.25, 4.56), (windshield_z(4.56) - 0.07, 4.56)]
    b_pillar = [(0.45, 2.84), (0.78, 2.84), (0.78, 4.56), (0.45, 4.56)]
    c_pillar = [(c_pillar_z(2.84), 2.84), (rear_glass_z(2.84) + 0.07, 2.84), (rear_glass_z(4.56) + 0.07, 4.56), (c_pillar_z(4.56), 4.56)]
    z0, z1 = windshield_z(SILL_Y), rear_glass_z(SILL_Y)
    for sx in (-1, 1):
        for poly in (a_pillar, b_pillar, c_pillar):
            parts.append(side_extrude(poly, 0.38, m["paint"]).transformed(T(sx * 2.69, 0, 0)))
        sill = sh.rounded_box((0.4, SILL_Y - 2.84, z1 - z0), 0.0, 1, m["trim"], faces=["+x", "-x", "+y", "-z", "+z"])
        parts.append(sill.transformed(T(sx * 2.7, (SILL_Y + 2.84) / 2, (z0 + z1) / 2)))
    return parts


def glazing():
    top = ROOF_Y + 0.02
    front_pane = [(windshield_z(SILL_Y) + 0.25, SILL_Y), (0.45, SILL_Y), (0.45, top), (windshield_z(ROOF_Y) + 0.25, top)]
    rear_pane = [(0.78, SILL_Y), (c_pillar_z(SILL_Y), SILL_Y), (c_pillar_z(ROOF_Y), top), (0.78, top)]
    front_shards = [(-1.86, SILL_Y - 0.02), (0.44, SILL_Y - 0.02), (0.44, 3.52), (0.28, 3.3), (0.06, 3.66), (-0.2, 3.24), (-0.62, 3.42), (-0.92, 3.14), (-1.3, 3.34), (-1.6, 3.12), (-1.86, 3.24)]
    rear_shards = [(0.8, SILL_Y - 0.02), (1.99, SILL_Y - 0.02), (1.96, 3.46), (1.72, 3.2), (1.42, 3.5), (1.15, 3.16), (0.8, 3.36)]
    parts = [
        side_sheet(front_pane, -2.74),
        side_sheet(rear_pane, 2.74),
        side_sheet(front_shards, 2.74),
        side_sheet([(0.44, top), (0.44, 4.0), (0.18, top)], 2.74),
        side_sheet(rear_shards, -2.74),
        side_sheet([(1.9, top), (c_pillar_z(4.2), 4.2), (1.5, top)], -2.74),
        slanted_sheet(5.0, CABIN_Y, windshield_z(CABIN_Y), 0.891, -1),
        slanted_sheet(5.0, CABIN_Y, rear_glass_z(CABIN_Y), 0.718, 1),
    ]
    lens = sh.lathe([(0.35, 0.07), (0.24, 0.12), (0.0, 0.14)], 12, None, smooth_angle=60)
    parts.append(lens.transformed(compose(T(2.3, 2.04, -6.7), R(-90, 0, 0))))
    parts.append(sheet([(-0.22, -0.3), (0.12, -0.33), (0.05, 0.02)]).transformed(T(-2.22, 2.04, -6.79)))
    return parts


def tumblehome(mesh, k=0.042, y0=2.84):
    out = mesh.copy()
    rise = np.clip(out.pos[:, 1] - y0, 0, None)
    scale = 1 - k * rise
    x = out.pos[:, 0].copy()
    out.pos[:, 0] = x * scale
    lean = np.where(out.pos[:, 1] > y0, k * x, 0.0)
    out.nrm[:, 1] += lean * out.nrm[:, 0] / scale
    out.nrm[:, 0] /= scale
    out.nrm /= np.linalg.norm(out.nrm, axis=1, keepdims=True)
    return out


def squash(mesh, x, contact=0.1, bulge=0.55):
    out = mesh.copy()
    y = out.pos[:, 1].copy()
    depth = np.clip(contact - y, 0, None)
    out.pos[:, 1] = np.where(y < contact, contact * np.exp((y - contact) / contact), y)
    out.pos[:, 0] = x + (out.pos[:, 0] - x) * (1 + bulge * np.clip(depth / 0.3, 0, 1))
    return out


def wheel(m, x, z, hubcap, flat=0.0):
    turn = R(0, 0, 90) if x > 0 else R(0, 0, -90)
    place = compose(T(x, AXLE_Y - flat, z), turn)
    if hubcap:
        rim = sh.lathe(HUBCAP, 10, m["hubcap"], smooth_angle=40)
    else:
        rim = sh.lathe(RIM, 10, m["rim"], smooth_angle=40, r_ref=LUG_R)
    tire = sh.lathe(TIRE, 16, m["tire"], smooth_angle=50).transformed(place)
    if flat > 0:
        tire = squash(tire, x)
    return [tire, rim.transformed(place)]


def build():
    a = Asset("RustyCar", budget=3000, atlas=1024, ao_radius=1.0, edge_width=0.1, preview_radius=7.9,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.45)
    m = materials()
    shear = np.eye(4)
    shear[1, 0], shear[1, 2] = SAG
    a.add("Body", [part.transformed(shear) for part in lower_body(m)])
    a.add("Body", [tumblehome(part).transformed(shear) for part in cabin(m)])
    a.add("Glass", [tumblehome(part).transformed(shear) for part in glazing()])
    for x, z, hubcap, flat in ((-TRACK, FRONT_AXLE, True, 0.0), (TRACK, FRONT_AXLE, True, 0.0), (-TRACK, REAR_AXLE, False, 0.0), (TRACK, REAR_AXLE, False, 0.3)):
        a.add("Body", wheel(m, x, z, hubcap, flat))
    destructible(a, "ScrapYard")
    collider(a, "Hitbox", (6.8, 2.6, 13.6), (0, 1.6, 0))
    collider(a, "Cabin", (5.6, 1.8, 4.4), (0, 3.78, 0.5))
    return a
