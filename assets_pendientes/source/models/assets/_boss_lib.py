import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider, animate


def boss_asset(name, budget, eye, core):
    a = Asset(name, budget=budget, atlas=1024, ao_radius=1.0, ao_strength=0.6, edge_width=0.08, gradient=0.1, highlight=0.5, preview_radius=22.0,
              views=[("FRONT 3/4", 215, 12), ("FRONT", 180, 4), ("SIDE", 270, 6), ("BACK 3/4", 35, 16)])
    a.role("Body", "surface")
    a.role("ArmL", "surface")
    a.role("ArmR", "surface")
    a.role("Eyes", "neon", color=eye)
    a.role("Core", "neon", color=core)
    destructible(a, "Event")
    collider(a, "Hitbox", (24.0, 24.0, 24.0), (0.0, 12.0, 0.0))
    animate(a, "ArmL", "Arm")
    animate(a, "ArmR", "Arm")
    animate(a, "Core", "Core")
    return a


def skeleton(a, armor, joint, dark, trim=None):
    trim = trim or joint
    for side in (-1, 1):
        x = side * 6.0
        a.add("Body", sh.rounded_box((9.0, 3.0, 12.0), 0.5, 1, armor).transformed(T(x, 1.5, -3.0)))
        a.add("Body", sh.rounded_box((7.0, 1.0, 4.0), 0.3, 1, dark).transformed(T(x, 0.5, -9.4)))
        a.add("Body", sh.lathe([(0.0, 0.0), (2.6, 0.0), (3.0, 1.5), (2.4, 6.5), (2.9, 7.6), (2.4, 9.0), (0.0, 9.0)], 10, joint, smooth_angle=35).transformed(T(x, 3.0, 0.0)))
        a.add("Body", sh.rounded_box((6.6, 4.6, 7.4), 0.6, 1, armor).transformed(T(x, 6.4, -0.4)))
    a.add("Body", sh.lathe([(0.0, 6.0), (8.5, 6.0), (8.8, 7.2), (8.0, 11.2), (6.8, 12.0), (0.0, 12.0)], 16, dark, smooth_angle=35))
    for k in range(8):
        ang = k * 45.0
        a.add("Body", sh.box((1.0, 3.6, 0.8), trim).transformed(compose(R(0, ang, 0), T(0, 9.0, -8.6))))
    a.add("Body", sh.rounded_box((19.0, 12.0, 13.0), 1.6, 2, armor).transformed(T(0, 16.0, 0)))
    a.add("Body", sh.rounded_box((16.0, 3.0, 11.0), 1.0, 1, joint).transformed(T(0, 22.4, 0.4)))
    for side in (-1, 1):
        a.add("Body", sh.rounded_box((6.0, 5.0, 9.0), 1.6, 1, armor).transformed(compose(T(side * 10.6, 20.4, 0), R(0, 0, side * -14))))


def head(a, shell, visor_mat, y=25.0):
    a.add("Body", sh.rounded_box((14.0, 5.0, 10.0), 1.4, 2, shell).transformed(T(0, y, 0)))
    a.add("Body", sh.rounded_box((11.0, 2.2, 0.6), 0.3, 1, visor_mat).transformed(T(0, y, -5.0)))
    for side in (-1, 1):
        a.add("Eyes", sh.box((3.0, 1.1, 0.4), None).transformed(T(side * 3.5, y, -5.35)))


def core_gear(a, y=17.0, z=-6.8, radius=3.0, mat=None):
    teeth = 10
    pts = []
    for k in range(teeth * 2):
        ang = 2 * np.pi * k / (teeth * 2)
        r = radius if k % 2 == 0 else radius * 0.82
        pts.append((np.cos(ang) * r, np.sin(ang) * r))
    gear = sh.extrude(np.asarray(pts), 1.0, None, bevel=0.0, corner_radius=0.0, smooth_angle=20)
    a.add("Core", gear.transformed(T(0, y, z)))
    if mat is not None:
        a.add("Body", sh.lathe([(radius + 0.3, -0.7), (radius + 1.0, -0.7), (radius + 1.0, 0.7), (radius + 0.3, 0.7)], 16, mat, closed=True, smooth_angle=30).transformed(compose(T(0, y, z + 0.4), R(90, 0, 0))))


def arm(a, role, side, armor, joint, hand):
    sx = side
    shoulder = sh.lathe([(0.0, -3.4), (2.8, -3.0), (3.6, 0.0), (2.8, 3.0), (0.0, 3.4)], 10, joint, smooth_angle=40)
    a.add(role, shoulder.transformed(compose(T(sx * 13.4, 21.0, 0), R(0, 0, 90))))
    upper = sh.rounded_box((6.0, 8.0, 7.0), 1.2, 1, armor)
    a.add(role, upper.transformed(compose(T(sx * 15.0, 17.0, 0), R(0, 0, sx * 11.5))))
    a.add(role, sh.lathe([(0.0, 0.0), (2.2, 0.0), (2.4, 1.0), (2.0, 4.0), (0.0, 4.0)], 8, joint, smooth_angle=40).transformed(T(sx * 16.0, 9.6, 0)))
    a.add(role, hand.transformed(T(sx * 16.4, 8.6, 0)))
