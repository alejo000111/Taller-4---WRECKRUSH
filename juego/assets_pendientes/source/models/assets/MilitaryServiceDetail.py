from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel
from _bay_lib import DESIGN
from _military_lib import olive
from _landmark_lib import landmark


def build():
    a = building_asset("MilitaryServiceDetail", 900, 7.0, atlas=512)
    a.role("Glow", "neon", color=(255, 60, 40))
    body = olive() if callable(olive) else Material("paint", color=(90, 103, 75))
    metal = steel((103, 119, 135))
    dark = steel((25, 32, 44))
    a.add("Body", sh.rounded_box((4.0, 2.0, 1.1), 0.1, 1, body).transformed(T(0, 2.5, 0.0)))
    for x in (-1.2, -0.4):
        a.add("Body", sh.cylinder(0.18, 0.2, dark, bevel=0.0, segments=8).transformed(compose(T(x, 2.7, 0.6), R(90, 0, 0))))
    a.add("Body", sh.box((1.4, 0.6, 0.05), Material("screen", color=(20, 40, 24))).transformed(T(1.0, 2.8, 0.57)))
    a.add("Body", sh.cylinder(0.15, 10.0, metal, bevel=0.0, segments=6).transformed(T(0, 5.0, -0.3)))
    a.add("Body", sh.cylinder(0.12, 9.0, metal, bevel=0.0, segments=6).transformed(compose(T(0, 8.0, -0.3), R(0, 0, 90))))
    for x in (-4.0, 0.0, 4.0):
        a.add("Body", sh.cylinder(0.05, 2.0, dark, bevel=0.0, segments=4).transformed(T(x, 9.0, -0.3)))
        a.add("Body", sh.sphere(0.12, dark, 6, 3).transformed(T(x, 10.0, -0.3)))
    a.add("Glow", sh.sphere(0.18, None, 6, 3).transformed(T(0, 10.05, -0.3)))
    for y in (3.6, 6.4):
        a.add("Body", sh.box((0.5, 0.15, 0.5), dark).transformed(T(0, y, -0.3)))
    landmark(a, DESIGN, "MilitaryService_Detail", fit="box")
    return a
