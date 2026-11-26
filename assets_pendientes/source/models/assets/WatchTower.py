import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _military_lib import olive, camo_metal, OLIVE_DARK, STENCIL, YELLOW, INK

LEG = 4.5
DECK_Y = 22.0
WALL_H = 2.6
POST_TOP = 28.2
ROOF_Y = 28.4


def leg_xz(y, sx, sz):
    taper = 1.0 + 0.12 * (1 - y / DECK_Y)
    return sx * LEG * taper, sz * LEG * taper


def build():
    a = Asset("WatchTower", budget=4500, atlas=1024, ao_radius=1.2, edge_width=0.08, preview_radius=16.0,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 16), ("SIDE", 270, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 238, 180))
    a.role("Beacon", "neon", color=(255, 60, 40))

    concrete = Material("concrete", color=(128, 128, 124), dirt=0.6)
    steel = olive(OLIVE_DARK, wear=0.45, metal=0.2)
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0, z0 = leg_xz(0.0, sx, sz)
            a.add("Body", sh.rounded_box((2.0, 1.0, 2.0), 0.08, 1, concrete, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(x0, 0.5, z0)))
            x1, z1 = leg_xz(DECK_Y, sx, sz)
            a.add("Body", sh.sweep([(x0, 1.0, z0), (x1, DECK_Y, z1)], 0.42, 4, steel))
    levels = [1.0, 7.8, 14.6, DECK_Y - 0.4]
    for k in range(3):
        y0, y1 = levels[k], levels[k + 1]
        for side in range(4):
            sx0, sz0, sx1, sz1 = [(-1, -1, 1, -1), (1, -1, 1, 1), (1, 1, -1, 1), (-1, 1, -1, -1)][side]
            p0 = leg_xz(y0, sx0, sz0)
            p1 = leg_xz(y1, sx1, sz1)
            q0 = leg_xz(y0, sx1, sz1)
            q1 = leg_xz(y1, sx0, sz0)
            a.add("Body", sh.sweep([(p0[0], y0, p0[1]), (p1[0], y1, p1[1])], 0.11, 4, steel))
            a.add("Body", sh.sweep([(q0[0], y0, q0[1]), (q1[0], y1, q1[1])], 0.11, 4, steel))
            h0 = leg_xz(y1, sx0, sz0)
            h1 = leg_xz(y1, sx1, sz1)
            a.add("Body", sh.sweep([(h0[0], y1, h0[1]), (h1[0], y1, h1[1])], 0.14, 4, steel))

    deck_top = Material("diamondplate", color=(96, 104, 76), pitch=0.45, dirt=0.6)
    a.add("Body", sh.rounded_box((11.4, 0.6, 11.4), 0.05, 1, steel, faces=["+x", "-x", "-y", "+z", "-z", "+y"], face_mats={"+y": deck_top}).transformed(T(0, DECK_Y + 0.3, 0)))

    front = camo_metal(decals=[
        {"type": "rect", "center": (0.0, 0.1), "size": (3.6, 1.2), "radius": 0.08, "color": OLIVE_DARK, "wear": 0.3},
        {"type": "text", "text": "TOWER 2", "center": (0.0, 0.12), "height": 0.8, "color": STENCIL, "font": "impact", "wear": 0.4},
        {"type": "stripes", "center": (-4.0, 0.9), "size": (2.6, 0.5), "width": 0.3, "color": YELLOW, "wear": 0.4},
        {"type": "stripes", "center": (4.0, 0.9), "size": (2.6, 0.5), "width": 0.3, "color": YELLOW, "wear": 0.4},
    ])
    plain = camo_metal(decals=[{"type": "rect", "center": (x, 0.0), "size": (0.04, 2.6), "darken": 0.4, "raise": -0.006} for x in (-2.8, 0.0, 2.8)])
    wall_y = DECK_Y + 0.6 + WALL_H / 2
    for idx, (cx, cz, sx, sz, face) in enumerate([(0, -5.5, 11.4, 0.35, "-z"), (0, 5.5, 11.4, 0.35, "+z"), (-5.5, 0, 0.35, 10.7, "-x"), (5.5, 0, 0.35, 10.7, "+x")]):
        mats = {face: front if face == "-z" else plain}
        a.add("Body", sh.rounded_box((sx, WALL_H, sz), 0.04, 1, camo_metal(), face_mats=mats).transformed(T(cx, wall_y, cz)))
    for sx in (-1, 1):
        for sz in (-1, 1):
            a.add("Body", sh.box((0.4, POST_TOP - DECK_Y - 0.6, 0.4), steel).transformed(T(sx * 5.35, (POST_TOP + DECK_Y + 0.6) / 2, sz * 5.35)))

    roof = Material("corrugated", color=(74, 84, 52), pitch=0.5, axis=0, depth=0.04, wear=0.3, dirt=0.5, skin=False)
    hip = sh.lathe([(0.0, 0.0), (8.6, 0.0), (8.6, 0.3), (0.0, 2.0)], 4, roof, smooth_angle=10, start=45)
    a.add("Body", hip.transformed(T(0, ROOF_Y - 0.3, 0)))
    a.add("Body", sh.cylinder(0.18, 0.7, steel, bevel=0.0, segments=8).transformed(T(0, ROOF_Y + 2.0, 0)))
    a.add("Beacon", sh.sphere(0.4, None, 10, 5).transformed(T(0, ROOF_Y + 2.6, 0)))

    lamp = olive((50, 54, 46), metal=0.3)
    a.add("Body", sh.cylinder(0.12, 1.4, steel, bevel=0.0, segments=6).transformed(T(4.2, DECK_Y + 0.6 + WALL_H + 0.6, -5.5)))
    housing = sh.lathe([(0.0, -0.75), (0.55, -0.75), (0.7, -0.5), (0.7, 0.55), (0.6, 0.62), (0.0, 0.62)], 12, lamp, smooth_angle=40)
    head = compose(T(4.2, DECK_Y + 0.6 + WALL_H + 1.6, -5.9), R(0, 25, 0), R(-80, 0, 0))
    a.add("Body", housing.transformed(head))
    a.add("Glow", sh.lathe([(0.0, 0.62), (0.6, 0.62), (0.0, 0.7)], 12, None, smooth_angle=50).transformed(head))

    yellow = olive(YELLOW, wear=0.4)
    lz = 6.2
    for dx in (-0.5, 0.5):
        a.add("Body", sh.box((0.1, DECK_Y + 1.5, 0.1), yellow).transformed(T(dx, (DECK_Y + 1.5) / 2, lz)))
    for y in np.arange(1.0, DECK_Y + 0.5, 1.0):
        a.add("Body", sh.box((1.0, 0.07, 0.07), yellow).transformed(T(0, y, lz)))
    for y in np.arange(8.0, DECK_Y, 3.0):
        hoop = sh.lathe([(0.68, -0.04), (0.74, -0.04), (0.74, 0.04), (0.68, 0.04)], 8, yellow, closed=True, arc=200, start=-190, smooth_angle=50)
        a.add("Body", hoop.transformed(T(0, y, lz - 0.05)))

    sign = olive((240, 236, 220), under=(150, 150, 140), wear=0.3, decals=[
        {"type": "rect", "center": (0.0, -0.45), "size": (2.0, 0.4), "color": (200, 44, 36), "wear": 0.3},
        {"type": "text", "text": "DANGER", "center": (0.0, -0.45), "height": 0.3, "color": (240, 236, 220), "font": "impact", "wear": 0.3},
        {"type": "text", "text": "RESTRICTED", "center": (0.0, 0.05), "height": 0.26, "color": INK, "font": "impact", "wear": 0.3},
        {"type": "text", "text": "AREA", "center": (0.0, 0.38), "height": 0.26, "color": INK, "font": "impact", "wear": 0.3},
    ])
    a.add("Body", sh.rounded_box((2.2, 1.3, 0.06), 0.0, 1, sign, faces=["-z", "+x", "-x", "+y", "-y", "+z"]).transformed(compose(T(-2.4, 4.0, -LEG * 1.1), R(0, 0, 2))))

    destructible(a, "Military")
    collider(a, "Hitbox", (11.4, WALL_H + 0.6, 11.4), (0, DECK_Y + (WALL_H + 0.6) / 2, 0))
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0, z0 = leg_xz(DECK_Y / 2, sx, sz)
            collider(a, f"Leg{'L' if sx < 0 else 'R'}{'F' if sz < 0 else 'B'}", (1.2, DECK_Y, 1.2), (x0, DECK_Y / 2, z0))
    collider(a, "Roof", (11.0, 1.0, 11.0), (0, ROOF_Y + 0.2, 0))
    return a
