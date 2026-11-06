import numpy as np

from wr3d import Material
from _backdrop_lib import backdrop_asset, heightfield, noise2, peaks

W, D, H = 420.0, 260.0, 180.0


def build():
    a = backdrop_asset("MesaRidgeA", 2600, 240.0)
    rock = Material("terrain_rock", color=(122, 82, 64), cap=(176, 132, 96), cap_amount=0.75, strata=0.18, dirt=0.3)

    def shape(x, z):
        base = peaks(x, z, 11, count=4, sharp=0.7, base=0.3)
        ripple = 0.08 * noise2(x * 3.0, z * 3.0, 11 + 1)
        level = np.clip(base + ripple, 0, None)
        steps = np.floor(level * 4.0) / 4.0
        terrace = steps + np.clip((level * 4.0 - np.floor(level * 4.0) - 0.75) * 4.0, 0, 1) / 4.0
        return terrace * H

    a.add("Body", heightfield(W, D, 24, 14, rock, shape))
    a.meta["ring"] = [{'parent': 'Backdrop', 'centers': [[0.0, 0.0]], 'radius': 1320.0, 'count': 16, 'scale': [0.95, 1.35], 'seed': 5, 'sink': -6.0, 'offset': 0.0}, {'parent': 'Backdrop', 'centers': [[0.0, 4800.0]], 'radius': 470.0, 'count': 16, 'scale': [1.0, 1.4], 'seed': 201, 'sink': -70.0, 'offset': 0.0}, {'parent': 'Backdrop', 'centers': [[4080.0, 2400.0]], 'radius': 690.0, 'count': 18, 'scale': [1.2, 1.6], 'seed': 202, 'sink': -90.0, 'offset': 0.5}]
    return a
