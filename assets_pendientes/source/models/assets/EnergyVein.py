import numpy as np

from wr3d import Material, T
from _ground_lib import ground_asset, slab, zigzag
from _landmark_lib import patch

LENGTH = 60.0


def ribbon(path, width):
    p = np.asarray(path)
    d = np.gradient(p, axis=0)
    d = d / np.linalg.norm(d, axis=1, keepdims=True)
    n = np.stack([-d[:, 1], d[:, 0]], 1)
    left = p + n * width / 2
    right = p - n * width / 2
    return np.concatenate([left, right[::-1]])


def build():
    a = ground_asset("EnergyVein", 300, 32.0)
    a.role("Glow", "neon", color=(166, 77, 255))
    scorch = Material("glossy", color=(22, 14, 30), rough=0.35, metal=0.0, dirt=0.3)
    path = zigzag(LENGTH, 0.6, 5, count=16)
    a.add("Body", slab(ribbon(path, 0.36), 0.03, scorch))
    a.add("Glow", slab(ribbon(path, 0.14), 0.05, None))
    patch(a, ["Zones/ChaosCore/GroundDetail"], ["EnergyVein"], keep_height=True, tint=["Glow"])
    return a
