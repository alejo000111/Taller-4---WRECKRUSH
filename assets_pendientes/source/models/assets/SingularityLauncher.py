from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _bosstools_lib import tool_asset, materials, gun_frame
import _chaos_lib

AXIS_Y = 1.3


def build():
    a = tool_asset("SingularityLauncher", (48, 44, 62), (166, 77, 255), (190, 110, 255), budget=3500)
    m = materials((48, 44, 62), (166, 77, 255))
    obsidian = Material("chaos_obsidian")
    gun_frame(a, m, AXIS_Y)
    a.add("Primary", sh.cylinder(0.55, 2.4, m["paint"], bevel=0.1, segments=14).transformed(compose(T(0, AXIS_Y, -0.6), R(90, 0, 0))))
    a.add("Base", sh.tube(0.75, 0.5, 0.5, obsidian, segments=14).transformed(compose(T(0, AXIS_Y, -2.0), R(90, 0, 0))))
    a.add("AccentGlow", sh.sphere(0.42, None, 12, 8).transformed(T(0, AXIS_Y + 0.15, 0.55)))
    a.add("Base", sh.tube(0.6, 0.48, 0.16, m["chrome"], segments=14).transformed(T(0, AXIS_Y + 0.15, 0.55)))
    for k in range(3):
        a.add("AccentTrim", sh.torus(0.62, 0.07, m["trim"], 14, 5).transformed(compose(T(0, AXIS_Y, -0.2 - k * 0.5), R(90, 0, 0))))
    for side in (-1, 1):
        a.add("Base", sh.gem(0.14, 0.9, 5, obsidian, crown=0.2).transformed(compose(T(side * 0.62, AXIS_Y + 0.35, -1.8), R(-70, 0, side * 20))))
    a.point("muzzle", (0, AXIS_Y, -2.3))
    a.point("grip", (0, -0.1, 0))
    return a
