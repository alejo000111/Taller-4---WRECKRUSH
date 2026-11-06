import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, eye
from _chaos_lib import basalt


def chunk(size, mat, seed, segments=8, rings=5):
    ball = sh.sphere(1.0, mat, segments, rings)
    rng = np.random.default_rng(seed)
    ball.pos *= 1 + rng.normal(0, 0.1, (len(ball.pos), 1))
    ball.pos *= np.asarray(size) / 2.0
    return sh.recompute_normals(ball)


def build():
    a = pet_asset("MagmaGolem", 2600, 3.0)
    a.role("Lava", "neon", color=(255, 120, 20))
    rock = basalt(color=(52, 40, 38), glow=(255, 120, 20), veins=0.72, vein_glow=0.95)
    a.add("Body", chunk((2.0, 1.8, 1.5), rock, 3, 10, 7))
    a.add("Body", chunk((1.15, 0.95, 1.05), rock, 5).transformed(compose(T(0.08, 1.2, -0.1), R(0, 0, -4))))
    for side, seed in ((-1, 7), (1, 9)):
        a.add("Body", chunk((0.85, 0.8, 0.85), rock, seed).transformed(T(side * 1.1, 0.45, 0)))
        a.add("Body", chunk((0.75, 1.4, 0.75), rock, seed + 1).transformed(compose(T(side * 1.28, -0.2, 0), R(0, 0, side * 8))))
        a.add("Body", chunk((0.95, 0.6, 0.95), rock, seed + 2).transformed(T(side * 1.35, -0.95, -0.05)))
        a.add("Body", chunk((0.75, 0.85, 0.75), rock, seed + 3).transformed(T(side * 0.55, -1.2, 0)))
        a.add("Lava", sh.box((0.26, 0.15, 0.1), None).transformed(compose(T(0.08 + side * 0.25, 1.25, -0.63), R(0, 0, -4))))
    for (x, y, ang, length) in ((-0.3, 0.05, 16, 1.2), (0.38, -0.2, -34, 0.8), (0.1, 0.45, 70, 0.5)):
        a.add("Lava", sh.box((0.1, length, 0.06), None).transformed(compose(T(x, y, -0.76), R(0, 0, ang))))
    return a
