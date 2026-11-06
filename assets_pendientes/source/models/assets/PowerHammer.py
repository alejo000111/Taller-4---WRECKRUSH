import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
import _hammers_lib
import _egg_common
from _hammers_lib import place

HEAD_Y = 2.15
ORANGE = (255, 122, 26)
YELLOW = (255, 210, 31)


def along_z(mesh, x=0.0, y=HEAD_Y, z=0.0, back=False):
    return mesh.transformed(compose(T(x, y, z), R(90 if back else -90, 0, 0)))


def build():
    a = Asset("PowerHammer", budget=5000, ao_radius=0.35)
    a.role("Primary", "surface", color=ORANGE, skin="Primary")
    a.role("AccentTrim", "surface", color=ORANGE, skin="Accent")
    a.role("AccentGlow", "neon", color=YELLOW, skin="Accent")
    a.role("Base", "surface")

    side_decals = [
        {"type": "stripes", "center": (0.08, 0.22), "size": (0.86, 0.5), "width": 0.11, "color": (24, 24, 28), "wear": 0.35},
        {"type": "rect", "center": (0.08, 0.22), "size": (0.58, 0.24), "radius": 0.03, "color": (24, 24, 28), "wear": 0.3},
        {"type": "text", "text": "PWR-5", "center": (0.08, 0.22), "height": 0.15, "color": YELLOW, "font": "impact", "wear": 0.3},
        {"type": "rivets", "points": [(-0.42, 0.0), (0.58, 0.0), (-0.42, 0.44), (0.58, 0.44)], "radius": 0.045, "color": (150, 152, 160), "height": 0.012},
    ]
    paint = Material("paint", color=ORANGE, wear=0.42, scratches=0.35, dirt=0.3, rough=0.4)
    side_paint = Material("paint", color=ORANGE, wear=0.42, scratches=0.35, dirt=0.3, rough=0.4, decals=side_decals)
    top_paint = Material("paint", color=ORANGE, wear=0.42, scratches=0.35, dirt=0.3, rough=0.4, decals=[
        {"type": "rect", "center": (0.0, 0.05), "size": (0.86, 1.0), "radius": 0.06, "color": (52, 54, 62), "wear": 0.2},
    ] + [{"type": "rect", "center": (0.0, -0.33 + k * 0.19), "size": (0.7, 0.06), "radius": 0.02, "color": (18, 18, 22), "wear": 0.0, "raise": -0.008} for k in range(5)])
    trim = Material("paint", color=ORANGE, wear=0.5, scratches=0.4, dirt=0.35, rough=0.38)
    dark = Material("metal", color=(66, 70, 80), rough=0.42, polish=0.6, dirt=0.35, skin=False)
    steel = Material("metal", color=(150, 154, 164), rough=0.32, polish=0.8, dirt=0.3, skin=False, decals=[
        {"type": "rivets", "points": [(0.0, 0.0)], "radius": 0.05, "height": 0.01},
    ])
    chrome = Material("chrome", color=(226, 230, 238), rough=0.1)
    face = Material("hammers_machined", color=(178, 180, 190), center=(0, HEAD_Y, -1.47), axis=(0, 0, -1), rings=[(0.32, 0.035), (0.52, 0.03)], zone=0.44, dents=0.5)
    nozzle = Material("hammers_heat", color=(92, 94, 102), center=(0, HEAD_Y, 0.82), axis=(0, 0, 1), length=0.62, amount=0.85)
    rubber = Material("rubber", color=(26, 26, 30), pattern="ribs", freq=7.0, depth=0.014)
    hose = Material("rubber", color=(30, 30, 34), pattern="ribs", freq=26.0, depth=0.006)

    a.add("Base", sh.lathe([(0, -1.52), (0.2, -1.52), (0.2, 1.62), (0, 1.62)], 12, dark))
    ribs = [(0.19, -1.44)] + [(0.262 if k % 2 == 0 else 0.248, y) for k, y in enumerate(np.linspace(-1.4, -0.3, 13))] + [(0.19, -0.27)]
    a.add("Base", sh.lathe(ribs, 16, rubber, smooth_angle=60))
    a.add("AccentTrim", sh.lathe([(0, -1.8), (0.26, -1.8), (0.35, -1.72), (0.35, -1.52), (0.25, -1.44), (0, -1.44)], 16, trim))
    a.add("Base", sh.lathe([(0.19, 1.12), (0.33, 1.14), (0.34, 1.3), (0.3, 1.38), (0.36, 1.44), (0.36, 1.6), (0.19, 1.64)], 16, steel, smooth_angle=30))

    head = sh.rounded_box((1.32, 1.32, 1.62), 0.13, 2, paint, face_mats={"+x": side_paint, "-x": side_paint, "+y": top_paint})
    a.add("Primary", head.transformed(T(0, HEAD_Y, -0.04)))
    a.add("Primary", sh.rounded_box((1.42, 1.0, 0.5), 0.09, 2, paint).transformed(T(0, HEAD_Y, -0.62)))
    for side in (-1, 1):
        a.add("AccentGlow", sh.box((0.05, 0.2, 1.3), None).transformed(T(side * 0.675, HEAD_Y + 0.36, -0.04)))

    neck = sh.lathe([(0, 0), (0.55, 0), (0.6, 0.12), (0.72, 0.2), (0.72, 0.58), (0.66, 0.64), (0, 0.64)], 24, face, smooth_angle=35)
    a.add("Base", along_z(neck, z=-0.83))
    nozzle_prof = [(0, 0), (0.5, 0), (0.5, 0.12), (0.42, 0.2), (0.42, 0.4), (0.52, 0.48), (0.58, 0.64), (0.48, 0.66), (0.38, 0.5), (0.0, 0.5)]
    a.add("Base", along_z(sh.lathe(nozzle_prof, 20, nozzle, smooth_angle=35), z=0.78, back=True))
    a.add("AccentGlow", sh.torus(0.53, 0.035, None, segments=20, sides=4).transformed(compose(T(0, HEAD_Y, 1.4), R(90, 0, 0))))

    for side in (-1, 1):
        x = side * 0.84
        a.add("Base", along_z(sh.lathe([(0, 0), (0.17, 0), (0.17, 1.0), (0.13, 1.04), (0, 1.04)], 12, dark), x=x, y=HEAD_Y - 0.2, z=0.62))
        a.add("Base", along_z(sh.cylinder(0.085, 0.72, chrome, bevel=0.0, segments=10), x=x, y=HEAD_Y - 0.2, z=-0.75))
        for z in (-1.04, 0.72):
            a.add("Base", sh.rounded_box((0.34, 0.36, 0.16), 0.03, 1, steel).transformed(T(side * 0.76, HEAD_Y - 0.2, z)))
            a.add("Base", sh.cylinder(0.06, 0.42, steel, bevel=0.01, segments=8).transformed(compose(T(side * 0.8, HEAD_Y - 0.2, z), R(0, 0, 90))))
        path = [(side * 0.27, 1.45, 0.12), (side * 0.5, 1.56, 0.36), (side * 0.72, 1.74, 0.6), (side * 0.84, HEAD_Y - 0.36, 0.78)]
        a.add("Base", sh.sweep(path, 0.065, 8, hose, samples=12))
        for end in (path[0], path[-1]):
            a.add("Base", sh.cylinder(0.09, 0.1, steel, bevel=0.015, segments=10).transformed(T(*end)))

    for k in range(5):
        fin = sh.rounded_box((0.82, 0.16, 0.06), 0.02, 1, steel)
        a.add("Base", fin.transformed(T(0, HEAD_Y + 0.74, -0.38 + k * 0.19)))
    gauge_c = (0.725, HEAD_Y + 0.05, -0.62)
    dial = Material("egg_gauge", center=(gauge_c[0] + 0.09, gauge_c[1], gauge_c[2]), normal=(1, 0, 0), radius=0.17, needle=70.0)
    a.add("Base", place(sh.cylinder(0.19, 0.1, steel, bevel=0.02, segments=16), gauge_c, (1, 0, 0)))
    a.add("Base", place(sh.cylinder(0.16, 0.02, dial, bevel=0.0, segments=16), (gauge_c[0] + 0.07, gauge_c[1], gauge_c[2]), (1, 0, 0)))
    a.point("muzzle", (0, HEAD_Y, -1.5))
    a.point("grip", (0, -0.9, 0))
    return a
