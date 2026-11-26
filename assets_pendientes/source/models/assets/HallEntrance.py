from wr3d import Material, T
from wr3d import shapes as sh
from _hall_lib import HALL, ORANGE, hall_asset, gold, dark_metal, square_pillar
from _landmark_lib import landmark, box_collider


def build():
    a = hall_asset("HallEntrance", 1600, 36.0)
    a.role("Glow", "neon", color=ORANGE)
    steel = dark_metal()
    trim = gold(0.25)
    for x in (-31.0, 31.0):
        a.add("Body", sh.rounded_box((5.2, 1.4, 5.2), 0.1, 1, steel).transformed(T(x, 0.7, 0)))
        a.add("Body", [p.transformed(T(x, 1.4, 0)) for p in square_pillar(4.0, 26.6, steel)])
        a.add("Body", sh.rounded_box((5.0, 1.0, 5.0), 0.1, 1, trim).transformed(T(x, 28.5, 0)))
        for z in (-2.08, 2.08):
            a.add("Glow", sh.box((0.8, 24.0, 0.1), None).transformed(T(x, 14.6, z)))
        a.add("Body", sh.box((3.0, 0.3, 4.2), trim).transformed(T(x, 3.0, 0)))
    for y in (27.9, 40.1):
        a.add("Body", sh.rounded_box((64.0, 0.8, 2.6), 0.1, 1, steel).transformed(T(0, y, 0)))
        for z in (-1.32, 1.32):
            a.add("Glow", sh.box((62.0, 0.2, 0.06), None).transformed(T(0, y, z)))
    for x in (-30.6, 30.6):
        a.add("Body", sh.rounded_box((0.8, 12.2, 2.6), 0.1, 1, steel).transformed(T(x, 34.0, 0)))
        for z in (-1.32, 1.32):
            a.add("Glow", sh.box((0.2, 11.4, 0.06), None).transformed(T(x, 34.0, z)))
    for x in (-33.0, 33.0):
        a.add("Body", sh.box((0.02, 0.02, 4.26), steel).transformed(T(x, 0.01, 0)))
    a.add("Body", sh.box((0.02, 0.02, 0.02), steel).transformed(T(0, 40.49, 0)))
    landmark(a, HALL, "Entrance", fit="none", bounds_all=True, keep=["ArchSign"], tint={"Glow": "ArchSignFrame"},
             colliders=[box_collider("PostL", (4.0, 30.0, 4.0), (-31.0, 15.0, 0)), box_collider("PostR", (4.0, 30.0, 4.0), (31.0, 15.0, 0))])
    return a
