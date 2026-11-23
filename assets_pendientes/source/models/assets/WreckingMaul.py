from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _bosstools_lib import tool_asset, materials, hammer_handle

TOP = 1.7
HEAD_Y = 2.35


def build():
    a = tool_asset("WreckingMaul", (236, 176, 34), (34, 34, 38), (255, 200, 40), budget=3500)
    m = materials((236, 176, 34), (34, 34, 38))
    hazard = Material("hazard", color=(255, 200, 30), color2=(24, 24, 28), width=0.25, angle=45)
    hammer_handle(a, m, 3.8, TOP)
    a.add("Primary", sh.cylinder(0.85, 2.6, m["paint"], bevel=0.12, segments=16).transformed(compose(T(0, HEAD_Y, -0.1), R(90, 0, 0))))
    for z in (-1.2, 1.0):
        a.add("Base", sh.cylinder(0.95, 0.35, m["steel"], bevel=0.06, segments=16).transformed(compose(T(0, HEAD_Y, z), R(90, 0, 0))))
    a.add("AccentTrim", sh.cylinder(0.9, 0.5, hazard, bevel=0.05, segments=16).transformed(compose(T(0, HEAD_Y, -0.1), R(90, 0, 0))))
    for side in (-1, 1):
        a.add("Base", sh.cylinder(0.12, 1.8, m["chrome"], segments=8).transformed(compose(T(side * 0.62, HEAD_Y + 0.62, -0.1), R(90, 0, 0))))
    a.add("AccentGlow", sh.cylinder(0.55, 0.06, None, segments=16).transformed(compose(T(0, HEAD_Y, -1.42), R(90, 0, 0))))
    a.point("muzzle", (0, HEAD_Y, -1.45))
    a.point("grip", (0, -0.9, 0))
    return a
