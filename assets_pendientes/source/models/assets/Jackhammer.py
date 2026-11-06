import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
import _hammers_lib
from _launch_lib import pistol_grip, side_profile

AXIS_Y = 0.8
YELLOW = (255, 210, 31)
DARK = (50, 52, 58)


def forward(mesh, x=0.0, y=AXIS_Y, z=0.0):
    return mesh.transformed(compose(T(x, y, z), R(-90, 0, 0)))


def build():
    a = Asset("Jackhammer", budget=5500, ao_radius=0.35)
    a.role("Primary", "surface", color=YELLOW, skin="Primary")
    a.role("AccentTrim", "surface", color=DARK, skin="Accent")
    a.role("Base", "surface")
    a.role("Glow", "neon", color=(60, 255, 120))

    paint = Material("paint", color=YELLOW, wear=0.45, scratches=0.4, dirt=0.4, rough=0.42)
    housing_side = Material("paint", color=YELLOW, wear=0.4, scratches=0.35, dirt=0.35, rough=0.4, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (1.05, 0.3), "radius": 0.04, "color": (22, 22, 26), "wear": 0.3},
        {"type": "text", "text": "JACK-250", "center": (0.0, 0.01), "height": 0.17, "color": YELLOW, "font": "impact", "wear": 0.3},
    ])
    housing_top = Material("paint", color=YELLOW, wear=0.4, scratches=0.35, dirt=0.35, rough=0.4, decals=[
        {"type": "rect", "center": (0.0, -0.45 + k * 0.3), "size": (0.62, 0.07), "radius": 0.02, "color": (20, 20, 24), "wear": 0.0, "raise": -0.01} for k in range(4)
    ])
    vent_side = Material("metal", color=DARK, rough=0.4, polish=0.7, dirt=0.35, skin=True, decals=[
        {"type": "rect", "center": (-0.28 + k * 0.19, 0.0), "size": (0.06, 0.34), "radius": 0.02, "color": (14, 14, 16), "wear": 0.0, "raise": -0.012} for k in range(4)
    ])
    trim = Material("metal", color=DARK, rough=0.4, polish=0.7, dirt=0.35, skin=True, decals=[
        {"type": "rivets", "points": [(u, 0.09) for u in np.linspace(0.3, 3.7, 6)], "radius": 0.04, "height": 0.012},
    ])
    plain_trim = Material("metal", color=DARK, rough=0.4, polish=0.7, dirt=0.35, skin=True)
    dark = Material("metal", color=(58, 60, 68), rough=0.42, polish=0.6, dirt=0.4, skin=False)
    steel = Material("metal", color=(170, 172, 182), rough=0.3, polish=0.8, brushed=True, dirt=0.3, skin=False)
    bit_steel = Material("hammers_heat", color=(150, 152, 160), center=(0, AXIS_Y, -3.2), axis=(0, 0, -1), length=1.6, amount=0.55, soot=0.2)
    rubber = Material("rubber", color=(26, 26, 30), pattern="knurl", freq=12.0, depth=0.01)
    grip_rubber = Material("rubber", color=(28, 28, 32), pattern="ribs", freq=9.0, depth=0.012)
    hose = Material("rubber", color=(34, 32, 30), pattern="ribs", freq=22.0, depth=0.007)
    frame = Material("metal", color=(44, 46, 52), rough=0.45, polish=0.5, dirt=0.4, skin=False)

    a.add("Base", pistol_grip(frame, rubber, dark, steel, width=0.4))
    a.add("Base", sh.cylinder(0.12, 1.7, dark, bevel=0.0, segments=8).transformed(compose(T(0, AXIS_Y, 0.02), R(0, 0, 90))))
    for side in (-1, 1):
        g = sh.lathe([(0.12, -0.26), (0.22, -0.25), (0.22, -0.2), (0.205, -0.15), (0.215, 0.0), (0.205, 0.15), (0.22, 0.2), (0.22, 0.25), (0.12, 0.26)], 14, grip_rubber)
        a.add("Base", g.transformed(compose(T(side * 0.66, AXIS_Y, 0.02), R(0, 0, 90))))
    a.add("Base", sh.box((0.42, 0.42, 0.42), dark).transformed(T(0, AXIS_Y, 0.02)))
    a.add("Base", forward(sh.lathe([(0, 0.18), (0.15, 0.18), (0.15, 0.5), (0.2, 0.56), (0.2, 0.82), (0, 0.82)], 14, steel, smooth_angle=30)))

    body_prof = [(0, 0.78), (0.45, 0.78), (0.55, 0.9)]
    for k in range(5):
        z = 1.0 + k * 0.24
        body_prof += [(0.55, z), (0.6, z + 0.04), (0.6, z + 0.12), (0.55, z + 0.16)]
    body_prof += [(0.57, 2.45), (0.52, 2.72), (0.36, 2.8), (0, 2.8)]
    a.add("Primary", forward(sh.lathe(body_prof, 24, paint, smooth_angle=40)))
    housing = sh.rounded_box((0.86, 0.5, 1.42), 0.1, 1, paint, face_mats={"+x": housing_side, "-x": housing_side, "+y": housing_top})
    a.add("Primary", housing.transformed(T(0, AXIS_Y + 0.56, -1.72)))

    for zc in (-1.0, -2.6):
        a.add("AccentTrim", forward(sh.tube(0.64, 0.5, 0.18, trim, bevel=0.025, segments=24), z=zc))
    for side in (-1, 1):
        a.add("AccentTrim", sh.rounded_box((0.12, 0.46, 0.78), 0.035, 1, plain_trim, face_mats={("+x" if side > 0 else "-x"): vent_side}).transformed(T(side * 0.6, AXIS_Y, -1.8)))
    throttle = side_profile([(-0.28, 0.62), (-0.24, 0.62), (-0.28, 0.3), (-0.4, 0.05), (-0.46, 0.08), (-0.36, 0.32)], 0.12, plain_trim, bevel=0.02, corner_radius=0.0)
    a.add("AccentTrim", throttle)

    a.add("Base", forward(sh.prism(6, 0.34, 0.32, steel, bevel=0.025), z=-2.98))
    a.add("Base", forward(sh.lathe([(0, 0), (0.24, 0), (0.24, 0.12), (0.18, 0.18), (0, 0.18)], 16, dark), z=-3.1))
    a.add("Base", forward(sh.lathe([(0, 0), (0.15, 0), (0.15, 0.08), (0.13, 0.12), (0.13, 1.18), (0, 1.18)], 12, bit_steel, smooth_angle=30), z=-3.24))
    tip = sh.extrude([(0.0, -0.12), (0.42, -0.04), (0.47, 0.0), (0.42, 0.04), (0.0, 0.12)], 0.3, bit_steel, bevel=0.015, corner_radius=0.0)
    a.add("Base", tip.transformed(compose(T(0, AXIS_Y, -4.38), R(0, 90, 0))))

    path = [(0.0, AXIS_Y - 0.5, -1.2), (0.08, AXIS_Y - 0.78, -0.85), (0.16, -0.25, -0.35), (0.14, -0.55, 0.15), (0.05, -0.6, 0.55)]
    a.add("Base", sh.sweep(path, 0.07, 8, hose, samples=14))
    for end in (path[0], path[-1]):
        a.add("Base", sh.cylinder(0.095, 0.12, steel, bevel=0.015, segments=10).transformed(T(*end)))

    coil = sh.spring(0.22, 0.03, 4.5, 0.46, steel, sides=5, samples_per_turn=12)
    a.add("Base", forward(coil, z=-0.5))
    exhaust = [(0.42, AXIS_Y + 0.38, -2.3), (0.55, AXIS_Y + 0.62, -2.15), (0.58, AXIS_Y + 0.95, -1.95), (0.5, AXIS_Y + 1.1, -1.7)]
    a.add("Base", sh.sweep(exhaust, 0.07, 8, dark, samples=10))
    a.add("Base", sh.tube(0.1, 0.07, 0.12, steel, bevel=0.01, segments=10).transformed(compose(T(0.5, AXIS_Y + 1.12, -1.68), R(-60, 0, 0))))
    arch = [(0.0, AXIS_Y + 0.82, -1.25), (0.0, AXIS_Y + 1.2, -1.4), (0.0, AXIS_Y + 1.28, -1.75), (0.0, AXIS_Y + 1.2, -2.1), (0.0, AXIS_Y + 0.82, -2.25)]
    a.add("Base", sh.sweep(arch, 0.07, 8, grip_rubber, samples=12))
    for k, dz in enumerate((-1.45, -1.62, -1.79)):
        a.add("Glow", sh.sphere(0.045, None, 8, 4).transformed(T(0.47, AXIS_Y + 0.4, dz)))
    a.point("muzzle", (0, AXIS_Y, -4.8))
    a.point("grip", (0, -0.1, 0))
    return a
