import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

STEEL = (150, 156, 166)
ORANGE = (255, 122, 26)
RED = (220, 48, 40)
YELLOW = (255, 210, 31)
INK = (20, 20, 24)
FIRE = (255, 120, 30)

VESSEL_R = 6.0
BANDS = (4.2, 9.0, 13.8)
STACK_TOP = 25.6


def vessel_profile():
    pts = [(0.0, 1.0), (6.25, 1.0), (6.25, 1.7), (VESSEL_R, 1.85)]
    for y in BANDS:
        pts += [(VESSEL_R, y - 0.3), (VESSEL_R + 0.18, y - 0.22), (VESSEL_R + 0.18, y + 0.22), (VESSEL_R, y + 0.3)]
    pts += [(VESSEL_R, 16.8), (5.6, 17.6), (5.0, 17.9), (4.9, 18.3), (4.0, 19.0), (2.6, 19.6), (1.4, 19.85), (0.0, 19.9)]
    return pts


def profile_v(profile):
    pts = np.asarray(profile)
    arc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    return pts, arc[-1] - arc


def vessel_material():
    pts, v = profile_v(vessel_profile())
    wall = pts[:, 0] >= VESSEL_R - 0.01
    def at_y(y):
        return float(np.interp(y, pts[wall, 1], v[wall]))
    ring = 2 * np.pi * VESSEL_R
    front = np.pi / 2 * VESSEL_R
    rivets = []
    for y in BANDS:
        for k in range(36):
            u = k * ring / 36
            rivets += [(u, at_y(y) - 0.12), (u, at_y(y) + 0.12)]
    seams = [{"type": "rect", "center": (u, at_y(9.0)), "size": (0.05, 15.0), "darken": 0.35, "raise": -0.004} for u in np.linspace(0.0, ring, 7)[:-1] + 1.3]
    return Material("metal", color=STEEL, rough=0.42, polish=0.4, dirt=0.55, dirt_color=(60, 50, 40), scratches=0.35, decals=[
        {"type": "rivets", "points": rivets, "radius": 0.07, "color": (120, 124, 132), "height": 0.02},
        *seams,
        {"type": "rect", "center": (front + 9.5, at_y(11.4)), "size": (5.4, 1.6), "radius": 0.1, "color": ORANGE, "wear": 0.4},
        {"type": "text", "text": "WRECK WORKS", "center": (front + 9.5, at_y(11.38)), "height": 1.0, "color": INK, "font": "impact", "wear": 0.35},
        {"type": "text", "text": "BOILER No. 1", "center": (front - 9.5, at_y(11.4)), "height": 0.9, "color": INK, "font": "impact", "wear": 0.4},
        {"type": "text", "text": "MAX 250 PSI", "center": (front, at_y(15.4)), "height": 0.7, "color": RED, "font": "impact", "wear": 0.35},
    ])


def stack_material():
    return Material("metal", color=(70, 68, 66), rough=0.6, polish=0.2, dirt=0.75, dirt_color=(26, 22, 20), scratches=0.2)


def gauge(face_mat, rim_mat):
    rim = sh.lathe([(0.0, 0.0), (0.62, 0.0), (0.66, 0.14), (0.56, 0.2), (0.0, 0.2)], 12, rim_mat, smooth_angle=40)
    face = sh.lathe([(0.0, 0.19), (0.54, 0.19), (0.0, 0.2)], 12, face_mat, smooth_angle=40)
    stem = sh.cylinder(0.08, 1.6, rim_mat, bevel=0.0, segments=6).transformed(T(0, -0.8, 0))
    return [rim, face, stem]


def valve(mat):
    parts = [sh.torus(0.55, 0.06, mat, segments=12, sides=4)]
    for ang in (0, 60, 120):
        parts.append(sh.box((1.05, 0.06, 0.06), mat).transformed(R(0, ang, 0)))
    return parts


def build():
    a = Asset("FactoryBoiler", budget=6000, atlas=1024, ao_radius=1.6, edge_width=0.12, preview_radius=14.5,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 16), ("SIDE", 270, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=FIRE)

    concrete = Material("concrete", color=(120, 120, 118), dirt=0.6, decals=[
        {"type": "stripes", "center": (0.0, -8.5), "size": (17.6, 0.5), "width": 0.4, "color": YELLOW, "wear": 0.5},
    ])
    a.add("Body", sh.rounded_box((17.6, 1.0, 17.6), 0.08, 1, concrete, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 0.5, 0)))
    a.add("Body", sh.lathe(vessel_profile(), 24, vessel_material(), smooth_angle=30, r_ref=VESSEL_R))

    stack = stack_material()
    a.add("Body", sh.lathe([(0.0, 19.6), (1.5, 19.6), (1.35, 20.2), (1.3, STACK_TOP - 0.6), (1.55, STACK_TOP - 0.4), (1.55, STACK_TOP), (1.2, STACK_TOP), (1.2, STACK_TOP - 0.3)], 14, stack, smooth_angle=35))
    soot = Material("metal", color=(24, 22, 22), rough=0.9, polish=0.0, dirt=0.2)
    a.add("Body", sh.lathe([(1.2, STACK_TOP - 0.3), (0.0, STACK_TOP - 0.3)], 14, soot, smooth_angle=30))
    band = Material("paint", color=ORANGE, under=STEEL, wear=0.5, scratches=0.4, rough=0.45, dirt=0.6, skin=False)
    for y in (21.6, 23.4):
        a.add("Body", sh.lathe([(1.3, y - 0.2), (1.45, y - 0.2), (1.45, y + 0.2), (1.3, y + 0.2)], 14, band, closed=True, smooth_angle=30))

    iron = Material("metal", color=(54, 54, 58), rough=0.55, polish=0.3, dirt=0.6, scratches=0.3)
    box_face = Material("metal", color=(54, 54, 58), rough=0.55, polish=0.3, dirt=0.6, decals=[
        {"type": "rivets", "points": [(x, y) for x in (-2.3, 2.3) for y in np.linspace(-2.2, 2.2, 7)] + [(x, y) for x in np.linspace(-1.5, 1.5, 5) for y in (-2.3, 2.3)], "radius": 0.08, "color": (90, 90, 96), "height": 0.02},
        {"type": "text", "text": "FIREBOX", "center": (0.0, 1.8), "height": 0.4, "color": ORANGE, "font": "impact", "wear": 0.4},
    ])
    a.add("Body", sh.rounded_box((5.2, 5.2, 2.4), 0.12, 1, iron, faces=["+x", "-x", "+y", "-y", "-z"], face_mats={"-z": box_face}).transformed(T(0, 4.0, -VESSEL_R - 0.6)))
    door = sh.lathe([(0.0, 0.0), (1.5, 0.0), (1.55, 0.12), (1.4, 0.24), (0.0, 0.24)], 14, iron, smooth_angle=40)
    a.add("Body", door.transformed(compose(T(0, 3.6, -VESSEL_R - 1.8), R(-90, 0, 0))))
    a.add("Glow", sh.box((2.2, 0.7, 0.05), None).transformed(T(0, 3.95, -VESSEL_R - 2.06)))
    a.add("Glow", sh.box((3.6, 0.35, 0.05), None).transformed(T(0, 1.75, -VESSEL_R - 1.82)))
    a.add("Body", sh.sweep([(-0.9, 3.0, -VESSEL_R - 2.1), (0.0, 2.85, -VESSEL_R - 2.35), (0.9, 3.0, -VESSEL_R - 2.1)], 0.08, 5, Material("metal", color=(180, 184, 190), rough=0.3, polish=0.7, dirt=0.3)))

    rim = Material("metal", color=(180, 150, 70), rough=0.3, polish=0.7, dirt=0.4)
    for k, x in enumerate((-2.8, -0.9)):
        face = Material("plastic", color=(236, 232, 220), rough=0.3, decals=[
            {"type": "circle", "center": (0.0, 0.0), "radius": 0.5, "outline": 0.03, "color": INK, "wear": 0.0},
            {"type": "rect", "center": (0.12, -0.08), "size": (0.38, 0.04), "angle": 40 + k * 60, "color": RED, "wear": 0.0},
            {"type": "rect", "center": (0.0, 0.3), "size": (0.5, 0.08), "color": RED, "wear": 0.0},
        ])
        a.add("Body", [part.transformed(compose(T(x, 11.0, -VESSEL_R - 0.75), R(-90, 0, 0))) for part in gauge(face, rim)])

    pipe = Material("paint", color=ORANGE, under=STEEL, wear=0.5, scratches=0.4, rough=0.45, dirt=0.6, skin=False)
    red = Material("paint", color=RED, under=STEEL, wear=0.4, scratches=0.35, rough=0.4, dirt=0.4, skin=False)
    for sx in (-1, 1):
        x = sx * 7.6
        path = [(x, 1.0, 0.0), (x, 15.0, 0.0), (x, 17.3, 0.0), (sx * 6.6, 18.4, 0.0), (sx * 4.6, 18.9, 0.0)]
        a.add("Body", sh.sweep(path, 0.62, 8, pipe, samples=14))
        for y in (1.5, 9.8):
            a.add("Body", sh.cylinder(0.85, 0.3, pipe, bevel=0.03, segments=10).transformed(T(x, y, 0.0)))
        a.add("Body", [part.transformed(compose(T(x + sx * 0.75, 10.0, 0.0), R(0, 0, 90))) for part in valve(red)])
        a.add("Body", sh.cylinder(0.12, 0.6, red, bevel=0.0, segments=6).transformed(compose(T(x + sx * 0.45, 10.0, 0.0), R(0, 0, 90))))

    a.add("Body", sh.sweep([(0.0, 7.0, VESSEL_R - 0.4), (0.0, 7.0, 8.4)], 0.95, 10, pipe))
    a.add("Body", sh.cylinder(1.3, 0.35, pipe, bevel=0.04, segments=12).transformed(compose(T(0, 7.0, 8.5), R(90, 0, 0))))

    yellow = Material("paint", color=YELLOW, under=STEEL, wear=0.45, scratches=0.35, rough=0.4, dirt=0.45, skin=False)
    lx = 3.2
    lz = np.sqrt(VESSEL_R ** 2 - lx ** 2) + 0.5
    for dx in (-0.5, 0.5):
        a.add("Body", sh.box((0.1, 17.6, 0.1), yellow).transformed(T(lx + dx, 9.8, lz)))
    for y in np.arange(1.8, 18.4, 0.9):
        a.add("Body", sh.box((1.0, 0.07, 0.07), yellow).transformed(T(lx, y, lz)))
    for y in (8.0, 11.0, 14.0, 17.0):
        hoop = sh.lathe([(0.66, -0.04), (0.72, -0.04), (0.72, 0.04), (0.66, 0.04)], 8, yellow, closed=True, arc=200, start=-190, smooth_angle=50)
        a.add("Body", hoop.transformed(T(lx, y, lz + 0.1)))

    destructible(a, "Industrial")
    collider(a, "Hitbox", (12.4, 19.0, 12.4), (0, 10.4, 0), shape="Cylinder")
    collider(a, "Foundation", (17.6, 1.0, 17.6), (0, 0.5, 0))
    collider(a, "Stack", (3.0, STACK_TOP - 19.6, 3.0), (0, (STACK_TOP + 19.6) / 2, 0), shape="Cylinder")
    collider(a, "Firebox", (5.2, 5.2, 2.4), (0, 4.0, -VESSEL_R - 0.6))
    return a
