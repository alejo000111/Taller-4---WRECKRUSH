from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, eye, metal, painted


def build():
    a = pet_asset("RustyBot", 2000, 2.8)
    a.role("Glow", "neon", color=(255, 196, 40))
    rust = painted((158, 96, 60), wear=0.65)
    plate = Material("diamondplate", color=(120, 122, 128), pitch=0.2, dirt=0.4)
    dark = metal((52, 54, 60))
    rubber = Material("rubber", color=(30, 30, 34), pattern="ribs", freq=16.0)
    a.add("Body", sh.rounded_box((1.6, 1.3, 1.3), 0.2, 2, rust).transformed(T(0, 0.0, 0)))
    a.add("Body", sh.rounded_box((1.3, 0.9, 0.12), 0.06, 1, plate).transformed(T(0, 0.05, -0.68)))
    a.add("Body", sh.cylinder(0.55, 0.8, dark, bevel=0.06, segments=12).transformed(T(0, 0.95, 0)))
    a.add("Body", sh.rounded_box((0.9, 0.3, 0.12), 0.05, 1, dark).transformed(T(0, 1.0, -0.55)))
    a.add("Glow", sh.rounded_box((0.75, 0.16, 0.06), 0.04, 1, None).transformed(T(0, 1.0, -0.62)))
    a.add("Body", sh.cylinder(0.04, 0.6, dark, bevel=0.0, segments=5).transformed(compose(T(0.3, 1.6, 0.1), R(0, 0, -15))))
    a.add("Glow", eye(0.09, None, 6, 4).transformed(T(0.38, 1.9, 0.1)))
    for side in (-1, 1):
        a.add("Body", sh.rounded_box((0.45, 0.5, 1.5), 0.15, 1, rubber).transformed(T(side * 0.7, -0.8, 0)))
        a.add("Body", sh.cylinder(0.2, 0.5, dark, bevel=0.0, segments=8).transformed(compose(T(side * 0.7, -0.8, -0.55), R(0, 0, 90))))
        a.add("Body", sh.cylinder(0.2, 0.5, dark, bevel=0.0, segments=8).transformed(compose(T(side * 0.7, -0.8, 0.55), R(0, 0, 90))))
        a.add("Body", sh.rounded_box((0.25, 0.9, 0.25), 0.08, 1, dark).transformed(compose(T(side * 1.0, -0.05, -0.2), R(25, 0, side * 10))))
        a.add("Body", sh.rounded_box((0.18, 0.35, 0.12), 0.04, 1, plate).transformed(compose(T(side * 1.06, -0.45, -0.6), R(-20, 0, side * 25))))
        a.add("Body", sh.rounded_box((0.18, 0.35, 0.12), 0.04, 1, plate).transformed(compose(T(side * 0.9, -0.45, -0.6), R(-20, 0, side * -25))))
    return a
