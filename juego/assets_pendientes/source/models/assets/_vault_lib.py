import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

BODY = (8.0, 7.2, 7.4)
BODY_Y = 0.6 + 0.4 + BODY[1] / 2
FRONT_Z = -BODY[2] / 2
INK = (18, 16, 14)


def gold(decals=()):
    return Material("gold", color=(255, 196, 40), rough=0.22, scratches=0.25, dirt=0.15, decals=list(decals))


def trim(decals=()):
    return Material("metal", color=(26, 24, 26), rough=0.35, polish=0.7, dirt=0.25, scratches=0.3, decals=list(decals))


def side_decals(accent):
    return [
        {"type": "rect", "center": (0.0, 0.0), "size": (6.4, 5.6), "radius": 0.2, "outline": 0.08, "darken": 0.35, "raise": -0.008},
        {"type": "rivets", "points": [(x, y) for x in (-3.0, 3.0) for y in np.linspace(-2.6, 2.6, 6)], "radius": 0.1, "color": (230, 180, 50), "height": 0.025},
        {"type": "text", "text": "$", "center": (0.0, 0.0), "height": 2.6, "color": (200, 140, 20), "font": "impact", "wear": 0.0, "raise": -0.006},
    ]


def build_vault(name, title, accent, zone="VIP"):
    a = Asset(name, budget=2500, atlas=1024, ao_radius=0.8, edge_width=0.07, gradient=0.08, highlight=0.6, preview_radius=7.0,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("FRONT", 180, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=accent)

    body = sh.rounded_box(BODY, 0.35, 1, gold(), faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"+x": gold(side_decals(accent)), "-x": gold(side_decals(accent)), "+z": gold(side_decals(accent))})
    a.add("Body", body.transformed(T(0, BODY_Y, 0)))
    dark = trim()
    a.add("Body", sh.rounded_box((8.4, 0.5, 7.8), 0.1, 1, dark).transformed(T(0, 0.85, 0)))
    a.add("Body", sh.rounded_box((8.4, 0.5, 7.8), 0.1, 1, dark).transformed(T(0, BODY_Y + BODY[1] / 2 + 0.05, 0)))
    for sx in (-1, 1):
        for sz in (-1, 1):
            a.add("Body", sh.box((0.5, BODY[1] - 0.4, 0.5), dark).transformed(T(sx * 4.0, BODY_Y, sz * 3.7)))
            a.add("Body", sh.lathe([(0.0, 0.0), (0.55, 0.0), (0.45, 0.6), (0.0, 0.6)], 8, dark, smooth_angle=40).transformed(T(sx * 3.3, 0.0, sz * 3.0)))

    door_y = BODY_Y - 0.2
    door_mount = compose(T(0, door_y, FRONT_Z), R(-90, 0, 0))
    rim = sh.lathe([(2.6, 0.0), (3.0, 0.0), (3.0, 0.25), (2.8, 0.35), (2.6, 0.3)], 24, dark, closed=True, smooth_angle=40)
    a.add("Body", rim.transformed(door_mount))
    door_face = gold([
        {"type": "circle", "center": (0.0, 0.0), "radius": 2.0, "outline": 0.06, "darken": 0.35, "raise": -0.006},
        {"type": "circle", "center": (0.0, 0.0), "radius": 1.2, "outline": 0.05, "darken": 0.35, "raise": -0.006},
    ])
    door = sh.lathe([(0.0, 0.4), (2.55, 0.4), (2.6, 0.3), (2.6, 0.0), (0.0, 0.0)][::-1], 24, door_face, smooth_angle=40)
    a.add("Body", door.transformed(door_mount))
    for k in range(8):
        ang = np.radians(k * 45 + 22.5)
        bolt = sh.cylinder(0.18, 0.3, Material("chrome"), bevel=0.04, segments=8)
        a.add("Body", bolt.transformed(compose(door_mount, T(np.cos(ang) * 2.2, 0.5, -np.sin(ang) * 2.2))))
    hub = sh.lathe([(0.0, 0.4), (0.6, 0.4), (0.6, 0.8), (0.45, 0.95), (0.0, 0.95)], 12, Material("chrome"), smooth_angle=40)
    a.add("Body", hub.transformed(door_mount))
    for k in range(3):
        spoke = sh.cylinder(0.12, 3.2, dark, bevel=0.0, segments=6)
        a.add("Body", spoke.transformed(compose(door_mount, T(0, 0.75, 0), R(0, k * 60, 0), R(0, 0, 90))))
        for sgn in (-1, 1):
            knob = sh.sphere(0.22, dark, 6, 3)
            a.add("Body", knob.transformed(compose(door_mount, T(0, 0.75, 0), R(0, k * 60, 0), T(sgn * 1.6, 0, 0))))
    a.add("Glow", sh.lathe([(0.0, 0.96), (0.35, 0.96)][::-1], 10, None, smooth_angle=40).transformed(door_mount))

    plaque = trim([
        {"type": "rect", "center": (0.0, 0.0), "size": (3.8, 0.66), "radius": 0.08, "outline": 0.05, "color": accent, "wear": 0.0},
        {"type": "text", "text": title, "center": (0.0, 0.02), "height": 0.42, "color": (255, 210, 60), "font": "impact", "wear": 0.0},
    ])
    a.add("Body", sh.rounded_box((4.0, 0.8, 0.12), 0.04, 1, dark, face_mats={"-z": plaque}).transformed(T(0, BODY_Y + BODY[1] / 2 - 0.55, FRONT_Z - 0.06)))
    crown = sh.lathe([(0.0, 0.0), (3.2, 0.0), (3.0, 0.25), (2.4, 0.4), (0.0, 0.45)], 4, gold(), smooth_angle=10, start=45)
    a.add("Body", crown.transformed(compose(T(0, BODY_Y + BODY[1] / 2 + 0.3, 0), S(1.0, 1.0, 0.92))))
    a.add("Glow", sh.box((8.5, 0.14, 7.9), None).transformed(T(0, 1.32, 0)))
    for x in (-1.6, 0.0, 1.6):
        coin = sh.cylinder(0.42, 0.12, gold(), bevel=0.02, segments=12)
        a.add("Body", coin.transformed(compose(T(x * 1.4 + 0.4, 0.06 + abs(x) * 0.02, FRONT_Z - 1.2 - abs(x) * 0.3), R(0, x * 20, 0))))
    a.add("Body", sh.cylinder(0.42, 0.12, gold(), bevel=0.02, segments=12).transformed(compose(T(-2.6, 0.32, FRONT_Z - 0.9), R(70, 30, 0))))

    destructible(a, zone)
    collider(a, "Hitbox", (8.4, BODY_Y + BODY[1] / 2 + 0.3, 7.8), (0, (BODY_Y + BODY[1] / 2 + 0.3) / 2, 0))
    return a
