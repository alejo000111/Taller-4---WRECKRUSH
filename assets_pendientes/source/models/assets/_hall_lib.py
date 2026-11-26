import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh

HALL = "@Leaderboards/HallOfWreckers"
GOLD = (255, 196, 40)
SILVER = (205, 212, 225)
BRONZE = (214, 128, 52)
ORANGE = (255, 122, 26)


def hall_asset(name, budget, radius, atlas=1024, front=180):
    a = Asset(name, budget=budget, atlas=atlas, ao_radius=0.8, ao_strength=0.6, edge_width=0.06, gradient=0.08, highlight=0.6, preview_radius=radius,
              views=[("FRONT 3/4", front + 35, 14), ("FRONT", front, 4), ("SIDE", front + 90, 6), ("TOP", front + 20, 50)])
    a.role("Body", "surface")
    return a


def gold(rough=0.2):
    return Material("gold", color=GOLD, rough=rough, dirt=0.05)


def dark_metal(color=(30, 31, 38)):
    return Material("metal", color=color, rough=0.32, polish=0.7, dirt=0.2, scratches=0.2)


def marble(color=(30, 31, 38), veins=(120, 110, 90)):
    return Material("paint", color=color, under=color, wear=0.0, scratches=0.05, rough=0.15, dirt=0.05, skin=False, decals=[
        {"type": "rect", "center": (x, 0.0), "size": (0.06, 30.0), "angle": a, "color": veins, "rough": 0.1, "wear": 0.6}
        for x, a in ((-2.1, 18), (0.4, -24), (2.6, 32), (-0.8, 61), (1.5, -48))
    ])


def square_pillar(width, height, mat, cap=None, base_mat=None):
    out = []
    out.append(sh.lathe([(0.0, 0.0), (width * 0.72, 0.0), (width * 0.72, height * 0.04), (width * 0.62, height * 0.06), (width * 0.62, height * 0.94), (width * 0.72, height * 0.96), (width * 0.72, height), (0.0, height)], 4, mat, smooth_angle=10, start=45))
    return out
