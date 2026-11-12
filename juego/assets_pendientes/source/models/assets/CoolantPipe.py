import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider, animate
import _expedition_lib


def build():
    a = Asset("CoolantPipe", budget=1600, atlas=512, ao_radius=0.6, edge_width=0.06, preview_radius=8.0,
              views=[("FRONT 3/4", 215, 14), ("FRONT", 180, 4), ("SIDE", 270, 6), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Bands", "neon", color=(129, 207, 230))
    a.role("Charge", "glass", color=(170, 230, 255), transparency=0.15)
    destructible(a, "Event")
    collider(a, "Base", (9.0, 2.0, 9.0), (0.0, 1.0, 0.0), shape="Cylinder")
    animate(a, "Charge", "Orb")
    steel = Material("metal", color=(90, 108, 120), rough=0.35, polish=0.5, dirt=0.4, scratches=0.4)
    paint = Material("paint", color=(239, 153, 94), under=(110, 100, 90), wear=0.4, scratches=0.4, rough=0.4, dirt=0.4, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (40.0, 0.6), "color": (30, 30, 34), "wear": 0.3},
    ])
    frost = Material("terrain_rock", color=(200, 220, 235), cap=(240, 246, 250), cap_amount=1.0, dirt=0.0)
    a.add("Body", sh.lathe([(0.0, 0.0), (4.5, 0.0), (4.5, 1.2), (3.8, 2.0), (0.0, 2.0)], 12, steel, smooth_angle=35))
    a.add("Body", sh.lathe([(0.0, 1.8), (2.6, 1.8), (2.5, 8.6), (2.9, 9.0), (0.0, 9.2)], 12, paint, smooth_angle=40))
    for y in (3.0, 6.0):
        a.add("Body", sh.lathe([(2.5, y - 0.3), (3.0, y - 0.3), (3.0, y + 0.3), (2.5, y + 0.3)], 12, steel, closed=True, smooth_angle=30))
    a.add("Body", sh.cylinder(0.25, 1.4, steel, bevel=0.0, segments=6).transformed(compose(T(2.9, 5.0, 0), R(0, 0, 90))))
    a.add("Body", sh.torus(0.8, 0.15, steel, segments=10, sides=4).transformed(compose(T(3.7, 5.0, 0), R(0, 0, 90))))
    for j in range(1, 4):
        a.add("Bands", sh.lathe([(2.55, j * 2.3 - 0.27), (2.95, j * 2.3 - 0.27), (2.95, j * 2.3 + 0.27), (2.55, j * 2.3 + 0.27)], 12, None, closed=True, smooth_angle=30))
    a.add("Body", sh.box((3.0, 0.4, 2.0), frost).transformed(compose(T(-2.0, 2.1, 1.4), R(0, 30, 0))))
    a.add("Charge", sh.sphere(2.5, None, 12, 7).transformed(T(0, 10.0, 0)))
    return a
