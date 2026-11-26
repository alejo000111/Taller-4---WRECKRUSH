import numpy as np

from wr3d import Asset, Chart, Material, Mesh, T, R, S, compose, register
from wr3d import shapes as sh
from wr3d.materials import Surface, rgb, wear_mask, scratch_mask, grime_amount, apply_decals
from wr3d.mesh import grid_triangles
from wr3d.noise import smoothstep
from _destructible import destructible, collider

PAINT = (180, 70, 40)
RUST = (120, 50, 30)
RUST_DARK = (92, 38, 18)
RUST_LIGHT = (150, 62, 24)
YELLOW = (255, 210, 31)
CHARCOAL = (42, 44, 52)
STEEL = (120, 124, 132)
CREAM = (234, 224, 198)
INK = (24, 22, 22)

WALL_BOTTOM, WALL_TOP = 0.7, 9.45
WALL_MID = (WALL_BOTTOM + WALL_TOP) / 2
WALL_HEIGHT = WALL_TOP - WALL_BOTTOM
ROOF_Y = 9.8
DOOR_Z = 11.5
BAR_Z = 11.82
BARS = (-3.0, -1.0, 1.0, 3.0)
POCKETS = (-4.1, 4.1)


@register("scrapcontainer_paint")
def weathered_paint(ctx, p):
    s = Surface(ctx.n)
    y = ctx.P[:, 1]
    up = np.clip(ctx.N[:, 1], 0, 1)
    side = 1 - np.abs(ctx.N[:, 1])
    color = rgb(p.get("color", PAINT))
    pale = color + (rgb((222, 156, 112)) - color) * 0.45
    broad = ctx.noise(0.3, 3, 61)
    fine = ctx.noise(7.0, 3, 62)
    fade = np.clip(0.3 + 0.9 * broad + 0.25 * up + 0.2 * smoothstep(3.0, 10.0, y), 0, 1) * p.get("fade", 0.5)
    s.base = (color[None, :] + (pale - color)[None, :] * fade[:, None]) * (0.93 + 0.1 * fine)[:, None]
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.5 + 0.08 * fine + 0.14 * fade, 0, 1)
    s.metal = np.full(ctx.n, 0.06)
    s.height = ctx.noise(40.0, 2, 66) * 0.0003
    apply_decals(ctx, s, p.get("stencils", ()))

    chips = wear_mask(ctx, p.get("wear", 0.5), p.get("wear_scale", 1.0))
    blot = ctx.noise(p.get("patch_scale", 0.5), 4, 63) + 0.35 * ctx.noise(5.0, 3, 64) + up * p.get("top_rust", 0.15)
    t = 0.42 - 0.36 * p.get("patches", 0.4)
    patches = smoothstep(t, t + 0.04, blot)
    halo = smoothstep(t - 0.12, t, blot) * (1 - patches)
    scr = scratch_mask(ctx, p.get("scratches", 0.3))
    loss = np.clip(np.maximum(chips, patches) + scr * 0.45, 0, 1)
    tone = smoothstep(-0.3, 0.3, ctx.noise(4.0, 3, 67))
    rust = rgb(RUST)[None, :] + (rgb(RUST_DARK) - rgb(RUST))[None, :] * tone[:, None]
    flecks = smoothstep(0.15, 0.45, ctx.noise(12.0, 2, 68)) * 0.55
    rust = rust + (rgb(RUST_LIGHT)[None, :] - rust) * flecks[:, None]
    stain = rgb(RUST_LIGHT) * 0.85
    s.base = s.base + (stain[None, :] - s.base) * (halo * 0.45)[:, None]
    s.base = s.base + (rust - s.base) * loss[:, None]

    streak = ctx.noise_aniso(np.array([2.4, 0.14, 2.4]), 3, 69)
    from_top = 0.25 + 0.75 * smoothstep(1.0, 9.6, y)
    drip = smoothstep(0.0, 0.32, streak) * side * from_top * p.get("streaks", 0.6)
    streak_col = rgb(RUST_LIGHT) * 0.75
    s.base = s.base + (streak_col[None, :] - s.base) * (drip * 0.6)[:, None]

    low = (1 - smoothstep(0.0, p.get("grime_height", 2.6), y)) * (0.55 + 0.45 * smoothstep(-0.3, 0.3, ctx.noise(1.4, 3, 70)))
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.3)) + low * p.get("grime", 0.5), 0, 0.85)
    s.rough = s.rough + (0.86 - s.rough) * loss
    s.rough = s.rough + (0.72 - s.rough) * drip
    s.metal = s.metal + (0.14 - s.metal) * loss
    s.height = s.height - loss * p.get("chip_depth", 0.005) + patches * ctx.noise(26.0, 3, 71) * 0.004
    ripple = p.get("ripple")
    if ripple:
        axis, pitch, depth = ripple
        wave = 0.5 + 0.5 * np.cos(ctx.U[:, axis] / pitch * 2 * np.pi)
        s.height = s.height + wave * depth
        s.base = s.base * (0.95 + 0.06 * wave)[:, None]
    s.base = np.clip(s.base, 0, 1)
    s.tint = np.ones(ctx.n)
    return s


def paint(color=PAINT, **params):
    return Material("scrapcontainer_paint", color=color, **params)


def corrugation(span, periods, depth, crest=0.34, slope=0.14):
    pitch = span / periods
    trough = 1.0 - crest - 2 * slope
    pts = [(-span / 2, 0.0)]
    for i in range(periods):
        a = -span / 2 + pitch * (i + trough / 2)
        b = a + pitch * slope
        c = b + pitch * crest
        pts += [(a, 0.0), (b, depth), (c, depth), (c + pitch * slope, 0.0)]
    pts.append((span / 2, 0.0))
    return np.asarray(pts)


def sheet(width, height, periods, depth, mat, levels=(0.0, 1.0), ribs="vertical", dents=(), crest=0.34, slope=0.14, pieces=1):
    span, run = (width, height) if ribs == "vertical" else (height, width)
    prof = corrugation(span, periods, depth, crest, slope)
    rows = [(f - 0.5) * run for f in levels]
    pos, tris, wedges, owner = [], [], [], []
    for (t0, z0), (t1, z1) in zip(prof[:-1], prof[1:]):
        base = len(pos)
        piece = min(int((t0 + t1 + span) / (2 * span) * pieces), pieces - 1)
        for r in rows:
            pos += [(t0, r, z0), (t1, r, z1)]
            owner += [piece, piece]
        tris.append(grid_triangles(len(rows), 2, base))
        for col, z in ((0, z0), (1, z1)):
            if z > 0:
                wedges += [(base + j * 2 + col, base + (j + 1) * 2 + col) for j in range(len(rows) - 1)]
    pos = np.asarray(pos, dtype=np.float64)
    if ribs != "vertical":
        pos = pos[:, [1, 0, 2]]
    for cx, cy, radius, amount in dents:
        falloff = np.exp(-((pos[:, 0] - cx) ** 2 + (pos[:, 1] - cy) ** 2) / (radius * radius))
        pos[:, 2] -= amount * falloff * (0.6 + 0.4 * pos[:, 2] / depth)
    tri = np.concatenate(tris)
    a, b, c = pos[tri[:, 0]], pos[tri[:, 1]], pos[tri[:, 2]]
    fn = np.cross(b - a, c - a)
    if fn[:, 2].sum() < 0:
        tri = tri[:, ::-1].copy()
        fn = -fn
    nrm = np.zeros_like(pos)
    for k in range(3):
        np.add.at(nrm, tri[:, k], fn)
    uv = np.column_stack([pos[:, 0], -pos[:, 1]])
    mesh = Mesh(pos, nrm, uv, tri, vchart=owner, charts=[Chart(mat) for _ in range(pieces)], wedges=np.asarray(wedges, dtype=np.int64))
    seed = sh.next_seed()
    for chart in mesh.charts:
        chart.seed = seed
    return mesh.clean()


def shelve(sizes, row, gap):
    shelves, spots = [], {}
    for key in sorted(sizes, key=lambda k: (-sizes[k][1], -sizes[k][0])):
        w, h = sizes[key]
        spot = next((shelf for shelf in shelves if shelf[2] + w <= row + 1e-6 and h <= shelf[1] + 1e-6), None)
        if spot is None:
            top = shelves[-1][0] + shelves[-1][1] + gap if shelves else 0.0
            spot = [top, h, 0.0]
            shelves.append(spot)
        spots[key] = (spot[2], spot[0])
        spot[2] += w + gap
    return spots, shelves[-1][0] + shelves[-1][1]


def fuse(meshes, gap=0.08, scale=1.0, height=None):
    mesh = Mesh.merge(meshes)
    groups = {}
    for ci, chart in enumerate(mesh.charts):
        groups.setdefault(id(chart.material), []).append(ci)
    boxes = {}
    for ci in range(len(mesh.charts)):
        sel = mesh.vchart == ci
        boxes[ci] = (sel, mesh.uv[sel].min(0), mesh.uv[sel].max(0))
    remap = np.zeros(len(mesh.charts), dtype=np.int64)
    charts, centers = [], {}
    for cids in groups.values():
        remap[cids] = len(charts)
        charts.append(mesh.charts[cids[0]])
        if len(cids) == 1:
            continue
        sizes = {}
        for ci in cids:
            sel, lo, hi = boxes[ci]
            local = (mesh.uv[sel] - lo) * scale
            w, h = (hi - lo) * scale
            if h > w * 1.05:
                local = np.column_stack([local[:, 1], w - local[:, 0]])
                w, h = h, w
            mesh.uv[sel] = local
            sizes[ci] = (w, h)
        row = max(max(w for w, _ in sizes.values()), np.sqrt(sum(w * h for w, h in sizes.values())) * 1.05)
        spots, tall = shelve(sizes, row, gap)
        while height and tall > height:
            row *= 1.03
            spots, tall = shelve(sizes, row, gap)
        for ci, (x, y) in spots.items():
            w, h = sizes[ci]
            mesh.uv[boxes[ci][0]] += np.array([x, y])
            centers[ci] = (x + w / 2, y + h / 2)
    mesh.vchart = remap[mesh.vchart]
    mesh.charts = charts
    return mesh, centers


def slab(size, center, mat, faces, **kw):
    return sh.rounded_box(size, 0.0, 1, mat, faces=faces, **kw).transformed(T(*center))


def corner_post(mat, height, y0):
    outline = [(4.05, 11.05), (4.95, 11.05), (4.95, 11.66), (4.66, 11.95), (4.05, 11.95)]
    post = sh.extrude(outline, height, mat, bevel=0.0, corner_radius=0.0, caps=False)
    return post.transformed(compose(T(0, y0 + height / 2, 0), R(90, 0, 0)))


def castings():
    blank = Material("scrapcontainer_paint")
    parts = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in (0.4, 9.6):
                parts.append(slab((1.0, 0.8, 1.0), (sx * 4.5, y, sz * 11.5), blank, ["+x", "-x", "+y", "+z", "-z"]))
    mesh, centers = fuse(parts, gap=0.16)
    holes = []
    for center in centers.values():
        holes.append({"type": "rect", "center": center, "size": (0.54, 0.3), "radius": 0.15, "darken": 0.9, "raise": -0.03})
        holes.append({"type": "rect", "center": center, "size": (0.66, 0.42), "radius": 0.21, "outline": 0.05, "darken": 0.35, "raise": 0.004})
    return mesh.material(paint(CHARCOAL, wear=0.6, patches=0.3, fade=0.25, stencils=holes))


def bottom_rail(sx, mat, cavity):
    out = "+x" if sx > 0 else "-x"
    x = sx * 4.65
    parts = [slab((0.5, 0.86, 11.05), (x, 0.47, zc), mat, ["+y"]) for zc in (-5.525, 5.525)]
    edges = [-11.05, POCKETS[0] - 0.8, POCKETS[0] + 0.8, POCKETS[1] - 0.8, POCKETS[1] + 0.8, 11.05]
    for z0, z1 in zip(edges[0::2], edges[1::2]):
        parts.append(slab((0.5, 0.86, z1 - z0), (x, 0.47, (z0 + z1) / 2), mat, [out]))
    for zc in POCKETS:
        parts.append(slab((0.5, 0.28, 1.6), (x, 0.76, zc), mat, [out]))
        parts.append(slab((0.5, 0.16, 1.6), (x, 0.12, zc), mat, [out]))
        pocket = sh.rounded_box((0.45, 0.42, 1.6), 0.0, 1, cavity, faces=["-x" if sx > 0 else "+x", "+y", "-y", "+z", "-z"])
        parts.append(pocket.flipped().transformed(T(sx * 4.675, 0.41, zc)))
    return parts


def roof(mat):
    plate = sh.plane((9.2, 23.2), mat, divisions=(7, 18))
    x, z = plate.pos[:, 0], plate.pos[:, 2]
    sag = 0.14 * (1 - (x / 4.6) ** 2) * (1 - (z / 11.6) ** 2)
    for cx, cz, radius, depth in ((1.4, 4.2, 1.9, 0.32), (-2.1, -6.4, 1.5, 0.24), (2.6, -2.0, 1.2, 0.12), (-1.2, 8.6, 1.1, 0.1)):
        sag = sag + depth * np.exp(-((x - cx) ** 2 + (z - cz) ** 2) / (radius * radius))
    plate.pos[:, 1] = ROOF_Y - sag
    plate.uv *= 0.65
    return sh.recompute_normals(plate)


def side_stencils():
    return [
        {"type": "circle", "center": (-6.6, -1.25), "radius": 1.25, "color": YELLOW, "wear": 0.2},
        {"type": "circle", "center": (-6.6, -1.25), "radius": 0.98, "color": CHARCOAL, "wear": 0.2},
        {"type": "text", "text": "SC", "center": (-6.6, -1.22), "height": 0.95, "color": YELLOW, "font": "black", "wear": 0.2},
        {"type": "text", "text": "SCRAP CO.", "center": (1.0, -1.35), "height": 2.1, "color": CREAM, "font": "impact", "wear": 0.25},
        {"type": "rect", "center": (1.0, 0.2), "size": (9.6, 0.62), "color": CHARCOAL, "wear": 0.25},
        {"type": "text", "text": "SALVAGE  &  DEMOLITION", "center": (1.0, 0.21), "height": 0.42, "color": YELLOW, "font": "impact", "wear": 0.2},
        {"type": "text", "text": "WRCK 402719 0", "center": (7.9, -3.55), "height": 0.4, "color": CREAM, "font": "impact", "wear": 0.2},
        {"type": "text", "text": "22G1", "center": (9.4, -2.95), "height": 0.32, "color": CREAM, "font": "impact", "wear": 0.2},
    ]


def right_door_stencils():
    return [
        {"type": "text", "text": "WRCK 402719", "center": (-0.32, -2.95), "height": 0.42, "color": CREAM, "font": "impact", "wear": 0.2},
        {"type": "rect", "center": (1.3, -2.95), "size": (0.4, 0.56), "outline": 0.045, "color": CREAM, "wear": 0.2},
        {"type": "text", "text": "0", "center": (1.3, -2.95), "height": 0.42, "color": CREAM, "font": "impact", "wear": 0.2},
        {"type": "text", "text": "22G1", "center": (-0.85, -2.35), "height": 0.34, "color": CREAM, "font": "impact", "wear": 0.2},
        {"type": "rect", "center": (-0.02, 1.15), "size": (1.3, 1.2), "radius": 0.06, "color": YELLOW, "wear": 0.25},
        {"type": "rect", "center": (-0.02, 1.15), "size": (1.3, 1.2), "radius": 0.06, "outline": 0.07, "color": INK, "wear": 0.2},
        {"type": "stripes", "center": (-0.02, 1.62), "size": (1.16, 0.16), "width": 0.12, "color": INK, "wear": 0.2},
        {"type": "text", "text": "!", "center": (-0.02, 0.95), "height": 0.62, "color": INK, "font": "black", "wear": 0.15},
        {"type": "text", "text": "DANGER", "center": (-0.02, 0.48), "height": 0.17, "color": INK, "font": "impact", "wear": 0.15},
    ]


def left_door_stencils():
    lines = [("MAX GROSS  30,480 KG", -3.1), ("67,200 LB", -2.8), ("TARE  2,230 KG", -2.4), ("4,920 LB", -2.1), ("NET  28,250 KG", -1.7), ("CU.CAP.  33.2 M3", -1.4)]
    out = [{"type": "text", "text": text, "center": (0.05, v), "height": 0.2, "color": CREAM, "font": "bold", "wear": 0.2} for text, v in lines]
    out += [
        {"type": "rect", "center": (0.0, 1.55), "size": (1.1, 0.74), "radius": 0.04, "color": (172, 174, 180), "metal": 0.7, "rough": 0.4, "wear": 0.15},
        {"type": "rect", "center": (0.0, 1.55), "size": (1.1, 0.74), "radius": 0.04, "outline": 0.035, "color": (70, 72, 78), "wear": 0.1},
        {"type": "text", "text": "CSC SAFETY APPROVAL", "center": (0.0, 1.3), "height": 0.075, "color": (40, 40, 44), "font": "bold", "wear": 0.1},
    ]
    out += [{"type": "rect", "center": (0.0, 1.43 + k * 0.1), "size": (0.86, 0.035), "color": (96, 98, 104), "wear": 0.1} for k in range(5)]
    out.append({"type": "rivets", "points": [(-0.47, 1.25), (0.47, 1.25), (-0.47, 1.85), (0.47, 1.85)], "radius": 0.035, "color": (150, 152, 158), "height": 0.01})
    return out


def end_stencils():
    return [
        {"type": "text", "text": "WRCK 402719 0", "center": (2.1, -3.6), "height": 0.38, "color": CREAM, "font": "impact", "wear": 0.2},
        {"type": "text", "text": "22G1", "center": (2.9, -3.05), "height": 0.3, "color": CREAM, "font": "impact", "wear": 0.2},
    ]


def door_leaf(side, frame, panel_mat, dark, dents):
    inner, outer = ("+x", "-x") if side > 0 else ("-x", "+x")
    cx = side * 1.985
    parts = [
        slab((0.26, 8.0, 0.38), (side * 0.17, 5.0, 11.49), frame, ["+z", inner, outer]),
        slab((0.34, 8.0, 0.38), (side * 3.84, 5.0, 11.49), frame, ["+z", outer, inner]),
        slab((3.37, 0.3, 0.38), (cx, 8.85, 11.49), frame, ["+z", "-y"]),
        slab((3.37, 0.3, 0.38), (cx, 1.15, 11.49), frame, ["+z", "+y"]),
    ]
    panel = sheet(3.49, 7.5, 5, 0.12, panel_mat, levels=(0.0, 0.5, 1.0), ribs="horizontal", dents=dents, crest=0.4, slope=0.12)
    parts.append(panel.transformed(T(cx, 5.0, DOOR_Z)))
    for y in (1.75, 3.85, 6.15, 8.25):
        parts.append(sh.cylinder(0.12, 0.5, dark, bevel=0.0, segments=8).transformed(T(side * 4.03, y, 11.76)))
        parts.append(slab((0.5, 0.26, 0.07), (side * 3.8, y, 11.715), dark, ["+z", "+y", "-y", inner]))
    return parts


def lock_gear(bar_mat, dark, handle_mat):
    parts = []
    hardware = ["+z", "+x", "-x", "+y", "-y"]
    for x in BARS:
        parts.append(sh.lathe([(0.11, 0.95), (0.11, 9.1)], 8, bar_mat, smooth_angle=50).transformed(T(x, 0, BAR_Z)))
        for y in (0.83, 9.15):
            parts.append(slab((0.46, 0.44, 0.3), (x, y, 11.83), dark, hardware))
        for y in (3.0, 6.9):
            parts.append(slab((0.34, 0.2, 0.2), (x, y, 11.81), dark, hardware))
        d = 1.0 if x > 0 else -1.0
        parts.append(slab((0.3, 0.38, 0.24), (x, 4.6, 11.84), dark, hardware))
        lever = [(x, 4.62, 11.9), (x + d * 0.45, 4.6, 11.92), (x + d * 0.88, 4.56, 11.9)]
        parts.append(sh.sweep(lever, 0.065, 6, handle_mat))
        parts.append(slab((0.16, 0.3, 0.12), (x + d * 0.92, 4.56, 11.74), dark, hardware))
    return parts


def build():
    a = Asset("ScrapContainer", budget=3500, atlas=1024, ao_radius=1.0, edge_width=0.1, preview_radius=13.6,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")

    frame = paint(wear=0.65, patches=0.35, streaks=0.5)
    rails = paint(wear=0.65, patches=0.4, streaks=0.4)
    dark = paint(CHARCOAL, wear=0.55, patches=0.3, fade=0.2)
    roof_mat = paint((140, 52, 30), wear=0.4, patches=0.85, top_rust=0.4, fade=0.08, streaks=0.0, gradient=0.0, highlight=0.3, ripple=(1, 0.58, 0.03))
    cavity = paint((34, 30, 28), wear=0.15, patches=0.2, fade=0.0, grime=0.8)
    bar_mat = paint(STEEL, wear=0.5, patches=0.45, fade=0.15, streaks=0.3, scratches=0.4)
    handle_mat = Material("paint", color=YELLOW, under=RUST, wear=0.55, scratches=0.4, dirt=0.4, rough=0.45)
    hazard = Material("hazard", color=YELLOW, color2=CHARCOAL, width=0.32, angle=45, under=RUST, wear=0.55, scratches=0.3, dirt=0.5)
    gasket = Material("rubber", color=(26, 24, 24), pattern="ribs", freq=6.0)

    parts = [castings()]
    for sx in (-1, 1):
        for sz in (-1, 1):
            parts.append(corner_post(frame, 8.4, 0.8).transformed(S(sx, 1, sz)))

    for sx in (-1, 1):
        out = "+x" if sx > 0 else "-x"
        inn = "-x" if sx > 0 else "+x"
        parts += bottom_rail(sx, rails, cavity)
        parts += [slab((0.45, 0.62, 11.05), (sx * 4.675, 9.61, zc), rails, [out, inn, "+y", "-y"]) for zc in (-5.525, 5.525)]

    parts.append(slab((8.1, 0.86, 0.55), (0.0, 0.47, -11.675), rails, ["-z", "+y"], face_mats={"-z": hazard}))
    parts.append(slab((8.1, 0.62, 0.55), (0.0, 9.61, -11.675), rails, ["-z", "+z", "+y", "-y"]))
    parts.append(slab((8.1, 0.96, 0.5), (0.0, 0.52, 11.45), rails, ["+z", "+y"], face_mats={"+z": hazard}))
    parts.append(slab((8.1, 0.92, 0.5), (0.0, 9.46, 11.45), rails, ["+z", "-z", "+y", "-y"]))

    plus_x = sheet(22.3, WALL_HEIGHT, 20, 0.26, paint(wear=0.3, patches=0.45, streaks=0.7, stencils=side_stencils()),
                   levels=(0.0, 0.26, 0.5, 0.74, 1.0), dents=[(-4.6, -1.2, 2.2, 0.62), (7.8, 2.0, 1.4, 0.3), (2.0, 2.8, 2.4, 0.1), (-9.0, 0.6, 1.4, 0.14)], pieces=2)
    skins = [plus_x.transformed(compose(T(4.52, WALL_MID, 0.0), R(0, 90, 0)))]
    minus_x = sheet(22.3, WALL_HEIGHT, 20, 0.26, paint(wear=0.3, patches=0.45, streaks=0.7, stencils=side_stencils()),
                    levels=(0.0, 0.3, 0.54, 0.78, 1.0), dents=[(-5.8, -0.4, 2.3, 0.55), (6.4, 1.6, 1.4, 0.28), (-0.5, -2.6, 2.0, 0.1)], pieces=2)
    skins.append(minus_x.transformed(compose(T(-4.52, WALL_MID, 0.0), R(0, -90, 0))))
    end_wall = sheet(8.3, WALL_HEIGHT, 6, 0.25, paint(wear=0.3, patches=0.5, streaks=0.8, stencils=end_stencils()),
                     levels=(0.0, 0.32, 0.6, 1.0), dents=[(1.6, -0.6, 1.8, 0.36)], crest=0.36, slope=0.12)
    skins.append(end_wall.transformed(compose(T(0.0, WALL_MID, -11.45), R(0, 180, 0))))
    skins.append(roof(roof_mat))

    for sz, sx in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        louvers = paint(CHARCOAL, wear=0.5, fade=0.2, stencils=[
            {"type": "rect", "center": (0.0, -0.12 + k * 0.12), "size": (0.7, 0.05), "darken": 0.8, "raise": -0.01} for k in range(3)
        ])
        out = "+x" if sx > 0 else "-x"
        parts.append(slab((0.12, 0.44, 0.9), (sx * 4.84, 8.75, sz * 10.0), dark, [out, "+y", "-y", "+z", "-z"], face_mats={out: louvers}))

    patch = paint((78, 74, 70), wear=0.6, patches=0.55, fade=0.1, streaks=0.3, stencils=[
        {"type": "rect", "center": (0.0, 0.0), "size": (2.0, 1.4), "outline": 0.07, "darken": 0.6, "raise": 0.006},
        {"type": "rivets", "points": [(-0.85, -0.55), (0.85, -0.55), (-0.85, 0.55), (0.85, 0.55), (0.0, -0.55), (0.0, 0.55)], "radius": 0.06, "color": (60, 58, 56), "height": 0.016},
        {"type": "text", "text": "PATCHED", "center": (0.0, 0.05), "height": 0.26, "color": CREAM, "font": "impact", "wear": 0.4},
    ])
    plate = sh.rounded_box((0.07, 1.4, 2.0), 0.0, 1, patch, faces=["-x", "+y", "-y", "+z", "-z"], face_mats={"+y": rails, "-y": rails, "+z": rails, "-z": rails})
    parts.append(plate.transformed(compose(T(-4.815, 2.6, 4.2), R(7, 0, 0))))

    parts.append(slab((0.14, 8.0, 0.06), (0.0, 5.0, 11.33), gasket, ["+z"]))
    parts += door_leaf(1, frame, paint(wear=0.45, patches=0.4, streaks=0.6, stencils=right_door_stencils()), dark, [])
    parts += door_leaf(-1, frame, paint(wear=0.45, patches=0.4, streaks=0.6, stencils=left_door_stencils()), dark, [(0.3, -2.2, 1.3, 0.1)])
    parts += lock_gear(bar_mat, dark, handle_mat)

    body, _ = fuse(parts, scale=0.8, height=8.6)
    a.add("Body", body, skins)

    destructible(a, "ScrapYard")
    collider(a, "Hitbox", (10.0, 10.0, 24.0), (0.0, 5.0, 0.0))
    a.point("label", (0.0, 11.5, 0.0))
    a.meta["footprint"] = (10.0, 24.0)
    return a
