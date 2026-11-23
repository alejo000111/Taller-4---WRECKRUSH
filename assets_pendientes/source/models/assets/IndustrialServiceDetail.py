from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel
from _bay_lib import DESIGN
from _landmark_lib import landmark


def build():
    a = building_asset("IndustrialServiceDetail", 900, 11.0, atlas=512)
    pipe = Material("paint", color=(171, 79, 52), under=(110, 90, 80), wear=0.45, scratches=0.4, rough=0.45, dirt=0.5, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (40.0, 0.25), "color": (255, 196, 30), "wear": 0.3},
    ])
    clamp = steel((103, 119, 135), dirt=0.5)
    run = sh.sweep([(-9.0, 0.0, 0.0), (-9.0, 9.8, 0.0), (-8.6, 10.75, 0.0), (-7.8, 11.0, 0.0), (7.8, 11.0, 0.0), (8.6, 10.75, 0.0), (9.0, 9.8, 0.0), (9.0, 0.0, 0.0)], 0.55, 8, pipe, samples=22, caps=False)
    a.add("Body", run)
    for x in (-9.0, 9.0):
        for y in (1.5, 5.5, 9.5):
            a.add("Body", sh.cylinder(0.75, 0.25, clamp, bevel=0.0, segments=10).transformed(T(x, y, 0)))
            a.add("Body", sh.box((0.3, 0.25, 0.9), clamp).transformed(T(x, y, -0.6)))
    for x in (-4.0, 4.0):
        a.add("Body", sh.cylinder(0.75, 0.25, clamp, bevel=0.0, segments=10).transformed(compose(T(x, 11.0, 0), R(0, 0, 90))))
    a.add("Body", sh.cylinder(0.3, 0.6, clamp, bevel=0.0, segments=8).transformed(T(0, 11.7, 0)))
    a.add("Body", sh.cylinder(0.45, 0.2, Material("paint", color=(200, 40, 30), under=(80, 80, 80), wear=0.3, rough=0.4, dirt=0.3, skin=False), bevel=0.0, segments=8).transformed(T(0, 12.05, 0)))
    landmark(a, DESIGN, "IndustrialService_Detail", fit="box")
    return a
