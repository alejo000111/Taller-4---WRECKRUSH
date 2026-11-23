from wr3d import Material, T
from wr3d import shapes as sh
from _skyline_lib import tower_asset, block, slab, roof_kit, install

W, D = 43.0, 40.0


def build():
    a = tower_asset("OfficeSlab", 900, 125.0)
    strips = Material("facade", style="ribbon", cell=(5.0, 4.0), sill=0.38, mullion=0.12, wall=(215, 217, 225), glass=(44, 60, 82), lit=(250, 236, 200), lit_ratio=0.2, dirt=0.35, streaks=0.4)
    podium = Material("facade", style="curtain", cell=(6.0, 7.0), mullion=0.3, slab=0.1, frame=(70, 72, 80), glass=(34, 44, 58), lit=(255, 220, 170), lit_ratio=0.6, dirt=0.25)
    concrete = Material("city_stone", color=(200, 200, 206), dirt=0.35, streaks=0.4)
    dark = Material("metal", color=(50, 52, 58), rough=0.4, polish=0.4, dirt=0.4)

    a.add("Body", block((W, 14.0, D - 6.0), podium).transformed(T(0, 7.0, 3.0)))
    a.add("Body", slab((W + 1.0, 0.8, D - 5.0), concrete, 14.4))
    a.add("Warm", sh.box((32.0, 6.0, 0.25), None).transformed(T(0, 4.0, -D / 2 + 5.85)))
    a.add("Body", sh.box((W - 2.0, 0.8, 4.0), dark).transformed(T(0, 9.0, -D / 2 + 4.0)))
    for x in (-W / 2 + 3.0, W / 2 - 3.0):
        a.add("Body", sh.box((0.6, 9.0, 0.6), dark).transformed(T(x, 4.5, -D / 2 + 2.3)))
    sw, sd, s0, s1 = 40.0, 30.0, 14.8, 214.0
    a.add("Body", block((sw, s1 - s0, sd), strips).transformed(T(0, (s0 + s1) / 2, 3.0)))
    for x in (-sw / 2 - 0.4, sw / 2 + 0.4):
        a.add("Body", block((1.6, s1 - s0, sd + 0.6), concrete, faces=["+x", "-x", "-z"]).transformed(T(x, (s0 + s1) / 2, 3.0)))
    a.add("Body", slab((sw + 3.0, 2.0, sd + 1.0), concrete, s1 + 1.0))
    a.add("Body", block((12.0, 6.0, 9.0), dark, faces=["+x", "-x", "-z", "+z", "+y"]).transformed(T(-6.0, s1 + 5.0, 6.0)))
    a.add("Glow", sh.box((1.8, 32.0, 6.0), None).transformed(T(-W / 2 + 2.6, 36.0, -D / 2 + 4.0)))
    a.add("Body", sh.box((1.4, 34.0, 7.0), dark).transformed(T(-W / 2 + 1.8, 36.0, -D / 2 + 4.0)))
    roof_kit(a, s1 + 2.0, 20.0, 14.0, dark, 5, mast_h=18.0)
    install(a, ["OfficeSlab"], tint=("BladeFace",))
    return a
