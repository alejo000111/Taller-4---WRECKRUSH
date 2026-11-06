import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import FROST, expedition_asset
from _landmark_lib import patch

L, H, D = 30.0, 2.0, 16.0


def build():
    a = expedition_asset("DockDeck", 900, 17.0, atlas=512)
    planks = Material("wood", color=(110, 96, 82), dirt=0.5)
    beam = Material("wood", color=(70, 60, 52), dirt=0.6)
    steel = Material("metal", color=(60, 66, 72), rough=0.45, polish=0.3, dirt=0.5)
    snow = Material("terrain_rock", color=(230, 238, 246), cap=(244, 248, 252), cap_amount=1.0, dirt=0.0)
    count = 15
    for k in range(count):
        z = -D / 2 + (k + 0.5) * D / count
        a.add("Body", sh.box((L, 0.4, D / count - 0.1), planks).transformed(compose(T(0, H - 0.2, z), R(0, 0, (k % 3 - 1) * 0.3))))
    for z in (-D / 2 + 0.4, D / 2 - 0.4):
        a.add("Body", sh.box((L, 1.2, 0.6), beam).transformed(T(0, H - 1.0, z)))
    for x in (-L / 2 + 1.0, 0.0, L / 2 - 1.0):
        for z in (-D / 2 + 0.6, D / 2 - 0.6):
            a.add("Body", sh.cylinder(0.45, H, beam, bevel=0.0, segments=6).transformed(T(x, H / 2, z)))
    for x in (-L / 2 + 2.0, L / 2 - 2.0):
        a.add("Body", sh.lathe([(0.0, 0.0), (0.5, 0.0), (0.4, 0.9), (0.6, 1.1), (0.0, 1.2)], 8, steel, smooth_angle=40).transformed(T(x, H, D / 2 - 0.8)))
    a.add("Body", sh.box((6.0, 0.15, 3.0), snow).transformed(compose(T(-8.0, H + 0.05, -4.0), R(0, 12, 0))))
    patch(a, [FROST], ["Dock"], functional=True)
    return a
