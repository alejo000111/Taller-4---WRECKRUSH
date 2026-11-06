import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
import _hammers_lib
from _launch_lib import pistol_grip, trigger_group

CENTER_Y = 1.37
WHITE = (230, 230, 236)
RED = (230, 40, 40)


def forward(mesh, x=0.0, y=0.0, z=0.0):
    return mesh.transformed(compose(T(x, y, z), R(-90, 0, 0)))


def build():
    a = Asset("RocketRig", budget=6500, ao_radius=0.35)
    a.role("Primary", "surface", color=WHITE, skin="Primary")
    a.role("AccentTrim", "surface", color=RED, skin="Accent")
    a.role("Glow", "neon", color=(255, 50, 50))
    a.role("Base", "surface")

    shell = Material("paint", color=WHITE, wear=0.4, scratches=0.35, dirt=0.35, rough=0.38)
    cap = Material("paint", color=RED, wear=0.45, scratches=0.3, dirt=0.3)
    panel = Material("paint", color=RED, wear=0.4, scratches=0.3, dirt=0.3)
    stencil_plus = Material("paint", color=RED, wear=0.4, dirt=0.3, decals=[
        {"type": "text", "text": "R-4", "center": (0.0, -0.12), "height": 0.34, "color": (245, 245, 248), "font": "impact", "wear": 0.35},
        {"type": "stripes", "center": (0.0, 0.36), "size": (1.4, 0.14), "width": 0.09, "color": (24, 24, 28), "wear": 0.3},
    ])
    warhead = Material("paint", color=(214, 36, 36), wear=0.3, skin=False, decals=[{"type": "rect", "center": (0.4, 0.2), "size": (3.0, 0.06), "color": (240, 240, 240), "wear": 0.2}])
    dark = Material("metal", color=(56, 58, 66), rough=0.42, polish=0.6, dirt=0.35, skin=False)
    steel = Material("metal", color=(160, 164, 172), rough=0.3, polish=0.8, dirt=0.3, skin=False)
    bore = Material("hammers_heat", color=(70, 72, 80), center=(0, 0, 1.55), axis=(0, 0, -1), length=0.4, amount=0.6, soot=0.8)
    rubber = Material("rubber", color=(28, 28, 32), pattern="knurl", freq=12.0)
    clamp = Material("metal", color=(56, 58, 66), rough=0.42, polish=0.6, dirt=0.35, skin=False, decals=[{"type": "rivets", "points": [(-0.66, 0.0), (0.66, 0.0), (0.0, -0.66), (0.0, 0.66)], "radius": 0.05, "height": 0.014}])
    pad_rubber = Material("rubber", color=(28, 28, 32), pattern="ribs", freq=8.0)
    glass = Material("glossy", color=(20, 20, 26), rough=0.08)

    a.add("Base", pistol_grip(dark, rubber, dark, steel, width=0.4))
    a.add("Base", trigger_group(dark, steel))
    a.add("Base", sh.rounded_box((0.7, 0.42, 1.72), 0.06, 1, dark).transformed(T(0, 0.76, 0.0)))

    tube_prof = [(0.0, -1.55), (0.26, -1.55), (0.3, -1.5), (0.3, 1.98), (0.24, 1.98), (0.24, 1.66), (0.0, 1.66)]
    nose = sh.lathe([(0, 0), (0.21, 0), (0.21, 0.1), (0.17, 0.22), (0.1, 0.32), (0, 0.38)], 12, warhead, smooth_angle=50)
    for x in (-0.33, 0.33):
        for y in (CENTER_Y - 0.33, CENTER_Y + 0.33):
            a.add("Primary", forward(sh.lathe(tube_prof, 16, shell, smooth_angle=35), x=x, y=y, z=-0.2))
            nozzle = sh.lathe([(0.0, 0.0), (0.2, 0.0), (0.2, 0.06), (0.24, 0.2), (0.17, 0.22), (0.13, 0.08), (0.0, 0.08)], 12, bore, smooth_angle=40)
            a.add("Base", nozzle.transformed(compose(T(x, y, 1.33), R(90, 0, 0))))
            a.add("Base", forward(nose, x=x, y=y, z=-1.86))
            ring = sh.tube(0.335, 0.24, 0.16, cap, bevel=0.02, segments=16)
            a.add("AccentTrim", forward(ring, x=x, y=y, z=-2.12))

    for zc in (-1.0, 0.9):
        for y in (CENTER_Y + 0.67, CENTER_Y - 0.67):
            a.add("Base", sh.rounded_box((1.5, 0.18, 0.28), 0.04, 1, clamp).transformed(T(0, y, zc)))
        for x in (-0.67, 0.67):
            a.add("Base", sh.rounded_box((0.18, 1.5, 0.28), 0.04, 1, clamp).transformed(T(x, CENTER_Y, zc)))

    for side in (-1, 1):
        face = "+x" if side > 0 else "-x"
        slab = sh.rounded_box((0.06, 1.0, 1.5), 0.02, 1, panel, face_mats={face: stencil_plus}).transformed(T(side * 0.79, CENTER_Y, -0.05))
        a.add("AccentTrim", slab)

    a.add("Base", sh.rounded_box((0.26, 0.34, 0.52), 0.05, 1, dark).transformed(T(-0.94, CENTER_Y + 0.25, -0.6)))
    a.add("Base", sh.box((0.12, 0.16, 0.5), dark).transformed(T(-0.86, CENTER_Y + 0.02, -0.6)))
    hood = sh.tube(0.13, 0.1, 0.12, dark, bevel=0.0, segments=10)
    a.add("Base", forward(hood, x=-0.94, y=CENTER_Y + 0.25, z=-0.9))
    a.add("Base", forward(sh.cylinder(0.1, 0.02, glass, bevel=0.0, segments=10), x=-0.94, y=CENTER_Y + 0.25, z=-0.87))
    a.add("Glow", sh.sphere(0.035, None, 6, 3).transformed(T(-0.94, CENTER_Y + 0.25, -0.88)))

    pad = sh.rounded_box((0.86, 0.86, 0.3), 0.1, 1, pad_rubber).transformed(T(0, CENTER_Y, 1.78))
    a.add("Base", pad)
    a.add("Base", sh.box((0.3, 0.3, 0.24), dark).transformed(T(0, CENTER_Y, 1.56)))

    arch = [(0, CENTER_Y + 0.7, 0.5), (0, CENTER_Y + 1.05, 0.35), (0, CENTER_Y + 1.12, -0.1), (0, CENTER_Y + 1.05, -0.55), (0, CENTER_Y + 0.7, -0.7)]
    a.add("Base", sh.sweep(arch, 0.07, 8, rubber, samples=12))
    for z in (0.5, -0.7):
        a.add("Base", sh.rounded_box((0.26, 0.14, 0.26), 0.03, 1, dark).transformed(T(0, CENTER_Y + 0.72, z)))
    grip2 = sh.lathe([(0, -0.38), (0.13, -0.38), (0.15, -0.3), (0.13, 0.25), (0.1, 0.34), (0, 0.34)], 12, rubber)
    a.add("Base", grip2.transformed(T(0, CENTER_Y - 1.0, -1.35)))
    a.add("Base", sh.rounded_box((0.3, 0.2, 0.42), 0.04, 1, dark).transformed(T(0, CENTER_Y - 0.62, -1.35)))
    a.add("Base", sh.rounded_box((0.2, 0.16, 0.5), 0.03, 1, dark).transformed(T(0.0, CENTER_Y - 0.78, -0.55)))
    a.add("Glow", forward(sh.cylinder(0.04, 0.02, None, bevel=0.0, segments=8), x=0.0, y=CENTER_Y - 0.78, z=-0.8))
    a.point("muzzle", (0, CENTER_Y, -2.2))
    a.point("grip", (0, -0.1, 0))
    return a
