import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _military_lib import olive, OLIVE_DARK, STENCIL, YELLOW, INK

WHITE = (214, 218, 224)
CYAN = (34, 225, 255)
DISH_R = 5.2
FOCAL = 4.6
PIVOT = (0.0, 9.3, 0.4)
TILT = 35.0


def dish_profile():
    rs = np.linspace(0.0, DISH_R, 7)
    front = [(r, r * r / (4 * FOCAL)) for r in rs]
    back = [(r, r * r / (4 * FOCAL) - 0.28 + 0.1 * (r / DISH_R) ** 2) for r in rs]
    return back + [(DISH_R + 0.12, front[-1][1] + 0.02)] + front[::-1]


def dish_frame():
    return compose(T(*PIVOT), R(-90 + TILT, 0, 0), T(0, 0.7, 0))


def build():
    a = Asset("RadarDish", budget=3000, atlas=1024, ao_radius=1.0, edge_width=0.08, preview_radius=8.2,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=CYAN)

    concrete = Material("concrete", color=(128, 128, 124), dirt=0.6, decals=[
        {"type": "stripes", "center": (0.0, -4.7), "size": (10.0, 0.5), "width": 0.4, "color": YELLOW, "wear": 0.5},
        {"type": "stripes", "center": (0.0, 4.7), "size": (10.0, 0.5), "width": 0.4, "color": YELLOW, "wear": 0.5},
        {"type": "rivets", "points": [(x, z) for x in (-3.2, 3.2) for z in (-3.2, 3.2)], "radius": 0.18, "color": (110, 112, 108), "height": 0.03},
    ])
    a.add("Body", sh.rounded_box((10.0, 1.0, 10.0), 0.08, 1, concrete, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 0.5, 0)))
    dark = Material("metal", color=(60, 62, 58), rough=0.45, polish=0.4, dirt=0.5, scratches=0.35, decals=[
        {"type": "rect", "center": (np.pi * 2.5, 0.25), "size": (2 * np.pi * 2.5 + 0.2, 0.2), "darken": 0.4, "raise": -0.006},
    ])
    a.add("Body", sh.lathe([(0.0, 1.0), (2.6, 1.0), (2.6, 1.5), (2.3, 1.7), (2.3, 2.0), (1.4, 2.1), (0.0, 2.1)], 16, dark, smooth_angle=35))
    paint = olive(WHITE, under=(130, 132, 136), wear=0.3, rough=0.45, metal=0.1)
    a.add("Body", sh.lathe([(0.0, 2.0), (1.05, 2.0), (0.8, 7.2), (0.95, 7.4), (0.0, 7.4)], 12, paint, smooth_angle=35))
    brace = olive(OLIVE_DARK)
    for k in range(4):
        ang = np.radians(45 + 90 * k)
        foot = (np.cos(ang) * 3.6, 1.0, np.sin(ang) * 3.6)
        top = (np.cos(ang) * 0.85, 5.2, np.sin(ang) * 0.85)
        a.add("Body", sh.sweep([foot, top], 0.13, 5, brace))
        a.add("Body", sh.box((0.6, 0.12, 0.6), dark).transformed(T(foot[0], 1.06, foot[2])))

    yoke = olive(WHITE, under=(130, 132, 136), wear=0.3, rough=0.45, decals=[
        {"type": "text", "text": "WR-RADAR 2", "center": (0.0, 0.0), "height": 0.28, "color": INK, "font": "black", "wear": 0.3},
    ])
    a.add("Body", sh.rounded_box((3.6, 0.6, 2.2), 0.1, 1, yoke).transformed(T(0, 7.7, PIVOT[2])))
    for sx in (-1, 1):
        arm = sh.extrude([(-0.9, 0.0), (0.9, 0.0), (0.5, 2.0), (-0.5, 2.0)], 0.4, yoke, bevel=0.06, corner_radius=0.2)
        a.add("Body", arm.transformed(compose(T(sx * 1.6, 7.9, PIVOT[2]), R(0, 90, 0))))
        a.add("Body", sh.cylinder(0.45, 0.4, dark, bevel=0.05, segments=12).transformed(compose(T(sx * 1.9, PIVOT[1], PIVOT[2]), R(0, 0, 90))))

    dish_mat = olive(WHITE, under=(140, 142, 146), wear=0.25, rough=0.4, metal=0.15, decals=[
        *[{"type": "rect", "center": (k * 2 * np.pi * DISH_R / 12, 3.0), "size": (0.05, 6.0), "darken": 0.3, "raise": -0.004} for k in range(12)],
        {"type": "text", "text": "WRECKRUSH DEFENSE", "center": (np.pi / 2 * DISH_R, 1.6), "height": 0.4, "color": INK, "font": "impact", "wear": 0.3},
    ])
    frame = dish_frame()
    a.add("Body", sh.lathe(dish_profile(), 22, dish_mat, smooth_angle=30, r_ref=DISH_R).transformed(frame))
    a.add("Body", sh.lathe([(0.0, -0.9), (1.2, -0.9), (1.4, -0.3), (0.0, -0.2)], 12, dark, smooth_angle=40).transformed(frame))
    focus = FOCAL * 0.9
    for k in range(3):
        ang = np.radians(90 + k * 120)
        rim = (np.cos(ang) * DISH_R * 0.92, DISH_R ** 2 * 0.85 / (4 * FOCAL), -np.sin(ang) * DISH_R * 0.92)
        a.add("Body", sh.sweep([rim, (0.0, focus - 0.4, 0.0)], 0.06, 4, dark).transformed(frame))
    a.add("Body", sh.lathe([(0.0, focus - 0.6), (0.38, focus - 0.6), (0.3, focus - 0.1), (0.0, focus)], 10, dark, smooth_angle=40).transformed(frame))
    a.add("Glow", sh.sphere(0.32, None, 10, 5).transformed(compose(frame, T(0, focus + 0.15, 0))))

    cab = olive(OLIVE_DARK, decals=[
        {"type": "rect", "center": (0.0, -0.45), "size": (1.6, 1.0), "radius": 0.06, "color": (10, 14, 16), "wear": 0.0},
        *[{"type": "rect", "center": (0.0, 0.5 + k * 0.16), "size": (1.6, 0.06), "darken": 0.6, "raise": -0.006} for k in range(4)],
        {"type": "text", "text": "TRACK", "center": (0.0, 1.2), "height": 0.18, "color": STENCIL, "font": "black", "wear": 0.3},
    ])
    a.add("Body", sh.rounded_box((2.4, 3.0, 1.6), 0.08, 1, olive(OLIVE_DARK), faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"-z": cab}).transformed(compose(T(3.4, 2.5, 3.2), R(0, 20, 0))))
    a.add("Glow", sh.box((1.5, 0.92, 0.03), None).transformed(compose(T(3.4, 2.5, 3.2), R(0, 20, 0), T(0, 0.45, -0.82))))
    cable = Material("rubber", color=(22, 22, 24), pattern="ribs", freq=14.0, depth=0.004)
    a.add("Body", sh.sweep([(3.0, 1.05, 2.5), (1.8, 1.05, 1.6), (0.9, 1.6, 0.9), (0.6, 2.8, 0.5)], 0.08, 4, cable, samples=8))

    destructible(a, "Military")
    collider(a, "Hitbox", (10.0, 1.0, 10.0), (0, 0.5, 0))
    collider(a, "Mast", (2.4, 7.0, 2.4), (0, 4.5, 0), shape="Cylinder")
    collider(a, "Dish", (10.4, 10.4, 1.6), (0, PIVOT[1] + 0.8, PIVOT[2] - 1.15), rotation=(TILT, 0, 0))
    collider(a, "Cabinet", (2.4, 3.0, 1.6), (3.4, 2.5, 3.2), rotation=(0, 20, 0))
    return a
