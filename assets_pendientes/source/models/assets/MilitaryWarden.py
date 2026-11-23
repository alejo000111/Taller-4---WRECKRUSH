import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _island_boss_lib import island_boss, ring_sockets, scale_asset
import _military_lib


def build():
    a = island_boss("MilitaryWarden", 7000, (255, 210, 31), (140, 255, 90), ((18.0, 34.0, 14.0), (0.0, 17.0, 0.0)), radius=26.0)
    camo = Material("military_camo")
    olive = Material("paint", color=(86, 96, 58), under=(70, 70, 64), wear=0.45, scratches=0.5, rough=0.55, metal=0.3, dirt=0.6)
    steel = Material("metal", color=(70, 74, 70), rough=0.45, polish=0.35, dirt=0.55, scratches=0.5)
    dark = Material("metal", color=(30, 32, 30), rough=0.6, polish=0.2, dirt=0.6)
    glass = Material("glossy", color=(20, 26, 22), metal=0.3, rough=0.1)
    hazard = Material("hazard", color=(255, 210, 31), color2=(26, 28, 24), width=0.2, angle=45)

    for side in (-1, 1):
        x = side * 5.2
        a.add("Body", sh.rounded_box((6.6, 2.4, 11.0), 0.6, 1, steel).transformed(T(x, 1.2, -1.2)))
        a.add("Body", sh.rounded_box((5.0, 9.0, 5.6), 0.9, 1, olive).transformed(compose(T(x, 7.0, 0.6), R(-8, 0, 0))))
        a.add("Body", sh.rounded_box((5.6, 3.0, 4.0), 0.6, 1, steel).transformed(T(x, 11.8, -1.6)))
        a.add("Body", sh.rounded_box((5.4, 8.0, 6.0), 0.9, 1, camo).transformed(compose(T(x, 15.6, 0.4), R(6, 0, 0))))
    a.add("Body", sh.rounded_box((14.0, 4.0, 9.0), 1.0, 1, dark).transformed(T(0, 20.0, 0.0)))
    a.add("Body", sh.rounded_box((18.0, 11.0, 12.0), 2.0, 2, camo).transformed(T(0, 27.0, 0.0)))
    a.add("Body", sh.rounded_box((14.0, 6.0, 1.0), 0.6, 1, olive).transformed(compose(T(0, 26.0, -6.2), R(-6, 0, 0))))
    a.add("Body", sh.box((14.4, 0.8, 1.2), hazard).transformed(T(0, 22.6, -6.0)))
    a.add("Body", sh.rounded_box((7.0, 4.0, 7.4), 1.0, 1, olive).transformed(T(0, 34.6, -0.4)))
    a.add("Body", sh.rounded_box((6.0, 1.6, 0.6), 0.3, 1, glass).transformed(T(0, 35.0, -4.1)))
    a.add("Eyes", sh.box((5.0, 0.6, 0.3), None).transformed(T(0, 35.0, -4.35)))
    a.add("Body", sh.cylinder(0.25, 6.0, dark, segments=6).transformed(T(2.6, 38.4, 2.0)))
    a.add("Core", sh.cylinder(1.4, 0.6, None, segments=12).transformed(compose(T(0, 28.4, -6.9), R(90, 0, 0))))

    for side in (-1, 1):
        x = side * 10.0
        a.add("Body", sh.rounded_box((6.0, 5.0, 8.0), 1.0, 1, olive).transformed(T(x, 32.0, 0.0)))
        a.add("Body", sh.rounded_box((3.6, 2.6, 9.0), 0.5, 1, dark).transformed(T(x, 35.6, -0.6)))
        for k in range(2):
            a.add("Body", sh.cylinder(0.55, 5.0, steel, segments=8).transformed(compose(T(x + (k - 0.5) * 1.6, 35.6, -6.6), R(90, 0, 0))))

    for side, role in ((-1, "ArmL"), (1, "ArmR")):
        x = side * 13.0
        a.add(role, sh.sphere(2.8, steel, 10, 6).transformed(T(x, 29.0, 0.0)))
        a.add(role, sh.rounded_box((4.6, 9.0, 4.6), 0.8, 1, camo).transformed(compose(T(side * 14.0, 23.6, 0.0), R(0, 0, side * 6))))
        a.add(role, sh.rounded_box((4.0, 8.0, 4.4), 0.8, 1, steel).transformed(T(side * 14.6, 15.4, -1.0)))
        shield = sh.rounded_box((10.0, 15.0, 1.4), 0.8, 2, olive)
        a.add(role, shield.transformed(compose(T(side * 15.0, 15.0, -4.6), R(0, side * 12, 0))))
        a.add(role, sh.box((8.0, 0.8, 1.6), hazard).transformed(compose(T(side * 15.0, 21.0, -4.6), R(0, side * 12, 0))))
        a.add(role, sh.box((1.2, 12.0, 1.8), steel).transformed(compose(T(side * 15.0, 14.6, -4.8), R(0, side * 12, 0))))

    ring_sockets(a, "WeakSocket", 4, 8.4, (16.0, 10.0), start=0.0)
    return scale_asset(a, 1.1)
