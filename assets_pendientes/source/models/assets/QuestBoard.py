import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _station_lib import station, collider, platform, sign_face, steel, painted, YELLOW, INK

CYAN = (34, 225, 255)
BOARD_Z = 0.9
BOARD_Y = 5.4


def notes():
    papers = [(-3.4, -1.4, (236, 226, 190), -4), (-0.9, -1.6, (255, 210, 31), 3), (1.6, -1.3, (236, 226, 190), -2), (3.6, -1.5, (120, 230, 255), 5),
              (-3.0, 1.1, (236, 226, 190), 4), (-0.4, 1.2, (150, 240, 150), -3), (2.1, 1.0, (236, 226, 190), 2)]
    out = []
    for x, y, color, angle in papers:
        out.append({"type": "rect", "center": (x, y), "size": (1.9, 2.1), "color": color, "angle": angle, "wear": 0.15})
        out.append({"type": "rect", "center": (x, y - 0.6), "size": (1.4, 0.18), "color": INK, "angle": angle, "wear": 0.1})
        for k in range(3):
            out.append({"type": "rect", "center": (x - 0.1, y - 0.15 + k * 0.32), "size": (1.2 - 0.25 * k, 0.08), "color": (90, 84, 76), "angle": angle, "wear": 0.1})
        out.append({"type": "circle", "center": (x, y - 0.95), "radius": 0.12, "color": (220, 40, 40), "wear": 0.0})
    out.append({"type": "rect", "center": (3.7, 1.2), "size": (1.2, 1.2), "angle": 10, "color": (230, 60, 60), "wear": 0.2})
    out.append({"type": "text", "text": "!", "center": (3.7, 1.22), "height": 0.9, "color": (255, 255, 255), "font": "black", "wear": 0.1, "angle": 10})
    return Material("wood", color=(96, 64, 40), axis="x", ring_freq=5.0, dirt=0.35, decals=out)


def build():
    a = Asset("QuestBoard", budget=3000, atlas=1024, ao_radius=0.8, edge_width=0.07, preview_radius=7.4,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("FRONT", 180, 6), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=CYAN)
    a.role("Lamp", "neon", color=(255, 220, 140))
    station(a, "QuestBoard")
    platform(a, CYAN)

    timber = Material("wood", color=(110, 72, 44), axis="y", dirt=0.4)
    beam = Material("wood", color=(110, 72, 44), axis="x", dirt=0.4)
    for x in (-5.3, 5.3):
        a.add("Body", sh.rounded_box((0.8, 9.4, 0.8), 0.08, 1, timber, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(x, 4.9, BOARD_Z)))
        a.add("Body", sh.box((1.2, 0.5, 1.2), steel((50, 52, 58))).transformed(T(x, 0.45, BOARD_Z)))
    a.add("Body", sh.rounded_box((10.0, 6.0, 0.4), 0.05, 1, beam, face_mats={"-z": notes()}).transformed(T(0, BOARD_Y, BOARD_Z)))
    for y in (BOARD_Y - 3.15, BOARD_Y + 3.15):
        a.add("Body", sh.box((10.6, 0.35, 0.6), beam).transformed(T(0, y, BOARD_Z - 0.05)))
    for y in (BOARD_Y - 3.35, BOARD_Y + 3.35):
        a.add("Glow", sh.box((10.6, 0.1, 0.1), None).transformed(T(0, y, BOARD_Z - 0.38)))
    header = sh.rounded_box((6.0, 1.3, 0.3), 0.06, 1, steel((30, 32, 40)), face_mats={"-z": sign_face("QUESTS", CYAN, (6.0, 1.3), height=0.85)})
    a.add("Body", header.transformed(T(0, 9.0, BOARD_Z - 0.25)))

    roof = Material("corrugated", color=(46, 70, 84), pitch=0.35, axis=0, depth=0.04, wear=0.3, dirt=0.4, skin=False)
    slope = sh.extrude([(-1.4, 0.0), (1.4, 0.0), (0.0, 0.9)], 12.2, roof, bevel=0.05, corner_radius=0.0)
    a.add("Body", slope.transformed(compose(T(0, 9.75, BOARD_Z), R(0, 90, 0))))

    lantern = steel((40, 42, 48))
    for sx in (-1, 1):
        x = sx * 5.3
        a.add("Body", sh.sweep([(x, 8.6, BOARD_Z - 0.4), (x, 8.6, BOARD_Z - 1.2), (x, 8.3, BOARD_Z - 1.4)], 0.06, 4, lantern, samples=5))
        cage = sh.lathe([(0.0, 0.0), (0.35, 0.0), (0.35, 0.7), (0.2, 0.85), (0.0, 0.9)], 6, lantern, smooth_angle=20)
        a.add("Body", cage.transformed(T(x, 7.4, BOARD_Z - 1.4)))
        a.add("Lamp", sh.cylinder(0.25, 0.55, None, bevel=0.0, segments=6).transformed(T(x, 7.75, BOARD_Z - 1.4)))

    crate = Material("wood", color=(150, 108, 62), axis="x", dirt=0.4, decals=[{"type": "text", "text": "XP", "center": (0.0, 0.0), "height": 0.6, "color": INK, "font": "impact", "wear": 0.4}])
    a.add("Body", sh.rounded_box((1.6, 1.4, 1.4), 0.05, 1, crate).transformed(compose(T(-3.6, 0.9, -2.6), R(0, 12, 0))))
    a.add("Body", sh.rounded_box((1.2, 1.0, 1.2), 0.05, 1, crate).transformed(compose(T(-3.4, 2.1, -2.6), R(0, -8, 0))))

    collider(a, "Board", (11.4, 9.8, 1.2), (0, 4.9, BOARD_Z))
    return a
