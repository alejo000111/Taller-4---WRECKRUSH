import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _military_lib import olive, camo_metal, star, OLIVE_DARK, STENCIL

TRACK_X = 4.6
TRACK_W = 2.2
HULL_Y = 2.4
DECK_Y = 4.3
TURRET_Y = DECK_Y
TURRET_H = 1.9
GUN_Y = TURRET_Y + 0.95


def side_extrude(points, width, mat, bevel=0.05, cap_mats=None):
    mesh = sh.extrude(np.asarray(points, dtype=np.float64), width, mat, bevel=bevel, corner_radius=0.0, cap_mats=cap_mats)
    return mesh.transformed(R(0, -90, 0))


def track_outline():
    return [(-8.6, 1.6), (-7.6, 0.25), (-6.6, 0.0), (6.6, 0.0), (7.8, 0.3), (8.4, 1.4), (8.3, 2.5), (-8.2, 2.5)]


def turret_outline():
    return [(-2.0, -4.6), (2.0, -4.6), (3.3, -2.6), (3.3, 2.4), (2.8, 3.6), (-2.8, 3.6), (-3.3, 2.4), (-3.3, -2.6)]


def turret(mat, top_mat):
    poly = [(x, -z) for x, z in turret_outline()]
    body = sh.extrude(poly, TURRET_H, mat, bevel=0.08, corner_radius=0.0, cap_mats=[None, top_mat])
    body = body.transformed(R(-90, 0, 0))
    y = body.pos[:, 1]
    top = y > 0.0
    body.pos[top, 0] *= 0.86
    body.pos[top, 2] = np.where(body.pos[top, 2] < 0, body.pos[top, 2] * 0.9, body.pos[top, 2] * 0.95)
    return sh.recompute_normals(body.transformed(T(0, TURRET_Y + TURRET_H / 2, 0.6)))


def build():
    a = Asset("ArmoredTank", budget=4500, atlas=1024, ao_radius=1.1, edge_width=0.1, preview_radius=11.0,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Lamp", "neon", color=(255, 236, 190))

    camo = camo_metal(scale=0.22)
    dark = olive((44, 48, 38), metal=0.3, wear=0.4)
    track = Material("military_track", pitch=0.42, width=TRACK_W, dirt=0.6)
    for sx in (-1, 1):
        a.add("Body", side_extrude(track_outline(), TRACK_W, track, bevel=0.06).transformed(T(sx * TRACK_X, 0, 0)))
        for z in np.linspace(-5.8, 5.8, 6):
            wheel = sh.cylinder(0.78, 0.35, dark, bevel=0.06, segments=12)
            a.add("Body", wheel.transformed(compose(T(sx * (TRACK_X + TRACK_W / 2 + 0.12), 0.95, z), R(0, 0, 90))))
        for z, r in ((-7.7, 0.95), (7.6, 1.0)):
            a.add("Body", sh.cylinder(r, 0.4, dark, bevel=0.06, segments=12).transformed(compose(T(sx * (TRACK_X + TRACK_W / 2 + 0.14), 1.45, z), R(0, 0, 90))))
        skirt = camo_metal(scale=0.22, decals=[{"type": "rect", "center": (x, 0.0), "size": (0.04, 1.2), "darken": 0.5, "raise": -0.006} for x in np.linspace(-6.0, 6.0, 5)])
        a.add("Body", sh.rounded_box((0.25, 1.3, 14.4), 0.04, 1, camo, face_mats={"+x" if sx > 0 else "-x": skirt}).transformed(T(sx * (TRACK_X + TRACK_W / 2 + 0.45), 2.45, -0.2)))

    hull = [(-9.2, 3.2), (-7.6, 1.6), (7.2, 1.6), (8.2, 2.4), (8.2, DECK_Y - 0.3), (7.8, DECK_Y), (-5.8, DECK_Y), (-9.4, 3.6)]
    a.add("Body", side_extrude(hull, 7.2, camo, bevel=0.08))
    deck = camo_metal(scale=0.22, decals=star((0.0, 4.5), 2.2, STENCIL, angle=180) + [
        {"type": "text", "text": "WR-12", "center": (0.0, -5.6), "height": 0.7, "color": STENCIL, "font": "impact", "wear": 0.4, "angle": 180},
    ])
    a.add("Body", sh.rounded_box((11.6, 0.35, 15.4), 0.06, 1, camo, faces=["+x", "-x", "+y", "-y", "+z", "-z"], face_mats={"+y": deck}).transformed(T(0, DECK_Y - 0.17, 0.4)))

    side = camo_metal(scale=0.22, decals=[
        {"type": "rect", "center": (-1.4, 0.1), "size": (1.6, 1.0), "radius": 0.06, "color": OLIVE_DARK, "wear": 0.3},
        {"type": "text", "text": "12", "center": (-1.4, 0.12), "height": 0.75, "color": STENCIL, "font": "impact", "wear": 0.35},
    ])
    top = camo_metal(scale=0.22)
    a.add("Body", turret(camo, top))
    for sx in (-1, 1):
        plate = sh.rounded_box((0.06, 1.1, 2.4), 0.0, 1, camo, face_mats={"+x" if sx > 0 else "-x": side})
        a.add("Body", plate.transformed(compose(T(sx * 3.0, TURRET_Y + 0.85, 1.0), R(0, 0, -sx * 9))))

    a.add("Body", sh.rounded_box((2.4, 1.4, 1.0), 0.1, 1, camo).transformed(T(0, GUN_Y, -4.5)))
    barrel = olive((70, 78, 54), metal=0.3, wear=0.35)
    a.add("Body", sh.cylinder(0.32, 6.6, barrel, bevel=0.0, segments=10).transformed(compose(T(0, GUN_Y, -8.0), R(90, 0, 0))))
    a.add("Body", sh.cylinder(0.5, 1.3, barrel, bevel=0.08, segments=10).transformed(compose(T(0, GUN_Y, -7.3), R(90, 0, 0))))
    brake = sh.lathe([(0.3, -0.5), (0.52, -0.5), (0.52, 0.5), (0.3, 0.5)], 10, dark, closed=True, smooth_angle=40)
    a.add("Body", brake.transformed(compose(T(0, GUN_Y, -11.0), R(90, 0, 0))))

    a.add("Body", sh.lathe([(0.0, 0.0), (0.75, 0.0), (0.75, 0.3), (0.6, 0.42), (0.0, 0.42)], 12, camo, smooth_angle=40).transformed(T(1.4, TURRET_Y + TURRET_H, 1.6)))
    mg = Material("metal", color=(40, 42, 40), rough=0.4, polish=0.5, dirt=0.4)
    a.add("Body", sh.cylinder(0.08, 1.8, mg, bevel=0.0, segments=6).transformed(compose(T(1.4, TURRET_Y + TURRET_H + 0.8, 0.6), R(90, 0, 0))))
    a.add("Body", sh.rounded_box((0.3, 0.35, 0.6), 0.04, 1, mg).transformed(T(1.4, TURRET_Y + TURRET_H + 0.75, 1.5)))
    a.add("Body", sh.box((0.08, 0.6, 0.08), mg).transformed(T(1.4, TURRET_Y + TURRET_H + 0.45, 1.5)))
    a.add("Body", sh.cylinder(0.04, 3.0, mg, bevel=0.0, segments=4).transformed(T(-2.4, TURRET_Y + TURRET_H + 1.4, 3.6)))
    for sx in (-1, 1):
        for k in range(3):
            tube = sh.cylinder(0.14, 0.6, dark, bevel=0.0, segments=6)
            a.add("Body", tube.transformed(compose(T(sx * (2.5 + k * 0.3), TURRET_Y + 1.2 + k * 0.05, -2.6), R(60, 0, 0))))
    stowage = olive(OLIVE_DARK, decals=[{"type": "rect", "center": (0.0, 0.0), "size": (5.0, 0.04), "darken": 0.5, "raise": -0.006}])
    a.add("Body", sh.rounded_box((5.6, 1.2, 1.4), 0.06, 1, stowage).transformed(T(0, TURRET_Y + 0.75, 4.9)))

    exhaust = Material("metal", color=(36, 34, 32), rough=0.6, polish=0.2, dirt=0.8, dirt_color=(20, 18, 16))
    for x in (-2.2, 2.2):
        a.add("Body", sh.rounded_box((1.4, 0.6, 0.4), 0.04, 1, exhaust, face_mats={"+z": exhaust.but(decals=[{"type": "rect", "center": (0.0, 0.0), "size": (1.1, 0.3), "darken": 0.9, "raise": -0.02}])}).transformed(T(x, 3.6, 8.3)))
    for x in (-4.4, 4.4):
        a.add("Body", sh.rounded_box((0.6, 0.4, 0.4), 0.04, 1, dark).transformed(T(x, DECK_Y + 0.15, -7.4)))
        a.add("Lamp", sh.box((0.45, 0.28, 0.04), None).transformed(T(x, DECK_Y + 0.15, -7.62)))
    rope = Material("wrap", color=(90, 80, 60), width=0.05, slope=1.0, dirt=0.5)
    for sx in (-1, 1):
        a.add("Body", sh.sweep([(sx * 5.4, DECK_Y + 0.1, -5.0), (sx * 5.5, DECK_Y + 0.12, 0.0), (sx * 5.4, DECK_Y + 0.1, 5.5)], 0.07, 4, rope, samples=6))

    destructible(a, "Military")
    collider(a, "Hitbox", (11.6, DECK_Y, 17.6), (0, DECK_Y / 2, -0.2))
    collider(a, "Turret", (6.6, TURRET_H, 8.2), (0, TURRET_Y + TURRET_H / 2, 0.6))
    collider(a, "Barrel", (1.2, 1.2, 6.6), (0, GUN_Y, -8.4))
    return a
