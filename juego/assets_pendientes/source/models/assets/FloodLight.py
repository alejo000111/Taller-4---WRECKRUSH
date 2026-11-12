import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _station_lib import steel, painted, YELLOW, INK

TOP = 18.0


def build():
    a = Asset("FloodLight", budget=1000, atlas=512, ao_radius=0.4, edge_width=0.04, preview_radius=10.0,
              views=[("FRONT 3/4", 215, 10), ("BACK 3/4", 35, 14), ("SIDE", 270, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 244, 210))
    a.meta["scatter"] = {
        "target": ["Zones/ScrapYard/FloodLights", "Zones/Industrial/FloodLights"],
        "key": "FloodPole",
        "remove": ["FloodPole", "FloodHead", "FloodBulb"],
        "radius": 4.0,
        "face": "FloodHead",
        "tint": {},
        "colliders": [{"name": "Pole", "shape": "Cylinder", "size": [1.0, TOP, 1.0], "center": [0.0, TOP / 2, 0.0], "rotation": [0.0, 0.0, 0.0]}],
    }

    concrete = Material("concrete", color=(140, 138, 132), dirt=0.6, decals=[
        {"type": "stripes", "center": (np.pi * 1.2, 0.5), "size": (2 * np.pi * 1.2 + 0.4, 0.5), "width": 0.3, "color": YELLOW, "wear": 0.5},
    ])
    a.add("Body", sh.lathe([(0.0, 0.0), (1.2, 0.0), (1.2, 1.2), (1.0, 1.4), (0.0, 1.4)], 8, concrete, smooth_angle=30, start=22.5, r_ref=1.2))
    mast = steel((70, 72, 78))
    a.add("Body", sh.lathe([(0.0, 1.3), (0.36, 1.3), (0.26, TOP - 1.2), (0.0, TOP - 1.2)], 6, mast, smooth_angle=30))
    for y in np.arange(3.0, TOP - 2.0, 1.2):
        a.add("Body", sh.box((0.6, 0.06, 0.06), steel((120, 120, 124))).transformed(T(0, y, 0.32)))
    frame = steel((40, 42, 48))
    a.add("Body", sh.box((5.0, 0.3, 0.3), frame).transformed(T(0, TOP - 1.0, 0)))
    for x in (-1.8, 0.0, 1.8):
        place = compose(T(x, TOP - 0.2, -0.3), R(-35, 0, 0))
        a.add("Body", sh.rounded_box((1.5, 1.0, 0.7), 0.08, 1, frame).transformed(place))
        a.add("Glow", sh.box((1.3, 0.8, 0.05), None).transformed(compose(place, T(0, 0, -0.37))))
    box = painted((60, 64, 70), [{"type": "rect", "center": (0.0, -0.2), "size": (0.5, 0.5), "angle": 45, "color": YELLOW, "wear": 0.3}])
    a.add("Body", sh.rounded_box((0.9, 1.2, 0.5), 0.05, 1, box).transformed(T(0, 4.2, 0.55)))
    return a
