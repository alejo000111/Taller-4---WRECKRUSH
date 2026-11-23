import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset
from _chaos_lib import crystal


def build():
    a = pet_asset("ChaosWisp", 1800, 3.0)
    a.parts.pop("Body", None)
    a.roles.pop("Body", None)
    a.role("Core", "neon", color=(166, 77, 255))
    a.role("Shell", "glass", color=(200, 140, 255), transparency=0.55)
    a.role("Shards", "neon", color=(255, 59, 160))
    a.add("Core", sh.sphere(0.7, None, 12, 8))
    a.add("Shell", sh.sphere(1.0, None, 16, 10))
    for k, (pos, rot) in enumerate((((-0.75, -0.3, 1.3), (-10, 118, 17)), ((-0.75, 0.0, -1.3), (-10, -118, -17)), ((1.5, 0.3, 0.0), (20, 0, 0)))):
        a.add("Shards", crystal(0.22, 0.9, None, facets=4).transformed(compose(T(*pos), R(*rot), T(0, -0.45, 0))))
    a.add("Shards", sh.torus(1.25, 0.03, None, segments=24, sides=3).transformed(R(20, 0, 10)))
    return a
