import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _city_lib import window_frame, awning, shrub

CYAN = (34, 225, 255)
WHITE = (240, 240, 244)
INK = (18, 20, 26)
RED = (232, 52, 44)
GLASS = (110, 190, 220)

BUILDING = (19.6, 15.2, 5.5)
BUILDING_Z = 1.2
FACE_Z = BUILDING_Z - BUILDING[2] / 2
WINDOW = (-3.2, 4.0, 11.0, 5.4)
DOOR = (5.6, 3.15, 3.2, 6.1)
UPPER = [(-6.0, 13.2), (0.0, 13.2), (6.0, 13.2)]


def face_decals():
    cx, cy = 0.0, BUILDING[1] / 2

    def at(x, y):
        return (-(x - cx), -(y - cy))

    out = []
    wx, wy, ww, wh = WINDOW
    out.append({"type": "rect", "center": at(wx, wy), "size": (ww, wh), "color": (34, 30, 30), "wear": 0.0})
    for k, y in enumerate((1.9, 3.4, 4.9)):
        out.append({"type": "rect", "center": at(wx, y), "size": (ww - 0.6, 0.08), "color": (120, 110, 100), "wear": 0.0})
        for i in range(14):
            x = wx - ww / 2 + 0.6 + i * 0.72
            col = [(232, 52, 44), (255, 210, 31), (60, 200, 120), (34, 160, 255), (255, 122, 26), (240, 240, 244)][(i + k * 3) % 6]
            out.append({"type": "rect", "center": at(x, y + 0.35), "size": (0.5, 0.6), "radius": 0.05, "color": col, "wear": 0.0})
    out.append({"type": "rect", "center": at(wx, wy + 2.4), "size": (ww, 0.4), "color": (250, 246, 220), "wear": 0.0})
    out.append({"type": "rect", "center": at(-6.6, 2.4), "size": (1.6, 1.4), "color": (230, 220, 200), "wear": 0.0})
    out.append({"type": "text", "text": "SALE", "center": at(-6.6, 2.55), "height": 0.5, "color": RED, "font": "impact", "wear": 0.0})
    dx, dy, dw, dh = DOOR
    out.append({"type": "rect", "center": at(dx, dy), "size": (dw, dh), "color": (30, 28, 30), "wear": 0.0})
    out.append({"type": "rect", "center": at(dx, dy + 1.0), "size": (dw - 0.6, 0.06), "color": (110, 100, 90), "wear": 0.0})
    for x, y in UPPER:
        out.append({"type": "rect", "center": at(x, y), "size": (3.2, 2.4), "color": (40, 44, 58), "wear": 0.0})
        out.append({"type": "rect", "center": at(x - 0.9, y), "size": (1.0, 2.4), "color": (150, 60, 60), "wear": 0.0})
        out.append({"type": "rect", "center": at(x + 0.9, y), "size": (1.0, 2.4), "color": (150, 60, 60), "wear": 0.0})
    for x in np.linspace(-9.0, 9.0, 7):
        out.append({"type": "rect", "center": at(x, 15.0), "size": (0.9, 0.35), "darken": 0.25, "raise": 0.0})
    return out


def build():
    a = Asset("ShopFront", budget=4500, atlas=1024, ao_radius=1.2, edge_width=0.1, preview_radius=11.5,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 16), ("FRONT", 180, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.6)
    a.role("Glow", "neon", color=CYAN)

    brick = Material("city_brick", color=(176, 78, 54), mortar=(196, 188, 174), brick=(1.0, 0.4), gap=0.05, wear=0.3, soot=0.25, dirt=0.35)
    stone = Material("city_stone", color=(200, 194, 180), dirt=0.4)
    metal = Material("metal", color=(30, 32, 38), rough=0.4, polish=0.5, dirt=0.35, scratches=0.3)
    chrome = Material("metal", color=(200, 204, 212), rough=0.2, polish=0.9, dirt=0.2)
    slate = Material("concrete", color=(70, 74, 82), dirt=0.5)

    shell = sh.rounded_box(BUILDING, 0.0, 1, brick, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"-z": brick.but(decals=face_decals())})
    a.add("Body", shell.transformed(T(0, BUILDING[1] / 2, BUILDING_Z)))

    for x in (-9.4, 9.4):
        a.add("Body", sh.rounded_box((1.2, BUILDING[1], 0.8), 0.05, 1, stone, faces=["+x", "-x", "+y", "-z"]).transformed(T(x, BUILDING[1] / 2, FACE_Z - 0.4)))
        a.add("Body", sh.rounded_box((1.5, 0.9, 1.1), 0.05, 1, stone, faces=["+x", "-x", "+y", "-z"]).transformed(T(x, 0.45, FACE_Z - 0.4)))
    cornice = sh.extrude([(0.0, 0.0), (0.25, 0.0), (0.25, 0.25), (0.6, 0.45), (0.6, 0.85), (0.0, 0.85)], 20.4, stone, bevel=0.02, corner_radius=0.0)
    a.add("Body", cornice.transformed(compose(T(0, BUILDING[1] - 0.05, FACE_Z), R(0, 90, 0))))
    a.add("Body", sh.box((20.0, 0.25, 5.8), stone).transformed(T(0, BUILDING[1] + 0.92, BUILDING_Z + 0.1)))
    a.add("Body", sh.rounded_box((19.8, 1.2, 0.6), 0.04, 1, slate, faces=["+x", "-x", "+y", "-z"]).transformed(T(0, 0.6, FACE_Z - 0.3)))

    wx, wy, ww, wh = WINDOW
    a.add("Glass", sh.box((ww, wh, 0.04), None).transformed(T(wx, wy, FACE_Z - 0.12)))
    for x in (wx - ww / 2, wx - ww / 6, wx + ww / 6, wx + ww / 2):
        a.add("Body", sh.box((0.28, wh + 0.2, 0.32), metal).transformed(T(x, wy, FACE_Z - 0.16)))
    a.add("Body", sh.box((ww + 0.5, 0.32, 0.36), metal).transformed(T(wx, wy + wh / 2 + 0.16, FACE_Z - 0.18)))

    dx, dy, dw, dh = DOOR
    a.add("Body", [part.transformed(T(dx, dy, FACE_Z - 0.16)) for part in window_frame(dw + 0.5, dh + 0.3, 0.32, 0.25, metal)])
    a.add("Glass", sh.box((dw, dh, 0.04), None).transformed(T(dx, dy, FACE_Z - 0.1)))
    a.add("Body", sh.box((0.12, 1.6, 0.1), chrome).transformed(T(dx - 1.2, dy, FACE_Z - 0.3)))
    a.add("Body", sh.box((0.1, 0.1, 0.14), chrome).transformed(T(dx - 1.2, dy + 0.7, FACE_Z - 0.22)))
    a.add("Body", sh.box((0.1, 0.1, 0.14), chrome).transformed(T(dx - 1.2, dy - 0.7, FACE_Z - 0.22)))
    open_sign = Material("paint", color=INK, under=(150, 152, 158), wear=0.1, scratches=0.1, rough=0.3, dirt=0.2, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (1.7, 0.62), "radius": 0.12, "outline": 0.05, "color": CYAN, "wear": 0.0},
        {"type": "text", "text": "OPEN", "center": (0.0, 0.02), "height": 0.44, "color": RED, "font": "impact", "wear": 0.0},
    ])
    a.add("Body", sh.rounded_box((1.8, 0.7, 0.05), 0.0, 1, open_sign, faces=["-z", "+x", "-x", "+y", "-y"]).transformed(T(dx + 0.2, dy + 2.0, FACE_Z - 0.15)))

    canvas = Material("canvas", stripes=[CYAN, WHITE], stripe_width=0.9, axis=1, dirt=0.35)
    for part in awning(ww + 0.8, 2.6, 0.95, canvas, valance=0.5):
        a.add("Body", part.transformed(T(wx, wy + wh / 2 + 0.55, FACE_Z - 0.05)))
    for x in (wx - ww / 2 - 0.2, wx + ww / 2 + 0.2):
        a.add("Body", sh.sweep([(x, wy + wh / 2 + 0.1, FACE_Z - 0.1), (x, wy + wh / 2 - 0.25, FACE_Z - 1.3), (x, wy + wh / 2 - 0.35, FACE_Z - 2.55)], 0.04, 4, metal))

    sign_face = Material("paint", color=INK, under=(150, 152, 158), wear=0.15, scratches=0.2, rough=0.35, dirt=0.3, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (13.6, 2.2), "radius": 0.15, "outline": 0.1, "color": CYAN, "wear": 0.1},
        {"type": "text", "text": "MEGA MART", "center": (-0.6, 0.05), "height": 1.55, "color": WHITE, "font": "impact", "wear": 0.1},
        {"type": "circle", "center": (5.3, 0.0), "radius": 0.75, "color": CYAN, "wear": 0.1},
        {"type": "text", "text": "24H", "center": (5.3, 0.04), "height": 0.5, "color": INK, "font": "impact", "wear": 0.1},
    ])
    sign = sh.rounded_box((14.0, 2.6, 0.45), 0.06, 1, metal, faces=["+x", "-x", "+y", "-y", "-z"], face_mats={"-z": sign_face})
    a.add("Body", sign.transformed(T(0, 10.4, FACE_Z - 0.23)))
    for y in (11.82, 8.98):
        a.add("Glow", sh.box((14.2, 0.14, 0.18), None).transformed(T(0, y, FACE_Z - 0.3)))

    for x, y in UPPER:
        a.add("Body", [part.transformed(T(x, y, FACE_Z - 0.12)) for part in window_frame(3.6, 2.8, 0.24, 0.22, stone)])
        a.add("Body", sh.rounded_box((3.9, 0.22, 0.5), 0.03, 1, stone, faces=["+x", "-x", "+y", "-y", "-z"]).transformed(T(x, y - 1.5, FACE_Z - 0.25)))
        a.add("Body", sh.box((3.8, 0.4, 0.3), stone).transformed(T(x, y + 1.55, FACE_Z - 0.15)))
        a.add("Glass", sh.box((3.2, 2.4, 0.03), None).transformed(T(x, y, FACE_Z - 0.06)))

    planter = Material("concrete", color=(150, 150, 146), dirt=0.55)
    leaves = Material("plastic", color=(56, 150, 64), rough=0.7, scuff=0.0, dirt=0.3)
    a.add("Body", sh.rounded_box((2.6, 1.0, 1.2), 0.06, 1, planter, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(-7.4, 0.5, FACE_Z - 1.4)))
    a.add("Body", [part.transformed(T(-7.4, 0.95, FACE_Z - 1.4)) for part in shrub(leaves, 4, 0.7)])

    ac = Material("metal", color=(170, 174, 182), rough=0.4, polish=0.5, dirt=0.5, decals=[
        {"type": "circle", "center": (0.0, 0.0), "radius": 0.5, "color": (40, 42, 48), "outline": 0.05, "wear": 0.2},
        {"type": "circle", "center": (0.0, 0.0), "radius": 0.12, "color": (40, 42, 48), "wear": 0.1},
    ])
    a.add("Body", sh.rounded_box((2.0, 0.9, 1.4), 0.06, 1, ac, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"+y": ac}).transformed(T(5.2, BUILDING[1] + 1.5, BUILDING_Z + 0.6)))
    a.add("Body", sh.cylinder(0.18, 1.2, metal, bevel=0.02, segments=8).transformed(T(-6.0, BUILDING[1] + 1.6, BUILDING_Z + 1.4)))

    destructible(a, "Downtown")
    collider(a, "Hitbox", (20.0, 16.0, 6.2), (0, 8.0, BUILDING_Z - 0.35))
    return a
