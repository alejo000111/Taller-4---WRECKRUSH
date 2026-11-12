import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _hall_lib import HALL, GOLD, SILVER, BRONZE, ORANGE, hall_asset, gold, dark_metal
from _bay_lib import ibeam
from _ground_lib import ring
from _landmark_lib import landmark, box_collider

PEDESTALS = [
    ("Gold", (0.0, -2.15), (10.0, 7.0, 10.0), 13.0),
    ("Silver", (12.5, -0.15), (9.0, 5.0, 9.0), 12.0),
    ("Bronze", (-12.5, -0.15), (9.0, 3.5, 9.0), 12.0),
]


def build():
    a = hall_asset("HallPodium", 3600, 30.0)
    a.role("Gold", "neon", color=GOLD)
    a.role("Silver", "neon", color=SILVER)
    a.role("Bronze", "neon", color=BRONZE)
    a.role("Accent", "neon", color=ORANGE)
    a.role("Lens", "neon", color=(255, 246, 220))
    steel = dark_metal()
    metals = {
        "Gold": Material("gold", color=GOLD, rough=0.18, dirt=0.04),
        "Silver": Material("chrome", color=SILVER, rough=0.15),
        "Bronze": Material("gold", color=(196, 116, 56), rough=0.25, dirt=0.06),
    }
    base_top = 0.8
    a.add("Body", sh.rounded_box((38.0, 0.6, 16.0), 0.1, 1, steel).transformed(T(0, 0.5, -0.15)))
    for sx, sz, w, d in ((0, -1, 38.2, 0.2), (0, 1, 38.2, 0.2), (-1, 0, 0.2, 16.2), (1, 0, 0.2, 16.2)):
        a.add("Accent", sh.box((w, 0.2, d), None).transformed(T(sx * 19.0, 0.85, -0.15 + sz * 8.0)))
    for role, (x, z), (w, h, d), glow in PEDESTALS:
        metal = metals[role]
        a.add("Body", sh.rounded_box((w - 0.06, h - 0.35, d - 0.06), 0.08, 1, metal, faces=["+x", "-x", "+z", "-z"]).transformed(T(x, base_top + (h - 0.35) / 2, z)))
        a.add("Body", sh.rounded_box((w + 0.3, 0.35, d + 0.3), 0.08, 1, steel).transformed(T(x, base_top + h - 0.175, z)))
        a.add(role, sh.box((w + 0.34, 0.12, d + 0.34), None).transformed(T(x, base_top + h - 0.42, z)))
        a.add("Body", sh.rounded_box((w + 0.5, 0.4, d + 0.5), 0.08, 1, steel).transformed(T(x, base_top + 0.2, z)))
        a.add(role, ring(glow / 2 - 0.35, glow / 2, 0.22, None, segments=32).transformed(T(x, 0.85, z)))
        for sx in (-1, 1):
            a.add(role, sh.box((0.12, h - 1.2, 0.12), None).transformed(T(x + sx * (w / 2 - 0.02), base_top + h / 2 - 0.1, z - d / 2 + 0.6)))
    for x in (-23.0, 23.0):
        a.add("Body", ibeam(30.0, steel, 1.6, 1.6).transformed(T(x, 0.0, 7.85)))
        a.add("Body", sh.rounded_box((2.6, 0.5, 2.6), 0.06, 1, steel).transformed(T(x, 0.25, 7.85)))
    a.add("Body", sh.rounded_box((48.0, 1.6, 1.6), 0.1, 1, steel).transformed(T(0, 30.8, 7.85)))
    a.add("Accent", sh.box((46.0, 0.3, 0.4), None).transformed(T(0, 30.0, 6.95)))
    for x in (-12.5, 0.0, 12.5):
        a.add("Body", sh.box((0.5, 0.5, 12.0), steel).transformed(T(x, 30.8, 1.85)))
        fixture = sh.lathe([(0.0, -1.0), (0.8, -1.0), (1.1, 0.6), (0.9, 1.0), (0.0, 1.0)], 10, steel, smooth_angle=40)
        a.add("Body", fixture.transformed(compose(T(x, 29.6, -3.65), R(-15, 0, 0))))
        a.add("Lens", sh.cylinder(0.8, 0.1, None, bevel=0.0, segments=10).transformed(compose(T(x, 29.6, -3.65), R(-15, 0, 0), T(0, -1.02, 0))))
    landmark(a, HALL, "Podium", fit="none", bounds_all=True, keep=["Pedestal1", "Pedestal2", "Pedestal3", "LightColumn", "SparkleSource"],
             hide=["Pedestal1", "Pedestal2", "Pedestal3"],
             colliders=[box_collider("Base", (38.0, 0.6, 16.0), (0, 0.5, -0.15)), box_collider("PostL", (1.6, 30.0, 1.6), (-23.0, 15.0, 7.85)), box_collider("PostR", (1.6, 30.0, 1.6), (23.0, 15.0, 7.85))])
    return a
