import numpy as np

from wr3d import Material
from _backdrop_lib import backdrop_asset, heightfield, noise2, peaks

W, D, H = 200.0, 160.0, 380.0


def build():
    a = backdrop_asset("SkyCrag", 2600, 220.0)
    rock = Material("terrain_rock", color=(92, 88, 118), cap=(168, 150, 220), cap_amount=0.25, strata=0.25, dirt=0.2)

    def shape(x, z):
        base = peaks(x, z, 47, count=5, sharp=1.5)
        detail = 0.06 * noise2(x * 4.0, z * 4.0, 47 + 3)
        return np.clip(base + detail * (base > 0.02), 0, None) * H

    a.add("Body", heightfield(W, D, 22, 16, rock, shape))
    a.meta["ring"] = [{'parent': 'Backdrop', 'centers': [[-2880.0, 0.0]], 'radius': 470.0, 'count': 16, 'scale': [0.8, 1.25], 'seed': 47, 'sink': -140.0, 'offset': 0.0}, {'parent': 'Backdrop', 'centers': [[-2880.0, 0.0]], 'radius': 690.0, 'count': 18, 'scale': [1.05, 1.5], 'seed': 147, 'sink': -165.0, 'offset': 0.5}, {'parent': 'Backdrop', 'centers': [[-4080.0, -2400.0]], 'radius': 470.0, 'count': 16, 'scale': [0.8, 1.25], 'seed': 209, 'sink': -140.0, 'offset': 0.0}, {'parent': 'Backdrop', 'centers': [[-4080.0, -2400.0]], 'radius': 690.0, 'count': 18, 'scale': [1.05, 1.5], 'seed': 210, 'sink': -165.0, 'offset': 0.5}, {'parent': 'Backdrop', 'centers': [[-4080.0, 2400.0]], 'radius': 470.0, 'count': 16, 'scale': [0.8, 1.25], 'seed': 211, 'sink': -140.0, 'offset': 0.0}, {'parent': 'Backdrop', 'centers': [[-4080.0, 2400.0]], 'radius': 690.0, 'count': 18, 'scale': [1.05, 1.5], 'seed': 212, 'sink': -165.0, 'offset': 0.5}]
    return a
