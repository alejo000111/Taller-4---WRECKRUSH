import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _future_lib import pearl, graphite, VIOLET, INK

CORE_Y = 2.3
ARM = 2.15


def build():
    a = Asset("HoverDrone", budget=1500, atlas=512, ao_radius=0.4, edge_width=0.04, gradient=0.08, highlight=0.4, preview_radius=3.6,
              views=[("FRONT 3/4", 215, 18), ("BACK 3/4", 35, 22), ("SIDE", 270, 6), ("TOP", 200, 60)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=VIOLET)
    a.role("Eye", "neon", color=(255, 60, 120))

    shell = pearl(panel=1.8, decals=[
        {"type": "text", "text": "WR-D7", "center": (np.pi / 2 * 1.1 + 1.7, 0.5), "height": 0.22, "color": INK, "font": "impact", "wear": 0.0},
        {"type": "rect", "center": (np.pi / 2 * 1.1 - 1.7, 0.5), "size": (0.6, 0.12), "color": VIOLET, "wear": 0.0},
    ])
    body = sh.lathe([(0.0, -0.75), (0.6, -0.72), (1.05, -0.45), (1.15, 0.0), (1.05, 0.35), (0.7, 0.62), (0.0, 0.72)], 14, shell, smooth_angle=50, r_ref=1.1)
    a.add("Body", body.transformed(T(0, CORE_Y, 0)))
    dark = graphite(panel=2.0)
    a.add("Body", sh.lathe([(0.0, -0.95), (0.55, -0.95), (0.7, -0.7), (0.0, -0.7)], 12, dark, smooth_angle=40).transformed(T(0, CORE_Y, 0)))
    a.add("Glow", sh.lathe([(0.0, -1.0), (0.45, -0.95)], 10, None, smooth_angle=40).transformed(T(0, CORE_Y, 0)))
    a.add("Body", sh.lathe([(0.0, 0.0), (0.5, 0.0), (0.42, 0.18), (0.0, 0.25)], 10, dark, smooth_angle=40).transformed(T(0, CORE_Y + 0.68, 0)))

    eye_mount = compose(T(0, CORE_Y + 0.05, -1.0), R(-90, 0, 0))
    a.add("Body", sh.lathe([(0.0, 0.0), (0.42, 0.0), (0.42, 0.18), (0.32, 0.26), (0.0, 0.26)], 12, dark, smooth_angle=40).transformed(eye_mount))
    a.add("Eye", sh.sphere(0.24, None, 8, 4).transformed(compose(eye_mount, T(0, 0.22, 0))))

    for k in range(4):
        ang = np.radians(45 + 90 * k)
        d = np.array([np.cos(ang), 0.0, np.sin(ang)])
        root = np.array([0, CORE_Y + 0.2, 0]) + d * 0.9
        tip = np.array([0, CORE_Y + 0.45, 0]) + d * ARM
        a.add("Body", sh.sweep([tuple(root), tuple((root + tip) / 2 + np.array([0, 0.12, 0])), tuple(tip)], 0.14, 6, dark, samples=5))
        hub = tip + np.array([0, 0.05, 0])
        ring = sh.lathe([(0.82, -0.18), (0.95, -0.18), (0.95, 0.18), (0.82, 0.18)], 12, pearl(panel=3.2, decals=[{"type": "rect", "center": (3.0, 0.31), "size": (6.4, 0.08), "color": VIOLET, "rough": 0.1, "wear": 0.0}]), closed=True, smooth_angle=35)
        a.add("Body", ring.transformed(T(*hub)))
        a.add("Glow", sh.lathe([(0.8, -0.19), (0.97, -0.19)], 12, None, smooth_angle=35).transformed(T(*hub)))
        a.add("Body", sh.cylinder(0.16, 0.3, dark, bevel=0.0, segments=6).transformed(T(*hub)))
        for b in range(2):
            blade = sh.rounded_box((1.4, 0.03, 0.18), 0.0, 1, dark)
            a.add("Body", blade.transformed(compose(T(*(hub + np.array([0, 0.12, 0]))), R(4, k * 25 + b * 90, 0))))

    for sx in (-1, 1):
        skid = [(sx * 0.55, CORE_Y - 0.6, -0.5), (sx * 0.75, 0.15, -0.6), (sx * 0.75, 0.12, 0.6), (sx * 0.55, CORE_Y - 0.6, 0.5)]
        a.add("Body", sh.sweep(skid, 0.06, 4, dark, samples=8))
    
    grow = compose(T(0, 0.1, 0), S(1.18, 1.18, 1.18))
    for role in a.parts:
        a.parts[role] = [m.transformed(grow) for m in a.parts[role]]

    destructible(a, "FutureDistrict")
    collider(a, "Hitbox", (2.8, 2.8, 2.8), (0, CORE_Y * 1.18 + 0.1, 0), shape="Ball")
    collider(a, "Rotors", (6.4, 0.6, 6.4), ((0, (CORE_Y + 0.5) * 1.18 + 0.1, 0)))
    return a
