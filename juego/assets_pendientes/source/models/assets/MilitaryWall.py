import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _wall_lib import wall_asset, targets, SEGMENT
from _military_lib import STENCIL, SAND, KHAKI

H = 6.0
PANEL = 4.0


def build():
    a = wall_asset("MilitaryWall", 900, height=H)
    targets(a, ["Zones/Military/Perimeter"])

    profile = [(-1.3, 0.0), (1.3, 0.0), (1.3, 0.6), (0.45, 0.9), (0.35, H), (-0.35, H), (-0.45, 0.9), (-1.3, 0.6)]
    count = int(SEGMENT / PANEL)
    for k in range(count):
        x = -SEGMENT / 2 + (k + 0.5) * PANEL
        tone = (128 + 8 * (k % 3), 126 + 6 * (k % 2), 112)
        concrete = Material("concrete", color=tone, dirt=0.55, decals=[
            {"type": "text", "text": f"B-{k + 11}", "center": (0.0, 2.6), "height": 0.8, "color": STENCIL, "font": "impact", "wear": 0.55, "angle": 90},
            {"type": "rect", "center": (0.0, 5.4), "size": (3.8, 0.05), "darken": 0.4, "raise": -0.006},
        ])
        panel = sh.extrude(np.asarray(profile), PANEL - 0.12, concrete, bevel=0.0, corner_radius=0.0, caps=True)
        a.add("Body", panel.transformed(compose(T(x, 0, 0), R(0, 90, 0), R(0, 0, (k % 3 - 1) * 0.6))))
        a.add("Body", sh.box((0.5, 0.3, 0.25), Material("metal", color=(80, 80, 76), rough=0.5, dirt=0.5)).transformed(T(x, H + 0.15, 0)))
    for k, x in enumerate((-14.0, 9.0)):
        sz = (-1, 1)[k]
        for i in range(3):
            bag = sh.rounded_box((2.2, 0.75, 1.2), 0.0, 1, Material("military_burlap", color=(SAND, KHAKI)[i % 2], dirt=0.5))
            a.add("Body", bag.transformed(compose(T(x + (i - 1) * 2.1, 1.0 + 0.6 * (i == 1), sz * 1.9), R(0, i * 7 - 7, 0))))
    for sz in (-1, 1):
        a.add("Glow", sh.box((SEGMENT, 0.12, 0.1), None).transformed(T(0, 0.75, sz * 1.0)))
    return a
