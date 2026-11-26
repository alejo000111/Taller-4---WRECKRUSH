import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _skyline_lib import tower_asset, block, slab, roof_kit, install

W, D = 40.0, 38.0


def chamfered(w, d, c, height, mat, y0):
    poly = [(-w / 2 + c, -d / 2), (w / 2 - c, -d / 2), (w / 2, -d / 2 + c), (w / 2, d / 2 - c),
            (w / 2 - c, d / 2), (-w / 2 + c, d / 2), (-w / 2, d / 2 - c), (-w / 2, -d / 2 + c)]
    prism = sh.extrude(np.asarray(poly), height, mat, bevel=0.0, corner_radius=0.0, smooth_angle=10)
    return prism.transformed(compose(T(0, y0 + height / 2, 0), R(-90, 0, 0)))


def build():
    a = tower_asset("NightTowerB", 900, 175.0)
    band = Material("facade", style="ribbon", cell=(4.0, 4.2), sill=0.46, mullion=0.1, wall=(58, 62, 74), glass=(30, 38, 58), lit=(255, 206, 140), lit_ratio=0.32, lit_rows=True, wall_metal=0.3, wall_rough=0.45, dirt=0.2)
    podium = Material("facade", style="curtain", cell=(5.0, 6.0), mullion=0.25, slab=0.1, frame=(40, 42, 48), glass=(36, 44, 60), lit=(255, 214, 160), lit_ratio=0.65, dirt=0.2)
    trim = Material("metal", color=(140, 146, 158), rough=0.3, polish=0.6, dirt=0.25)
    dark = Material("metal", color=(40, 42, 50), rough=0.4, polish=0.4, dirt=0.4)

    a.add("Body", block((W, 12.0, D), podium).transformed(T(0, 6.0, 0)))
    a.add("Body", slab((W + 1.0, 1.0, D + 1.0), trim, 12.5))
    a.add("Warm", sh.box((24.0, 7.0, 0.25), None).transformed(T(0, 4.5, -D / 2 - 0.15)))
    a.add("Body", sh.box((W - 4.0, 0.5, 4.0), dark).transformed(T(0, 8.6, -D / 2 - 2.0)))

    a.add("Body", chamfered(35.0, 33.0, 4.0, 168.0, band, 13.0))
    for y in (70.0, 128.0):
        a.add("Body", chamfered(35.8, 33.8, 4.1, 0.8, trim, y))
    a.add("Body", chamfered(37.0, 35.0, 4.4, 1.4, trim, 181.0))
    a.add("Body", chamfered(27.0, 25.0, 3.2, 86.0, band.but(lit_ratio=0.3), 182.4))
    for x in (-10.0, 10.0):
        a.add("Glow", sh.box((0.6, 86.0, 0.6), None).transformed(T(x, 225.4, -12.8)))
    a.add("Body", chamfered(29.0, 27.0, 3.4, 3.0, dark, 268.4))
    a.add("Glow", chamfered(29.6, 27.6, 3.5, 0.5, None, 269.6))
    a.add("Body", chamfered(21.0, 19.0, 2.6, 6.0, dark, 271.4))
    a.add("Glow", chamfered(21.6, 19.6, 2.7, 0.4, None, 276.0))
    a.add("Body", chamfered(13.0, 11.0, 1.8, 4.0, trim, 277.4))
    roof_kit(a, 281.4, 12.0, 10.0, dark, 34, mast_h=34.0)
    install(a, ["NightTower"], pick=(2, 1))
    return a
