import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _hall_lib import HALL, hall_asset, gold, dark_metal, square_pillar
from _landmark_lib import landmark, box_collider


def crown(width, height, depth, mat):
    w, h = width / 2, height
    pts = [(-w, 0.0), (w, 0.0), (w, h * 0.55), (w * 0.62, h * 0.3), (w * 0.32, h), (0.0, h * 0.42), (-w * 0.32, h), (-w * 0.62, h * 0.3), (-w, h * 0.55)]
    return sh.extrude(np.asarray(pts), depth, mat, bevel=0.06, corner_radius=0.0)


def build():
    a = hall_asset("HallBoard", 2400, 24.0)
    a.role("Glow", "neon", color=(255, 59, 59))
    steel = dark_metal()
    trim = gold(0.25)
    plaque = Material("paint", color=(22, 23, 28), under=(60, 60, 66), wear=0.1, scratches=0.1, rough=0.35, dirt=0.1, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (20.0, 1.4), "outline": 0.08, "color": (230, 180, 60), "wear": 0.1},
        {"type": "text", "text": "HALL OF WRECKERS", "center": (0.0, 0.05), "height": 0.9, "color": (240, 196, 80), "font": "impact", "wear": 0.1},
    ])
    panel = Material("metal", color=(22, 23, 28), rough=0.4, polish=0.4, dirt=0.15, decals=[
        *[{"type": "rect", "center": (x, y), "size": (0.25, 0.25), "radius": 0.12, "color": (60, 62, 70), "wear": 0.1} for x in (-13.4, 13.4) for y in np.linspace(-17.0, 17.0, 9)],
    ])

    a.add("Body", sh.rounded_box((30.0, 1.6, 7.0), 0.08, 1, steel).transformed(T(0, 0.8, 0)))
    a.add("Body", sh.rounded_box((28.4, 1.2, 6.0), 0.08, 1, steel).transformed(T(0, 2.2, 0.2)))
    a.add("Glow", sh.box((30.1, 0.3, 7.1), None).transformed(T(0, 1.65, 0)))
    a.add("Body", sh.box((22.0, 1.6, 0.1), plaque).transformed(T(0, 0.85, -3.55)))
    a.add("Body", sh.rounded_box((28.0, 36.0, 0.6), 0.05, 1, panel, faces=["-z", "+z", "+x", "-x", "+y", "-y"]).transformed(T(0, 22.0, 0.4)))
    for x in (-14.6, 14.6):
        a.add("Body", [p.transformed(T(x, 2.8, 0.5)) for p in square_pillar(2.0, 38.6, steel)])
        a.add("Body", sh.lathe([(0.0, 0.0), (0.95, 0.0), (1.2, 0.5), (0.6, 1.1), (0.0, 1.4)], 8, trim, smooth_angle=40, start=22.5).transformed(T(x, 41.4, 0.5)))
        a.add("Glow", sh.box((0.3, 32.0, 0.12), None).transformed(T(x, 22.0, -0.95)))
    bezel = steel
    a.add("Body", sh.rounded_box((28.0, 1.0, 1.2), 0.12, 1, bezel).transformed(T(0, 39.5, -0.5)))
    a.add("Body", sh.rounded_box((28.0, 1.0, 1.2), 0.12, 1, bezel).transformed(T(0, 4.5, -0.5)))
    for x in (-13.5, 13.5):
        a.add("Body", sh.rounded_box((1.0, 34.0, 1.2), 0.12, 1, bezel).transformed(T(x, 22.0, -0.5)))
    for y in (39.5, 4.5):
        a.add("Glow", sh.box((26.4, 0.18, 0.1), None).transformed(T(0, y, -1.12)))
    for x in (-13.5, 13.5):
        a.add("Glow", sh.box((0.18, 32.4, 0.1), None).transformed(T(x, 22.0, -1.12)))
    a.add("Body", crown(12.0, 3.0, 1.4, trim).transformed(T(0, 40.0, -0.3)))
    a.add("Glow", sh.box((9.0, 0.3, 1.5), None).transformed(T(0, 40.3, -0.3)))
    for x in (-3.84, 0.0, 3.84):
        a.add("Glow", sh.sphere(0.32, None, 6, 3).transformed(T(x, 43.0 if x == 0.0 else 42.7, -0.3)))
    landmark(a, f"{HALL}/Boards", ["Board_TopDamage", "Board_TopWrecks", "Board_TopRebirths", "Board_TopCash"], fit="box", keep=["Screen"],
             tint={"Glow": "FrameTop"}, colliders=[box_collider("Base", (30.0, 3.0, 7.0), (0, 1.5, 0)), box_collider("Panel", (31.2, 40.0, 2.0), (0, 22.0, 0.3))])
    return a
