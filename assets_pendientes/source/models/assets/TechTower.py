import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _future_lib import pearl, graphite, VIOLET, CYAN, INK

CORE = 11.0
CORE_Y0 = 2.1
CORE_Y1 = 38.1
CROWN_Y = 38.1
SPIRE_Y = 42.0


def glass_material():
    out = []
    for f in range(12):
        y = -18.0 + f * 3.0
        out.append({"type": "rect", "center": (0.0, y), "size": (11.2, 0.18), "color": (20, 24, 34), "wear": 0.0})
        for k in range(5):
            if (f * 3 + k * 5) % 7 < 3:
                out.append({"type": "rect", "center": (-4.4 + k * 2.2, y + 1.5), "size": (1.8, 1.6), "color": (90, 70, 150), "rough": 0.1, "wear": 0.0})
    return Material("glossy", color=(18, 20, 32), rough=0.08, metal=0.3, dirt=0.05, decals=out)


def build():
    a = Asset("TechTower", budget=6000, atlas=1024, ao_radius=2.0, edge_width=0.12, gradient=0.06, highlight=0.4, preview_radius=24.0,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 16), ("FRONT", 180, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=VIOLET)
    a.role("Cyan", "neon", color=CYAN)

    dark = graphite(panel=4.0)
    plinth = graphite(panel=4.0, decals=[
        {"type": "text", "text": "WRECK TECH", "center": (0.0, -0.1), "height": 0.7, "color": (210, 214, 230), "font": "impact", "wear": 0.0},
    ])
    a.add("Body", sh.rounded_box((18.0, 1.5, 18.0), 0.1, 1, dark, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"-z": plinth}).transformed(T(0, 0.75, 0)))
    a.add("Body", sh.rounded_box((15.0, 0.6, 15.0), 0.08, 1, pearl(panel=4.0), faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 1.8, 0)))
    a.add("Glow", sh.box((15.2, 0.1, 15.2), None).transformed(T(0, 2.13, 0)))

    glass = glass_material()
    a.add("Body", sh.rounded_box((CORE, CORE_Y1 - CORE_Y0, CORE), 0.0, 1, glass, faces=["+x", "-x", "+z", "-z"]).transformed(T(0, (CORE_Y0 + CORE_Y1) / 2, 0)))
    column = pearl(panel=5.0, decals=[{"type": "rect", "center": (0.0, y), "size": (2.0, 0.06), "darken": 0.3, "raise": -0.004} for y in np.linspace(-16, 16, 9)])
    for sx in (-1, 1):
        for sz in (-1, 1):
            col = sh.extrude([(-0.8, -0.8), (0.8, -0.8), (0.8, 0.8), (-0.8, 0.8)], CORE_Y1 - CORE_Y0 + 1.0, column, bevel=0.15, corner_radius=0.0)
            a.add("Body", col.transformed(compose(T(sx * 5.5, (CORE_Y0 + CORE_Y1 + 1.0) / 2, sz * 5.5), R(90, 0, 0))))
    for side in range(4):
        rot = R(0, side * 90, 0)
        for x in (-1.8, 1.8):
            a.add("Glow", sh.box((0.25, CORE_Y1 - CORE_Y0 - 3.0, 0.12), None).transformed(compose(rot, T(x, (CORE_Y0 + CORE_Y1) / 2 + 0.5, -CORE / 2 - 0.06))))
    for y in (11.0, 20.0, 29.0):
        a.add("Body", sh.rounded_box((11.6, 0.6, 11.6), 0.06, 1, pearl(panel=5.0)).transformed(T(0, y, 0)))
        a.add("Glow", sh.box((11.7, 0.1, 11.7), None).transformed(T(0, y - 0.32, 0)))

    crown = sh.lathe([(0.0, 0.0), (9.2, 0.0), (9.2, 0.8), (7.4, 2.4), (6.0, 3.0), (0.0, 3.0)], 4, pearl(panel=5.0), smooth_angle=10, start=45)
    a.add("Body", crown.transformed(T(0, CROWN_Y, 0)))
    a.add("Glow", sh.lathe([(9.22, 0.15), (9.22, 0.6)], 4, None, smooth_angle=10, start=45).transformed(T(0, CROWN_Y, 0)))
    spire = sh.lathe([(0.0, 0.0), (1.2, 0.0), (0.9, 1.0), (0.35, 3.0), (0.12, 4.6), (0.0, 4.8)], 8, dark, smooth_angle=40)
    a.add("Body", spire.transformed(T(0, SPIRE_Y - 1.0, 0)))
    a.add("Cyan", sh.sphere(0.4, None, 8, 5).transformed(T(0, SPIRE_Y + 3.9, 0)))
    a.add("Glow", sh.torus(2.4, 0.12, None, segments=16, sides=4).transformed(compose(T(0, SPIRE_Y + 0.4, 0), R(8, 0, 0))))
    a.add("Glow", sh.torus(1.6, 0.1, None, segments=14, sides=4).transformed(compose(T(0, SPIRE_Y + 1.6, 0), R(-10, 0, 0))))

    door = Material("screen", color=(10, 20, 30), decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (0.06, 4.0), "color": CYAN, "wear": 0.0},
        {"type": "text", "text": "ENTER", "center": (0.0, -1.5), "height": 0.4, "color": CYAN, "font": "impact", "wear": 0.0},
    ])
    a.add("Body", sh.rounded_box((4.0, 4.0, 0.2), 0.0, 1, door, faces=["-z"]).transformed(T(0, 4.1, -CORE / 2 - 0.12)))
    a.add("Cyan", sh.box((4.4, 0.15, 0.15), None).transformed(T(0, 6.2, -CORE / 2 - 0.2)))
    for x in (-2.2, 2.2):
        a.add("Cyan", sh.box((0.15, 4.0, 0.15), None).transformed(T(x, 4.1, -CORE / 2 - 0.2)))
    canopy = sh.extrude([(-3.2, 0.0), (3.2, 0.0), (2.8, 0.4), (-2.8, 0.4)], 2.4, pearl(panel=5.0), bevel=0.05, corner_radius=0.0)
    a.add("Body", canopy.transformed(T(0, 6.5, -CORE / 2 - 1.1)))

    destructible(a, "FutureDistrict")
    collider(a, "Hitbox", (12.6, CORE_Y1 - CORE_Y0, 12.6), (0, (CORE_Y0 + CORE_Y1) / 2, 0))
    collider(a, "Plinth", (18.0, 2.1, 18.0), (0, 1.05, 0))
    collider(a, "Crown", (13.0, 3.0, 13.0), (0, CROWN_Y + 1.5, 0))
    collider(a, "Spire", (2.4, 5.0, 2.4), (0, SPIRE_Y + 1.5, 0), shape="Cylinder")
    return a
