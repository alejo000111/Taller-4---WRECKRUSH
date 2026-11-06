import numpy as np

from wr3d import Material
from _backdrop_lib import backdrop_asset, heightfield, noise2, peaks

W, D, H = 300.0, 220.0, 330.0


def build():
    a = backdrop_asset("VerdantPeak", 2600, 220.0)
    rock = Material("terrain_rock", color=(86, 96, 80), cap=(58, 92, 56), cap_amount=0.95, strata=0.1, dirt=0.2)

    def shape(x, z):
        base = peaks(x, z, 31, count=4, sharp=0.9)
        detail = 0.06 * noise2(x * 4.0, z * 4.0, 31 + 3)
        return np.clip(base + detail * (base > 0.02), 0, None) * H

    a.add("Body", heightfield(W, D, 22, 16, rock, shape))
    a.meta["ring"] = [{"parent": "Backdrop", "centers": [[0.000000, -2880.000000]], "radius": 470.0, "count": 16, "scale": [0.8, 1.25], "seed": 41, "sink": -140.0, "offset": 0.0}, {"parent": "Backdrop", "centers": [[0.000000, -2880.000000]], "radius": 690.0, "count": 18, "scale": [1.05, 1.5], "seed": 141, "sink": -165.0, "offset": 0.5}]
    return a
