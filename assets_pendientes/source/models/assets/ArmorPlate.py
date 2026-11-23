from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _island_boss_lib import part_asset


def build():
    a = part_asset("ArmorPlate", 900, (255, 140, 40), ((9.0, 9.0, 3.0), (0.0, 0.0, 0.0)), radius=7.0)
    steel = Material("metal", color=(78, 72, 66), rough=0.5, polish=0.3, dirt=0.65, scratches=0.6, hammered=0.5)
    dark = Material("metal", color=(36, 34, 34), rough=0.6, polish=0.2, dirt=0.6)
    hazard = Material("hazard", color=(255, 160, 30), color2=(26, 26, 30), width=0.25, angle=45)
    a.add("Body", sh.rounded_box((9.0, 9.0, 1.6), 0.5, 1, dark).transformed(T(0, 0, 0.4)))
    a.add("Body", sh.rounded_box((7.6, 7.6, 1.4), 0.6, 2, steel).transformed(T(0, 0, -0.6)))
    for y in (-3.9, 3.9):
        a.add("Body", sh.box((8.6, 0.8, 1.9), hazard).transformed(T(0, y, 0.0)))
    for x in (-3.0, 3.0):
        for y in (-3.0, 3.0):
            a.add("Body", sh.cylinder(0.45, 0.6, dark, segments=6).transformed(compose(T(x, y, -1.35), R(90, 0, 0))))
    a.add("Glow", sh.box((5.6, 0.35, 0.3), None).transformed(T(0, 0.0, -1.35)))
    a.add("Glow", sh.box((0.35, 5.6, 0.3), None).transformed(T(0, 0.0, -1.35)))
    return a
