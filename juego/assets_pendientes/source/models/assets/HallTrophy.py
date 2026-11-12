import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _hall_lib import HALL, GOLD, hall_asset, gold, marble
from _landmark_lib import landmark, box_collider


def build():
    a = hall_asset("HallTrophy", 1800, 9.0)
    a.role("Glow", "neon", color=GOLD)
    stone = marble()
    metal = gold(0.16)
    a.add("Body", sh.rounded_box((8.0, 0.6, 8.0), 0.08, 1, stone).transformed(T(0, 0.3, 0)))
    a.add("Body", sh.rounded_box((7.2, 3.0, 7.2), 0.06, 1, stone).transformed(T(0, 2.1, 0)))
    a.add("Body", sh.rounded_box((7.8, 0.4, 7.8), 0.08, 1, stone).transformed(T(0, 3.8, 0)))
    for sx, sz, w, d in ((0, -1, 8.2, 0.2), (0, 1, 8.2, 0.2), (-1, 0, 0.2, 8.2), (1, 0, 0.2, 8.2)):
        a.add("Glow", sh.box((w, 0.2, d), None).transformed(T(sx * 4.0, 3.95, sz * 4.0)))
    plaque = Material("gold", color=(230, 180, 60), rough=0.3, dirt=0.05)
    a.add("Body", sh.box((4.0, 1.0, 0.06), plaque).transformed(T(0, 2.1, -3.62)))
    profile = [(0.0, 0.0), (2.5, 0.0), (2.5, 0.4), (1.9, 0.9), (0.8, 1.3), (0.6, 2.6), (0.75, 4.4), (1.4, 4.9), (2.6, 5.9), (3.2, 7.6), (3.4, 10.2), (3.6, 10.6), (3.3, 10.7), (3.0, 10.2), (2.8, 7.8), (2.2, 6.4), (0.0, 6.2)]
    a.add("Body", sh.lathe(profile, 16, metal, smooth_angle=35).transformed(T(0, 4.3, 0)))
    for sx in (-1, 1):
        handle = sh.sweep([(sx * 2.9, 13.6, 0.0), (sx * 4.2, 13.4, 0.0), (sx * 4.3, 11.8, 0.0), (sx * 3.3, 10.6, 0.0)], 0.28, 6, metal, samples=10, caps=True)
        a.add("Body", handle)
    a.add("Glow", sh.torus(3.45, 0.12, None, segments=20, sides=4).transformed(T(0, 15.0, 0)))
    a.add("Body", sh.lathe([(0.0, 0.0), (0.7, 0.0), (0.0, 0.9)], 8, metal, smooth_angle=40).transformed(T(0, 15.3, 0)))
    landmark(a, f"{HALL}/Decor", "Trophy", fit="box", tint={"Glow": "TrophyRim"},
             colliders=[box_collider("Plinth", (8.0, 4.0, 8.0), (0, 2.0, 0)), box_collider("Cup", (6.4, 11.0, 6.4), (0, 9.8, 0))])
    return a
