import numpy as np

from wr3d import Asset
from wr3d import shapes as sh


def rim_asset(name, budget, radius, atlas=512):
    a = Asset(name, budget=budget, atlas=atlas, ao_radius=0.8, ao_strength=0.6, edge_width=0.05, gradient=0.1, highlight=0.4, preview_radius=radius,
              views=[("INSIDE 3/4", 20, 14), ("INSIDE", 0, 4), ("END", 90, 6), ("TOP", 20, 55)])
    a.role("Body", "surface")
    return a


def periodic(phi, span, seed, terms=3):
    rng = np.random.default_rng(seed)
    total = np.zeros_like(phi)
    for k in range(1, terms + 1):
        amp = rng.uniform(0.4, 1.0) / k
        phase = rng.uniform(0, 2 * np.pi)
        total += amp * np.sin(2 * np.pi * k * (phi / span) * 2 + phase)
    return total


def arc_segment(profile, radius, count, mat, seed, arc_steps=14, overlap=1.06, rough=(1.3, 1.9)):
    span = np.radians(360.0 / count)
    arc = 360.0 / count * overlap
    ring = sh.lathe([(radius + dr, y) for dr, y in profile], segments=arc_steps, mat=mat, arc=arc, start=-arc / 2, r_ref=radius)
    p = ring.pos
    theta = np.arctan2(-p[:, 2], p[:, 0])
    r = np.hypot(p[:, 0], p[:, 2])
    height = np.clip((p[:, 1] + 1.0) / 11.0, 0, 1)
    r = r + periodic(theta, span, seed) * rough[0] * height
    y = p[:, 1] + periodic(theta, span, seed + 7, terms=4) * rough[1] * height ** 2
    ring.pos = np.stack([r * np.sin(theta), y, r * np.cos(theta) - radius], -1)
    return sh.recompute_normals(ring)


def colliders(radius, count, inner, outer, top, bottom=-1.0, pieces=2):
    span = np.radians(360.0 / count)
    chord = 2 * radius * np.sin(span / 2)
    width = chord / pieces + 0.8
    mid_r = radius + (inner + outer) / 2
    out = []
    for i in range(pieces):
        angle = ((i + 0.5) / pieces - 0.5) * span
        x = mid_r * np.sin(angle)
        z = mid_r * np.cos(angle) - radius
        out.append({"name": "RimCollider", "shape": "Block", "size": [float(width), float(top - bottom), float(outer - inner)],
                    "center": [float(x), float((top + bottom) / 2), float(z)], "rotation": [0.0, float(np.degrees(angle)), 0.0]})
    return out
