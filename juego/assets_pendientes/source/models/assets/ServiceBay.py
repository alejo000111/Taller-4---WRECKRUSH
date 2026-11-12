from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel, trim_paint
from _bay_lib import DESIGN, deck, ibeam
from _landmark_lib import landmark, box_collider


def build():
    a = building_asset("ServiceBay", 2000, 15.0)
    a.role("Trim", "surface", skin="Trim", color=(202, 140, 57))
    a.role("Glow", "neon", color=(202, 140, 57))
    frame = steel((103, 119, 135))
    beam = steel((47, 60, 75))
    dark = steel((25, 32, 44))
    trim = trim_paint()
    slat = Material("metal", color=(40, 48, 60), rough=0.4, polish=0.4, dirt=0.45, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (18.6, 0.1), "color": (20, 24, 30), "wear": 0.1},
    ])

    a.add("Body", sh.box((18.0, 0.08, 10.0), deck(18.0, 10.0)).transformed(T(0, 0.44, -4.32)))
    for x in (-9.5, 9.5):
        a.add("Body", ibeam(18.0, frame, 0.65, 0.65).transformed(T(x, 0.6, 9.68)))
        a.add("Body", sh.rounded_box((1.3, 0.65, 1.3), 0.06, 1, beam).transformed(T(x, 0.32, 9.68)))
        a.add("Trim", sh.box((0.72, 0.55, 0.72), trim).transformed(T(x, 3.5, 9.68)))
        a.add("Trim", sh.box((0.72, 0.55, 0.72), trim).transformed(T(x, 15.0, 9.68)))
        a.add("Body", sh.box((0.8, 0.6, 20.0), beam).transformed(T(x, 18.3, -0.32)))
        a.add("Body", sh.box((0.25, 0.25, 5.5), frame).transformed(compose(T(x, 16.4, 7.8), R(-42, 0, 0))))
        cx = 8.1 if x > 0 else -8.1
        a.add("Body", sh.cylinder(0.22, 7.0, dark, bevel=0.0, segments=6).transformed(T(cx, 8.0, -6.12)))
        a.add("Body", sh.box((0.6, 0.6, 0.6), frame).transformed(T(cx, 11.6, -6.12)))
        a.add("Trim", sh.box((1.6, 0.04, 2.3), trim).transformed(T(cx, 0.5, -0.32)))
    for z in (-5.32, -0.32, 4.68):
        a.add("Body", sh.rounded_box((19.0, 0.25, 2.4), 0.03, 1, slat, faces=["+y", "-y", "+z", "-z"]).transformed(compose(T(0, 18.4, z), R(-8, 0, 0))))
    a.add("Body", sh.rounded_box((20.0, 0.6, 0.7), 0.05, 1, beam).transformed(T(0, 18.3, 9.68)))
    a.add("Glow", sh.box((16.0, 0.12, 0.16), None).transformed(T(0, 17.95, 10.1)))
    landmark(a, DESIGN, ["UpgradeBay", "ToolsBay"], fit="box", tint={"Trim": "PaintedSupportBand", "Glow": "FrontLightStrip"},
             colliders=[box_collider("PostL", (0.7, 18.5, 0.7), (-9.5, 9.25, 9.68)), box_collider("PostR", (0.7, 18.5, 0.7), (9.5, 9.25, 9.68)), box_collider("Roof", (20.0, 0.8, 20.0), (0, 18.3, -0.32))])
    return a
