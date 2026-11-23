import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import FROST, expedition_asset, terrain
from _chaos_lib import crystal_cluster
from _landmark_lib import patch


def build():
    a = expedition_asset("IceShard", 700, 14.0, atlas=512)
    a.role("Ice", "glass", color=(170, 220, 240), transparency=0.15)
    base = terrain("frost")
    rock = sh.sphere(1.0, base, 10, 5)
    rng = np.random.default_rng(41)
    rock.pos *= 1 + rng.normal(0, 0.12, (len(rock.pos), 1))
    rock.pos[:, 1] = np.maximum(rock.pos[:, 1], 0.0)
    rock.pos *= np.array([8.0, 4.0, 8.0])
    a.add("Body", sh.recompute_normals(rock))
    a.add("Ice", [p.transformed(T(0, 2.0, 0)) for p in crystal_cluster(None, 17, 6, 3.4, 22.0, 5.0, tilt=26)])
    patch(a, [FROST], ["IceCliff"])
    return a
