from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel, louvre
from _bay_lib import STATIONS, deck, ibeam, canopy, paw_decals
from _landmark_lib import landmark, box_collider


def build():
    a = building_asset("CompanionBay", 2400, 13.0)
    a.role("Glow", "neon", color=(202, 140, 57))
    wall = panel((32, 40, 54), decals=paw_decals((0.0, 0.2), 1.0, (222, 150, 60)) + [
        {"type": "rect", "center": (0.0, 4.6), "size": (19.0, 0.12), "color": (222, 150, 60), "wear": 0.3},
    ])
    frame = steel((96, 110, 126))
    dark = steel((30, 36, 48))
    locker = panel((60, 76, 92), decals=[
        {"type": "rect", "center": (0.0, -1.6), "size": (2.2, 0.5), "color": (222, 150, 60), "wear": 0.3},
        {"type": "text", "text": "PET", "center": (0.0, -1.6), "height": 0.36, "color": (24, 26, 30), "font": "black", "wear": 0.2},
    ])
    cushion = Material("canvas", stripes=[(74, 111, 109), (66, 100, 98)], stripe_width=0.4, axis=1, dirt=0.3)
    bowl = Material("metal", color=(160, 170, 180), rough=0.25, polish=0.8, dirt=0.2)
    food = Material("plastic", color=(151, 104, 54), rough=0.85, dirt=0.2)

    a.add("Body", sh.box((20.0, 0.12, 10.0), deck(20.0, 10.0)).transformed(T(0, 0.32, 0)))
    a.add("Body", sh.rounded_box((20.0, 11.0, 0.6), 0.05, 1, wall, faces=["+z", "+x", "-x", "+y"]).transformed(T(0, 5.85, -3.5)))
    for x in (-9.3, 9.3):
        a.add("Body", ibeam(14.6, frame, 0.7, 0.7).transformed(T(x, 0.3, -3.5)))
    a.add("Body", canopy(21.0, 6.5, 0.45, panel((47, 60, 75))).transformed(T(0, 14.75, -1.1)))
    a.add("Body", sh.box((20.0, 0.65, 0.5), dark).transformed(T(0, 14.25, 2.1)))
    for x in (-9.3, 9.3):
        a.add("Body", sh.box((0.25, 0.25, 6.2), frame).transformed(compose(T(x, 12.6, -0.6), R(28, 0, 0))))
    a.add("Glow", sh.box((14.0, 0.12, 0.12), None).transformed(T(0, 13.89, 2.4)))
    for x in (-4.4, 4.4):
        a.add("Body", sh.rounded_box((3.4, 5.5, 1.3), 0.06, 1, locker, faces=["+z", "+x", "-x", "+y"]).transformed(T(x, 3.65, -2.55)))
        a.add("Body", [p.transformed(T(x, 5.15, -1.85)) for p in louvre(2.0, 0.8, 3, dark, frame)])
        a.add("Body", sh.box((0.14, 0.7, 0.18), dark).transformed(T(x + (0.9 if x > 0 else -0.9), 3.85, -1.82)))
    for x in (-7.91, 7.91):
        a.add("Body", sh.rounded_box((3.0, 0.5, 4.7), 0.06, 1, frame).transformed(T(x, 2.25, -0.9)))
        a.add("Body", sh.rounded_box((2.7, 0.35, 4.3), 0.12, 1, cushion, faces=["+y", "+x", "-x", "+z", "-z"]).transformed(T(x, 2.65, -0.9)))
        for z in (-2.5, 0.7):
            a.add("Body", sh.box((2.4, 1.8, 0.3), dark).transformed(T(x, 1.15, z)))
    for x in (-3.0, 3.0):
        a.add("Body", sh.lathe([(0.0, 0.0), (0.7, 0.0), (0.82, 0.45), (0.62, 0.45), (0.5, 0.12), (0.0, 0.12)], 12, bowl, smooth_angle=40).transformed(T(x, 0.38, 2.9)))
        a.add("Body", sh.lathe([(0.0, 0.0), (0.56, 0.0), (0.4, 0.18), (0.0, 0.22)], 10, food, smooth_angle=50).transformed(T(x, 0.5, 2.9)))
    landmark(a, STATIONS, "CompanionBay", fit="box", keep=["SignPanel"], tint={"Glow": "WarmAccent"},
             colliders=[box_collider("Wall", (20.0, 11.0, 0.6), (0, 5.85, -3.5)), box_collider("BenchL", (3.0, 2.8, 4.7), (-7.91, 1.4, -0.9)), box_collider("BenchR", (3.0, 2.8, 4.7), (7.91, 1.4, -0.9)),
                        box_collider("LockerL", (3.4, 5.5, 1.3), (-4.4, 3.65, -2.55)), box_collider("LockerR", (3.4, 5.5, 1.3), (4.4, 3.65, -2.55))])
    return a
