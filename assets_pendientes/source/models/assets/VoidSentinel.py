import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _island_boss_lib import island_boss, scale_asset
import _chaos_lib


def build():
    a = island_boss("VoidSentinel", 7000, (34, 225, 255), (166, 77, 255), ((16.0, 30.0, 16.0), (0.0, 19.0, 0.0)),
                    roles=("ArmL", "ArmR", "Halo"), motions={"ArmL": "Wing", "ArmR": "Wing", "Halo": "Rotor", "Core": "Core"}, radius=24.0)
    obsidian = Material("chaos_obsidian")
    panel = Material("metal", color=(48, 44, 62), rough=0.35, polish=0.5, dirt=0.35, scratches=0.3)
    trim = Material("metal", color=(150, 140, 190), rough=0.3, polish=0.6, dirt=0.25)
    crystal = Material("glossy", color=(120, 70, 210), metal=0.1, rough=0.1)

    a.add("Body", sh.gem(7.5, 18.0, 8, obsidian, crown=0.55).transformed(T(0, 20.0, 0)))
    a.add("Body", sh.lathe([(0.0, 0.0), (5.0, 0.0), (6.2, 1.6), (5.4, 3.4), (0.0, 3.4)], 12, panel, smooth_angle=35).transformed(T(0, 9.0, 0)))
    a.add("Body", sh.gem(3.0, 9.0, 6, obsidian, crown=0.3).transformed(compose(T(0, 5.0, 0), R(180, 0, 0))))
    a.add("Body", sh.tube(6.4, 5.4, 1.2, trim, segments=16).transformed(T(0, 21.0, 0)))
    a.add("Core", sh.sphere(3.2, None, 14, 9).transformed(T(0, 21.0, -5.6)))
    a.add("Body", sh.tube(4.2, 3.3, 1.4, trim, segments=16).transformed(compose(T(0, 21.0, -6.2), R(90, 0, 0))))
    for side in (-1, 1):
        a.add("Eyes", sh.box((1.8, 0.5, 0.3), None).transformed(compose(T(side * 1.8, 26.6, -5.2), R(-20, side * -10, 0))))
    a.add("Body", sh.gem(2.6, 7.0, 6, crystal, crown=0.2).transformed(T(0, 31.6, 0)))

    for k in range(10):
        angle = k * 36.0
        shard = sh.gem(0.9, 4.0, 5, crystal, crown=0.2)
        a.add("Halo", shard.transformed(compose(R(0, angle, 0), T(0, 34.0, -8.0), R(70, 0, 0))))
    a.add("Halo", sh.torus(8.0, 0.35, trim, 32, 4).transformed(T(0, 34.0, 0)))

    for side, role in ((-1, "ArmL"), (1, "ArmR")):
        for k, (y, out, size) in enumerate(((26.0, 13.0, 12.0), (17.0, 15.0, 11.0), (9.0, 12.0, 8.0))):
            limb = sh.gem(2.6, size, 6, obsidian, crown=0.25)
            a.add(role, limb.transformed(compose(T(side * out, y, 1.0 - k), R(0, 0, side * (70 - k * 15)))))
            a.add(role, sh.torus(1.6, 0.35, trim, 12, 4).transformed(compose(T(side * (out - 3.4), y + 0.6, 1.0 - k), R(0, 0, 90))))
            tip = sh.gem(1.0, 4.0, 5, crystal, crown=0.2)
            a.add(role, tip.transformed(compose(T(side * (out + size * 0.42), y - size * 0.18, 1.0 - k), R(0, 0, side * (115 - k * 15)))))
    for k in range(4):
        fin = sh.gem(1.4, 12.0, 4, obsidian, crown=0.3).transformed(compose(R(0, 45 + k * 90, 0), T(0, 16.0, -7.4), R(-14, 0, 0)))
        a.add("Body", fin)
    for k in range(6):
        a.add("Body", sh.box((0.5, 10.0, 0.5), trim).transformed(compose(R(0, k * 60, 0), T(0, 19.0, -6.6), R(-12, 0, 0))))
    return scale_asset(a, 1.15)
