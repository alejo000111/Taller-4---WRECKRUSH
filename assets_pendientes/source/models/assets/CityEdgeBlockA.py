import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel, IMMERSION
from _landmark_lib import landmark, box_collider

W, D, H = 66.0, 14.0, 28.0
ROOF = 29.05


def shop_front(width, color):
    return Material("facade", style="curtain", cell=(4.0, 7.0), mullion=0.22, slab=0.12, frame=color, glass=(34, 46, 60), lit=(255, 216, 160), lit_ratio=0.55, dirt=0.3)


def water_tank(a, x, z, y0, wood, metal):
    a.add("Body", sh.lathe([(0.0, 0.0), (3.2, 0.0), (3.2, 5.6), (0.0, 5.6)], 10, wood, smooth_angle=40).transformed(T(x, y0 + 3.0, z)))
    a.add("Body", sh.lathe([(0.0, 0.0), (3.5, 0.0), (0.0, 2.2)], 10, metal, smooth_angle=40).transformed(T(x, y0 + 8.6, z)))
    for k in range(4):
        ang = np.radians(45 + k * 90)
        a.add("Body", sh.box((0.35, 3.0, 0.35), metal).transformed(T(x + np.cos(ang) * 2.4, y0 + 1.5, z + np.sin(ang) * 2.4)))
    for y in (1.6, 3.4, 5.2):
        a.add("Body", sh.torus(3.25, 0.06, metal, segments=10, sides=3).transformed(T(x, y0 + 3.0 + y, z)))


def build():
    a = building_asset("CityEdgeBlockA", 2200, 40.0)
    front = Material("facade", style="punched", wall_kind="brick", brick=(1.0, 0.42), cell=(5.5, 6.5), margin=(0.2, 0.16, 0.3), wall=(150, 74, 56), mortar=(176, 166, 152), glass=(36, 48, 64), lit=(255, 212, 150), lit_ratio=0.3, dirt=0.35, streaks=0.35)
    side = front.but(cell=(7.0, 6.5), lit_ratio=0.15)
    stone = Material("city_stone", color=(190, 184, 172), dirt=0.45, streaks=0.4)
    base = Material("city_stone", color=(70, 72, 78), dirt=0.5)
    roof = Material("concrete", color=(96, 98, 104), dirt=0.5)
    metal = steel()
    door = Material("corrugated", color=(70, 78, 90), under=(110, 110, 116), pitch=0.35, axis=1, wear=0.4, scratches=0.4, rough=0.5, dirt=0.45, skin=False)

    a.add("Body", sh.rounded_box((67.0, 2.0, 15.0), 0.0, 1, base, faces=["+x", "-x", "+z", "+y"]).transformed(T(0, 1.0, 0)))
    a.add("Body", sh.rounded_box((W, H - 9.5, D), 0.0, 1, front, faces=["+x", "-x", "+z"], face_mats={"+x": side, "-x": side}).transformed(T(0, 9.5 + (H - 9.5) / 2, 0)))
    a.add("Body", sh.rounded_box((W, 7.5, D), 0.0, 1, stone, faces=["+x", "-x", "+z"]).transformed(T(0, 2.0 + 3.75, 0)))
    a.add("Body", sh.box((38.0, 6.0, 0.3), shop_front(38.0, (40, 44, 52))).transformed(T(-12.0, 5.2, D / 2 + 0.1)))
    a.add("Body", sh.box((12.0, 7.4, 0.25), door).transformed(T(18.0, 5.7, D / 2 + 0.08)))
    a.add("Body", sh.box((13.0, 0.5, 0.5), metal).transformed(T(18.0, 9.6, D / 2 + 0.25)))
    awning = Material("canvas", stripes=[(30, 110, 70), (230, 226, 210)], stripe_width=1.2, dirt=0.35)
    slope = sh.extrude([(0.0, 0.0), (3.2, -1.4), (3.2, -1.5), (0.0, -0.1)], 36.0, awning, bevel=0.0, corner_radius=0.0)
    a.add("Body", slope.transformed(compose(T(-12.0, 10.4, D / 2), R(0, -90, 0))))
    a.add("Body", sh.rounded_box((W + 0.6, 0.6, D + 0.6), 0.05, 1, stone, faces=["+x", "-x", "+z", "+y", "-y"]).transformed(T(0, 9.5, 0)))
    for y in (16.0, 22.5):
        a.add("Body", sh.box((W + 0.3, 0.35, D + 0.3), stone).transformed(T(0, y, 0)))
    a.add("Body", sh.rounded_box((68.0, 1.1, 16.0), 0.08, 1, stone, faces=["+x", "-x", "+z", "+y", "-y"]).transformed(T(0, ROOF - 0.55, 0)))
    for x in np.linspace(-32.0, 32.0, 17):
        a.add("Body", sh.box((0.5, 0.6, 0.6), stone).transformed(T(x, ROOF - 1.4, D / 2 + 0.3)))
    a.add("Body", sh.box((W - 0.4, 0.2, D - 0.4), roof).transformed(T(0, ROOF + 0.05, 0)))
    a.add("Body", sh.rounded_box((28.0, 7.0, 10.0), 0.0, 1, side.but(lit_ratio=0.1, cell=(5.0, 3.5)), faces=["+x", "-x", "+z", "+y"]).transformed(T(-12.0, ROOF + 3.5, -1.0)))
    a.add("Body", sh.rounded_box((28.6, 0.5, 10.6), 0.04, 1, stone).transformed(T(-12.0, ROOF + 7.1, -1.0)))
    water_tank(a, 9.0, -2.0, ROOF, Material("wood", color=(110, 78, 50), dirt=0.5), steel((60, 62, 68)))
    a.add("Body", sh.rounded_box((7.0, 3.0, 6.0), 0.1, 1, panel((120, 128, 140)), faces=["+x", "-x", "+z", "-z", "+y"]).transformed(T(20.0, ROOF + 1.5, 0)))
    a.add("Body", sh.box((8.0, 0.4, 7.0), metal).transformed(T(20.0, ROOF + 3.2, 0)))
    for x in (-10.0, 10.0):
        a.add("Body", sh.box((0.35, 4.6, 0.35), metal).transformed(T(x, ROOF + 2.3, D / 2 + 0.1)))
    a.add("Body", sh.box((21.0, 0.3, 0.3), metal).transformed(T(0, ROOF + 0.9, D / 2 + 0.1)))
    landmark(a, IMMERSION, ["CityEdgeBlock_2", "CityEdgeBlock_5"], fit="box", keep=["SignPanel"],
             colliders=[box_collider("Block", (W, ROOF, D), (0, ROOF / 2, 0)), box_collider("Roof", (28.0, 7.0, 10.0), (-12.0, ROOF + 3.5, -1.0))])
    return a
