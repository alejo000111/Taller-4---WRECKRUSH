import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _station_lib import steel, painted, YELLOW, INK

POLE_TOP = 17.6


def build():
    a = Asset("PlazaLamp", budget=1200, atlas=512, ao_radius=0.4, edge_width=0.04, preview_radius=9.5,
              views=[("FRONT 3/4", 215, 10), ("BACK 3/4", 35, 14), ("SIDE", 270, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 160, 60))
    a.meta["scatter"] = {
        "target": "Plaza/Lamps",
        "key": "LampPole",
        "remove": ["LampPole", "LampBase", "LampHead"],
        "radius": 4.0,
        "tint": {"Glow": "LampHead"},
        "colliders": [{"name": "Pole", "shape": "Cylinder", "size": [0.9, POLE_TOP, 0.9], "center": [0.0, POLE_TOP / 2, 0.0], "rotation": [0.0, 0.0, 0.0]}],
    }

    base = painted((34, 36, 42), [
        {"type": "stripes", "center": (np.pi * 1.25, 0.9), "size": (2 * np.pi * 1.25 + 0.4, 0.5), "width": 0.25, "color": YELLOW, "wear": 0.3},
    ])
    a.add("Body", sh.lathe([(0.0, 0.0), (1.25, 0.0), (1.25, 0.8), (1.0, 1.0), (0.7, 1.6), (0.5, 1.8), (0.0, 1.8)], 8, base, smooth_angle=30, start=22.5, r_ref=1.25))
    pole = steel((40, 42, 48))
    a.add("Body", sh.lathe([(0.0, 1.7), (0.42, 1.7), (0.32, POLE_TOP - 0.4), (0.4, POLE_TOP - 0.2), (0.4, POLE_TOP), (0.0, POLE_TOP)], 8, pole, smooth_angle=30))
    for y in (6.0, 11.0):
        a.add("Body", sh.lathe([(0.36, y - 0.15), (0.48, y - 0.15), (0.48, y + 0.15), (0.36, y + 0.15)], 8, painted(YELLOW), closed=True, smooth_angle=30))
    for k in range(2):
        ang = k * 180
        arm = sh.sweep([(0.0, POLE_TOP - 0.8, 0.0), (1.4, POLE_TOP - 0.2, 0.0), (2.6, POLE_TOP - 0.3, 0.0)], 0.12, 5, pole, samples=7)
        a.add("Body", arm.transformed(R(0, ang, 0)))
        head = sh.lathe([(0.0, 0.0), (0.3, 0.0), (0.85, -0.4), (0.8, -0.55), (0.0, -0.35)], 10, steel((30, 32, 38)), smooth_angle=40)
        a.add("Body", head.transformed(compose(R(0, ang, 0), T(2.8, POLE_TOP - 0.2, 0))))
        a.add("Glow", sh.lathe([(0.75, -0.52), (0.0, -0.4)], 10, None, smooth_angle=40).transformed(compose(R(0, ang, 0), T(2.8, POLE_TOP - 0.2, 0))))
    banner = Material("canvas", stripes=[(255, 122, 26)], stripe_width=1.0, axis=0, dirt=0.25, decals=[
        {"type": "text", "text": "WRECK", "center": (0.0, -0.6), "height": 0.55, "color": (20, 20, 24), "font": "impact", "wear": 0.15, "angle": 90},
        {"type": "text", "text": "RUSH", "center": (0.0, 0.6), "height": 0.55, "color": (20, 20, 24), "font": "impact", "wear": 0.15, "angle": 90},
    ])
    flag = sh.rounded_box((0.05, 3.2, 1.2), 0.0, 1, banner, face_mats={"+x": banner, "-x": banner})
    a.add("Body", flag.transformed(T(0.0, 13.2, 0.85)))
    a.add("Body", sh.cylinder(0.05, 1.4, steel((150, 150, 156)), bevel=0.0, segments=5).transformed(compose(T(0.0, 14.85, 0.75), R(90, 0, 0))))
    a.add("Glow", sh.lathe([(1.27, 0.25), (1.27, 0.45)], 8, None, smooth_angle=30, start=22.5))
    return a
