import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _landmark_lib import landmark, box_collider
from _station_lib import steel
import _city_lib

W = 12.6
H = 80.0
FLOOR = 4.0


def windows(width, height, seed, lit=0.45):
    rng = np.random.default_rng(seed)
    out = []
    cols = 4
    rows = int(height / FLOOR)
    for r in range(rows):
        for c in range(cols):
            x = -width / 2 + (c + 0.5) * width / cols
            y = height / 2 - (r + 0.55) * FLOOR
            on = rng.random() < lit
            out.append({"type": "rect", "center": (x, y), "size": (width / cols - 0.9, FLOOR * 0.55), "radius": 0.08,
                        "color": (255, 214, 140) if on else (34, 44, 62), "rough": 0.1, "metal": 0.0, "wear": 0.0})
        out.append({"type": "rect", "center": (0.0, height / 2 - r * FLOOR), "size": (width, 0.18), "color": (200, 196, 186), "wear": 0.2})
    return out


def build():
    a = Asset("CityHighrise", budget=1500, atlas=1024, ao_radius=1.5, edge_width=0.1, preview_radius=44.0,
              views=[("FRONT 3/4", 215, 8), ("BACK 3/4", 35, 12), ("FRONT", 180, 4), ("TOP", 200, 45)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 60, 40))

    shaft_h = H - 8.0
    faces = {}
    for k, f in enumerate(("+x", "-x", "+z", "-z")):
        faces[f] = Material("city_brick", color=(140, 70, 52), mortar=(170, 160, 150), brick=(1.0, 0.4), gap=0.05, wear=0.25, soot=0.35, dirt=0.4, decals=windows(W - 1.0, shaft_h, 10 + k))
    base = Material("city_stone", color=(70, 72, 80), dirt=0.4, decals=[
        {"type": "rect", "center": (0.0, 0.6), "size": (W - 3.0, 4.6), "color": (40, 60, 80), "rough": 0.1, "wear": 0.0},
        {"type": "rect", "center": (0.0, -2.3), "size": (W - 1.0, 0.8), "color": (255, 196, 40), "wear": 0.1},
    ])
    a.add("Body", sh.rounded_box((W, 8.0, W), 0.0, 1, base, faces=["+x", "-x", "+z", "-z", "+y"]).transformed(T(0, 4.0, 0)))
    a.add("Body", sh.rounded_box((W - 1.0, shaft_h, W - 1.0), 0.0, 1, faces["+x"], faces=["+x", "-x", "+z", "-z"], face_mats=faces).transformed(T(0, 8.0 + shaft_h / 2, 0)))
    stone = Material("city_stone", color=(196, 190, 176), dirt=0.4)
    for y in (8.0, 8.0 + shaft_h * 0.5):
        a.add("Body", sh.rounded_box((W + 0.2, 0.6, W + 0.2), 0.05, 1, stone).transformed(T(0, y, 0)))
    for sx in (-1, 1):
        for sz in (-1, 1):
            a.add("Body", sh.box((0.9, shaft_h, 0.9), stone).transformed(T(sx * (W - 1.0) / 2, 8.0 + shaft_h / 2, sz * (W - 1.0) / 2)))
    crown = sh.extrude([(-W / 2 - 0.4, -W / 2 - 0.4), (W / 2 + 0.4, -W / 2 - 0.4), (W / 2 + 0.4, W / 2 + 0.4), (-W / 2 - 0.4, W / 2 + 0.4)], 1.2, stone, bevel=0.1, corner_radius=0.0)
    a.add("Body", crown.transformed(compose(T(0, H - 0.6, 0), R(90, 0, 0))))
    a.add("Body", sh.rounded_box((5.0, 2.4, 5.0), 0.1, 1, steel((70, 72, 80))).transformed(T(1.5, H + 1.2, -1.5)))
    a.add("Body", sh.cylinder(0.12, 8.0, steel((80, 82, 88)), bevel=0.0, segments=5).transformed(T(-3.0, H + 4.0, 3.0)))
    a.add("Glow", sh.sphere(0.4, None, 8, 4).transformed(T(-3.0, H + 8.2, 3.0)))
    landmark(a, "Zones/Downtown/Landmarks", "Facade", fit="box", colliders=[box_collider("Tower", (W, H, W), (0, H / 2, 0))])
    return a
