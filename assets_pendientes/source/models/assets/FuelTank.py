import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

WHITE = (226, 228, 232)
RED = (232, 52, 44)
YELLOW = (255, 210, 31)
INK = (20, 20, 24)
STEEL = (130, 134, 142)

TANK_R = 4.3
TANK_Y0 = 2.4
TANK_Y1 = 10.4
DOME_TOP = 11.3
PAD_R = 4.9


def tank_profile():
    pts = [(0.0, TANK_Y0 - 0.25), (2.2, TANK_Y0 - 0.15), (3.8, TANK_Y0), (TANK_R, TANK_Y0 + 0.3)]
    for y in (4.9, 7.6):
        pts += [(TANK_R, y - 0.08), (TANK_R + 0.06, y), (TANK_R, y + 0.08)]
    pts += [(TANK_R, TANK_Y1), (3.9, TANK_Y1 + 0.35), (2.8, TANK_Y1 + 0.7), (1.4, DOME_TOP - 0.08), (0.0, DOME_TOP)]
    return pts


def profile_v(profile):
    pts = np.asarray(profile)
    arc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    return arc[-1] - arc, arc[-1]


def tank_material():
    v, total = profile_v(tank_profile())
    ring = 2 * np.pi * TANK_R
    front = np.pi / 2 * TANK_R
    def at_y(y):
        pts = np.asarray(tank_profile())
        wall = pts[:, 0] >= TANK_R - 0.01
        return float(np.interp(y, pts[wall, 1], v[wall]))
    decals = [
        {"type": "rect", "center": (ring / 2, at_y(7.6)), "size": (ring + 0.4, 1.2), "color": RED, "wear": 0.35},
        {"type": "stripes", "center": (ring / 2, at_y(7.6)), "size": (ring + 0.4, 1.2), "width": 0.55, "color": WHITE, "wear": 0.35},
        {"type": "rect", "center": (front, at_y(5.6)), "size": (2.2, 2.2), "angle": 45, "color": RED, "wear": 0.25},
        {"type": "rect", "center": (front, at_y(5.6)), "size": (2.2, 2.2), "angle": 45, "outline": 0.08, "color": WHITE, "wear": 0.25},
        {"type": "text", "text": "FLAMMABLE", "center": (front, at_y(5.55)), "height": 0.32, "color": WHITE, "font": "impact", "wear": 0.2},
        {"type": "text", "text": "3", "center": (front, at_y(5.0)), "height": 0.38, "color": WHITE, "font": "impact", "wear": 0.2},
        {"type": "text", "text": "DIESEL", "center": (front + 4.6, at_y(9.2)), "height": 0.9, "color": INK, "font": "impact", "wear": 0.3},
        {"type": "text", "text": "TANK  B-02", "center": (front + 4.6, at_y(3.6)), "height": 0.4, "color": INK, "font": "black", "wear": 0.3},
        {"type": "text", "text": "NO SMOKING", "center": (front - 4.6, at_y(9.2)), "height": 0.45, "color": RED, "font": "impact", "wear": 0.3},
        {"type": "rect", "center": (front + 2.2, at_y(4.2)), "size": (0.5, 3.6), "radius": 0.08, "color": (40, 44, 52), "wear": 0.1},
        {"type": "rect", "center": (front + 2.2, at_y(3.6)), "size": (0.24, 2.2), "color": (230, 150, 40), "wear": 0.05},
    ]
    return Material("paint", color=WHITE, under=STEEL, wear=0.35, scratches=0.35, rough=0.4, dirt=0.5, dirt_color=(78, 64, 48), skin=False, decals=decals)


def build():
    a = Asset("FuelTank", budget=3000, atlas=1024, ao_radius=1.0, edge_width=0.08, preview_radius=7.4,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 60, 50))

    concrete = Material("concrete", color=(140, 140, 138), dirt=0.55, decals=[
        {"type": "stripes", "center": (np.pi * PAD_R, PAD_R - 0.4), "size": (2 * np.pi * PAD_R + 0.4, 0.4), "width": 0.3, "color": YELLOW, "wear": 0.5},
    ])
    a.add("Body", sh.lathe([(0.0, 0.0), (PAD_R, 0.0), (PAD_R, 0.3), (PAD_R - 0.15, 0.42), (0.0, 0.42)], 20, concrete, smooth_angle=35))
    a.add("Body", sh.lathe(tank_profile(), 20, tank_material(), smooth_angle=30, start=0, r_ref=TANK_R))

    steel = Material("metal", color=STEEL, rough=0.4, polish=0.4, dirt=0.55, scratches=0.35)
    yellow = Material("paint", color=YELLOW, under=STEEL, wear=0.45, scratches=0.35, rough=0.4, dirt=0.45, skin=False)
    for k in range(4):
        ang = np.radians(45 + k * 90)
        x, z = np.cos(ang) * 3.1, np.sin(ang) * 3.1
        a.add("Body", sh.cylinder(0.24, 2.2, steel, bevel=0.03, segments=8).transformed(T(x, 1.4, z)))
        a.add("Body", sh.cylinder(0.42, 0.12, steel, bevel=0.02, segments=8).transformed(T(x, 0.48, z)))
        nx, nz = np.cos(ang + np.pi / 2) * 3.1, np.sin(ang + np.pi / 2) * 3.1
        a.add("Body", sh.sweep([(x, 0.6, z), (nx, 2.2, nz)], 0.07, 4, steel))

    ladder_x = TANK_R + 0.45
    for dz in (-0.45, 0.45):
        a.add("Body", sh.box((0.1, DOME_TOP + 0.6, 0.1), yellow).transformed(T(ladder_x, (DOME_TOP + 0.6) / 2 + 0.2, dz)))
    for y in np.arange(1.0, DOME_TOP, 0.9):
        a.add("Body", sh.box((0.07, 0.07, 0.9), yellow).transformed(T(ladder_x, y, 0.0)))
    for y in (5.0, 7.2, 9.4):
        hoop = sh.lathe([(0.62, -0.04), (0.68, -0.04), (0.68, 0.04), (0.62, 0.04)], 8, yellow, closed=True, arc=200, start=-100, smooth_angle=50)
        a.add("Body", hoop.transformed(T(ladder_x + 0.05, y, 0.0)))

    rail_y = DOME_TOP + 0.7
    ring = [(np.cos(t) * 3.0, rail_y, np.sin(t) * 3.0) for t in np.linspace(0, 2 * np.pi, 19)]
    a.add("Body", sh.sweep(ring, 0.06, 4, yellow, closed=False))
    for k in range(6):
        t = k * np.pi / 3 + 0.3
        x, z = np.cos(t) * 3.0, np.sin(t) * 3.0
        base_y = float(np.interp(3.0, [1.4, 2.8], [DOME_TOP - 0.08, TANK_Y1 + 0.7]))
        a.add("Body", sh.box((0.08, rail_y - base_y, 0.08), yellow).transformed(T(x, (rail_y + base_y) / 2, z)))

    a.add("Body", sh.cylinder(0.75, 0.35, steel, bevel=0.04, segments=12).transformed(T(-1.2, DOME_TOP + 0.05, 0.6)))
    a.add("Body", sh.cylinder(0.14, 1.2, steel, bevel=0.0, segments=8).transformed(T(1.0, DOME_TOP + 0.5, -0.8)))
    a.add("Body", sh.lathe([(0.0, 0.0), (0.3, 0.0), (0.26, 0.1), (0.0, 0.22)], 8, steel, smooth_angle=40).transformed(T(1.0, DOME_TOP + 1.1, -0.8)))
    a.add("Glow", sh.sphere(0.3, None, 8, 5).transformed(T(2.0, rail_y + 0.25, 2.0)))
    a.add("Body", sh.cylinder(0.2, 0.5, steel, bevel=0.0, segments=8).transformed(T(2.0, rail_y - 0.1, 2.0)))

    pipe_z = -TANK_R + 0.2
    a.add("Body", sh.sweep([(-2.2, 3.1, pipe_z + 0.4), (-2.2, 3.1, pipe_z - 0.6), (-2.2, 2.4, pipe_z - 1.0), (-2.2, 0.5, pipe_z - 1.1)], 0.28, 8, steel, samples=10))
    valve = Material("paint", color=RED, under=STEEL, wear=0.4, scratches=0.35, rough=0.4, dirt=0.35, skin=False)
    a.add("Body", sh.torus(0.5, 0.06, valve, segments=12, sides=4).transformed(compose(T(-2.2, 3.1, pipe_z - 0.55), R(90, 0, 0))))
    for ang in (0, 60, 120):
        a.add("Body", sh.box((0.9, 0.06, 0.06), valve).transformed(compose(T(-2.2, 3.1, pipe_z - 0.55), R(0, 0, ang))))

    destructible(a, "Industrial")
    collider(a, "Hitbox", (8.8, DOME_TOP - 0.2, 8.8), (0, (DOME_TOP + 0.2) / 2 + 0.3, 0), shape="Cylinder")
    collider(a, "Pad", (PAD_R * 2, 0.42, PAD_R * 2), (0, 0.21, 0), shape="Cylinder")
    return a
