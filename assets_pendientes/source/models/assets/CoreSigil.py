import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _ground_lib import ground_asset, slab, circle, ring
from _landmark_lib import patch
from _chaos_lib import VIOLET

RADIUS = 11.0


def build():
    a = ground_asset("CoreSigil", 1200, 13.0, atlas=1024)
    a.role("Glow", "neon", color=VIOLET)
    stone = Material("glossy", color=(20, 16, 28), rough=0.2, metal=0.1, dirt=0.15, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (19.0, 19.0), "radius": 9.5, "outline": 0.08, "color": (90, 60, 130), "wear": 0.2},
        {"type": "rect", "center": (0.0, 0.0), "size": (9.0, 9.0), "radius": 4.5, "outline": 0.08, "color": (90, 60, 130), "wear": 0.2},
        *[{"type": "rect", "center": (np.cos(np.radians(k * 22.5)) * 7.2, np.sin(np.radians(k * 22.5)) * 7.2), "size": (0.4, 1.4), "angle": k * 22.5 + 90, "color": (70, 46, 100), "wear": 0.3} for k in range(16)],
    ])
    a.add("Body", slab(circle(RADIUS, 40), 0.08, stone))
    a.add("Glow", ring(RADIUS - 0.7, RADIUS - 0.35, 0.12, None, segments=40))
    a.add("Glow", ring(5.6, 5.85, 0.12, None, segments=32))
    a.add("Glow", ring(1.6, 2.0, 0.14, None, segments=20))
    for k in range(8):
        ang = k * 45.0 + 22.5
        rad = np.radians(ang)
        cx, cz = np.cos(rad) * 8.2, -np.sin(rad) * 8.2
        a.add("Glow", sh.box((1.6, 0.12, 0.22), None).transformed(compose(T(cx, 0.06, cz), R(0, ang, 0))))
        a.add("Glow", sh.box((0.22, 0.12, 1.0), None).transformed(compose(T(cx, 0.06, cz), R(0, ang + 30, 0), T(0.5, 0, 0))))
    for k in range(3):
        ang = k * 120.0
        a.add("Glow", sh.box((3.4, 0.12, 0.18), None).transformed(compose(R(0, ang, 0), T(3.8, 0.06, 0))))
    patch(a, ["Zones/ChaosCore/GroundDetail"], ["CoreSigil"], keep_height=True, tint=["Glow"])
    return a
