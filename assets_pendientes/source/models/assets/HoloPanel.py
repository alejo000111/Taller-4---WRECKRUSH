import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _future_lib import pearl, graphite, CYAN, INK

SCREEN_W = 6.4
SCREEN_H = 5.2
SCREEN_Y = 6.0


def screen_material():
    bars = []
    for k, h in enumerate((0.9, 1.6, 1.2, 2.1, 1.4, 1.8)):
        x = -2.4 + k * 0.62
        bars.append({"type": "rect", "center": (x, 1.6 - h / 2), "size": (0.4, h), "color": CYAN, "rough": 0.1, "wear": 0.0})
    ring = [
        {"type": "circle", "center": (1.75, 0.6), "radius": 1.05, "outline": 0.12, "color": CYAN, "wear": 0.0},
        {"type": "circle", "center": (1.75, 0.6), "radius": 0.7, "outline": 0.06, "color": (120, 240, 255), "wear": 0.0},
        {"type": "text", "text": "87%", "center": (1.75, 0.62), "height": 0.4, "color": (200, 250, 255), "font": "impact", "wear": 0.0},
    ]
    lines = [{"type": "rect", "center": (-1.2, -1.2 + k * 0.32), "size": (2.4 - 0.3 * (k % 3), 0.08), "color": (90, 200, 230), "wear": 0.0} for k in range(5)]
    return Material("screen", color=(8, 16, 26), decals=bars + ring + lines + [
        {"type": "text", "text": "SECTOR 5 // ONLINE", "center": (0.0, -2.15), "height": 0.36, "color": CYAN, "font": "impact", "wear": 0.0},
        {"type": "rect", "center": (0.0, -1.85), "size": (5.8, 0.04), "color": CYAN, "wear": 0.0},
    ])


def build():
    a = Asset("HoloPanel", budget=1500, atlas=512, ao_radius=0.5, edge_width=0.04, gradient=0.08, highlight=0.4, preview_radius=5.6,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("FRONT", 180, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=CYAN)

    base = sh.extrude([(-3.1, 0.0), (3.1, 0.0), (3.1, 0.4), (2.8, 0.75), (-2.8, 0.75), (-3.1, 0.4)], 1.9, pearl(), bevel=0.05, corner_radius=0.0)
    a.add("Body", base)
    for sx in (-1, 1):
        pylon = sh.extrude([(-0.35, 0.0), (0.35, 0.0), (0.25, 9.0), (-0.25, 9.0)], 0.7, pearl(), bevel=0.06, corner_radius=0.0)
        a.add("Body", pylon.transformed(T(sx * 3.5, 0.6, 0)))
        a.add("Glow", sh.box((0.08, 7.6, 0.72), None).transformed(T(sx * 3.5, 4.9, 0)))
    frame = graphite()
    a.add("Body", sh.rounded_box((SCREEN_W + 0.4, SCREEN_H + 0.4, 0.4), 0.08, 1, frame, face_mats={"-z": screen_material()}).transformed(T(0, SCREEN_Y, 0.05)))
    back = pearl(decals=[
        {"type": "text", "text": "WR-HOLO", "center": (0.0, 0.0), "height": 0.6, "color": (150, 156, 170), "font": "impact", "wear": 0.0},
        {"type": "rect", "center": (0.0, 1.8), "size": (5.0, 0.6), "radius": 0.1, "darken": 0.3, "raise": -0.006},
    ])
    a.add("Body", sh.rounded_box((SCREEN_W - 0.4, SCREEN_H - 0.6, 0.4), 0.12, 1, pearl(), face_mats={"+z": back}).transformed(T(0, SCREEN_Y, 0.42)))
    a.add("Glow", sh.box((SCREEN_W + 0.5, 0.1, 0.1), None).transformed(T(0, SCREEN_Y - SCREEN_H / 2 - 0.25, -0.18)))
    a.add("Glow", sh.box((SCREEN_W + 0.5, 0.1, 0.1), None).transformed(T(0, SCREEN_Y + SCREEN_H / 2 + 0.25, -0.18)))
    emitter = sh.rounded_box((1.6, 0.4, 0.6), 0.1, 1, graphite())
    a.add("Body", emitter.transformed(T(0, 9.55, 0)))
    a.add("Body", sh.box((7.2, 0.25, 0.4), pearl()).transformed(T(0, 9.6, 0)))
    a.add("Glow", sh.box((1.2, 0.06, 0.4), None).transformed(T(0, 9.8, 0)))
    holo = sh.extrude([(-0.9, 0.0), (0.9, 0.0), (0.2, 1.4), (-0.2, 1.4)], 0.02, None, bevel=0.0, corner_radius=0.0)
    a.add("Glow", holo.transformed(T(0, 9.8, 0)))
    a.add("Glow", sh.box((5.4, 0.06, 1.0), None).transformed(T(0, 0.77, 0)))

    destructible(a, "FutureDistrict")
    collider(a, "Hitbox", (SCREEN_W + 0.4, SCREEN_H + 0.4, 0.9), (0, SCREEN_Y, 0.2))
    collider(a, "Frame", (7.6, 9.9, 0.8), (0, 4.95, 0))
    return a
