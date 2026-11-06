import numpy as np

from wr3d import Material, T
from wr3d import shapes as sh
from _ground_lib import ground_asset, slab
from _hall_lib import HALL, GOLD
from _landmark_lib import patch

W, L = 12.0, 96.0


def build():
    a = ground_asset("RedCarpet", 300, 50.0, atlas=1024)
    a.role("Glow", "neon", color=GOLD)
    velvet = Material("canvas", stripes=[(126, 22, 32), (112, 18, 28)], stripe_width=0.25, axis=1, dirt=0.25, decals=[
        {"type": "rect", "center": (sx * 5.0, 0.0), "size": (0.3, L - 1.0), "color": (210, 160, 60), "rough": 0.4, "wear": 0.2} for sx in (-1, 1)
    ] + [
        {"type": "rect", "center": (0.0, z), "size": (1.6, 1.6), "angle": 45, "outline": 0.15, "color": (210, 160, 60), "rough": 0.4, "wear": 0.2} for z in np.arange(-44.0, 45.0, 8.0)
    ])
    a.add("Body", slab([(-W / 2, -L / 2), (W / 2, -L / 2), (W / 2, L / 2), (-W / 2, L / 2)], 0.08, velvet))
    for sx in (-1, 1):
        a.add("Glow", sh.box((0.25, 0.1, L), None).transformed(T(sx * (W / 2 - 0.13), 0.05, 0)))
    patch(a, [f"{HALL}/Grounds"], ["Carpet"], remove=["CarpetTrim"], keep_height=True)
    return a
