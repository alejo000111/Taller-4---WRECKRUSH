import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh


def ground_asset(name, budget, radius, atlas=512):
    a = Asset(name, budget=budget, atlas=atlas, ao_radius=0.3, ao_strength=0.3, edge_width=0.03, gradient=0.0, highlight=0.3, preview_radius=radius,
              views=[("TOP 3/4", 35, 40), ("TOP", 0, 85), ("LOW", 90, 12), ("TOP 3/4 B", 215, 40)])
    a.role("Body", "surface")
    return a


def blob(seed, rx, rz, points=28, rough=0.22):
    rng = np.random.default_rng(seed)
    angles = np.linspace(0, 2 * np.pi, points, endpoint=False)
    k = np.arange(1, 5)
    phase = rng.uniform(0, 2 * np.pi, len(k))
    amp = rng.uniform(0.3, 1.0, len(k)) / k
    wobble = sum(a * np.sin(kk * angles + ph) for a, kk, ph in zip(amp, k, phase))
    wobble = wobble / np.abs(wobble).max() * rough
    jitter = rng.normal(0, rough * 0.25, points)
    r = 1.0 + wobble + jitter
    return np.stack([np.cos(angles) * rx * r, np.sin(angles) * rz * r], 1)


def slab(polygon, thickness, top, side=None, y=0.0):
    prism = sh.extrude(np.asarray(polygon), thickness, side or top, bevel=0.0, corner_radius=0.0, smooth_angle=60, cap_mats=[top, top])
    return prism.transformed(compose(T(0, y + thickness / 2, 0), R(-90, 0, 0)))


def circle(radius, segments=32):
    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    return np.stack([np.cos(angles) * radius, np.sin(angles) * radius], 1)


def ring(r_in, r_out, thickness, mat, y=0.0, segments=32):
    profile = [(r_out, 0.0), (r_out, thickness), (r_in, thickness)]
    return sh.lathe(profile, segments, mat, smooth_angle=30).transformed(T(0, y, 0))


def zigzag(length, width, seed, count=14):
    rng = np.random.default_rng(seed)
    zs = np.linspace(-length / 2, length / 2, count)
    xs = rng.uniform(-0.5, 0.5, count) * width * 0.6
    xs[0] = xs[-1] = 0.0
    return np.stack([xs, zs], 1)
