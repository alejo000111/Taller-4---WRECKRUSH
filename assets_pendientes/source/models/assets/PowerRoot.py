import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider, animate
from _expedition_lib import leaves


def build():
    a = Asset("PowerRoot", budget=1600, atlas=512, ao_radius=0.6, edge_width=0.06, preview_radius=8.0,
              views=[("FRONT 3/4", 215, 14), ("FRONT", 180, 4), ("SIDE", 270, 6), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Bands", "neon", color=(109, 206, 145))
    a.role("Charge", "glass", color=(160, 255, 190), transparency=0.15)
    destructible(a, "Event")
    collider(a, "Base", (9.0, 2.0, 9.0), (0.0, 1.0, 0.0), shape="Cylinder")
    animate(a, "Charge", "Orb")
    bark = Material("wood", color=(96, 78, 56), dirt=0.5)
    metal = Material("metal", color=(70, 74, 64), rough=0.45, polish=0.3, dirt=0.5)
    a.add("Body", sh.lathe([(0.0, 0.0), (4.5, 0.0), (4.5, 1.2), (3.8, 2.0), (0.0, 2.0)], 12, metal, smooth_angle=35))
    a.add("Body", sh.lathe([(0.0, 1.8), (3.0, 1.8), (2.6, 3.0), (2.4, 8.0), (2.8, 9.0), (0.0, 9.2)], 10, bark, smooth_angle=40))
    for k in range(5):
        ang = np.radians(k * 72 + 20)
        tip = (np.cos(ang) * 4.4, 0.4, np.sin(ang) * 4.4)
        a.add("Body", sh.sweep([(np.cos(ang) * 1.8, 4.0, np.sin(ang) * 1.8), (np.cos(ang) * 3.4, 2.4, np.sin(ang) * 3.4), tip], 0.6, 5, bark, samples=5, taper=lambda t: 1.0 - 0.6 * t))
    for j in range(1, 4):
        a.add("Bands", sh.lathe([(2.55, j * 2.3 - 0.27), (2.95, j * 2.3 - 0.27), (2.95, j * 2.3 + 0.27), (2.55, j * 2.3 + 0.27)], 12, None, closed=True, smooth_angle=30))
    a.add("Charge", sh.sphere(2.5, None, 12, 7).transformed(T(0, 10.0, 0)))
    leaf = leaves((90, 140, 80), scale=3.0)
    for k in range(3):
        ang = np.radians(k * 120)
        a.add("Body", sh.box((1.4, 0.15, 0.9), leaf).transformed(compose(T(np.cos(ang) * 2.4, 8.8, np.sin(ang) * 2.4), R(20, -np.degrees(ang), 0))))
    return a
