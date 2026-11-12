import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _ground_lib import ground_asset, slab, circle, ring
from _landmark_lib import patch

RADIUS = 15.0
ORANGE = (255, 122, 26)


def build():
    a = ground_asset("SpawnEmblem", 1200, 17.0, atlas=1024)
    a.role("Glow", "neon", color=ORANGE)
    lines = dict(rough=0.4, wear=0.25)
    top = Material("glossy", color=(36, 37, 46), rough=0.35, metal=0.2, dirt=0.25, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (28.0, 28.0), "radius": 14.0, "outline": 0.35, "color": ORANGE, **lines},
        {"type": "rect", "center": (0.0, 0.0), "size": (12.0, 12.0), "radius": 6.0, "outline": 0.25, "color": (230, 230, 236), **lines},
        *[{"type": "rect", "center": (np.cos(np.radians(k * 45)) * 10.0, np.sin(np.radians(k * 45)) * 10.0), "size": (3.4, 0.5), "angle": k * 45, "color": (230, 230, 236), **lines} for k in (0, 1, 3, 4, 5, 7)],
        {"type": "text", "text": "WRECK", "center": (0.0, -8.3), "height": 1.5, "color": ORANGE, "font": "impact", **lines},
        {"type": "text", "text": "RUSH", "center": (0.0, 8.3), "height": 1.5, "color": ORANGE, "font": "impact", **lines},
    ])
    edge = Material("metal", color=(54, 56, 64), rough=0.35, polish=0.6, dirt=0.3)
    a.add("Body", slab(circle(RADIUS, 48), 0.1, top, side=edge))
    a.add("Body", ring(RADIUS - 0.2, RADIUS + 0.25, 0.16, edge, segments=48))
    a.add("Glow", ring(RADIUS - 1.6, RADIUS - 1.3, 0.13, None, segments=48))
    for k in range(8):
        ang = k * 45.0 + 22.5
        chevron = sh.extrude([(-0.9, 0.0), (0.0, 0.7), (0.9, 0.0), (0.9, 0.35), (0.0, 1.05), (-0.9, 0.35)], 0.05, None, bevel=0.0, corner_radius=0.0)
        a.add("Glow", chevron.transformed(compose(R(0, -ang, 0), T(11.6, 0.13, 0), R(-90, 0, 0), R(0, 0, -90))))
    patch(a, ["Plaza/Floor"], ["SpawnDisc"], keep_height=True)
    return a
