import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _wall_lib import wall_asset, targets, post_line, SEGMENT
from _station_lib import steel, painted, YELLOW, INK

H = 6.0
BASE_H = 3.4


def build():
    a = wall_asset("FactoryWall", 900, height=H)
    targets(a, ["Zones/Industrial/Perimeter"])

    concrete = Material("concrete", color=(150, 148, 142), dirt=0.55, decals=[
        {"type": "stripes", "center": (0.0, 1.35), "size": (SEGMENT, 0.7), "width": 0.6, "color": YELLOW, "wear": 0.45},
        *[{"type": "rect", "center": (x, 0.0), "size": (0.06, BASE_H), "darken": 0.55, "raise": -0.008} for x in np.linspace(-SEGMENT / 2 + 5.0, SEGMENT / 2 - 5.0, 4)],
        {"type": "text", "text": "AREA 3", "center": (-15.0, -0.3), "height": 0.8, "color": (40, 40, 44), "font": "impact", "wear": 0.5},
        {"type": "text", "text": "HARD HAT ZONE", "center": (5.0, -0.3), "height": 0.6, "color": (40, 40, 44), "font": "impact", "wear": 0.5},
    ])
    profile = [(-1.0, 0.0), (1.0, 0.0), (0.95, 0.5), (0.5, 1.0), (0.4, BASE_H), (-0.4, BASE_H), (-0.5, 1.0), (-0.95, 0.5)]
    barrier = sh.extrude(np.asarray(profile), SEGMENT, concrete, bevel=0.04, corner_radius=0.0, caps=False)
    a.add("Body", barrier.transformed(R(0, 90, 0)))
    rail = painted(YELLOW, [{"type": "stripes", "center": (0.0, 0.0), "size": (SEGMENT, 0.4), "width": 0.6, "color": INK, "wear": 0.35}])
    post = steel((70, 72, 80))
    for x in post_line(SEGMENT, 8.0):
        a.add("Body", sh.cylinder(0.14, H - BASE_H + 0.2, post, bevel=0.0, segments=6).transformed(T(x - 4.0, (H + BASE_H) / 2, 0)))
    for y in (BASE_H + 1.2, H - 0.1):
        a.add("Body", sh.cylinder(0.12, SEGMENT, rail, bevel=0.0, segments=6).transformed(compose(T(0, y, 0), R(0, 0, 90))))
    mesh = Material("metal", color=(120, 124, 132), rough=0.4, polish=0.4, dirt=0.4, decals=[
        *[{"type": "rect", "center": (x, 0.0), "size": (0.05, 3.0), "angle": 45, "darken": 0.8, "raise": -0.004} for x in np.linspace(-SEGMENT / 2, SEGMENT / 2, 61)],
        *[{"type": "rect", "center": (x, 0.0), "size": (0.05, 3.0), "angle": -45, "darken": 0.8, "raise": -0.004} for x in np.linspace(-SEGMENT / 2, SEGMENT / 2, 61)],
    ])
    a.add("Body", sh.rounded_box((SEGMENT, H - BASE_H - 0.3, 0.04), 0.0, 1, mesh, faces=["+z", "-z"]).transformed(T(0, (H + BASE_H) / 2 + 0.05, 0)))
    for sz in (-1, 1):
        a.add("Glow", sh.box((SEGMENT, 0.14, 0.1), None).transformed(T(0, BASE_H - 0.3, sz * 0.42)))
    return a
