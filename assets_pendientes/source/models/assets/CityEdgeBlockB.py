import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel, louvre, IMMERSION
from _landmark_lib import landmark, box_collider
from CityEdgeBlockA import shop_front

W, D, H = 66.0, 14.0, 20.5
ROOF = 21.55


def build():
    a = building_asset("CityEdgeBlockB", 2000, 38.0)
    bands = Material("facade", style="ribbon", cell=(4.5, 5.5), sill=0.45, mullion=0.1, wall=(176, 180, 186), glass=(40, 56, 74), lit=(250, 236, 200), lit_ratio=0.22, dirt=0.4, streaks=0.5)
    side = bands.but(lit_ratio=0.1, cell=(6.0, 5.5))
    concrete = Material("city_stone", color=(150, 154, 160), dirt=0.5, streaks=0.5)
    base = Material("city_stone", color=(64, 66, 72), dirt=0.5)
    roof = Material("concrete", color=(92, 94, 100), dirt=0.5)
    metal = steel()
    door = Material("corrugated", color=(62, 70, 82), under=(110, 110, 116), pitch=0.35, axis=1, wear=0.4, scratches=0.4, rough=0.5, dirt=0.45, skin=False)
    unit = panel((150, 156, 164))

    a.add("Body", sh.rounded_box((67.0, 2.0, 15.0), 0.0, 1, base, faces=["+x", "-x", "+z", "+y"]).transformed(T(0, 1.0, 0)))
    a.add("Body", sh.rounded_box((W, H - 8.0, D), 0.0, 1, bands, faces=["+x", "-x", "+z"], face_mats={"+x": side, "-x": side}).transformed(T(0, 8.0 + (H - 8.0) / 2, 0)))
    a.add("Body", sh.rounded_box((W, 6.0, D), 0.0, 1, concrete, faces=["+x", "-x", "+z"]).transformed(T(0, 5.0, 0)))
    a.add("Body", sh.box((40.0, 5.4, 0.3), shop_front(40.0, (54, 58, 66))).transformed(T(-11.0, 4.9, D / 2 + 0.1)))
    a.add("Body", sh.box((12.0, 7.0, 0.25), door).transformed(T(18.0, 5.5, D / 2 + 0.08)))
    a.add("Body", sh.box((44.0, 0.4, 3.0), metal).transformed(T(-11.0, 8.2, D / 2 + 1.5)))
    for x in (-32.0, 10.0):
        a.add("Body", sh.box((0.3, 0.3, 3.2), metal).transformed(T(x, 8.9, D / 2 + 1.4)).transformed(compose(T(0, 0, 0))))
    for x in np.linspace(-30.0, 30.0, 9):
        a.add("Body", sh.box((0.8, H - 8.0, 0.5), concrete).transformed(T(x, 8.0 + (H - 8.0) / 2, D / 2 + 0.25)))
    a.add("Body", sh.rounded_box((W + 0.6, 0.6, D + 0.6), 0.05, 1, concrete, faces=["+x", "-x", "+z", "+y", "-y"]).transformed(T(0, 8.0, 0)))
    a.add("Body", sh.rounded_box((68.0, 1.1, 16.0), 0.08, 1, concrete, faces=["+x", "-x", "+z", "+y", "-y"]).transformed(T(0, ROOF - 0.55, 0)))
    a.add("Body", sh.box((W - 0.4, 0.2, D - 0.4), roof).transformed(T(0, ROOF + 0.05, 0)))
    a.add("Body", sh.rounded_box((28.0, 7.0, 10.0), 0.0, 1, concrete, faces=["+x", "-x", "+z", "+y"]).transformed(T(-12.0, ROOF + 3.5, -1.0)))
    a.add("Body", [p.transformed(T(-12.0, ROOF + 3.6, 4.15)) for p in louvre(18.0, 4.0, 6, metal, metal)])
    a.add("Body", sh.rounded_box((28.6, 0.5, 10.6), 0.04, 1, metal).transformed(T(-12.0, ROOF + 7.1, -1.0)))
    for k, x in enumerate((12.0, 20.0)):
        a.add("Body", sh.rounded_box((6.0, 2.6, 5.0), 0.12, 1, unit, faces=["+x", "-x", "+z", "-z", "+y"]).transformed(T(x, ROOF + 1.3, 0.5)))
        a.add("Body", sh.cylinder(1.6, 0.4, metal, bevel=0.0, segments=10).transformed(T(x, ROOF + 2.8, 0.5)))
    a.add("Body", sh.box((8.0, 0.4, 7.0), metal).transformed(T(20.0, ROOF + 0.2, -4.0)))
    a.add("Body", sh.cylinder(0.25, 6.0, metal, bevel=0.0, segments=5).transformed(compose(T(16.0, ROOF + 0.6, -4.5), R(0, 0, 90))))
    landmark(a, IMMERSION, ["CityEdgeBlock_1", "CityEdgeBlock_3", "CityEdgeBlock_4", "CityEdgeBlock_6"], fit="box", keep=["SignPanel"],
             colliders=[box_collider("Block", (W, ROOF, D), (0, ROOF / 2, 0)), box_collider("Roof", (28.0, 7.0, 10.0), (-12.0, ROOF + 3.5, -1.0))])
    return a
