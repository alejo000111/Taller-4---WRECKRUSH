import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _island_boss_lib import island_boss, socket, spikes, scale_asset
import _chaos_lib


def build():
    a = island_boss("ChaosOverlord", 8000, (255, 150, 30), (255, 59, 160), ((24.0, 36.0, 16.0), (0.0, 18.0, 0.0)),
                    roles=("ArmL", "ArmR", "Crystals"), motions={"ArmL": "Arm", "ArmR": "Arm", "Core": "Core"}, radius=30.0)
    basalt = Material("chaos_basalt")
    obsidian = Material("chaos_obsidian")
    gold = Material("metal", color=(150, 110, 60), rough=0.35, polish=0.55, dirt=0.4, scratches=0.4)
    dark = Material("metal", color=(30, 24, 34), rough=0.5, polish=0.3, dirt=0.5)
    crystal = Material("glossy", color=(150, 60, 220), metal=0.1, rough=0.08)
    ember = Material("glossy", color=(255, 120, 40), metal=0.0, rough=0.2)

    for side in (-1, 1):
        x = side * 7.0
        a.add("Body", sh.rounded_box((9.0, 3.0, 13.0), 0.8, 1, dark).transformed(T(x, 1.5, -1.2)))
        a.add("Body", sh.rounded_box((7.0, 8.0, 7.4), 1.2, 1, basalt).transformed(compose(T(x, 7.0, 0.4), R(-6, 0, 0))))
        a.add("Body", sh.sphere(2.8, gold, 10, 6).transformed(T(x, 11.8, -0.8)))
        a.add("Crystals", sh.gem(1.3, 6.0, 6, crystal, crown=0.2).transformed(compose(T(x, 13.0, -3.0), R(-50, 0, side * -20))))
        a.add("Body", sh.rounded_box((7.4, 8.0, 8.0), 1.2, 1, obsidian).transformed(T(x, 16.4, 0.0)))

    a.add("Body", sh.rounded_box((18.0, 5.0, 11.0), 1.2, 1, dark).transformed(T(0, 21.4, 0.0)))
    a.add("Body", sh.rounded_box((26.0, 14.0, 15.0), 2.4, 2, basalt).transformed(T(0, 30.0, 0.0)))
    a.add("Body", sh.rounded_box((20.0, 10.0, 1.2), 1.0, 1, obsidian).transformed(compose(T(0, 30.0, -7.6), R(-4, 0, 0))))
    a.add("Body", sh.tube(6.6, 4.8, 1.6, gold, segments=20).transformed(compose(T(0, 30.0, -8.2), R(90, 0, 0))))
    a.add("Core", sh.sphere(4.8, None, 16, 10).transformed(compose(T(0, 30.0, -7.0), R(90, 0, 0))))
    for k in range(6):
        angle = k * 60.0 + 30.0
        a.add("Body", sh.gem(0.9, 4.0, 4, ember, crown=0.2).transformed(compose(T(0, 30.0, -8.4), R(0, 0, angle), T(0, 7.6, 0))))

    a.add("Body", sh.rounded_box((10.0, 6.0, 9.0), 1.4, 1, obsidian).transformed(T(0, 40.0, -0.8)))
    a.add("Body", sh.rounded_box((8.0, 1.4, 0.5), 0.3, 1, dark).transformed(T(0, 40.4, -5.3)))
    for side in (-1, 1):
        a.add("Eyes", sh.gem(0.8, 2.6, 4, None, crown=0.2).transformed(compose(T(side * 2.4, 40.4, -5.5), R(0, 0, side * 70))))
        horn = [(side * 4.4, 42.0, -0.4), (side * 7.6, 45.4, 0.6), (side * 9.0, 49.6, -0.6), (side * 8.2, 53.0, -2.8)]
        a.add("Body", sh.sweep(horn, 1.3, 7, gold, samples=10, taper=lambda t: 1.0 - 0.75 * t))

    for k, x in enumerate((-8.0, 0.0, 8.0)):
        spikes(a, "Crystals", (x, 34.0, 6.4), 3, 16.0 - abs(x) * 0.4, 2.4, crystal, spread=25.0, tilt=-28.0, seed=7 + k)
        spikes(a, "Crystals", (x * 0.8, 27.0, 7.2), 2, 10.0, 1.7, crystal, spread=20.0, tilt=-50.0, seed=17 + k)

    for side, role in ((-1, "ArmL"), (1, "ArmR")):
        x = side * 15.6
        a.add(role, sh.rounded_box((8.0, 7.0, 9.0), 1.6, 1, obsidian).transformed(T(x, 35.0, 0.0)))
        a.add(role, sh.gem(1.6, 8.0, 6, crystal, crown=0.2).transformed(compose(T(x + side * 2.0, 40.0, 1.0), R(0, 0, side * -25))))
        a.add(role, sh.rounded_box((6.0, 10.0, 6.0), 1.0, 1, basalt).transformed(compose(T(side * 17.0, 27.4, 0.0), R(0, 0, side * 8))))
        a.add(role, sh.sphere(2.4, gold, 8, 5).transformed(T(side * 17.8, 21.8, 0.0)))
        a.add(role, sh.rounded_box((5.4, 9.0, 5.8), 1.0, 1, dark).transformed(compose(T(side * 18.2, 16.6, -1.0), R(10, 0, 0))))
        fist = sh.gem(4.2, 8.0, 6, crystal, crown=0.35)
        a.add(role, fist.transformed(compose(T(side * 18.4, 10.6, -2.0), R(10, 30, 0))))
        a.add(role, sh.tube(3.6, 2.8, 1.2, gold, segments=12).transformed(T(side * 18.3, 12.6, -1.6)))

    socket(a, "PlateSocket1", (-7.0, 15.0, -4.8), 0.0)
    socket(a, "PlateSocket2", (7.0, 15.0, -4.8), 0.0)
    socket(a, "PlateSocket3", (-11.4, 18.0, 0.0), 90.0)
    socket(a, "PlateSocket4", (11.4, 18.0, 0.0), -90.0)
    return scale_asset(a, 1.15)
