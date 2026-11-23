import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _chaos_lib import basalt, obsidian, crystal, VIOLET, PINK

CORE_Y = 15.2
NAVY = (34, 40, 70)


def machine(decals=()):
    return Material("metal", color=NAVY, rough=0.35, polish=0.6, dirt=0.3, scratches=0.3, decals=list(decals))


def build():
    a = Asset("DoomEngine", budget=6000, atlas=1024, ao_radius=1.8, edge_width=0.12, gradient=0.06, highlight=0.45, preview_radius=19.0,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=VIOLET)
    a.role("Pink", "neon", color=PINK)

    stone = basalt(veins=0.82, glow=VIOLET)
    a.add("Body", sh.lathe([(0.0, 0.0), (13.8, 0.0), (13.8, 1.3), (13.0, 1.6), (0.0, 1.6)], 8, stone, smooth_angle=20, start=22.5))
    a.add("Glow", sh.lathe([(13.02, 1.61), (12.4, 1.61)], 8, None, smooth_angle=20, start=22.5))
    a.add("Body", sh.lathe([(0.0, 1.6), (11.5, 1.6), (11.5, 2.2), (11.0, 2.4), (0.0, 2.4)], 8, obsidian(rim_glow=0.2), smooth_angle=20, start=22.5))

    plate = machine([
        {"type": "rivets", "points": [(x, y) for x in np.linspace(-7, 7, 8) for y in (-3.0, 3.0)], "radius": 0.15, "color": (90, 96, 120), "height": 0.03},
        {"type": "rect", "center": (0.0, 0.0), "size": (14.0, 0.3), "darken": 0.4, "raise": -0.008},
    ])
    front = machine([
        {"type": "rect", "center": (0.0, 1.0), "size": (5.0, 0.8), "color": (20, 14, 30), "wear": 0.0},
        {"type": "text", "text": "DOOM ENGINE", "center": (0.0, 1.0), "height": 0.6, "color": PINK, "font": "impact", "wear": 0.0},
        {"type": "stripes", "center": (0.0, -2.6), "size": (14.0, 0.8), "width": 0.5, "color": (255, 210, 31), "wear": 0.3},
    ])
    for rot in (0, 90):
        housing = sh.rounded_box((16.0, 7.0, 6.6), 0.25, 1, machine(), faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"+z": plate, "-z": front if rot == 0 else plate, "+x": plate, "-x": plate})
        a.add("Body", housing.transformed(compose(R(0, rot, 0), T(0, 5.9, 0))))
    a.add("Glow", sh.lathe([(8.3, 3.9), (8.3, 4.2)], 8, None, smooth_angle=20, start=22.5))

    upper = sh.lathe([(0.0, 9.4), (6.4, 9.4), (6.4, 10.6), (5.6, 11.4), (0.0, 11.4)], 12, obsidian(rim_glow=0.25), smooth_angle=30)
    a.add("Body", upper)
    for k in range(6):
        ang = np.radians(k * 60)
        p = np.array([np.cos(ang) * 4.6, 0.0, np.sin(ang) * 4.6])
        bar = sh.lathe([(0.0, 0.0), (0.35, 0.0), (0.3, 8.0), (0.0, 8.2)], 6, machine(), smooth_angle=30)
        a.add("Body", bar.transformed(T(p[0], 11.2, p[2])))
    a.add("Pink", sh.sphere(3.4, None, 14, 9).transformed(T(0, CORE_Y, 0)))
    for k, (rx, rz, r) in enumerate(((75, 10, 5.6), (-65, 40, 6.0), (15, 80, 6.6))):
        a.add("Glow", sh.torus(r, 0.18, None, segments=24, sides=4).transformed(compose(T(0, CORE_Y, 0), R(rx, 0, rz))))

    cap = sh.lathe([(0.0, 19.0), (5.2, 19.0), (5.2, 19.8), (4.0, 20.6), (1.6, 21.0), (0.0, 21.0)], 12, obsidian(rim_glow=0.3), smooth_angle=30)
    a.add("Body", cap)
    spire = sh.lathe([(0.0, 0.0), (0.9, 0.0), (0.6, 2.0), (0.2, 3.4), (0.0, 3.6)], 6, machine(), smooth_angle=30)
    a.add("Body", spire.transformed(T(0, 21.0, 0)))
    a.add("Pink", crystal(0.5, 1.6, None, facets=5).transformed(T(0, 25.1, 0)))
    for x in (-1.4, 1.4):
        a.add("Body", sh.cylinder(0.1, 3.0, machine(), bevel=0.0, segments=5).transformed(compose(T(x, 22.4, 0), R(0, 0, -x * 10))))

    for k in range(4):
        ang = np.radians(45 + 90 * k)
        d = np.array([np.cos(ang), 0.0, np.sin(ang)])
        p = d * 10.4
        a.add("Body", sh.rounded_box((3.0, 4.0, 3.0), 0.2, 1, machine()).transformed(compose(T(p[0], 4.4, p[2]), R(0, -np.degrees(ang), 0))))
        a.add("Body", sh.cylinder(0.8, 8.6, Material("metal", color=(190, 196, 210), rough=0.15, polish=0.9, dirt=0.15), bevel=0.0, segments=10).transformed(T(p[0], 10.6, p[2])))
        a.add("Glow", sh.cylinder(1.1, 0.6, None, bevel=0.05, segments=10).transformed(T(p[0], 15.2, p[2])))
        arm_end = d * 5.0 + np.array([0, 17.4, 0])
        a.add("Body", sh.sweep([tuple(p + np.array([0, 15.6, 0])), tuple(arm_end)], 0.38, 6, machine()))
        if k == 3:
            continue
        side_ang = np.radians(90 * k)
        s = np.array([np.cos(side_ang), 0.0, np.sin(side_ang)])
        stack = s * 12.2
        a.add("Body", sh.lathe([(0.0, 0.0), (1.1, 0.0), (1.0, 5.6), (1.25, 5.9), (1.25, 6.4), (0.9, 6.4), (0.9, 6.0), (0.0, 6.0)], 10, machine(), smooth_angle=40).transformed(T(stack[0], 1.6, stack[2])))
        a.add("Glow", sh.lathe([(0.9, 7.6), (0.0, 7.6)], 10, None, smooth_angle=40).transformed(T(stack[0], 0.0, stack[2])))
    a.add("Pink", sh.box((3.4, 0.4, 0.1), None).transformed(T(0, 5.9, -3.36)))

    destructible(a, "ChaosCore")
    collider(a, "Hitbox", (16.4, 9.6, 16.4), (0, 4.8, 0))
    collider(a, "Foundation", (27.6, 2.4, 27.6), (0, 1.2, 0), shape="Cylinder")
    collider(a, "Core", (8.0, 10.6, 8.0), (0, 15.6, 0), shape="Cylinder")
    collider(a, "Spire", (2.0, 4.4, 2.0), (0, 23.2, 0), shape="Cylinder")
    return a
