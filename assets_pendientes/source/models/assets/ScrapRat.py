import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, blob, eye, plastic, metal, painted


def build():
    a = pet_asset("ScrapRat", 1600, 3.0)
    a.role("Eyes", "neon", color=(255, 210, 31))
    a.role("Bolt", "neon", color=(255, 122, 26))
    hull = painted((128, 116, 104), decals=[
        *[{"type": "rect", "center": (x, y), "size": (0.08, 0.08), "radius": 0.04, "color": (70, 64, 58), "wear": 0.2} for x in (-0.7, 0.7) for y in (-0.4, 0.4)],
        {"type": "rect", "center": (0.0, 0.0), "size": (2.6, 0.05), "color": (80, 72, 64), "wear": 0.3},
    ], wear=0.5, scratches=0.6)
    pink = plastic((220, 150, 150), rough=0.55)
    dark = metal((60, 56, 52))
    a.add("Body", blob((1.9, 1.5, 2.3), hull, 12, 8))
    a.add("Body", blob((1.3, 1.2, 1.4), hull, 10, 7).transformed(T(0, 0.5, -1.15)))
    a.add("Body", blob((0.62, 0.5, 0.8), pink, 8, 6).transformed(T(0, 0.33, -1.85)))
    a.add("Body", eye(0.1, dark).transformed(T(0, 0.42, -2.22)))
    for side in (-1, 1):
        ear = sh.lathe([(0.0, 0.0), (0.36, 0.0), (0.36, 0.08), (0.0, 0.08)], 12, pink, closed=False, smooth_angle=40)
        a.add("Body", ear.transformed(compose(T(side * 0.45, 1.15, -1.05), R(90, 0, side * 10))))
        a.add("Eyes", eye(0.14).transformed(T(side * 0.31, 0.65, -1.72)))
        for z in (-0.6, 0.6):
            a.add("Body", blob((0.38, 0.5, 0.5), dark, 6, 4).transformed(T(side * 0.7, -0.62, z)))
    a.add("Body", sh.sweep([(0.0, 0.0, 1.05), (0.0, 0.15, 1.6), (0.25, 0.5, 2.1), (0.1, 0.9, 2.45)], 0.08, 5, pink, samples=10, taper=lambda t: 1.0 - 0.6 * t))
    a.add("Bolt", sh.cylinder(0.3, 0.3, None, bevel=0.0, segments=6).transformed(T(0, 0.82, 0.2)))
    a.add("Body", sh.cylinder(0.18, 0.12, dark, bevel=0.0, segments=6).transformed(T(0, 0.99, 0.2)))
    return a
