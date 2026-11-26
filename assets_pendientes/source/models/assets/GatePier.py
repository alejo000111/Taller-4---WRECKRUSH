from wr3d import Material, T
from wr3d import shapes as sh
from _expedition_lib import ALL, expedition_asset
from _landmark_lib import patch
import _city_lib


def build():
    a = expedition_asset("GatePier", 600, 11.0, atlas=512)
    a.role("Glow", "neon", color=(255, 210, 150))
    stone = Material("city_stone", color=(120, 118, 112), dirt=0.45, streaks=0.4)
    metal = Material("metal", color=(60, 64, 70), rough=0.4, polish=0.4, dirt=0.4)
    a.add("Body", sh.rounded_box((5.0, 2.0, 6.0), 0.12, 1, stone).transformed(T(0, 1.0, 0)))
    a.add("Body", sh.rounded_box((4.0, 15.0, 5.0), 0.1, 1, stone, faces=["+x", "-x", "+z", "-z"]).transformed(T(0, 9.5, 0)))
    for y in (5.0, 10.0, 15.0):
        a.add("Body", sh.box((4.2, 0.5, 5.2), metal).transformed(T(0, y, 0)))
    a.add("Body", sh.rounded_box((4.6, 1.2, 5.6), 0.1, 1, stone).transformed(T(0, 17.6, 0)))
    a.add("Glow", sh.box((0.2, 11.0, 0.2), None).transformed(T(0, 9.5, -2.55)))
    a.add("Glow", sh.box((0.2, 11.0, 0.2), None).transformed(T(0, 9.5, 2.55)))
    a.add("Body", sh.lathe([(0.0, 0.0), (1.2, 0.0), (1.0, 0.6), (0.0, 0.8)], 8, metal, smooth_angle=40).transformed(T(0, 18.2, 0)))
    patch(a, ALL, ["EntryPier"])
    return a
