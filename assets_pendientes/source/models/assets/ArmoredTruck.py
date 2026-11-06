import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from RustyCar import TIRE, HUBCAP, arc_from_end

ARMOR = (104, 86, 60)
YELLOW = (255, 210, 31)
INK = (20, 18, 16)
AXLE_Y = 1.55
WHEEL_SCALE = 1.32
TRACK = 4.25
AXLES = (-6.4, 3.0, 6.7)
BOX_Z0 = -3.4
BOX_Z1 = 9.4
BOX_Y0 = 2.6
BOX_Y1 = 9.0
HALF_W = 4.5


def armor(decals=()):
    return Material("paint", color=ARMOR, under=(150, 150, 150), wear=0.35, scratches=0.4, rough=0.45, metal=0.3, dirt=0.45, dirt_color=(60, 50, 40), skin=False, decals=list(decals))


def side_extrude(points, width, mat, bevel=0.1, cap_mats=None):
    mesh = sh.extrude(np.asarray(points, dtype=np.float64), width, mat, bevel=bevel, corner_radius=0.0, cap_mats=cap_mats)
    return mesh.transformed(R(0, -90, 0))


def box_side(sign):
    zc = (BOX_Z0 + BOX_Z1) / 2
    yc = (BOX_Y0 + BOX_Y1) / 2

    def at(z, y):
        return ((z - zc) if sign < 0 else -(z - zc), -(y - yc))

    return [
        {"type": "rect", "center": at(zc, 3.4), "size": (12.8, 0.7), "color": YELLOW, "wear": 0.35},
        {"type": "rect", "center": at(zc + 0.4, 6.1), "size": (8.4, 2.2), "radius": 0.15, "color": INK, "wear": 0.3},
        {"type": "text", "text": "$ CASH $", "center": at(zc + 0.4, 6.15), "height": 1.5, "color": YELLOW, "font": "impact", "wear": 0.3},
        {"type": "text", "text": "WRECK BANK & TRUST", "center": at(zc + 0.4, 4.4), "height": 0.4, "color": INK, "font": "black", "wear": 0.3},
        *[{"type": "rect", "center": at(z, 7.8), "size": (1.4, 0.36), "radius": 0.08, "color": (10, 10, 10), "wear": 0.0, "raise": -0.02} for z in (-1.0, 7.4)],
        {"type": "rivets", "points": [at(z, y) for z in np.linspace(BOX_Z0 + 0.4, BOX_Z1 - 0.4, 14) for y in (2.9, 8.7)], "radius": 0.09, "color": (150, 140, 120), "height": 0.02},
    ]


def cab_side(sign):
    def at(z, y):
        return (z if sign < 0 else -z, -y)

    return [
        {"type": "rect", "center": at(-6.6, 3.4), "size": (5.6, 0.6), "color": YELLOW, "wear": 0.35},
        {"type": "rect", "center": at(-5.4, 5.7), "size": (2.0, 1.2), "radius": 0.1, "color": (12, 14, 16), "wear": 0.0},
        {"type": "rect", "center": at(-5.4, 4.6), "size": (3.0, 3.6), "outline": 0.04, "darken": 0.5, "raise": -0.006},
        {"type": "rect", "center": at(-4.3, 4.7), "size": (0.36, 0.1), "color": (40, 40, 40), "wear": 0.1, "raise": 0.004},
        {"type": "text", "text": "07", "center": at(-8.4, 4.4), "height": 0.7, "color": YELLOW, "font": "impact", "wear": 0.3},
    ]


def rear_decals():
    return [
        {"type": "rect", "center": (0.0, 0.0), "size": (7.6, 5.6), "outline": 0.08, "darken": 0.5, "raise": -0.008},
        {"type": "stripes", "center": (0.0, 2.6), "size": (8.6, 0.6), "width": 0.4, "color": YELLOW, "wear": 0.35},
        {"type": "text", "text": "NO CASH KEPT IN VEHICLE", "center": (0.0, -2.2), "height": 0.32, "color": YELLOW, "font": "impact", "wear": 0.3},
    ]


def wheel(m, x, z):
    turn = R(0, 0, 90) if x > 0 else R(0, 0, -90)
    place = compose(T(x, AXLE_Y, z), turn, S(WHEEL_SCALE, WHEEL_SCALE * 1.1, WHEEL_SCALE))
    return [sh.lathe(TIRE, 14, m["tire"], smooth_angle=50).transformed(place), sh.lathe(HUBCAP, 10, m["hub"], smooth_angle=40).transformed(place)]


def build():
    a = Asset("ArmoredTruck", budget=4500, atlas=1024, ao_radius=1.2, edge_width=0.1, gradient=0.08, highlight=0.5, preview_radius=11.8,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=(30, 34, 40), transparency=0.25)
    a.role("Glow", "neon", color=YELLOW)
    a.role("Lamp", "neon", color=(255, 248, 220))

    m = {
        "tire": Material("rustycar_tire", tread_v=(arc_from_end(TIRE, 4), arc_from_end(TIRE, 3)), ring_v=arc_from_end(TIRE, 1) + 0.06, pitch=0.4, dirt=0.4, dirt_color=(90, 80, 66)),
        "hub": Material("paint", color=YELLOW, under=(150, 150, 150), wear=0.35, scratches=0.3, rough=0.4, dirt=0.3, skin=False),
    }
    dark = Material("metal", color=(30, 30, 32), rough=0.45, polish=0.4, dirt=0.5)
    plate = Material("diamondplate", color=(120, 104, 80), pitch=0.4, dirt=0.5)

    a.add("Body", sh.box((8.4, 1.2, 19.0), dark).transformed(T(0, 2.0, 0.1)))
    box = sh.rounded_box((2 * HALF_W, BOX_Y1 - BOX_Y0, BOX_Z1 - BOX_Z0), 0.18, 1, armor(), faces=["+x", "-x", "+y", "-y", "+z", "-z"],
                         face_mats={"-x": armor(box_side(-1)), "+x": armor(box_side(1)), "+z": armor(rear_decals()), "+y": plate})
    a.add("Body", box.transformed(T(0, (BOX_Y0 + BOX_Y1) / 2, (BOX_Z0 + BOX_Z1) / 2)))
    cab = [(-9.6, 2.5), (-3.3, 2.5), (-3.3, 7.3), (-6.4, 7.3), (-8.0, 5.9), (-9.6, 5.5)]
    a.add("Body", side_extrude(cab, 2 * HALF_W - 0.2, armor(), bevel=0.15, cap_mats=[armor(cab_side(-1)), armor(cab_side(1))]))
    hood_face = armor([
        *[{"type": "rect", "center": (x, 0.0), "size": (0.22, 1.2), "radius": 0.08, "color": (14, 14, 14), "wear": 0.0, "raise": -0.02} for x in np.linspace(-2.2, 2.2, 9)],
    ])
    a.add("Body", sh.rounded_box((6.0, 1.6, 0.12), 0.0, 1, dark, faces=["-z", "+x", "-x", "+y", "-y"], face_mats={"-z": hood_face}).transformed(T(0, 4.0, -9.66)))
    for x in (-3.3, 3.3):
        a.add("Body", sh.lathe([(0.0, 0.0), (0.55, 0.0), (0.55, 0.15), (0.45, 0.2), (0.0, 0.2)], 10, dark, smooth_angle=40).transformed(compose(T(x, 4.0, -9.6), R(-90, 0, 0))))
        a.add("Lamp", sh.lathe([(0.0, 0.0), (0.42, 0.0), (0.3, 0.1), (0.0, 0.14)], 10, None, smooth_angle=50).transformed(compose(T(x, 4.0, -9.82), R(-90, 0, 0))))
    tilt = np.degrees(np.arctan2(1.6, 1.4))
    pane = compose(T(0, 6.64, -7.24), R(tilt, 0, 0))
    a.add("Glass", sh.box((7.6, 1.9, 0.04), None).transformed(pane))
    grille = Material("metal", color=(34, 34, 36), rough=0.4, polish=0.4, dirt=0.4)
    for k in range(4):
        a.add("Body", sh.box((7.8, 0.08, 0.08), grille).transformed(compose(pane, T(0, -0.6 + k * 0.4, -0.08))))

    bar = [(-4.6, 1.6, -10.2), (-4.6, 3.3, -10.4), (4.6, 3.3, -10.4), (4.6, 1.6, -10.2)]
    a.add("Body", sh.sweep(bar, 0.22, 6, dark, samples=10))
    a.add("Body", sh.box((9.0, 0.5, 0.5), dark).transformed(T(0, 2.4, -10.3)))
    a.add("Body", sh.rounded_box((9.4, 0.8, 0.5), 0.06, 1, m["hub"]).transformed(T(0, 1.8, 9.7)))

    wheel_rim = Material("paint", color=YELLOW, under=(150, 150, 150), wear=0.35, scratches=0.3, rough=0.4, dirt=0.3, skin=False)
    door_mount = compose(T(0, 5.8, BOX_Z1 + 0.05), R(90, 0, 0))
    a.add("Body", sh.torus(1.1, 0.12, wheel_rim, segments=16, sides=4).transformed(door_mount))
    a.add("Body", sh.cylinder(0.3, 0.3, wheel_rim, bevel=0.04, segments=10).transformed(compose(door_mount, T(0, 0.12, 0))))
    for ang in (0, 60, 120):
        a.add("Body", sh.box((2.2, 0.12, 0.12), dark).transformed(compose(door_mount, T(0, 0.15, 0), R(0, ang, 0))))
    for x in (-3.9, 3.9):
        a.add("Body", sh.box((0.25, 5.0, 0.25), dark).transformed(T(x, 5.8, BOX_Z1 + 0.1)))

    hatch = armor([{"type": "rect", "center": (0.0, 0.0), "size": (2.0, 2.0), "outline": 0.08, "darken": 0.5, "raise": -0.006}])
    a.add("Body", sh.rounded_box((2.4, 0.3, 2.4), 0.06, 1, armor(), face_mats={"+y": hatch}).transformed(T(0, BOX_Y1 + 0.15, 2.0)))
    for x in (-3.4, 3.4):
        a.add("Body", sh.cylinder(0.32, 0.2, dark, bevel=0.02, segments=10).transformed(T(x, 7.4, -4.6)))
        a.add("Glow", sh.lathe([(0.0, 0.0), (0.32, 0.0), (0.3, 0.3), (0.15, 0.45), (0.0, 0.48)], 10, None, smooth_angle=50).transformed(T(x, 7.5, -4.6)))

    for x in (-TRACK, TRACK):
        for z in AXLES:
            a.add("Body", wheel(m, x, z))
    liner = Material("rubber", color=(24, 24, 26), pattern="dots", freq=5.0, depth=0.004, dirt=0.5)
    for z in AXLES:
        a.add("Body", sh.rounded_box((6.6, 1.8, 3.4), 0.0, 1, liner, faces=["+x", "-x", "-y", "+z", "-z"]).transformed(T(0, 2.3, z)))

    destructible(a, "Event")
    collider(a, "Hitbox", (2 * HALF_W, BOX_Y1 - 1.0, BOX_Z1 - BOX_Z0), (0, (BOX_Y1 + 1.0) / 2, (BOX_Z0 + BOX_Z1) / 2))
    collider(a, "Cab", (8.8, 6.3, 6.3), (0, 4.15, -6.45))
    return a
