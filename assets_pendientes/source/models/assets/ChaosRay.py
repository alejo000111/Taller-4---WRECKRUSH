import numpy as np

from wr3d import Asset, Material, register, T, R, compose
from wr3d import shapes as sh
from wr3d.noise import fbm, smoothstep
from wr3d.materials import Surface, grime_amount, rgb, mix

AXIS_Y = 0.95
DISH_F = 1.62
DISH_R = 0.95
DISH_DEPTH = 0.3

BODY_PROFILE = [
    (0.0, -1.36), (0.2, -1.35), (0.33, -1.27), (0.42, -1.08), (0.47, -0.78),
    (0.485, -0.42), (0.47, -0.06), (0.42, 0.28), (0.35, 0.52), (0.31, 0.66), (0.3, 0.76), (0.0, 0.77),
]


@register("ray_lens")
def ray_lens(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (40, 34, 56)))
    rel = ctx.P - np.array([0.0, AXIS_Y, 0.0])
    radius = np.sqrt(rel[:, 0] ** 2 + rel[:, 1] ** 2)
    pitch = p.get("pitch", 0.06)
    ring = 0.5 + 0.5 * np.cos(radius / pitch * 2 * np.pi)
    ridge = smoothstep(0.25, 0.85, ring)
    var = ctx.noise(4.0, 3, 41)
    s.base = np.clip(color[None, :] * (0.8 + 0.35 * ridge + 0.1 * var)[:, None], 0, 1)
    s.rough = np.clip(p.get("rough", 0.3) + 0.12 * (1 - ridge) + 0.05 * var, 0, 1)
    s.metal = np.full(ctx.n, 0.85)
    s.height = ridge * 0.004 + var * 0.0003
    s.dirt = grime_amount(ctx, p.get("dirt", 0.25))
    return s


def body_radius(f):
    prof = sh.round_polyline(BODY_PROFILE, [0, 0.05, 0.08, 0.12, 0.15, 0.15, 0.15, 0.12, 0.1, 0.05, 0.02, 0], 4)
    return float(np.interp(f, prof[:, 1], prof[:, 0]))


def dish_front(r):
    return DISH_F + DISH_DEPTH * (r / DISH_R) ** 2


def dish_back(r):
    return DISH_F - 0.13 + 0.28 * (r / DISH_R) ** 2


def axial(mesh, y=AXIS_Y):
    return mesh.transformed(compose(T(0, y, 0), R(-90, 0, 0)))


def ring_at(mesh, f, y=AXIS_Y):
    return mesh.transformed(compose(T(0, y, -f), R(90, 0, 0)))


def side(poly_zy, depth, mat, x=0.0, **kw):
    pts = [(-z, y) for z, y in poly_zy]
    return sh.extrude(pts, depth, mat, **kw).transformed(compose(T(x, 0, 0), R(0, 90, 0)))


def on_body(f, theta, inset=0.0):
    r = body_radius(f) - inset
    t = np.radians(theta)
    return np.array([r * np.cos(t), AXIS_Y + r * np.sin(t), -f])


def vein(points_ft, radius, mat, inset=0.006, samples=None):
    path = [on_body(f, th, inset) for f, th in points_ft]
    return sh.sweep(path, radius, 4, mat, samples=samples or len(path) * 2, taper=lambda t: 0.55 + 0.45 * np.sin(np.pi * min(max(t, 0.0), 1.0)) ** 0.5)


def build():
    a = Asset("ChaosRay", budget=8000, ao_radius=0.35)
    a.role("Primary", "surface", color=(70, 40, 110), skin="Primary")
    a.role("Dish", "surface", color=(166, 77, 255), skin="Primary")
    a.role("Base", "surface")
    a.role("Accent", "neon", color=(166, 77, 255), skin="Accent")
    a.role("AccentPink", "neon", color=(255, 59, 160), skin="Accent")
    a.role("Glass", "glass", color=(196, 160, 255), transparency=0.55)

    body_paint = Material("paint", color=(70, 40, 110), wear=0.35, scratches=0.3, dirt=0.25, rough=0.32, under=(178, 172, 196), chip_depth=0.003)
    dish_paint = Material("paint", color=(166, 77, 255), wear=0.4, scratches=0.3, dirt=0.2, rough=0.3, under=(190, 186, 204))
    gunmetal = Material("metal", color=(70, 74, 86), rough=0.34, polish=0.7, dirt=0.3, skin=False)
    dark = Material("metal", color=(46, 40, 60), rough=0.38, polish=0.6, dirt=0.3, skin=False)
    steel = Material("metal", color=(184, 186, 200), rough=0.22, polish=0.8, brushed=True, dirt=0.25, skin=False)
    rubber = Material("rubber", color=(25, 20, 32), pattern="knurl", freq=10, dirt=0.3)
    lens = Material("ray_lens", color=(44, 36, 62))
    neon = Material("plastic")

    body = sh.lathe(sh.round_polyline(BODY_PROFILE, [0, 0.05, 0.08, 0.12, 0.15, 0.15, 0.15, 0.12, 0.1, 0.05, 0.02, 0], 1), 20, body_paint, start=90)
    a.add("Primary", axial(body))

    for f, w in ((-0.98, 0.12), (-0.38, 0.1)):
        r = body_radius(f)
        band = sh.tube(r + 0.03, r - 0.06, w, steel, bevel=0.02, segments=14)
        a.add("Base", ring_at(band.transformed(R(0, 0, 0)), f).transformed(R(0, 0, 0)) if False else band.transformed(compose(T(0, AXIS_Y, -f), R(90, 0, 0))))

    keel = side([(-0.42, 0.62), (-0.2, 0.42), (0.3, 0.42), (0.52, 0.6), (0.3, 0.75), (-0.3, 0.75)], 0.3, body_paint, bevel=0.05, corner_radius=0.08)
    a.add("Primary", keel)

    grip_poly = [
        (-0.17, 0.62), (-0.2, 0.44), (-0.26, 0.33), (-0.21, 0.2), (-0.27, 0.06), (-0.22, -0.08),
        (-0.27, -0.22), (-0.22, -0.36), (-0.26, -0.5), (-0.22, -0.62), (0.3, -0.62), (0.31, -0.36),
        (0.27, 0.0), (0.25, 0.32), (0.3, 0.5), (0.36, 0.58), (0.3, 0.66),
    ]
    raked = [(z + 0.06 * (0.6 - y) / 1.2 - 0.02, y) for z, y in grip_poly]
    grip = side(raked, 0.42, rubber, bevel=0.06, bevel_segments=1, corner_radius=0.0)
    a.add("Base", grip)
    pommel = sh.rounded_box((0.48, 0.1, 0.62), 0.03, 1, dark).transformed(T(0, -0.66, 0.07))
    a.add("Base", pommel)

    guard = side([(-0.2, 0.22), (-0.2, 0.13), (-0.56, 0.13), (-0.7, 0.24), (-0.72, 0.68), (-0.62, 0.68), (-0.62, 0.28), (-0.54, 0.21)], 0.1, dark, bevel=0.03, corner_radius=0.04)
    a.add("Base", guard)
    trigger = side([(-0.3, 0.52), (-0.36, 0.42), (-0.41, 0.3), (-0.38, 0.25), (-0.33, 0.33), (-0.27, 0.46)], 0.07, steel, bevel=0.02, corner_radius=0.02)
    a.add("Base", trigger)

    neck_prof = sh.round_polyline([
        (0.0, 0.6), (0.36, 0.6), (0.37, 0.74), (0.24, 0.8), (0.22, 0.86), (0.27, 0.92), (0.27, 1.0), (0.22, 1.06),
        (0.22, 1.14), (0.27, 1.2), (0.27, 1.28), (0.22, 1.34), (0.24, 1.4), (0.33, 1.48), (0.34, 1.56), (0.0, 1.56),
    ], [0, 0.02, 0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.03, 0.02, 0], 1)
    neck = sh.lathe(neck_prof, 12, gunmetal, start=90)
    a.add("Base", axial(neck))

    for f in (0.85, 1.2):
        halo = sh.torus(0.6, 0.045, neon, segments=24, sides=5)
        a.add("Accent", ring_at(halo, f))

    back = [(r, dish_back(r)) for r in np.linspace(0.0, DISH_R, 8)]
    rim = [(DISH_R + 0.03, dish_back(DISH_R) + 0.03), (DISH_R + 0.035, dish_front(DISH_R) - 0.03)]
    front = [(r, dish_front(r)) for r in np.linspace(DISH_R, 0.72, 4)]
    dish_prof = back + rim + front + [(0.7, dish_front(0.7) - 0.03)]
    radii = [0] * len(back) + [0.03, 0.03] + [0.02] * len(front) + [0]
    radii[len(back) - 1] = 0.03
    dish = sh.lathe(sh.round_polyline(dish_prof, radii, 1), 24, dish_paint, start=90, smooth_angle=50)
    a.add("Dish", axial(dish))

    inner_prof = [(r, dish_front(r) - 0.03) for r in np.linspace(0.7, 0.0, 8)]
    inner = sh.lathe(inner_prof, 24, lens, start=90)
    a.add("Base", axial(inner))

    dish_ring = sh.torus(0.5, 0.032, neon, segments=18, sides=4)
    a.add("Accent", ring_at(dish_ring, dish_front(0.5) - 0.02))
    dish_rim = sh.torus(DISH_R + 0.03, 0.05, neon, segments=28, sides=5)
    a.add("Accent", ring_at(dish_rim, dish_front(DISH_R) - 0.005))

    hub_base = dish_front(0.3) - 0.04
    hub = sh.lathe(sh.round_polyline([(0.0, hub_base), (0.3, hub_base), (0.3, hub_base + 0.06), (0.22, hub_base + 0.1), (0.16, hub_base + 0.18), (0.0, hub_base + 0.19)], [0, 0, 0.03, 0.03, 0.03, 0], 1), 12, dark, start=90)
    a.add("Base", axial(hub))

    spike = sh.lathe([(0.0, hub_base + 0.12), (0.1, hub_base + 0.14), (0.085, 2.0), (0.068, 2.3), (0.05, 2.52), (0.0, 2.58)], 8, neon)
    a.add("AccentPink", axial(spike))
    tip = sh.sphere(0.16, neon, segments=10, rings=6).transformed(T(0, AXIS_Y, -2.72))
    a.add("AccentPink", tip)

    collar_f = 2.3
    collar = sh.tube(0.14, 0.075, 0.1, steel, bevel=0.0, segments=10)
    a.add("Base", ring_at(collar, collar_f))
    for k in range(3):
        ang = np.radians(90 + k * 120)
        d = np.array([np.cos(ang), np.sin(ang)])
        pts = []
        for t, (r, f) in zip(range(4), ((0.84, dish_front(0.84) - 0.01), (0.66, 2.08), (0.36, 2.26), (0.13, collar_f))):
            pts.append((d[0] * r, AXIS_Y + d[1] * r, -f))
        strut = sh.sweep(pts, 0.03, 4, dark, samples=6)
        a.add("Base", strut)

    fin_poly = [(0.12, 1.3), (1.12, 1.24), (1.4, 1.9), (1.22, 1.95), (0.5, 1.5)]
    top_fin = side(fin_poly, 0.09, dark, bevel=0.025, corner_radius=0.0)
    a.add("Base", top_fin)
    for sgn in (-1, 1):
        wing = side([(0.55, 1.26), (1.2, 1.2), (1.36, 1.7), (1.2, 1.74), (0.8, 1.45)], 0.08, dark, bevel=0.025, corner_radius=0.0)
        wing = wing.transformed(compose(T(0, AXIS_Y, 0), R(0, 0, sgn * 115), T(0, -AXIS_Y, 0)))
        a.add("Base", wing)

    socket = sh.lathe(sh.round_polyline([(0.0, -1.44), (0.25, -1.44), (0.27, -1.38), (0.24, -1.3), (0.0, -1.3)], [0, 0.02, 0.02, 0.02, 0], 1), 12, steel, start=90)
    a.add("Base", axial(socket))
    orb_f = -1.72
    orb = sh.sphere(0.32, None, segments=12, rings=8).transformed(T(0, AXIS_Y, -orb_f))
    a.add("Glass", orb)
    core = sh.sphere(0.19, neon, segments=10, rings=6)
    core.pos += core.nrm * (0.05 * fbm(core.pos * 6.0 + 3.1, 3))[:, None]
    sh.recompute_normals(core)
    a.add("AccentPink", core.transformed(T(0, AXIS_Y, -orb_f)))
    for k in range(3):
        band = sh.torus(0.335, 0.026, dark, segments=14, sides=4)
        band = band.transformed(compose(T(0, AXIS_Y, -orb_f), R(0, 0, k * 60), R(0, 0, 90)))
        a.add("Base", band)
    equator = sh.torus(0.335, 0.03, neon, segments=16, sides=4)
    a.add("Accent", ring_at(equator, orb_f))
    cap = sh.lathe(sh.round_polyline([(0.0, -2.1), (0.1, -2.1), (0.14, -2.04), (0.12, -1.98), (0.0, -1.98)], [0, 0.02, 0.02, 0.02, 0], 1), 10, steel)
    a.add("Base", axial(cap))

    rng = np.random.default_rng(7)
    for sgn in (-1, 1):
        base_t = 0 if sgn > 0 else 180
        for lane, dt in ((0, 14), (1, -16)):
            fs = np.linspace(-0.92, 0.22, 7)
            pts = []
            for i, f in enumerate(fs):
                jag = (12 if i % 2 else -12) + rng.uniform(-5, 5)
                pts.append((f, base_t + sgn * (dt + jag * 0.6)))
            a.add("Accent", vein(pts, 0.024, neon))

    for k in range(7):
        ang = np.radians(k * 360 / 7 + 10)
        r = 1.28 + 0.12 * np.sin(k * 2.1)
        f = 1.1 + 0.35 * np.cos(k * 1.7)
        shard = sh.gem(0.08 + 0.03 * (k % 3), 0.34 + 0.08 * (k % 2), 6, neon)
        pos = (np.cos(ang) * r, AXIS_Y + np.sin(ang) * r, -f)
        a.add("AccentPink" if k % 2 else "Accent", shard.transformed(compose(T(*pos), R(k * 40, k * 25, k * 55))))
    a.point("muzzle", (0, AXIS_Y, -2.88))
    a.point("grip", (0, -0.1, 0))
    a.point("orb", (0, AXIS_Y, -orb_f))
    a.point("dish", (0, AXIS_Y, -DISH_F))
    return a
