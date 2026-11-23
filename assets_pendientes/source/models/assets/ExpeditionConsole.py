from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import ALL, GATE, expedition_asset
from _bossisland_lib import PATHS as ISLAND_PATHS
from _building_lib import trim_paint
from _landmark_lib import patch


def build():
    a = expedition_asset("ExpeditionConsole", 700, 6.0, atlas=512)
    a.role("Trim", "surface", skin="Trim", color=(239, 183, 95))
    a.role("Glow", "neon", color=(120, 230, 255))
    body = Material("metal", color=(46, 52, 62), rough=0.35, polish=0.5, dirt=0.3, scratches=0.3)
    screen = Material("screen", color=(14, 26, 34))
    trim = trim_paint()
    a.add("Body", sh.rounded_box((8.0, 0.6, 6.0), 0.1, 1, body).transformed(T(0, 0.3, 0)))
    a.add("Body", sh.rounded_box((6.6, 3.4, 4.4), 0.2, 1, body).transformed(T(0, 2.3, 0.4)))
    desk = sh.extrude([(-3.4, 0.0), (3.4, 0.0), (3.4, 0.5), (-3.4, 1.6)], 5.0, body, bevel=0.05, corner_radius=0.0)
    a.add("Body", desk.transformed(compose(T(0, 4.0, 0), R(0, 90, 0))))
    a.add("Body", sh.box((4.2, 0.06, 4.6), screen).transformed(compose(T(0, 5.12, 0), R(-9.2, 0, 0))))
    a.add("Glow", sh.box((4.4, 0.08, 0.12), None).transformed(compose(T(0, 4.82, -2.6), R(-9.2, 0, 0))))
    for x in (-3.0, 3.0):
        a.add("Trim", sh.box((0.6, 3.4, 4.5), trim).transformed(T(x, 2.3, 0.4)))
    a.add("Glow", sh.box((6.0, 0.15, 0.1), None).transformed(T(0, 0.65, -1.85)))
    patch(a, ALL + [GATE] + ISLAND_PATHS, ["ReturnConsole", "Console"], functional=True, tint=["Trim"])
    return a
