import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _chaos_lib import basalt, obsidian, rock, grounded, crystal, VIOLET, PINK, CYAN


def slab_prism(sides, radius, height, mat, top_scale=0.8, rotation=0.0):
    mesh = sh.lathe([(0.0, -height / 2), (radius, -height / 2), (radius * top_scale, height / 2), (0.0, height / 2)], sides, mat, smooth_angle=10, start=rotation)
    return mesh


def build():
    a = Asset("ChaosGiant", budget=6000, atlas=1024, ao_radius=1.6, edge_width=0.1, gradient=0.06, highlight=0.45, preview_radius=18.0,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 16), ("FRONT", 180, 4), ("TOP", 200, 45)])
    a.role("Body", "surface")
    a.role("Crystal", "glass", color=VIOLET, transparency=0.2)
    a.role("Core", "neon", color=PINK)
    a.role("Glow", "neon", color=CYAN)

    stone = basalt(veins=0.8, glow=PINK)
    shell = obsidian(rim_glow=0.35, glow=PINK)
    a.add("Body", grounded(rock(8.0, stone, 2, squash=(1.0, 0.1, 1.0), jitter=0.05, segments=12, rings=4).transformed(T(0, 0.45, 0))))

    for sx in (-1, 1):
        x = sx * 4.5
        foot = grounded(rock(2.6, stone, 10 + sx, squash=(1.0, 0.45, 1.3), jitter=0.08, segments=8, rings=5).transformed(T(x, 1.6, -0.5)))
        a.add("Body", foot)
        a.add("Crystal", slab_prism(6, 2.0, 8.6, None, 0.85, 30).transformed(T(x, 7.4, 0.0)))
        a.add("Core", sh.box((0.4, 7.0, 0.4), None).transformed(T(x, 7.2, -2.0)))
        a.add("Body", slab_prism(6, 2.3, 1.4, shell, 0.9, 30).transformed(T(x, 11.2, 0)))

    a.add("Body", rock(5.6, stone, 30, squash=(1.0, 0.36, 0.6), jitter=0.06, segments=10, rings=6).transformed(T(0, 12.6, 0)))
    torso = sh.lathe([(0.0, 0.0), (4.2, 0.0), (5.4, 4.0), (5.2, 7.0), (3.6, 9.0), (0.0, 9.2)], 7, None, smooth_angle=10, start=90)
    a.add("Crystal", torso.transformed(compose(T(0, 13.6, 0), S(1.0, 1.0, 0.7))))
    a.add("Core", sh.sphere(2.1, None, 12, 7).transformed(T(0, 18.2, -0.6)))
    chest = sh.extrude([(-3.0, 0.0), (3.0, 0.0), (2.4, 2.6), (-2.4, 2.6)], 0.8, shell, bevel=0.1, corner_radius=0.0)
    a.add("Body", chest.transformed(compose(T(0, 19.6, -3.5), R(-10, 0, 0))))

    for sx in (-1, 1):
        shoulder = crystal(2.4, 4.4, None, facets=6, crown=0.5)
        a.add("Crystal", shoulder.transformed(compose(T(sx * 6.8, 22.0, 0), R(0, 0, sx * 70))))
        upper = slab_prism(6, 1.7, 7.0, stone, 0.8, 0)
        a.add("Body", upper.transformed(compose(T(sx * 8.4, 16.8, 0.2), R(0, 0, sx * 8))))
        fist = rock(2.1, None, 50 + sx, squash=(1.0, 1.0, 1.0), jitter=0.12, segments=7, rings=5)
        a.add("Crystal", fist.transformed(T(sx * 9.0, 11.0, 0.0)))
        for k in range(3):
            knuckle = crystal(0.45, 1.6, None, facets=4)
            a.add("Core", knuckle.transformed(compose(T(sx * 9.0 + (k - 1) * 0.8, 11.4, -1.9), R(-80, 0, 0))))

    head = crystal(2.6, 5.0, None, facets=6, crown=0.45)
    a.add("Crystal", head.transformed(T(0, 25.2, -0.4)))
    brow = sh.extrude([(-2.2, 0.0), (2.2, 0.0), (1.8, 0.8), (-1.8, 0.8)], 1.0, shell, bevel=0.06, corner_radius=0.0)
    a.add("Body", brow.transformed(T(0, 25.9, -2.0)))
    for sx in (-1, 1):
        a.add("Core", sh.box((1.2, 0.45, 0.2), None).transformed(compose(T(sx * 1.1, 25.4, -2.55), R(0, 0, sx * -12))))
    for k, (x, h, lean) in enumerate(((-1.6, 2.4, 20), (0.0, 3.2, 0), (1.6, 2.4, -20))):
        a.add("Crystal", crystal(0.6, h, None, facets=5).transformed(compose(T(x, 27.6 + h / 2 - 0.6, 0.0), R(0, 0, lean))))
    for sx in (-1, 1):
        for k, (dx, dy, h) in enumerate(((1.6, 24.0, 5.0), (3.2, 21.0, 4.0))):
            a.add("Crystal", crystal(0.8, h, None, facets=5).transformed(compose(T(sx * dx, dy, 2.8), R(40, 0, sx * -20))))

    rng = np.random.default_rng(6)
    for k in range(4):
        ang = np.radians(45 + 90 * k)
        p = np.array([np.cos(ang) * 9.6, 7.0 + 2.0 * (k % 2), np.sin(ang) * 9.6])
        a.add("Glow", crystal(0.6, 2.2, None, facets=4).transformed(compose(T(*p), R(rng.uniform(-30, 30), rng.uniform(0, 90), rng.uniform(-30, 30)))))
    for k in range(6):
        ang = np.radians(k * 60 + 15)
        d = np.array([np.cos(ang), 0.0, np.sin(ang)])
        path = [tuple(d * 2.0 + np.array([0, 0.9, 0])), tuple(d * 4.5 + np.array([0, 0.88, 0.3])), tuple(d * 7.4 + np.array([0, 0.85, -0.2]))]
        a.add("Glow", sh.sweep(path, 0.18, 3, None, samples=5, taper=lambda u: 1.0 - 0.8 * u))

    destructible(a, "Event")
    collider(a, "Hitbox", (11.0, 14.6, 8.0), (0, 20.2, 0))
    collider(a, "Legs", (11.0, 11.5, 6.0), (0, 6.6, 0))
    collider(a, "Arms", (21.0, 13.0, 5.0), (0, 16.8, 0))
    collider(a, "Base", (16.0, 1.0, 16.0), (0, 0.5, 0), shape="Cylinder")
    return a
