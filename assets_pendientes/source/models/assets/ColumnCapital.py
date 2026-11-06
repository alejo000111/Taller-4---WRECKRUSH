from wr3d import T
from wr3d import shapes as sh
from _expedition_lib import SKY, expedition_asset
from _temple_lib import marble
from _landmark_lib import patch


def build():
    a = expedition_asset("ColumnCapital", 400, 5.0, atlas=256)
    stone = marble((210, 180, 120), (240, 220, 170))
    a.add("Body", sh.lathe([(0.0, 0.0), (2.6, 0.0), (3.2, 0.9), (3.6, 1.6)], 12, stone, smooth_angle=50))
    a.add("Body", sh.rounded_box((8.0, 1.4, 8.0), 0.12, 1, stone).transformed(T(0, 2.3, 0)))
    for x in (-3.4, 3.4):
        a.add("Body", sh.torus(0.7, 0.28, stone, segments=10, sides=4).transformed(T(x, 1.6, 0)).transformed(T(0, 0, 0)))
    patch(a, [SKY], ["Capital"])
    return a
