import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import VERDANT, expedition_asset
from _landmark_lib import landmark, box_collider
import _city_lib
import ScrapWall

ZC = -55.25


def build():
    a = expedition_asset("FoundryPair", 2600, 90.0, atlas=1024)
    a.role("Glow", "neon", color=(239, 183, 95))
    shell = Material("corrugated", color=(66, 78, 73), under=(110, 96, 80), pitch=0.6, axis=0, depth=0.06, wear=0.5, scratches=0.4, rough=0.55, dirt=0.6, skin=False)
    rust = Material("scrapwall_sheet", color=(96, 88, 72))
    brick = Material("city_brick", color=(112, 84, 70), mortar=(140, 130, 116), brick=(1.0, 0.42), gap=0.05, wear=0.4, soot=0.6, dirt=0.6)
    steel = Material("metal", color=(70, 74, 72), rough=0.45, polish=0.3, dirt=0.5, scratches=0.4)
    for side in (-1, 1):
        x = side * 105.0
        z = -55.0 - ZC
        a.add("Body", sh.rounded_box((31.0, 22.0, 45.0), 0.0, 1, shell, faces=["+x", "-x", "+z", "-z"]).transformed(T(x, 11.0, z)))
        a.add("Body", sh.box((31.6, 1.4, 45.6), rust).transformed(T(x, 0.7, z)))
        for zz in (-22.5, 22.5):
            for xx in (-15.5, 15.5):
                a.add("Body", sh.box((1.2, 22.4, 1.2), steel).transformed(T(x + xx, 11.2, z + zz)))
        for j in range(3):
            wz = -65.0 + j * 10.0 - ZC
            wx = x - side * 15.6
            a.add("Glow", sh.box((0.3, 6.0, 6.0), None).transformed(T(wx, 14.0, wz)))
            a.add("Body", sh.box((0.5, 7.0, 0.5), steel).transformed(T(wx - side * 0.1, 14.0, wz - 3.25)))
            a.add("Body", sh.box((0.5, 7.0, 0.5), steel).transformed(T(wx - side * 0.1, 14.0, wz + 3.25)))
            a.add("Body", sh.box((0.5, 0.5, 7.0), steel).transformed(T(wx - side * 0.1, 17.5, wz)))
            a.add("Body", sh.box((0.5, 0.5, 7.0), steel).transformed(T(wx - side * 0.1, 10.5, wz)))
        door = Material("corrugated", color=(90, 100, 92), under=(110, 96, 80), pitch=0.4, axis=1, wear=0.5, rough=0.5, dirt=0.5, skin=False)
        a.add("Body", sh.box((0.3, 12.0, 14.0), door).transformed(T(x - side * 15.6, 6.0, z + 14.0)))
        cz = -74.0 - ZC
        a.add("Body", sh.lathe([(0.0, 0.0), (4.6, 0.0), (4.6, 2.0), (4.0, 2.6), (3.6, 44.0), (4.2, 44.6), (4.2, 46.0), (3.2, 46.0), (3.2, 45.0), (0.0, 45.0)], 12, brick, smooth_angle=30))
        a.parts["Body"][-1] = a.parts["Body"][-1].transformed(T(x, 0.0, cz))
        for y in (12.0, 24.0, 36.0):
            a.add("Body", sh.lathe([(3.75, y - 0.3), (4.1, y - 0.3), (4.1, y + 0.3), (3.75, y + 0.3)], 12, steel, closed=True, smooth_angle=30).transformed(T(x, 0.0, cz)))
        mz = -50.0 - ZC
        a.add("Body", sh.cylinder(0.7, 17.0, steel, bevel=0.0, segments=8).transformed(T(x, 24.0 + 8.5, mz)))
        a.add("Body", sh.lathe([(0.0, 0.0), (1.6, 0.0), (1.6, 1.0), (0.0, 1.4)], 8, steel, smooth_angle=40).transformed(T(x, 40.0, mz)))
    landmark(a, VERDANT, "ReclaimedFoundry", fit="box", keep=["WindRotor"],
             colliders=[box_collider("FactoryL", (31.0, 22.0, 45.0), (-105.0, 11.0, -55.0 - ZC)), box_collider("FactoryR", (31.0, 22.0, 45.0), (105.0, 11.0, -55.0 - ZC))])
    return a
