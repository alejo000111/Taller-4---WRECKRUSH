import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _boss_lib import boss_asset, skeleton, head, core_gear, arm
from _destructible import animate
from _expedition_lib import leaves, terrain
import ScrapWall


def build():
    a = boss_asset("VerdantWarden", 6000, (239, 183, 95), (109, 206, 145))
    a.role("Leaves", "surface")
    animate(a, "Leaves", "Leaf")
    rust = Material("scrapwall_sheet", color=(96, 104, 86))
    moss = terrain("verdant", cap_amount=0.85)
    joint = Material("metal", color=(60, 66, 58), rough=0.45, polish=0.3, dirt=0.5, scratches=0.4)
    dark = Material("metal", color=(40, 46, 42), rough=0.5, polish=0.2, dirt=0.5)
    wood = Material("wood", color=(115, 133, 91), dirt=0.4)
    skeleton(a, rust, joint, dark, trim=joint)
    a.add("Body", sh.rounded_box((17.0, 3.0, 11.6), 1.0, 1, moss).transformed(T(0, 21.4, 0.6)))
    head(a, rust, dark)
    core_gear(a, mat=joint)
    for side, role in ((-1, "ArmL"), (1, "ArmR")):
        hand = sh.rounded_box((5.0, 3.0, 5.6), 0.8, 1, rust)
        arm(a, role, side, rust, joint, hand)
        for k, ang in enumerate((-35, 0, 35)):
            finger = sh.lathe([(0.0, 0.0), (0.7, 0.0), (0.5, 2.6), (0.0, 3.4)], 6, joint, smooth_angle=40)
            a.add(role, finger.transformed(compose(T(side * 16.4, 7.4, 0), R(0, ang, 0), T(0, 0, -1.6), R(160, 0, 0))))
        for j in range(1, 4):
            base = (side * (4.5 + j * 0.8), 26.6, 1.0 + (j - 2) * 1.6)
            tip = (side * (9.5 + j * 2.4), 30 + j * 3, 1.0 + (j - 2) * 2.4)
            a.add("Body", sh.sweep([base, (base[0] + side * 1.2, (base[1] + tip[1]) / 2 + 1.4, (base[2] + tip[2]) / 2), tip], 0.75, 6, wood, samples=6, taper=lambda t: 1.0 - 0.55 * t))
            ball = sh.sphere(1.0, leaves((109, 206, 145), scale=2.0, tips=0.5), 8, 5)
            rng = np.random.default_rng(j * 7 + (side > 0))
            ball.pos *= 1 + rng.normal(0, 0.1, (len(ball.pos), 1))
            ball.pos *= np.array([3.0, 2.0, 2.6])
            a.add("Leaves", sh.recompute_normals(ball).transformed(T(*tip)))
    a.add("Leaves", sh.box((0.01, 0.01, 0.01), leaves()).transformed(T(0, 32.0, 1.2)))
    return a
