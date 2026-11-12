from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _bosstools_lib import tool_asset, materials, hammer_handle, blade

TOP = 1.6


def build():
    a = tool_asset("ScrapCleaver", (196, 112, 60), (64, 112, 118), (255, 150, 40), budget=3000)
    m = materials((196, 112, 60), (64, 112, 118))
    rust = Material("paint", color=(150, 88, 52), under=(84, 64, 54), wear=0.7, scratches=0.6, rough=0.6, metal=0.3, dirt=0.6)
    hammer_handle(a, m, 3.6, TOP)
    a.add("Primary", blade(2.2, 2.0, 0.18, rust).transformed(compose(T(0, TOP + 0.4, -0.15), R(0, 90, 0))))
    a.add("AccentTrim", blade(2.0, 0.5, 0.24, m["trim"]).transformed(compose(T(0, TOP + 1.05, -0.2), R(0, 90, 0))))
    a.add("Base", sh.rounded_box((0.5, 0.9, 0.7), 0.08, 1, m["dark"]).transformed(T(0, TOP + 0.35, 0.1)))
    for k in range(3):
        a.add("Base", sh.cylinder(0.08, 0.32, m["steel"], segments=6).transformed(compose(T(0, TOP + 0.05 + k * 0.42, -0.55), R(0, 0, 90))))
    a.add("AccentGlow", sh.box((0.26, 0.08, 1.7), None).transformed(T(0, TOP - 0.38, -1.15)))
    a.point("muzzle", (0, TOP + 0.3, -2.1))
    a.point("grip", (0, -0.8, 0))
    return a
