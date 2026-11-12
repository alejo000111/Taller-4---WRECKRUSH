import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _landmark_lib import landmark, box_collider
from _station_lib import steel, painted
import _city_lib

H = 72.0
R0 = 6.5
R1 = 4.6


def radius_at(y):
    return R0 + (R1 - R0) * np.clip((y - 2.0) / (H - 2.0), 0, 1)


def build():
    a = Asset("Smokestack", budget=2500, atlas=1024, ao_radius=1.6, edge_width=0.1, preview_radius=40.0,
              views=[("FRONT 3/4", 215, 8), ("BACK 3/4", 35, 12), ("SIDE", 270, 4), ("TOP", 200, 45)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 40, 40))

    brick = Material("city_brick", color=(150, 74, 56), mortar=(120, 110, 100), brick=(1.2, 0.5), gap=0.06, wear=0.3, soot=0.6, dirt=0.5)
    bands = []
    for y0, y1, color in ((52.0, 57.0, (200, 50, 40)), (57.0, 62.0, (230, 230, 230)), (62.0, 67.0, (200, 50, 40))):
        bands.append((y0, y1, color))
    profile = [(0.0, 2.0), (R0, 2.0), (radius_at(H), H), (0.0, H)]
    a.add("Body", sh.lathe(profile, 18, brick, smooth_angle=30, r_ref=R0))
    for y0, y1, color in bands:
        band = Material("paint", color=color, under=(120, 110, 100), wear=0.35, scratches=0.3, rough=0.6, dirt=0.5, dirt_color=(30, 26, 24), skin=False)
        r0, r1 = radius_at(y0) + 0.08, radius_at(y1) + 0.08
        a.add("Body", sh.lathe([(r0, y0), (r1, y1)], 18, band, smooth_angle=30))
    concrete = Material("concrete", color=(110, 110, 112), dirt=0.6)
    a.add("Body", sh.lathe([(0.0, 0.0), (8.2, 0.0), (8.2, 1.4), (7.4, 2.2), (0.0, 2.2)], 8, concrete, smooth_angle=20, start=22.5))
    soot = Material("metal", color=(30, 28, 28), rough=0.85, polish=0.0, dirt=0.3)
    a.add("Body", sh.lathe([(R1 + 0.6, H - 0.6), (R1 + 0.6, H + 0.6), (R1 - 0.6, H + 0.6), (R1 - 0.6, H - 0.4)], 18, steel((44, 44, 48)), closed=True, smooth_angle=30))
    a.add("Body", sh.lathe([(R1 - 0.6, H + 0.2), (0.0, H - 2.0)], 18, soot, smooth_angle=30))
    for y in (20.0, 36.0):
        r = radius_at(y)
        a.add("Body", sh.lathe([(r, y - 0.4), (r + 0.5, y - 0.4), (r + 0.5, y + 0.4), (r, y + 0.4)], 18, steel((60, 60, 64)), closed=True, smooth_angle=30))
    ladder = steel((80, 82, 88))
    for dx in (-0.45, 0.45):
        pts = [(dx, y, -(radius_at(y) + 0.5)) for y in (2.0, H)]
        a.add("Body", sh.sweep(pts, 0.07, 4, ladder))
    for y in np.arange(4.0, H - 1.0, 2.0):
        a.add("Body", sh.box((0.9, 0.08, 0.08), ladder).transformed(T(0, y, -(radius_at(y) + 0.5))))
    for k in range(3):
        ang = np.radians(k * 120 + 30)
        r = radius_at(H - 4.0) + 0.3
        a.add("Glow", sh.sphere(0.5, None, 8, 4).transformed(T(np.cos(ang) * r, H - 4.0, np.sin(ang) * r)))

    landmark(a, "Zones/Industrial/Landmarks", "Smokestack", fit="height", colliders=[
        box_collider("Stack", (R0 * 2, H, R0 * 2), (0, H / 2, 0), shape="Cylinder"),
    ])
    return a
