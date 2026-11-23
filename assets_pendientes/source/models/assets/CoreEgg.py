import numpy as np

from wr3d import Asset, Material, T
from wr3d import shapes as sh
from _egg_common import shell, band, place, egg_point, EGG_H


def build():
    a = Asset("CoreEgg", budget=3600, ao_radius=0.4, edge_width=0.03)
    a.role("Shell", "surface")
    a.role("Band", "surface")
    a.role("Glow", "neon", color=(255, 59, 160))
    a.role("Heat", "neon", color=(255, 122, 26))
    hull = Material("metal", color=(46, 44, 54), rough=0.4, polish=0.55, hammered=0.25, dirt=0.35)
    copper = Material("metal", color=(196, 110, 60), rough=0.32, polish=0.75, dirt=0.3, skin=False)
    dark = Material("metal", color=(30, 30, 36), rough=0.45, polish=0.5, dirt=0.3, skin=False)
    a.add("Shell", shell(hull, 24, 16))
    for theta in range(0, 360, 60):
        path = [egg_point(theta, y, 0.02) for y in np.linspace(-1.45, 1.45, 9)]
        a.add("Glow", sh.sweep(path, 0.045, 4, None, samples=12))
        rib = [egg_point(theta + 30, y, 0.05) for y in np.linspace(-1.7, 1.7, 11)]
        a.add("Band", sh.sweep(rib, 0.07, 5, dark, samples=14))
    for y, lift in ((-1.2, 0.06), (0.0, 0.08), (1.2, 0.06)):
        a.add("Band", band(y - 0.07, y + 0.07, lift, copper, 24))
    for k in range(3):
        a.add("Heat", sh.torus(0.42 - k * 0.1, 0.035, None, segments=16, sides=4).transformed(T(0, EGG_H / 2 + 0.12 + k * 0.16, 0)))
    a.add("Band", sh.cylinder(0.06, 0.62, dark, bevel=0.01, segments=8).transformed(T(0, EGG_H / 2 + 0.24, 0)))
    a.add("Glow", sh.gem(0.14, 0.42, 6, None).transformed(T(0, EGG_H / 2 + 0.56, 0)))
    for theta in (0, 120, 240):
        vent = sh.rounded_box((0.4, 0.08, 0.26), 0.03, 1, copper)
        a.add("Band", place(vent, theta + 30, -0.62, 0.04))
        a.add("Heat", place(sh.box((0.3, 0.03, 0.05), None), theta + 30, -0.55, 0.09))
    return a
