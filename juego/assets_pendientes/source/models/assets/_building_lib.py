from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
import _city_lib
import _skyline_lib

IMMERSION = "Decor/ImmersionPass_20261005"


def building_asset(name, budget, radius, atlas=1024):
    a = Asset(name, budget=budget, atlas=atlas, ao_radius=1.2, ao_strength=0.6, edge_width=0.08, gradient=0.08, highlight=0.45, preview_radius=radius,
              views=[("FRONT 3/4", 35, 14), ("FRONT", 0, 4), ("SIDE", 90, 6), ("TOP", 20, 50)])
    a.role("Body", "surface")
    return a


def steel(color=(70, 76, 86), dirt=0.4):
    return Material("metal", color=color, rough=0.42, polish=0.4, dirt=dirt, scratches=0.35)


def panel(color, decals=(), wear=0.3):
    return Material("paint", color=color, under=(120, 124, 130), wear=wear, scratches=0.35, rough=0.45, dirt=0.4, skin=False, decals=list(decals))


def trim_paint():
    return Material("paint", color=(255, 255, 255), under=(110, 112, 118), wear=0.35, scratches=0.4, rough=0.4, dirt=0.35, skin=True)


def louvre(width, height, slats, mat_frame, mat_slat, depth=0.3):
    parts = [sh.rounded_box((width + 0.3, height + 0.3, 0.12), 0.02, 1, mat_frame, faces=["+z", "+x", "-x", "+y", "-y"]).transformed(T(0, 0, -depth / 2))]
    for k in range(slats):
        y = -height / 2 + (k + 0.5) * height / slats
        parts.append(sh.box((width, 0.05, 0.34), mat_slat).transformed(compose(T(0, y, 0), R(35, 0, 0))))
    return parts
