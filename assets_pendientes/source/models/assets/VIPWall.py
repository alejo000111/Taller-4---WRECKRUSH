import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _wall_lib import wall_asset, targets, post_line, SEGMENT

H = 6.0


def build():
    a = wall_asset("VIPWall", 900, height=H)
    targets(a, ["VIPArea/Perimeter"])

    marble = Material("paint", color=(24, 22, 28), under=(24, 22, 28), wear=0.0, scratches=0.05, rough=0.15, metal=0.0, dirt=0.05, skin=False, decals=[
        *[{"type": "rect", "center": (x, 0.0), "size": (0.12, 4.4), "color": (230, 180, 60), "metal": 1.0, "rough": 0.2, "wear": 0.0} for x in (-15.0, -5.0, 5.0, 15.0)],
        *[{"type": "text", "text": "VIP", "center": (x, 0.0), "height": 1.4, "color": (240, 196, 70), "font": "impact", "metal": 1.0, "rough": 0.2, "wear": 0.0} for x in (-10.0, 10.0)],
    ])
    gold = Material("gold", color=(255, 196, 40), rough=0.2, dirt=0.05)
    a.add("Body", sh.rounded_box((SEGMENT, H - 1.0, 1.4), 0.0, 1, marble, faces=["+z", "-z"]).transformed(T(0, (H - 1.0) / 2 + 0.5, 0)))
    a.add("Body", sh.rounded_box((SEGMENT, 0.5, 1.9), 0.08, 1, gold).transformed(T(0, H - 0.25, 0)))
    a.add("Body", sh.rounded_box((SEGMENT, 0.5, 1.9), 0.08, 1, gold, faces=["+y", "+z", "-z"]).transformed(T(0, 0.25, 0)))
    for x in post_line(SEGMENT, 10.0):
        a.add("Body", sh.rounded_box((1.4, H + 0.6, 2.0), 0.1, 1, gold, faces=["+x", "-x", "+z", "-z", "+y"]).transformed(T(x - 5.0, (H + 0.6) / 2, 0)))
        a.add("Glow", sh.sphere(0.45, None, 8, 5).transformed(T(x - 5.0, H + 1.05, 0)))
    return a
