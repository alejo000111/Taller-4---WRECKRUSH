from wr3d import T
from wr3d import shapes as sh
from _expedition_lib import SKY, expedition_asset
from _temple_lib import marble, fluted, broken_top
from _landmark_lib import patch

H = 20.0


def build():
    a = expedition_asset("BrokenColumn", 600, 12.0, atlas=512)
    stone = marble((131, 129, 151))
    a.add("Body", sh.lathe([(0.0, 0.0), (3.2, 0.0), (3.2, 0.8), (2.6, 1.3), (2.5, 1.4)], 14, stone, smooth_angle=50))
    a.add("Body", fluted(2.5, H - 2.4, stone, flutes=10, depth=0.1).transformed(T(0, 1.4, 0)))
    a.add("Body", broken_top(2.5, H - 1.0, stone, 5))
    patch(a, [SKY], ["BrokenPillar"])
    return a
