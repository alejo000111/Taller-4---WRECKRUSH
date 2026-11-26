from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel
from _bay_lib import DESIGN
from _chaos_lib import basalt, obsidian, crystal, VIOLET
from _landmark_lib import landmark


def build():
    a = building_asset("ChaosServiceDetail", 1100, 10.0, atlas=512)
    a.role("Glow", "neon", color=VIOLET)
    stone = basalt(veins=0.8)
    cap = obsidian() if callable(obsidian) else stone
    metal = steel((47, 60, 75))
    for x in (-8.0, 8.0):
        post = sh.lathe([(0.0, 0.0), (0.8, 0.0), (0.75, 1.0), (0.6, 8.6), (0.75, 9.4), (0.0, 9.4)], 6, stone, smooth_angle=20, start=30)
        a.add("Body", post.transformed(T(x, 0.0, 0.0)))
        a.add("Glow", sh.box((0.16, 5.0, 0.16), None).transformed(T(x, 5.0, 0.72)))
        a.add("Glow", crystal(0.35, 1.4, None, facets=4).transformed(T(x, 9.4, 0.0)))
    a.add("Body", sh.rounded_box((18.0, 0.6, 2.0), 0.08, 1, cap).transformed(T(0, 10.0, 0.0)))
    for x in (-4.0, 0.0, 4.0):
        a.add("Body", sh.box((0.5, 0.5, 2.1), metal).transformed(T(x, 10.0, 0.0)))
    a.add("Glow", sh.box((16.0, 0.1, 0.1), None).transformed(T(0, 9.62, 0.95)))
    landmark(a, DESIGN, "ChaosService_Detail", fit="box", tint={"Glow": "ContainmentAccent"})
    return a
