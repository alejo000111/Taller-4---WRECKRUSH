import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _ground_lib import ground_asset, slab, circle, ring
from _landmark_lib import patch

RADIUS = 5.5


def octagon(r):
    angles = np.radians(np.arange(8) * 45.0 + 22.5)
    return np.stack([np.cos(angles) * r, np.sin(angles) * r], 1)


def build():
    a = ground_asset("PortalPad", 900, 7.0)
    a.role("Glow", "neon", color=(255, 122, 26))
    plate = Material("glossy", color=(26, 28, 36), rough=0.3, metal=0.4, dirt=0.25, decals=[
        *[{"type": "rect", "center": (np.cos(np.radians(k * 45 + 22.5)) * 3.4, np.sin(np.radians(k * 45 + 22.5)) * 3.4), "size": (0.12, 2.6), "angle": k * 45 + 22.5 + 90, "color": (60, 64, 76), "wear": 0.2} for k in range(8)],
    ])
    steel = Material("metal", color=(68, 68, 71), rough=0.35, polish=0.6, dirt=0.3)
    a.add("Body", slab(octagon(RADIUS), 0.3, plate, side=steel))
    a.add("Body", sh.lathe([(RADIUS * 1.0, 0.0), (RADIUS * 1.0, 0.55), (RADIUS - 0.6, 0.55), (RADIUS - 0.6, 0.3)], 8, steel, smooth_angle=10, start=22.5))
    a.add("Glow", ring(RADIUS - 1.1, RADIUS - 0.85, 0.36, None, segments=32))
    a.add("Glow", ring(1.6, 2.0, 0.36, None, segments=24))
    for k in range(8):
        ang = k * 45.0
        a.add("Glow", sh.box((1.2, 0.06, 0.18), None).transformed(compose(R(0, ang, 0), T(3.0, 0.33, 0))))
    patch(a, ["Portals"], ["Pad"], keep_height=True, functional=True, tint=["Glow"])
    return a
