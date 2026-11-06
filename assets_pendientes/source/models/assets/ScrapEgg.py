import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _egg_common import shell, band, place, EGG_H, EGG_R, TAPER
from _eggs_lib import EggForm


def build():
    a = Asset("ScrapEgg", budget=3200, ao_radius=0.4, edge_width=0.035)
    a.role("Shell", "surface")
    a.role("Band", "surface")
    a.role("Glow", "neon", color=(255, 150, 40))
    form = EggForm(EGG_H, EGG_R, TAPER)
    plates = Material("egg_scrap_plates", color=(255, 122, 26), scrap=(128, 130, 138), wear=0.35, dirt=0.3)
    patch = Material("metal", color=(146, 148, 156), hammered=0.4, rough=0.4, dirt=0.4, skin=False, decals=[
        {"type": "rivets", "points": [(-0.28, -0.2), (0.28, -0.2), (-0.28, 0.2), (0.28, 0.2)], "radius": 0.045, "color": (150, 150, 156), "height": 0.014},
    ])
    rivets = [(u, 0.27) for u in np.linspace(0.25, 9.6, 14)]
    metal = Material("metal", color=(110, 112, 120), rough=0.38, polish=0.7, dirt=0.35, skin=False, decals=[
        {"type": "rivets", "points": rivets, "radius": 0.05, "height": 0.014},
    ])
    dark = Material("metal", color=(70, 72, 80), rough=0.4, polish=0.6, dirt=0.3, skin=False)
    a.add("Shell", shell(plates, 24, 16))
    a.add("Band", band(-0.32, 0.2, 0.07, metal, 24))
    for theta, y, size, spin in ((60, 0.9, (0.8, 0.62), 8), (200, 0.75, (0.7, 0.55), -6), (320, -0.95, (0.75, 0.6), 4), (120, -1.0, (0.62, 0.5), -10)):
        plate = sh.rounded_box((size[0], size[1], 0.06), 0.02, 1, patch)
        a.add("Band", form.wrap(plate.transformed(R(0, 0, spin)), theta, form.s_of_y(y), 0.03))
    a.add("Band", sh.prism(6, 0.24, 0.16, dark, bevel=0.02).transformed(T(0, EGG_H / 2 + 0.02, 0)))
    pipe = sh.lathe([(0.0, 0.0), (0.1, 0.0), (0.1, 0.32), (0.13, 0.34), (0.13, 0.42), (0.08, 0.42), (0.08, 0.36), (0.0, 0.36)], 10, dark, smooth_angle=35)
    a.add("Band", place(pipe, 140, 1.05, -0.04))
    antenna = [(0.0, EGG_H / 2 + 0.08, 0.0), (0.05, EGG_H / 2 + 0.3, 0.02), (0.02, EGG_H / 2 + 0.55, 0.06)]
    a.add("Band", sh.sweep(antenna, 0.025, 5, dark, samples=6))
    a.add("Glow", sh.sphere(0.07, None, 10, 6).transformed(T(0.02, EGG_H / 2 + 0.6, 0.06)))
    return a
