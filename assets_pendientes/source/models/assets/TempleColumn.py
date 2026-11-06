from wr3d import Material, T
from wr3d import shapes as sh
from _expedition_lib import SKY, expedition_asset
from _temple_lib import marble, fluted, plinth, GOLD
from _landmark_lib import patch

H = 39.0


def build():
    a = expedition_asset("TempleColumn", 900, 21.0, atlas=512)
    a.role("Glow", "neon", color=GOLD)
    stone = marble()
    a.add("Body", plinth(9.0, 1.4, stone))
    a.add("Body", plinth(8.0, 1.0, stone, 1.4))
    a.add("Body", sh.lathe([(3.6, 2.4), (3.9, 2.9), (3.3, 3.3)], 16, stone, smooth_angle=50))
    a.add("Body", fluted(3.2, H - 7.6, stone).transformed(T(0, 3.3, 0)))
    a.add("Body", sh.lathe([(3.3, H - 4.3), (3.9, H - 3.6), (4.2, H - 3.0)], 16, stone, smooth_angle=50))
    a.add("Body", plinth(9.0, 1.6, stone, H - 3.0))
    a.add("Body", plinth(8.0, 1.4, stone, H - 1.4))
    a.add("Glow", sh.lathe([(3.28, 6.0), (3.4, 6.0), (3.4, 6.5), (3.28, 6.5)], 16, None, closed=True, smooth_angle=50))
    patch(a, [SKY], ["TemplePier"])
    return a
