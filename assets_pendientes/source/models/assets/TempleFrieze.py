from wr3d import Material, T
from wr3d import shapes as sh
from _expedition_lib import SKY, expedition_asset
from _landmark_lib import patch

W, H, L = 15.0, 1.0, 73.0


def build():
    a = expedition_asset("TempleFrieze", 300, 38.0, atlas=256, front=270)
    a.role("Glow", "neon", color=(173, 161, 230))
    for x in (-W / 2 + 0.2, W / 2 - 0.2):
        a.add("Glow", sh.box((0.15, 0.25, L - 1.0), None).transformed(T(x, H / 2, 0)))
    for z in (-L / 2 + 0.2, L / 2 - 0.2):
        a.add("Glow", sh.box((W - 1.0, 0.25, 0.15), None).transformed(T(0, H / 2, z)))
    a.add("Body", sh.box((0.02, 0.02, 0.02), Material("metal", color=(80, 80, 90))).transformed(T(W / 2 - 0.01, 0.01, L / 2 - 0.01)))
    a.add("Body", sh.box((0.02, 0.02, 0.02), Material("metal", color=(80, 80, 90))).transformed(T(-W / 2 + 0.01, H - 0.01, -L / 2 + 0.01)))
    patch(a, [SKY], ["TempleFrieze"], tint=["Glow"])
    return a
