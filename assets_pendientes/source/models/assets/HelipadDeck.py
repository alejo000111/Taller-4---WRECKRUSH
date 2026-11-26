import numpy as np

from wr3d import Material, T
from wr3d import shapes as sh
from _ground_lib import ground_asset, slab, circle, ring
from _landmark_lib import patch

RADIUS = 15.0


def build():
    a = ground_asset("HelipadDeck", 900, 17.0, atlas=1024)
    a.role("Glow", "neon", color=(120, 255, 90))
    paint = dict(rough=0.6, wear=0.45)
    top = Material("concrete", color=(62, 66, 60), dirt=0.45, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (28.6, 28.6), "radius": 14.3, "outline": 0.7, "color": (255, 210, 31), **paint},
        {"type": "rect", "center": (0.0, 0.0), "size": (22.0, 22.0), "radius": 11.0, "outline": 0.5, "color": (236, 236, 228), **paint},
        {"type": "rect", "center": (-4.0, 0.0), "size": (2.0, 12.0), "color": (236, 236, 228), **paint},
        {"type": "rect", "center": (4.0, 0.0), "size": (2.0, 12.0), "color": (236, 236, 228), **paint},
        {"type": "rect", "center": (0.0, 0.0), "size": (6.0, 2.0), "color": (236, 236, 228), **paint},
        {"type": "text", "text": "MIL-01", "center": (0.0, 9.0), "height": 1.4, "color": (255, 210, 31), "font": "black", **paint},
    ])
    edge = Material("metal", color=(70, 74, 66), rough=0.45, polish=0.3, dirt=0.5)
    a.add("Body", slab(circle(RADIUS, 40), 0.12, top, side=edge))
    for k in range(12):
        ang = np.radians(k * 30)
        x, z = np.cos(ang) * (RADIUS - 0.6), np.sin(ang) * (RADIUS - 0.6)
        a.add("Body", sh.cylinder(0.35, 0.12, edge, bevel=0.0, segments=8).transformed(T(x, 0.14, z)))
        a.add("Glow", sh.cylinder(0.22, 0.08, None, bevel=0.0, segments=6).transformed(T(x, 0.22, z)))
    patch(a, ["Zones/Military/GroundDetail"], ["Helipad"], remove=["HelipadBarA", "HelipadBarB", "HelipadBarC"], lift=0.0, keep_height=True)
    return a
