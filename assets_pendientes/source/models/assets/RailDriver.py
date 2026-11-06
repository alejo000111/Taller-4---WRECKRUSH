from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _bosstools_lib import tool_asset, materials, gun_frame
import _military_lib

AXIS_Y = 1.15


def build():
    a = tool_asset("RailDriver", (86, 96, 58), (255, 210, 31), (140, 255, 90), budget=3500)
    m = materials((86, 96, 58), (255, 210, 31))
    camo = Material("military_camo")
    gun_frame(a, m, AXIS_Y)
    a.add("Primary", sh.rounded_box((0.8, 0.7, 2.0), 0.12, 2, camo).transformed(T(0, AXIS_Y, 0.2)))
    for side in (-1, 1):
        a.add("Base", sh.rounded_box((0.16, 0.3, 3.6), 0.04, 1, m["steel"]).transformed(T(side * 0.24, AXIS_Y, -2.4)))
    for k in range(5):
        a.add("AccentTrim", sh.box((0.7, 0.12, 0.12), m["trim"]).transformed(T(0, AXIS_Y + 0.2, -1.2 - k * 0.6)))
    for k in range(3):
        a.add("AccentGlow", sh.cylinder(0.12, 0.5, None, segments=8).transformed(T(0, AXIS_Y + 0.55, 0.6 - k * 0.45)))
    a.add("Base", sh.rounded_box((0.5, 0.5, 1.2), 0.08, 1, m["dark"]).transformed(T(0, AXIS_Y + 0.05, 1.7)))
    a.point("muzzle", (0, AXIS_Y, -4.2))
    a.point("grip", (0, -0.1, 0))
    return a
