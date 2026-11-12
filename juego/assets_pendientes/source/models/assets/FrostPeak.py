import numpy as np

from wr3d import Material
from _backdrop_lib import backdrop_asset, heightfield, noise2, peaks

W, D, H = 300.0, 220.0, 360.0


def build():
    a = backdrop_asset("FrostPeak", 2600, 220.0)
    rock = Material("terrain_rock", color=(108, 122, 140), cap=(240, 246, 252), cap_amount=1.0, strata=0.12, dirt=0.2)

    def shape(x, z):
        base = peaks(x, z, 37, count=4, sharp=1.15)
        detail = 0.06 * noise2(x * 4.0, z * 4.0, 37 + 3)
        return np.clip(base + detail * (base > 0.02), 0, None) * H

    a.add("Body", heightfield(W, D, 22, 16, rock, shape))
    a.meta["ring"] = [{'parent': 'Backdrop', 'centers': [[2880.0, 0.0]], 'radius': 470.0, 'count': 16, 'scale': [0.8, 1.25], 'seed': 43, 'sink': -140.0, 'offset': 0.0}, {'parent': 'Backdrop', 'centers': [[2880.0, 0.0]], 'radius': 690.0, 'count': 18, 'scale': [1.05, 1.5], 'seed': 143, 'sink': -165.0, 'offset': 0.5}, {'parent': 'Backdrop', 'centers': [[4080.0, -2400.0]], 'radius': 470.0, 'count': 16, 'scale': [0.8, 1.25], 'seed': 206, 'sink': -140.0, 'offset': 0.0}, {'parent': 'Backdrop', 'centers': [[0.0, -4800.0]], 'radius': 470.0, 'count': 16, 'scale': [0.8, 1.25], 'seed': 207, 'sink': -140.0, 'offset': 0.0}, {'parent': 'Backdrop', 'centers': [[0.0, -4800.0]], 'radius': 690.0, 'count': 18, 'scale': [1.05, 1.5], 'seed': 208, 'sink': -165.0, 'offset': 0.5}]
    return a
