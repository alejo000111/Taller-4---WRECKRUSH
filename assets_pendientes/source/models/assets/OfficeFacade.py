import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _city_lib import window_frame

CYAN = (34, 225, 255)
LIT = (200, 244, 255)
INK = (16, 18, 24)
WHITE = (240, 240, 244)
GLASS = (70, 120, 190)

CORE = (24.0, 31.2, 7.0)
CORE_Z = 1.5
FACE_Z = CORE_Z - CORE[2] / 2
FLOOR0 = 7.6
FLOOR_H = 3.3
FLOORS = 7
FINS = [-8.0, -4.0, 0.0, 4.0, 8.0]
LIT_CELLS = [(0, 1), (1, 4), (2, 2), (3, 5), (4, 0), (5, 3), (6, 1), (2, 5), (4, 4)]


def bay_center(i):
    edges = [-11.4] + FINS + [11.4]
    return (edges[i] + edges[i + 1]) / 2, edges[i + 1] - edges[i]


def interior_decals():
    cy = 1.0 + CORE[1] / 2

    def at(x, y):
        return (-x, -(y - cy))

    out = []
    for f in range(FLOORS):
        y0 = FLOOR0 + f * FLOOR_H
        out.append({"type": "rect", "center": at(0.0, y0 + FLOOR_H / 2), "size": (24.0, FLOOR_H), "color": (28, 34, 46), "wear": 0.0})
        out.append({"type": "rect", "center": at(0.0, y0 + FLOOR_H - 0.45), "size": (23.0, 0.12), "color": (220, 232, 240), "wear": 0.0})
        for k in range(10):
            x = -10.8 + k * 2.4 + (0.6 if f % 2 else 0.0)
            out.append({"type": "rect", "center": at(x, y0 + 1.15), "size": (1.6, 0.12), "color": (90, 84, 76), "wear": 0.0})
            out.append({"type": "rect", "center": at(x + 0.2, y0 + 1.5), "size": (0.5, 0.4), "color": (40, 120, 170) if (k + f) % 3 else (60, 64, 74), "wear": 0.0})
            if (k * 7 + f * 3) % 5 == 0:
                out.append({"type": "rect", "center": at(x - 0.5, y0 + 1.6), "size": (0.36, 0.8), "radius": 0.15, "color": (46, 52, 70), "wear": 0.0})
    return out


def lobby_decals():
    return [
        {"type": "rect", "center": (0.0, 0.0), "size": (10.0, 5.4), "color": (36, 40, 50), "wear": 0.0},
        {"type": "rect", "center": (0.0, -2.2), "size": (9.4, 0.14), "color": (230, 236, 240), "wear": 0.0},
        {"type": "rect", "center": (-2.6, 0.9), "size": (3.0, 1.0), "color": (150, 120, 90), "wear": 0.0},
        {"type": "rect", "center": (-2.6, -0.4), "size": (2.4, 0.5), "color": (34, 225, 255), "wear": 0.0},
        {"type": "text", "text": "WRECK CORP", "center": (-2.6, -0.4), "height": 0.32, "color": INK, "font": "impact", "wear": 0.0},
        {"type": "circle", "center": (3.2, 0.6), "radius": 0.6, "color": (50, 140, 70), "wear": 0.0},
    ]


def build():
    a = Asset("OfficeFacade", budget=6000, atlas=1024, ao_radius=1.6, edge_width=0.12, preview_radius=19.0,
              views=[("FRONT 3/4", 215, 10), ("BACK 3/4", 35, 14), ("FRONT", 180, 3), ("TOP", 200, 45)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.5)
    a.role("Glow", "neon", color=LIT)
    a.role("Beacon", "neon", color=(255, 52, 52))

    concrete = Material("city_stone", color=(206, 208, 210), dirt=0.35, streaks=0.35)
    granite = Material("concrete", color=(72, 74, 80), dirt=0.4)
    metal = Material("metal", color=(176, 182, 192), rough=0.3, polish=0.7, dirt=0.3, scratches=0.2)
    dark = Material("metal", color=(36, 40, 48), rough=0.35, polish=0.6, dirt=0.3)

    core = sh.rounded_box(CORE, 0.0, 1, concrete, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"-z": concrete.but(decals=interior_decals())})
    a.add("Body", core.transformed(T(0, 1.0 + CORE[1] / 2, CORE_Z)))
    a.add("Body", sh.rounded_box((26.0, 1.0, 9.6), 0.08, 1, granite, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 0.5, 0.2)))

    for f in range(FLOORS + 1):
        y = FLOOR0 + f * FLOOR_H
        a.add("Body", sh.box((23.0, 0.55, 0.5), concrete).transformed(T(0, y, FACE_Z - 0.25)))
    a.add("Glass", sh.box((22.8, FLOORS * FLOOR_H, 0.05), None).transformed(T(0, FLOOR0 + FLOORS * FLOOR_H / 2, FACE_Z - 0.12)))
    for x in FINS:
        a.add("Body", sh.box((0.45, FLOORS * FLOOR_H + 0.6, 0.9), metal).transformed(T(x, FLOOR0 + FLOORS * FLOOR_H / 2, FACE_Z - 0.45)))
    for f, b in LIT_CELLS:
        cx, width = bay_center(b)
        a.add("Glow", sh.box((width - 0.9, 0.18, 0.04), None).transformed(T(cx, FLOOR0 + f * FLOOR_H + FLOOR_H - 0.45, FACE_Z - 0.06)))

    for x in (-12.2, 12.2):
        a.add("Body", sh.rounded_box((1.6, CORE[1] + 1.0, 1.6), 0.05, 1, concrete, faces=["+x", "-x", "+y", "-z", "+z"]).transformed(T(x, 1.0 + (CORE[1] + 1.0) / 2, FACE_Z + 0.2)))
        a.add("Glass", sh.box((0.05, 22.0, 4.0), None).transformed(T(np.sign(x) * (CORE[0] / 2 + 0.03), 19.0, 2.6)))

    lobby_face = Material("paint", color=(36, 40, 50), under=(120, 120, 120), wear=0.0, scratches=0.0, rough=0.4, skin=False, decals=lobby_decals())
    a.add("Body", sh.rounded_box((10.4, 5.6, 0.1), 0.0, 1, lobby_face, faces=["-z"]).transformed(T(0, 3.8, FACE_Z - 0.9)))
    a.add("Body", [part.transformed(T(0, 3.8, FACE_Z - 1.05)) for part in window_frame(10.8, 5.9, 0.3, 0.3, dark)])
    for x in (-2.5, 2.5):
        a.add("Body", sh.box((0.3, 5.4, 0.3), dark).transformed(T(x, 3.8, FACE_Z - 1.05)))
    a.add("Glass", sh.box((10.2, 5.4, 0.05), None).transformed(T(0, 3.8, FACE_Z - 1.0)))
    for x in (-8.6, 8.6):
        a.add("Body", sh.rounded_box((6.2, 5.9, 1.2), 0.04, 1, granite, faces=["+x", "-x", "+y", "-z"]).transformed(T(x, 3.95, FACE_Z - 0.6)))
    revolving = sh.lathe([(0.0, 0.0), (1.1, 0.0), (1.1, 3.4), (0.0, 3.4)], 12, None, smooth_angle=30)
    a.add("Glass", revolving.transformed(T(0, 1.0, FACE_Z - 1.9)))
    a.add("Body", sh.lathe([(0.0, 0.0), (1.25, 0.0), (1.25, 0.3), (0.0, 0.3)], 12, dark, smooth_angle=30).transformed(T(0, 4.4, FACE_Z - 1.9)))

    canopy_face = Material("metal", color=(36, 40, 48), rough=0.35, polish=0.6, dirt=0.3, decals=[
        {"type": "text", "text": "WRECK CORP", "center": (0.0, 0.02), "height": 0.34, "color": WHITE, "font": "impact", "wear": 0.1},
    ])
    a.add("Body", sh.rounded_box((13.0, 0.5, 2.6), 0.05, 1, dark, faces=["+x", "-x", "+y", "-y", "-z"], face_mats={"-z": canopy_face}).transformed(T(0, 6.95, FACE_Z - 1.3)))
    a.add("Glow", sh.box((13.1, 0.12, 0.08), None).transformed(T(0, 6.75, FACE_Z - 2.62)))
    for x in (-5.8, 5.8):
        a.add("Body", sh.cylinder(0.12, 5.9, metal, bevel=0.0, segments=8).transformed(T(x, 3.95, FACE_Z - 2.35)))

    crown_top = 1.0 + CORE[1]
    a.add("Body", sh.rounded_box((26.0, 1.4, 8.8), 0.06, 1, concrete, faces=["+x", "-x", "+y", "-y", "+z", "-z"]).transformed(T(0, crown_top + 0.7, CORE_Z - 0.2)))
    logo = Material("paint", color=INK, under=(150, 152, 158), wear=0.1, scratches=0.15, rough=0.35, dirt=0.3, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (17.4, 1.4), "radius": 0.12, "outline": 0.08, "color": CYAN, "wear": 0.05},
        {"type": "text", "text": "WRECK CORP", "center": (0.0, 0.05), "height": 1.1, "color": WHITE, "font": "impact", "wear": 0.05},
    ])
    a.add("Body", sh.rounded_box((18.0, 1.8, 0.4), 0.04, 1, dark, faces=["+x", "-x", "+y", "-y", "-z"], face_mats={"-z": logo}).transformed(T(0, crown_top - 0.45, FACE_Z - 0.85)))
    a.add("Body", sh.rounded_box((10.0, 1.6, 5.0), 0.05, 1, concrete, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(-3.0, crown_top + 2.2, CORE_Z + 0.6)))
    vent = Material("metal", color=(150, 154, 162), rough=0.4, polish=0.5, dirt=0.5, decals=[
        *[{"type": "rect", "center": (0.0, y), "size": (2.6, 0.06), "darken": 0.6, "raise": -0.006} for y in np.linspace(-0.5, 0.5, 6)],
    ])
    for x in (5.0, 8.2):
        a.add("Body", sh.rounded_box((2.8, 1.4, 2.2), 0.04, 1, vent, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(x, crown_top + 2.1, CORE_Z + 1.4)))
    a.add("Body", sh.frustum(0.3, 0.08, 1.5, metal, bevel=0.0, segments=8).transformed(T(-3.0, crown_top + 3.75, CORE_Z + 0.6)))
    a.add("Beacon", sh.sphere(0.2, None, 8, 4).transformed(T(-3.0, crown_top + 4.55, CORE_Z + 0.6)))

    destructible(a, "Downtown")
    collider(a, "Hitbox", (24.4, crown_top + 1.4, 7.4), (0, (crown_top + 1.4) / 2, CORE_Z))
    collider(a, "Plinth", (26.0, 1.0, 9.6), (0, 0.5, 0.2))
    collider(a, "Lobby", (21.0, 5.9, 1.4), (0, 3.95, FACE_Z - 0.7))
    return a
