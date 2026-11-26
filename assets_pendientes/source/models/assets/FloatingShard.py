import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _chaos_lib import basalt, rock, grounded, crystal, CYAN

SHARD_Y = 10.0


def rune_ring(radius):
    out = []
    for k in range(12):
        ang = k * 30
        out.append({"type": "rect", "center": (np.radians(ang) * radius, 0.2), "size": (0.25, 0.12 + 0.1 * (k % 3)), "color": CYAN, "rough": 0.1, "wear": 0.0})
    return out


def build():
    a = Asset("FloatingShard", budget=2500, atlas=1024, ao_radius=0.8, edge_width=0.06, gradient=0.06, highlight=0.4, preview_radius=8.6,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Shard", "glass", color=(80, 220, 255), transparency=0.25)
    a.role("Glow", "neon", color=CYAN)

    stone = basalt(veins=0.85, glow=CYAN)
    tiers = [(4.6, 0.0, 0.6), (3.8, 0.6, 1.1), (2.9, 1.1, 1.5)]
    for k, (r, y0, y1) in enumerate(tiers):
        tier = sh.lathe([(0.0, y0), (r, y0), (r, y1 - 0.08), (r - 0.12, y1), (0.0, y1)], 6, stone, smooth_angle=20, start=k * 10)
        a.add("Body", tier)
    a.add("Glow", sh.lathe([(3.35, 1.11), (3.1, 1.11)], 6, None, smooth_angle=20, start=10))
    a.add("Glow", sh.lathe([(2.0, 1.51), (1.4, 1.51)], 12, None, smooth_angle=60))

    for k in range(3):
        ang = np.radians(90 + k * 120)
        p = np.array([np.cos(ang) * 3.7, 0.6, -np.sin(ang) * 3.7])
        ob = sh.lathe([(0.0, 0.0), (0.55, 0.0), (0.45, 2.4), (0.2, 3.0), (0.0, 3.2)], 4, stone, smooth_angle=20, start=45)
        a.add("Body", ob.transformed(T(*p)))
        a.add("Glow", sh.gem(0.28, 0.7, 4, None).transformed(T(p[0], p[1] + 3.5, p[2])))
        beam = sh.sweep([tuple(p + np.array([0, 3.5, 0])), (0.0, SHARD_Y - 2.4, 0.0)], 0.05, 4, None)
        a.add("Glow", beam)

    a.add("Glow", sh.cylinder(0.22, SHARD_Y - 4.0, None, bevel=0.0, segments=6).transformed(T(0, 1.5 + (SHARD_Y - 4.0) / 2, 0)))
    shard = crystal(1.7, 7.6, None, facets=6, crown=0.3)
    a.add("Shard", shard.transformed(compose(T(0, SHARD_Y, 0), R(0, 0, 8))))
    a.add("Glow", crystal(0.5, 6.2, None, facets=5).transformed(compose(T(0, SHARD_Y, 0), R(0, 0, 8))))
    for k, (ang, dist, h, size) in enumerate(((20, 2.8, 8.4, 0.5), (150, 3.2, 11.6, 0.42), (260, 2.6, 13.0, 0.36))):
        rad = np.radians(ang)
        a.add("Shard", crystal(size, size * 3.0, None, facets=5).transformed(compose(T(np.cos(rad) * dist, h, np.sin(rad) * dist), R(30 * k, 0, 25))))

    for seed, (x, z, r) in enumerate(((4.4, 2.6, 0.7), (-4.2, -2.2, 0.6), (-1.0, 4.6, 0.55))):
        a.add("Body", grounded(rock(r, stone, 40 + seed, squash=(1.0, 0.6, 1.0), segments=6, rings=4).transformed(T(x, 0.25, z))))

    destructible(a, "ChaosCore")
    collider(a, "Hitbox", (3.6, 8.0, 3.6), (0, SHARD_Y, 0))
    collider(a, "Altar", (9.2, 1.5, 9.2), (0, 0.75, 0), shape="Cylinder")
    return a
