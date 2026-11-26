import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _ground_lib import ground_asset, slab, ring
from _landmark_lib import patch

ORANGE = (255, 122, 26)


def octagon(r):
    angles = np.radians(np.arange(8) * 45.0 + 22.5)
    return np.stack([np.cos(angles) * r, np.sin(angles) * r], 1)


def build():
    a = ground_asset("SpawnPedestal", 1200, 11.0, atlas=1024)
    a.role("Glow", "neon", color=ORANGE)
    base = Material("hazard", color=(255, 196, 30), color2=(28, 28, 32), width=0.6, angle=45, wear=0.45, dirt=0.4)
    steel = Material("metal", color=(48, 50, 58), rough=0.35, polish=0.6, dirt=0.35)
    top = Material("diamondplate", color=(54, 58, 68), pitch=0.5, dirt=0.3, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (7.4, 7.4), "radius": 3.7, "color": (24, 24, 30), "rough": 0.3, "wear": 0.1},
        {"type": "rect", "center": (0.0, 0.0), "size": (7.4, 7.4), "radius": 3.7, "outline": 0.3, "color": ORANGE, "wear": 0.2},
        {"type": "text", "text": "WR", "center": (0.0, 0.0), "height": 2.6, "color": ORANGE, "font": "impact", "wear": 0.2},
    ])
    a.add("Body", sh.lathe([(9.5, 0.0), (9.5, 0.45), (9.1, 0.7), (6.6, 0.7)], 40, base, smooth_angle=30))
    a.add("Body", slab(octagon(6.5), 1.0, top, side=steel))
    a.add("Glow", ring(6.75, 7.05, 0.74, None, segments=40))
    for k in range(8):
        ang = k * 45.0
        a.add("Glow", sh.box((1.4, 0.05, 0.3), None).transformed(compose(R(0, ang, 0), T(8.2, 0.72, 0))))
    a.add("Glow", ring(4.6, 4.8, 1.04, None, segments=32))
    patch(a, ["Plaza"], ["SpawnRing"], remove=["SpawnLocation", "SpawnEmblem", "SpawnEmblemCore"], keep_height=True, functional=True)
    return a
