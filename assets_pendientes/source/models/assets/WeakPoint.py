from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _island_boss_lib import part_asset


def build():
    a = part_asset("WeakPoint", 900, (255, 230, 60), ((6.0, 6.0, 6.0), (0.0, 0.0, 0.0)), radius=5.0, motion="Core")
    frame = Material("metal", color=(44, 48, 42), rough=0.45, polish=0.35, dirt=0.5)
    hazard = Material("hazard", color=(255, 210, 31), color2=(26, 28, 24), width=0.28, angle=45)
    a.add("Body", sh.prism(6, 3.0, 1.6, frame, bevel=0.15).transformed(compose(T(0, 0, 0.2), R(90, 0, 0))))
    a.add("Body", sh.tube(2.7, 2.0, 0.8, hazard, segments=12).transformed(compose(T(0, 0, -0.8), R(90, 0, 0))))
    a.add("Body", sh.cylinder(2.2, 2.4, frame, segments=10).transformed(compose(T(0, 0, 1.6), R(90, 0, 0))))
    a.add("Glow", sh.dome(1.9, 1.3, None, 14, 5).transformed(compose(T(0, 0, -1.0), R(-90, 0, 0))))
    return a
