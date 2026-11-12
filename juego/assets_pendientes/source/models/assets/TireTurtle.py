import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, blob, eye, plastic, metal


def build():
    a = pet_asset("TireTurtle", 2000, 3.0)
    a.role("Eyes", "neon", color=(255, 255, 255))
    rubber = Material("rubber", color=(28, 28, 32), pattern="ribs", freq=26.0)
    gold = Material("gold", color=(255, 210, 31), rough=0.25, dirt=0.15)
    skin = plastic((120, 170, 90), rough=0.6, scuff=0.2)
    dark = metal((40, 40, 44))
    a.add("Body", sh.lathe([(0.6, -0.45), (1.15, -0.45), (1.3, -0.25), (1.32, 0.25), (1.15, 0.45), (0.6, 0.45), (0.6, -0.45)], 20, rubber, closed=True, smooth_angle=50).transformed(T(0, 0.15, 0)))
    a.add("Body", sh.lathe([(0.0, 0.25), (0.75, 0.25), (0.7, 0.55), (0.35, 0.72), (0.0, 0.74)], 14, gold, smooth_angle=40).transformed(T(0, 0.15, 0)))
    for k in range(5):
        ang = np.radians(k * 72)
        a.add("Body", sh.cylinder(0.06, 0.06, dark, bevel=0.0, segments=6).transformed(T(np.cos(ang) * 0.42, 0.88, np.sin(ang) * 0.42)))
    a.add("Body", blob((0.9, 0.85, 1.0), skin, 10, 7).transformed(T(0, 0.15, -1.55)))
    a.add("Body", sh.lathe([(0.0, 0.0), (0.3, 0.0), (0.3, 0.6), (0.0, 0.6)], 8, skin, smooth_angle=40).transformed(compose(T(0, 0.12, -1.0), R(90, 0, 0))))
    for side in (-1, 1):
        a.add("Eyes", eye(0.1).transformed(T(side * 0.24, 0.32, -1.98)))
        a.add("Body", eye(0.05, dark).transformed(T(side * 0.24, 0.32, -2.06)))
        for z in (-0.75, 0.75):
            a.add("Body", blob((0.55, 0.42, 0.6), skin, 8, 5).transformed(T(side * 1.05, -0.45, z)))
    a.add("Body", blob((0.3, 0.25, 0.4), skin, 6, 4).transformed(T(0, -0.1, 1.35)))
    return a
