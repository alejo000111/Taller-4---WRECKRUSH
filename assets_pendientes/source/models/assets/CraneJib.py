from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import FROST, expedition_asset
from _landmark_lib import patch

L, H, D = 39.0, 4.0, 5.0


def build():
    a = expedition_asset("CraneJib", 900, 21.0, atlas=512)
    paint = Material("paint", color=(239, 153, 94), under=(110, 100, 90), wear=0.4, scratches=0.4, rough=0.45, dirt=0.45, skin=False)
    steel = Material("metal", color=(60, 66, 72), rough=0.45, polish=0.3, dirt=0.5)
    for y in (0.3, H - 0.3):
        for z in (-D / 2 + 0.3, D / 2 - 0.3):
            a.add("Body", sh.box((L, 0.5, 0.5), paint).transformed(T(0, y, z)))
    k = 0
    x = -L / 2 + 1.5
    while x < L / 2 - 1.0:
        for z in (-D / 2 + 0.3, D / 2 - 0.3):
            a.add("Body", sh.box((0.25, H * 1.2, 0.25), paint).transformed(compose(T(x, H / 2, z), R(0, 0, 40 if k % 2 else -40))))
        a.add("Body", sh.box((0.25, 0.25, D), paint).transformed(T(x, H - 0.3, 0)))
        x += 3.0
        k += 1
    a.add("Body", sh.box((2.4, 1.6, 2.4), steel).transformed(T(-L / 2 + 1.2, -0.6, 0)))
    a.add("Body", sh.box((5.0, 3.0, 4.6), Material("metal", color=(80, 86, 92), rough=0.4, dirt=0.5)).transformed(T(L / 2 - 2.5, H / 2, 0)))
    patch(a, [FROST], ["CraneArm"])
    return a
