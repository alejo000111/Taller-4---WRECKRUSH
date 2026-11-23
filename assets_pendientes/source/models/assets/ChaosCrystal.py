import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _chaos_lib import basalt, rock, grounded, crystal_cluster, crystal, VIOLET, PINK


def build():
    a = Asset("ChaosCrystal", budget=1500, atlas=512, ao_radius=0.6, edge_width=0.05, gradient=0.06, highlight=0.4, preview_radius=6.4,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Crystal", "glass", color=VIOLET, transparency=0.25)
    a.role("Core", "neon", color=PINK)

    stone = basalt(veins=0.8)
    base = rock(2.6, stone, 3, squash=(1.0, 0.45, 0.9), segments=10, rings=6)
    a.add("Body", grounded(base.transformed(T(0, 0.95, 0))))
    for seed, (x, z, r) in enumerate(((1.6, 1.2, 1.1), (-1.8, 0.8, 0.9), (0.4, -1.9, 0.8))):
        a.add("Body", grounded(rock(r, stone, 20 + seed, squash=(1.0, 0.7, 1.0), segments=7, rings=4).transformed(T(x, 0.75, z))))

    a.add("Crystal", [part.transformed(T(0, 0.9, 0)) for part in crystal_cluster(None, 7, 5, 1.25, 10.5, 1.6)])
    a.add("Core", crystal(0.42, 8.0, None, facets=5).transformed(T(0, 4.9, 0)))
    for k, (x, z) in enumerate(((2.3, -1.2), (-2.1, -1.4))):
        a.add("Crystal", crystal(0.4, 1.8, None, facets=5).transformed(compose(T(x, 1.3, z), R(0, 0, 18 if x > 0 else -18))))
    a.add("Core", sh.lathe([(2.0, 0.0), (0.0, 0.0)], 12, None, smooth_angle=60).transformed(T(0, 1.42, 0)))

    destructible(a, "ChaosCore")
    collider(a, "Hitbox", (3.2, 10.0, 3.2), (0, 5.8, 0))
    collider(a, "Base", (5.2, 2.0, 4.6), (0, 1.0, 0))
    return a
