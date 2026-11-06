import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from RustyCar import TIRE, HUBCAP, BEZEL, arc_from_end, side_extrude, top_extrude, plate_box, side_sheet

WHITE = (234, 236, 240)
CYAN = (34, 225, 255)
NAVY = (24, 40, 70)
INK = (22, 24, 30)
ORANGE = (255, 122, 26)
GLASS = (36, 52, 70)

HALF_W = 3.6
BOX_HALF_W = 3.72
AXLE_Y = 1.3
FRONT_AXLE = -5.2
REAR_AXLE = 5.0
ARCH_R = 1.52
DECK_Y = 2.15
BOX_TOP = 8.45
BOX_Z0 = -2.9
BOX_Z1 = 7.75
CAB_ROOF = 7.25
WHEEL_SCALE = 1.12


def arc(cz, radius, start_y, end_y, count):
    a0 = np.pi - np.arcsin((start_y - AXLE_Y) / radius)
    a1 = np.arcsin((end_y - AXLE_Y) / radius)
    return [(cz + radius * np.cos(t), AXLE_Y + radius * np.sin(t)) for t in np.linspace(a0, a1, count)]


def outline():
    pts = [(-7.8, 0.95, 0.1)]
    pts += [(z, y, 0.0) for z, y in arc(FRONT_AXLE, ARCH_R, 0.95, 0.95, 9)]
    pts += [(z, y, 0.0) for z, y in arc(REAR_AXLE, ARCH_R, 0.95, 0.95, 9)]
    pts += [(7.7, 0.95, 0.08), (7.72, DECK_Y, 0.0), (BOX_Z0 + 0.05, DECK_Y, 0.0), (BOX_Z0 + 0.05, CAB_ROOF, 0.2),
            (-4.95, CAB_ROOF - 0.05, 0.3), (-6.4, 4.3, 0.25), (-7.78, 4.05, 0.2), (-7.88, 3.5, 0.1)]
    pts = np.asarray(pts)
    return sh.round_polyline(pts[:, :2], pts[:, 2], 1, closed=True)


def windshield_point(t):
    a, b = np.array([-6.32, 4.42]), np.array([-5.02, 7.02])
    return a + (b - a) * t


def cab_side_decals(sign):
    def at(z, y):
        return (z if sign < 0 else -z, -y)

    return [
        {"type": "rect", "center": at(-4.1, 3.0), "size": (2.5, 3.3), "outline": 0.03, "darken": 0.55, "raise": -0.007},
        {"type": "rect", "center": at(-3.2, 4.1), "size": (0.4, 0.09), "radius": 0.03, "color": (60, 62, 70), "wear": 0.2, "raise": 0.004},
        {"type": "rect", "center": at(-4.6, 2.2), "size": (9.0, 0.34), "color": CYAN, "wear": 0.15},
        {"type": "circle", "center": at(-4.2, 3.2), "radius": 0.5, "color": NAVY, "wear": 0.15},
        {"type": "text", "text": "CW", "center": at(-4.2, 3.2), "height": 0.42, "color": WHITE, "font": "impact", "wear": 0.15},
        {"type": "text", "text": "UNIT 12", "center": at(-6.6, 3.0), "height": 0.22, "color": NAVY, "font": "black", "wear": 0.2},
    ]


def box_side_decals(sign):
    zc = (BOX_Z0 + BOX_Z1) / 2
    yc = (BOX_TOP + DECK_Y) / 2

    def at(z, y):
        return ((z - zc) if sign < 0 else -(z - zc), -(y - yc))

    return [
        {"type": "rect", "center": at(2.4, 3.15), "size": (10.7, 0.75), "color": CYAN, "wear": 0.15},
        {"type": "rect", "center": at(2.4, 2.65), "size": (10.7, 0.12), "color": NAVY, "wear": 0.15},
        {"type": "text", "text": "CITY WORKS", "center": at(3.3, 5.55), "height": 1.15, "color": NAVY, "font": "impact", "wear": 0.15},
        {"type": "text", "text": "DEPT. OF DEMOLITION", "center": at(3.3, 4.65), "height": 0.34, "color": INK, "font": "black", "wear": 0.15},
        {"type": "circle", "center": at(-1.35, 5.3), "radius": 0.85, "color": CYAN, "outline": 0.14, "wear": 0.15},
        {"type": "text", "text": "W", "center": at(-1.35, 5.3), "height": 0.9, "color": NAVY, "font": "impact", "wear": 0.15},
        {"type": "text", "text": "CALL 555-WRECK", "center": at(3.3, 3.95), "height": 0.26, "color": NAVY, "font": "bold", "wear": 0.15},
        *[{"type": "rect", "center": at(z, 5.3), "size": (0.03, 6.1), "darken": 0.25, "raise": -0.003} for z in np.linspace(-2.0, 6.8, 7)],
        {"type": "rivets", "points": [at(z, y) for z in np.linspace(-2.6, 7.4, 12) for y in (2.4, 8.2)], "radius": 0.035, "height": 0.008},
    ]


def rear_decals():
    return [
        {"type": "rect", "center": (0.0, 0.2), "size": (0.04, 6.0), "darken": 0.7, "raise": -0.008},
        {"type": "rect", "center": (-1.75, 0.2), "size": (3.4, 5.9), "outline": 0.03, "darken": 0.4, "raise": -0.006},
        {"type": "rect", "center": (1.75, 0.2), "size": (3.4, 5.9), "outline": 0.03, "darken": 0.4, "raise": -0.006},
        *[{"type": "rect", "center": (x, 0.4), "size": (0.12, 5.4), "radius": 0.05, "color": (150, 154, 162), "metal": 1.0, "rough": 0.35, "wear": 0.3, "raise": 0.006} for x in (-0.55, 0.55)],
        *[{"type": "rect", "center": (x, 0.9), "size": (0.5, 0.12), "radius": 0.05, "color": (60, 62, 70), "wear": 0.2, "raise": 0.004} for x in (-0.55, 0.55)],
        {"type": "stripes", "center": (0.0, 2.55), "size": (7.2, 0.7), "width": 0.32, "color": ORANGE, "wear": 0.3},
        {"type": "text", "text": "CITY WORKS", "center": (0.0, -1.6), "height": 0.6, "color": NAVY, "font": "impact", "wear": 0.15},
        {"type": "text", "text": "KEEP BACK 50 FT", "center": (0.0, -0.85), "height": 0.24, "color": INK, "font": "black", "wear": 0.15},
    ]


def fascia_decals():
    return [
        {"type": "rect", "center": (0.0, 0.05), "size": (3.6, 0.95), "radius": 0.1, "color": (20, 20, 24), "wear": 0.1, "raise": -0.02},
        *[{"type": "rect", "center": (0.0, -0.3 + k * 0.175), "size": (3.4, 0.06), "color": (180, 184, 192), "metal": 1.0, "rough": 0.3, "wear": 0.2, "raise": 0.004} for k in range(5)],
        {"type": "circle", "center": (0.0, 0.05), "radius": 0.24, "color": CYAN, "wear": 0.1},
        {"type": "text", "text": "W", "center": (0.0, 0.05), "height": 0.26, "color": NAVY, "font": "impact", "wear": 0.1},
        {"type": "rect", "center": (2.9, 0.55), "size": (0.7, 0.14), "radius": 0.04, "color": (240, 150, 40), "rough": 0.2, "wear": 0.1},
        {"type": "rect", "center": (-2.9, 0.55), "size": (0.7, 0.14), "radius": 0.04, "color": (240, 150, 40), "rough": 0.2, "wear": 0.1},
    ]


def materials():
    paint = Material("paint", color=WHITE, under=(150, 152, 158), wear=0.2, scratches=0.3, rough=0.32, dirt=0.4, dirt_color=(70, 64, 56), skin=False)
    m = {"paint": paint}
    m["cab_left"] = paint.but(decals=cab_side_decals(-1))
    m["cab_right"] = paint.but(decals=cab_side_decals(1))
    m["box"] = Material("paint", color=WHITE, under=(160, 164, 170), wear=0.15, scratches=0.35, rough=0.36, dirt=0.45, dirt_color=(70, 64, 56), skin=False)
    m["box_left"] = m["box"].but(decals=box_side_decals(-1))
    m["box_right"] = m["box"].but(decals=box_side_decals(1))
    m["box_rear"] = m["box"].but(decals=rear_decals())
    m["box_front"] = m["box"].but(decals=[{"type": "text", "text": "CITY WORKS", "center": (0.0, -2.3), "height": 0.5, "color": NAVY, "font": "impact", "wear": 0.15}])
    m["roof"] = m["box"].but(decals=[{"type": "rect", "center": (0.0, z), "size": (7.0, 0.05), "darken": 0.3, "raise": -0.004} for z in np.linspace(-4.5, 4.5, 6)])
    m["fascia"] = paint.but(decals=fascia_decals())
    m["chassis"] = Material("metal", color=(36, 38, 44), rough=0.5, polish=0.3, dirt=0.55, dirt_color=(70, 60, 48))
    m["trim"] = Material("metal", color=(44, 46, 52), rough=0.42, polish=0.5, dirt=0.35)
    m["chrome"] = Material("rustycar_chrome", color=(200, 204, 212), rust=-0.45)
    m["step"] = Material("diamondplate", color=(150, 154, 162), pitch=0.3, dirt=0.5)
    m["plate"] = Material("paint", color=(240, 236, 220), under=(150, 152, 158), wear=0.2, scratches=0.2, dirt=0.3, rough=0.5, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (1.24, 0.5), "radius": 0.05, "outline": 0.035, "color": (34, 60, 130), "wear": 0.15},
        {"type": "text", "text": "CW-1012", "center": (0.0, 0.04), "height": 0.21, "color": (30, 52, 120), "font": "black", "wear": 0.15},
    ])
    m["tire"] = Material("rustycar_tire", tread_v=(arc_from_end(TIRE, 4), arc_from_end(TIRE, 3)), ring_v=arc_from_end(TIRE, 1) + 0.06, pitch=0.34, dirt=0.3, dirt_color=(90, 84, 76))
    cap_total = arc_from_end(HUBCAP, 0)
    m["hubcap"] = Material("rustycar_chrome", color=(214, 218, 226), rust=-0.45, decals=[
        {"type": "rect", "center": (2.0, cap_total - 0.12), "size": (5.0, 0.02), "darken": 0.45, "raise": -0.004},
        {"type": "rect", "center": (2.0, cap_total - 0.4), "size": (5.0, 0.025), "darken": 0.4, "raise": -0.004},
    ])
    m["lightbar"] = Material("metal", color=(30, 32, 38), rough=0.4, polish=0.5, dirt=0.25)
    return m


def wheel(m, x, z):
    turn = R(0, 0, 90) if x > 0 else R(0, 0, -90)
    place = compose(T(x, AXLE_Y, z), turn, S(WHEEL_SCALE, WHEEL_SCALE, WHEEL_SCALE))
    tire = sh.lathe(TIRE, 16, m["tire"], smooth_angle=50)
    cap = sh.lathe(HUBCAP, 10, m["hubcap"], smooth_angle=40)
    return [tire.transformed(place), cap.transformed(place)]


def body(m):
    parts = [side_extrude(outline(), 2 * HALF_W, m["paint"], bevel=0.14, cap_mats=[m["cab_left"], m["cab_right"]])]
    box = sh.rounded_box((2 * BOX_HALF_W, BOX_TOP - DECK_Y, BOX_Z1 - BOX_Z0), 0.14, 1, m["box"], faces=["+x", "-x", "+y", "+z", "-z"],
                         face_mats={"-x": m["box_left"], "+x": m["box_right"], "+z": m["box_rear"], "-z": m["box_front"], "+y": m["roof"]})
    parts.append(box.transformed(T(0, (BOX_TOP + DECK_Y) / 2, (BOX_Z0 + BOX_Z1) / 2)))
    for sx in (-1, 1):
        face = "+x" if sx > 0 else "-x"
        parts.append(sh.rounded_box((0.12, 0.3, BOX_Z1 - BOX_Z0 + 0.1), 0.0, 1, m["trim"], faces=[face, "+y", "-y", "+z", "-z"]).transformed(T(sx * (BOX_HALF_W + 0.04), DECK_Y + 0.1, (BOX_Z0 + BOX_Z1) / 2)))
        parts.append(sh.rounded_box((0.14, 0.14, BOX_Z1 - BOX_Z0 + 0.1), 0.0, 1, m["trim"], faces=[face, "+y", "-y", "+z", "-z"]).transformed(T(sx * (BOX_HALF_W + 0.03), BOX_TOP - 0.06, (BOX_Z0 + BOX_Z1) / 2)))
        parts.append(sh.rounded_box((0.16, 0.5, 1.4), 0.0, 1, m["step"], faces=[face, "+y", "-y", "+z", "-z"]).transformed(T(sx * (HALF_W + 0.05), 1.05, -3.6)))
        arm = sh.rounded_box((0.5, 0.08, 0.08), 0.0, 1, m["trim"])
        head = sh.rounded_box((0.16, 0.85, 0.42), 0.0, 1, m["trim"])
        parts.append(arm.transformed(T(sx * (HALF_W + 0.25), 5.0, -5.6)))
        parts.append(head.transformed(T(sx * (HALF_W + 0.52), 5.0, -5.6)))
    parts.append(plate_box((6.6, 1.5, 0.08), m["paint"], "-z", m["fascia"]).transformed(T(0, 2.95, -7.86)))
    parts.append(sh.rounded_box((7.6, 0.6, 0.4), 0.08, 1, m["chassis"], faces=["+x", "-x", "+y", "-z", "+z"]).transformed(T(0, 1.25, -7.95)))
    parts.append(sh.rounded_box((7.6, 0.55, 0.4), 0.08, 1, m["chassis"], faces=["+x", "-x", "+y", "-z", "+z"]).transformed(T(0, 1.2, 7.95)))
    parts.append(plate_box((1.3, 0.52, 0.04), m["plate"], "-z").transformed(T(0, 1.25, -8.17)))
    parts.append(plate_box((1.3, 0.52, 0.04), m["plate"], "+z").transformed(T(0, 1.75, 7.78)))
    for x in (-2.9, 2.9):
        parts.append(sh.lathe(BEZEL, 10, m["chrome"], smooth_angle=40).transformed(compose(T(x, 3.65, -7.87), R(-90, 0, 0), S(1.2, 1.2, 1.2))))
    for z in (FRONT_AXLE, REAR_AXLE):
        parts.append(sh.rounded_box((5.0, 1.5, 2.9), 0.0, 1, m["chassis"], faces=["+x", "-x", "-y", "+z", "-z"]).transformed(T(0, 1.75, z)))
    base = sh.rounded_box((3.3, 0.16, 0.8), 0.0, 1, m["lightbar"], faces=["+x", "-x", "+y", "+z", "-z"])
    parts.append(base.transformed(T(0, BOX_TOP + 0.08, BOX_Z0 + 0.7)))
    for x in (-1.2, 0.0, 1.2):
        parts.append(sh.rounded_box((0.18, 0.34, 0.66), 0.0, 1, m["lightbar"], faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(x, BOX_TOP + 0.33, BOX_Z0 + 0.7)))
    for x in (-3.0, 3.0):
        parts.append(sh.rounded_box((0.7, 1.6, 0.12), 0.0, 1, m["trim"], faces=["+x", "-x", "+y", "-y", "+z"]).transformed(T(x, 3.25, BOX_Z1 + 0.07)))
    return parts


def glazing():
    top = windshield_point(1.0)
    bottom = windshield_point(0.0)
    angle = np.degrees(np.arctan2(top[0] - bottom[0], top[1] - bottom[1]))
    length = np.hypot(*(top - bottom))
    pane = sh.box((6.3, length, 0.02), None)
    center = (top + bottom) / 2
    normal = np.array([-(top[1] - bottom[1]), top[0] - bottom[0]]) / length
    out = [pane.transformed(compose(T(0, center[1] + normal[1] * 0.06, center[0] + normal[0] * 0.06), R(angle, 0, 0)))]
    side = [(windshield_point(0.15)[0] + 0.3, 4.75), (-3.3, 4.75), (-3.3, 6.85), (windshield_point(0.9)[0] + 0.35, 6.85)]
    for x in (-HALF_W - 0.02, HALF_W + 0.02):
        out.append(side_sheet(side, x))
    return out


def build():
    a = Asset("CityVan", budget=3000, atlas=1024, ao_radius=1.0, edge_width=0.08, preview_radius=9.0,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.3)
    a.role("Glow", "neon", color=ORANGE)
    a.role("Lamp", "neon", color=(255, 248, 220))
    a.role("Tail", "neon", color=(255, 48, 40))
    m = materials()
    a.add("Body", body(m))
    a.add("Glass", glazing())
    for x in (-1.75, -0.6, 0.6, 1.75):
        a.add("Glow", sh.rounded_box((0.9, 0.28, 0.58), 0.0, 1, None).transformed(T(x, BOX_TOP + 0.33, BOX_Z0 + 0.7)))
    lens = sh.lathe([(0.35, 0.07), (0.24, 0.12), (0.0, 0.14)], 10, None, smooth_angle=60)
    a.add("Lamp", [lens.transformed(compose(T(x, 3.65, -7.87), R(-90, 0, 0), S(1.2, 1.2, 1.2))) for x in (-2.9, 2.9)])
    a.add("Tail", [sh.box((0.5, 1.3, 0.05), None).transformed(T(x, 3.25, BOX_Z1 + 0.15)) for x in (-3.0, 3.0)])
    for x in (-3.05, 3.05):
        for z in (FRONT_AXLE, REAR_AXLE):
            a.add("Body", wheel(m, x, z))
    destructible(a, "Downtown")
    collider(a, "Hitbox", (7.5, BOX_TOP, BOX_Z1 - BOX_Z0), (0, BOX_TOP / 2, (BOX_Z0 + BOX_Z1) / 2))
    collider(a, "Cab", (7.2, CAB_ROOF, 4.9), (0, CAB_ROOF / 2, -5.35))
    return a
