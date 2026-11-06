import numpy as np

from wr3d import Material, T
from _ground_lib import ground_asset, slab, circle, ring
from _landmark_lib import patch
import _city_lib

RADIUS = 27.0
ORANGE = (255, 122, 26)


def build():
    a = ground_asset("MonumentDisc", 1200, 30.0, atlas=1024)
    a.role("Glow", "neon", color=ORANGE)
    grout = dict(rough=0.8, wear=0.1)
    decals = [{"type": "rect", "center": (0.0, 0.0), "size": (r * 2, r * 2), "radius": r, "outline": 0.08, "color": (24, 24, 30), **grout} for r in (8.0, 14.0, 20.0, 25.6)]
    decals += [{"type": "rect", "center": (np.cos(np.radians(k * 15)) * 16.8, np.sin(np.radians(k * 15)) * 16.8), "size": (17.6, 0.08), "angle": k * 15, "color": (24, 24, 30), **grout} for k in range(24)]
    decals += [{"type": "rect", "center": (0.0, 0.0), "size": (50.0, 50.0), "radius": 25.0, "outline": 0.4, "color": (200, 96, 24), "rough": 0.3, "wear": 0.3}]
    stone = Material("city_stone", color=(56, 58, 68), dirt=0.25, decals=decals)
    edge = Material("metal", color=(40, 42, 50), rough=0.35, polish=0.6, dirt=0.3)
    a.add("Body", slab(circle(RADIUS, 64), 0.1, stone, side=edge))
    a.add("Body", ring(RADIUS - 0.3, RADIUS + 0.2, 0.16, edge, segments=64))
    a.add("Glow", ring(RADIUS - 0.9, RADIUS - 0.6, 0.13, None, segments=64))
    patch(a, ["Plaza/Floor"], ["MonumentDisc"], remove=["MonumentRingGlow"], keep_height=True)
    return a
