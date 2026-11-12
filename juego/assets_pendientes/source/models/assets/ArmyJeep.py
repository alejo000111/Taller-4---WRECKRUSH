import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _military_lib import olive, camo_metal, star, OLIVE_DARK, STENCIL
from RustyCar import TIRE, HUBCAP, arc_from_end

AXLE_Y = 1.4
FRONT_AXLE = -4.3
REAR_AXLE = 4.0
TRACK = 3.05
WHEEL_SCALE = 1.2
TUB_Y0 = 1.75
TUB_Y1 = 3.75
TUB_Z0 = -1.6
TUB_Z1 = 5.9
HALF_W = 2.4
GLASS = (90, 120, 120)


def wheel(m, x, z):
    turn = R(0, 0, 90) if x > 0 else R(0, 0, -90)
    place = compose(T(x, AXLE_Y, z), turn, S(WHEEL_SCALE, WHEEL_SCALE * 1.15, WHEEL_SCALE))
    return [sh.lathe(TIRE, 12, m["tire"], smooth_angle=50).transformed(place), sh.lathe(HUBCAP, 8, m["rim"], smooth_angle=40).transformed(place)]


def build():
    a = Asset("ArmyJeep", budget=3000, atlas=1024, ao_radius=0.9, edge_width=0.07, preview_radius=8.0,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.5)
    a.role("Lamp", "neon", color=(255, 236, 190))

    m = {
        "tire": Material("rustycar_tire", tread_v=(arc_from_end(TIRE, 4), arc_from_end(TIRE, 3)), ring_v=arc_from_end(TIRE, 1) + 0.06, pitch=0.42, dirt=0.55, dirt_color=(110, 92, 66)),
        "rim": olive(OLIVE_DARK, wear=0.4),
    }
    side = camo_metal(decals=[
        {"type": "text", "text": "ARMY 07", "center": (0.0, -0.1), "height": 0.5, "color": STENCIL, "font": "impact", "wear": 0.4},
        {"type": "text", "text": "W.R.A.", "center": (2.4, 0.15), "height": 0.3, "color": STENCIL, "font": "black", "wear": 0.4},
    ])
    camo = camo_metal()
    tub = sh.rounded_box((2 * HALF_W, TUB_Y1 - TUB_Y0, TUB_Z1 - TUB_Z0), 0.12, 1, camo, faces=["+x", "-x", "-y", "+z"], face_mats={"+x": side, "-x": side})
    a.add("Body", tub.transformed(T(0, (TUB_Y0 + TUB_Y1) / 2, (TUB_Z0 + TUB_Z1) / 2)))
    floor = olive(OLIVE_DARK)
    a.add("Body", sh.box((2 * HALF_W - 0.3, 0.1, TUB_Z1 - TUB_Z0 - 0.3), Material("diamondplate", color=(80, 84, 70), pitch=0.3, dirt=0.6)).transformed(T(0, TUB_Y0 + 0.55, (TUB_Z0 + TUB_Z1) / 2)))
    for sx in (-1, 1):
        a.add("Body", sh.box((0.12, TUB_Y1 - TUB_Y0 - 0.5, TUB_Z1 - TUB_Z0 - 0.3), floor).transformed(T(sx * (HALF_W - 0.2), TUB_Y0 + 1.05, (TUB_Z0 + TUB_Z1) / 2)))

    hood_top = camo_metal(decals=star((0.0, 0.0), 2.0, STENCIL, angle=180) + [
        {"type": "text", "text": "WR-07", "center": (0.0, 1.55), "height": 0.4, "color": STENCIL, "font": "impact", "wear": 0.4, "angle": 180},
    ])
    hood = sh.rounded_box((5.0, 1.4, 4.3), 0.15, 1, camo, faces=["+x", "-x", "+y", "-y"], face_mats={"+y": hood_top})
    a.add("Body", hood.transformed(T(0, 3.35, -3.75)))
    grille_face = olive(OLIVE_DARK, decals=[
        *[{"type": "rect", "center": (x, -0.15), "size": (0.22, 1.05), "radius": 0.08, "color": (16, 18, 14), "wear": 0.0, "raise": -0.02} for x in np.linspace(-1.2, 1.2, 7)],
        {"type": "text", "text": "07", "center": (0.0, 0.62), "height": 0.3, "color": STENCIL, "font": "impact", "wear": 0.4},
    ])
    a.add("Body", sh.rounded_box((5.0, 1.85, 0.2), 0.06, 1, camo, faces=["-z", "+x", "-x", "+y"], face_mats={"-z": grille_face}).transformed(T(0, 3.1, -5.95)))
    bezel = Material("metal", color=(60, 62, 56), rough=0.4, polish=0.5, dirt=0.4)
    for x in (-1.95, 1.95):
        a.add("Body", sh.lathe([(0.0, 0.0), (0.42, 0.0), (0.42, 0.12), (0.34, 0.16), (0.0, 0.16)], 10, bezel, smooth_angle=40).transformed(compose(T(x, 3.15, -6.05), R(-90, 0, 0))))
        a.add("Lamp", sh.lathe([(0.0, 0.0), (0.32, 0.0), (0.24, 0.08), (0.0, 0.12)], 10, None, smooth_angle=50).transformed(compose(T(x, 3.15, -6.2), R(-90, 0, 0))))
    bumper = olive(OLIVE_DARK, decals=[{"type": "text", "text": "ARMY  WR-07", "center": (0.0, 0.0), "height": 0.3, "color": STENCIL, "font": "impact", "wear": 0.4}])
    a.add("Body", sh.rounded_box((6.6, 0.55, 0.45), 0.06, 1, floor, face_mats={"-z": bumper}).transformed(T(0, 2.0, -6.35)))
    a.add("Body", sh.rounded_box((6.0, 0.5, 0.4), 0.06, 1, floor).transformed(T(0, 2.0, 6.1)))

    for sx in (-1, 1):
        fender = sh.extrude([(-2.2, 0.0), (1.5, 0.0), (2.1, -0.45), (2.1, -0.57), (1.45, -0.12), (-2.2, -0.12)], 1.4, camo, bevel=0.03, corner_radius=0.0)
        a.add("Body", fender.transformed(compose(T(sx * 3.05, 3.12, FRONT_AXLE), R(0, -90, 0))))
        a.add("Body", sh.box((1.4, 0.12, 3.2), camo).transformed(T(sx * 3.05, 3.0, REAR_AXLE)))

    frame_mat = olive(OLIVE_DARK, wear=0.45)
    ws_y = TUB_Y1 + 1.0
    for x in (-2.3, 2.3):
        a.add("Body", sh.box((0.16, 2.0, 0.16), frame_mat).transformed(compose(T(x, ws_y, TUB_Z0 + 0.05), R(-8, 0, 0))))
    a.add("Body", sh.box((4.76, 0.16, 0.16), frame_mat).transformed(compose(T(0, ws_y + 0.98, TUB_Z0 + 0.19), R(-8, 0, 0))))
    a.add("Body", sh.box((4.76, 0.16, 0.18), frame_mat).transformed(T(0, TUB_Y1 + 0.08, TUB_Z0 + 0.0)))
    a.add("Body", sh.box((0.1, 1.8, 0.12), frame_mat).transformed(compose(T(0, ws_y, TUB_Z0 + 0.05), R(-8, 0, 0))))
    for x in (-1.15, 1.15):
        a.add("Glass", sh.box((2.1, 1.75, 0.03), None).transformed(compose(T(x, ws_y, TUB_Z0 + 0.05), R(-8, 0, 0))))

    seat = Material("canvas", stripes=[(60, 66, 44)], stripe_width=1.0, axis=0, dirt=0.5)
    for x in (-1.1, 1.1):
        a.add("Body", sh.rounded_box((1.6, 0.45, 1.6), 0.0, 1, seat).transformed(T(x, TUB_Y0 + 1.0, 0.6)))
        a.add("Body", sh.rounded_box((1.6, 1.4, 0.35), 0.12, 1, seat).transformed(compose(T(x, TUB_Y0 + 1.75, 1.5), R(-10, 0, 0))))
    wheel_mat = Material("rubber", color=(26, 26, 28), pattern="ribs", freq=8.0)
    a.add("Body", sh.cylinder(0.32, 0.12, wheel_mat, bevel=0.0, segments=12).transformed(compose(T(-1.1, TUB_Y1 + 0.45, -0.7), R(-60, 0, 0))))
    a.add("Body", sh.sweep([(-1.1, TUB_Y1 - 0.4, -1.4), (-1.1, TUB_Y1 + 0.42, -0.72)], 0.05, 4, frame_mat))

    bar = [(-2.3, TUB_Y1, 3.4), (-2.3, TUB_Y1 + 2.0, 3.4), (-1.9, TUB_Y1 + 2.5, 3.4), (1.9, TUB_Y1 + 2.5, 3.4), (2.3, TUB_Y1 + 2.0, 3.4), (2.3, TUB_Y1, 3.4)]
    a.add("Body", sh.sweep(bar, 0.14, 6, frame_mat, samples=16))

    spare_place = compose(T(0, 3.3, TUB_Z1 + 0.6), R(90, 0, 0), S(WHEEL_SCALE, WHEEL_SCALE * 1.15, WHEEL_SCALE))
    a.add("Body", sh.lathe(TIRE, 14, m["tire"], smooth_angle=50).transformed(spare_place))
    a.add("Body", sh.lathe(HUBCAP, 10, m["rim"], smooth_angle=40).transformed(spare_place))
    can = olive((70, 82, 46), decals=[{"type": "rect", "center": (0.0, 0.0), "size": (0.5, 0.9), "outline": 0.05, "darken": 0.5, "raise": -0.008}])
    a.add("Body", sh.rounded_box((0.7, 1.3, 1.1), 0.08, 1, can).transformed(T(1.85, TUB_Y1 + 0.2, 5.3)))
    a.add("Body", sh.cylinder(0.12, 0.25, frame_mat, bevel=0.02, segments=6).transformed(T(2.0, TUB_Y1 + 0.95, 5.0)))
    a.add("Body", sh.cylinder(0.04, 2.4, frame_mat, bevel=0.0, segments=5).transformed(T(-2.2, TUB_Y1 + 1.5, 5.6)))

    for x in (-TRACK, TRACK):
        for z in (FRONT_AXLE, REAR_AXLE):
            a.add("Body", wheel(m, x, z))
    a.add("Body", sh.box((5.0, 0.5, 11.0), Material("metal", color=(30, 32, 28), rough=0.5, polish=0.3, dirt=0.6)).transformed(T(0, 1.55, 0)))

    destructible(a, "Military")
    collider(a, "Hitbox", (7.0, 3.0, 12.4), (0, 2.2, 0))
    collider(a, "Upper", (4.8, 2.6, 5.0), (0, TUB_Y1 + 1.3, 3.4))
    return a
