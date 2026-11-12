import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel, louvre, trim_paint

STATIONS = "Decor/StationExpansion_20261006"
DESIGN = "Decor/DesignExpansion_20261006"


def deck(width, depth):
    return Material("diamondplate", color=(70, 80, 96), pitch=0.45, dirt=0.45)


def ibeam(height, mat, w=0.65, d=0.65):
    f = 0.12
    poly = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, -d / 2 + f), (0.07, -d / 2 + f), (0.07, d / 2 - f), (w / 2, d / 2 - f),
            (w / 2, d / 2), (-w / 2, d / 2), (-w / 2, d / 2 - f), (-0.07, d / 2 - f), (-0.07, -d / 2 + f), (-w / 2, -d / 2 + f)]
    return sh.extrude(np.asarray(poly), height, mat, bevel=0.0, corner_radius=0.0, smooth_angle=10).transformed(compose(T(0, height / 2, 0), R(-90, 0, 0)))


def canopy(width, depth, thick, mat):
    return sh.rounded_box((width, thick, depth), 0.06, 1, mat, faces=["+x", "-x", "+z", "-z", "+y", "-y"])


def paw_decals(center, scale, color):
    cx, cy = center
    out = [{"type": "rect", "center": (cx, cy + 0.25 * scale), "size": (1.9 * scale, 1.5 * scale), "radius": 0.7 * scale, "color": color, "wear": 0.25}]
    for dx, dy in ((-1.15, -1.0), (-0.4, -1.45), (0.4, -1.45), (1.15, -1.0)):
        out.append({"type": "rect", "center": (cx + dx * scale, cy + dy * scale), "size": (0.6 * scale, 0.75 * scale), "radius": 0.29 * scale, "color": color, "wear": 0.25})
    return out


def corner_brackets(width, depth, arm_long, arm_short, thick, y, mat):
    out = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            out.append(sh.box((arm_long, thick, 0.2), mat).transformed(T(sx * (width / 2 - arm_long / 2 - 0.05), y, sz * (depth / 2 - 0.1))))
            out.append(sh.box((0.2, thick, arm_short), mat).transformed(T(sx * (width / 2 - 0.1), y, sz * (depth / 2 - 0.2 - arm_short / 2))))
    return out
