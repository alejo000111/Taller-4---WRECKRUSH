from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel, louvre, trim_paint, IMMERSION
from _landmark_lib import landmark, box_collider


def build():
    a = building_asset("ServicePanel", 1200, 11.0)
    a.role("Trim", "surface", skin="Trim", color=(139, 80, 48))
    a.role("Glow", "neon", color=(139, 80, 48))
    housing = panel((47, 60, 75), decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (16.6, 0.06), "color": (30, 36, 46), "wear": 0.2},
        {"type": "rect", "center": (2.6, 0.0), "size": (0.06, 5.6), "color": (30, 36, 46), "wear": 0.2},
        {"type": "text", "text": "SERVICE", "center": (-6.8, 2.3), "height": 0.45, "color": (220, 224, 230), "font": "black", "wear": 0.4},
    ])
    cabinet = panel((103, 119, 135), decals=[
        {"type": "rect", "center": (-0.6, -0.6), "size": (2.0, 1.2), "color": (16, 30, 40), "rough": 0.1, "wear": 0.0},
        {"type": "rect", "center": (-0.6, -0.6), "size": (1.7, 0.08), "color": (60, 220, 160), "wear": 0.0},
        *[{"type": "rect", "center": (1.2, -1.0 + k * 0.6), "size": (0.4, 0.4), "radius": 0.18, "color": c, "wear": 0.2} for k, c in enumerate([(220, 50, 40), (250, 200, 40), (60, 200, 90)])],
        {"type": "rect", "center": (0.0, 1.1), "size": (3.2, 0.5), "color": (255, 200, 40), "wear": 0.3},
    ])
    frame = steel((90, 104, 120))
    dark = steel((25, 32, 44))
    trim = trim_paint()

    a.add("Body", sh.rounded_box((17.0, 6.0, 1.0), 0.08, 1, housing, faces=["+z", "+x", "-x", "+y", "-y"]).transformed(T(0, 5.0, -0.58)))
    a.add("Body", sh.box((6.0, 3.8, 0.2), dark).transformed(T(-4.0, 5.0, 0.0)))
    a.add("Body", [p.transformed(T(-4.0, 5.0, 0.15)) for p in louvre(5.6, 3.4, 4, frame, frame)])
    a.add("Body", sh.rounded_box((4.0, 4.0, 1.2), 0.08, 1, cabinet, faces=["+z", "+x", "-x", "+y", "-y"]).transformed(T(4.7, 4.8, 0.32)))
    a.add("Body", sh.box((4.2, 0.25, 1.4), frame).transformed(T(4.7, 6.9, 0.32)))
    a.add("Glow", sh.box((2.5, 0.22, 0.18), None).transformed(T(4.7, 5.9, 0.98)))
    for x in (-7.6, 7.6):
        a.add("Trim", sh.cylinder(0.2, 8.0, trim, bevel=0.0, segments=8).transformed(T(x, 4.0, 0.32)))
        for y in (2.2, 7.6):
            a.add("Body", sh.cylinder(0.26, 0.25, frame, bevel=0.0, segments=8).transformed(T(x, y, 0.32)))
        a.add("Trim", sh.lathe([(0.0, 0.0), (0.3, 0.0), (0.3, 0.3), (0.0, 0.3)], 8, trim, smooth_angle=40).transformed(T(x, 0.0, 0.32)))
    a.add("Trim", sh.box((17.0, 0.18, 1.05), trim).transformed(T(0, 7.9, -0.58)))
    a.add("Body", sh.box((17.4, 3.4, 0.12), dark).transformed(T(0, 10.0, -0.55)))
    for x in (-6.0, 6.0):
        a.add("Body", sh.box((0.25, 0.9, 0.5), frame).transformed(T(x, 8.3, -0.6)))
    landmark(a, IMMERSION, ["ScrapService", "IndustrialService", "DowntownService", "ChaosService", "FutureService", "MilitaryService"], fit="box", keep=["SignPanel"],
             tint={"Trim": "Pipe", "Glow": "StatusSlit"}, colliders=[box_collider("Panel", (17.0, 6.0, 1.0), (0, 5.0, -0.58))])
    return a
