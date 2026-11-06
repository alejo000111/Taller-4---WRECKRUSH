import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
import _egg_common

EGG_Y = 6.3
EGG_HEIGHT = 7.4
EGG_RADIUS = 2.75


def egg_arc_from_top(y_local, rings=14):
    prof = sh.egg_profile(EGG_HEIGHT, EGG_RADIUS, 0.18, rings)
    seg = np.linalg.norm(np.diff(prof, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(seg)])
    return float(arc[-1] - np.interp(y_local, prof[:, 1], arc))


def build():
    a = Asset("EggIncubator", budget=7000, atlas=1024, ao_radius=1.0, edge_width=0.1, preview_radius=8.5)
    a.role("Base", "surface")
    a.role("Cradle", "surface")
    a.role("Egg", "surface")
    a.role("Glow", "neon", color=(255, 170, 40))
    a.role("Glass", "glass", color=(200, 230, 255), transparency=0.55)

    r_ref = EGG_RADIUS * 1.06
    v_q = egg_arc_from_top(0.55)
    marks = [{"type": "text", "text": "?", "center": (u, v_q), "height": 1.5, "color": (255, 248, 230), "font": "black", "wear": 0.25} for u in (np.pi * r_ref * 0.5, np.pi * r_ref, np.pi * r_ref * 1.5)]
    shell_paint = Material("paint", color=(255, 160, 40), wear=0.25, scratches=0.2, dirt=0.15, rough=0.3, skin=False, decals=marks)
    hazard = Material("hazard", color=(255, 210, 31), color2=(22, 22, 26), width=0.45, wear=0.35, skin=False)
    deck = Material("diamondplate", color=(70, 74, 84), pitch=0.5, dirt=0.4)
    steel = Material("metal", color=(70, 74, 86), rough=0.38, polish=0.6, dirt=0.35, skin=False)
    arm_mat = Material("paint", color=(46, 48, 56), under=(150, 152, 160), wear=0.35, dirt=0.3, skin=False)
    pipe_mat = Material("rubber", color=(30, 30, 34), pattern="ribs", freq=6.0)

    a.add("Base", sh.lathe([(6.75, 1.2), (0.0, 1.2)], 28, deck))
    a.add("Base", sh.lathe([(7.0, 0.0), (7.0, 0.95), (6.75, 1.2)], 28, hazard, smooth_angle=30))
    a.add("Glow", sh.torus(7.12, 0.09, None, segments=32, sides=4).transformed(T(0, 0.45, 0)))
    a.add("Glow", sh.torus(2.55, 0.06, None, segments=24, sides=4).transformed(T(0, 1.26, 0)))

    pedestal = sh.lathe([(0.0, 1.2), (2.4, 1.2), (2.4, 1.62), (1.95, 2.05), (1.45, 2.5), (0.0, 2.6)], 24, steel, smooth_angle=30)
    a.add("Cradle", pedestal)
    for k in range(3):
        ang = np.radians(90 + k * 120)
        d = np.array([np.cos(ang), 0.0, -np.sin(ang)])
        pts = [d * r + np.array([0, y, 0]) for r, y in ((2.2, 1.7), (3.25, 3.0), (3.45, 4.8), (3.08, 6.6))]
        a.add("Cradle", sh.sweep(pts, 0.17, 6, arm_mat, samples=10))
        tip = sh.rounded_box((0.5, 0.7, 0.3), 0.06, 1, steel)
        facing = np.degrees(np.arctan2(d[0], d[2]))
        a.add("Cradle", tip.transformed(compose(T(*(d * 3.02 + np.array([0, 6.6, 0]))), R(0, facing, 0), R(-12, 0, 0))))
        a.add("Glow", sh.sphere(0.17, None, 8, 4).transformed(T(*(d * 3.42 + np.array([0, 4.8, 0])))))
        base_plate = sh.rounded_box((1.0, 0.24, 1.0), 0.06, 1, steel)
        a.add("Cradle", base_plate.transformed(compose(T(*(d * 2.25 + np.array([0, 1.3, 0]))), R(0, facing, 0))))

    for k, ang in enumerate((30, 210)):
        t = np.radians(ang)
        d = np.array([np.cos(t), 0.0, -np.sin(t)])
        pts = [d * 6.4 + np.array([0, 1.3, 0]), d * 5.2 + np.array([0, 1.75, 0]), d * 3.6 + np.array([0, 1.6, 0]), d * 2.3 + np.array([0, 1.5, 0])]
        a.add("Base", sh.sweep(pts, 0.13, 6, pipe_mat, samples=10))

    egg = sh.lathe(sh.egg_profile(EGG_HEIGHT, EGG_RADIUS, 0.18, 18), 28, shell_paint, smooth_angle=89, start=270, r_ref=r_ref)
    a.add("Egg", egg.transformed(T(0, EGG_Y, 0)))
    band_y = (-0.45, 0.25)
    ys = np.linspace(band_y[0], band_y[1], 3)
    prof = [(_egg_common.egg_radius(band_y[0], EGG_HEIGHT, EGG_RADIUS) - 0.03, band_y[0])]
    prof += [(_egg_common.egg_radius(y, EGG_HEIGHT, EGG_RADIUS) + 0.1, y) for y in ys]
    prof += [(_egg_common.egg_radius(band_y[1], EGG_HEIGHT, EGG_RADIUS) - 0.03, band_y[1])]
    a.add("Egg", sh.lathe(prof, 28, hazard, smooth_angle=50).transformed(T(0, EGG_Y, 0)))

    console_face = Material("screen", color=(14, 22, 30), decals=[
        {"type": "text", "text": "PETS", "center": (0.0, -0.22), "height": 0.32, "color": (255, 170, 40), "font": "impact", "wear": 0.0},
        {"type": "rect", "center": (-0.35, 0.18), "size": (0.5, 0.08), "color": (60, 255, 140), "wear": 0.0},
        {"type": "rect", "center": (0.3, 0.18), "size": (0.6, 0.08), "color": (255, 59, 160), "wear": 0.0},
    ])
    console = sh.rounded_box((1.8, 1.1, 0.9), 0.06, 1, steel).transformed(T(0, 1.75, -5.2))
    a.add("Cradle", console)
    panel = sh.rounded_box((1.6, 0.08, 0.9), 0.03, 1, steel, face_mats={"+y": console_face})
    a.add("Cradle", panel.transformed(compose(T(0, 2.4, -5.25), R(-28, 0, 0))))
    for k, x in enumerate((-0.6, -0.3, 0.3, 0.6)):
        a.add("Glow", sh.sphere(0.06, None, 8, 4).transformed(T(x, 2.32, -5.66)))
    a.add("Base", sh.rounded_box((3.0, 0.36, 1.2), 0.05, 1, deck).transformed(T(0, 0.18, -7.4)))
    for k in range(4):
        ang = np.radians(45 + k * 90)
        d = np.array([np.cos(ang), 0.0, -np.sin(ang)])
        base = d * 3.9
        a.add("Glass", sh.cylinder(0.32, 2.2, None, bevel=0.0, segments=14).transformed(T(base[0], 2.4, base[2])))
        a.add("Glow", sh.cylinder(0.2, 2.0, None, bevel=0.0, segments=10).transformed(T(base[0], 2.4, base[2])))
        for y in (1.25, 3.55):
            a.add("Cradle", sh.cylinder(0.38, 0.2, steel, bevel=0.03, segments=14).transformed(T(base[0], y, base[2])))
    for k in range(4):
        ang = np.radians(k * 90)
        d = np.array([np.cos(ang), 0.0, -np.sin(ang)])
        post = d * 6.45
        a.add("Cradle", sh.cylinder(0.12, 2.2, steel, bevel=0.02, segments=10).transformed(T(post[0], 2.3, post[2])))
        a.add("Cradle", sh.cylinder(0.22, 0.12, steel, bevel=0.02, segments=12).transformed(T(post[0], 3.45, post[2])))
        a.add("Glow", sh.sphere(0.2, None, 12, 6).transformed(T(post[0], 3.68, post[2])))
    a.point("prompt", (0, EGG_Y, 0))
    a.point("label", (0, EGG_Y + EGG_HEIGHT / 2 + 1.6, 0))
    a.point("particles", (0, EGG_Y, 0))
    a.meta["platform_radius"] = 7.0
    a.meta["platform_height"] = 1.2
    a.meta["egg"] = {"center_y": EGG_Y, "height": EGG_HEIGHT, "radius": EGG_RADIUS}
    return a
