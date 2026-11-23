import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

GOLD = (255, 196, 40)
FRAME = (110, 54, 30)


def gold(decals=()):
    return Material("gold", color=GOLD, rough=0.2, scratches=0.2, dirt=0.1, decals=list(decals))


def face_decals():
    return [
        {"type": "circle", "center": (0.0, 0.0), "radius": 1.5, "outline": 0.1, "color": (200, 140, 20), "wear": 0.0, "raise": 0.004},
        {"type": "text", "text": "$", "center": (0.0, 0.05), "height": 2.2, "color": (200, 136, 18), "font": "impact", "wear": 0.0, "raise": 0.006},
        {"type": "rivets", "points": [(x, y) for x in (-2.2, 2.2) for y in (-2.2, 2.2)], "radius": 0.14, "color": (255, 230, 140), "height": 0.03},
    ]


def build():
    a = Asset("GoldCrate", budget=1500, atlas=1024, ao_radius=0.6, edge_width=0.05, gradient=0.08, highlight=0.7, preview_radius=5.0,
              views=[("FRONT 3/4", 215, 18), ("BACK 3/4", 35, 22), ("FRONT", 180, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 220, 90))

    core = sh.rounded_box((5.3, 5.3, 5.3), 0.0, 1, gold(), face_mats={f: gold(face_decals()) for f in ("+x", "-x", "+y", "+z", "-z")})
    a.add("Body", core.transformed(T(0, 3.0, 0)))
    wood = Material("wood", color=FRAME, axis="y", dirt=0.25)
    rail = Material("wood", color=FRAME, axis="x", dirt=0.25)
    rail_z = Material("wood", color=FRAME, axis="z", dirt=0.25)
    for sx in (-1, 1):
        for sz in (-1, 1):
            a.add("Body", sh.rounded_box((0.7, 6.0, 0.7), 0.06, 1, wood, faces=["+x", "-x", "+z", "-z"]).transformed(T(sx * 2.65, 3.0, sz * 2.65)))
    for y in (0.35, 5.65):
        for sz in (-1, 1):
            a.add("Body", sh.rounded_box((4.6, 0.7, 0.7), 0.0, 1, rail, faces=["+y", "-y", "+z", "-z"]).transformed(T(0, y, sz * 2.65)))
        for sx in (-1, 1):
            a.add("Body", sh.rounded_box((0.7, 0.7, 4.6), 0.0, 1, rail_z, faces=["+y", "-y", "+x", "-x"]).transformed(T(sx * 2.65, y, 0)))
    metal = Material("metal", color=(50, 40, 30), rough=0.35, polish=0.6, dirt=0.2)
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in (0.0, 6.0):
                cap = sh.rounded_box((0.9, 0.3, 0.9), 0.0, 1, metal)
                a.add("Body", cap.transformed(T(sx * 2.65, y + (0.12 if y > 0 else 0.15), sz * 2.65)))
    a.add("Glow", sh.box((4.4, 0.06, 4.4), None).transformed(T(0, 0.02, 0)))
    for k in range(3):
        coin = sh.cylinder(0.42, 0.12, gold(), bevel=0.02, segments=12)
        a.add("Body", coin.transformed(compose(T(-1.2 + k * 1.1, 5.72 + 0.12 * k, 0.4 - 0.5 * k), R(4 * k, 30 * k, 0))))

    destructible(a, "Event")
    collider(a, "Hitbox", (6.0, 6.0, 6.0), (0, 3.0, 0))
    return a
