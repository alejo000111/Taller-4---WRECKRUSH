import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _military_lib import olive, OLIVE, OLIVE_DARK, STENCIL, YELLOW, INK

BODY = (4.4, 3.0, 6.4)
BODY_Y = 0.4 + BODY[1] / 2
LID_Y = 0.4 + BODY[1] + 0.22


def planks(width, rows, height):
    return [{"type": "rect", "center": (0.0, -height / 2 + k * height / rows), "size": (width, 0.035), "darken": 0.55, "raise": -0.006} for k in range(1, rows)]


def side_decals():
    return planks(6.4, 5, 3.0) + [
        {"type": "text", "text": "AMMO 7.62", "center": (0.0, 0.05), "height": 0.62, "color": STENCIL, "font": "impact", "wear": 0.45},
        {"type": "text", "text": "1200 RDS  LINKED", "center": (0.0, 0.62), "height": 0.26, "color": STENCIL, "font": "black", "wear": 0.45},
        {"type": "text", "text": "LOT WR-0719", "center": (1.9, 1.12), "height": 0.2, "color": STENCIL, "font": "black", "wear": 0.5},
    ]


def end_decals():
    return planks(4.4, 5, 3.0) + [
        {"type": "text", "text": "WR-AMMO", "center": (0.0, -0.75), "height": 0.48, "color": STENCIL, "font": "impact", "wear": 0.45},
        {"type": "rect", "center": (0.0, 0.5), "size": (0.95, 0.95), "angle": 45, "color": (240, 120, 30), "wear": 0.35},
        {"type": "text", "text": "1.1", "center": (0.0, 0.5), "height": 0.32, "color": INK, "font": "impact", "wear": 0.3},
    ]


def lid_decals():
    return [
        {"type": "rect", "center": (0.0, z), "size": (4.8, 0.55), "color": YELLOW, "wear": 0.45} for z in (-2.2, 2.2)
    ] + [
        {"type": "text", "text": "THIS SIDE UP", "center": (0.0, 0.0), "height": 0.34, "color": STENCIL, "font": "impact", "wear": 0.5, "angle": 180},
        *[{"type": "rect", "center": (x, 0.0), "size": (0.03, 6.8), "darken": 0.5, "raise": -0.005} for x in (-1.2, 0.0, 1.2)],
    ]


def build():
    a = Asset("AmmoCrate", budget=1200, atlas=512, ao_radius=0.5, edge_width=0.05, preview_radius=4.6,
              views=[("FRONT 3/4", 215, 18), ("BACK 3/4", 35, 22), ("SIDE", 270, 8), ("TOP", 200, 55)])
    a.role("Body", "surface")

    paint = olive()
    crate = sh.rounded_box(BODY, 0.06, 1, paint, faces=["+x", "-x", "+z", "-z"], face_mats={
        "+x": olive(decals=side_decals()), "-x": olive(decals=side_decals()), "+z": olive(decals=end_decals()), "-z": olive(decals=end_decals()),
    })
    a.add("Body", crate.transformed(T(0, BODY_Y, 0)))
    lid = sh.rounded_box((4.8, 0.45, 6.8), 0.06, 1, paint, faces=["+x", "-x", "+y", "-y", "+z", "-z"], face_mats={"+y": olive(decals=lid_decals())})
    a.add("Body", lid.transformed(T(0, LID_Y, 0)))

    wood = Material("wood", color=(96, 74, 48), axis="z", dirt=0.6)
    for x in (-1.5, 1.5):
        a.add("Body", sh.rounded_box((0.7, 0.4, 6.6), 0.04, 1, wood, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(x, 0.2, 0)))

    trim = olive(OLIVE_DARK, wear=0.45)
    for sx in (-1, 1):
        for sz in (-1, 1):
            a.add("Body", sh.box((0.28, BODY[1], 0.28), trim).transformed(T(sx * (BODY[0] / 2 - 0.08), BODY_Y, sz * (BODY[2] / 2 - 0.08))))

    strap = Material("metal", color=(70, 76, 56), rough=0.5, polish=0.3, dirt=0.5, scratches=0.4, decals=[
        {"type": "rivets", "points": [(0.0, y) for y in (-1.2, 0.0, 1.2)], "radius": 0.06, "color": (110, 112, 104), "height": 0.015},
    ])
    for z in (-2.4, 2.4):
        for sx in (-1, 1):
            a.add("Body", sh.box((0.06, BODY[1] + 0.1, 0.36), strap).transformed(T(sx * (BODY[0] / 2 + 0.03), BODY_Y, z)))

    rope = Material("wrap", color=(46, 44, 38), width=0.05, slope=0.8, dirt=0.4)
    for sx in (-1, 1):
        x = sx * (BODY[0] / 2 + 0.05)
        loop = [(x, 3.15, -0.75), (x + sx * 0.3, 2.9, -0.6), (x + sx * 0.36, 2.72, 0.0), (x + sx * 0.3, 2.9, 0.6), (x, 3.15, 0.75)]
        a.add("Body", sh.sweep(loop, 0.06, 4, rope, samples=9))
        for z in (-0.75, 0.75):
            a.add("Body", sh.box((0.08, 0.22, 0.22), strap).transformed(T(x, 3.17, z)))

    latch = Material("metal", color=(120, 122, 116), rough=0.35, polish=0.6, dirt=0.35)
    for x in (-1.3, 1.3):
        a.add("Body", sh.rounded_box((0.6, 0.6, 0.12), 0.03, 1, latch, faces=["+x", "-x", "+y", "-y", "-z"]).transformed(T(x, LID_Y - 0.25, -BODY[2] / 2 - 0.06)))

    destructible(a, "Military")
    collider(a, "Hitbox", (4.8, LID_Y + 0.22, 6.8), (0, (LID_Y + 0.22) / 2, 0))
    return a
