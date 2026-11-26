import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, eye, metal, painted


def build():
    a = pet_asset("WreckKing", 4200, 3.2)
    a.role("Visor", "neon", color=(200, 20, 28))
    a.role("Gold", "neon", color=(255, 196, 40))
    a.role("Flame", "neon", color=(255, 40, 40))
    armor = metal((23, 21, 29), polish=0.8, rough=0.25)
    plate = metal((52, 50, 60))
    gold = Material("gold", color=(255, 196, 40), rough=0.2, dirt=0.05)
    cape = Material("canvas", stripes=[(190, 20, 28), (172, 16, 24)], stripe_width=0.12, axis=1, dirt=0.15)
    a.add("Body", sh.rounded_box((1.8, 1.4, 1.5), 0.35, 2, armor))
    a.add("Body", sh.rounded_box((1.5, 0.5, 0.1), 0.12, 1, plate).transformed(T(0, 0.12, -0.74)))
    a.add("Visor", sh.rounded_box((1.4, 0.4, 0.06), 0.1, 1, None).transformed(T(0, 0.12, -0.79)))
    for side in (-1, 1):
        a.add("Gold", eye(0.13).transformed(T(side * 0.33, 0.12, -0.83)))
    a.add("Body", sh.rounded_box((1.88, 0.14, 1.58), 0.05, 1, gold).transformed(T(0, -0.55, 0)))
    a.add("Body", sh.rounded_box((1.2, 0.6, 1.0), 0.2, 1, plate).transformed(T(0, -0.95, 0)))
    a.add("Body", sh.box((0.5, 0.36, 0.06), gold).transformed(T(0, -0.95, -0.52)))
    a.add("Body", sh.lathe([(0.0, 0.0), (0.45, 0.0), (0.42, -0.35), (0.3, -0.45), (0.0, -0.45)], 10, plate, smooth_angle=40).transformed(T(0, -1.25, 0)))
    a.add("Flame", sh.lathe([(0.0, 0.0), (0.32, 0.0), (0.15, -0.35), (0.0, -0.55)], 8, None, smooth_angle=50).transformed(T(0, -1.7, 0)))
    for side in (-1, 1):
        a.add("Body", eye(0.29, gold).transformed(T(side * 1.15, -0.45, -0.1)))
        a.add("Body", sh.rounded_box((0.3, 0.55, 0.4), 0.1, 1, armor).transformed(T(side * 1.0, -0.05, -0.05)))
    a.add("Body", sh.cylinder(0.07, 1.3, plate, bevel=0.0, segments=6).transformed(T(1.15, 0.15, -0.1)))
    a.add("Body", sh.rounded_box((0.48, 0.48, 0.85), 0.06, 1, armor).transformed(T(1.15, 0.8, -0.1)))
    a.add("Body", sh.box((0.52, 0.52, 0.12), gold).transformed(T(1.15, 0.8, -0.1)))
    a.add("Flame", sh.cylinder(0.18, 0.04, None, bevel=0.0, segments=10).transformed(compose(T(1.15, 0.8, -0.54), R(90, 0, 0))))
    a.add("Body", sh.lathe([(0.62, -0.13), (0.66, -0.13), (0.66, 0.13), (0.62, 0.13)], 16, gold, closed=True, smooth_angle=40).transformed(T(0, 0.83, 0)))
    for k in range(5):
        ang = np.radians(k * 72 - 90)
        spike = sh.lathe([(0.0, 0.0), (0.14, 0.0), (0.0, 0.42)], 4, gold, smooth_angle=10)
        a.add("Body", spike.transformed(T(np.cos(ang) * 0.6, 0.94, np.sin(ang) * 0.6)))
    a.add("Visor", eye(0.13).transformed(T(0, 0.86, -0.66)))
    capemesh = sh.rounded_box((1.6, 1.5, 0.08), 0.03, 1, cape)
    capemesh.pos[:, 2] += 0.12 * np.sin(capemesh.pos[:, 0] * 3.0) * (0.5 - capemesh.pos[:, 1] / 1.5)
    a.add("Body", sh.recompute_normals(capemesh).transformed(compose(T(0, -0.45, 0.86), R(-12, 0, 0))))
    a.add("Body", sh.box((1.62, 0.12, 0.1), gold).transformed(compose(T(0, -1.17, 1.01), R(-12, 0, 0))))
    return a
