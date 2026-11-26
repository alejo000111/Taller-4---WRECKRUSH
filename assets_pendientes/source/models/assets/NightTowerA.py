from wr3d import Material, T
from wr3d import shapes as sh
from _skyline_lib import tower_asset, block, slab, glow_ring, roof_kit, install

W, D = 40.0, 38.0


def build():
    a = tower_asset("NightTowerA", 900, 175.0)
    stone = Material("city_stone", color=(206, 202, 194), dirt=0.35, streaks=0.4)
    podium = Material("facade", style="ribbon", cell=(6.0, 7.0), sill=0.3, wall=(206, 202, 194), glass=(30, 40, 56), lit=(255, 214, 160), lit_ratio=0.7, dirt=0.3)
    shaft = Material("facade", style="punched", cell=(3.6, 4.0), margin=(0.16, 0.18, 0.3), wall=(176, 186, 210), glass=(36, 48, 72), lit_ratio=0.28, dirt=0.3, streaks=0.3)
    upper = shaft.but(lit_ratio=0.36)
    dark = Material("metal", color=(54, 56, 64), rough=0.4, polish=0.4, dirt=0.4)

    a.add("Body", block((W, 14.0, D), podium).transformed(T(0, 7.0, 0)))
    a.add("Body", slab((W + 1.2, 0.8, D + 1.2), stone, 14.4))
    a.add("Warm", sh.box((26.0, 8.0, 0.25), None).transformed(T(0, 5.0, -D / 2 - 0.15)))
    a.add("Body", sh.box((30.0, 0.6, 3.0), dark).transformed(T(0, 9.6, -D / 2 - 1.5)))

    sw, sd, s0, s1 = 34.0, 32.0, 14.8, 190.0
    a.add("Body", block((sw, s1 - s0, sd), shaft).transformed(T(0, (s0 + s1) / 2, 0)))
    for x in (-sw / 2, sw / 2):
        for z in (-sd / 2, sd / 2):
            a.add("Body", block((1.8, s1 - s0, 1.8), stone, faces=["+x", "-x", "-z", "+z"]).transformed(T(x, (s0 + s1) / 2, z)))
    for y in (60.0, 102.0, 146.0):
        a.add("Body", slab((sw + 0.8, 0.7, sd + 0.8), stone, y))
    a.add("Body", slab((37.0, 1.4, 35.0), stone, 190.7))

    uw, ud, u0, u1 = 26.0, 24.0, 191.4, 270.0
    a.add("Body", block((uw, u1 - u0, ud), upper).transformed(T(0, (u0 + u1) / 2, 0)))
    for x in (-uw / 2 - 0.6, uw / 2 + 0.6):
        a.add("Body", block((1.2, u1 - u0 + 4.0, 3.2), stone, faces=["+x", "-x", "-z", "+z", "+y"]).transformed(T(x, (u0 + u1 + 4.0) / 2, -ud / 2 + 1.6)))
    a.add("Body", block((28.0, 4.0, 26.0), dark, faces=["+x", "-x", "-z", "+z", "+y", "-y"]).transformed(T(0, 272.0, 0)))
    a.add("Glow", glow_ring(28.0, 26.0, 271.2, thick=0.6, out=0.3))
    a.add("Body", block((20.0, 3.0, 18.0), dark, faces=["+x", "-x", "-z", "+z", "+y"]).transformed(T(0, 275.5, 1.0)))
    roof_kit(a, 277.0, 20.0, 18.0, dark, 21, mast_h=38.0)
    install(a, ["NightTower"], pick=(2, 0))
    return a
