import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _launch_lib import pistol_grip, trigger_group, along_z


def tool_asset(name, primary, accent, glow, budget=4000):
    a = Asset(name, budget=budget, ao_radius=0.35)
    a.role("Primary", "surface", color=primary, skin="Primary")
    a.role("AccentTrim", "surface", color=accent, skin="Accent")
    a.role("AccentGlow", "neon", color=glow, skin="Accent")
    a.role("Base", "surface")
    return a


def materials(primary, accent):
    return {
        "paint": Material("paint", color=primary, wear=0.45, scratches=0.4, dirt=0.35, rough=0.42),
        "trim": Material("paint", color=accent, wear=0.5, scratches=0.4, dirt=0.35, rough=0.4),
        "dark": Material("metal", color=(54, 56, 64), rough=0.42, polish=0.6, dirt=0.35, skin=False),
        "steel": Material("metal", color=(150, 154, 164), rough=0.32, polish=0.8, dirt=0.3, skin=False),
        "rubber": Material("rubber", color=(26, 26, 30), pattern="ribs", freq=7.0, depth=0.014),
        "leather": Material("rubber", color=(40, 30, 26), pattern="ribs", freq=11.0, depth=0.01),
        "chrome": Material("chrome", color=(226, 230, 238), rough=0.1),
    }


def hammer_handle(a, m, length=3.4, top=1.6):
    bottom = top - length
    a.add("Base", sh.lathe([(0, bottom), (0.2, bottom), (0.2, top), (0, top)], 12, m["dark"]))
    ribs = [(0.19, bottom + 0.1)] + [(0.262 if k % 2 == 0 else 0.248, y) for k, y in enumerate(np.linspace(bottom + 0.14, bottom + 1.3, 13))] + [(0.19, bottom + 1.34)]
    a.add("Base", sh.lathe(ribs, 16, m["rubber"], smooth_angle=60))
    a.add("AccentTrim", sh.lathe([(0, bottom - 0.3), (0.26, bottom - 0.3), (0.35, bottom - 0.22), (0.35, bottom), (0.25, bottom + 0.08), (0, bottom + 0.08)], 16, m["trim"]))
    a.add("Base", sh.lathe([(0.19, top - 0.5), (0.33, top - 0.48), (0.34, top - 0.32), (0.3, top - 0.24), (0.36, top - 0.18), (0.36, top - 0.02), (0.19, top + 0.02)], 16, m["steel"], smooth_angle=30))


def gun_frame(a, m, axis_y):
    for mesh in pistol_grip(m["dark"], m["leather"], m["dark"], m["steel"], width=0.4):
        a.add("Base", mesh)
    for mesh in trigger_group(m["dark"], m["steel"]):
        a.add("Base", mesh)
    a.add("Base", sh.rounded_box((0.5, 0.36, 1.2), 0.08, 1, m["dark"]).transformed(T(0, 0.82, 0.1)))


def blade(width, height, thickness, mat):
    poly = np.array([(0.0, -height * 0.5), (width * 0.75, -height * 0.62), (width, -height * 0.2), (width * 0.95, height * 0.35),
                     (width * 0.7, height * 0.6), (0.0, height * 0.45)])
    return sh.extrude(poly, thickness, mat, bevel=0.03, corner_radius=0.05)
