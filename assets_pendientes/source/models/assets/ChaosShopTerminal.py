import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _station_lib import station, collider, platform
from _chaos_lib import basalt, obsidian, rock, grounded, crystal_cluster, VIOLET, PINK

LILAC = (200, 150, 255)


def screen():
    tiles = []
    colors = [VIOLET, PINK, (34, 225, 255), (255, 210, 31), (60, 220, 160), (255, 122, 26)]
    for k in range(6):
        x = -1.1 + (k % 3) * 1.1
        y = -0.15 + (k // 3) * 0.85
        tiles.append({"type": "rect", "center": (x, y), "size": (0.9, 0.7), "radius": 0.08, "outline": 0.05, "color": colors[k], "wear": 0.0})
        tiles.append({"type": "circle", "center": (x, y - 0.05), "radius": 0.18, "color": colors[k], "wear": 0.0})
    return Material("screen", color=(10, 6, 20), decals=tiles + [
        {"type": "text", "text": "CHAOS SHOP", "center": (0.0, -0.95), "height": 0.42, "color": LILAC, "font": "impact", "wear": 0.0},
        {"type": "rect", "center": (0.0, -0.68), "size": (3.4, 0.05), "color": VIOLET, "wear": 0.0},
    ])


def body_side():
    return obsidian(rim_glow=0.3, glow=VIOLET, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (2.2, 5.4), "radius": 0.2, "outline": 0.06, "color": VIOLET, "wear": 0.0},
        {"type": "text", "text": "C", "center": (0.0, -1.0), "height": 1.2, "color": VIOLET, "font": "impact", "wear": 0.0},
    ])


def build():
    a = Asset("ChaosShopTerminal", budget=3000, atlas=1024, ao_radius=0.8, edge_width=0.06, gradient=0.06, highlight=0.45, preview_radius=6.4,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("FRONT", 180, 6), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=LILAC)
    a.role("Crystal", "neon", color=VIOLET)
    station(a, "ChaosShopTerminal")
    platform(a, VIOLET)

    profile = [(-1.0, 0.2), (2.5, 0.2), (2.5, 7.0), (0.4, 7.4), (-0.2, 7.0), (-0.9, 4.0), (-1.6, 3.6), (-1.6, 3.2), (-0.9, 3.0)]
    side_poly = [(z, y) for z, y in profile]
    shell = sh.extrude(np.asarray(side_poly), 4.6, obsidian(rim_glow=0.25), bevel=0.12, corner_radius=0.0, cap_mats=[body_side(), body_side()])
    a.add("Body", shell.transformed(R(0, -90, 0)))
    tilt = np.degrees(np.arctan2(0.7, 3.0))
    ledge = np.degrees(np.arctan2(0.4, 0.7))
    a.add("Body", sh.rounded_box((3.8, 2.9, 0.08), 0.0, 1, screen(), faces=["-z"]).transformed(compose(T(0, 5.5, -0.6), R(tilt, 0, 0))))
    keys = Material("plastic", color=(40, 30, 60), rough=0.3, decals=[
        {"type": "rect", "center": (x, z), "size": (0.5, 0.36), "radius": 0.06, "color": [VIOLET, PINK, LILAC][(k + j) % 3], "wear": 0.0}
        for k, x in enumerate(np.linspace(-1.3, 1.3, 5)) for j, z in enumerate((-0.25, 0.25))
    ])
    a.add("Body", sh.rounded_box((3.6, 0.12, 0.75), 0.0, 1, keys, faces=["+y"]).transformed(compose(T(0, 3.78, -1.25), R(-ledge, 0, 0))))
    a.add("Glow", sh.box((4.8, 0.12, 0.12), None).transformed(T(0, 7.0, -0.25)))
    a.add("Glow", sh.box((4.4, 0.25, 2.4), None).transformed(T(0, 7.42, 1.4)))
    a.add("Glow", sh.box((0.08, 3.6, 0.08), None).transformed(T(-2.35, 5.0, -0.5)))
    a.add("Glow", sh.box((0.08, 3.6, 0.08), None).transformed(T(2.35, 5.0, -0.5)))

    stone = basalt(veins=0.84, glow=VIOLET)
    for sx in (-1, 1):
        a.add("Body", grounded(rock(1.2, stone, 30 + sx, squash=(1.0, 0.5, 1.0), segments=8, rings=4).transformed(T(sx * 4.1, 0.4, 1.4)), 0.2))
        a.add("Crystal", [part.transformed(T(sx * 4.1, 0.6, 1.4)) for part in crystal_cluster(None, 10 + sx, 3, 0.55, 4.2, 0.6)])

    collider(a, "Terminal", (4.6, 7.2, 4.0), (0, 3.8, 0.75))
    for sx in (-1, 1):
        collider(a, f"Crystal{'L' if sx < 0 else 'R'}", (1.8, 4.4, 1.8), (sx * 4.1, 2.4, 1.4))
    return a
