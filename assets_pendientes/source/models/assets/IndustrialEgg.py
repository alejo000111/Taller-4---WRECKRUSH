import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _egg_common import shell, band, place, egg_point, egg_normal, egg_radius, EGG_H


def build():
    a = Asset("IndustrialEgg", budget=3400, ao_radius=0.4, edge_width=0.035)
    a.role("Shell", "surface")
    a.role("Band", "surface")
    a.role("Glow", "neon", color=(255, 60, 40))
    armor = Material("egg_armor", color=(255, 59, 59), latitudes=(-0.95, 0.95), meridian_step=60.0, dirt=0.3)
    hazard = Material("hazard", color=(255, 210, 31), color2=(24, 24, 28), width=0.16, wear=0.3, skin=False)
    steel = Material("metal", color=(96, 98, 108), rough=0.36, polish=0.7, dirt=0.3, skin=False)
    grille = Material("metal", color=(60, 62, 70), rough=0.4, polish=0.6, dirt=0.35, skin=False, decals=[
        {"type": "rect", "center": (0.0, -0.18 + k * 0.12), "size": (0.5, 0.05), "radius": 0.02, "color": (14, 14, 16), "wear": 0.0, "raise": -0.01} for k in range(4)
    ])
    a.add("Shell", shell(armor, 24, 16))
    a.add("Band", band(-0.34, 0.18, 0.08, hazard, 24))
    for y in (-0.95, 0.95):
        a.add("Band", band(y - 0.06, y + 0.06, 0.04, steel, 24))
    gauge_at = egg_point(90, 0.95, 0.02)
    gauge_n = egg_normal(90, 0.95)
    face = Material("egg_gauge", center=tuple(gauge_at + gauge_n * 0.1), normal=tuple(gauge_n), radius=0.24, needle=50.0)
    a.add("Band", place(sh.cylinder(0.26, 0.18, steel, bevel=0.03, segments=16), 90, 0.95, 0.06))
    a.add("Band", place(sh.cylinder(0.22, 0.02, face, bevel=0.0, segments=16), 90, 0.95, 0.15))
    a.add("Band", place(sh.rounded_box((0.64, 0.1, 0.5), 0.03, 1, grille), 270, 0.75, 0.02))
    for theta in (0, 180):
        a.add("Band", place(sh.rounded_box((0.42, 0.12, 0.62), 0.03, 1, steel), theta, -0.75, 0.02))
    cap = sh.lathe([(0.0, 0.0), (0.36, 0.0), (0.3, 0.1), (0.14, 0.16), (0.0, 0.17)], 16, steel)
    top = EGG_H / 2 - 0.1
    a.add("Band", cap.transformed(T(0, top, 0)))
    a.add("Band", sh.cylinder(0.05, 0.22, steel, bevel=0.01, segments=8).transformed(T(0, top + 0.26, 0)))
    a.add("Band", sh.torus(0.2, 0.035, steel, segments=16, sides=5).transformed(T(0, top + 0.38, 0)))
    for k in range(3):
        spoke = sh.box((0.4, 0.04, 0.04), steel).transformed(compose(T(0, top + 0.38, 0), R(0, k * 60, 0)))
        a.add("Band", spoke)
    a.add("Band", place(sh.cylinder(0.11, 0.08, steel, bevel=0.01, segments=10), 30, 1.35, 0.02))
    a.add("Glow", place(sh.dome(0.09, 0.12, None, 10, 3), 30, 1.35, 0.07))
    return a
