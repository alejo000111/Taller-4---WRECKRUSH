import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _landmark_lib import landmark, box_collider
from _station_lib import steel, painted, YELLOW, INK

MAST = 3.6
JIB_Y = 64.6
JIB_END = 62.0
COUNTER = -18.0
APEX = 75.0
TROLLEY_X = 52.0
HOOK_Y = 36.0


def lattice(length, width, mat, chord=0.22, brace=0.12, panels=None):
    h = width / 2
    parts = []
    corners = [(-h, -h), (h, -h), (h, h), (-h, h)]
    for cx, cz in corners:
        parts.append(sh.box((chord * 2, length, chord * 2), mat).transformed(T(cx, length / 2, cz)))
    count = panels or max(2, int(length / width))
    step = length / count
    for k in range(count):
        y0, y1 = k * step, (k + 1) * step
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            p0 = (a[0], y0, a[1]) if k % 2 == 0 else (b[0], y0, b[1])
            p1 = (b[0], y1, b[1]) if k % 2 == 0 else (a[0], y1, a[1])
            parts.append(sh.sweep([p0, p1], brace, 3, mat))
    return parts


def build():
    a = Asset("TowerCrane", budget=5000, atlas=1024, ao_radius=1.2, edge_width=0.08, preview_radius=44.0,
              views=[("FRONT 3/4", 215, 10), ("BACK 3/4", 35, 14), ("SIDE", 180, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 60, 40))
    a.role("Cab", "neon", color=(255, 214, 140))

    yellow = painted(YELLOW, [{"type": "rect", "center": (0.0, 0.0), "size": (0.3, 200.0), "darken": 0.15, "raise": 0.0}])
    concrete = Material("concrete", color=(140, 138, 132), dirt=0.6, decals=[
        {"type": "stripes", "center": (0.0, -0.4), "size": (9.0, 0.6), "width": 0.5, "color": YELLOW, "wear": 0.5},
    ])
    a.add("Body", sh.rounded_box((9.0, 2.0, 9.0), 0.08, 1, concrete, face_mats={"-z": concrete, "+z": concrete, "+x": concrete, "-x": concrete}).transformed(T(0, 1.0, 0)))
    for x in (-3.2, 3.2):
        for z in (-3.2, 3.2):
            a.add("Body", sh.box((1.2, 0.6, 1.2), steel((60, 62, 70))).transformed(T(x, 2.3, z)))
    a.add("Body", [p.transformed(T(0, 2.0, 0)) for p in lattice(JIB_Y - 3.5, MAST, yellow, panels=18)])
    a.add("Body", sh.rounded_box((5.2, 1.2, 5.2), 0.06, 1, steel((50, 52, 60))).transformed(T(0, JIB_Y - 1.6, 0)))

    jib = [p.transformed(compose(T(0, JIB_Y, 0), R(0, 0, -90))) for p in lattice(JIB_END, 2.4, yellow, chord=0.16, brace=0.09, panels=22)]
    a.add("Body", jib)
    counter = [p.transformed(compose(T(0, JIB_Y, 0), R(0, 0, 90))) for p in lattice(-COUNTER, 2.6, yellow, chord=0.18, brace=0.1, panels=6)]
    a.add("Body", counter)
    weight = Material("concrete", color=(110, 110, 112), dirt=0.5, decals=[{"type": "text", "text": "20T", "center": (0.0, 0.0), "height": 1.4, "color": (40, 40, 44), "font": "impact", "wear": 0.4}])
    a.add("Body", sh.rounded_box((5.0, 4.0, 4.0), 0.1, 1, weight).transformed(T(COUNTER + 2.8, JIB_Y - 1.0, 0)))
    apex = sh.lathe([(0.0, 0.0), (1.4, 0.0), (0.3, APEX - JIB_Y), (0.0, APEX - JIB_Y + 0.2)], 4, yellow, smooth_angle=10, start=45)
    a.add("Body", apex.transformed(T(0, JIB_Y + 1.2, 0)))
    wire = steel((70, 72, 78))
    for end in (JIB_END * 0.75, COUNTER + 1.0):
        a.add("Body", sh.sweep([(0.0, APEX, 0.0), (end, JIB_Y + 1.2, 0.0)], 0.07, 3, wire))
    a.add("Glow", sh.sphere(0.7, None, 8, 5).transformed(T(0, APEX + 0.6, 0)))
    a.add("Glow", sh.sphere(0.45, None, 8, 4).transformed(T(JIB_END - 0.5, JIB_Y + 1.4, 0)))

    cab_mat = painted((40, 42, 50), [{"type": "text", "text": "WRECK CRANES", "center": (0.0, 1.2), "height": 0.45, "color": YELLOW, "font": "impact", "wear": 0.3}])
    a.add("Body", sh.rounded_box((4.6, 4.2, 4.4), 0.2, 1, cab_mat).transformed(T(2.8, JIB_Y - 3.6, 2.8)))
    a.add("Cab", sh.box((3.6, 1.8, 0.06), None).transformed(T(2.8, JIB_Y - 3.0, 0.57)))
    a.add("Cab", sh.box((0.06, 1.8, 3.4), None).transformed(T(5.12, JIB_Y - 3.0, 2.8)))

    a.add("Body", sh.rounded_box((3.0, 1.4, 3.0), 0.1, 1, steel((50, 52, 60))).transformed(T(TROLLEY_X, JIB_Y - 1.9, 0)))
    for dx in (-0.6, 0.6):
        a.add("Body", sh.cylinder(0.08, JIB_Y - 2.6 - HOOK_Y, wire, bevel=0.0, segments=4).transformed(T(TROLLEY_X + dx, (JIB_Y - 2.6 + HOOK_Y) / 2, 0)))
    magnet = painted((200, 40, 36), [{"type": "stripes", "center": (np.pi * 2.6, 0.4), "size": (2 * np.pi * 2.6 + 0.4, 0.5), "width": 0.4, "color": YELLOW, "wear": 0.3}])
    a.add("Body", sh.lathe([(0.0, 0.0), (2.6, 0.0), (2.7, 0.6), (2.2, 1.2), (0.6, 1.4), (0.0, 1.5)], 14, magnet, smooth_angle=35, r_ref=2.6).transformed(T(TROLLEY_X, HOOK_Y - 1.0, 0)))
    car_side = [(-5.4, 0.0), (5.4, 0.0), (5.6, 0.7), (4.8, 1.3), (2.2, 1.45), (1.0, 2.5), (-2.0, 2.5), (-3.0, 1.5), (-5.2, 1.3), (-5.6, 0.7)]
    car = Material("paint", color=(176, 40, 32), under=(150, 62, 24), wear=0.6, scratches=0.5, rough=0.5, dirt=0.5, skin=False)
    body = sh.extrude(np.asarray(car_side), 5.6, car, bevel=0.12, corner_radius=0.0).transformed(R(0, -90, 0))
    a.add("Body", body.transformed(compose(T(TROLLEY_X + 0.5, HOOK_Y - 4.2, 0.0), R(4, 80, -3))))
    rubber = Material("rubber", color=(26, 26, 28), pattern="ribs", freq=10.0)
    for wx, wz in ((-3.6, -2.5), (3.6, -2.5), (-3.6, 2.5), (3.6, 2.5)):
        t = sh.cylinder(1.1, 0.8, rubber, bevel=0.1, segments=10).transformed(compose(T(wz, 0.1, wx), R(0, 0, 90)))
        a.add("Body", t.transformed(compose(T(TROLLEY_X + 0.5, HOOK_Y - 4.2, 0.0), R(4, 80, -3))))

    landmark(a, "Zones/ScrapYard/Landmarks", "Crane", fit="none", colliders=[
        box_collider("Mast", (4.0, JIB_Y, 4.0), (0, JIB_Y / 2, 0)),
        box_collider("Base", (9.0, 2.0, 9.0), (0, 1.0, 0)),
        box_collider("Car", (11.0, 3.0, 6.0), (TROLLEY_X + 0.5, HOOK_Y - 3.0, 0)),
    ])
    return a
