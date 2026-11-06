import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _island_boss_lib import island_boss, piston, scale_asset


def build():
    a = island_boss("IndustrialTitan", 7000, (255, 120, 40), (255, 80, 30), ((22.0, 30.0, 14.0), (0.0, 15.0, 0.0)), radius=26.0)
    red = Material("paint", color=(160, 44, 38), under=(80, 76, 72), wear=0.5, scratches=0.45, rough=0.5, metal=0.35, dirt=0.65)
    steel = Material("metal", color=(84, 84, 88), rough=0.45, polish=0.35, dirt=0.6, scratches=0.45)
    dark = Material("metal", color=(34, 32, 32), rough=0.6, polish=0.2, dirt=0.7)
    plate = Material("diamondplate", color=(120, 122, 126), dirt=0.6)
    chrome = Material("chrome", color=(190, 192, 198), dirt=0.35)
    hazard = Material("hazard", color=(255, 160, 20), color2=(24, 24, 28), width=0.22, angle=45)
    brick = Material("concrete", color=(96, 70, 60), dirt=0.6)

    for side in (-1, 1):
        x = side * 6.0
        a.add("Body", sh.rounded_box((8.0, 2.6, 12.0), 0.6, 1, plate).transformed(T(x, 1.3, -1.0)))
        a.add("Body", sh.rounded_box((6.0, 7.0, 6.6), 0.8, 1, red).transformed(T(x, 6.0, 0.0)))
        a.add("Body", sh.cylinder(2.4, 3.0, dark, bevel=0.2, segments=10).transformed(compose(T(x, 10.4, 0.0), R(0, 0, 90))))
        a.add("Body", sh.rounded_box((6.6, 6.0, 7.0), 0.8, 1, steel).transformed(T(x, 14.2, 0.0)))
        piston(a, "Body", (x + side * 2.6, 3.4, 2.2), (x + side * 2.6, 13.0, 2.2), 0.5, 0.3, dark, chrome)

    a.add("Body", sh.rounded_box((16.0, 4.0, 10.0), 1.0, 1, dark).transformed(T(0, 18.4, 0.0)))
    a.add("Body", sh.rounded_box((24.0, 12.0, 13.0), 1.8, 2, red).transformed(T(0, 26.0, 0.0)))
    a.add("Body", sh.box((24.4, 1.0, 13.4), hazard).transformed(T(0, 20.6, 0.0)))
    a.add("Body", sh.tube(5.6, 4.0, 2.0, steel, segments=20).transformed(compose(T(0, 26.0, -6.6), R(90, 0, 0))))
    a.add("Core", sh.sphere(4.2, None, 16, 10).transformed(compose(T(0, 26.0, -5.4), R(90, 0, 0))))
    for k in range(8):
        angle = k * 45.0
        louver = sh.box((1.2, 4.0, 0.4), dark).transformed(compose(T(0, 26.0, -7.7), R(0, 0, angle), T(0, 3.0, 0)))
        a.add("Body", louver)

    for side in (-1, 1):
        x = side * 8.0
        a.add("Body", sh.cylinder(1.8, 12.0, brick, bevel=0.1, segments=12).transformed(T(x, 37.0, 4.0)))
        a.add("Body", sh.cylinder(2.1, 1.2, steel, segments=12).transformed(T(x, 43.4, 4.0)))
        a.add("Body", sh.cylinder(2.0, 0.8, hazard, segments=12).transformed(T(x, 35.0, 4.0)))
    a.add("Body", sh.rounded_box((8.0, 5.0, 7.0), 1.0, 1, steel).transformed(T(0, 34.4, -1.0)))
    a.add("Body", sh.box((7.0, 1.2, 0.4), dark).transformed(T(0, 34.6, -4.6)))
    for side in (-1, 1):
        a.add("Eyes", sh.box((2.4, 0.8, 0.3), None).transformed(T(side * 1.8, 34.6, -4.85)))

    for side, role in ((-1, "ArmL"), (1, "ArmR")):
        x = side * 14.6
        a.add(role, sh.sphere(3.2, steel, 10, 6).transformed(T(x, 29.0, 0.0)))
        a.add(role, sh.rounded_box((6.0, 9.0, 6.0), 1.0, 1, red).transformed(compose(T(side * 16.0, 23.0, 0.0), R(0, 0, side * 6))))
        a.add(role, sh.cylinder(2.2, 3.0, dark, segments=10).transformed(compose(T(side * 16.6, 18.0, 0.0), R(0, 0, 90))))
    a.add("ArmR", sh.rounded_box((5.0, 6.0, 5.0), 0.8, 1, steel).transformed(T(16.8, 14.4, 0.0)))
    a.add("ArmR", sh.rounded_box((9.0, 1.6, 9.0), 0.4, 1, plate).transformed(T(16.8, 11.2, 0.0)))
    a.add("ArmR", sh.rounded_box((9.0, 1.6, 9.0), 0.4, 1, plate).transformed(T(16.8, 6.6, 0.0)))
    for dx in (-3.4, 3.4):
        for dz in (-3.4, 3.4):
            a.add("ArmR", sh.cylinder(0.45, 4.6, chrome, segments=6).transformed(T(16.8 + dx, 8.9, dz)))
    a.add("ArmL", sh.rounded_box((5.0, 5.0, 5.0), 0.8, 1, steel).transformed(T(-16.8, 15.0, 0.0)))
    links = []
    for k in range(6):
        links.append(sh.torus(0.9, 0.32, dark, 8, 5).transformed(compose(T(-16.8, 11.8 - k * 1.4, 0.0), R(0, 90 * (k % 2), 90))))
    for link in links:
        a.add("ArmL", link)
    hook = [(-16.8, 3.6, 0.0), (-16.8, 1.8, 0.3), (-17.8, 0.6, -1.2), (-17.4, 0.8, -3.0), (-16.4, 2.2, -3.6)]
    a.add("ArmL", sh.sweep(hook, 0.75, 8, steel, samples=10, taper=lambda t: 1.0 - 0.4 * t))
    return scale_asset(a, 1.1)
