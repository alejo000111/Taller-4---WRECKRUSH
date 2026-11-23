import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import VERDANT, expedition_asset
from _landmark_lib import patch

L, H, D = 29.0, 2.0, 3.0


def build():
    a = expedition_asset("WindRotor", 400, 16.0, atlas=256)
    blade = Material("paint", color=(239, 183, 95), under=(120, 110, 100), wear=0.45, scratches=0.4, rough=0.45, dirt=0.4, skin=False, decals=[
        {"type": "rect", "center": (x, 0.0), "size": (1.2, 4.0), "color": (200, 60, 40), "wear": 0.3} for x in (-12.5, 12.5)
    ])
    hub = Material("metal", color=(70, 74, 72), rough=0.4, polish=0.4, dirt=0.4)
    for side in (-1, 1):
        pts = [(0.8, -0.5), (L / 2 - 0.3, -0.25), (L / 2, 0.0), (L / 2 - 0.3, 0.35), (0.8, 0.9)]
        outline = [(side * x, y) for x, y in pts]
        if side < 0:
            outline = outline[::-1]
        wing = sh.extrude(np.asarray(outline), 0.35, blade, bevel=0.0, corner_radius=0.0, smooth_angle=30)
        a.add("Body", wing.transformed(T(0, 0.0, 0.2)))
    a.add("Body", sh.lathe([(0.0, -1.5), (1.0, -1.2), (1.0, 0.8), (0.6, 1.4), (0.0, 1.5)], 10, hub, smooth_angle=40).transformed(R(90, 0, 0)))
    patch(a, [VERDANT], ["WindRotor"])
    return a
