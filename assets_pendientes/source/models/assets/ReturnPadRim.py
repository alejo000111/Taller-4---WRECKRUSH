import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _ground_lib import ground_asset, slab, circle, ring
from _landmark_lib import patch

RADIUS = 4.0


def build():
    a = ground_asset("ReturnPadRim", 700, 5.0)
    a.role("Glow", "neon", color=(178, 85, 18))
    plate = Material("diamondplate", color=(60, 64, 74), pitch=0.35, dirt=0.35)
    rim = Material("hazard", color=(255, 210, 31), color2=(24, 24, 28), width=0.4, angle=45, wear=0.4, dirt=0.4)
    steel = Material("metal", color=(54, 58, 66), rough=0.35, polish=0.6, dirt=0.35)
    a.add("Body", slab(circle(RADIUS, 32), 0.2, plate, side=steel))
    a.add("Body", sh.lathe([(RADIUS, 0.0), (RADIUS, 0.45), (RADIUS - 0.5, 0.45), (RADIUS - 0.5, 0.2)], 32, rim, smooth_angle=30))
    a.add("Glow", slab(circle(2.6, 24), 0.24, None))
    a.add("Glow", ring(3.05, 3.25, 0.28, None, segments=28))
    for k in range(4):
        ang = k * 90.0 + 45.0
        arrow = sh.extrude([(-0.5, 0.0), (0.0, 0.45), (0.5, 0.0), (0.5, 0.22), (0.0, 0.67), (-0.5, 0.22)], 0.04, None, bevel=0.0, corner_radius=0.0)
        a.add("Glow", arrow.transformed(compose(R(0, -ang, 0), T(2.85, 0.26, 0), R(-90, 0, 0), R(0, 0, 90))))
    patch(a, ["Zones", "VIPArea"], ["ReturnPad"], keep_height=True, functional=True, tint=["Glow"])
    return a
