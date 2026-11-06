from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, blob, eye, metal, painted


def build():
    a = pet_asset("TNTPup", 2000, 2.8)
    a.role("Glow", "neon", color=(255, 122, 26))
    shell = painted((60, 62, 70), wear=0.3)
    dynamite = Material("paint", color=(210, 46, 40), under=(120, 30, 30), wear=0.3, rough=0.6, dirt=0.3)
    band = Material("hazard", color=(255, 196, 40), color2=(26, 26, 30), width=0.2, angle=45)
    joint = metal((120, 124, 132))
    fuse = Material("rubber", color=(60, 50, 40), pattern="ribs", freq=30.0)
    a.add("Body", sh.rounded_box((1.0, 0.9, 1.7), 0.25, 2, shell).transformed(T(0, 0, 0.1)))
    a.add("Glow", sh.cylinder(0.25, 0.1, None, bevel=0.0, segments=8).transformed(compose(T(0, 0.0, -0.8), R(90, 0, 0))))
    a.add("Body", blob((0.85, 0.75, 0.9), shell, 8, 6).transformed(T(0, 0.55, -0.95)))
    a.add("Body", sh.rounded_box((0.5, 0.35, 0.5), 0.12, 1, shell).transformed(T(0, 0.42, -1.4)))
    a.add("Body", blob((0.18, 0.14, 0.12), metal((30, 30, 34)), 6, 4).transformed(T(0, 0.48, -1.66)))
    for side in (-1, 1):
        a.add("Glow", eye(0.09, None, 6, 4).transformed(T(side * 0.22, 0.7, -1.33)))
        a.add("Body", sh.rounded_box((0.2, 0.45, 0.12), 0.05, 1, shell).transformed(compose(T(side * 0.32, 1.0, -0.85), R(-10, 0, side * 20))))
        for z in (-0.55, 0.7):
            a.add("Body", sh.sphere(0.16, joint, 6, 4).transformed(T(side * 0.42, -0.4, z)))
            a.add("Body", sh.box((0.2, 0.55, 0.22), shell).transformed(T(side * 0.42, -0.72, z)))
    for k in range(3):
        a.add("Body", sh.cylinder(0.16, 1.1, dynamite, bevel=0.0, segments=8).transformed(compose(T(-0.34 + k * 0.34, 0.62, 0.25), R(90, 0, 0))))
    a.add("Body", sh.cylinder(0.56, 0.18, band, bevel=0.02, segments=10).transformed(compose(T(0, 0.62, 0.25), R(90, 0, 0))))
    a.add("Body", sh.sweep([(0.0, 0.8, 0.8), (0.1, 1.1, 0.95), (0.25, 1.25, 0.85)], 0.035, 5, fuse, samples=6))
    a.add("Glow", eye(0.07, None, 6, 4).transformed(T(0.25, 1.28, 0.85)))
    a.add("Body", sh.sweep([(0.0, 0.2, 0.95), (0.0, 0.5, 1.25), (0.0, 0.7, 1.35)], 0.07, 5, shell, samples=6, taper=lambda t: 1.0 - 0.5 * t))
    return a
