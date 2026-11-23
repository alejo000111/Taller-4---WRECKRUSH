import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _boss_lib import boss_asset, skeleton, head, core_gear, arm
from _destructible import animate
from _chaos_lib import crystal_cluster
import _expedition_lib


def build():
    a = boss_asset("Tidebreaker", 6000, (239, 153, 94), (129, 207, 230))
    a.role("LegsL", "surface")
    a.role("LegsR", "surface")
    a.role("Shell", "glass", color=(150, 215, 240), transparency=0.2)
    animate(a, "LegsL", "Arm")
    animate(a, "LegsR", "Arm")
    hull = Material("paint", color=(125, 155, 172), under=(110, 110, 116), wear=0.45, scratches=0.4, rough=0.4, dirt=0.4, skin=False)
    accent = Material("paint", color=(239, 153, 94), under=(110, 100, 90), wear=0.45, scratches=0.4, rough=0.4, dirt=0.4, skin=False)
    joint = Material("metal", color=(70, 82, 92), rough=0.38, polish=0.5, dirt=0.4, scratches=0.4)
    dark = Material("metal", color=(41, 49, 57), rough=0.45, polish=0.3, dirt=0.45)
    frost = Material("terrain_rock", color=(170, 196, 214), cap=(240, 246, 250), cap_amount=0.9, dirt=0.0)
    skeleton(a, hull, joint, dark, trim=accent)
    head(a, hull, dark)
    core_gear(a, mat=joint)
    a.add("Body", sh.rounded_box((18.0, 2.0, 12.0), 0.8, 1, frost).transformed(T(0, 22.8, 1.6)))
    shell = sh.sphere(1.0, None, 12, 6)
    shell.pos[:, 1] = np.maximum(shell.pos[:, 1], 0.0)
    shell.pos *= np.array([12.0, 6.0, 9.0])
    a.add("Shell", sh.recompute_normals(shell).transformed(T(0, 19.0, 6.0)))
    a.add("Shell", [p.transformed(T(0, 22.0, 9.0)) for p in crystal_cluster(None, 9, 5, 1.6, 9.0, 5.0, tilt=30)])
    for side, role, legs in ((-1, "ArmL", "LegsL"), (1, "ArmR", "LegsR")):
        hand = sh.rounded_box((4.0, 3.0, 4.6), 0.6, 1, hull)
        arm(a, role, side, hull, joint, hand)
        palm = sh.sphere(1.0, accent, 12, 7)
        palm.pos *= np.array([5.0, 4.0, 5.0])
        a.add(role, sh.recompute_normals(palm).transformed(T(side * 23.0, 13.0, -8.0)))
        for dy, tilt, length in ((1.6, -12, 7.0), (-1.8, 14, 6.0)):
            jaw = sh.lathe([(0.0, 0.0), (2.0, 0.0), (1.7, length * 0.5), (0.9, length * 0.85), (0.0, length)], 8, joint, smooth_angle=40)
            jaw.pos[:, 0] *= 0.7
            a.add(role, jaw.transformed(compose(T(side * 23.0, 13.0 + dy, -11.0), R(-90 + tilt, 0, 0))))
        for j in range(3):
            z = j * 6.0 - 6.0
            seg = sh.rounded_box((8.0, 2.4, 3.0), 0.6, 1, accent)
            a.add(legs, seg.transformed(compose(T(side * 15.0, 7.0, z), R(0, side * 17, side * -18))))
            tip = sh.lathe([(0.0, 0.0), (1.2, 0.0), (0.8, 5.0), (0.0, 6.0)], 6, joint, smooth_angle=40)
            a.add(legs, tip.transformed(compose(T(side * 21.0, 0.0, z), R(0, 0, side * 22))))
    return a
