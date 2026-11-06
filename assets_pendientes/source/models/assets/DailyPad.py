import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _station_lib import station, collider, platform, sign_face, steel, painted, YELLOW, INK

GOLD = (255, 196, 40)
RED = (226, 40, 52)
BOX_Y = 1.3
BOX = 4.4


def wrapping(decals=()):
    return Material("plastic", color=(255, 206, 60), rough=0.35, scuff=0.2, dirt=0.1, decals=list(decals))


def ribbon_faces(size, vertical=True):
    w = 0.9
    decals = [{"type": "rect", "center": (0.0, 0.0), "size": (w, size + 0.4), "color": RED, "rough": 0.3, "wear": 0.0}]
    if vertical:
        decals.append({"type": "rect", "center": (0.0, 0.0), "size": (size + 0.4, w), "color": RED, "rough": 0.3, "wear": 0.0})
    dots = [{"type": "circle", "center": (x, y), "radius": 0.2, "color": (255, 240, 170), "wear": 0.0} for x in (-1.4, 1.4) for y in (-1.4, 1.4)]
    return decals + dots


def bow_loop(mat, side):
    loop = sh.torus(0.75, 0.24, mat, segments=12, sides=6)
    return loop.transformed(compose(T(side * 0.75, 0.55, 0), R(90, 0, side * 30), S(1.0, 1.0, 0.6)))


def build():
    a = Asset("DailyPad", budget=3000, atlas=1024, ao_radius=0.8, edge_width=0.06, highlight=0.6, preview_radius=6.6,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("FRONT", 180, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=GOLD)
    station(a, "DailyPad")
    platform(a, GOLD)

    pedestal = painted((40, 42, 50), [
        *[{"type": "text", "text": d, "center": (k * 2 * np.pi * 4.5 / 7 + 1.0, 0.25), "height": 0.3, "color": GOLD, "font": "impact", "wear": 0.2} for k, d in enumerate(("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"))],
    ])
    a.add("Body", sh.lathe([(0.0, 0.2), (4.5, 0.2), (4.5, 0.75), (4.2, 0.9), (0.0, 0.9)], 24, pedestal, smooth_angle=35, r_ref=4.5))
    a.add("Glow", sh.lathe([(4.25, 0.91), (3.7, 0.91)], 24, None, smooth_angle=35))
    a.add("Body", sh.lathe([(0.0, 0.9), (3.0, 0.9), (3.0, 1.2), (2.8, 1.3), (0.0, 1.3)], 20, steel((70, 72, 80)), smooth_angle=35))

    side = wrapping(ribbon_faces(BOX, vertical=False))
    top = wrapping(ribbon_faces(BOX, vertical=True))
    box = sh.rounded_box((BOX, BOX - 0.6, BOX), 0.1, 1, wrapping(), faces=["+x", "-x", "+z", "-z"], face_mats={f: side for f in ("+x", "-x", "+z", "-z")})
    a.add("Body", box.transformed(T(0, BOX_Y + (BOX - 0.6) / 2, 0)))
    lid = sh.rounded_box((BOX + 0.3, 0.7, BOX + 0.3), 0.12, 1, wrapping(), faces=["+x", "-x", "+y", "-y", "+z", "-z"], face_mats={"+y": top, "+x": side, "-x": side, "+z": side, "-z": side})
    lid_y = BOX_Y + BOX - 0.6 + 0.3
    a.add("Body", lid.transformed(compose(T(0, lid_y, 0), R(0, 0, 4))))
    ribbon = Material("plastic", color=RED, rough=0.3, scuff=0.1, dirt=0.05)
    a.add("Body", bow_loop(ribbon, -1).transformed(T(0, lid_y + 0.1, 0)))
    a.add("Body", bow_loop(ribbon, 1).transformed(T(0, lid_y + 0.1, 0)))
    a.add("Body", sh.sphere(0.35, ribbon, 8, 5).transformed(T(0, lid_y + 0.55, 0)))
    for side_ in (-1, 1):
        tail = sh.sweep([(0.0, lid_y + 0.4, 0.0), (side_ * 0.5, lid_y + 0.3, -0.6), (side_ * 0.8, lid_y + 0.1, -1.2)], 0.14, 4, ribbon, samples=5, taper=lambda u: 1.0 - 0.3 * u)
        a.add("Body", tail)

    coin = Material("gold", color=GOLD, rough=0.2, dirt=0.05, decals=[{"type": "text", "text": "$", "center": (0.0, 0.0), "height": 0.5, "color": (200, 140, 20), "font": "impact", "wear": 0.0}])
    for k in range(5):
        ang = np.radians(k * 72 + 20)
        p = (np.cos(ang) * 3.6, 1.2 + (k % 2) * 0.12, np.sin(ang) * 3.6)
        a.add("Body", sh.cylinder(0.45, 0.14, coin, bevel=0.03, segments=12).transformed(compose(T(*p), R(10 * (k % 3), k * 40, 0))))

    sign = sh.rounded_box((5.0, 1.2, 0.3), 0.06, 1, steel((40, 42, 50)), face_mats={"-z": sign_face("DAILY GIFT", GOLD, (5.0, 1.2), height=0.7)})
    a.add("Body", sign.transformed(T(0, 0.75, -4.6)))

    collider(a, "Gift", (BOX + 0.3, BOX + 0.6, BOX + 0.3), (0, BOX_Y + (BOX + 0.6) / 2, 0))
    collider(a, "Pedestal", (9.0, 1.3, 9.0), (0, 0.65, 0), shape="Cylinder")
    return a
