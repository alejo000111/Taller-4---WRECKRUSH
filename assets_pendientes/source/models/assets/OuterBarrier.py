import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _wall_lib import wall_asset, targets, SEGMENT
from _station_lib import YELLOW, INK

H = 3.0
UNIT = 10.0


def build():
    a = wall_asset("OuterBarrier", 900, height=H, glow_source="OuterBarrierGlow")
    targets(a, ["Decor/Boundary"], part="OuterBarrier", glow="OuterBarrierGlow")

    profile = [(-1.0, 0.0), (1.0, 0.0), (0.95, 0.35), (0.45, 1.0), (0.3, H), (-0.3, H), (-0.45, 1.0), (-0.95, 0.35)]
    count = int(SEGMENT / UNIT)
    for k in range(count):
        x = -SEGMENT / 2 + (k + 0.5) * UNIT
        concrete = Material("concrete", color=(176, 172, 162), dirt=0.55, decals=[
            {"type": "stripes", "center": (0.0, 0.55), "size": (UNIT, 0.6), "width": 0.55, "color": YELLOW if k % 2 == 0 else (230, 60, 40), "wear": 0.45},
            {"type": "text", "text": "WRECKRUSH", "center": (0.0, -0.45), "height": 0.5, "color": (60, 60, 64), "font": "impact", "wear": 0.5},
        ])
        block = sh.extrude(np.asarray(profile), UNIT - 0.15, concrete, bevel=0.05, corner_radius=0.0)
        a.add("Body", block.transformed(compose(T(x, 0, 0), R(0, 90, 0))))
        for sz in (-1, 1):
            a.add("Glow", sh.box((0.5, 0.25, 0.05), None).transformed(T(x, 2.2, sz * 0.36)))
    return a
