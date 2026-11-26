import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _landmark_lib import patch

L, H, D = 8.0, 2.6, 1.8


def build():
    a = Asset("JerseyBarrier", budget=300, atlas=512, ao_radius=0.4, edge_width=0.05, preview_radius=5.0,
              views=[("FRONT 3/4", 35, 16), ("SIDE", 90, 4), ("FRONT", 0, 6), ("TOP", 20, 50)])
    a.role("Body", "surface")
    concrete = Material("concrete", color=(168, 166, 156), dirt=0.55)
    hazard = Material("hazard", color=(255, 210, 31), color2=(24, 24, 28), width=0.35, angle=45, wear=0.5, dirt=0.45)
    profile = [(-0.9, 0.0), (0.9, 0.0), (0.9, 0.22), (0.42, 0.9), (0.3, H), (-0.3, H), (-0.42, 0.9), (-0.9, 0.22)]
    body = sh.extrude(np.asarray(profile), L, concrete, bevel=0.03, corner_radius=0.0, smooth_angle=20)
    a.add("Body", body.transformed(R(0, 90, 0)))
    band = sh.extrude(np.asarray([(-0.37, 1.95), (0.37, 1.95), (0.33, 2.45), (-0.33, 2.45)]), L + 0.02, hazard, bevel=0.0, corner_radius=0.0, caps=False)
    a.add("Body", band.transformed(compose(R(0, 90, 0), T(0, 0, 0))).transformed(T(0, 0, 0)))
    for x in (-3.0, 3.0):
        a.add("Body", sh.box((0.9, 0.18, 0.5), Material("metal", color=(90, 92, 96), rough=0.5, dirt=0.6)).transformed(T(x, 0.09, 0.0)))
    patch(a, ["Zones/Military/Landmarks"], ["JerseyBarrier"], remove=["BarrierStripe"], functional=True)
    return a
