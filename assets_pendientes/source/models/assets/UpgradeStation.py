import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _station_lib import station, collider, platform, sign_face, steel, painted, YELLOW, INK

RED = (255, 59, 59)
HOT = (255, 140, 40)
MACHINE_Z = 2.0


def gear(radius, teeth, depth, mat):
    pts = []
    for k in range(teeth):
        a0 = 2 * np.pi * k / teeth
        step = 2 * np.pi / teeth
        for t, r in ((0.0, radius - depth), (0.18, radius), (0.5, radius), (0.68, radius - depth)):
            ang = a0 + t * step
            pts.append((np.cos(ang) * r, np.sin(ang) * r))
    return sh.extrude(pts, 0.7, mat, bevel=0.06, corner_radius=0.0)


def anvil(mat):
    side = [(-2.5, 0.0), (1.4, 0.0), (1.6, 0.35), (2.6, 0.55), (2.5, 0.75), (1.6, 0.9), (-1.4, 0.9), (-1.8, 0.75), (-1.5, 0.4)]
    body = sh.extrude(side, 2.0, mat, bevel=0.06, corner_radius=0.0)
    return body


def build():
    a = Asset("UpgradeStation", budget=4500, atlas=1024, ao_radius=0.9, edge_width=0.07, preview_radius=8.6,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("FRONT", 180, 6), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=RED)
    a.role("Hot", "neon", color=HOT)
    station(a, "UpgradeStation")
    platform(a, RED)

    shell = painted((52, 54, 62))
    front = painted((52, 54, 62), [
        {"type": "rect", "center": (0.0, 0.2), "size": (6.0, 3.0), "radius": 0.15, "color": (14, 16, 20), "wear": 0.0},
        {"type": "text", "text": "UPGRADES", "center": (0.0, -0.3), "height": 0.9, "color": RED, "font": "impact", "wear": 0.0},
        *[{"type": "rect", "center": (-1.8 + k * 0.9, 0.9), "size": (0.6, 0.18 + 0.12 * k), "color": (255, 210, 31) if k < 3 else (255, 255, 255), "wear": 0.0} for k in range(5)],
        *[{"type": "rect", "center": (0.0, 2.6 + k * 0.28), "size": (6.0, 0.12), "darken": 0.7, "raise": -0.008} for k in range(3)],
        {"type": "stripes", "center": (0.0, -3.3), "size": (8.0, 0.6), "width": 0.35, "color": YELLOW, "wear": 0.35},
    ])
    a.add("Body", sh.rounded_box((8.0, 7.6, 4.0), 0.2, 1, shell, face_mats={"-z": front}).transformed(T(0, 4.2, MACHINE_Z)))
    a.add("Body", sh.rounded_box((8.6, 0.5, 4.6), 0.08, 1, painted(RED)).transformed(T(0, 8.2, MACHINE_Z)))
    chrome = Material("metal", color=(214, 218, 226), rough=0.12, polish=0.9, dirt=0.15)
    for sx in (-1, 1):
        x = sx * 4.6
        a.add("Body", sh.cylinder(0.65, 4.4, painted(RED), bevel=0.06, segments=12).transformed(T(x, 2.6, MACHINE_Z)))
        a.add("Body", sh.cylinder(0.32, 3.6, chrome, bevel=0.0, segments=10).transformed(T(x, 6.2, MACHINE_Z)))
        a.add("Body", sh.cylinder(0.75, 0.4, steel(), bevel=0.05, segments=12).transformed(T(x, 8.2, MACHINE_Z)))
        a.add("Body", sh.sweep([(x, 1.0, MACHINE_Z + 0.6), (x + sx * 0.3, 0.8, MACHINE_Z + 1.6), (sx * 3.0, 0.5, MACHINE_Z + 2.2)], 0.12, 5, Material("rubber", color=(22, 22, 24), pattern="ribs", freq=14.0), samples=6))

    dark = steel((44, 46, 52))
    g = gear(3.2, 14, 0.5, dark)
    a.add("Body", g.transformed(T(0, 10.6, MACHINE_Z)))
    a.add("Glow", sh.cylinder(1.6, 0.8, None, bevel=0.0, segments=14).transformed(compose(T(0, 10.6, MACHINE_Z), R(90, 0, 0))))
    a.add("Body", sh.cylinder(0.8, 1.0, chrome, bevel=0.08, segments=10).transformed(compose(T(0, 10.6, MACHINE_Z), R(90, 0, 0))))
    a.add("Body", sh.box((1.0, 2.2, 1.0), dark).transformed(T(0, 9.0, MACHINE_Z)))
    small = gear(1.4, 9, 0.35, painted(YELLOW))
    a.add("Body", small.transformed(compose(T(3.2, 9.3, MACHINE_Z - 0.1), R(0, 0, 10))))

    stump = Material("wood", color=(110, 70, 40), axis="y", dirt=0.5)
    a.add("Body", sh.cylinder(1.4, 1.6, stump, bevel=0.08, segments=10).transformed(T(0, 1.0, -2.6)))
    iron = Material("metal", color=(60, 62, 70), rough=0.35, polish=0.7, dirt=0.3, scratches=0.4)
    a.add("Body", anvil(iron).transformed(T(0, 1.8, -2.6)))
    a.add("Hot", sh.rounded_box((2.2, 0.3, 0.5), 0.08, 1, None).transformed(compose(T(-0.2, 2.86, -2.6), R(0, 12, 0))))
    hammer_head = steel((90, 94, 104))
    handle = Material("wood", color=(120, 74, 44), axis="y", dirt=0.3)
    a.add("Body", sh.cylinder(0.12, 2.4, handle, bevel=0.0, segments=6).transformed(compose(T(1.6, 1.4, -4.1), R(0, 0, -60))))
    a.add("Body", sh.rounded_box((0.5, 0.9, 0.5), 0.06, 1, hammer_head).transformed(compose(T(2.6, 0.75, -4.1), R(0, 0, -60))))

    collider(a, "Machine", (9.4, 8.4, 4.6), (0, 4.4, MACHINE_Z))
    collider(a, "Anvil", (5.2, 3.0, 2.4), (0, 1.6, -2.6))
    return a
