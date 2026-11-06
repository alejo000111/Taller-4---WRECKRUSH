import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import FROST, expedition_asset
from _landmark_lib import landmark, box_collider

L, W = 86.0, 33.0


def hull_section(width, height, z):
    w = width / 2
    return [(-w * 0.72, 0.0), (w * 0.72, 0.0), (w, height * 0.45), (w, height), (-w, height), (-w, height * 0.45)]


def build():
    a = expedition_asset("Icebreaker", 3200, 50.0, atlas=1024, front=270)
    a.role("Glow", "neon", color=(129, 207, 230))
    hull = Material("paint", color=(44, 69, 91), under=(120, 110, 100), wear=0.45, scratches=0.4, rough=0.45, dirt=0.45, skin=False, decals=[
        {"type": "rect", "center": (0.0, 5.5), "size": (200.0, 2.2), "color": (180, 40, 36), "wear": 0.4},
        {"type": "text", "text": "WR ICEBREAKER", "center": (-20.0, -2.0), "height": 2.2, "color": (230, 236, 240), "font": "impact", "wear": 0.4},
    ])
    deck = Material("wood", color=(150, 110, 70), dirt=0.45)
    white = Material("paint", color=(175, 191, 199), under=(110, 110, 116), wear=0.3, scratches=0.3, rough=0.4, dirt=0.35, skin=False)
    steel = Material("metal", color=(70, 78, 86), rough=0.4, polish=0.4, dirt=0.4)
    body = sh.extrude(np.asarray(hull_section(W, 14.0, 0)), L - 14.0, hull, bevel=0.0, corner_radius=0.0, smooth_angle=30)
    a.add("Body", body.transformed(T(0, 0, 7.0)))
    for z0, sign in ((-L / 2 + 7.0, -1),):
        bow = []
        for k in range(5):
            t = k / 4
            bow.append(t)
        pts = [(0.0, 0.0), (W / 2 * 0.72, 0.0), (W / 2, 6.3), (W / 2, 14.0), (0.0, 14.0)]
        nose = sh.lathe(pts, 12, hull, smooth_angle=35, arc=180.0, start=90.0)
        a.add("Body", nose.transformed(compose(T(0, 0, z0), R(0, 0, 0), np.diag([1.0, 1.0, 0.95, 1.0]))))
    stern = sh.box((W, 14.0, 0.4), hull).transformed(T(0, 7.0, L / 2 - 0.2))
    a.add("Body", stern)
    a.add("Body", sh.rounded_box((30.0, 3.0, L - 6.0), 0.1, 1, deck, faces=["+y", "+x", "-x", "+z", "-z"]).transformed(T(0, 15.5, 3.0)))
    for x in (-15.2, 15.2):
        a.add("Body", sh.box((0.25, 1.2, L - 10.0), steel).transformed(T(x, 17.6, 3.0)))
    bz = -43.0 + 35.0
    a.add("Body", sh.rounded_box((23.0, 13.0, 26.0), 0.3, 1, white).transformed(T(0, 17.0 + 6.5, bz)))
    a.add("Body", sh.rounded_box((19.0, 4.0, 20.0), 0.3, 1, white).transformed(T(0, 30.0 + 2.0, bz)))
    a.add("Body", sh.box((24.0, 0.6, 27.0), steel).transformed(T(0, 30.2, bz)))
    a.add("Glow", sh.box((0.3, 3.4, 18.0), None).transformed(T(11.65, 27.0, bz)))
    a.add("Glow", sh.box((0.3, 3.4, 18.0), None).transformed(T(-11.65, 27.0, bz)))
    a.add("Body", sh.cylinder(1.6, 8.0, Material("paint", color=(180, 40, 36), under=(100, 100, 100), wear=0.3, rough=0.4, dirt=0.4, skin=False), bevel=0.0, segments=10).transformed(T(0, 38.0, bz + 4.0)))
    a.add("Body", sh.cylinder(0.25, 6.0, steel, bevel=0.0, segments=5).transformed(T(0, 37.0, bz - 6.0)))
    landmark(a, FROST, "Icebreaker", fit="box",
             colliders=[box_collider("Hull", (W, 17.0, L), (0, 8.5, 0)), box_collider("Bridge", (23.0, 17.0, 26.0), (0, 25.5, bz))])
    return a
