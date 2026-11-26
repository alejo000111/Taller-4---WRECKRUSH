import numpy as np

from wr3d import Mesh, register, S, axis_angle
from wr3d import shapes as sh
from wr3d.mesh import grid_triangles, grid_border, normalize
from wr3d.materials import Surface, rgb, wear_mask, grime_amount
from wr3d.noise import fbm, hash01, smoothstep, mix

RUST = (150, 62, 24)
RUST_DARK = (92, 38, 18)
STEEL = (120, 124, 132)
STRAP = (138, 140, 146)

FACES = [
    ("+x", (1, 0, 0), (0, 0, -1), (0, -1, 0)),
    ("-x", (-1, 0, 0), (0, 0, 1), (0, -1, 0)),
    ("+y", (0, 1, 0), (1, 0, 0), (0, 0, 1)),
    ("-y", (0, -1, 0), (1, 0, 0), (0, 0, -1)),
    ("+z", (0, 0, 1), (1, 0, 0), (0, -1, 0)),
    ("-z", (0, 0, -1), (-1, 0, 0), (0, -1, 0)),
]

FACE_YAW = {"-z": 0.0, "+x": -90.0, "+z": 180.0, "-x": 90.0}


def crate(size, counts, mat, faces=None, uv_scale=None, face_mats=None):
    h = np.asarray(size, dtype=np.float64) / 2
    parts = []
    for key, n, u3, v3 in FACES:
        if faces is not None and key not in faces:
            continue
        n, u3, v3 = (np.asarray(x, dtype=np.float64) for x in (n, u3, v3))
        ua, va, na = (int(np.argmax(np.abs(x))) for x in (u3, v3, n))
        us = np.linspace(-h[ua], h[ua], counts[ua] + 1)
        vs = np.linspace(-h[va], h[va], counts[va] + 1)
        gu, gv = np.meshgrid(us, vs, indexing="xy")
        pos = n * h[na] + gu.reshape(-1, 1) * u3 + gv.reshape(-1, 1) * v3
        uv = np.column_stack([gu.ravel(), gv.ravel()]) * (uv_scale or {}).get(key, 1.0)
        face = Mesh(pos, np.tile(n, (len(pos), 1)), uv, grid_triangles(len(vs), len(us)), wedges=grid_border(len(vs), len(us)))
        sh.orient(face)
        parts.append(face.material((face_mats or {}).get(key, mat)))
    return Mesh.merge(parts).seeded(sh.next_seed())


def crush(mesh, size, seed, ripple=0.14, jitter=0.15, sag=0.2, dent=0.6, corner=(1, 1, -1), twist=3.0):
    h = np.asarray(size, dtype=np.float64) / 2
    p = mesh.pos.copy()
    q = p / h
    o = (seed % 17) * 3.1
    n1 = fbm(p * 0.42 + o, 3, seed=seed)
    n2 = fbm(p * 0.42 + o + 11.3, 3, seed=seed + 1)
    n3 = fbm(p * 0.42 + o + 23.7, 3, seed=seed + 2)
    rows = np.round((q[:, 1] + 1) / 2 * row_count(mesh))
    swing = 0.55 + 0.45 * np.sin(q[:, 0] * 2.1 + q[:, 2] * 1.7 + seed) + 2.0 * n2
    radial = ripple * np.cos(np.pi * rows) * swing
    disp = np.column_stack([q[:, 0] * radial, np.zeros(len(p)), q[:, 2] * radial])
    disp += np.column_stack([n1, n2 * 0.6, n3]) * jitter * 2.5
    disp[:, 1] -= sag * (1 - q[:, 0] ** 2) * (1 - q[:, 2] ** 2) * np.clip(q[:, 1], 0, 1)
    c = np.asarray(corner, dtype=np.float64)
    d = np.linalg.norm(p - c * h, axis=1)
    w = np.clip(1 - d / (h.min() * 1.7), 0, 1) ** 2
    disp -= normalize(c)[None, :] * (dent * w)[:, None]
    p = p + disp
    ang = np.radians(twist) * q[:, 1]
    ca, sa = np.cos(ang), np.sin(ang)
    p[:, 0], p[:, 2] = ca * p[:, 0] + sa * p[:, 2], -sa * p[:, 0] + ca * p[:, 2]
    mesh.pos = p
    return sh.recompute_normals(mesh)


def row_count(mesh):
    ys = np.unique(np.round(mesh.pos[:, 1], 4))
    return max(len(ys) - 1, 1)


def fold(mesh, lever, at, angle, axis):
    p = mesh.pos.copy()
    hinge = np.zeros(3)
    hinge[lever] = at
    rot = axis_angle(np.eye(3)[axis], angle)[:3, :3]
    moving = p[:, lever] > at
    p[moving] = (p[moving] - hinge) @ rot.T + hinge
    mesh.pos = p
    return sh.recompute_normals(mesh)


def aim(origin, direction, up=(0.0, 1.0, 0.0)):
    z = normalize(np.asarray(direction, dtype=np.float64))
    x = np.cross(np.asarray(up, dtype=np.float64), z)
    if np.linalg.norm(x) < 1e-6:
        x = np.cross((1.0, 0.0, 0.0), z)
    x = normalize(x)
    y = np.cross(z, x)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, origin
    return m


def i_beam(length, mat, width=0.46, height=0.62, flange=0.11, web=0.09):
    w, hh, t = width / 2, height / 2, web / 2
    poly = [(-w, -hh), (w, -hh), (w, -hh + flange), (t, -hh + flange), (t, hh - flange), (w, hh - flange), (w, hh), (-w, hh), (-w, hh - flange), (-t, hh - flange), (-t, -hh + flange), (-w, -hh + flange)]
    return sh.extrude(poly, length, mat, bevel=0.025, corner_radius=0.0)


def tire(rubber, rim, radius=1.15, inner=0.56, width=0.8, arc=230.0, segments=10):
    hw = width / 2
    start = -(arc - 180.0) / 2
    prof = [(inner, -hw * 0.8), (radius * 0.86, -hw), (radius, -hw * 0.55), (radius, hw * 0.55), (radius * 0.86, hw), (inner, hw * 0.8)]
    body = sh.lathe(prof, segments, rubber, closed=True, arc=arc, start=start, smooth_angle=50)
    dish = [(0.0, -hw * 0.5), (inner * 0.55, -hw * 0.62), (inner + 0.02, -hw * 0.82), (inner + 0.02, hw * 0.82), (inner * 0.55, hw * 0.62), (0.0, hw * 0.5)]
    hub = sh.lathe(dish, segments, rim, arc=arc, start=start, smooth_angle=50)
    return [body, hub]


def chain(path, mat, link=0.95, width=0.56, wire=0.11, segments=6):
    pts = sh.catmull_rom(path, 240)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(seg)])
    pitch = link - 2 * wire - 0.05
    stations = np.arange(link / 2, arc[-1] - link / 2, pitch)
    ro = width / 2
    ring = sh.lathe([(ro - 2 * wire, -wire), (ro, -wire), (ro, wire), (ro - 2 * wire, wire)], segments, mat, closed=True, smooth_angle=50)
    ring = ring.transformed(S(1.0, 1.0, link / width))
    out = []
    side = np.array([0.0, 0.0, 1.0])
    for k, s in enumerate(stations):
        center = np.array([np.interp(s, arc, pts[:, i]) for i in range(3)])
        ahead = np.array([np.interp(min(s + 0.05, arc[-1]), arc, pts[:, i]) for i in range(3)])
        behind = np.array([np.interp(max(s - 0.05, 0.0), arc, pts[:, i]) for i in range(3)])
        d = normalize(ahead - behind)
        m = normalize(np.cross(d, side)) if k % 2 else normalize(np.cross(d, np.cross(d, side)))
        x = normalize(np.cross(m, d))
        frame = np.eye(4)
        frame[:3, 0], frame[:3, 1], frame[:3, 2], frame[:3, 3] = x, m, d, center
        out.append(ring.transformed(frame))
    return out


@register("junktower_scrap")
def _scrap(ctx, p):
    s = Surface(ctx.n)
    frame = np.asarray(p.get("frame", np.eye(4)), dtype=np.float64)
    L = ctx.P @ frame[:3, :3].T + frame[:3, 3]
    seed = int(p.get("seed", 1))
    paint = np.tile(rgb(p.get("color", RUST)), (ctx.n, 1))
    crease = np.zeros(ctx.n)
    layer = p.get("layer", 0.0)
    glass = np.zeros(ctx.n)
    trim = np.zeros(ctx.n)
    if layer > 0:
        warp = L[:, 1] + 0.3 * np.sin(L[:, 1] * 1.7 + seed)
        wobble = 0.22 * np.sin(L[:, 0] * 1.3 + L[:, 2] * 0.9 + seed) + p.get("wobble", 0.9) * ctx.noise(0.6, 3, 81)
        band = warp / layer + wobble
        idx = np.floor(band).astype(np.int64)
        frac = band - idx
        crease = 1 - smoothstep(0.0, p.get("crease_width", 0.07), np.minimum(frac, 1 - frac))
        crease = crease * (0.55 + 0.45 * hash01(idx, seed, 17, 99))
        along = L[:, 0] * 0.8 + L[:, 2] * 0.6 + 0.7 * ctx.noise(0.9, 2, 96)
        cell = idx * 131 + np.floor(along / p.get("segment", 1.7) + hash01(idx, seed, 5, 97) * 3).astype(np.int64)
        palette = [rgb(c) for c in p.get("palette", [])]
        if palette:
            use = hash01(cell, seed, 3, 91) < p.get("mix", 0.3)
            pick = np.floor(hash01(cell, seed, 7, 92) * len(palette)).astype(np.int64) % len(palette)
            paint = np.where(use[:, None], np.stack(palette)[pick], paint)
        paint = paint * (0.88 + 0.18 * hash01(cell, seed, 11, 93))[:, None]
        glass = (hash01(cell, seed, 13, 98) < p.get("glass", 0.05)) * (1 - smoothstep(0.32, 0.42, np.abs(frac - 0.5)))
        trim = (hash01(idx, seed, 19, 100) < p.get("trim", 0.2)) * (1 - smoothstep(0.03, 0.05, np.abs(frac - 0.13)))
    gray = paint.mean(1, keepdims=True)
    paint = mix(paint, np.repeat(gray, 3, 1), p.get("fade", 0.22)) * (0.86 + 0.2 * ctx.noise(1.6, 3, 82))[:, None]
    worn = wear_mask(ctx, p.get("wear", 0.5), p.get("wear_scale", 0.8))
    flake = ctx.noise(2.6, 5, 70) + 0.3 * ctx.noise(9.0, 3, 71)
    cluster = smoothstep(-0.12, 0.18, ctx.noise(0.7, 2, 72))
    limit = p.get("chips", 0.2) + 0.09 - 0.18 * cluster
    chip = smoothstep(limit, limit + 0.02, flake)
    lip = smoothstep(limit - 0.03, limit, flake) * (1 - chip)
    worn = np.maximum(worn, chip)
    rusty = smoothstep(-0.25, 0.12, ctx.noise(2.4, 4, 83) + 0.3 * (1 - ctx.AO)) * p.get("rust", 0.85)
    rust = mix(rgb(RUST), rgb(RUST_DARK), smoothstep(-0.25, 0.3, ctx.noise(8.0, 3, 84)))
    steel = rgb(STEEL)[None, :] * (0.85 + 0.2 * ctx.noise(7.0, 3, 85))[:, None]
    bare = mix(steel, rust, rusty)
    base = mix(paint, rgb(STEEL) * 1.08, lip * 0.7)
    base = mix(base, bare, worn)
    bloom = smoothstep(0.1, 0.28, ctx.noise(1.5, 4, 86)) * p.get("bloom", 0.4)
    base = mix(base, rust, bloom * 0.85)
    metal = mix(np.full(ctx.n, 0.12), 0.85, worn * (1 - rusty))
    rough = mix(np.full(ctx.n, p.get("rough", 0.58)), 0.88, np.maximum(bloom, worn * rusty))
    height = -worn * 0.004 + (rusty * worn + bloom) * ctx.noise(30.0, 2, 63) * 0.003
    streak = smoothstep(0.1, 0.22, ctx.noise_aniso(np.array([4.5, 0.32, 4.5]), 3, 88))
    streak = streak * smoothstep(-0.05, 0.2, ctx.noise(0.8, 2, 89)) * p.get("streaks", 0.5) * (1 - smoothstep(0.5, 0.8, np.abs(ctx.N[:, 1])))
    base = mix(base, rust * 0.75, streak)
    rough = mix(rough, 0.85, streak)
    strap = np.zeros(ctx.n)
    for sx in p.get("straps", ()):
        strap = np.maximum(strap, 1 - smoothstep(0.13 - ctx.texel, 0.13 + ctx.texel, np.abs(L[:, 0] - sx)))
    if strap.any():
        band_rust = smoothstep(0.0, 0.2, ctx.noise(5.0, 3, 94))
        strap_col = mix(rgb(STRAP) * (0.9 + 0.15 * ctx.noise(12.0, 2, 95))[:, None], rust, band_rust * 0.6)
        base = mix(base, strap_col, strap)
        metal = mix(metal, 0.75 * (1 - band_rust * 0.6), strap)
        rough = mix(rough, 0.45, strap)
        height = height + strap * 0.012
    base = base * (1 - crease * (1 - strap) * 0.62)[:, None]
    height = height - crease * (1 - strap) * 0.01
    if glass.any() or trim.any():
        shard = smoothstep(0.1, 0.25, ctx.noise(14.0, 2, 101))
        base = mix(base, mix(rgb((34, 44, 56)), rgb((120, 140, 156)), shard * 0.5), glass)
        rough = mix(rough, 0.18, glass)
        metal = mix(metal, 0.3, glass)
        base = mix(base, rgb((196, 200, 208)) * (0.85 + 0.2 * ctx.noise(10.0, 2, 102))[:, None], trim * (1 - worn * 0.5))
        rough = mix(rough, 0.22, trim)
        metal = mix(metal, 1.0, trim)
        height = height + trim * 0.004
    soot = smoothstep(0.1, 0.32, ctx.noise(0.5, 3, 87)) * p.get("soot", 0.35)
    base = base * (1 - soot * 0.7)[:, None]
    rough = mix(rough, 0.92, soot)
    s.base = np.clip(base, 0, 1)
    s.paint = np.zeros(ctx.n)
    s.metal = metal * (1 - soot)
    s.rough = rough
    s.height = height
    dust = smoothstep(0.55, 0.9, ctx.N[:, 1]) * smoothstep(-0.3, 0.15, ctx.noise(1.2, 3, 103)) * p.get("dust", 0.45)
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.45)) + crease * 0.2 + dust, 0, 0.85)
    return s
