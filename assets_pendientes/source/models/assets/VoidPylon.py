from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _island_boss_lib import part_asset
import _chaos_lib


def build():
    a = part_asset("VoidPylon", 1200, (190, 100, 255), ((7.0, 16.0, 7.0), (0.0, 8.0, 0.0)), radius=10.0, motion="Orb")
    obsidian = Material("chaos_obsidian")
    metal = Material("metal", color=(54, 50, 66), rough=0.35, polish=0.5, dirt=0.4)
    trim = Material("metal", color=(150, 140, 190), rough=0.3, polish=0.6, dirt=0.3)
    a.add("Body", sh.lathe([(0.0, 0.0), (3.6, 0.0), (3.8, 0.6), (3.0, 2.2), (0.0, 2.2)], 8, metal, smooth_angle=35))
    a.add("Body", sh.tube(3.2, 2.6, 0.6, trim, segments=8).transformed(T(0, 2.4, 0)))
    for k in range(4):
        shard = sh.gem(1.1, 9.0, 5, obsidian, crown=0.25)
        a.add("Body", shard.transformed(compose(R(0, k * 90 + 45, 0), T(0, 7.0, -1.9), R(-10, 0, 0))))
    a.add("Body", sh.gem(1.6, 13.0, 6, obsidian, crown=0.3).transformed(T(0, 8.8, 0)))
    a.add("Glow", sh.sphere(1.4, None, 10, 6).transformed(T(0, 9.0, 0)))
    a.add("Glow", sh.torus(2.8, 0.25, None, 16, 4).transformed(T(0, 12.4, 0)))
    return a
