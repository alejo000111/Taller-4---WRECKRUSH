import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

ORANGE = (255, 140, 30)
CHARCOAL = (40, 42, 48)
YELLOW = (255, 210, 31)
TEAL = (40, 255, 210)
RED = (232, 52, 44)
INK = (20, 20, 24)
WHITE = (236, 236, 240)

HOUSING = (7.0, 4.4, 8.0)
HOUSING_Y = 0.6 + HOUSING[1] / 2
HOUSING_Z = 0.4
FRONT_Z = HOUSING_Z - HOUSING[2] / 2
ROOF_Y = 0.6 + HOUSING[1]


def side_decals(sign):
    def at(z, y):
        return (-(z - HOUSING_Z) if sign > 0 else (z - HOUSING_Z), -(y - HOUSING_Y))

    out = []
    for z0, z1 in ((-3.4, -0.2), (0.4, 3.6)):
        out.append({"type": "rect", "center": at((z0 + z1) / 2, 2.8), "size": (z1 - z0, 3.6), "outline": 0.04, "darken": 0.55, "raise": -0.006})
        out.append({"type": "rect", "center": at(z1 - 0.35, 2.8), "size": (0.14, 0.6), "radius": 0.05, "color": (60, 62, 70), "wear": 0.2, "raise": 0.006})
    out.append({"type": "rect", "center": at(-1.8, 4.1), "size": (1.1, 1.1), "color": YELLOW, "wear": 0.25, "angle": 45})
    out.append({"type": "rect", "center": at(-1.8, 4.1), "size": (1.1, 1.1), "outline": 0.06, "color": INK, "wear": 0.25, "angle": 45})
    out.append({"type": "text", "text": "HV", "center": at(-1.8, 4.12), "height": 0.4, "color": INK, "font": "impact", "wear": 0.2})
    out.append({"type": "text", "text": "WRECK POWER 500kVA", "center": at(2.0, 1.75), "height": 0.3, "color": INK, "font": "impact", "wear": 0.3})
    out.append({"type": "stripes", "center": at(0.4, 1.0), "size": (7.6, 0.3), "width": 0.25, "color": INK, "wear": 0.3})
    return out


def front_decals():
    return [
        {"type": "rect", "center": (0.0, 0.0), "size": (6.6, 4.0), "outline": 0.04, "darken": 0.45, "raise": -0.006},
        {"type": "text", "text": "DANGER  HIGH VOLTAGE", "center": (0.0, -1.75), "height": 0.24, "color": RED, "font": "impact", "wear": 0.2},
        {"type": "stripes", "center": (0.0, 1.85), "size": (6.8, 0.3), "width": 0.25, "color": INK, "wear": 0.3},
    ]


def louvers(width, height, count, mat):
    parts = []
    pitch = height / count
    for k in range(count):
        y = -height / 2 + (k + 0.5) * pitch
        slat = sh.box((width, pitch * 0.9, 0.05), mat)
        parts.append(slat.transformed(compose(T(0, y, 0), R(35, 0, 0))))
    return parts


def build():
    a = Asset("Generator", budget=3000, atlas=1024, ao_radius=0.8, edge_width=0.07, preview_radius=6.6,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=TEAL)

    paint = Material("paint", color=ORANGE, under=(120, 122, 128), wear=0.35, scratches=0.4, rough=0.38, dirt=0.45, skin=False)
    housing = sh.rounded_box(HOUSING, 0.12, 1, paint, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={
        "+x": paint.but(decals=side_decals(1)), "-x": paint.but(decals=side_decals(-1)), "-z": paint.but(decals=front_decals()),
        "+z": paint.but(decals=[{"type": "rect", "center": (0.0, 0.0), "size": (6.4, 3.8), "outline": 0.04, "darken": 0.5, "raise": -0.006}]),
    })
    a.add("Body", housing.transformed(T(0, HOUSING_Y, HOUSING_Z)))

    frame = Material("paint", color=CHARCOAL, under=(110, 112, 118), wear=0.45, scratches=0.4, rough=0.45, dirt=0.6, skin=False, decals=[
        {"type": "rect", "center": (x, 0.0), "size": (1.2, 0.36), "radius": 0.05, "darken": 0.85, "raise": -0.02} for x in (-1.8, 1.8)
    ])
    a.add("Body", sh.rounded_box((7.6, 0.6, 9.6), 0.05, 1, frame, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 0.3, 0)))

    roof_mat = Material("paint", color=CHARCOAL, under=(110, 112, 118), wear=0.4, scratches=0.35, rough=0.45, dirt=0.55, skin=False)
    roof = sh.extrude([(-3.7, 0.0), (3.7, 0.0), (3.7, 0.15), (0.0, 0.55), (-3.7, 0.15)], 8.3, roof_mat, bevel=0.03, corner_radius=0.0)
    a.add("Body", roof.transformed(T(0, ROOF_Y, HOUSING_Z)))
    steel = Material("metal", color=(150, 154, 162), rough=0.35, polish=0.6, dirt=0.5)
    soot = Material("metal", color=(70, 66, 62), rough=0.6, polish=0.2, dirt=0.7, dirt_color=(30, 26, 24))
    a.add("Body", sh.rounded_box((1.8, 0.9, 2.6), 0.08, 1, steel, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(2.0, ROOF_Y + 0.75, 2.0)))
    a.add("Body", sh.cylinder(0.35, 1.8, soot, bevel=0.02, segments=10).transformed(T(2.0, ROOF_Y + 1.9, 3.0)))
    a.add("Body", sh.lathe([(0.0, 0.0), (0.55, 0.0), (0.5, 0.12), (0.0, 0.32)], 10, soot, smooth_angle=40).transformed(T(2.0, ROOF_Y + 2.9, 3.0)))
    for x, z in ((-2.6, -2.6), (2.6, -2.6), (-2.6, 3.4)):
        a.add("Body", sh.torus(0.22, 0.06, steel, segments=8, sides=4).transformed(compose(T(x, ROOF_Y + 0.42, z), R(90, 0, 0))))
    cap = Material("paint", color=RED, under=(150, 152, 158), wear=0.3, scratches=0.3, rough=0.4, dirt=0.3, skin=False)
    a.add("Body", sh.lathe([(0.0, 0.0), (0.36, 0.0), (0.36, 0.16), (0.28, 0.24), (0.0, 0.24)], 10, cap, smooth_angle=40).transformed(T(-2.3, ROOF_Y + 0.3, 2.6)))

    for sx in (-1, 1):
        lv = louvers(2.6, 1.6, 6, roof_mat)
        a.add("Body", [part.transformed(compose(T(sx * (HOUSING[0] / 2 + 0.04), 3.9, 2.0), R(0, 90 * sx, 0))) for part in lv])

    panel_face = Material("paint", color=(30, 32, 38), under=(110, 112, 118), wear=0.2, scratches=0.3, rough=0.4, dirt=0.35, skin=False, decals=[
        {"type": "rect", "center": (-0.9, -0.35), "size": (2.0, 0.95), "radius": 0.06, "color": (10, 12, 14), "wear": 0.0},
        {"type": "circle", "center": (1.05, -0.45), "radius": 0.36, "color": (220, 220, 214), "outline": 0.05, "wear": 0.1},
        {"type": "rect", "center": (1.1, -0.5), "size": (0.3, 0.04), "angle": 35, "color": RED, "wear": 0.0},
        *[{"type": "circle", "center": (x, 0.65), "radius": 0.15, "color": c, "wear": 0.2} for x, c in ((-1.3, RED), (-0.75, (60, 200, 90)), (-0.2, YELLOW))],
        {"type": "text", "text": "MAIN", "center": (1.05, 0.65), "height": 0.16, "color": WHITE, "font": "black", "wear": 0.2},
        {"type": "rivets", "points": [(-1.85, -0.95), (1.85, -0.95), (-1.85, 0.95), (1.85, 0.95)], "radius": 0.05, "color": (150, 152, 158), "height": 0.012},
    ])
    panel = sh.rounded_box((4.0, 2.4, 0.4), 0.05, 1, roof_mat, faces=["+x", "-x", "+y", "-y", "-z"], face_mats={"-z": panel_face})
    a.add("Body", panel.transformed(T(-0.8, 3.2, FRONT_Z - 0.2)))
    a.add("Glow", sh.box((1.8, 0.78, 0.02), None).transformed(T(-0.8 + 0.9, 3.55, FRONT_Z - 0.42)))
    grille = Material("diamondplate", color=(110, 100, 90), pitch=0.22, dirt=0.6)
    a.add("Body", sh.rounded_box((2.2, 3.2, 0.2), 0.03, 1, grille, faces=["+x", "-x", "+y", "-y", "-z"]).transformed(T(2.3, 2.8, FRONT_Z - 0.1)))
    cable = Material("rubber", color=(24, 24, 26), pattern="ribs", freq=14.0, depth=0.004)
    a.add("Body", sh.sweep([(-2.4, 2.4, FRONT_Z - 0.25), (-2.9, 1.4, FRONT_Z - 0.7), (-3.3, 0.7, FRONT_Z - 1.2), (-3.6, 0.65, FRONT_Z - 2.0)], 0.1, 5, cable, samples=10))

    bollard = Material("paint", color=YELLOW, under=(150, 152, 158), wear=0.5, scratches=0.4, rough=0.4, dirt=0.5, skin=False, decals=[
        {"type": "stripes", "center": (0.6, 0.6), "size": (1.3, 0.3), "width": 0.15, "color": INK, "wear": 0.4},
    ])
    for x in (-3.4, 3.4):
        a.add("Body", sh.cylinder(0.2, 1.6, bollard, bevel=0.03, segments=8).transformed(T(x, 0.8, -4.6)))
    a.add("Body", sh.sweep([(-3.4, 1.45, -4.6), (0.0, 1.5, -4.62), (3.4, 1.45, -4.6)], 0.11, 6, bollard, samples=6))

    destructible(a, "Industrial")
    collider(a, "Hitbox", (7.2, ROOF_Y + 0.5, 8.4), (0, (ROOF_Y + 0.5) / 2, HOUSING_Z))
    collider(a, "Guard", (7.2, 1.6, 0.4), (0, 0.8, -4.6))
    return a
