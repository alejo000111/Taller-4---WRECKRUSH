from wr3d import T
from wr3d import shapes as sh
from _expedition_lib import SKY, expedition_asset
from _temple_lib import marble
from _landmark_lib import patch


def build():
    a = expedition_asset("MarbleStep", 100, 14.0, atlas=256)
    stone = marble((150, 146, 168))
    a.add("Body", sh.rounded_box((24.0, 0.5, 5.0), 0.08, 1, stone, faces=["+y", "+x", "-x", "+z", "-z"]).transformed(T(0, 0.25, 0)))
    patch(a, [SKY], ["TempleStep"])
    return a
