import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _chaos_lib import basalt, rock, grounded

LAVA = (255, 110, 20)


def build():
    a = Asset("MeteorRock", budget=1500, atlas=1024, ao_radius=0.7, edge_width=0.05, gradient=0.06, highlight=0.35, preview_radius=5.4,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Lava", "neon", color=LAVA)

    stone = basalt(color=(46, 34, 30), glow=LAVA, veins=0.78, vein_glow=0.95, crack_scale=0.7)
    core = rock(3.2, stone, 5, squash=(1.05, 0.85, 1.0), jitter=0.12, segments=14, rings=9)
    a.add("Body", grounded(core.transformed(T(0, 2.75, 0)), 0.0))
    for seed, (x, y, z, r) in enumerate(((2.2, 4.4, 1.0, 1.4), (-2.0, 4.6, -0.8, 1.2), (0.6, 5.3, -1.6, 1.1), (-1.0, 1.0, 2.6, 1.0), (2.6, 0.9, -1.8, 0.9))):
        chunk = rock(r, stone, 60 + seed, squash=(1.0, 0.8, 1.1), jitter=0.1, segments=7, rings=4)
        a.add("Body", grounded(chunk.transformed(compose(T(x, y, z), R(seed * 23, seed * 47, 0)))))

    a.add("Lava", grounded(rock(3.05, None, 9, squash=(1.05, 0.85, 1.0), jitter=0.1, segments=10, rings=6).transformed(T(0, 2.75, 0)), 0.05))
    rng = np.random.default_rng(4)
    for k in range(6):
        ang = rng.uniform(0, 2 * np.pi)
        d = np.array([np.cos(ang), 0.0, np.sin(ang)])
        start = d * 2.6 + np.array([0, 0.36, 0])
        path = [tuple(start), tuple(d * 3.2 + np.array([0, 0.18, rng.normal(0, 0.2)])), tuple(d * 3.8 + np.array([0, 0.14, rng.normal(0, 0.25)]))]
        crack = sh.sweep(path, 0.12, 3, None, samples=5, taper=lambda u: 1.0 - 0.85 * u)
        a.add("Lava", crack)

    scorch = basalt(color=(22, 18, 16), glow=LAVA, veins=0.74, vein_glow=0.9, crack_scale=1.4)
    ring = sh.lathe([(0.0, 0.0), (4.0, 0.0), (3.6, 0.1), (2.6, 0.25), (0.0, 0.25)], 16, scorch, smooth_angle=40)
    a.add("Body", ring)

    destructible(a, "Event")
    collider(a, "Hitbox", (6.0, 6.0, 6.0), (0, 3.0, 0), shape="Ball")
    return a
