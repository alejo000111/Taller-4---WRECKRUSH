import numpy as np

from wr3d import Asset, Material, T
from wr3d import shapes as sh
import _expedition_lib


def backdrop_asset(name, budget, radius):
    a = Asset(name, budget=budget, atlas=1024, ao_radius=6.0, ao_strength=0.6, edge_width=0.0, gradient=0.15, highlight=0.3, preview_radius=radius,
              views=[("FRONT 3/4", 215, 12), ("FRONT", 180, 4), ("SIDE", 270, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    return a


def noise2(x, z, seed, octaves=4):
    rng = np.random.default_rng(seed)
    total = np.zeros_like(x)
    amp, freq = 1.0, 1.0
    for _ in range(octaves):
        px, pz, phase = rng.uniform(0, 100, 3)
        angle = rng.uniform(0, np.pi)
        u = x * np.cos(angle) - z * np.sin(angle)
        v = x * np.sin(angle) + z * np.cos(angle)
        total += amp * (np.sin(u * freq + px) * np.cos(v * freq * 1.3 + pz) + 0.5 * np.sin((u + v) * freq * 0.7 + phase))
        amp *= 0.5
        freq *= 2.1
    return total


def heightfield(width, depth, nx, nz, mat, height_fn):
    grid = sh.plane((width, depth), mat, divisions=(nx, nz))
    x = grid.pos[:, 0] / (width / 2)
    z = grid.pos[:, 2] / (depth / 2)
    grid.pos[:, 1] = height_fn(x, z)
    edge = (np.abs(x) > 0.999) | (np.abs(z) > 0.999)
    grid.pos[edge, 1] = -4.0
    return sh.recompute_normals(grid)


def peaks(x, z, seed, count=3, sharp=1.6, base=0.0):
    rng = np.random.default_rng(seed)
    h = np.zeros_like(x)
    for k in range(count):
        cx, cz = rng.uniform(-0.45, 0.45), rng.uniform(-0.35, 0.35)
        rad = rng.uniform(0.45, 0.75)
        amp = rng.uniform(0.6, 1.0) if k else 1.0
        d = np.sqrt((x - cx) ** 2 + ((z - cz) * 1.3) ** 2) / rad
        h = np.maximum(h, amp * np.clip(1 - d, 0, 1) ** sharp)
    falloff = np.clip(1 - np.maximum(np.abs(x), np.abs(z)) ** 6, 0, 1)
    return np.clip(h + base, 0, None) * falloff
