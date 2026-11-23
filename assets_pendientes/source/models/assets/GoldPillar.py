import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _landmark_lib import landmark, box_collider

H = 50.0


def build():
    a = Asset("GoldPillar", budget=1500, atlas=1024, ao_radius=1.0, edge_width=0.08, gradient=0.06, highlight=0.7, preview_radius=27.0,
              views=[("FRONT 3/4", 215, 8), ("BACK 3/4", 35, 12), ("FRONT", 180, 4), ("TOP", 200, 45)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 214, 90))

    gold = Material("gold", color=(255, 196, 40), rough=0.18, dirt=0.05)
    marble = Material("paint", color=(28, 26, 32), under=(28, 26, 32), wear=0.0, scratches=0.05, rough=0.12, dirt=0.05, skin=False, decals=[
        *[{"type": "rect", "center": (u, 0.0), "size": (0.12, 40.0), "color": (230, 180, 60), "metal": 1.0, "rough": 0.2, "wear": 0.0} for u in np.linspace(0.6, 17.0, 8)],
    ])
    a.add("Body", sh.lathe([(0.0, 0.0), (3.8, 0.0), (3.8, 1.2), (3.4, 1.6), (3.4, 2.4), (2.9, 2.8), (0.0, 2.8)], 8, gold, smooth_angle=20, start=22.5))
    a.add("Body", sh.lathe([(2.9, 2.8), (2.5, 6.0), (2.4, H - 7.0), (2.9, H - 6.0)], 16, marble, smooth_angle=30, r_ref=2.9))
    a.add("Body", sh.lathe([(0.0, H - 6.0), (2.9, H - 6.0), (3.6, H - 5.2), (3.8, H - 3.6), (3.2, H - 3.0), (0.0, H - 3.0)], 8, gold, smooth_angle=25, start=22.5))
    for y in (10.0, 20.0, 30.0):
        a.add("Glow", sh.lathe([(2.45, y - 0.25), (2.7, y - 0.25), (2.7, y + 0.25), (2.45, y + 0.25)], 16, None, closed=True, smooth_angle=30))
    a.add("Body", sh.lathe([(0.0, H - 3.0), (1.6, H - 3.0), (1.0, H - 2.2), (0.0, H - 2.0)], 8, gold, smooth_angle=30))
    a.add("Glow", sh.sphere(2.0, None, 12, 8).transformed(T(0, H - 1.6 + 1.6, 0)))
    landmark(a, "VIPArea/Landmarks", "GoldPillar", fit="box", colliders=[box_collider("Pillar", (6.0, H, 6.0), (0, H / 2, 0))])
    return a
