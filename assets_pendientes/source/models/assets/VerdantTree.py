import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import VERDANT, expedition_asset, leaves, jagged


def clump(seed, radius, mat, squash=0.75):
    ball = sh.sphere(radius, mat, 9, 6)
    rng = np.random.default_rng(seed)
    ball.pos *= 1 + rng.normal(0, 0.12, (len(ball.pos), 1))
    ball.pos[:, 1] *= squash
    return sh.recompute_normals(ball)


def build():
    a = expedition_asset("VerdantTree", 1400, 16.0)
    bark = Material("wood", color=(92, 74, 58), dirt=0.5)
    leaf = leaves((66, 108, 62), scale=1.4, tips=0.35)
    trunk = sh.lathe([(0.0, 0.0), (2.2, 0.0), (1.7, 0.6), (1.35, 2.0), (1.15, 9.0), (0.95, 15.0), (0.6, 19.5), (0.0, 20.0)], 9, bark, smooth_angle=40)
    a.add("Body", jagged(trunk, 4, amount=0.04, scale=0.8))
    for ang, y, length in ((30, 11.0, 5.0), (160, 13.5, 4.5), (260, 15.5, 4.0)):
        rad = np.radians(ang)
        tip = (np.cos(rad) * length, y + 2.6, np.sin(rad) * length)
        a.add("Body", sh.sweep([(0.0, y, 0.0), (tip[0] * 0.5, y + 1.6, tip[2] * 0.5), tip], 0.35, 5, bark, samples=4, taper=lambda t: 1.0 - 0.6 * t))
    rng = np.random.default_rng(12)
    spots = [(0.0, 21.0, 0.0, 6.2), (3.6, 18.2, 1.8, 4.6), (-3.4, 17.6, -2.0, 4.4), (1.4, 16.4, -3.6, 4.0), (-1.8, 15.6, 3.6, 3.8)]
    for k, (x, y, z, r) in enumerate(spots):
        a.add("Body", clump(20 + k, r, leaf).transformed(T(x, y, z)))
    for k in range(3):
        ang = rng.uniform(0, 2 * np.pi)
        a.add("Body", sh.box((0.9, 0.15, 0.5), leaf).transformed(compose(T(np.cos(ang) * 2.5, 0.08, np.sin(ang) * 2.5), R(0, np.degrees(ang), 0))))
    a.meta["scatter"] = {"target": VERDANT, "key": "Trunk", "remove": ["Trunk", "Canopy"], "radius": 6.0}
    return a
