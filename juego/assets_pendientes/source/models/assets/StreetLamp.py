import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

IRON = (34, 36, 42)
SILVER = (186, 190, 198)
CYAN = (34, 225, 255)
YELLOW = (255, 210, 31)
WARM = (255, 236, 170)

POLE_Z = 1.2
POLE_TOP = 12.55
HEAD_Z = -1.1
HEAD_Y = 12.3


def base_profile():
    return [(0.0, 0.0), (0.78, 0.0), (0.78, 0.16), (0.66, 0.24), (0.6, 0.62), (0.48, 0.7), (0.4, 1.1), (0.3, 1.22), (0.3, 1.32), (0.22, 1.4), (0.0, 1.4)]


def pole_profile():
    return [(0.0, 1.3), (0.24, 1.3), (0.2, POLE_TOP - 0.2), (0.24, POLE_TOP - 0.12), (0.24, POLE_TOP), (0.0, POLE_TOP)]


def arm_path():
    return [(0.0, POLE_TOP - 0.3, POLE_Z), (0.0, POLE_TOP + 0.2, POLE_Z - 0.6), (0.0, POLE_TOP + 0.5, POLE_Z - 1.4), (0.0, POLE_TOP + 0.53, HEAD_Z + 0.3), (0.0, HEAD_Y + 0.66, HEAD_Z)]


def scroll_path():
    t = np.linspace(0.0, 1.0, 12)
    z = POLE_Z - 0.1 - 1.3 * t
    y = POLE_TOP - 1.15 + 1.05 * t ** 0.7
    curl = np.exp(-((t - 0.85) ** 2) / 0.01) * 0.12
    return np.stack([np.zeros_like(t), y - curl, z], 1)


def shade_profile():
    return [(0.0, 0.0), (0.26, 0.0), (0.56, 0.08), (0.62, 0.14), (0.42, 0.42), (0.18, 0.56), (0.08, 0.66), (0.0, 0.7)]


def banner_face(sign):
    return Material("canvas", stripes=[CYAN], stripe_width=1.0, axis=0, dirt=0.3, decals=[
        {"type": "rect", "center": (0.0, 0.62), "size": (1.2, 0.26), "color": YELLOW, "wear": 0.2},
        {"type": "rect", "center": (0.0, -0.95), "size": (1.2, 0.08), "color": YELLOW, "wear": 0.2},
        {"type": "text", "text": "DOWN", "center": (0.0, -0.45), "height": 0.32, "color": (16, 22, 40), "font": "impact", "wear": 0.15},
        {"type": "text", "text": "TOWN", "center": (0.0, -0.08), "height": 0.32, "color": (16, 22, 40), "font": "impact", "wear": 0.15},
        {"type": "text", "text": "ZONE 2", "center": (0.0, 0.62), "height": 0.16, "color": (16, 22, 40), "font": "black", "wear": 0.15},
    ])


def build():
    a = Asset("StreetLamp", budget=1200, atlas=512, ao_radius=0.35, edge_width=0.03, preview_radius=7.2,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 16), ("SIDE", 270, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=WARM)

    iron = Material("paint", color=IRON, under=(110, 112, 118), wear=0.3, scratches=0.35, rough=0.45, metal=0.3, dirt=0.45, skin=False)
    base = Material("paint", color=IRON, under=(110, 112, 118), wear=0.35, scratches=0.35, rough=0.5, metal=0.3, dirt=0.6, skin=False, decals=[
        {"type": "rect", "center": (2.45, 1.22), "size": (5.0, 0.05), "darken": 0.5, "raise": -0.006},
        {"type": "text", "text": "WRECK CITY", "center": (1.22, 0.86), "height": 0.12, "color": (120, 122, 130), "font": "black", "wear": 0.4, "metal": 0.8},
        {"type": "rivets", "points": [(k * 0.82, 1.32) for k in range(6)], "radius": 0.04, "color": (120, 122, 130), "height": 0.012},
    ])
    silver = Material("metal", color=SILVER, rough=0.3, polish=0.8, dirt=0.3, scratches=0.3)

    a.add("Body", sh.lathe(base_profile(), 12, base, smooth_angle=35, start=90).transformed(T(0, 0, POLE_Z)))
    a.add("Body", sh.lathe(pole_profile(), 10, iron, smooth_angle=35).transformed(T(0, 0, POLE_Z)))
    for y in (4.2, 9.0):
        a.add("Body", sh.lathe([(0.0, -0.1), (0.3, -0.1), (0.33, 0.0), (0.3, 0.1), (0.0, 0.1)], 10, silver, smooth_angle=50).transformed(T(0, y, POLE_Z)))
    a.add("Body", sh.lathe([(0.0, 0.0), (0.2, 0.0), (0.22, 0.12), (0.12, 0.3), (0.04, 0.5), (0.0, 0.56)], 8, silver, smooth_angle=50).transformed(T(0, POLE_TOP, POLE_Z)))

    a.add("Body", sh.sweep(arm_path(), 0.11, 6, iron, samples=11))
    a.add("Body", sh.sweep(scroll_path(), 0.05, 5, iron))
    a.add("Body", sh.lathe(shade_profile(), 12, iron, smooth_angle=40).transformed(T(0, HEAD_Y, HEAD_Z)))
    a.add("Body", sh.lathe([(0.0, 0.0), (0.27, 0.0), (0.3, 0.05), (0.26, 0.1), (0.0, 0.1)], 12, silver, smooth_angle=50).transformed(T(0, HEAD_Y - 0.06, HEAD_Z)))
    a.add("Glow", sh.lathe([(0.0, -0.22), (0.16, -0.18), (0.25, -0.05), (0.26, 0.0), (0.0, 0.0)], 10, None, smooth_angle=60).transformed(T(0, HEAD_Y - 0.06, HEAD_Z)))

    for y in (10.45, 7.95):
        a.add("Body", sh.cylinder(0.04, 1.35, silver, bevel=0.0, segments=6).transformed(compose(T(0, y, POLE_Z - 0.85), R(90, 0, 0))))
        a.add("Body", sh.sphere(0.07, silver, 5, 3).transformed(T(0, y, POLE_Z - 1.55)))
    fabric = Material("canvas", stripes=[CYAN], stripe_width=1.0, axis=0, dirt=0.3)
    banner = sh.rounded_box((0.05, 2.4, 1.2), 0.0, 1, fabric, faces=["+x", "-x", "+y", "-y", "+z", "-z"], face_mats={"+x": banner_face(1), "-x": banner_face(-1)})
    a.add("Body", banner.transformed(T(0, 9.2, POLE_Z - 0.9)))

    destructible(a, "Downtown")
    collider(a, "Hitbox", (0.5, POLE_TOP + 0.5, 0.5), (0, (POLE_TOP + 0.5) / 2, POLE_Z), shape="Cylinder")
    collider(a, "Base", (1.5, 1.4, 1.5), (0, 0.7, POLE_Z), shape="Cylinder")
    return a
