import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

YELLOW = (255, 210, 31)
INK = (20, 18, 16)
SIZE = 18.4
HALF = 10.0


def planks(decals=()):
    seams = [{"type": "rect", "center": (0.0, -SIZE / 2 + k * SIZE / 8), "size": (SIZE, 0.08), "darken": 0.55, "raise": -0.01} for k in range(1, 8)]
    return Material("wood", color=(176, 124, 72), axis="x", ring_freq=6.0, dirt=0.4, decals=seams + list(decals))


def front_decals():
    return [
        {"type": "rect", "center": (0.0, -2.4), "size": (14.4, 3.8), "radius": 0.3, "color": (24, 22, 20), "wear": 0.35},
        {"type": "text", "text": "MEGA LOOT", "center": (0.0, -2.35), "height": 2.7, "color": YELLOW, "font": "impact", "wear": 0.35},
        {"type": "text", "text": "FRAGILE - HANDLE WITH TNT", "center": (0.0, 1.4), "height": 0.8, "color": INK, "font": "impact", "wear": 0.45},
        {"type": "rect", "center": (3.6, 5.2), "size": (4.0, 2.6), "radius": 0.15, "color": (236, 230, 210), "wear": 0.3},
        {"type": "text", "text": "SHIP TO: YOU", "center": (3.6, 4.8), "height": 0.5, "color": INK, "font": "black", "wear": 0.3},
        *[{"type": "rect", "center": (3.6, 5.5 + k * 0.28), "size": (3.0, 0.1), "color": INK, "wear": 0.3} for k in range(3)],
    ]


def side_decals():
    return [
        {"type": "text", "text": "WR-LOOT", "center": (0.0, -5.6), "height": 2.4, "color": INK, "font": "impact", "wear": 0.5},
        {"type": "rect", "center": (-5.4, 5.4), "size": (3.0, 3.0), "angle": 45, "color": YELLOW, "wear": 0.4},
        {"type": "text", "text": "!", "center": (-5.4, 5.46), "height": 2.0, "color": INK, "font": "black", "wear": 0.3},
    ]


def build():
    a = Asset("GiantCrate", budget=2500, atlas=1024, ao_radius=2.0, edge_width=0.12, preview_radius=15.0,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("FRONT", 180, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=YELLOW)

    core = sh.rounded_box((SIZE, SIZE, SIZE), 0.0, 1, planks(), face_mats={
        "-z": planks(front_decals()), "+z": planks(front_decals()), "+x": planks(side_decals()), "-x": planks(side_decals()),
        "+y": Material("wood", color=(170, 118, 68), axis="z", ring_freq=6.0, dirt=0.45, decals=[{"type": "rect", "center": (-SIZE / 2 + k * SIZE / 8, 0.0), "size": (0.08, SIZE), "darken": 0.55, "raise": -0.01} for k in range(1, 8)]),
    })
    a.add("Body", core.transformed(T(0, HALF, 0)))

    frame = Material("wood", color=(110, 70, 40), axis="y", dirt=0.45)
    frame_x = Material("wood", color=(110, 70, 40), axis="x", dirt=0.45)
    frame_z = Material("wood", color=(110, 70, 40), axis="z", dirt=0.45)
    for sx in (-1, 1):
        for sz in (-1, 1):
            a.add("Body", sh.rounded_box((1.6, 20.0, 1.6), 0.1, 1, frame, faces=["+x", "-x", "+z", "-z"]).transformed(T(sx * 9.2, HALF, sz * 9.2)))
    for y in (0.8, 19.2):
        for sz in (-1, 1):
            a.add("Body", sh.rounded_box((16.8, 1.6, 1.6), 0.0, 1, frame_x, faces=["+y", "-y", "+z", "-z"]).transformed(T(0, y, sz * 9.2)))
        for sx in (-1, 1):
            a.add("Body", sh.rounded_box((1.6, 1.6, 16.8), 0.0, 1, frame_z, faces=["+y", "-y", "+x", "-x"]).transformed(T(sx * 9.2, y, 0)))
    for sx in (-1, 1):
        brace = sh.box((0.6, 23.6, 1.2), frame)
        a.add("Body", brace.transformed(compose(T(sx * 9.45, HALF, 0), R(45 if sx > 0 else -45, 0, 0))))

    strap = Material("paint", color=YELLOW, under=(120, 122, 128), wear=0.45, scratches=0.4, rough=0.45, dirt=0.4, skin=False, decals=[
        {"type": "rivets", "points": [(0.0, y) for y in np.linspace(-8.5, 8.5, 7)], "radius": 0.18, "color": (150, 150, 150), "height": 0.03},
    ])
    for x in (-7.7, 7.7):
        for sz in (-1, 1):
            a.add("Body", sh.box((1.4, 18.4, 0.3), strap).transformed(T(x, HALF, sz * 9.35)))
        a.add("Body", sh.box((1.4, 0.3, 18.4), strap).transformed(T(x, 19.35, 0)))

    metal = Material("metal", color=(40, 40, 44), rough=0.4, polish=0.5, dirt=0.4)
    for sx in (-1, 1):
        for sz in (-1, 1):
            a.add("Body", sh.box((2.2, 0.5, 2.2), metal).transformed(T(sx * 9.2, 20.2, sz * 9.2)))
            a.add("Glow", sh.box((1.6, 0.2, 1.6), None).transformed(T(sx * 9.2, 20.55, sz * 9.2)))
            a.add("Body", sh.box((2.2, 0.4, 2.2), metal).transformed(T(sx * 9.2, 0.2, sz * 9.2)))

    destructible(a, "Event")
    collider(a, "Hitbox", (20.0, 20.0, 20.0), (0, HALF, 0))
    return a
