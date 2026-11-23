import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import VERDANT, expedition_asset, leaves
from _landmark_lib import patch


def blade(length, width, mat, curl=0.35):
    pts = []
    for k in range(9):
        t = k / 8
        w = width * np.sin(np.pi * min(1.0, t * 1.1)) * (1 - 0.3 * t)
        pts.append((t * length, w / 2))
    outline = pts + [(x, -y) for x, y in reversed(pts[:-1])]
    leaf = sh.extrude(np.asarray(outline), 0.06, mat, bevel=0.0, corner_radius=0.0, smooth_angle=60)
    out = leaf.copy()
    x = out.pos[:, 0]
    out.pos[:, 2] += -(x / length) ** 2 * length * curl
    return sh.recompute_normals(out)


def build():
    a = expedition_asset("FernFrond", 300, 4.0, atlas=256)
    leaf = leaves((70, 116, 70), scale=4.0, tips=0.4)
    for k, (ang, tilt, length) in enumerate(((0, 55, 6.5), (25, 70, 5.5), (-28, 62, 5.8))):
        b = blade(length, 1.6, leaf)
        a.add("Body", b.transformed(compose(R(0, ang, 0), R(0, 0, tilt), R(90, 0, 0))))
    patch(a, [VERDANT], ["Fern"])
    return a
