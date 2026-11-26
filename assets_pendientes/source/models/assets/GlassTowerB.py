from wr3d import Material, T
from wr3d import shapes as sh
from _skyline_lib import tower_asset, block, slab, roof_kit, install
from NightTowerB import chamfered

W, D = 41.0, 35.0


def build():
    a = tower_asset("GlassTowerB", 900, 160.0)
    curtain = Material("facade", style="curtain", cell=(3.6, 4.0), mullion=0.14, slab=0.2, frame=(150, 166, 176), glass=(52, 120, 132), lit=(230, 250, 240), lit_ratio=0.12, glass_metal=0.6, dirt=0.12)
    podium = Material("facade", style="ribbon", cell=(6.0, 7.0), sill=0.25, wall=(190, 194, 200), glass=(36, 50, 60), lit=(255, 220, 170), lit_ratio=0.7, dirt=0.25)
    trim = Material("metal", color=(170, 180, 190), rough=0.28, polish=0.7, dirt=0.2)
    dark = Material("metal", color=(48, 52, 60), rough=0.4, polish=0.4, dirt=0.4)

    a.add("Body", block((W, 13.0, D), podium).transformed(T(0, 6.5, 0)))
    a.add("Body", slab((W + 1.0, 0.8, D + 1.0), trim, 13.4))
    a.add("Warm", sh.box((26.0, 8.0, 0.25), None).transformed(T(0, 5.0, -D / 2 - 0.15)))
    a.add("Body", chamfered(35.0, 29.0, 5.0, 160.0, curtain, 13.8))
    for y in (66.0, 120.0):
        a.add("Body", chamfered(35.6, 29.6, 5.1, 0.6, trim, y))
    a.add("Body", chamfered(36.4, 30.4, 5.3, 1.4, trim, 173.8))
    a.add("Body", chamfered(27.0, 21.0, 4.0, 82.0, curtain.but(lit_ratio=0.16), 175.2))
    a.add("Glow", chamfered(27.6, 21.6, 4.1, 0.6, None, 230.0))
    a.add("Glow", chamfered(27.6, 21.6, 4.1, 0.6, None, 256.4))
    a.add("Body", chamfered(28.0, 22.0, 4.2, 2.4, dark, 257.2))
    a.add("Body", chamfered(16.0, 12.0, 2.6, 8.0, curtain.but(lit_ratio=0.0), 259.6))
    a.add("Body", chamfered(16.6, 12.6, 2.7, 0.6, trim, 267.6))
    roof_kit(a, 268.2, 12.0, 9.0, dark, 7, mast_h=26.0)
    install(a, ["GlassTower"], pick=(2, 1))
    return a
