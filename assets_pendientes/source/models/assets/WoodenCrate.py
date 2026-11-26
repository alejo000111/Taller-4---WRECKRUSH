import numpy as np

from wr3d import Asset, Material, register, T, R, compose
from wr3d import shapes as sh
from wr3d.materials import REGISTRY, Surface, rgb, grime_amount, scratch_mask
from wr3d.noise import fbm, worley, smoothstep, mix
from _destructible import destructible, collider

TAN = (176, 124, 72)
FRAME = (110, 76, 44)
INK = (30, 24, 20)
RED = (178, 38, 30)
RUST = (150, 62, 24)
RUST_DARK = (92, 38, 18)

OUTER = 2.5
HEIGHT = 5.0
FACE = 2.45
CORE = 2.33
BOARD = 0.55
INNER = FACE - BOARD
TOP = 4.95
OPEN_LO = BOARD
OPEN_HI = TOP - BOARD
OPEN_MID = (OPEN_LO + OPEN_HI) / 2
CAP = 0.8
UP = np.array([0.0, 1.0, 0.0])
SIDES = {"front": (0.0, 0.0, -1.0), "right": (1.0, 0.0, 0.0), "back": (0.0, 0.0, 1.0), "left": (-1.0, 0.0, 0.0)}


def _hash01(values):
    return (np.sin(values * 12.9898 + 78.233) * 43758.5453) % 1.0


def _nail_marks(ctx, s, nails, head_color, rust_amount):
    if not len(nails):
        return
    P, N = ctx.P, ctx.N
    rust_col = mix(rgb(RUST), rgb(RUST_DARK), smoothstep(-0.3, 0.5, ctx.noise(9.0, 2, 91)))
    vertical = 1 - smoothstep(0.4, 0.7, np.abs(N[:, 1]))
    for i, nail in enumerate(nails):
        rel = P - nail
        near = np.abs(rel).max(1) < 1.0
        if not near.any():
            continue
        r = rel[near]
        n = N[near]
        dist = np.linalg.norm(r, axis=1)
        flat = r - (r * n).sum(1, keepdims=True) * n
        below = -flat[:, 1]
        side = np.linalg.norm(flat - np.outer(flat[:, 1], UP), axis=1)
        length = 0.25 + 0.5 * _hash01(i + 0.37)
        head = 1 - smoothstep(0.034, 0.044, dist)
        halo = (1 - smoothstep(0.045, 0.11, dist)) * (1 - head)
        streak = (1 - smoothstep(0.012, 0.035 + 0.05 * np.clip(below, 0, 1), side)) * smoothstep(0.02, 0.06, below) * (1 - smoothstep(0.0, length, below)) * vertical[near]
        stain = np.clip(halo * 0.7 + streak * 0.8, 0, 1) * rust_amount
        base = s.base[near]
        base = mix(base, rust_col[near], stain)
        dome = np.sqrt(np.clip(1 - (dist / 0.044) ** 2, 0, 1))
        base = mix(base, rgb(head_color) * (0.75 + 0.35 * dome)[:, None], head)
        s.base[near] = base
        s.tint[near] = s.tint[near] * (1 - stain * 0.3)
        s.paint[near] = s.paint[near] * (1 - np.maximum(head, stain * 0.6))
        s.metal[near] = mix(s.metal[near], 0.8, head)
        s.rough[near] = mix(mix(s.rough[near], 0.85, stain), 0.45, head)
        s.height[near] = s.height[near] + dome * 0.008 - halo * 0.002


@register("woodencrate_wood")
def crate_wood(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", TAN))
    axis = np.asarray(p.get("axis", (1.0, 0.0, 0.0)), dtype=np.float64)
    axis = axis / np.linalg.norm(axis)
    helper = UP if abs(axis[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    b1 = np.cross(axis, helper)
    b1 = b1 / np.linalg.norm(b1)
    b2 = np.cross(axis, b1)
    q = ctx.Ps
    along, r1, r2 = q @ axis, q @ b1, q @ b2
    warp = ctx.noise(1.2, 3, 15) * 0.7
    rings = smoothstep(0.25, 0.95, 0.5 + 0.5 * np.sin(np.hypot(r1, r2 + 2.0) * p.get("ring_freq", 16.0) + warp * 4 + along * 0.4))
    streak = fbm(np.stack([along * 1.3, r1 * 36.0, r2 * 36.0], 1) + 5.0, 3, 2.0, 0.5, 16)
    board = (_hash01(ctx.seed * 0.001) - 0.5) * 0.14
    tone = 0.8 + 0.15 * rings + 0.14 * streak + board
    seams = p.get("seams")
    groove = np.zeros(ctx.n)
    if seams:
        coord = (ctx.P[:, seams["axis"]] - seams["offset"]) / seams["pitch"]
        groove = 1 - smoothstep(0.012, 0.028, np.abs(coord - np.round(coord)) * seams["pitch"])
        tone = tone + (_hash01(np.floor(coord) + 3.1) - 0.5) * 0.16
    rub = smoothstep(0.3, 0.9, ctx.E) * p.get("rub", 0.3)
    scrape = smoothstep(0.42, 0.62, ctx.noise(3.2, 3, 92)) * smoothstep(-0.1, 0.5, ctx.noise(1.1, 2, 93)) * p.get("scuff", 0.5)
    scratches = scratch_mask(ctx, p.get("scratches", 0.35))
    stain = smoothstep(0.2, 0.55, ctx.noise(1.6, 4, 94)) * p.get("stains", 0.25)
    s.base = np.clip(color[None, :] * (tone + rub + scrape * 0.16 - scratches * 0.25 - stain * 0.25 - groove * 0.55)[:, None], 0, 1)
    s.base = mix(s.base, color[None, :] * 0.5, smoothstep(0.6, 0.9, ctx.noise(8.0, 3, 17)) * 0.3)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(p.get("rough", 0.68) + 0.08 * streak - rub * 0.25 + groove * 0.2, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = (rings - 0.5) * 0.0016 + streak * 0.001 - groove * 0.012 - scratches * 0.0015 + scrape * 0.0006
    low = 1 - smoothstep(0.0, 1.2, ctx.P[:, 1])
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.35)) + groove * 0.35 + low * 0.45 * (0.5 + 0.5 * smoothstep(-0.3, 0.3, ctx.noise(2.5, 3, 95))), 0, 0.85)
    for cx, cy, cz, radius in p.get("holes", ()):
        d = np.linalg.norm(ctx.P - np.array([cx, cy, cz]), axis=1)
        hole = 1 - smoothstep(radius * 0.8, radius, d)
        s.base = s.base * (1 - 0.85 * hole)[:, None]
        s.height = s.height - hole * 0.02
    _nail_marks(ctx, s, np.asarray(p.get("nails", ()), dtype=np.float64).reshape(-1, 3), (70, 70, 74), p.get("nail_rust", 0.8))
    return s


@register("woodencrate_galv")
def crate_galv(ctx, p):
    s = REGISTRY["metal"](ctx, dict(color=p.get("color", (170, 174, 180)), rough=0.38, polish=0.5, scratches=0.45, dirt=p.get("dirt", 0.4)))
    _, _, cell = worley(ctx.Ps * p.get("spangle", 6.0), 83)
    flake = (cell % 997) / 997.0 - 0.5
    s.base = np.clip(s.base * (1 + 0.16 * flake)[:, None], 0, 1)
    s.rough = np.clip(s.rough + 0.12 * flake, 0.05, 1)
    rust_col = mix(rgb(RUST), rgb(RUST_DARK), smoothstep(-0.3, 0.5, ctx.noise(8.0, 3, 85)))
    rust = smoothstep(0.5, 0.62, ctx.noise(4.0, 3, 84) + 0.35 * ctx.E + 0.35 * (1 - ctx.AO)) * p.get("rust", 0.5)
    s.base = mix(s.base, rust_col, rust)
    s.metal = mix(s.metal, 0.1, rust)
    s.rough = mix(s.rough, 0.85, rust)
    s.height = s.height + rust * ctx.noise(30.0, 2, 86) * 0.002
    _nail_marks(ctx, s, np.asarray(p.get("nails", ()), dtype=np.float64).reshape(-1, 3), (96, 98, 104), p.get("nail_rust", 0.6))
    return s


def frame(n):
    n = np.asarray(n, dtype=np.float64)
    m = np.eye(4)
    m[:3, 0] = np.cross(UP, n)
    m[:3, 1] = UP
    m[:3, 2] = n
    return m


def on_face(n, a, y, d):
    return (frame(n) @ np.array([a, y, d, 1.0]))[:3]


def board_profile(size, chamfer=0.05):
    h = size / 2
    return sh.round_polyline(np.array([(-h, -h), (h, -h), (h, h), (-h, h)]), chamfer, 1, closed=True)


def board(length, mat, center, axis, caps=False):
    m = sh.extrude(board_profile(BOARD), length, mat, bevel=0.0, corner_radius=0.0, caps=caps)
    turn = {"x": R(0, 90, 0), "y": R(-90, 0, 0), "z": np.eye(4)}[axis]
    return m.transformed(compose(T(*center), turn))


def brace_outline(rising):
    dw = 0.79
    pts = [(-INNER, OPEN_LO), (-INNER + dw, OPEN_LO), (INNER, OPEN_HI), (INNER - dw, OPEN_HI)]
    return [(a if rising else -a, y) for a, y in pts]


def brace_line(rising):
    a0, a1 = (-INNER + 0.395, INNER - 0.395) if rising else (INNER - 0.395, -INNER + 0.395)
    return np.array([a0, OPEN_LO]), np.array([a1, OPEN_HI])


def face_nails(n, rising):
    pts = []
    mid = (FACE + INNER) / 2
    for a in (-mid, mid):
        for y in (1.35, OPEN_MID, 3.6):
            pts.append(on_face(n, a, y, FACE))
    for y in (TOP - BOARD / 2, BOARD / 2):
        for a in (-1.35, 1.35):
            pts.append(on_face(n, a, y, FACE))
    p0, p1 = brace_line(rising)
    along = (p1 - p0) / np.linalg.norm(p1 - p0)
    across = np.array([-along[1], along[0]])
    for t in (0.1, 0.9):
        c = p0 + (p1 - p0) * t
        for k in (-0.15, 0.15):
            q = c + across * k
            pts.append(on_face(n, q[0], q[1], CORE + 0.1))
    c = (p0 + p1) / 2
    pts.append(on_face(n, c[0], c[1], CORE + 0.1))
    return pts


def cap_nails(sx, sz, top):
    pts = []
    y_edge = HEIGHT if top else 0.0
    sy = 1 if top else -1
    for u, v in ((0.2, 0.55), (0.55, 0.2)):
        pts.append((sx * OUTER, y_edge - sy * u, sz * (OUTER - v)))
        pts.append((sx * (OUTER - v), y_edge - sy * u, sz * OUTER))
        if top:
            pts.append((sx * (OUTER - u), y_edge, sz * (OUTER - v)))
    return pts


def build():
    a = Asset("WoodenCrate", budget=900, atlas=512, ao_radius=0.5, edge_width=0.045, preview_radius=3.9,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")

    rising = {"front": True, "right": False, "back": True, "left": False}
    nails = []
    for side, n in SIDES.items():
        nails += face_nails(n, rising[side])
    plank_z = [-1.55 + k * 0.775 for k in range(5)]
    for z in plank_z:
        for x in (-1.7, 1.7):
            nails.append((x, TOP - 0.02, z))
    for sx in (-1, 1):
        for z in (-1.0, 1.0):
            nails.append((sx * (FACE - BOARD / 2), TOP, z))
            nails.append((z, TOP, sx * (FACE - BOARD / 2)))
    holes = []
    rope_paths = []
    for side in ("right", "left"):
        n = SIDES[side]
        local = [(-0.62, 4.62, 2.36), (-0.64, 4.5, 2.5), (-0.5, 3.98, 2.53), (0.0, 3.8, 2.535), (0.5, 3.98, 2.53), (0.64, 4.5, 2.5), (0.62, 4.62, 2.36)]
        rope_paths.append([on_face(n, *p) for p in local])
        for sa in (-1, 1):
            holes.append(tuple(on_face(n, sa * 0.63, 4.6, FACE)) + (0.085,))

    def wood(axis, color=FRAME, **extra):
        return Material("woodencrate_wood", color=color, axis=axis, nails=nails, holes=holes, **extra)

    seams = {"axis": 1, "pitch": (OPEN_HI - OPEN_LO) / 5, "offset": OPEN_LO}

    def v(y):
        return -(y - OPEN_MID)

    arrows = []
    for au in (0.95, 1.5):
        arrows.append({"type": "text", "text": "↑", "center": (au, v(3.35)), "height": 0.6, "color": INK, "font": "bold", "wear": 0.45})
    arrows.append({"type": "rect", "center": (1.22, v(2.98)), "size": (0.95, 0.07), "color": INK, "wear": 0.45})
    label = [
        {"type": "rect", "center": (0.75, v(1.25)), "size": (1.05, 0.72), "radius": 0.03, "color": (232, 226, 206), "wear": 0.3, "angle": -4},
        {"type": "rect", "center": (0.75, v(1.48)), "size": (1.05, 0.12), "color": RED, "wear": 0.25, "angle": -4},
        {"type": "text", "text": "SHIP TO: YARD 7", "center": (0.74, v(1.3)), "height": 0.1, "color": INK, "font": "bold", "wear": 0.2, "angle": -4},
    ] + [
        {"type": "rect", "center": (0.38 + k * 0.06, v(1.07)), "size": (0.025 if k % 3 else 0.04, 0.22), "color": INK, "wear": 0.15, "angle": -4} for k in range(13)
    ]
    face_decals = {
        "front": label + [
            {"type": "text", "text": "LOT 07", "center": (-0.75, v(3.9)), "height": 0.36, "color": INK, "font": "impact", "wear": 0.5},
        ],
        "right": [
            {"type": "text", "text": "FRAGILE", "center": (-0.55, v(1.3)), "height": 0.55, "color": RED, "font": "impact", "wear": 0.5},
            {"type": "rect", "center": (-0.55, v(0.92)), "size": (2.2, 0.06), "color": RED, "wear": 0.5},
        ] + arrows,
        "back": [
            {"type": "text", "text": "SCRAP CO.", "center": (-0.6, v(3.9)), "height": 0.42, "color": INK, "font": "impact", "wear": 0.5},
            {"type": "text", "text": "KEEP DRY", "center": (0.8, v(1.15)), "height": 0.3, "color": INK, "font": "impact", "wear": 0.55},
        ],
        "left": [
            {"type": "text", "text": "07", "center": (-0.9, v(1.45)), "height": 1.1, "color": INK, "font": "impact", "wear": 0.55},
            {"type": "text", "text": "↑", "center": (1.3, v(3.3)), "height": 0.6, "color": INK, "font": "bold", "wear": 0.45},
        ],
    }

    for side, n in SIDES.items():
        t = np.cross(UP, n)
        core = wood(tuple(t), TAN, seams=seams, decals=face_decals[side])
        panel = sh.rounded_box((2 * INNER, OPEN_HI - OPEN_LO, 0.0), 0.0, 1, core, faces=["+z"])
        a.add("Body", panel.transformed(compose(frame(n), T(0, OPEN_MID, CORE))))
        grain = t * (1.0 if rising[side] else -1.0) + UP
        brace = sh.extrude(brace_outline(rising[side]), 0.1, wood(tuple(grain)), bevel=0.025, corner_radius=0.0)
        a.add("Body", brace.transformed(compose(frame(n), T(0, 0, CORE + 0.05))))

    lid = sh.rounded_box((2 * INNER, 0.0, 2 * INNER), 0.0, 1, wood((1.0, 0.0, 0.0), (120, 84, 50)), faces=["+y"])
    a.add("Body", lid.transformed(T(0, TOP - 0.12, 0)))

    corner = FACE - BOARD / 2
    for sx in (-1, 1):
        for sz in (-1, 1):
            a.add("Body", board(TOP, wood((0.0, 1.0, 0.0)), (sx * corner, TOP / 2, sz * corner), "y"))
    for y in (TOP - BOARD / 2, BOARD / 2):
        for s in (-1, 1):
            a.add("Body", board(2 * INNER, wood((1.0, 0.0, 0.0)), (0, y, s * corner), "x"))
            a.add("Body", board(2 * INNER, wood((0.0, 0.0, 1.0)), (s * corner, y, 0), "z"))

    plank = TAN
    for k, z in enumerate(plank_z):
        m = sh.extrude(sh.round_polyline(np.array([(-0.35, -0.05), (0.35, -0.05), (0.35, 0.05), (-0.35, 0.05)]), 0.03, 1, closed=True), 2 * INNER, wood((1.0, 0.0, 0.0), plank), bevel=0.0, corner_radius=0.0, caps=k == 3)
        m = m.transformed(R(0, 90, 0))
        if k == 3:
            m = m.transformed(compose(T(-INNER, TOP - 0.07, z), R(0, 0, 5), T(INNER, 0, 0)))
        else:
            m = m.transformed(T(0, TOP - 0.07, z))
        a.add("Body", m)

    plate_nails = [on_face(SIDES["front"], sa * 1.2, OPEN_MID + sb * 0.33, CORE + 0.15) for sa in (-1, 1) for sb in (-1, 1)]
    plate_face = Material("woodencrate_wood", color=(214, 192, 146), axis=(1.0, 0.0, 0.0), nails=plate_nails, scuff=0.3, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (2.5, 0.78), "radius": 0.05, "outline": 0.04, "color": INK, "wear": 0.4},
        {"type": "text", "text": "SCRAP CO.", "center": (0.0, -0.04), "height": 0.46, "color": INK, "font": "impact", "wear": 0.4},
        {"type": "text", "text": "WRECKRUSH YARD", "center": (0.0, 0.27), "height": 0.1, "color": INK, "font": "bold", "wear": 0.4},
    ])
    plate_edge = Material("woodencrate_wood", color=(190, 166, 120), axis=(1.0, 0.0, 0.0))
    plate = sh.rounded_box((2.7, 0.95, 0.05), 0.0, 1, plate_edge, faces=["+x", "-x", "+y", "-y", "-z"], face_mats={"-z": plate_face})
    a.add("Body", plate.transformed(T(0, OPEN_MID, -(CORE + 0.125))))

    galv_nails = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            galv_nails += cap_nails(sx, sz, True) + cap_nails(sx, sz, False)
    galv = Material("woodencrate_galv", color=(170, 174, 180), nails=galv_nails)
    for sx in (-1, 1):
        for sz in (-1, 1):
            for top in (True, False):
                y = HEIGHT - CAP / 2 if top else CAP / 2
                faces = ["+x", "-x", "+y", "-y", "+z", "-z"] if top else ["+x", "-x", "+y", "+z", "-z"]
                a.add("Body", sh.rounded_box((CAP, CAP, CAP), 0.0, 1, galv, faces=faces).transformed(T(sx * (OUTER - CAP / 2), y, sz * (OUTER - CAP / 2))))

    rope = Material("wrap", color=(184, 152, 100), width=0.1, slope=0.8, dirt=0.45)
    for path in rope_paths:
        a.add("Body", sh.sweep(path, 0.06, 5, rope, samples=8))

    destructible(a, "ScrapYard")
    collider(a, "Hitbox", (5.0, 5.0, 5.0), (0, 2.5, 0))
    return a
