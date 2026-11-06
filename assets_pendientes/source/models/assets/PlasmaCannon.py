import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
import _hammers_lib
from _launch_lib import pistol_grip, trigger_group, side_profile

AXIS_Y = 1.0
NAVY = (40, 44, 58)
CYAN = (34, 225, 255)


def forward(mesh, x=0.0, y=AXIS_Y, z=0.0):
    return mesh.transformed(compose(T(x, y, z), R(-90, 0, 0)))


def build():
    a = Asset("PlasmaCannon", budget=7000, ao_radius=0.35)
    a.role("Primary", "surface", color=NAVY, skin="Primary")
    a.role("AccentGlow", "neon", color=CYAN, skin="Accent")
    a.role("Glass", "glass", color=(180, 240, 255), transparency=0.45)
    a.role("Base", "surface")

    armor = Material("launch_armor", color=NAVY, under=(150, 160, 178), wear=0.3, scratches=0.3, rough=0.32, dirt=0.25, skin=True,
                     lines_z=(-0.45, 0.35, 1.05), lines_y=(1.12,), line_width=0.013)
    side_armor = Material("launch_armor", color=NAVY, under=(150, 160, 178), wear=0.35, scratches=0.3, rough=0.32, dirt=0.25, skin=True, decals=[
        {"type": "text", "text": "PLASMA", "center": (0.0, 0.0), "height": 0.15, "color": CYAN, "font": "black", "wear": 0.25},
    ])
    gun = Material("metal", color=(70, 74, 88), rough=0.32, polish=0.7, dirt=0.3, skin=False)
    dark = Material("metal", color=(36, 38, 48), rough=0.4, polish=0.5, dirt=0.3, skin=False)
    steel = Material("metal", color=(176, 182, 196), rough=0.24, polish=0.8, brushed=True, dirt=0.2, skin=False)
    rubber = Material("rubber", color=(26, 28, 34), pattern="knurl", freq=12.0)
    heat = Material("hammers_heat", color=(110, 114, 126), center=(0, AXIS_Y, -1.0), axis=(0, 0, -1), length=1.9, amount=0.7, soot=0.15)

    a.add("Base", pistol_grip(dark, rubber, dark, steel, width=0.4))
    a.add("Base", trigger_group(dark, steel))

    body_poly = [(-1.55, 0.62), (-1.55, 1.24), (-1.36, 1.44), (0.3, 1.44), (0.74, 1.3), (0.96, 1.06), (0.96, 0.76), (0.72, 0.56), (-1.3, 0.56)]
    a.add("Primary", side_profile(body_poly, 1.0, armor, bevel=0.06, corner_radius=0.0))
    fairing = [(-1.05, 1.4), (0.15, 1.4), (0.5, 1.52), (-0.15, 1.7), (-0.95, 1.64)]
    a.add("Primary", side_profile(fairing, 0.6, armor, bevel=0.04, corner_radius=0.0))
    for side in (-1, 1):
        plate = sh.rounded_box((0.06, 0.42, 1.2), 0.02, 1, side_armor).transformed(T(side * 0.52, 0.82, 0.25))
        a.add("Primary", plate)
        slot = sh.box((0.05, 0.22, 1.42), dark).transformed(T(side * 0.505, 1.17, 0.48))
        a.add("Base", slot)
        vent = sh.box((0.04, 0.1, 1.3), None).transformed(T(side * 0.53, 1.17, 0.48))
        a.add("AccentGlow", vent)

    barrel = sh.lathe([(0, 0), (0.36, 0), (0.36, 0.08), (0.28, 0.14), (0.28, 1.86), (0.34, 1.9), (0.42, 2.0), (0.42, 2.06), (0.24, 2.06), (0.24, 1.9), (0, 1.9)], 20, heat, smooth_angle=35)
    a.add("Base", forward(barrel, z=-0.92))
    for zc in (-1.3, -1.8, -2.3):
        housing = sh.tube(0.44, 0.27, 0.22, gun, bevel=0.025, segments=20)
        a.add("Base", forward(housing, z=zc))
        coil = sh.torus(0.46, 0.06, None, segments=24, sides=6)
        a.add("AccentGlow", coil.transformed(compose(T(0, AXIS_Y, zc), R(90, 0, 0))))
    for zc in (-1.45, -1.55, -1.65, -1.95, -2.05, -2.15, -2.45, -2.55):
        fin = sh.tube(0.4, 0.27, 0.04, steel, bevel=0.0, segments=16)
        a.add("Base", forward(fin, z=zc))
    emitter = sh.torus(0.33, 0.045, None, segments=14, sides=5)
    a.add("AccentGlow", emitter.transformed(compose(T(0, AXIS_Y, -2.96), R(90, 0, 0))))
    a.add("AccentGlow", forward(sh.cylinder(0.2, 0.03, None, bevel=0.0, segments=10), z=-2.8))

    collar = sh.tube(0.56, 0.4, 0.14, dark, bevel=0.02, segments=12).transformed(T(0, 1.55, 0.9))
    a.add("Base", collar)
    dome = sh.capsule(0.42, 0.84, None, segments=18, rings=5)
    a.add("Glass", dome.transformed(T(0, 1.9, 0.9)))
    a.add("AccentGlow", sh.sphere(0.25, None, 10, 6).transformed(T(0, 1.9, 0.9)))
    for k in range(4):
        rib = sh.box((0.05, 0.75, 0.05), steel).transformed(compose(T(0, 1.92, 0.9), R(0, k * 90 + 45, 0), T(0.43, 0, 0)))
        a.add("Base", rib)
    cap = sh.lathe([(0, 0), (0.3, 0), (0.3, 0.06), (0.18, 0.14), (0, 0.15)], 12, dark)
    a.add("Base", cap.transformed(T(0, 2.3, 0.9)))

    cell = sh.lathe([(0, 0), (0.42, 0), (0.42, 0.34), (0.34, 0.42), (0, 0.42)], 12, gun)
    a.add("Base", cell.transformed(compose(T(0, AXIS_Y, 1.62), R(90, 0, 0))))
    a.add("AccentGlow", sh.cylinder(0.27, 0.03, None, bevel=0.0, segments=10).transformed(compose(T(0, AXIS_Y, 2.05), R(90, 0, 0))))

    for side in (-1, 1):
        for k, y in enumerate((0.78, 1.18)):
            pos = (side * 0.62, y, 0.62)
            a.add("Glass", sh.capsule(0.09, 0.95, None, segments=10, rings=3).transformed(compose(T(*pos), R(90, 0, 0))))
            a.add("AccentGlow", sh.cylinder(0.045, 0.82, None, bevel=0.0, segments=6).transformed(compose(T(*pos), R(90, 0, 0))))
            for z in (0.16, 1.08):
                a.add("Base", sh.tube(0.115, 0.085, 0.06, steel, bevel=0.0, segments=10).transformed(compose(T(pos[0], pos[1], z), R(90, 0, 0))))
        a.add("Base", sh.rounded_box((0.1, 0.62, 0.08), 0.02, 1, dark).transformed(T(side * 0.58, 0.98, 0.18)))
        a.add("Base", sh.rounded_box((0.1, 0.62, 0.08), 0.02, 1, dark).transformed(T(side * 0.58, 0.98, 1.06)))
    rail = sh.rounded_box((0.18, 0.08, 1.4), 0.02, 1, dark).transformed(T(0, 1.76, -0.2))
    a.add("Base", rail)
    for k in range(6):
        a.add("Base", sh.box((0.22, 0.05, 0.08), steel).transformed(T(0, 1.82, -0.75 + k * 0.22)))
    a.point("muzzle", (0, AXIS_Y, -2.95))
    a.point("grip", (0, -0.1, 0))
    return a
