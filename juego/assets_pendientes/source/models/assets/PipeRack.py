from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel
from _landmark_lib import landmark, box_collider

LENGTH = 160.0
SUPPORTS = (-64.0, -24.0, 16.0, 56.0)


def run(a, z, big, small, frame, flange):
    a.add("Body", sh.cylinder(1.0, LENGTH, big, bevel=0.0, segments=12).transformed(compose(T(0, 3.2, z), R(0, 0, 90))))
    a.add("Body", sh.cylinder(0.7, LENGTH, small, bevel=0.0, segments=10).transformed(compose(T(0, 6.0, z), R(0, 0, 90))))
    for x in (-40.0, 0.0, 40.0):
        a.add("Body", sh.cylinder(1.25, 0.5, flange, bevel=0.0, segments=12).transformed(compose(T(x, 3.2, z), R(0, 0, 90))))
        a.add("Body", sh.cylinder(0.9, 0.4, flange, bevel=0.0, segments=10).transformed(compose(T(x + 20.0, 6.0, z), R(0, 0, 90))))
    side = 0.6 if z > 0 else -0.6
    for x in SUPPORTS:
        for dz in (-1.1, 1.1):
            a.add("Body", sh.box((0.45, 7.4, 0.45), frame).transformed(T(x, 3.7, z + side + dz)))
        for y in (2.0, 4.8):
            a.add("Body", sh.box((0.5, 0.4, 2.8), frame).transformed(T(x, y, z + side)))
        a.add("Body", sh.box((1.4, 0.2, 3.2), frame).transformed(T(x, 0.1, z + side)))
        a.add("Body", sh.box((0.6, 0.35, 2.6), frame).transformed(T(x, 7.2, z + side)))


def build():
    a = building_asset("PipeRack", 2600, 90.0, atlas=1024)
    big = Material("paint", color=(180, 92, 44), under=(110, 96, 86), wear=0.4, scratches=0.4, rough=0.45, dirt=0.55, skin=False, decals=[
        *[{"type": "rect", "center": (0.0, x), "size": (8.0, 1.2), "color": (255, 210, 31), "wear": 0.4} for x in (-60.0, -20.0, 20.0, 60.0)],
    ])
    small = Material("metal", color=(120, 124, 132), rough=0.35, polish=0.6, dirt=0.5, scratches=0.3)
    frame = steel((60, 60, 64), dirt=0.6)
    flange = steel((84, 86, 92), dirt=0.5)
    for z in (-95.0, 95.0):
        run(a, z, big, small, frame, flange)
    landmark(a, "Zones/Industrial/Landmarks", "Pipes", fit="box",
             colliders=[box_collider("RunN", (LENGTH, 7.4, 3.0), (0, 3.7, -95.2)), box_collider("RunS", (LENGTH, 7.4, 3.0), (0, 3.7, 95.2))])
    return a
