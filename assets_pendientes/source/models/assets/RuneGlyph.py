from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import SKY, expedition_asset
from _landmark_lib import patch


def build():
    a = expedition_asset("RuneGlyph", 150, 3.0, atlas=256)
    a.role("Glow", "neon", color=(245, 199, 116))
    plate = Material("metal", color=(70, 66, 86), rough=0.4, polish=0.4, dirt=0.4)
    a.add("Body", sh.box((4.0, 0.08, 1.0), plate).transformed(T(0, 0.04, 0)))
    for x, ang in ((-1.3, 0), (-0.5, 35), (0.3, -35), (1.2, 90)):
        a.add("Glow", sh.box((0.6, 0.06, 0.1), None).transformed(compose(T(x, 0.1, 0), R(0, ang, 0))))
    patch(a, [SKY], ["Rune"], keep_height=True, tint=["Glow"])
    return a
