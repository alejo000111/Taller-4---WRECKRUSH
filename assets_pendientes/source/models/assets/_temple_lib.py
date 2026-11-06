import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh

MARBLE = (138, 136, 158)
GOLD = (245, 199, 116)


def marble(color=MARBLE, veins=(186, 182, 204)):
    return Material("paint", color=color, under=color, wear=0.0, scratches=0.15, rough=0.35, dirt=0.35, skin=False, decals=[
        {"type": "rect", "center": (x, 0.0), "size": (0.05, 40.0), "angle": a, "color": veins, "rough": 0.25, "wear": 0.5}
        for x, a in ((-1.4, 14), (0.6, -21), (1.9, 33), (-0.3, 58))
    ])


def fluted(radius, height, mat, flutes=12, depth=0.12, rings=1):
    pts = []
    count = flutes * 2
    for k in range(count):
        ang = 2 * np.pi * k / count
        r = radius - (depth if k % 2 else 0.0)
        pts.append((np.cos(ang) * r, np.sin(ang) * r))
    shaft = sh.extrude(np.asarray(pts), height, mat, bevel=0.0, corner_radius=0.0, smooth_angle=50, caps=False)
    return shaft.transformed(compose(T(0, height / 2, 0), R(-90, 0, 0)))


def broken_top(radius, y, mat, seed):
    rng = np.random.default_rng(seed)
    pts = [(0.0, y + 0.6)]
    profile = [(0.0, y + rng.uniform(0.4, 1.4))]
    disc = sh.lathe([(radius, y), (radius * 0.8, y + 0.9), (radius * 0.35, y + 1.6), (0.0, y + 1.2)], 10, mat, smooth_angle=60)
    out = disc.copy()
    out.pos[:, 1] += rng.normal(0, 0.35, len(out.pos)) * (out.pos[:, 1] > y + 0.05)
    return sh.recompute_normals(out)


def plinth(width, height, mat, y=0.0):
    return sh.rounded_box((width, height, width), 0.08, 1, mat).transformed(T(0, y + height / 2, 0))
