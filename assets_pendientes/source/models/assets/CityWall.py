import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _wall_lib import wall_asset, targets, post_line, SEGMENT
import _city_lib

H = 6.0
POSTERS = [("SALE", (232, 52, 44)), ("WRECK FM", (34, 160, 255)), ("CONCERT", (166, 77, 255)), ("MEGA MART", (34, 225, 255))]


def build():
    a = wall_asset("CityWall", 900, height=H)
    targets(a, ["Zones/Downtown/Perimeter"])

    brick = Material("city_brick", color=(150, 72, 52), mortar=(170, 162, 150), brick=(1.0, 0.4), gap=0.05, wear=0.3, soot=0.3, dirt=0.45)
    stone = Material("city_stone", color=(190, 186, 176), dirt=0.45, streaks=0.4)
    a.add("Body", sh.rounded_box((SEGMENT, H - 0.6, 1.4), 0.0, 1, brick, faces=["+z", "-z", "+y"]).transformed(T(0, (H - 0.6) / 2, 0)))
    a.add("Body", sh.rounded_box((SEGMENT, 0.4, 2.0), 0.06, 1, stone, faces=["+z", "-z", "+y", "-y"]).transformed(T(0, H - 0.4, 0)))
    a.add("Body", sh.rounded_box((SEGMENT, 0.8, 1.8), 0.0, 1, stone, faces=["+z", "-z", "+y"]).transformed(T(0, 0.4, 0)))
    for x in post_line(SEGMENT, 10.0):
        px = x - 5.0
        a.add("Body", sh.rounded_box((1.6, H + 0.4, 2.2), 0.08, 1, stone, faces=["+x", "-x", "+z", "-z", "+y"]).transformed(T(px, (H + 0.4) / 2, 0)))
        a.add("Body", sh.rounded_box((2.0, 0.4, 2.6), 0.06, 1, stone).transformed(T(px, H + 0.6, 0)))
    for k, x in enumerate((-12.5, 2.5, 12.5)):
        text, color = POSTERS[k]
        for sz in (-1, 1):
            poster = Material("paint", color=color, under=(220, 214, 200), wear=0.45, scratches=0.2, rough=0.7, dirt=0.4, skin=False, decals=[
                {"type": "text", "text": text, "center": (0.0, -0.4), "height": 0.7, "color": (250, 250, 250), "font": "impact", "wear": 0.4},
                {"type": "rect", "center": (0.0, 0.6), "size": (2.2, 0.9), "color": (24, 24, 30), "wear": 0.4},
                {"type": "rect", "center": (0.9, -1.2), "size": (0.5, 0.5), "angle": 18, "color": (240, 236, 224), "wear": 0.2},
            ])
            face = "-z" if sz < 0 else "+z"
            sheet = sh.rounded_box((2.8, 3.2, 0.03), 0.0, 1, poster, faces=[face])
            a.add("Body", sheet.transformed(compose(T(x + sz * 1.6, 3.0, sz * 0.73), R(0, 0, sz * 2))))
    a.add("Glow", sh.box((SEGMENT, 0.12, 2.1), None).transformed(T(0, H - 0.15, 0)))
    return a
