import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh

SEGMENT = 40.0


def wall_asset(name, budget, height=6.0, thickness=2.0, segment=SEGMENT, glow_source="WallGlow"):
    a = Asset(name, budget=budget, atlas=1024, ao_radius=0.8, edge_width=0.06, preview_radius=segment * 0.42,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 16), ("FRONT", 180, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 122, 26))
    a.meta["wall"] = {
        "segment": segment,
        "height": height,
        "thickness": thickness,
        "glow": glow_source,
        "targets": [],
        "part": "Wall",
    }
    return a


def targets(asset, paths, part="Wall", glow="WallGlow"):
    asset.meta["wall"]["targets"] = list(paths)
    asset.meta["wall"]["part"] = part
    asset.meta["wall"]["glow"] = glow
    return asset


def corrugated_panel(width, height, depth, pitch, mat):
    count = max(2, int(round(width / pitch)))
    step = width / count
    pts = []
    for i in range(count):
        x0 = -width / 2 + i * step
        pts += [(x0, -depth / 2), (x0 + step * 0.2, -depth / 2), (x0 + step * 0.5, depth / 2), (x0 + step * 0.7, depth / 2)]
    pts.append((width / 2, -depth / 2))
    outline = pts + [(x, z + 0.08) for x, z in reversed(pts)]
    strip = sh.extrude(np.asarray(outline), height, mat, bevel=0.0, corner_radius=0.0, smooth_angle=60, caps=False)
    return strip.transformed(compose(T(0, height / 2, 0), R(-90, 0, 0)))


def post_line(segment, spacing):
    count = int(round(segment / spacing))
    return [-segment / 2 + (i + 0.5) * spacing for i in range(count)]
