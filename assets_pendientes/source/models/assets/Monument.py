import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _station_lib import station, collider, steel, painted, YELLOW, INK

ORANGE = (255, 122, 26)
GROUND = 0.2
SIGN_Y = 53.0
SIGN = (45.0, 25.0, 2.2)
TOWER_TOP = 38.0
LEG = 3.6


def ibeam(length, mat, width=0.9, flange=0.18, web=0.18):
    w = width / 2
    poly = [(-w, -w), (w, -w), (w, -w + flange), (web / 2, -w + flange), (web / 2, w - flange), (w, w - flange), (w, w), (-w, w), (-w, w - flange), (-web / 2, w - flange), (-web / 2, -w + flange), (-w, -w + flange)]
    return sh.extrude(poly, length, mat, bevel=0.02, corner_radius=0.0)


def strut(a, b, radius, mat, sides=6):
    return sh.sweep([tuple(a), tuple(b)], radius, sides, mat)


def frame_ring(outer, inner, depth, mat):
    ox, oy = outer[0] / 2, outer[1] / 2
    ix, iy = inner[0] / 2, inner[1] / 2
    parts = [
        sh.box((outer[0], oy - iy, depth), mat).transformed(T(0, (oy + iy) / 2, 0)),
        sh.box((outer[0], oy - iy, depth), mat).transformed(T(0, -(oy + iy) / 2, 0)),
        sh.box((ox - ix, 2 * iy, depth), mat).transformed(T((ox + ix) / 2, 0, 0)),
        sh.box((ox - ix, 2 * iy, depth), mat).transformed(T(-(ox + ix) / 2, 0, 0)),
    ]
    return parts


def crushed_car(paint):
    side = [(-3.6, 0.0), (3.6, 0.0), (3.7, 0.4), (3.3, 0.8), (1.6, 0.95), (0.9, 1.6), (-1.2, 1.7), (-2.0, 1.0), (-3.5, 0.85), (-3.7, 0.4)]
    body = sh.extrude(side, 5.4, paint, bevel=0.1, corner_radius=0.0).transformed(R(0, -90, 0))
    rng = np.random.default_rng(21)
    body.pos[:, 1] *= 0.8 + 0.2 * np.cos(body.pos[:, 2] * 1.1)
    body.pos += rng.normal(0, 0.06, body.pos.shape)
    return sh.recompute_normals(body)


def build():
    a = Asset("Monument", budget=7000, atlas=1024, ao_radius=2.0, edge_width=0.12, preview_radius=34.0,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 14), ("FRONT", 180, 4), ("TOP", 200, 45)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=ORANGE)
    a.role("Lamp", "neon", color=(255, 244, 210))
    station(a, "Monument")
    a.meta["station"]["root"] = [0.0, 0.0, 0.0, 0.0]
    a.meta["station"]["keep"] = ["WreckSign"]

    deck = Material("diamondplate", color=(64, 66, 74), pitch=0.6, dirt=0.4)
    band = Material("hazard", color=YELLOW, color2=INK, width=0.6, angle=45, wear=0.35, dirt=0.35)
    text = painted((30, 32, 38), [
        {"type": "text", "text": "WRECKRUSH", "center": (np.pi / 2 * 13.0, 0.5), "height": 0.7, "color": ORANGE, "font": "impact", "wear": 0.25},
        {"type": "text", "text": "DESTROY  GET RICH  REBIRTH", "center": (np.pi / 2 * 13.0 + 40.8, 0.5), "height": 0.45, "color": (240, 240, 240), "font": "impact", "wear": 0.25},
    ])
    a.add("Body", sh.lathe([(0.0, GROUND), (13.0, GROUND), (13.0, GROUND + 1.0), (12.6, GROUND + 1.15), (0.0, GROUND + 1.15)], 28, text, smooth_angle=35, r_ref=13.0))
    a.add("Body", sh.lathe([(11.0, GROUND + 1.15), (11.0, GROUND + 2.6), (10.6, GROUND + 2.85)], 28, band, smooth_angle=35, r_ref=11.0))
    a.add("Body", sh.lathe([(10.6, GROUND + 2.85), (0.0, GROUND + 2.85)], 28, deck, smooth_angle=35))
    a.add("Glow", sh.lathe([(12.62, GROUND + 1.16), (11.1, GROUND + 1.16)], 28, None, smooth_angle=35))

    legs = steel((40, 42, 50))
    glow_edges = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            leg = ibeam(TOWER_TOP - GROUND - 2.85, legs, width=1.0)
            a.add("Body", leg.transformed(compose(T(sx * LEG, (TOWER_TOP + GROUND + 2.85) / 2, sz * LEG), R(90, 0, 0))))
            glow_edges.append(sh.box((0.2, TOWER_TOP - GROUND - 4.0, 0.2), None).transformed(T(sx * (LEG + 0.55), (TOWER_TOP + GROUND + 2.85) / 2, sz * (LEG + 0.55))))
            a.add("Body", sh.box((1.8, 0.4, 1.8), steel((70, 72, 80))).transformed(T(sx * LEG, GROUND + 3.05, sz * LEG)))
    a.add("Glow", glow_edges)
    brace = steel((60, 62, 70))
    levels = np.linspace(GROUND + 3.0, TOWER_TOP, 6)
    corners = [(-LEG, -LEG), (LEG, -LEG), (LEG, LEG), (-LEG, LEG)]
    for k in range(len(levels) - 1):
        y0, y1 = levels[k], levels[k + 1]
        for i in range(4):
            c0, c1 = corners[i], corners[(i + 1) % 4]
            a.add("Body", strut((c0[0], y0, c0[1]), (c1[0], y1, c1[1]), 0.16, brace, 4))
            a.add("Body", strut((c1[0], y0, c1[1]), (c0[0], y1, c0[1]), 0.16, brace, 4))
            a.add("Body", strut((c0[0], y1, c0[1]), (c1[0], y1, c1[1]), 0.2, brace, 4))

    grate = Material("diamondplate", color=(80, 82, 90), pitch=0.5, dirt=0.4)
    a.add("Body", sh.rounded_box((16.0, 0.5, 8.0), 0.06, 1, grate).transformed(T(0, TOWER_TOP + 0.25, 0)))
    rail = painted(YELLOW)
    for sz in (-1, 1):
        for x in np.linspace(-7.6, 7.6, 5):
            a.add("Body", sh.box((0.16, 1.2, 0.16), rail).transformed(T(x, TOWER_TOP + 1.1, sz * 3.8)))
        a.add("Body", sh.box((15.4, 0.16, 0.16), rail).transformed(T(0, TOWER_TOP + 1.7, sz * 3.8)))
    for sx in (-1, 1):
        a.add("Body", strut((sx * LEG, TOWER_TOP - 6.0, -LEG), (sx * 7.6, TOWER_TOP, -3.6), 0.2, brace, 4))
        a.add("Body", strut((sx * LEG, TOWER_TOP - 6.0, LEG), (sx * 7.6, TOWER_TOP, 3.6), 0.2, brace, 4))

    lamp_body = steel((34, 36, 42))
    for sz in (-1, 1):
        for x in (-12.0, -4.0, 4.0, 12.0):
            arm = strut((x * 0.55, TOWER_TOP + 0.5, sz * 3.8), (x, TOWER_TOP + 2.6, sz * 6.0), 0.12, lamp_body, 4)
            a.add("Body", arm)
            head = sh.rounded_box((1.4, 0.7, 0.9), 0.08, 1, lamp_body)
            tilt = -sz * 55
            place = compose(T(x, TOWER_TOP + 2.8, sz * 6.2), R(tilt, 0, 0))
            a.add("Body", head.transformed(place))
            a.add("Lamp", sh.box((1.1, 0.06, 0.6), None).transformed(compose(place, T(0, -0.36, 0))))

    frame = steel((26, 28, 34))
    outer = (SIGN[0] + 3.0, SIGN[1] + 3.0)
    inner = (SIGN[0] - 0.2, SIGN[1] - 0.2)
    a.add("Body", [p.transformed(T(0, SIGN_Y, 0)) for p in frame_ring(outer, inner, SIGN[2] + 1.0, frame)])
    for sz in (-1, 1):
        a.add("Glow", [p.transformed(T(0, SIGN_Y, sz * (SIGN[2] / 2 + 0.55))) for p in frame_ring((outer[0] - 0.6, outer[1] - 0.6), (outer[0] - 1.4, outer[1] - 1.4), 0.12, None)])
    bolts = steel((150, 154, 162))
    for x in np.linspace(-outer[0] / 2 + 0.75, outer[0] / 2 - 0.75, 9):
        for y in (-outer[1] / 2 + 0.75, outer[1] / 2 - 0.75):
            for sz in (-1, 1):
                a.add("Body", sh.cylinder(0.22, 0.2, bolts, bevel=0.03, segments=6).transformed(compose(T(x, SIGN_Y + y, sz * (SIGN[2] / 2 + 0.6)), R(90, 0, 0))))
    a.add("Body", sh.rounded_box((10.0, 3.0, 3.0), 0.1, 1, frame).transformed(T(0, SIGN_Y - SIGN[1] / 2 - 2.2, 0)))
    for sx in (-1, 1):
        a.add("Body", strut((sx * 2.0, TOWER_TOP + 0.5, 0.0), (sx * 8.0, SIGN_Y - SIGN[1] / 2 - 1.5, 0.0), 0.35, brace, 6))

    car = Material("paint", color=(176, 40, 32), under=(150, 62, 24), wear=0.7, scratches=0.5, rough=0.5, dirt=0.5, skin=False)
    a.add("Body", crushed_car(car).transformed(compose(T(6.0, GROUND + 2.85, 4.0), R(-6, 40, 14))))
    tire = Material("rubber", color=(26, 26, 28), pattern="ribs", freq=10.0)
    for k, (x, z, rot) in enumerate(((-7.0, 5.5, 20), (-8.4, 3.0, -10), (7.0, -6.5, 70))):
        t = sh.lathe([(0.7, -0.4), (1.3, -0.4), (1.45, 0.0), (1.3, 0.4), (0.7, 0.4)], 14, tire, closed=True, smooth_angle=50)
        a.add("Body", t.transformed(compose(T(x, GROUND + 2.85 + 0.4 + (0.85 if k == 1 else 0.0), z), R(0, rot, 0))))
    flood = steel((40, 42, 48))
    for sz in (-1, 1):
        base = compose(T(0, GROUND + 2.85, sz * 9.0), R(sz * 30, 0, 0))
        a.add("Body", sh.rounded_box((2.4, 1.2, 1.6), 0.1, 1, flood).transformed(compose(base, T(0, 0.6, 0))))
        a.add("Lamp", sh.box((2.0, 0.06, 1.2), None).transformed(compose(base, T(0, 1.22, 0))))

    collider(a, "Plinth", (26.0, 2.65, 26.0), (0, GROUND + 1.42, 0), shape="Cylinder")
    collider(a, "Tower", (8.4, TOWER_TOP - GROUND - 2.85, 8.4), (0, (TOWER_TOP + GROUND + 2.85) / 2, 0))
    collider(a, "Catwalk", (16.0, 0.5, 8.0), (0, TOWER_TOP + 0.25, 0))
    collider(a, "SignFrame", (outer[0], outer[1], SIGN[2] + 1.0), (0, SIGN_Y, 0))
    return a
