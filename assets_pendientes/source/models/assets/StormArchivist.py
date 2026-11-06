import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _boss_lib import boss_asset, skeleton, head, core_gear, arm
from _destructible import animate
from _temple_lib import marble


def feather(length, width, mat):
    pts = [(0.0, -width / 2), (length * 0.7, -width / 2), (length, 0.0), (length * 0.7, width / 2), (0.0, width / 2)]
    return sh.extrude(np.asarray(pts), 0.6, mat, bevel=0.1, corner_radius=0.0)


def build():
    a = boss_asset("StormArchivist", 6000, (245, 199, 116), (173, 161, 230))
    a.role("WingL", "surface")
    a.role("WingR", "surface")
    a.role("Halo", "neon", color=(245, 199, 116))
    animate(a, "WingL", "Wing")
    animate(a, "WingR", "Wing")
    stone = marble((120, 120, 150), (190, 186, 220))
    gold = Material("gold", color=(245, 199, 116), rough=0.22, dirt=0.05)
    joint = Material("metal", color=(70, 68, 92), rough=0.35, polish=0.5, dirt=0.3)
    dark = Material("metal", color=(36, 34, 52), rough=0.4, polish=0.4, dirt=0.3)
    plume = Material("paint", color=(91, 92, 121), under=(140, 140, 170), wear=0.1, scratches=0.2, rough=0.35, dirt=0.2, skin=False, decals=[
        {"type": "rect", "center": (2.0, 0.0), "size": (6.0, 0.25), "color": (245, 199, 116), "wear": 0.2},
    ])
    skeleton(a, stone, joint, dark, trim=gold)
    head(a, stone, dark)
    core_gear(a, mat=gold)
    a.add("Body", sh.lathe([(0.0, 27.5), (2.0, 27.5), (1.2, 29.5), (0.0, 30.0)], 8, gold, smooth_angle=40))
    for side, role in ((-1, "ArmL"), (1, "ArmR")):
        hand = sh.rounded_box((4.0, 3.4, 4.6), 0.7, 1, gold)
        arm(a, role, side, stone, joint, hand)
        wing = "WingL" if side < 0 else "WingR"
        a.add(wing, sh.rounded_box((3.0, 4.0, 3.0), 0.6, 1, gold).transformed(T(side * 11.0, 23.0, 3.0)))
        for j in range(1, 5):
            length = 15.0 - j * 2.0
            mat = gold if j % 2 == 0 else plume
            f = feather(length, 3.6, mat)
            a.add(wing, f.transformed(compose(T(side * (9.0 + j * 4.6), 21.0 - j * 1.2, 3.0), R(0, 0, 90 - side * (16 + j * 9)), R(0, 0, 0))))
    for j in range(12):
        ang = j / 12 * 360.0
        rad = np.radians(ang)
        a.add("Halo", sh.box((3.0, 0.6, 1.0), None).transformed(compose(T(np.cos(rad) * 9.0, 32.0, np.sin(rad) * 9.0), R(0, -ang, 0))))
    a.add("Body", sh.torus(9.0, 0.25, gold, segments=24, sides=4).transformed(T(0, 31.4, 0)))
    return a
