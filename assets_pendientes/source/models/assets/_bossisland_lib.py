import numpy as np

from wr3d import Asset, Material
from wr3d import shapes as sh
from wr3d import T
from _expedition_lib import terrain_rock, boulder
from _rim_lib import rim_asset, arc_segment, colliders
import ScrapWall
import _chaos_lib
import _military_lib

ROOT = "BossIslands"
CENTERS = {
    "ScrapColossus": (0.0, 4800.0),
    "DowntownCrusher": (4080.0, 2400.0),
    "IndustrialTitan": (4080.0, -2400.0),
    "MilitaryWarden": (0.0, -4800.0),
    "VoidSentinel": (-4080.0, -2400.0),
    "ChaosOverlord": (-4080.0, 2400.0),
}
PATHS = [f"{ROOT}/{island}" for island in CENTERS]
RIM_RADIUS = 146.0
RIM_COUNT = 24
FLOOR_RADIUS = 150.0

ROCK = {
    "ScrapColossus": dict(color=(96, 74, 62), cap=(120, 92, 70), cap_amount=0.3, strata=1.8, dirt=0.5),
    "DowntownCrusher": dict(color=(84, 84, 90), cap=(110, 108, 104), cap_amount=0.25, strata=1.2, dirt=0.4),
    "IndustrialTitan": dict(color=(78, 70, 66), cap=(120, 70, 50), cap_amount=0.3, strata=2.2, dirt=0.6),
    "MilitaryWarden": dict(color=(82, 86, 72), cap=(96, 104, 70), cap_amount=0.45, strata=1.4, dirt=0.4),
    "VoidSentinel": dict(color=(48, 40, 66), cap=(120, 80, 190), cap_amount=0.2, strata=1.0, dirt=0.2),
    "ChaosOverlord": dict(color=(42, 30, 46), cap=(200, 80, 150), cap_amount=0.2, strata=2.6, dirt=0.3),
}

RIMS = {
    "ScrapColossus": (lambda: Material("scrapwall_sheet", color=(120, 84, 62)), [(5.0, -12.0), (4.0, -3.0), (3.0, 4.0), (2.2, 9.0), (0.8, 11.0), (-0.8, 10.4), (-2.2, 8.0), (-2.8, 3.0), (-3.2, 0.2), (-3.0, -1.5)], (1.8, 2.6)),
    "DowntownCrusher": (lambda: Material("concrete", color=(150, 150, 146), dirt=0.6), [(5.0, -12.0), (4.2, -3.0), (3.4, 2.0), (1.6, 3.4), (1.2, 9.6), (-1.2, 9.6), (-1.6, 3.4), (-3.2, 1.6), (-3.4, 0.2), (-3.2, -1.5)], (0.2, 0.3)),
    "IndustrialTitan": (lambda: Material("diamondplate", color=(118, 112, 106), dirt=0.6), [(5.0, -12.0), (4.0, -2.0), (1.8, 0.4), (1.6, 10.0), (0.6, 10.6), (-1.2, 10.6), (-1.6, 9.6), (-1.6, 1.0), (-3.0, 0.4), (-3.0, -1.5)], (0.15, 0.2)),
    "MilitaryWarden": (lambda: Material("military_burlap"), [(5.0, -12.0), (4.4, -2.0), (3.6, 2.0), (3.2, 5.6), (2.4, 9.0), (0.0, 10.4), (-2.4, 9.0), (-3.0, 5.0), (-3.4, 1.0), (-3.2, -1.5)], (0.6, 0.6)),
    "VoidSentinel": (lambda: Material("chaos_obsidian"), [(5.0, -12.0), (3.6, -2.0), (2.4, 5.0), (1.0, 12.0), (-0.6, 11.4), (-1.8, 7.0), (-2.8, 2.0), (-3.2, 0.2), (-3.0, -1.5)], (1.6, 3.4)),
    "ChaosOverlord": (lambda: Material("chaos_basalt"), [(5.0, -12.0), (4.0, -2.0), (3.0, 5.0), (1.6, 10.6), (0.0, 12.4), (-1.4, 10.0), (-2.6, 5.0), (-3.2, 0.4), (-3.0, -1.5)], (2.0, 3.0)),
}


def rim(name, island, seed):
    mat_factory, profile, rough = RIMS[island]
    a = rim_asset(name, 320, 26.0)
    a.add("Body", arc_segment(profile, RIM_RADIUS, RIM_COUNT, mat_factory(), seed, rough=rough))
    cx, cz = CENTERS[island]
    a.meta["rim"] = {"targets": [{"path": f"{ROOT}/{island}", "center": [cx, cz]}], "radius": RIM_RADIUS, "count": RIM_COUNT, "offset": 0.5,
                     "colliders": colliders(RIM_RADIUS, RIM_COUNT, -3.2, 2.0, 10.5)}
    return a


def underside(name, island, seed):
    a = Asset(name, budget=2600, atlas=1024, ao_radius=4.0, ao_strength=0.6, edge_width=0.2, gradient=0.2, highlight=0.3, preview_radius=170.0,
              views=[("SIDE", 200, 4), ("BELOW", 200, -40), ("SIDE 2", 290, 4), ("TOP", 200, 60)])
    a.role("Body", "surface")
    rock = Material("terrain_rock", **ROCK[island])
    profile = [(0.0, -150.0), (22.0, -138.0), (60.0, -104.0), (98.0, -64.0), (128.0, -30.0), (146.0, -10.0), (FLOOR_RADIUS + 1.5, -1.5), (FLOOR_RADIUS - 2.0, -0.4)]
    body = sh.lathe(profile, 36, rock, smooth_angle=50)
    rng = np.random.default_rng(seed)
    p = body.pos
    radial = np.hypot(p[:, 0], p[:, 2])
    angle = np.arctan2(p[:, 2], p[:, 0])
    depth = np.clip(-p[:, 1] / 150.0, 0, 1)
    wobble = np.zeros(len(p))
    for k in range(1, 6):
        wobble += rng.uniform(0.4, 1.0) / k * np.sin(angle * (k * 2 + 1) + rng.uniform(0, 6.28) + p[:, 1] * 0.03 * k)
    scale = 1 + 0.26 * wobble * np.sin(np.pi * depth) + rng.normal(0, 0.06, len(p)) * depth
    p[:, 0] *= scale
    p[:, 2] *= scale
    p[:, 1] += rng.normal(0, 3.0, len(p)) * depth * (radial > 1)
    body.pos = p
    a.add("Body", sh.recompute_normals(body))
    for k in range(10):
        angle = rng.uniform(0, 2 * np.pi)
        depth = rng.uniform(30.0, 95.0)
        radius = 150.0 * (1 - depth / 150.0) * rng.uniform(1.0, 1.1)
        size = (rng.uniform(16, 30), rng.uniform(22, 40), rng.uniform(16, 30))
        rock_mesh = boulder(seed + k, size, rock, segments=8, rings=5, amount=0.2)
        rock_mesh.pos[:, 1] *= -1
        rock_mesh.tri = rock_mesh.tri[:, ::-1].copy()
        a.add("Body", sh.recompute_normals(rock_mesh).transformed(T(np.cos(angle) * radius, -depth + size[1] * 0.3, np.sin(angle) * radius)))
    cx, cz = CENTERS[island]
    a.meta["place"] = {"targets": [{"path": f"{ROOT}/{island}", "center": [cx, 0.0, cz], "yaw": float(seed % 360)}]}
    return a
