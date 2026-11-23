import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

ORANGE = (255, 122, 26)
CHARCOAL = (44, 46, 54)
TEAL = (40, 240, 220)
YELLOW = (255, 210, 31)
INK = (20, 20, 24)
WHITE = (236, 236, 240)

SHOULDER = (3.5, 0.3)
ELBOW = (9.0, 1.5)
WRIST = (12.0, -1.4)


def beam(p0, p1, w0, w1, depth, mat, radius=0.3):
    a = np.array([p0[1], p0[0]], dtype=np.float64)
    b = np.array([p1[1], p1[0]], dtype=np.float64)
    d = (b - a) / np.linalg.norm(b - a)
    n = np.array([-d[1], d[0]])
    poly = [a + n * w0 / 2, b + n * w1 / 2, b - n * w1 / 2, a - n * w0 / 2]
    mesh = sh.extrude(poly, depth, mat, bevel=0.06, corner_radius=radius, corner_segments=2)
    return mesh.transformed(R(0, -90, 0))


def joint(y, z, radius, length, mat, cap=None):
    parts = [sh.cylinder(radius, length, mat, bevel=0.06, segments=14).transformed(compose(T(0, y, z), R(0, 0, 90)))]
    if cap is not None:
        for sx in (-1, 1):
            parts.append(sh.cylinder(radius * 0.55, 0.12, cap, bevel=0.03, segments=12).transformed(compose(T(sx * (length / 2 + 0.05), y, z), R(0, 0, 90))))
    return parts


def arm_paint(decals=()):
    return Material("paint", color=ORANGE, under=(130, 132, 138), wear=0.3, scratches=0.35, rough=0.36, dirt=0.4, skin=False, decals=list(decals))


def build():
    a = Asset("RobotArm", budget=3000, atlas=1024, ao_radius=0.7, edge_width=0.06, preview_radius=7.4,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("SIDE", 270, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=TEAL)

    plate = Material("paint", color=CHARCOAL, under=(120, 122, 128), wear=0.4, scratches=0.4, rough=0.45, dirt=0.55, skin=False, decals=[
        {"type": "stripes", "center": (np.pi * 2.8, 0.25), "size": (2 * np.pi * 2.8 + 0.4, 0.4), "width": 0.3, "color": YELLOW, "wear": 0.4},
        {"type": "rivets", "points": [(k * 2 * np.pi * 2.8 / 8, 0.8) for k in range(8)], "radius": 0.12, "color": (150, 152, 158), "height": 0.03},
    ])
    a.add("Body", sh.lathe([(0.0, 0.0), (2.8, 0.0), (2.8, 0.42), (2.6, 0.6), (0.0, 0.6)], 18, plate, smooth_angle=35))
    turret_mat = arm_paint([
        {"type": "text", "text": "WR-6", "center": (np.pi / 2 * 2.1, 0.8), "height": 0.5, "color": INK, "font": "impact", "wear": 0.3},
        {"type": "rect", "center": (np.pi / 2 * 2.1 + 3.3, 0.85), "size": (0.9, 0.9), "angle": 45, "color": YELLOW, "wear": 0.3},
        {"type": "text", "text": "!", "center": (np.pi / 2 * 2.1 + 3.3, 0.88), "height": 0.5, "color": INK, "font": "black", "wear": 0.2},
    ])
    a.add("Body", sh.lathe([(0.0, 0.6), (2.1, 0.6), (2.1, 1.7), (1.8, 2.3), (1.4, 2.5), (0.0, 2.5)], 16, turret_mat, smooth_angle=35, r_ref=2.1))
    a.add("Glow", sh.lathe([(2.08, 1.0), (2.18, 1.0), (2.18, 1.22), (2.08, 1.22)], 16, None, closed=True, smooth_angle=30))

    dark = Material("metal", color=CHARCOAL, rough=0.38, polish=0.6, dirt=0.4, scratches=0.3)
    chrome = Material("metal", color=(210, 214, 222), rough=0.15, polish=0.9, dirt=0.2)
    cap = Material("metal", color=(170, 174, 182), rough=0.3, polish=0.7, dirt=0.3)
    housing = sh.rounded_box((2.6, 2.2, 2.4), 0.3, 1, arm_paint())
    a.add("Body", housing.transformed(T(0, 2.9, 0.3)))
    a.add("Body", joint(SHOULDER[0], SHOULDER[1], 1.05, 3.2, dark, cap))

    lower_mat = arm_paint([
        {"type": "text", "text": "AXIS 2", "center": (0.0, 0.0), "height": 0.3, "color": INK, "font": "black", "wear": 0.3, "angle": -78},
        {"type": "stripes", "center": (1.6, 0.0), "size": (0.6, 1.4), "width": 0.2, "color": INK, "wear": 0.3},
    ])
    a.add("Body", beam(SHOULDER, ELBOW, 1.9, 1.4, 1.7, lower_mat))
    a.add("Body", joint(ELBOW[0], ELBOW[1], 0.85, 2.3, dark, cap))
    upper_mat = arm_paint([
        {"type": "text", "text": "WRECK ROBOTICS", "center": (0.0, 0.0), "height": 0.24, "color": INK, "font": "black", "wear": 0.3},
    ])
    a.add("Body", beam(ELBOW, WRIST, 1.35, 1.0, 1.4, upper_mat))
    motor = sh.rounded_box((1.8, 1.2, 1.4), 0.2, 1, arm_paint())
    a.add("Body", motor.transformed(compose(T(0, ELBOW[0] + 0.3, ELBOW[1] + 1.0), R(-40, 0, 0))))

    a.add("Body", joint(WRIST[0], WRIST[1], 0.6, 1.5, dark, cap))
    wrist = sh.cylinder(0.45, 1.0, dark, bevel=0.05, segments=10)
    a.add("Body", wrist.transformed(T(0, WRIST[0] - 0.75, WRIST[1] - 0.2)))
    a.add("Body", sh.rounded_box((1.3, 0.3, 1.0), 0.05, 1, dark).transformed(T(0, WRIST[0] - 1.35, WRIST[1] - 0.2)))
    for sx in (-1, 1):
        finger = sh.extrude([(0.0, 0.0), (0.22, 0.0), (0.3, -0.7), (0.1, -1.1), (-0.04, -1.05), (0.06, -0.62)], 0.5, chrome, bevel=0.02, corner_radius=0.0)
        a.add("Body", finger.transformed(compose(T(sx * 0.3, WRIST[0] - 1.45, WRIST[1] - 0.2), S(sx, 1, 1))))
    a.add("Body", sh.cylinder(0.09, 0.9, chrome, bevel=0.0, segments=6).transformed(T(0, WRIST[0] - 1.9, WRIST[1] - 0.2)))
    a.add("Glow", sh.sphere(0.16, None, 8, 4).transformed(T(0, WRIST[0] - 2.4, WRIST[1] - 0.2)))

    base_pt = np.array([0.95, 2.4, -1.0])
    top_pt = np.array([0.95, 6.6, 0.75])
    axis = top_pt - base_pt
    length = np.linalg.norm(axis)
    tilt = np.degrees(np.arctan2(axis[2], axis[1]))
    for sx in (-1, 1):
        mid = (base_pt + top_pt) / 2 * np.array([sx, 1, 1])
        a.add("Body", sh.cylinder(0.24, length * 0.55, dark, bevel=0.03, segments=8).transformed(compose(T(mid[0], base_pt[1] + axis[1] * 0.28, base_pt[2] + axis[2] * 0.28), R(tilt, 0, 0))))
        a.add("Body", sh.cylinder(0.13, length * 0.55, chrome, bevel=0.0, segments=8).transformed(compose(T(mid[0], base_pt[1] + axis[1] * 0.72, base_pt[2] + axis[2] * 0.72), R(tilt, 0, 0))))

    cable = Material("rubber", color=(22, 22, 24), pattern="ribs", freq=16.0, depth=0.004)
    path = [(0.0, 2.3, 1.5), (0.0, 3.6, 1.6), (0.0, 6.4, 2.2), (0.0, 9.0, 2.5), (0.0, 10.4, 1.6), (0.0, 11.8, 0.0), (0.0, 12.5, -1.1)]
    a.add("Body", sh.sweep(path, 0.13, 5, cable, samples=14))

    destructible(a, "Industrial")
    collider(a, "Hitbox", (5.6, 2.5, 5.6), (0, 1.25, 0), shape="Cylinder")
    collider(a, "Arm", (2.6, 10.6, 3.6), (0, 7.6, 0.0))
    return a
