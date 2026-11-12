import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, blob, eye, plastic, metal, painted


def build():
    a = pet_asset("BoltPup", 1600, 3.0)
    a.role("Glow", "neon", color=(34, 225, 255))
    yellow = painted((255, 210, 31), decals=[
        {"type": "rect", "center": (0.0, -0.1), "size": (3.0, 0.24), "color": (30, 30, 34), "wear": 0.3},
    ], wear=0.25)
    dark = metal((30, 30, 34))
    a.add("Body", sh.rounded_box((1.5, 1.2, 2.1), 0.45, 2, yellow))
    a.add("Body", sh.rounded_box((1.4, 1.2, 1.2), 0.42, 2, yellow).transformed(T(0, 0.8, -1.15)))
    a.add("Body", sh.rounded_box((0.8, 0.5, 0.55), 0.2, 1, dark).transformed(T(0, 0.55, -1.85)))
    a.add("Body", eye(0.09, dark).transformed(T(0, 0.75, -2.12)))
    for side in (-1, 1):
        ear = sh.extrude(np.asarray([(-0.25, 0.0), (0.25, 0.0), (0.05, 0.7)]), 0.16, dark, bevel=0.03, corner_radius=0.0)
        a.add("Body", ear.transformed(compose(T(side * 0.48, 1.35, -1.15), R(0, 0, side * -12))))
        a.add("Glow", eye(0.13).transformed(T(side * 0.3, 0.95, -1.76)))
        for z in (-0.7, 0.7):
            a.add("Body", sh.lathe([(0.0, 0.0), (0.24, 0.0), (0.22, 0.15), (0.17, 0.75), (0.0, 0.75)], 8, dark, smooth_angle=40).transformed(T(side * 0.5, -1.25, z)))
    bolt = sh.extrude(np.asarray([(0.0, 0.0), (0.35, 0.45), (0.12, 0.45), (0.42, 1.05), (-0.05, 0.5), (0.16, 0.5)]), 0.14, None, bevel=0.0, corner_radius=0.0)
    a.add("Glow", bolt.transformed(compose(T(0, 0.55, 1.15), R(0, 90, 0), R(0, 0, -20))))
    a.add("Body", sh.rounded_box((1.0, 0.15, 0.4), 0.06, 1, dark).transformed(T(0, 0.62, -0.2)))
    return a
