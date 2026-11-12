import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import VERDANT, expedition_asset, leaves
from _landmark_lib import patch

H = 16.0


def build():
    a = expedition_asset("WallVine", 500, 9.0, atlas=256)
    stem = Material("wood", color=(70, 86, 52), dirt=0.3)
    leaf = leaves((64, 112, 70), scale=5.0, tips=0.3)
    rng = np.random.default_rng(9)
    for s in (-0.35, 0.0, 0.35):
        pts = [(s + 0.15 * np.sin(k * 1.3 + s * 4), H - k * H / 7, 0.2 * np.cos(k * 0.9)) for k in range(8)]
        a.add("Body", sh.sweep(pts, 0.08, 4, stem, samples=10))
        for k in range(1, 7):
            x, y, z = pts[k]
            a.add("Body", sh.box((0.7, 0.05, 0.45), leaf).transformed(compose(T(x + 0.2, y, z + 0.3), R(rng.uniform(-30, 30), rng.uniform(0, 180), rng.uniform(-40, 40)))))
    patch(a, [VERDANT], ["WallVine"])
    return a
