import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _future_lib import pearl, graphite, CYAN, INK

HALF_W = 3.5
GLASS = (20, 26, 40)


def side_extrude(points, width, mat, bevel=0.1, cap_mats=None):
    mesh = sh.extrude(np.asarray(points, dtype=np.float64), width, mat, bevel=bevel, corner_radius=0.0, cap_mats=cap_mats)
    return mesh.transformed(R(0, -90, 0))


def body_outline():
    pts = [(-7.4, 1.45), (-6.6, 1.05), (-3.0, 0.9), (4.0, 0.9), (6.9, 1.15), (7.3, 1.6), (7.3, 2.45), (6.4, 2.75), (3.6, 2.8), (-2.6, 2.78), (-5.6, 2.45), (-7.3, 1.95)]
    p = np.asarray(pts)
    return sh.round_polyline(p, np.full(len(p), 0.25), 2, closed=True)


def canopy_outline():
    return [(-3.0, 2.7), (3.4, 2.7), (2.6, 3.7), (1.4, 4.15), (-0.8, 4.15), (-1.8, 3.8)]


def side_decals(sign):
    def at(z, y):
        return (z if sign < 0 else -z, -y)

    return [
        {"type": "rect", "center": at(0.4, 1.75), "size": (12.0, 0.12), "color": CYAN, "rough": 0.1, "wear": 0.0},
        {"type": "text", "text": "AERO-X", "center": at(3.6, 2.2), "height": 0.42, "color": INK, "font": "impact", "wear": 0.0},
        {"type": "text", "text": "07", "center": at(-3.8, 2.15), "height": 0.6, "color": CYAN, "font": "impact", "wear": 0.0},
        {"type": "rect", "center": at(0.2, 2.15), "size": (2.6, 0.9), "radius": 0.1, "outline": 0.03, "darken": 0.4, "raise": -0.005},
    ]


def build():
    a = Asset("HoverCar", budget=3000, atlas=1024, ao_radius=0.8, edge_width=0.06, gradient=0.08, highlight=0.45, preview_radius=8.2,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.2)
    a.role("Glow", "neon", color=CYAN)
    a.role("Tail", "neon", color=(255, 60, 90))

    paint = pearl(panel=3.0)
    body = side_extrude(body_outline(), 2 * HALF_W, paint, bevel=0.3, cap_mats=[pearl(panel=3.0, decals=side_decals(-1)), pearl(panel=3.0, decals=side_decals(1))])
    x = body.pos[:, 0]
    y = body.pos[:, 1]
    body.pos[:, 0] = x * (1 - 0.1 * np.clip((y - 1.6) / 1.2, 0, 1))
    body = sh.recompute_normals(body)
    a.add("Body", body)
    a.add("Glass", side_extrude(canopy_outline(), 5.4, None, bevel=0.25))
    a.add("Body", side_extrude([(-1.0, 4.08), (1.6, 4.08), (1.5, 4.22), (-0.9, 4.22)], 4.4, pearl(panel=3.0), bevel=0.05))

    dark = graphite(panel=2.0)
    for sx in (-1, 1):
        fin = side_extrude([(4.6, 2.7), (6.8, 2.7), (7.2, 4.1), (6.6, 4.1)], 0.3, paint, bevel=0.06)
        a.add("Body", fin.transformed(compose(T(sx * 2.9, 0, 0), R(0, 0, -sx * 12))))
        pod = sh.lathe([(0.0, -0.9), (0.55, -0.85), (0.65, -0.3), (0.65, 0.5), (0.5, 0.9), (0.0, 0.95)], 12, dark, smooth_angle=40)
        for z in (-4.6, 4.4):
            place = compose(T(sx * 2.7, 0.75, z), R(90, 0, 0), S(1.0, 1.0, 0.7))
            a.add("Body", pod.transformed(place))
            a.add("Glow", sh.lathe([(0.0, -0.08), (0.6, -0.08)], 12, None, smooth_angle=40).transformed(compose(T(sx * 2.7, 0.3, z), S(1.0, 1.0, 1.0))))
        a.add("Glow", sh.box((0.08, 0.1, 10.8), None).transformed(T(sx * (HALF_W + 0.02), 1.2, 0.0)))
    wing = side_extrude([(6.3, 3.5), (7.6, 3.5), (7.6, 3.68), (6.3, 3.68)], 7.0, paint, bevel=0.04)
    a.add("Body", wing)

    for sx in (-1, 1):
        nozzle = sh.lathe([(0.0, -0.7), (0.45, -0.7), (0.55, -0.2), (0.75, 0.55), (0.62, 0.62), (0.42, 0.3)], 12, dark, smooth_angle=40)
        a.add("Body", nozzle.transformed(compose(T(sx * 1.8, 1.9, 7.2), R(90, 0, 0))))
        a.add("Glow", sh.lathe([(0.44, 0.32), (0.0, 0.32)], 12, None, smooth_angle=40).transformed(compose(T(sx * 1.8, 1.9, 7.2), R(90, 0, 0))))
        a.add("Tail", sh.box((2.0, 0.18, 0.05), None).transformed(T(sx * 2.2, 2.55, 7.32)))
        a.add("Glow", sh.box((1.6, 0.16, 0.05), None).transformed(T(sx * 2.3, 1.55, -7.36)))
    nose = pearl(panel=3.0, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (3.0, 0.3), "radius": 0.15, "color": INK, "wear": 0.0},
        {"type": "text", "text": "WR", "center": (0.0, 0.0), "height": 0.24, "color": CYAN, "font": "impact", "wear": 0.0},
    ])
    a.add("Body", sh.rounded_box((3.4, 0.5, 0.12), 0.05, 1, dark, face_mats={"-z": nose}).transformed(T(0, 1.4, -7.38)))

    destructible(a, "FutureDistrict")
    collider(a, "Hitbox", (7.0, 2.0, 14.6), (0, 1.85, 0))
    collider(a, "Canopy", (5.2, 1.4, 5.4), (0, 3.45, 0.2))
    return a
