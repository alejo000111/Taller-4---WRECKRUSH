import numpy as np

from wr3d import Asset, Material, T, R, compose, register
from wr3d import shapes as sh
from wr3d.materials import REGISTRY, Surface, rgb, grime_amount
from wr3d.noise import smoothstep, worley
from _destructible import destructible, collider

YELLOW = (255, 210, 31)
INK = (22, 20, 20)
SIGNAL_RED = (196, 38, 32)
WHITE = (238, 236, 228)
ZINC = (158, 162, 168)
RUST = (150, 62, 24)

POST_TOP = 7.75
POST_HALF = 0.1
LEAN = 0.4
SIGN_Y = 6.55
SIGN_HALF = 1.45
SIGN_DEPTH = 0.07
FOLD_X = -0.98
PLATE_Y = 4.3


@register("roadsign_galvanized")
def galvanized(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", ZINC))
    f1, f2, cell = worley(ctx.Ps * p.get("spangle", 7.0), 81)
    tone = (cell & 255) / 255.0 - 0.5
    rim = smoothstep(0.0, 0.05, f2 - f1)
    var = ctx.noise(2.5, 3, 82)
    oxide = smoothstep(0.05, 0.45, ctx.noise(3.2, 4, 83)) * p.get("oxide", 0.45)
    pits = smoothstep(0.25, 0.5, ctx.noise(9.0, 3, 84) + 0.4 * np.clip(ctx.E, 0, 1)) * p.get("rust", 0.3)
    shade = 0.9 + 0.14 * tone * rim + 0.07 * var
    s.base = color[None, :] * shade[:, None]
    s.base = s.base + (rgb((206, 206, 198))[None, :] - s.base) * (oxide * 0.55)[:, None]
    s.base = s.base + (rgb(RUST)[None, :] * 0.8 - s.base) * pits[:, None]
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.42 + 0.12 * var + 0.3 * oxide + 0.35 * pits, 0, 1)
    s.metal = np.clip(0.85 - 0.55 * oxide - 0.7 * pits, 0, 1)
    s.height = 0.0006 * tone * rim + pits * ctx.noise(30.0, 2, 85) * 0.002
    low = 1 - smoothstep(0.0, p.get("splash", 1.2), ctx.P[:, 1])
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.35)) + low * 0.55, 0, 0.85)
    s.base = np.clip(s.base, 0, 1)
    return s


@register("roadsign_dented")
def dented_paint(ctx, p):
    s = REGISTRY["paint"](ctx, p)
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    sink = np.zeros(ctx.n)
    for cu, cv, radius, depth in p.get("dents", ()):
        sink += depth * np.exp(-((u - cu) ** 2 + (v - cv) ** 2) / (radius * radius))
    s.height = s.height - sink
    s.tint = np.clip(s.tint * (1 - sink * 6.0), 0, 1)
    return s


def axis(y):
    t = np.clip(y / POST_TOP, 0, 1)
    return np.array([0.05 * t ** 2, y, LEAN * t ** 1.5])


def on_post(y, offset=0.0):
    t = np.clip(y / POST_TOP, 1e-3, 1)
    dx = 0.1 * t / POST_TOP
    dz = 1.5 * LEAN * np.sqrt(t) / POST_TOP
    return compose(T(*axis(y)), R(np.degrees(np.arctan(dz)), 0, -np.degrees(np.arctan(dx))), T(0, 0, offset))


def split(poly, cut):
    left, right = [], []
    for a, b in zip(poly, np.roll(poly, -1, 0)):
        (left if a[0] <= cut else right).append(a)
        if (a[0] - cut) * (b[0] - cut) < 0:
            hit = a + (b - a) * (cut - a[0]) / (b[0] - a[0])
            left.append(hit)
            right.append(hit)
    return np.asarray(left), np.asarray(right)


def post(mat):
    ys = np.linspace(0.12, POST_TOP, 7)
    path = np.array([axis(y) for y in ys])
    turned = path @ R(0, -45, 0)[:3, :3].T
    tube = sh.sweep(turned, POST_HALF * np.sqrt(2), 4, mat)
    return tube.transformed(R(0, 45, 0))


def footing(mat):
    prof = [(0.43, -0.03), (0.44, 0.3), (0.41, 0.4), (0.33, 0.46), (0.16, 0.48), (0.0, 0.49)]
    block = sh.lathe(prof, 12, mat, smooth_angle=60, start=90)
    rng = np.random.default_rng(7)
    ang = np.arctan2(-block.pos[:, 2], block.pos[:, 0])
    wobble = 1.0 + 0.04 * np.sin(ang * 3 + 0.8) + rng.normal(0, 0.012, len(ang))
    block.pos[:, [0, 2]] *= wobble[:, None]
    top = block.pos[:, 1] > 0.35
    chip = np.exp(-((ang - 2.4) ** 2) / 0.18) * top
    block.pos[:, 1] -= chip * 0.13
    block.pos[:, [0, 2]] *= (1 - chip * 0.12)[:, None]
    return sh.recompute_normals(block)


def chunk(mat):
    rock = sh.sphere(0.13, mat, 6, 4)
    rng = np.random.default_rng(3)
    rock.pos *= 1 + rng.normal(0, 0.12, (len(rock.pos), 1))
    rock = sh.recompute_normals(rock)
    return rock.transformed(compose(T(0.52, 0.05, -0.2), R(12, 30, -8), sh_scale(1.3, 0.7, 1.0)))


def sh_scale(x, y, z):
    return np.diag([x, y, z, 1.0])


def sign_face():
    border = 1.83
    bolts = [(0.0, -0.98), (0.0, 0.98)]
    return Material("roadsign_dented", color=YELLOW, under=ZINC, wear=0.35, scratches=0.35, dirt=0.3, rough=0.38, metal=0.05,
                    dents=[(0.62, 0.55, 0.32, 0.02), (-0.35, -0.7, 0.25, 0.014), (0.2, 0.15, 0.5, 0.008)],
                    decals=[
                        {"type": "rect", "center": (0.0, 0.0), "size": (border, border), "radius": 0.06, "angle": 45, "outline": 0.1, "color": INK, "wear": 0.25},
                        {"type": "text", "text": "!", "center": (0.0, -0.02), "height": 1.32, "color": INK, "font": "black", "wear": 0.2},
                        {"type": "rect", "center": (0.0, -0.74), "size": (0.06, 0.42), "radius": 0.03, "darken": 0.35, "raise": 0.0},
                        {"type": "rect", "center": (0.03, 1.2), "size": (0.05, 0.36), "radius": 0.025, "darken": 0.45, "raise": 0.0},
                        {"type": "rect", "center": (-0.04, 1.16), "size": (0.03, 0.26), "radius": 0.015, "darken": 0.35, "raise": 0.0},
                        {"type": "circle", "center": (0.46, -0.36), "radius": 0.085, "color": ZINC, "wear": 0.0, "metal": 0.8},
                        {"type": "circle", "center": (0.46, -0.36), "radius": 0.065, "outline": 0.022, "darken": 0.35, "raise": 0.008},
                        {"type": "circle", "center": (0.46, -0.36), "radius": 0.036, "darken": 0.95, "raise": -0.02},
                        {"type": "circle", "center": (-0.52, 0.44), "radius": 0.075, "color": ZINC, "wear": 0.0, "metal": 0.8},
                        {"type": "circle", "center": (-0.52, 0.44), "radius": 0.058, "outline": 0.02, "darken": 0.35, "raise": 0.008},
                        {"type": "circle", "center": (-0.52, 0.44), "radius": 0.032, "darken": 0.95, "raise": -0.02},
                        {"type": "rect", "center": (-0.52, 0.62), "size": (0.035, 0.26), "radius": 0.017, "darken": 0.3, "raise": 0.0},
                        {"type": "rivets", "points": bolts, "radius": 0.05, "color": (176, 178, 182), "height": 0.012},
                    ])


def plate_face():
    return Material("roadsign_dented", color=SIGNAL_RED, under=ZINC, wear=0.4, scratches=0.35, dirt=0.35, rough=0.4, metal=0.05,
                    dents=[(0.45, 0.1, 0.22, 0.012)],
                    decals=[
                        {"type": "rect", "center": (0.0, 0.0), "size": (1.38, 0.78), "radius": 0.06, "outline": 0.04, "color": WHITE, "wear": 0.3},
                        {"type": "text", "text": "SCRAP YARD", "center": (0.0, -0.14), "height": 0.17, "color": WHITE, "font": "impact", "wear": 0.25},
                        {"type": "text", "text": "KEEP OUT", "center": (0.0, 0.14), "height": 0.27, "color": WHITE, "font": "impact", "wear": 0.25},
                        {"type": "rect", "center": (0.0, -0.27), "size": (0.04, 0.12), "radius": 0.02, "darken": 0.35, "raise": 0.0},
                        {"type": "rect", "center": (0.01, 0.48), "size": (0.04, 0.14), "radius": 0.02, "darken": 0.4, "raise": 0.0},
                        {"type": "rivets", "points": [(0.0, -0.37), (0.0, 0.37)], "radius": 0.035, "color": (176, 178, 182), "height": 0.01},
                    ])


def diamond(back, face):
    corners = [(SIGN_HALF, 0.0), (0.0, SIGN_HALF), (-SIGN_HALF, 0.0), (0.0, -SIGN_HALF)]
    outline = sh.round_polyline(corners, 0.14, 2, closed=True)
    flap, body = split(outline, FOLD_X)
    plate = sh.extrude(body, SIGN_DEPTH, back, bevel=0.025, corner_radius=0.0, cap_mats=[None, face])
    bent = sh.extrude(flap, SIGN_DEPTH, back, bevel=0.025, corner_radius=0.0, cap_mats=[None, face])
    hinge = compose(T(FOLD_X, 0, SIGN_DEPTH / 2), R(0, 22, 0), T(-FOLD_X, 0, -SIGN_DEPTH / 2))
    return [plate, bent.transformed(hinge)]


def info_plate(back, face):
    outline = [(-0.75, -0.45), (0.75, -0.45), (0.75, 0.45), (-0.75, 0.45)]
    return sh.extrude(outline, 0.05, back, bevel=0.015, corner_radius=0.07, corner_segments=1, cap_mats=[None, face])


def build():
    a = Asset("RoadSign", budget=700, atlas=512, ao_radius=0.3, edge_width=0.03, preview_radius=4.4,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")

    holes = [{"type": "rect", "center": ((k + 0.5) * np.pi / 2 * POST_HALF * np.sqrt(2), v), "size": (0.045, 0.045), "darken": 0.9, "raise": -0.008}
             for k in range(4) for v in np.arange(0.7, POST_TOP - 0.1, 0.24)]
    zinc_post = Material("roadsign_galvanized", oxide=0.5, rust=0.25, decals=holes)
    zinc = Material("roadsign_galvanized", oxide=0.4, rust=0.3)
    hardware = Material("roadsign_galvanized", color=(128, 132, 138), oxide=0.3, rust=0.55)
    concrete = Material("concrete", color=(150, 148, 142), dirt=0.6, decals=[
        {"type": "rect", "center": (0.62, 0.62), "size": (0.016, 0.34), "angle": 18, "darken": 0.7, "raise": -0.01},
        {"type": "rect", "center": (0.7, 0.78), "size": (0.012, 0.2), "angle": -30, "darken": 0.6, "raise": -0.008},
        {"type": "rect", "center": (1.95, 0.64), "size": (0.014, 0.3), "angle": -12, "darken": 0.65, "raise": -0.01},
        {"type": "rect", "center": (0.12, 0.6), "size": (0.012, 0.22), "angle": 25, "darken": 0.6, "raise": -0.008},
    ])

    a.add("Body", footing(concrete), chunk(concrete))
    a.add("Body", post(zinc_post))
    a.add("Body", sh.rounded_box((0.24, 0.05, 0.24), 0.0, 1, hardware, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(on_post(POST_TOP + 0.02)))

    for piece in diamond(zinc, sign_face()):
        a.add("Body", piece.transformed(on_post(SIGN_Y, -(POST_HALF + 0.06 + SIGN_DEPTH / 2))))
    a.add("Body", sh.rounded_box((0.18, 2.3, 0.06), 0.0, 1, hardware, faces=["+x", "-x", "+y", "-y", "+z"]).transformed(on_post(SIGN_Y, -(POST_HALF + 0.03))))
    for y in (SIGN_Y - 0.62, SIGN_Y + 0.58):
        a.add("Body", sh.rounded_box((0.3, 0.1, 0.3), 0.0, 1, hardware, faces=["+x", "-x", "+y", "-y", "+z"]).transformed(on_post(y, 0.0)))

    plate = info_plate(zinc, plate_face())
    a.add("Body", plate.transformed(compose(on_post(PLATE_Y, -(POST_HALF + 0.03 + 0.025)), R(0, 0, 4))))
    a.add("Body", sh.rounded_box((0.3, 0.1, 0.3), 0.0, 1, hardware, faces=["+x", "-x", "+y", "-y", "+z"]).transformed(on_post(PLATE_Y + 0.12, 0.0)))
    a.add("Body", sh.rounded_box((0.14, 0.7, 0.03), 0.0, 1, hardware, faces=["+x", "-x", "+y", "-y"]).transformed(on_post(PLATE_Y, -(POST_HALF + 0.015))))

    destructible(a, "ScrapYard")
    collider(a, "Hitbox", (0.45, 8.0, 0.45), (0.0, 4.0, 0.0), shape="Cylinder")
    sign_z = float(on_post(6.7, -(POST_HALF + 0.06 + SIGN_DEPTH / 2))[2, 3])
    collider(a, "SignPlate", (2.5, 2.6, 0.3), (0.0, 6.7, sign_z))
    a.point("label", (0.0, 9.0, 0.0))
    return a
