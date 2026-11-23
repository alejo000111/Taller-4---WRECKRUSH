from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel
from _bay_lib import STATIONS
from _landmark_lib import landmark, box_collider

SPIN = -119.58
CENTER = (-0.22, 0.0, 0.53)


def build():
    a = building_asset("DailySupplyCart", 1600, 4.5, atlas=512)
    blue = Material("paint", color=(70, 95, 135), under=(130, 132, 140), wear=0.35, scratches=0.4, rough=0.4, dirt=0.35, skin=False)
    plate = Material("diamondplate", color=(90, 115, 155), pitch=0.3, dirt=0.4)
    crate = Material("paint", color=(235, 195, 130), under=(160, 120, 70), wear=0.35, scratches=0.35, rough=0.55, dirt=0.35, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (1.6, 0.5), "color": (202, 140, 57), "wear": 0.3},
        {"type": "text", "text": "DAILY", "center": (0.0, 0.0), "height": 0.34, "color": (40, 30, 20), "font": "black", "wear": 0.2},
    ])
    strap = Material("plastic", color=(58, 63, 68), rough=0.5, dirt=0.3)
    rubber = Material("rubber", color=(28, 28, 30), pattern="ribs", freq=14.0)
    hub = steel((150, 156, 164))

    parts = []
    parts.append(sh.rounded_box((4.0, 0.4, 6.0), 0.06, 1, plate).transformed(T(0, 0.9, 0)))
    for sx in (-1, 1):
        for sz in (-1, 1):
            parts.append(sh.cylinder(0.4, 0.3, rubber, bevel=0.0, segments=12).transformed(compose(T(sx * 1.45, 0.4, sz * 2.2), R(0, 0, 90))))
            parts.append(sh.cylinder(0.17, 0.4, hub, bevel=0.0, segments=8).transformed(compose(T(sx * 1.45, 0.4, sz * 2.2), R(0, 0, 90))))
            parts.append(sh.box((0.2, 0.4, 0.3), hub).transformed(T(sx * 1.45, 0.7, sz * 2.2)))
        for y in (1.54, 1.97, 2.41):
            parts.append(sh.cylinder(0.12, 5.2, blue, bevel=0.0, segments=6).transformed(compose(T(sx * 1.6, y, 0), R(90, 0, 0))))
        for z in (-2.5, 2.5):
            parts.append(sh.cylinder(0.12, 1.5, blue, bevel=0.0, segments=6).transformed(T(sx * 1.6, 1.85, z)))
    parts.append(sh.rounded_box((2.6, 1.9, 3.6), 0.08, 1, crate).transformed(T(0, 2.05, 0)))
    for y in (1.12, 2.98):
        parts.append(sh.box((2.66, 0.15, 3.66), crate).transformed(T(0, y, 0)))
    for z in (-0.8, 0.8):
        parts.append(sh.box((2.68, 1.94, 0.12), strap).transformed(T(0, 2.06, z)))
        parts.append(sh.box((2.68, 0.08, 0.2), strap).transformed(T(0, 3.03, z)))
    handle = sh.sweep([(-1.6, 1.1, 2.7), (-1.6, 3.6, 3.0), (-1.1, 4.0, 3.05), (1.1, 4.0, 3.05), (1.6, 3.6, 3.0), (1.6, 1.1, 2.7)], 0.13, 6, blue, samples=16, caps=False)
    parts.append(handle)
    parts.append(sh.cylinder(0.18, 2.3, strap, bevel=0.0, segments=8).transformed(compose(T(0, 4.0, 3.05), R(0, 0, 90))))
    loop = sh.sweep([(-1.0, 1.1, -2.9), (-1.0, 1.9, -3.1), (1.0, 1.9, -3.1), (1.0, 1.1, -2.9)], 0.13, 6, blue, samples=10, caps=False)
    parts.append(loop)
    spin = compose(T(*CENTER), R(0, SPIN, 0))
    a.add("Body", [p.transformed(spin) for p in parts])
    landmark(a, STATIONS, "DailySupplyCart", fit="none",
             colliders=[box_collider("Cart", (6.4, 3.4, 6.4), (CENTER[0], 1.7, CENTER[2]))])
    return a
