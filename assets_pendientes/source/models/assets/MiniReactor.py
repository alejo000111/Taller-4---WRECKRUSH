import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _future_lib import pearl, graphite, CYAN, INK

GLASS = (150, 220, 255)
CORE_Y0 = 3.0
CORE_Y1 = 12.4
CAP_Y = 13.0


def build():
    a = Asset("MiniReactor", budget=3500, atlas=1024, ao_radius=1.0, edge_width=0.07, gradient=0.08, highlight=0.45, preview_radius=9.6,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.6)
    a.role("Glow", "neon", color=CYAN)

    dark = graphite(panel=3.0)
    base_mat = graphite(panel=3.0, decals=[
        {"type": "stripes", "center": (np.pi * 5.8, 0.6), "size": (2 * np.pi * 5.8 + 0.4, 0.5), "width": 0.4, "color": (255, 210, 31), "wear": 0.2},
    ])
    a.add("Body", sh.lathe([(0.0, 0.0), (5.9, 0.0), (5.9, 0.9), (5.5, 1.2), (0.0, 1.2)], 8, base_mat, smooth_angle=20, start=22.5))
    a.add("Glow", sh.lathe([(5.52, 1.19), (5.0, 1.19)], 8, None, smooth_angle=20, start=22.5))
    pearl_mat = pearl(panel=4.0, decals=[
        {"type": "text", "text": "REACTOR 02", "center": (np.pi / 2 * 4.0, 0.9), "height": 0.4, "color": INK, "font": "impact", "wear": 0.0},
        {"type": "rect", "center": (np.pi / 2 * 4.0 + 6.3, 0.9), "size": (1.0, 1.0), "angle": 45, "color": (255, 210, 31), "wear": 0.0},
        {"type": "text", "text": "!", "center": (np.pi / 2 * 4.0 + 6.3, 0.92), "height": 0.6, "color": INK, "font": "black", "wear": 0.0},
    ])
    a.add("Body", sh.lathe([(0.0, 1.2), (4.2, 1.2), (4.2, 2.4), (3.4, 3.0), (0.0, 3.0)], 12, pearl_mat, smooth_angle=30, r_ref=4.0))

    a.add("Glass", sh.lathe([(2.2, CORE_Y0), (2.2, CORE_Y1)], 16, None, smooth_angle=60))
    a.add("Glow", sh.lathe([(0.0, CORE_Y0 + 0.2), (0.75, CORE_Y0 + 0.2), (0.75, CORE_Y1 - 0.2), (0.0, CORE_Y1 - 0.2)], 10, None, smooth_angle=60))
    a.add("Glow", sh.sphere(1.4, None, 12, 7).transformed(T(0, (CORE_Y0 + CORE_Y1) / 2, 0)))
    for y in (4.6, 7.7, 10.8):
        a.add("Body", sh.lathe([(2.15, y - 0.25), (2.8, y - 0.25), (2.95, y), (2.8, y + 0.25), (2.15, y + 0.25)], 14, dark, closed=True, smooth_angle=40))
        a.add("Glow", sh.lathe([(2.96, y - 0.05), (2.96, y + 0.05)], 14, None, smooth_angle=40))

    for k in range(4):
        ang = np.radians(45 + 90 * k)
        d = np.array([np.cos(ang), 0.0, np.sin(ang)])
        p = d * 3.6
        pillar = sh.extrude([(-0.45, -0.45), (0.45, -0.45), (0.45, 0.45), (-0.45, 0.45)], CAP_Y - 2.4, pearl(panel=4.0), bevel=0.12, corner_radius=0.0)
        a.add("Body", pillar.transformed(compose(T(p[0], (CAP_Y + 2.4) / 2, p[2]), R(90, 0, 0), R(0, 0, -np.degrees(ang)))))
        a.add("Glow", sh.box((0.08, CAP_Y - 4.0, 0.08), None).transformed(T(*(d * 3.12 + np.array([0, (CAP_Y + 3.2) / 2, 0])))))
        fin_ang = np.radians(90 * k)
        f = np.array([np.cos(fin_ang), 0.0, np.sin(fin_ang)])
        fin = sh.extrude([(0.0, 0.0), (1.6, 0.0), (1.6, 2.6), (0.0, 3.4)], 0.3, dark, bevel=0.05, corner_radius=0.0)
        a.add("Body", fin.transformed(compose(T(*(f * 4.0 + np.array([0, 1.2, 0]))), R(0, -np.degrees(fin_ang), 0))))

    cap = pearl(panel=4.0)
    a.add("Body", sh.lathe([(0.0, CAP_Y - 0.6), (4.3, CAP_Y - 0.6), (4.5, CAP_Y - 0.2), (4.0, CAP_Y + 0.3), (2.0, CAP_Y + 0.6), (0.0, CAP_Y + 0.65)], 12, cap, smooth_angle=30))
    a.add("Body", sh.lathe([(0.0, CAP_Y + 0.6), (1.2, CAP_Y + 0.6), (1.0, CAP_Y + 1.4), (0.5, CAP_Y + 1.6), (0.0, CAP_Y + 1.6)], 10, dark, smooth_angle=40))
    a.add("Glow", sh.lathe([(0.0, CAP_Y + 1.6), (0.45, CAP_Y + 1.62), (0.0, CAP_Y + 2.2)], 10, None, smooth_angle=60))

    destructible(a, "FutureDistrict")
    collider(a, "Hitbox", (8.4, CAP_Y - 1.2, 8.4), (0, (CAP_Y + 1.2) / 2, 0), shape="Cylinder")
    collider(a, "Base", (11.8, 1.2, 11.8), (0, 0.6, 0), shape="Cylinder")
    return a
