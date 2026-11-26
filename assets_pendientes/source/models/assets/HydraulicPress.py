import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

RED = (220, 48, 40)
CHARCOAL = (40, 42, 48)
YELLOW = (255, 210, 31)
INK = (20, 20, 24)
WHITE = (236, 236, 240)
CAR_BLUE = (60, 90, 140)

BED_TOP = 2.4
TABLE_TOP = 3.2
FRAME_X = 5.6
CROWN_Y = 15.6
RAM_Y = 9.0


def red_paint(decals=()):
    return Material("paint", color=RED, under=(120, 122, 128), wear=0.35, scratches=0.4, rough=0.38, dirt=0.45, skin=False, decals=list(decals))


def frame_decals(sign):
    return [
        {"type": "rivets", "points": [(z, y) for z in (-4.2, -1.4, 1.4, 4.2) for y in (-6.0, -2.0, 2.0, 6.0)], "radius": 0.14, "color": (150, 152, 158), "height": 0.03},
        {"type": "rect", "center": (0.0, 0.0), "size": (9.0, 12.6), "outline": 0.06, "darken": 0.45, "raise": -0.006},
        {"type": "text", "text": "200 TON", "center": (0.0, -4.0), "height": 0.9, "color": WHITE, "font": "impact", "wear": 0.35},
        {"type": "rect", "center": (0.0, 3.2), "size": (2.4, 2.4), "angle": 45, "color": YELLOW, "wear": 0.3},
        {"type": "text", "text": "!", "center": (0.0, 3.25), "height": 1.5, "color": INK, "font": "black", "wear": 0.2},
    ]


def crown_face():
    return red_paint([
        {"type": "rect", "center": (0.0, 0.0), "size": (11.0, 1.5), "radius": 0.1, "color": INK, "wear": 0.2},
        {"type": "text", "text": "MEGA PRESS", "center": (0.0, 0.04), "height": 1.1, "color": YELLOW, "font": "impact", "wear": 0.25},
        {"type": "rivets", "points": [(x, y) for x in (-6.4, 6.4) for y in (-0.7, 0.7)], "radius": 0.12, "color": (150, 152, 158), "height": 0.03},
    ])


def crushed_car(paint, glass_mat):
    side = [(-3.4, 0.0), (3.4, 0.0), (3.5, 0.35), (3.2, 0.7), (1.6, 0.85), (0.9, 1.35), (-1.2, 1.4), (-2.0, 0.9), (-3.3, 0.75), (-3.5, 0.35)]
    body = sh.extrude(side, 4.6, paint, bevel=0.08, corner_radius=0.0)
    body = body.transformed(R(0, -90, 0))
    rng = np.random.default_rng(9)
    body.pos[:, 1] *= 0.85 + 0.15 * np.cos(body.pos[:, 2] * 1.3)
    body.pos += rng.normal(0, 0.05, body.pos.shape)
    body.pos[:, 0] *= 1.0 + 0.08 * np.sin(body.pos[:, 2] * 2.0)
    body = sh.recompute_normals(body)
    shard = sh.rounded_box((3.6, 0.08, 2.6), 0.0, 1, glass_mat).transformed(compose(T(0, 1.15, -0.15), R(4, 0, 6)))
    return [body, shard]


def build():
    a = Asset("HydraulicPress", budget=4500, atlas=1024, ao_radius=1.2, edge_width=0.1, preview_radius=11.0,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("SIDE", 270, 6), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 52, 52))

    bed_mat = Material("paint", color=CHARCOAL, under=(120, 122, 128), wear=0.4, scratches=0.4, rough=0.45, dirt=0.6, skin=False)
    bed_front = bed_mat.but(decals=[{"type": "stripes", "center": (0.0, -0.5), "size": (13.6, 0.6), "width": 0.4, "color": YELLOW, "wear": 0.4}])
    a.add("Body", sh.rounded_box((13.6, BED_TOP, 11.6), 0.1, 1, bed_mat, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"-z": bed_front}).transformed(T(0, BED_TOP / 2, 0)))
    plate = Material("diamondplate", color=(120, 124, 132), pitch=0.4, dirt=0.6)
    a.add("Body", sh.rounded_box((9.0, TABLE_TOP - BED_TOP, 8.0), 0.05, 1, plate, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, (TABLE_TOP + BED_TOP) / 2, -0.5)))

    for sx in (-1, 1):
        face = "+x" if sx > 0 else "-x"
        column = sh.rounded_box((2.2, CROWN_Y - BED_TOP, 10.0), 0.12, 1, red_paint(), faces=["+x", "-x", "+z", "-z"], face_mats={face: red_paint(frame_decals(sx))})
        a.add("Body", column.transformed(T(sx * FRAME_X, (CROWN_Y + BED_TOP) / 2, 0)))
        a.add("Body", sh.box((0.5, 12.0, 0.5), Material("metal", color=(170, 174, 182), rough=0.25, polish=0.8, dirt=0.3)).transformed(T(sx * (FRAME_X - 1.3), 9.0, -4.2)))

    crown = sh.rounded_box((13.6, 2.2, 10.4), 0.15, 1, red_paint(), faces=["+x", "-x", "+y", "-y", "+z", "-z"], face_mats={"-z": crown_face()})
    a.add("Body", crown.transformed(T(0, CROWN_Y + 1.1, 0)))
    tank_mat = Material("paint", color=(90, 94, 102), under=(140, 144, 150), wear=0.3, scratches=0.3, rough=0.4, dirt=0.5, skin=False, decals=[
        {"type": "text", "text": "HYDRAULIC OIL", "center": (np.pi / 2 * 1.0, 0.7), "height": 0.3, "color": WHITE, "font": "black", "wear": 0.3},
    ])
    tank = sh.lathe([(0.0, -1.6), (0.9, -1.6), (1.0, -1.4), (1.0, 1.4), (0.9, 1.6), (0.0, 1.6)], 12, tank_mat, smooth_angle=35, r_ref=1.0)
    a.add("Body", tank.transformed(compose(T(-3.0, CROWN_Y + 3.0, 2.0), R(0, 0, 90), S(0.8, 1.0, 0.8))))
    cradle = Material("metal", color=CHARCOAL, rough=0.4, polish=0.5, dirt=0.5)
    for x in (-4.0, -2.0):
        a.add("Body", sh.box((0.25, 0.5, 1.5), cradle).transformed(T(x, CROWN_Y + 2.4, 2.0)))

    steel = Material("metal", color=(150, 154, 162), rough=0.35, polish=0.6, dirt=0.4)
    chrome = Material("metal", color=(222, 226, 232), rough=0.1, polish=0.95, dirt=0.15)
    a.add("Body", sh.lathe([(0.0, 0.0), (1.5, 0.0), (1.5, 0.25), (1.3, 0.35), (1.3, 3.2), (1.5, 3.3), (1.5, 3.6), (0.0, 3.6)], 14, steel, smooth_angle=35).transformed(T(0, CROWN_Y - 3.6, -0.5)))
    a.add("Body", sh.cylinder(0.85, CROWN_Y - 3.6 - (RAM_Y + 0.7), chrome, bevel=0.0, segments=14).transformed(T(0, (CROWN_Y - 3.6 + RAM_Y + 0.7) / 2, -0.5)))

    ram_face = Material("paint", color=CHARCOAL, under=(120, 122, 128), wear=0.4, scratches=0.4, rough=0.45, dirt=0.5, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (8.6, 0.8), "color": YELLOW, "wear": 0.4},
        {"type": "stripes", "center": (0.0, 0.0), "size": (8.6, 0.8), "width": 0.35, "color": INK, "wear": 0.4},
    ])
    ram = sh.rounded_box((8.6, 1.4, 7.4), 0.1, 1, bed_mat, face_mats={"-z": ram_face, "+z": ram_face, "+x": ram_face, "-x": ram_face})
    a.add("Body", ram.transformed(T(0, RAM_Y, -0.5)))
    for sx in (-1, 1):
        a.add("Body", sh.rounded_box((0.6, 1.0, 1.2), 0.05, 1, steel).transformed(T(sx * 4.55, RAM_Y, -4.2)))

    car_paint = Material("paint", color=CAR_BLUE, under=(150, 62, 24), wear=0.75, scratches=0.6, rough=0.5, dirt=0.6, skin=False)
    glass = Material("glossy", color=(60, 120, 130), rough=0.1, dirt=0.3)
    a.add("Body", [part.transformed(compose(T(0.2, TABLE_TOP, -0.5), S(1.15, 1.15, 1.15))) for part in crushed_car(car_paint, glass)])

    hose = Material("rubber", color=(22, 22, 24), pattern="ribs", freq=14.0, depth=0.004)
    a.add("Body", sh.sweep([(-1.8, CROWN_Y + 3.0, 2.0), (-1.2, CROWN_Y + 2.6, 0.8), (-0.8, CROWN_Y + 2.25, -0.2)], 0.14, 5, hose, samples=8))
    a.add("Body", sh.sweep([(-4.4, CROWN_Y + 3.0, 2.0), (-5.4, CROWN_Y + 2.0, 3.6), (-6.85, CROWN_Y - 1.0, 4.4), (-6.85, 6.0, 4.6), (-6.4, BED_TOP + 0.2, 4.8)], 0.14, 5, hose, samples=14))

    box_mat = Material("paint", color=(150, 116, 60), under=(130, 132, 138), wear=0.4, scratches=0.35, rough=0.42, dirt=0.5, skin=False)
    box_face = box_mat.but(decals=[
        {"type": "circle", "center": (0.0, 0.45), "radius": 0.24, "color": (60, 220, 90), "wear": 0.1},
        {"type": "text", "text": "START", "center": (0.0, 0.85), "height": 0.14, "color": INK, "font": "black", "wear": 0.2},
        {"type": "rect", "center": (0.0, -0.5), "size": (1.1, 0.7), "radius": 0.06, "color": YELLOW, "wear": 0.2},
    ])
    a.add("Body", sh.rounded_box((1.6, 2.4, 1.2), 0.08, 1, box_mat, face_mats={"-z": box_face}).transformed(T(6.2, 3.8, -6.2)))
    a.add("Body", sh.box((0.3, 2.6, 0.3), cradle).transformed(T(6.2, 1.3, -6.0)))
    a.add("Glow", sh.lathe([(0.0, 0.0), (0.32, 0.0), (0.32, 0.12), (0.2, 0.22), (0.0, 0.24)], 10, None, smooth_angle=40).transformed(compose(T(6.2, 4.3, -6.8), R(-90, 0, 0))))
    for sx in (-1, 1):
        a.add("Glow", sh.rounded_box((1.0, 0.5, 0.2), 0.08, 1, None).transformed(T(sx * 4.0, CROWN_Y + 2.45, -5.25)))

    destructible(a, "Industrial")
    collider(a, "Hitbox", (13.6, BED_TOP, 11.6), (0, BED_TOP / 2, 0))
    collider(a, "LeftFrame", (2.2, CROWN_Y - BED_TOP, 10.0), (-FRAME_X, (CROWN_Y + BED_TOP) / 2, 0))
    collider(a, "RightFrame", (2.2, CROWN_Y - BED_TOP, 10.0), (FRAME_X, (CROWN_Y + BED_TOP) / 2, 0))
    collider(a, "Crown", (13.6, 2.2, 10.4), (0, CROWN_Y + 1.1, 0))
    return a
