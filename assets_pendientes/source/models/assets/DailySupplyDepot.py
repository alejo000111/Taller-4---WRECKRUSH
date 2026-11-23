import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel, louvre
from _bay_lib import STATIONS, deck, ibeam, canopy
from _landmark_lib import landmark, box_collider


def parcel_mat(seed):
    return Material("paint", color=(186, 150, 98), under=(150, 120, 80), wear=0.2, scratches=0.3, rough=0.85, dirt=0.4, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (0.4, 2.0), "color": (210, 190, 140), "rough": 0.4, "wear": 0.2},
        {"type": "rect", "center": (0.45, 0.45), "size": (0.6, 0.35), "color": (240, 240, 236), "wear": 0.2},
        {"type": "rect", "center": (-0.5, -0.5), "size": (0.5, 0.5), "color": (202, 140, 57) if seed % 2 else (60, 160, 220), "wear": 0.3},
    ])


def build():
    a = building_asset("DailySupplyDepot", 2200, 11.0)
    a.role("Glow", "neon", color=(202, 140, 57))
    wall = panel((32, 40, 54), decals=[
        {"type": "rect", "center": (0.0, 4.4), "size": (15.0, 0.12), "color": (222, 150, 60), "wear": 0.3},
        {"type": "text", "text": "DAILY SUPPLY", "center": (-3.6, -4.3), "height": 0.5, "color": (222, 150, 60), "font": "black", "wear": 0.3},
    ])
    frame = steel((96, 110, 126))
    dark = steel((30, 36, 48))
    shelf = steel((47, 60, 75))
    strap = Material("plastic", color=(28, 34, 44), rough=0.5, dirt=0.3)

    a.add("Body", sh.box((16.0, 0.12, 10.0), deck(16.0, 10.0)).transformed(T(0, 0.35, 0)))
    a.add("Body", sh.rounded_box((16.0, 11.0, 0.5), 0.05, 1, wall, faces=["+z", "+x", "-x", "+y"]).transformed(T(0, 5.9, -3.5)))
    for x in (-7.6, 7.6):
        a.add("Body", ibeam(15.0, frame, 0.6, 0.6).transformed(T(x, 0.0, -3.5)))
        a.add("Body", sh.box((0.25, 0.25, 6.0), frame).transformed(compose(T(x, 12.9, -0.6), R(32, 0, 0))))
    a.add("Body", canopy(17.0, 6.0, 0.4, panel((47, 60, 75))).transformed(T(0, 15.1, -1.0)))
    a.add("Body", sh.box((16.0, 0.8, 0.4), dark).transformed(T(0, 14.65, 1.95)))
    a.add("Glow", sh.box((12.0, 0.12, 0.12), None).transformed(T(0, 14.25, 2.18)))
    a.add("Body", sh.box((3.8, 2.0, 0.2), dark).transformed(T(4.0, 7.3, -3.15)))
    a.add("Body", [p.transformed(T(4.0, 7.3, -2.95)) for p in louvre(3.5, 1.8, 3, dark, frame)])
    for x in (-6.4, -0.9):
        a.add("Body", sh.box((0.3, 7.0, 0.3), frame).transformed(T(x, 3.9, -0.6)))
        a.add("Body", sh.box((0.3, 7.0, 0.3), frame).transformed(T(x, 3.9, -3.0)))
    for y in (1.0, 3.5, 6.0):
        a.add("Body", sh.box((6.0, 0.2, 2.6), shelf).transformed(T(-3.65, y, -1.8)))
    spots = [(-5.0, 1.1), (-2.4, 1.1), (-4.4, 3.6), (-2.0, 3.6), (-3.6, 6.1)]
    for k, (x, y) in enumerate(spots):
        box = sh.rounded_box((1.9, 1.8, 1.9), 0.05, 1, parcel_mat(k), faces=["+x", "-x", "+z", "-z", "+y"])
        a.add("Body", box.transformed(compose(T(x, y + 0.9, -1.8), R(0, (k * 23) % 17 - 8, 0))))
        a.add("Body", sh.box((0.2, 1.84, 1.96), strap).transformed(compose(T(x, y + 0.9, -1.8), R(0, (k * 23) % 17 - 8, 0))))
    landmark(a, STATIONS, "DailySupplyDepot", fit="box", keep=["SignPanel"], tint={"Glow": "AmberMarker"},
             colliders=[box_collider("Wall", (16.0, 11.0, 0.5), (0, 5.9, -3.5)), box_collider("Shelves", (6.0, 7.0, 2.6), (-3.65, 3.9, -1.8))])
    return a
