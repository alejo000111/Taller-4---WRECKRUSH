import numpy as np

from wr3d import Material, T
from wr3d import shapes as sh
from _expedition_lib import FROST, expedition_asset
from _landmark_lib import patch


def build():
    a = expedition_asset("SnowDrift", 300, 11.0, atlas=256)
    snow = Material("terrain_rock", color=(220, 232, 242), cap=(244, 248, 252), cap_amount=1.0, strata=0.2, dirt=0.0)
    mound = sh.sphere(1.0, snow, 14, 6)
    rng = np.random.default_rng(31)
    mound.pos *= 1 + rng.normal(0, 0.06, (len(mound.pos), 1))
    mound.pos[:, 1] = np.maximum(mound.pos[:, 1], 0.0)
    mound.pos *= np.array([10.0, 3.0, 6.0])
    a.add("Body", sh.recompute_normals(mound))
    patch(a, [FROST], ["SnowDrift"])
    return a
