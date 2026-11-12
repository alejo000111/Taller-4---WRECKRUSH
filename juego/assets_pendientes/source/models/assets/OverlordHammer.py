from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _bosstools_lib import tool_asset, materials, hammer_handle
import _chaos_lib

TOP = 1.8
HEAD_Y = 2.6


def build():
    a = tool_asset("OverlordHammer", (30, 24, 34), (255, 150, 40), (255, 59, 160), budget=4000)
    m = materials((30, 24, 34), (255, 150, 40))
    gold = Material("metal", color=(170, 128, 60), rough=0.3, polish=0.7, dirt=0.3)
    crystal = Material("glossy", color=(150, 60, 220), metal=0.1, rough=0.08)
    basalt = Material("chaos_basalt")
    hammer_handle(a, m, 4.0, TOP)
    a.add("Primary", sh.rounded_box((1.5, 1.5, 2.6), 0.2, 2, basalt).transformed(T(0, HEAD_Y, 0.0)))
    for z in (-1.0, 1.0):
        a.add("AccentTrim", sh.rounded_box((1.62, 1.62, 0.22), 0.05, 1, gold).transformed(T(0, HEAD_Y, z)))
    a.add("Base", sh.gem(0.7, 1.6, 6, crystal, crown=0.3).transformed(compose(T(0, HEAD_Y, -1.9), R(-90, 0, 0))))
    a.add("Base", sh.gem(0.5, 1.4, 6, crystal, crown=0.3).transformed(compose(T(0, HEAD_Y, 1.8), R(90, 0, 0))))
    for side in (-1, 1):
        a.add("Base", sh.gem(0.25, 1.1, 5, crystal, crown=0.2).transformed(compose(T(side * 0.5, HEAD_Y + 0.9, 0.3), R(0, 0, side * -25))))
    a.add("AccentGlow", sh.box((1.56, 0.12, 2.0), None).transformed(T(0, HEAD_Y + 0.2, 0.0)))
    a.point("muzzle", (0, HEAD_Y, -2.6))
    a.point("grip", (0, -1.0, 0))
    return a
