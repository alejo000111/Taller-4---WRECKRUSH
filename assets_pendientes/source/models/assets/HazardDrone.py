import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, eye, metal, painted


def build():
    a = pet_asset("HazardDrone", 2400, 3.0)
    a.role("Eye", "neon", color=(255, 59, 59))
    a.role("Rotors", "neon", color=(34, 225, 255))
    shell = Material("hazard", color=(255, 210, 31), color2=(24, 24, 28), width=0.18, angle=45, wear=0.3, dirt=0.25)
    body = metal((36, 38, 46))
    arm = metal((60, 62, 70))
    a.add("Body", sh.lathe([(0.0, -0.3), (0.7, -0.3), (0.82, -0.1), (0.82, 0.12), (0.6, 0.3), (0.0, 0.32)], 12, body, smooth_angle=40))
    a.add("Body", sh.lathe([(0.83, -0.08), (0.88, -0.08), (0.88, 0.1), (0.83, 0.1)], 16, shell, closed=True, smooth_angle=40))
    a.add("Body", sh.lathe([(0.0, 0.3), (0.4, 0.3), (0.3, 0.45), (0.0, 0.48)], 10, shell, smooth_angle=40))
    a.add("Body", sh.lathe([(0.0, -0.2), (0.32, -0.2), (0.28, 0.2), (0.0, 0.25)], 10, body, smooth_angle=40).transformed(compose(T(0, -0.12, -0.72), R(-90, 0, 0))))
    a.add("Eye", eye(0.2).transformed(T(0, -0.15, -0.95)))
    for sx in (-1, 1):
        for sz in (-1, 1):
            a.add("Body", sh.box((0.14, 0.12, 1.0), arm).transformed(compose(T(sx * 0.55, 0.05, sz * 0.55), R(0, sx * sz * -45, 0))))
            a.add("Body", sh.cylinder(0.16, 0.25, arm, bevel=0.0, segments=8).transformed(T(sx * 1.0, 0.15, sz * 1.0)))
            disc = sh.lathe([(0.12, 0.0), (0.5, 0.0), (0.5, 0.06), (0.12, 0.06)], 16, None, closed=True, smooth_angle=50)
            a.add("Rotors", disc.transformed(T(sx * 1.0, 0.25, sz * 1.0)))
            a.add("Body", sh.box((0.98, 0.03, 0.1), arm).transformed(compose(T(sx * 1.0, 0.33, sz * 1.0), R(0, 30 * sx * sz, 0))))
    return a
