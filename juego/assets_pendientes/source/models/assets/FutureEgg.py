import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _egg_common import shell, band, place, egg_radius, EGG_H
import _future_lib


def build():
    a = Asset("FutureEgg", budget=3400, ao_radius=0.4, edge_width=0.03)
    a.role("Shell", "surface")
    a.role("Band", "surface")
    a.role("Glow", "neon", color=(0, 220, 255))
    a.role("Accent", "neon", color=(170, 80, 255))
    pearl = Material("future_panel", color=(232, 236, 244), panel=1.4, gap=0.03, rough=0.2, metal=0.15)
    dark = Material("glossy", color=(24, 28, 44), rough=0.18, metal=0.5)
    a.add("Shell", shell(pearl, 24, 16))
    a.add("Band", band(-0.36, 0.22, 0.07, dark, 24))
    a.add("Glow", band(-0.1, -0.04, 0.09, None, 24))
    for y in (-1.0, 1.0):
        a.add("Accent", band(y - 0.03, y + 0.03, 0.03, None, 24))
    for theta in (0, 120, 240):
        fin = np.array([(0.0, 0.0), (0.42, -0.2), (0.5, -0.75), (0.12, -0.55), (0.0, -0.4)])
        mesh = sh.extrude(fin, 0.06, dark, bevel=0.01, corner_radius=0.0)
        r = egg_radius(-1.2)
        a.add("Band", mesh.transformed(compose(R(0, theta, 0), T(r - 0.08, -1.05, 0))))
        a.add("Glow", sh.box((0.3, 0.035, 0.07), None).transformed(compose(R(0, theta, 0), T(r + 0.2, -1.42, 0))))
    for theta in (45, 165, 285):
        a.add("Accent", place(sh.rounded_box((0.12, 0.04, 0.5), 0.02, 1, None), theta, 0.65, 0.02))
    top = EGG_H / 2
    a.add("Band", sh.lathe([(0.0, 0.0), (0.28, 0.0), (0.22, 0.08), (0.08, 0.14), (0.0, 0.15)], 16, dark).transformed(T(0, top - 0.08, 0)))
    a.add("Glow", sh.torus(0.62, 0.04, None, segments=24, sides=5).transformed(compose(T(0, top + 0.42, 0), R(12, 0, 0))))
    a.add("Accent", sh.gem(0.09, 0.3, 6, None).transformed(T(0, top + 0.16, 0)))
    return a
