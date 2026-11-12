from wr3d import Material, T
from wr3d import shapes as sh
from _skyline_lib import tower_asset, block, install
from _future_lib import pearl

W, D = 42.0, 38.0


def build():
    a = tower_asset("SpireTower", 1400, 155.0)
    hull = Material("facade", style="ribbon", cell=(4.0, 4.0), sill=0.5, mullion=0.06, wall=(232, 238, 246), glass=(30, 52, 80), lit=(200, 240, 255), lit_ratio=0.18, lit_rows=True, wall_rough=0.3, wall_metal=0.1, dirt=0.12)
    atrium = Material("facade", style="curtain", cell=(5.0, 10.0), mullion=0.2, slab=0.05, frame=(200, 210, 220), glass=(30, 44, 64), lit=(200, 240, 255), lit_ratio=0.5, dirt=0.1)
    deck = Material("facade", style="curtain", cell=(3.0, 6.0), mullion=0.12, slab=0.05, frame=(180, 190, 200), glass=(22, 36, 58), lit=(140, 220, 255), lit_ratio=0.4, dirt=0.1)
    shell = pearl(panel=6.0)
    steel = Material("metal", color=(206, 212, 220), rough=0.25, polish=0.8, dirt=0.15)

    a.add("Body", block((W, 10.0, D), atrium).transformed(T(0, 5.0, 0)))
    a.add("Warm", sh.box((28.0, 8.0, 0.25), None).transformed(T(0, 4.5, -D / 2 - 0.15)))
    a.add("Body", sh.rounded_box((W - 2.0, 120.0, D - 3.0), 3.0, 2, hull, faces=["+x", "-x", "-z", "+z", "+y"]).transformed(T(0, 70.0, 0)))
    a.add("Body", block((W - 4.0, 6.0, D - 5.0), deck).transformed(T(0, 133.0, 0)))
    a.add("Glow", sh.rounded_box((W - 2.6, 0.7, D - 3.6), 0.3, 1, None, faces=["+x", "-x", "-z", "+z"]).transformed(T(0, 136.4, 0)))
    a.add("Body", sh.rounded_box((W - 7.0, 96.0, D - 8.0), 2.6, 2, hull.but(lit_ratio=0.24), faces=["+x", "-x", "-z", "+z", "+y"]).transformed(T(0, 184.8, 0)))
    blade = sh.extrude([(-(W - 7.0) / 2, 0.0), ((W - 7.0) / 2, 0.0), ((W - 7.0) / 2, 4.0), (-(W - 7.0) / 2, 16.0)], D - 8.0, deck, bevel=0.0, corner_radius=0.0)
    a.add("Body", blade.transformed(T(0, 232.8, 0)))
    for x in (-W / 2 + 0.6, W / 2 - 0.6):
        a.add("Glow", sh.box((0.6, 120.0, 0.6), None).transformed(T(x, 70.0, -D / 2 + 1.2)))
    a.add("Body", sh.lathe([(0.0, 0.0), (2.4, 0.0), (2.0, 2.0), (0.0, 2.4)], 8, shell, smooth_angle=30).transformed(T(10.0, 246.0, 0)))
    a.add("Body", sh.cylinder(0.7, 38.0, steel, bevel=0.0, segments=6).transformed(T(10.0, 267.0, 0)))
    a.add("Beacon", sh.sphere(1.1, None, 6, 4).transformed(T(10.0, 287.0, 0)))
    install(a, ["SpireTower"])
    return a
