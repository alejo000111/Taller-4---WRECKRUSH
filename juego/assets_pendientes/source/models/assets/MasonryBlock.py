import numpy as np

from wr3d import Material, T
from wr3d import shapes as sh
from _expedition_lib import SKY, expedition_asset, jagged
from _temple_lib import marble
from _landmark_lib import patch


def build():
    a = expedition_asset("MasonryBlock", 300, 6.0, atlas=256)
    stone = Material("paint", color=(142, 138, 154), under=(110, 106, 120), wear=0.4, scratches=0.5, rough=0.5, dirt=0.5, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (6.0, 2.4), "outline": 0.15, "color": (110, 104, 126), "wear": 0.3},
        {"type": "rect", "center": (0.0, 0.0), "size": (1.6, 1.6), "radius": 0.8, "outline": 0.15, "color": (110, 104, 126), "wear": 0.3},
    ])
    block = sh.rounded_box((10.0, 4.0, 5.0), 0.25, 2, stone).transformed(T(0, 2.0, 0))
    a.add("Body", jagged(block, 3, amount=0.03, scale=0.9))
    patch(a, [SKY], ["FallenMasonry"])
    return a
