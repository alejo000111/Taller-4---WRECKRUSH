import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _chaos_lib import basalt, obsidian, crystal_cluster, crystal, PINK, CYAN

SLAB_Y0 = 2.2
SLAB_Y1 = 22.2
UPPER_Y1 = 26.6


def glyphs(width, height, seed, offset):
    rng = np.random.default_rng(seed)
    out = []
    cols = 4
    rows = 14
    for c in range(cols):
        x = -width / 2 + (c + 0.5) * width / cols
        for r in range(rows):
            y = offset - height / 2 + (r + 0.5) * height / rows
            kind = rng.integers(4)
            if kind == 0:
                out.append({"type": "rect", "center": (x, y), "size": (0.5, 0.12), "color": PINK, "rough": 0.1, "wear": 0.0})
            elif kind == 1:
                out.append({"type": "circle", "center": (x, y), "radius": 0.2, "outline": 0.06, "color": PINK, "wear": 0.0})
            elif kind == 2:
                out.append({"type": "rect", "center": (x, y), "size": (0.12, 0.5), "color": PINK, "rough": 0.1, "wear": 0.0})
            else:
                out.append({"type": "rect", "center": (x, y), "size": (0.36, 0.36), "angle": 45, "outline": 0.06, "color": PINK, "wear": 0.0})
    return out


def build():
    a = Asset("AlienMonolith", budget=3000, atlas=1024, ao_radius=1.0, edge_width=0.06, gradient=0.06, highlight=0.5, preview_radius=16.0,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 16), ("FRONT", 180, 4), ("TOP", 200, 45)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=PINK)
    a.role("Crystal", "glass", color=(80, 220, 255), transparency=0.25)

    stone = basalt(veins=0.84, glow=PINK)
    a.add("Body", sh.rounded_box((9.6, 1.2, 5.6), 0.12, 1, stone, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 0.6, 0)))
    a.add("Body", sh.rounded_box((7.6, 1.0, 4.2), 0.1, 1, stone, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 1.7, 0)))

    face = obsidian(rim_glow=0.2, glow=PINK, decals=glyphs(5.0, 17.0, 3, -(SLAB_Y1 - SLAB_Y0) / 2 - 0.8))
    back = obsidian(rim_glow=0.2, glow=PINK, decals=glyphs(5.0, 17.0, 8, -(SLAB_Y1 - SLAB_Y0) / 2 - 0.8))
    slab = sh.extrude([(-3.0, 0.0), (3.0, 0.0), (2.8, SLAB_Y1 - SLAB_Y0), (-2.8, SLAB_Y1 - SLAB_Y0)], 2.4, obsidian(rim_glow=0.2), bevel=0.15, corner_radius=0.0, cap_mats=[back, face])
    a.add("Body", slab.transformed(T(0, SLAB_Y0, 0)))
    a.add("Glow", sh.lathe([(0.9, 0.0), (0.0, 0.0)], 10, None, smooth_angle=60).transformed(compose(T(0, 18.4, -1.24), R(-90, 0, 0))))
    a.add("Glow", sh.lathe([(1.25, 0.0), (1.1, 0.0)], 14, None, smooth_angle=60).transformed(compose(T(0, 18.4, -1.25), R(-90, 0, 0))))

    a.add("Glow", sh.box((5.7, 0.2, 2.5), None).transformed(T(0, SLAB_Y1 + 0.1, 0)))
    upper = sh.extrude([(-2.3, 0.0), (2.3, 0.0), (1.7, UPPER_Y1 - SLAB_Y1 - 0.2), (-1.7, UPPER_Y1 - SLAB_Y1 - 0.2)], 2.0, obsidian(rim_glow=0.3), bevel=0.12, corner_radius=0.0)
    a.add("Body", upper.transformed(T(0, SLAB_Y1 + 0.2, 0)))
    frag = sh.gem(1.0, 2.0, 4, obsidian(rim_glow=0.5))
    a.add("Body", frag.transformed(compose(T(0, UPPER_Y1 + 1.8, 0), R(0, 45, 0))))
    a.add("Glow", sh.torus(1.6, 0.06, None, segments=14, sides=4).transformed(compose(T(0, UPPER_Y1 + 1.8, 0), R(15, 0, 0))))

    for k, (x, z, seed) in enumerate(((-3.8, 1.6, 4), (3.6, -1.9, 7), (-3.2, -2.0, 12))):
        a.add("Crystal", [part.transformed(T(x, 1.2, z)) for part in crystal_cluster(None, seed, 3, 0.5, 2.6, 0.5)])

    destructible(a, "ChaosCore")
    collider(a, "Hitbox", (6.0, UPPER_Y1 - SLAB_Y0, 2.4), (0, (UPPER_Y1 + SLAB_Y0) / 2, 0))
    collider(a, "Plinth", (9.6, 2.2, 5.6), (0, 1.1, 0))
    return a
