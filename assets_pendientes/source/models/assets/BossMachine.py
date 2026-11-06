import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _military_lib import military_track

RED = (255, 90, 60)
ORANGE = (240, 96, 52)
INK = (18, 18, 20)


def dark(decals=()):
    return Material("metal", color=(40, 40, 46), rough=0.4, polish=0.5, dirt=0.4, scratches=0.35, decals=list(decals))


def armor(decals=()):
    return Material("paint", color=ORANGE, under=(130, 130, 136), wear=0.35, scratches=0.4, rough=0.4, metal=0.2, dirt=0.4, skin=False, decals=list(decals))


def side_extrude(points, width, mat, bevel=0.15, cap_mats=None):
    mesh = sh.extrude(np.asarray(points, dtype=np.float64), width, mat, bevel=bevel, corner_radius=0.0, cap_mats=cap_mats)
    return mesh.transformed(R(0, -90, 0))


def track_outline():
    return [(-12.2, 2.4), (-11.0, 0.3), (-9.6, 0.0), (9.6, 0.0), (11.0, 0.3), (12.2, 2.4), (11.4, 4.6), (-11.4, 4.6)]


def drill(mat, glow):
    body = sh.lathe([(0.0, 0.0), (2.3, 0.0), (2.0, 1.2), (1.4, 2.6), (0.8, 3.8), (0.2, 4.8), (0.0, 5.0)], 10, mat, smooth_angle=30)
    flutes = []
    for k in range(3):
        pts = []
        for t in np.linspace(0.0, 1.0, 10):
            r = 2.2 * (1 - t) + 0.25
            ang = k * 2 * np.pi / 3 + t * 4.0
            pts.append((np.cos(ang) * r, t * 4.6, np.sin(ang) * r))
        flutes.append(sh.sweep(pts, 0.14, 4, None))
    return [body], flutes


def build():
    a = Asset("BossMachine", budget=6000, atlas=1024, ao_radius=2.0, edge_width=0.12, gradient=0.06, highlight=0.5, preview_radius=21.0,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("FRONT", 180, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=RED)

    track = Material("military_track", pitch=0.6, width=7.0, dirt=0.6)
    for sx in (-1, 1):
        a.add("Body", side_extrude(track_outline(), 6.6, track, bevel=0.12).transformed(T(sx * 10.0, 0, 0)))
        for z in np.linspace(-8.4, 8.4, 5):
            a.add("Body", sh.cylinder(2.0, 0.4, armor(), bevel=0.08, segments=12).transformed(compose(T(sx * 13.45, 2.3, z), R(0, 0, 90))))
        guard = armor([{"type": "stripes", "center": (0.0, 0.0), "size": (24.0, 0.6), "width": 0.6, "color": INK, "wear": 0.3}])
        a.add("Body", sh.rounded_box((7.4, 0.6, 24.0), 0.08, 1, dark(), face_mats={"+y": guard}).transformed(T(sx * 10.0, 5.0, 0)))

    hull_face = dark([{"type": "rect", "center": (0.0, 0.0), "size": (14.0, 0.8), "color": (30, 30, 34), "wear": 0.0}])
    a.add("Body", sh.rounded_box((14.0, 5.0, 18.0), 0.3, 1, dark(), face_mats={"-z": hull_face}).transformed(T(0, 6.5, 0)))
    a.add("Glow", sh.box((14.1, 0.6, 0.1), None).transformed(T(0, 7.5, -9.05)))

    torso = sh.extrude([(-8.0, 0.0), (8.0, 0.0), (8.6, 6.0), (7.0, 11.0), (-7.0, 11.0), (-8.6, 6.0)], 13.0, armor(), bevel=0.3, corner_radius=0.0)
    a.add("Body", torso.transformed(T(0, 9.0, 0)))
    plate = dark([
        {"type": "rivets", "points": [(x, y) for x in np.linspace(-7.0, 7.0, 8) for y in (-1.2, 1.2)], "radius": 0.16, "color": (110, 110, 116), "height": 0.03},
        {"type": "text", "text": "BOSS-01", "center": (4.6, 0.0), "height": 1.0, "color": RED, "font": "impact", "wear": 0.3},
    ])
    a.add("Body", sh.rounded_box((16.4, 3.0, 2.0), 0.2, 1, dark(), face_mats={"-z": plate}).transformed(T(0, 18.6, -6.6)))
    rim = sh.lathe([(1.8, 0.0), (2.9, 0.0), (2.9, 0.5), (2.5, 0.7), (1.8, 0.6)], 16, dark(), closed=True, smooth_angle=40)
    a.add("Body", rim.transformed(compose(T(0, 14.2, -6.5), R(-90, 0, 0))))
    a.add("Glow", sh.sphere(2.0, None, 14, 8).transformed(compose(T(0, 14.2, -6.4), S(1.0, 1.0, 0.45))))

    for sx in (-1, 1):
        sh_ = sh.rounded_box((5.6, 5.0, 7.0), 0.4, 1, armor())
        a.add("Body", sh_.transformed(T(sx * 10.6, 18.8, 0)))
        spike = sh.lathe([(0.0, 0.0), (1.4, 0.0), (0.4, 3.4), (0.0, 3.6)], 6, dark(), smooth_angle=20)
        a.add("Body", spike.transformed(compose(T(sx * 10.6, 21.2, 0), R(0, 0, -sx * 12))))
        arm = sh.rounded_box((4.0, 4.0, 9.0), 0.3, 1, dark())
        a.add("Body", arm.transformed(T(sx * 11.0, 15.0, -3.6)))
        a.add("Body", sh.cylinder(0.4, 7.0, Material("metal", color=(200, 204, 212), rough=0.15, polish=0.9, dirt=0.2), bevel=0.0, segments=8).transformed(compose(T(sx * 11.0, 17.4, -3.6), R(90, 0, 0))))

    mount = armor()
    a.add("Body", sh.cylinder(2.8, 2.0, mount, bevel=0.15, segments=12).transformed(compose(T(-11.0, 15.0, -8.8), R(90, 0, 0))))
    body, flutes = drill(Material("metal", color=(180, 184, 192), rough=0.25, polish=0.8, dirt=0.3), None)
    place = compose(T(-11.0, 15.0, -9.6), R(-90, 0, 0))
    a.add("Body", [m.transformed(place) for m in body])
    a.add("Glow", [m.transformed(place) for m in flutes])

    a.add("Body", sh.cylinder(1.6, 2.0, mount, bevel=0.15, segments=12).transformed(compose(T(11.0, 13.0, -8.4), R(0, 0, 90))))
    blade = Material("metal", color=(150, 154, 166), rough=0.2, polish=0.9, dirt=0.3)
    teeth = []
    for k in range(16):
        ang = k * 2 * np.pi / 16
        r0, r1 = 4.0, 4.7
        teeth += [(np.cos(ang) * r1, np.sin(ang) * r1), (np.cos(ang + 0.25) * r0, np.sin(ang + 0.25) * r0)]
    saw = sh.extrude(teeth, 0.35, blade, bevel=0.02, corner_radius=0.0)
    a.add("Body", saw.transformed(compose(T(11.0, 13.0, -10.6), R(0, 90, 0))))
    a.add("Glow", sh.cylinder(1.3, 0.5, None, bevel=0.0, segments=12).transformed(compose(T(11.0, 13.0, -10.6), R(0, 0, 90))))

    a.add("Body", sh.cylinder(2.5, 1.6, dark(), bevel=0.1, segments=10).transformed(T(0, 20.8, 0)))
    head = sh.extrude([(-4.5, 0.0), (4.5, 0.0), (4.2, 3.6), (3.0, 5.5), (-3.0, 5.5), (-4.2, 3.6)], 7.5, dark(), bevel=0.25, corner_radius=0.0)
    a.add("Body", head.transformed(T(0, 21.5, -0.5)))
    for sx in (-1, 1):
        a.add("Glow", sh.box((2.2, 1.0, 0.2), None).transformed(compose(T(sx * 2.0, 24.6, -4.32), R(0, 0, sx * 10))))
        a.add("Body", sh.box((3.0, 0.7, 0.9), armor()).transformed(compose(T(sx * 2.0, 25.6, -4.4), R(0, 0, sx * 14))))
        horn = sh.lathe([(0.0, 0.0), (0.9, 0.0), (0.5, 2.4), (0.0, 3.2)], 6, armor(), smooth_angle=20)
        a.add("Body", horn.transformed(compose(T(sx * 3.4, 26.8, 0.0), R(0, 0, -sx * 25))))
    a.add("Body", sh.box((6.0, 1.2, 1.0), Material("metal", color=(20, 20, 22), rough=0.4, polish=0.5, dirt=0.3)).transformed(T(0, 22.4, -4.5)))
    a.add("Glow", sh.box((5.0, 0.3, 0.1), None).transformed(T(0, 22.4, -5.05)))
    a.add("Body", sh.cylinder(0.15, 3.4, dark(), bevel=0.0, segments=6).transformed(T(2.5, 28.7, 1.5)))
    a.add("Glow", sh.sphere(0.4, None, 8, 5).transformed(T(2.5, 30.5, 1.5)))

    pack = dark([{"type": "rect", "center": (0.0, y), "size": (10.0, 0.2), "darken": 0.6, "raise": -0.006} for y in (-2.0, -1.0, 0.0, 1.0, 2.0)])
    a.add("Body", sh.rounded_box((12.0, 8.0, 3.5), 0.3, 1, dark(), face_mats={"+z": pack}).transformed(T(0, 15.0, 8.2)))
    for x in (-3.5, 0.0, 3.5):
        a.add("Glow", sh.box((2.5, 0.4, 0.1), None).transformed(T(x, 15.0, 10.0)))
    for sx in (-1, 1):
        stack = sh.lathe([(0.0, 0.0), (1.0, 0.0), (1.0, 7.4), (1.2, 7.6), (1.2, 8.0), (0.8, 8.0), (0.8, 7.6), (0.0, 7.6)], 10, armor(), smooth_angle=40)
        a.add("Body", stack.transformed(T(sx * 4.0, 19.0, 8.5)))
        a.add("Glow", sh.lathe([(0.8, 0.0), (0.0, 0.0)], 10, None, smooth_angle=40).transformed(T(sx * 4.0, 26.6, 8.5)))

    destructible(a, "Event")
    collider(a, "Hitbox", (16.4, 11.0, 13.0), (0, 14.5, 0))
    collider(a, "Tracks", (27.0, 9.0, 24.0), (0, 4.5, 0))
    collider(a, "Head", (9.0, 5.5, 7.5), (0, 24.2, -0.5))
    collider(a, "Arms", (27.0, 5.0, 12.0), (0, 15.0, -4.0))
    return a
