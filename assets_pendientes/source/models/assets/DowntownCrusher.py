import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _island_boss_lib import island_boss, piston, scale_asset


def build():
    a = island_boss("DowntownCrusher", 7000, (255, 170, 40), (255, 110, 30), ((22.0, 18.0, 20.0), (0.0, 9.0, 0.0)),
                    motions={"ArmL": "Arm", "ArmR": "Arm", "Core": "Core"}, radius=26.0)
    yellow = Material("paint", color=(236, 176, 34), under=(90, 90, 92), wear=0.5, scratches=0.5, rough=0.5, metal=0.3, dirt=0.6)
    steel = Material("metal", color=(78, 80, 86), rough=0.45, polish=0.35, dirt=0.55, scratches=0.5)
    dark = Material("metal", color=(34, 35, 38), rough=0.6, polish=0.2, dirt=0.6)
    chrome = Material("chrome", color=(200, 202, 208), dirt=0.3)
    rubber = Material("rubber", color=(28, 28, 30), dirt=0.45)
    glass = Material("glossy", color=(26, 38, 48), metal=0.2, rough=0.12)
    hazard = Material("hazard", color=(255, 200, 30), color2=(24, 24, 28), width=0.25, angle=45)
    concrete = Material("concrete", color=(140, 138, 132), dirt=0.6)

    a.add("Body", sh.rounded_box((18.0, 5.0, 17.0), 1.0, 1, yellow).transformed(T(0, 6.6, 0)))
    a.add("Body", sh.box((18.4, 1.2, 17.4), hazard).transformed(T(0, 4.6, 0)))
    a.add("Body", sh.rounded_box((14.0, 2.6, 13.0), 0.6, 1, dark).transformed(T(0, 3.6, 0)))
    for sx in (-1, 1):
        for sz in (-1, 1):
            center = (sx * 9.8, 4.6, sz * 5.6)
            a.add("Body", sh.torus(3.7, 1.6, rubber, 14, 7).transformed(compose(T(*center), R(0, 0, 90))))
            a.add("Body", sh.cylinder(2.4, 2.4, steel, bevel=0.15, segments=10).transformed(compose(T(*center), R(0, 0, 90))))
            a.add("Body", sh.cylinder(0.9, 2.8, chrome, segments=8).transformed(compose(T(*center), R(0, 0, 90))))
    a.add("Body", sh.rounded_box((16.0, 2.2, 1.2), 0.4, 1, steel).transformed(T(0, 5.4, -9.1)))
    for k in range(6):
        a.add("Core", sh.box((1.6, 2.4, 0.3), None).transformed(T(-5.0 + k * 2.0, 7.0, -8.7)))
    a.add("Body", sh.box((13.0, 3.6, 0.6), dark).transformed(T(0, 7.0, -8.55)))

    a.add("Body", sh.rounded_box((8.0, 7.0, 7.4), 0.8, 1, yellow).transformed(T(-4.6, 12.5, -3.4)))
    a.add("Body", sh.box((7.0, 3.2, 0.3), glass).transformed(T(-4.6, 13.6, -7.15)))
    for side in (-1, 1):
        a.add("Body", sh.box((0.3, 3.2, 5.6), glass).transformed(T(-4.6 + side * 4.05, 13.6, -3.6)))
    a.add("Body", sh.rounded_box((8.6, 0.8, 8.0), 0.3, 1, dark).transformed(T(-4.6, 16.3, -3.4)))
    for x in (-7.2, -2.0):
        a.add("Eyes", sh.cylinder(0.7, 1.2, None, segments=10).transformed(T(x, 17.3, -6.4)))
        a.add("Body", sh.cylinder(0.85, 0.4, steel, segments=10).transformed(T(x, 16.8, -6.4)))
    for side in (-1, 1):
        a.add("Body", sh.cylinder(0.9, 9.0, dark, segments=8).transformed(T(side * 3.0 - 4.0, 13.0, 7.4)))
        a.add("Body", sh.cylinder(1.1, 0.8, steel, segments=8).transformed(T(side * 3.0 - 4.0, 17.7, 7.4)))
    for k in range(3):
        a.add("Body", sh.rounded_box((3.4, 3.0, 3.4), 0.5, 1, concrete).transformed(compose(T(2.0 + k * 3.2, 10.6, 6.2), R(0, k * 17, k * 6))))

    a.add("ArmR", sh.cylinder(3.4, 2.0, steel, bevel=0.2, segments=14).transformed(T(4.2, 10.0, 1.0)))
    a.add("ArmR", sh.rounded_box((3.6, 4.0, 4.0), 0.6, 1, yellow).transformed(T(4.2, 12.6, 1.0)))
    boom1 = [(4.2, 13.0, 1.0), (4.2, 21.0, -3.0), (4.2, 26.0, -7.0)]
    a.add("ArmR", sh.sweep(boom1, 1.5, 6, yellow, samples=6))
    boom2 = [(4.2, 26.0, -7.0), (4.2, 24.0, -11.0), (4.2, 19.5, -14.5)]
    a.add("ArmR", sh.sweep(boom2, 1.2, 6, yellow, samples=6))
    a.add("ArmR", sh.sphere(1.9, steel, 8, 5).transformed(T(4.2, 26.0, -7.0)))
    piston(a, "ArmR", (5.8, 13.0, -0.4), (5.8, 21.6, -4.6), 0.55, 0.32, dark, chrome)
    piston(a, "ArmR", (2.6, 13.0, -0.4), (2.6, 21.6, -4.6), 0.55, 0.32, dark, chrome)
    a.add("ArmR", sh.rounded_box((5.4, 4.0, 5.4), 0.6, 1, steel).transformed(T(4.2, 18.0, -14.8)))
    a.add("ArmR", sh.cylinder(2.4, 7.0, dark, bevel=0.2, segments=12).transformed(T(4.2, 13.4, -14.8)))
    a.add("ArmR", sh.cylinder(2.8, 1.2, hazard, bevel=0.1, segments=12).transformed(T(4.2, 15.6, -14.8)))
    a.add("ArmR", sh.cylinder(3.2, 1.6, steel, bevel=0.25, segments=12).transformed(T(4.2, 9.6, -14.8)))

    a.add("ArmL", sh.rounded_box((3.0, 3.0, 4.0), 0.5, 1, yellow).transformed(T(-7.4, 8.6, -9.4)))
    a.add("ArmL", sh.sweep([(-7.4, 8.6, -10.0), (-8.4, 9.4, -13.0), (-8.8, 8.4, -15.6)], 1.0, 6, steel, samples=5))
    for side in (-1, 1):
        jaw = [(-8.8, 8.4, -15.6), (-8.8 + side * 2.4, 9.4, -17.4), (-8.8 + side * 2.6, 7.6, -20.2), (-8.8 + side * 1.0, 6.4, -21.4)]
        a.add("ArmL", sh.sweep(jaw, 0.7, 6, dark, samples=8, taper=lambda t: 1.0 - 0.5 * t))
    piston(a, "ArmL", (-6.0, 9.6, -8.4), (-7.6, 10.2, -13.4), 0.45, 0.28, dark, chrome)
    return scale_asset(a, 1.35)
