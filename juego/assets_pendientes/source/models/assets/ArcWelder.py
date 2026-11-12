from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _bosstools_lib import tool_asset, materials, gun_frame

AXIS_Y = 1.1


def build():
    a = tool_asset("ArcWelder", (160, 44, 38), (255, 140, 40), (255, 160, 60), budget=3500)
    m = materials((160, 44, 38), (255, 140, 40))
    copper = Material("metal", color=(196, 110, 60), rough=0.35, polish=0.6, dirt=0.3)
    gun_frame(a, m, AXIS_Y)
    a.add("Primary", sh.rounded_box((0.7, 0.8, 2.2), 0.12, 2, m["paint"]).transformed(T(0, AXIS_Y, -0.3)))
    a.add("Base", sh.cylinder(0.22, 1.6, m["dark"], segments=10).transformed(compose(T(0, AXIS_Y, -2.1), R(90, 0, 0))))
    for k in range(4):
        a.add("AccentTrim", sh.torus(0.36, 0.08, copper, 12, 5).transformed(compose(T(0, AXIS_Y, -1.5 - k * 0.32), R(90, 0, 0))))
    a.add("Base", sh.gem(0.16, 0.7, 6, m["chrome"], crown=0.2).transformed(compose(T(0, AXIS_Y, -3.05), R(-90, 0, 0))))
    a.add("AccentGlow", sh.sphere(0.2, None, 8, 5).transformed(T(0, AXIS_Y, -3.4)))
    a.add("Base", sh.sweep([(0.0, AXIS_Y - 0.3, 0.7), (0.0, AXIS_Y - 0.9, 1.3), (0.0, AXIS_Y - 1.2, 1.9)], 0.1, 6, m["rubber"], samples=6))
    a.add("AccentGlow", sh.box((0.05, 0.12, 1.6), None).transformed(T(0.36, AXIS_Y + 0.2, -0.3)))
    a.point("muzzle", (0, AXIS_Y, -3.45))
    a.point("grip", (0, -0.1, 0))
    return a
