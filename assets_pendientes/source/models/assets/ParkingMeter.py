import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

STEEL_BLUE = (62, 74, 92)
YELLOW = (255, 210, 31)
INK = (20, 22, 26)
MINT = (90, 255, 190)
RED = (255, 52, 52)

POLE_TOP = 4.0
HEAD_Y = 4.68
HEAD = (1.12, 1.3, 0.86)


def pole_profile():
    return [(0.0, 0.1), (0.2, 0.1), (0.2, 0.22), (0.15, 0.3), (0.14, POLE_TOP - 0.1), (0.2, POLE_TOP - 0.04), (0.2, POLE_TOP), (0.0, POLE_TOP)]


def head_front():
    return Material("paint", color=STEEL_BLUE, under=(140, 144, 150), wear=0.35, scratches=0.4, rough=0.38, dirt=0.4, skin=False, decals=[
        {"type": "rect", "center": (0.0, -0.06), "size": (0.86, 0.5), "radius": 0.07, "color": (16, 18, 22), "wear": 0.05, "raise": -0.008},
        {"type": "rect", "center": (0.0, -0.06), "size": (0.86, 0.5), "radius": 0.07, "outline": 0.035, "color": (176, 180, 188), "metal": 1.0, "rough": 0.3, "wear": 0.2},
        {"type": "text", "text": "PARKING", "center": (0.0, -0.47), "height": 0.15, "color": (236, 236, 240), "font": "black", "wear": 0.3},
        {"type": "text", "text": "2 HR LIMIT", "center": (-0.12, 0.34), "height": 0.1, "color": YELLOW, "font": "bold", "wear": 0.3},
        {"type": "rect", "center": (0.33, 0.34), "size": (0.08, 0.24), "radius": 0.03, "color": (12, 12, 14), "wear": 0.0, "raise": -0.006},
        {"type": "rect", "center": (0.33, 0.34), "size": (0.16, 0.32), "radius": 0.05, "outline": 0.03, "color": (176, 180, 188), "metal": 1.0, "rough": 0.3, "wear": 0.2},
        {"type": "text", "text": "25¢", "center": (0.3, 0.52), "height": 0.08, "color": (236, 236, 240), "font": "bold", "wear": 0.3},
        {"type": "rivets", "points": [(-0.44, -0.52), (0.44, -0.52), (-0.44, 0.52), (0.44, 0.52)], "radius": 0.03, "color": (150, 152, 158), "height": 0.008},
    ])


def head_side():
    return Material("paint", color=STEEL_BLUE, under=(140, 144, 150), wear=0.35, scratches=0.4, rough=0.38, dirt=0.4, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.1), "size": (0.5, 0.7), "radius": 0.05, "outline": 0.02, "darken": 0.4, "raise": -0.004},
        {"type": "circle", "center": (0.0, -0.36), "radius": 0.06, "color": (150, 152, 158), "metal": 1.0, "wear": 0.2},
        {"type": "circle", "center": (0.0, -0.36), "radius": 0.025, "darken": 0.9, "raise": -0.006},
    ])


def build():
    a = Asset("ParkingMeter", budget=800, atlas=512, ao_radius=0.3, edge_width=0.03, preview_radius=3.3,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=MINT)
    a.role("Flag", "neon", color=RED)

    pole_paint = Material("paint", color=(70, 72, 80), under=(150, 152, 158), wear=0.4, scratches=0.4, rough=0.42, dirt=0.45, skin=False, decals=[
        {"type": "rect", "center": (0.7, 2.85), "size": (1.6, 0.36), "color": YELLOW, "wear": 0.45},
        {"type": "stripes", "center": (0.7, 2.85), "size": (1.6, 0.36), "width": 0.12, "color": INK, "wear": 0.45},
    ])
    plate = Material("diamondplate", color=(110, 114, 122), pitch=0.18, dirt=0.6, decals=[
        {"type": "rivets", "points": [(-0.36, -0.36), (0.36, -0.36), (-0.36, 0.36), (0.36, 0.36)], "radius": 0.06, "color": (150, 152, 158), "height": 0.02},
    ])
    cap = Material("metal", color=(176, 180, 190), rough=0.3, polish=0.8, dirt=0.3, scratches=0.4)
    collar = Material("paint", color=YELLOW, under=(150, 152, 158), wear=0.45, scratches=0.4, rough=0.4, dirt=0.4, skin=False)
    body = Material("paint", color=STEEL_BLUE, under=(140, 144, 150), wear=0.35, scratches=0.4, rough=0.38, dirt=0.4, skin=False)

    a.add("Body", sh.rounded_box((0.95, 0.1, 0.95), 0.0, 1, plate, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 0.05, 0)))
    a.add("Body", sh.lathe(pole_profile(), 10, pole_paint, smooth_angle=40, start=90))
    a.add("Body", sh.lathe([(0.0, 0.0), (0.42, 0.0), (0.38, 0.14), (0.24, 0.2), (0.0, 0.2)], 12, collar, smooth_angle=40).transformed(T(0, POLE_TOP - 0.02, 0)))

    head = sh.rounded_box(HEAD, 0.14, 1, body, face_mats={"-z": head_front(), "+x": head_side(), "-x": head_side()})
    a.add("Body", head.transformed(T(0, HEAD_Y, 0)))
    a.add("Body", sh.rounded_box((1.2, 0.1, 0.94), 0.0, 1, cap, faces=["+x", "-x", "+y", "-y", "+z", "-z"]).transformed(T(0, HEAD_Y + HEAD[1] / 2 + 0.03, 0)))
    dome = sh.lathe([(0.0, 0.0), (0.5, 0.0), (0.5, 0.08), (0.44, 0.3), (0.3, 0.46), (0.0, 0.54)], 12, cap, smooth_angle=50)
    a.add("Body", dome.transformed(T(0, HEAD_Y + HEAD[1] / 2 + 0.08, 0)))
    a.add("Body", sh.sphere(0.07, cap, 6, 3).transformed(T(0, HEAD_Y + HEAD[1] / 2 + 0.66, 0)))
    a.add("Body", sh.rounded_box((0.24, 0.3, 0.12), 0.0, 1, cap, faces=["+x", "-x", "+y", "-y", "-z"]).transformed(T(0.42, HEAD_Y - 0.5, -HEAD[2] / 2 - 0.04)))

    window = (0.0, HEAD_Y + 0.06, -HEAD[2] / 2 - 0.006)
    a.add("Glow", sh.box((0.62, 0.26, 0.02), None).transformed(T(window[0], window[1] - 0.04, window[2])))
    flag = sh.rounded_box((0.46, 0.16, 0.06), 0.0, 1, None, faces=["+x", "-x", "+y", "-y", "-z"])
    a.add("Flag", flag.transformed(compose(T(-0.06, HEAD_Y + HEAD[1] / 2 + 0.33, -0.44), R(0, 0, 8))))

    destructible(a, "Downtown")
    collider(a, "Hitbox", (1.2, 1.9, 1.0), (0, HEAD_Y + 0.25, 0))
    collider(a, "Pole", (0.42, POLE_TOP, 0.42), (0, POLE_TOP / 2, 0), shape="Cylinder")
    return a
