import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh


def pet_asset(name, budget, radius=3.0):
    a = Asset(name, budget=budget, atlas=512, ao_radius=0.18, ao_strength=0.55, edge_width=0.025, gradient=0.12, highlight=0.6, preview_radius=radius,
              views=[("FRONT 3/4", 215, 14), ("FRONT", 180, 6), ("SIDE", 270, 6), ("BACK 3/4", 35, 20)])
    a.role("Body", "surface")
    a.meta["pet"] = {}
    return a


def blob(size, mat, segments=12, rings=8):
    ball = sh.sphere(1.0, mat, segments, rings)
    ball.pos *= np.asarray(size) / 2.0
    return sh.recompute_normals(ball)


def eye(radius, mat=None, segments=8, rings=5):
    return sh.sphere(radius, mat, segments, rings)


def plastic(color, **extra):
    params = dict(color=color, rough=0.4, scuff=0.3, scratches=0.15, dirt=0.15)
    params.update(extra)
    return Material("plastic", **params)


def metal(color, **extra):
    params = dict(color=color, rough=0.35, polish=0.6, dirt=0.25, scratches=0.35)
    params.update(extra)
    return Material("metal", **params)


def painted(color, decals=(), **extra):
    params = dict(color=color, under=(120, 122, 128), wear=0.3, scratches=0.3, rough=0.4, dirt=0.25, skin=False, decals=list(decals))
    params.update(extra)
    return Material("paint", **params)


def leg(length, radius, mat, foot=None):
    out = [sh.lathe([(0.0, 0.0), (radius * 1.25, 0.0), (radius * 1.2, radius * 0.6), (radius, radius * 1.1), (radius * 0.9, length), (0.0, length)], 8, mat, smooth_angle=40)]
    return out
