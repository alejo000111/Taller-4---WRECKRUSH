import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel
from _bay_lib import STATIONS
from _landmark_lib import landmark, box_collider

CY, RING = 9.1, 7.55


def build():
    a = building_asset("RebirthCoreArray", 2000, 12.0)
    a.role("Glow", "neon", color=(130, 80, 166))
    segment = Material("metal", color=(70, 60, 92), rough=0.32, polish=0.6, dirt=0.25, scratches=0.3, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (0.5, 2.6), "color": (40, 34, 56), "wear": 0.1},
    ])
    frame = steel((96, 110, 126))
    dark = steel((28, 32, 44))
    plinth = Material("concrete", color=(40, 46, 60), dirt=0.4)
    for k in range(16):
        ang = np.radians(-90 + 11.25 + 22.5 * k)
        pos = (np.cos(ang) * RING, CY + np.sin(ang) * RING, -2.0)
        piece = sh.rounded_box((0.8, 1.6, 3.1), 0.0, 1, segment, faces=["+x", "-x", "+y", "-y", "+z", "-z"])
        a.add("Body", piece.transformed(compose(T(*pos), R(0, 0, np.degrees(ang)))))
        if k % 4 == 0:
            a.add("Glow", sh.box((0.12, 1.2, 0.12), None).transformed(compose(T(pos[0], pos[1], -0.42), R(0, 0, np.degrees(ang)))))
    a.add("Body", sh.torus(RING - 0.7, 0.14, dark, segments=24, sides=4).transformed(compose(T(0, CY, -2.0), R(90, 0, 0))))
    a.add("Glow", sh.torus(RING + 0.55, 0.06, None, segments=24, sides=3).transformed(compose(T(0, CY, -0.5), R(90, 0, 0))))
    a.add("Body", sh.rounded_box((18.0, 0.35, 6.0), 0.05, 1, plinth, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 0.175, -2.0)))
    for x in (-7.0, 7.0):
        a.add("Body", sh.rounded_box((3.0, 0.7, 4.0), 0.08, 1, dark).transformed(T(x, 0.6, -2.0)))
        a.add("Body", sh.rounded_box((1.6, 7.0, 2.6), 0.1, 1, panel((40, 48, 64)), faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(x, 3.89, -1.2)))
        a.add("Body", sh.rounded_box((2.0, 0.4, 3.0), 0.06, 1, frame).transformed(T(x, 7.6, -1.2)))
        a.add("Glow", sh.box((0.18, 3.0, 0.12), None).transformed(T(x, 4.3, 0.12)))
        cx = 4.7 if x > 0 else -4.7
        a.add("Body", sh.cylinder(0.18, 7.0, dark, bevel=0.0, segments=6).transformed(compose(T(cx, 0.5, 1.5), R(90, 0, 0))))
        a.add("Body", sh.rounded_box((0.8, 0.6, 1.3), 0.06, 1, frame).transformed(T(cx, 0.6, 4.35)))
    a.add("Body", sh.box((7.4, 2.2, 0.2), dark).transformed(T(0, 2.8, -0.6)))
    landmark(a, STATIONS, "RebirthCoreArray", fit="box", keep=["SignPanel"], tint={"Glow": "SegmentAccent"},
             colliders=[box_collider("Plinth", (18.0, 1.0, 6.0), (0, 0.5, -2.0)), box_collider("PostL", (1.6, 7.0, 2.6), (-7.0, 3.89, -1.2)), box_collider("PostR", (1.6, 7.0, 2.6), (7.0, 3.89, -1.2))])
    return a
