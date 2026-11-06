import numpy as np

from wr3d import Material, T
from _ground_lib import ground_asset, slab, circle, ring
from _hall_lib import HALL, ORANGE
from _landmark_lib import patch

RADIUS = 24.0


def build():
    a = ground_asset("HallDisc", 1200, 27.0, atlas=1024)
    a.role("Glow", "neon", color=ORANGE)
    inlay = dict(rough=0.25, wear=0.2, metal=1.0)
    decals = [{"type": "rect", "center": (0.0, 0.0), "size": (r * 2, r * 2), "radius": r, "outline": w, "color": (220, 170, 60), **inlay} for r, w in ((22.4, 0.3), (17.0, 0.15), (9.0, 0.2))]
    decals += [{"type": "rect", "center": (np.cos(np.radians(k * 22.5)) * 13.0, np.sin(np.radians(k * 22.5)) * 13.0), "size": (7.6, 0.14 if k % 2 else 0.3), "angle": k * 22.5, "color": (220, 170, 60), **inlay} for k in range(16)]
    stone = Material("glossy", color=(28, 28, 34), rough=0.12, metal=0.1, dirt=0.05, decals=decals)
    edge = Material("gold", color=(220, 170, 60), rough=0.25, dirt=0.05)
    a.add("Body", slab(circle(RADIUS, 64), 0.1, stone, side=edge))
    a.add("Body", ring(RADIUS - 0.25, RADIUS + 0.2, 0.14, edge, segments=64))
    a.add("Glow", ring(RADIUS - 0.95, RADIUS - 0.7, 0.12, None, segments=64))
    patch(a, [f"{HALL}/Grounds"], ["PodiumDisc"], remove=["PodiumRingGlow"], keep_height=True)
    return a
