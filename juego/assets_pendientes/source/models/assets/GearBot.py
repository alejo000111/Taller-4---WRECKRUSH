import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, eye, plastic, metal, painted


def gear(radius, thick, mat, teeth=10):
    pts = []
    for k in range(teeth * 2):
        ang = 2 * np.pi * k / (teeth * 2)
        r = radius if k % 2 == 0 else radius * 0.8
        pts.append((np.cos(ang) * r, np.sin(ang) * r))
    return sh.extrude(np.asarray(pts), thick, mat, bevel=0.02, corner_radius=0.0, smooth_angle=20)


def build():
    a = pet_asset("GearBot", 2000, 3.0)
    a.role("Glow", "neon", color=(255, 122, 26))
    a.role("Tip", "neon", color=(255, 59, 59))
    plate = Material("diamondplate", color=(150, 154, 164), pitch=0.2, dirt=0.2)
    trim = metal((60, 62, 70))
    gold = Material("gold", color=(255, 210, 31), rough=0.3, dirt=0.15)
    rubber = Material("rubber", color=(30, 30, 34), pattern="ribs", freq=18.0)
    a.add("Body", sh.rounded_box((1.8, 1.8, 1.8), 0.25, 2, plate))
    a.add("Body", sh.rounded_box((1.5, 0.7, 0.12), 0.08, 1, trim).transformed(T(0, 0.25, -0.92)))
    a.add("Glow", sh.rounded_box((1.3, 0.42, 0.06), 0.06, 1, None).transformed(T(0, 0.25, -0.99)))
    a.add("Body", sh.cylinder(0.06, 0.9, trim, bevel=0.0, segments=6).transformed(T(0, 1.35, 0)))
    a.add("Tip", eye(0.18).transformed(T(0, 1.85, 0)))
    a.add("Body", gear(0.7, 0.22, gold).transformed(T(0, 0, 1.02)))
    a.add("Body", sh.cylinder(0.18, 0.3, trim, bevel=0.0, segments=8).transformed(compose(T(0, 0, 1.1), R(90, 0, 0))))
    for side in (-1, 1):
        a.add("Body", sh.lathe([(0.0, -0.18), (0.42, -0.18), (0.45, 0.0), (0.42, 0.18), (0.0, 0.18)], 12, rubber, smooth_angle=50).transformed(compose(T(side * 1.05, -0.9, 0), R(0, 0, 90))))
        a.add("Body", sh.cylinder(0.2, 0.38, gold, bevel=0.0, segments=8).transformed(compose(T(side * 1.06, -0.9, 0), R(0, 0, 90))))
        a.add("Body", sh.rounded_box((0.3, 0.7, 0.3), 0.1, 1, trim).transformed(T(side * 1.0, -0.2, -0.4)))
    return a
