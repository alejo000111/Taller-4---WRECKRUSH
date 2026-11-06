import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _island_boss_lib import island_boss, socket, add_all


def build():
    a = island_boss("ScrapColossus", 6500, (255, 214, 120), (255, 122, 26), ((22.0, 32.0, 14.0), (0.0, 16.0, 0.0)), radius=24.0)
    rust = Material("paint", color=(150, 88, 52), under=(84, 64, 54), wear=0.65, scratches=0.5, rough=0.62, metal=0.3, dirt=0.65)
    teal = Material("paint", color=(64, 112, 118), under=(140, 96, 70), wear=0.55, scratches=0.45, rough=0.5, metal=0.25, dirt=0.55)
    steel = Material("metal", color=(72, 74, 78), rough=0.5, polish=0.3, dirt=0.6, scratches=0.5)
    dark = Material("metal", color=(36, 36, 40), rough=0.6, polish=0.2, dirt=0.6)
    rubber = Material("rubber", color=(30, 30, 33), dirt=0.4)
    chrome = Material("chrome", color=(196, 198, 204), dirt=0.35)
    glass = Material("glossy", color=(28, 40, 46), metal=0.2, rough=0.15)
    hazard = Material("hazard", color=(255, 196, 40), color2=(26, 26, 30), width=0.22, angle=45)

    for side in (-1, 1):
        x = side * 6.5
        a.add("Body", sh.rounded_box((9.0, 3.0, 13.0), 0.8, 1, rust).transformed(T(x, 1.5, -1.5)))
        a.add("Body", sh.box((7.5, 0.6, 1.2), chrome).transformed(T(x, 2.2, -8.2)))
        for k, y in enumerate((4.4, 6.9, 9.4)):
            a.add("Body", sh.torus(2.6, 1.25, rubber, 12, 6).transformed(compose(T(x, y, 0.0), R(0, k * 20, 0))))
        a.add("Body", sh.cylinder(1.6, 8.0, steel, bevel=0.1, segments=8).transformed(T(x, 7.0, 0.0)))
        a.add("Body", sh.sphere(2.3, steel, 10, 6).transformed(T(x, 11.6, 0.0)))
        a.add("Body", sh.rounded_box((5.6, 5.0, 6.2), 0.8, 1, rust).transformed(compose(T(x, 14.0, 0.0), R(0, 0, side * -6))))

    a.add("Body", sh.rounded_box((16.0, 5.0, 10.0), 0.9, 1, steel).transformed(T(0, 17.2, 0.6)))
    for k in range(4):
        a.add("Body", sh.box((3.0, 0.8, 9.4), dark).transformed(T(-4.5 + k * 3.0, 19.9, 0.6)))
    for side in (-1, 1):
        a.add("Body", sh.sweep([(side * 5.5, 18.0, 5.0), (side * 6.2, 24.0, 7.2), (side * 6.6, 33.0, 7.0)], 0.75, 8, dark, samples=6))
        a.add("Body", sh.cylinder(1.05, 1.0, steel, segments=8).transformed(T(side * 6.6, 33.2, 7.0)))

    a.add("Body", sh.rounded_box((20.0, 11.0, 12.0), 2.0, 2, teal).transformed(T(0, 24.6, 0.0)))
    a.add("Body", sh.rounded_box((15.0, 4.0, 0.6), 0.4, 1, glass).transformed(compose(T(0, 28.2, -5.4), R(-18, 0, 0))))
    a.add("Body", sh.rounded_box((21.0, 1.2, 1.4), 0.4, 1, chrome).transformed(T(0, 19.6, -6.2)))
    for k in range(5):
        a.add("Body", sh.box((0.5, 3.0, 0.5), chrome).transformed(T(-4.0 + k * 2.0, 21.6, -6.1)))
    a.add("Body", sh.tube(4.6, 3.4, 1.4, chrome, segments=18).transformed(compose(T(0, 24.6, -6.2), R(90, 0, 0))))
    teeth = 10
    pts = []
    for k in range(teeth * 2):
        ang = 2 * np.pi * k / (teeth * 2)
        r = 3.3 if k % 2 == 0 else 2.6
        pts.append((np.cos(ang) * r, np.sin(ang) * r))
    a.add("Core", sh.extrude(np.asarray(pts), 1.0, None, bevel=0.0, corner_radius=0.0, smooth_angle=20).transformed(T(0, 24.6, -6.4)))
    a.add("Body", sh.box((20.4, 1.0, 12.4), hazard).transformed(T(0, 30.4, 0.0)))

    a.add("Body", sh.rounded_box((8.0, 5.0, 7.0), 1.0, 1, rust).transformed(T(0, 33.4, -0.6)))
    a.add("Body", sh.rounded_box((8.4, 1.0, 7.4), 0.3, 1, dark).transformed(T(0, 35.9, -0.6)))
    for side in (-1, 1):
        a.add("Body", sh.tube(1.3, 0.9, 0.6, chrome, segments=12).transformed(compose(T(side * 2.2, 33.6, -4.1), R(90, 0, 0))))
        a.add("Eyes", sh.cylinder(0.95, 0.4, None, segments=12).transformed(compose(T(side * 2.2, 33.6, -4.2), R(90, 0, 0))))

    for side, role in ((-1, "ArmL"), (1, "ArmR")):
        x = side * 12.6
        a.add(role, sh.torus(3.0, 1.4, rubber, 12, 6).transformed(compose(T(x, 28.0, 0.0), R(0, 0, 90))))
        a.add(role, sh.sphere(1.8, steel, 8, 5).transformed(T(x, 28.0, 0.0)))
        a.add(role, sh.box((3.0, 10.0, 3.0), steel).transformed(compose(T(side * 14.6, 22.0, 0.0), R(0, 0, side * 8))))
        a.add(role, sh.box((3.4, 0.6, 3.4), hazard).transformed(T(side * 15.2, 18.6, 0.0)))
    a.add("ArmL", sh.rounded_box((8.0, 7.0, 10.0), 1.2, 1, teal).transformed(compose(T(-15.6, 13.4, -0.6), R(6, 0, -4))))
    a.add("ArmL", sh.rounded_box((8.6, 2.0, 10.6), 0.6, 1, rust).transformed(compose(T(-15.6, 17.0, -0.6), R(6, 0, -4))))
    a.add("ArmL", sh.box((7.0, 0.6, 1.0), chrome).transformed(T(-15.6, 12.0, -6.0)))
    a.add("ArmR", sh.rounded_box((5.0, 4.0, 5.0), 0.6, 1, steel).transformed(T(15.8, 16.0, 0.0)))
    hook = [(15.8, 14.0, 0.0), (15.8, 10.0, -0.4), (16.4, 7.0, -2.6), (16.0, 6.4, -5.6), (15.6, 8.6, -7.4)]
    a.add("ArmR", sh.sweep(hook, 0.9, 8, dark, samples=10, taper=lambda t: 1.0 - 0.45 * t))

    rng = np.random.default_rng(12)
    for k in range(6):
        yaw = -40 + k * 16 + rng.uniform(-5, 5)
        size = (rng.uniform(3.0, 5.0), rng.uniform(5.0, 8.0), 0.5)
        mat = rust if k % 2 == 0 else teal
        a.add("Body", sh.box(size, mat).transformed(compose(T(rng.uniform(-6, 6), 29.0 + rng.uniform(-2, 2), 6.6), R(-25 + rng.uniform(-10, 10), yaw, rng.uniform(-20, 20)))))

    socket(a, "PlateSocket1", (-5.0, 20.0, -6.9), 0.0)
    socket(a, "PlateSocket2", (5.0, 20.0, -6.9), 0.0)
    socket(a, "PlateSocket3", (-9.6, 15.0, 0.0), 90.0)
    socket(a, "PlateSocket4", (9.6, 15.0, 0.0), -90.0)
    return a
