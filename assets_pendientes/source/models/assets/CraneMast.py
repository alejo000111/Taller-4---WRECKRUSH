from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import FROST, expedition_asset
from _landmark_lib import patch

H = 46.0


def build():
    a = expedition_asset("CraneMast", 1200, 24.0, atlas=512)
    paint = Material("paint", color=(239, 153, 94), under=(110, 100, 90), wear=0.4, scratches=0.4, rough=0.45, dirt=0.45, skin=False)
    steel = Material("metal", color=(60, 66, 72), rough=0.45, polish=0.3, dirt=0.5)
    for x in (-2.2, 2.2):
        for z in (-2.2, 2.2):
            a.add("Body", sh.box((0.6, H, 0.6), paint).transformed(T(x, H / 2, z)))
    step = 4.0
    y = 2.0
    while y < H - 2.0:
        for side in range(4):
            a.add("Body", sh.box((0.3, 6.0, 0.3), paint).transformed(compose(R(0, side * 90, 0), T(0, y + 2.0, 2.2), R(0, 0, 47 if (y / step) % 2 < 1 else -47))))
        for side in range(4):
            a.add("Body", sh.box((4.4, 0.3, 0.3), paint).transformed(compose(R(0, side * 90, 0), T(0, y, 2.2))))
        y += step
    a.add("Body", sh.box((6.0, 1.0, 6.0), steel).transformed(T(0, 0.5, 0)))
    a.add("Body", sh.box((5.4, 2.0, 5.4), steel).transformed(T(0, H - 1.0, 0)))
    patch(a, [FROST], ["CraneTower"])
    return a
