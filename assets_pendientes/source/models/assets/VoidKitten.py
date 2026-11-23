import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, blob, eye, plastic


def build():
    a = pet_asset("VoidKitten", 2600, 3.0)
    a.role("Glow", "neon", color=(150, 70, 255))
    fur = Material("glossy", color=(20, 18, 28), rough=0.35, metal=0.0, dirt=0.0)
    a.add("Body", blob((1.6, 1.4, 2.0), fur, 12, 8))
    a.add("Body", blob((1.4, 1.25, 1.3), fur, 12, 8).transformed(T(0, 0.8, -1.1)))
    a.add("Body", blob((0.5, 0.3, 0.35), fur, 8, 5).transformed(T(0, 0.58, -1.7)))
    for side in (-1, 1):
        ear = sh.extrude(np.asarray([(-0.28, 0.0), (0.28, 0.0), (0.04, 0.62)]), 0.16, fur, bevel=0.03, corner_radius=0.0)
        a.add("Body", ear.transformed(compose(T(side * 0.42, 1.3, -1.1), R(0, 0, side * -10))))
        inner = sh.extrude(np.asarray([(-0.16, 0.0), (0.16, 0.0), (0.03, 0.4)]), 0.04, None, bevel=0.0, corner_radius=0.0)
        a.add("Glow", inner.transformed(compose(T(side * 0.42, 1.36, -1.19), R(0, 0, side * -10))))
        a.add("Glow", blob((0.3, 0.34, 0.2), None, 8, 5).transformed(T(side * 0.29, 0.9, -1.7)))
        for z in (-0.65, 0.65):
            a.add("Body", blob((0.38, 0.6, 0.4), fur, 8, 5).transformed(T(side * 0.48, -0.65, z)))
    a.add("Body", sh.sweep([(0.0, 0.2, 0.95), (0.0, 0.5, 1.4), (0.2, 1.0, 1.55), (0.1, 1.5, 1.35)], 0.11, 6, fur, samples=10, taper=lambda t: 1.0 - 0.45 * t))
    a.add("Glow", sh.torus(0.62, 0.05, None, segments=18, sides=4).transformed(T(0, 2.0, -1.1)))
    return a
