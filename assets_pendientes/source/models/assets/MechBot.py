import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _future_lib import pearl, graphite, PINK, INK

STEEL_BLUE = (64, 74, 104)
SILVER = (196, 202, 214)
GLASS = (30, 20, 40)


def armor(decals=()):
    return Material("future_panel", color=STEEL_BLUE, panel=4.0, rough=0.3, metal=0.4, dirt=0.2, decals=list(decals))


def silver(decals=()):
    return Material("future_panel", color=SILVER, panel=3.0, rough=0.25, metal=0.6, dirt=0.15, decals=list(decals))


def plate(size, mat, bevel=0.12):
    return sh.rounded_box(size, bevel, 1, mat)


def leg(sx, mats, glow):
    parts = []
    x = sx * 2.1
    parts.append(sh.extrude([(-1.1, 0.0), (1.4, 0.0), (1.1, 0.8), (-0.8, 0.8)], 2.2, mats["armor"], bevel=0.1, corner_radius=0.0).transformed(compose(T(x, 0, -0.3), R(0, 90, 0), S(1, 1, 1))))
    parts.append(sh.sphere(0.5, mats["dark"], 8, 5).transformed(T(x, 1.15, 0.0)))
    parts.append(plate((1.4, 3.6, 1.6), mats["armor"]).transformed(compose(T(x, 3.2, 0.15), R(8, 0, 0))))
    parts.append(plate((1.6, 2.4, 0.4), mats["silver"]).transformed(compose(T(x, 3.4, -0.8), R(8, 0, 0))))
    glow.append(sh.box((0.25, 1.6, 0.05), None).transformed(compose(T(x, 3.4, -1.02), R(8, 0, 0))))
    parts.append(sh.cylinder(0.7, 1.4, mats["dark"], bevel=0.08, segments=10).transformed(compose(T(x, 5.3, 0.0), R(0, 0, 90))))
    parts.append(plate((1.6, 3.0, 1.8), mats["armor"]).transformed(compose(T(x, 7.1, 0.2), R(-6, 0, 0))))
    pistons = mats["silver"]
    parts.append(sh.cylinder(0.12, 2.4, pistons, bevel=0.0, segments=6).transformed(compose(T(x + sx * 0.75, 4.2, 0.6), R(14, 0, 0))))
    return parts


def arm(sx, mats, glow):
    parts = []
    x = sx * 3.8
    parts.append(plate((1.7, 1.9, 2.6), mats["silver"], 0.25).transformed(T(x, 13.0, 0.2)))
    parts.append(sh.cylinder(0.55, 2.4, mats["dark"], bevel=0.05, segments=10).transformed(T(x, 11.0, 0.2)))
    parts.append(plate((1.5, 1.5, 3.6), mats["armor"]).transformed(T(x, 9.3, -0.6)))
    barrel = sh.lathe([(0.0, 0.0), (0.42, 0.0), (0.42, 1.6), (0.32, 1.7), (0.32, 2.2), (0.0, 2.2)], 10, mats["silver"], smooth_angle=40)
    parts.append(barrel.transformed(compose(T(x, 9.3, -2.2), R(-90, 0, 0))))
    glow.append(sh.lathe([(0.26, 2.22), (0.0, 2.22)], 10, None, smooth_angle=40).transformed(compose(T(x, 9.3, -2.2), R(-90, 0, 0))))
    return parts


def build():
    a = Asset("MechBot", budget=3000, atlas=1024, ao_radius=0.9, edge_width=0.07, gradient=0.08, highlight=0.45, preview_radius=9.0,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 16), ("SIDE", 270, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.25)
    a.role("Glow", "neon", color=PINK)

    mats = {"armor": armor(), "silver": silver(), "dark": graphite(panel=3.0)}
    glow = []
    for sx in (-1, 1):
        a.add("Body", leg(sx, mats, glow))
        a.add("Body", arm(sx, mats, glow))

    a.add("Body", plate((5.4, 1.4, 2.6), mats["silver"]).transformed(T(0, 9.2, 0.2)))
    glow.append(sh.box((4.8, 0.18, 0.05), None).transformed(T(0, 9.2, -1.12)))
    chest = armor([
        {"type": "text", "text": "MK-IV", "center": (-1.7, -0.8), "height": 0.4, "color": (220, 224, 236), "font": "impact", "wear": 0.0},
        {"type": "rect", "center": (1.8, -0.8), "size": (1.0, 0.3), "color": PINK, "rough": 0.1, "wear": 0.0},
        {"type": "rect", "center": (0.0, -1.3), "size": (5.0, 0.08), "darken": 0.4, "raise": -0.005},
    ])
    torso = sh.extrude([(-3.0, 0.0), (3.0, 0.0), (3.2, 2.6), (2.6, 3.6), (-2.6, 3.6), (-3.2, 2.6)], 4.2, armor(), bevel=0.15, corner_radius=0.0, cap_mats=[chest, None])
    a.add("Body", torso.transformed(compose(T(0, 9.9, 0.2), R(0, 180, 0))))
    a.add("Glass", sh.rounded_box((3.0, 1.4, 0.2), 0.12, 1, None).transformed(compose(T(0, 12.2, -2.0), R(-12, 0, 0))))
    glow.append(sh.box((2.6, 0.12, 0.05), None).transformed(compose(T(0, 12.95, -2.1), R(-12, 0, 0))))
    pack = silver([{"type": "rect", "center": (0.0, y), "size": (2.6, 0.08), "darken": 0.5, "raise": -0.006} for y in (-0.6, -0.2, 0.2, 0.6)])
    a.add("Body", sh.rounded_box((3.2, 2.6, 1.2), 0.15, 1, mats["silver"], face_mats={"+z": pack}).transformed(T(0, 11.8, 2.8)))
    glow.append(sh.box((2.4, 0.18, 0.05), None).transformed(T(0, 12.4, 3.42)))
    for x in (-0.9, 0.9):
        a.add("Body", sh.cylinder(0.32, 1.4, mats["dark"], bevel=0.04, segments=8).transformed(compose(T(x, 10.8, 3.3), R(0, 0, 0))))

    head = sh.extrude([(-1.0, 0.0), (1.0, 0.0), (1.1, 0.7), (0.7, 1.2), (-0.7, 1.2), (-1.1, 0.7)], 1.8, mats["silver"], bevel=0.12, corner_radius=0.0)
    a.add("Body", head.transformed(T(0, 13.5, 0.2)))
    glow.append(sh.box((1.4, 0.2, 0.05), None).transformed(T(0, 14.2, -0.72)))
    a.add("Body", sh.cylinder(0.05, 1.2, mats["silver"], bevel=0.0, segments=5).transformed(T(0.6, 15.2, 0.6)))
    pod = plate((1.6, 1.3, 2.0), mats["armor"])
    a.add("Body", pod.transformed(T(-3.7, 14.6, 0.6)))
    pod_face = [sh.lathe([(0.18, 0.0), (0.0, 0.0)], 8, None, smooth_angle=40).transformed(compose(T(-3.7 + dx, 14.6 + dy, -0.42), R(-90, 0, 0))) for dx in (-0.4, 0.4) for dy in (-0.3, 0.3)]
    glow.extend(pod_face)

    a.add("Glow", glow)
    destructible(a, "FutureDistrict")
    collider(a, "Hitbox", (6.4, 6.2, 5.0), (0, 11.6, 0.4))
    collider(a, "Legs", (5.8, 8.6, 2.4), (0, 4.3, 0.0))
    collider(a, "Arms", (9.2, 4.0, 3.0), (0, 11.0, 0.0))
    return a
