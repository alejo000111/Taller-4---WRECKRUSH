from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel, louvre, IMMERSION
from _landmark_lib import landmark, box_collider


def build():
    a = building_asset("ServiceWorkshop", 1500, 13.0)
    a.role("Glow", "neon", color=(202, 140, 57))
    clad = Material("corrugated", color=(150, 164, 178), under=(110, 112, 118), pitch=0.5, axis=0, depth=0.04, wear=0.35, scratches=0.4, rough=0.45, dirt=0.45, skin=False)
    frame = steel((86, 100, 116))
    dark = steel((34, 40, 52))
    concrete = Material("concrete", color=(76, 84, 96), dirt=0.55)
    hazard = Material("hazard", color=(255, 196, 30), color2=(24, 24, 28), width=0.35, angle=45, wear=0.4, dirt=0.4)
    box = panel((52, 64, 80), decals=[
        {"type": "rect", "center": (0.0, -0.7), "size": (1.1, 0.5), "color": (255, 200, 40), "wear": 0.3},
        {"type": "text", "text": "⚡", "center": (0.0, -0.7), "height": 0.4, "color": (20, 20, 24), "font": "bold", "wear": 0.2},
    ])
    rust = Material("paint", color=(139, 80, 48), under=(90, 60, 40), wear=0.5, scratches=0.4, rough=0.6, dirt=0.5, skin=False)

    a.add("Body", sh.rounded_box((19.0, 0.7, 4.0), 0.06, 1, concrete, faces=["+x", "-x", "+z", "-z", "+y"]).transformed(T(0, 0.35, -1.0)))
    a.add("Body", sh.box((18.0, 0.25, 0.6), hazard).transformed(T(0, 0.82, 0.7)))
    a.add("Body", sh.rounded_box((18.0, 14.0, 1.5), 0.0, 1, clad, faces=["+z", "+x", "-x", "+y"]).transformed(T(0, 7.0, -1.0)))
    a.add("Body", sh.box((18.2, 0.5, 1.7), frame).transformed(T(0, 1.2, -1.0)))
    a.add("Body", sh.box((15.8, 3.9, 0.1), dark).transformed(T(0, 11.0, -0.22)))
    a.add("Body", sh.box((11.0, 4.0, 0.2), dark).transformed(T(0, 5.0, -0.18)))
    a.add("Body", [p.transformed(T(0, 5.0, 0.0)) for p in louvre(10.6, 3.6, 5, frame, frame)])
    for x in (-8.7, 8.7):
        web = sh.extrude([(-0.3, -0.95), (0.3, -0.95), (0.3, -0.8), (0.05, -0.8), (0.05, 0.8), (0.3, 0.8), (0.3, 0.95), (-0.3, 0.95), (-0.3, 0.8), (-0.05, 0.8), (-0.05, -0.8), (-0.3, -0.8)], 15.0, frame, bevel=0.0, corner_radius=0.0)
        a.add("Body", web.transformed(compose(T(x, 7.5, -0.9), R(-90, 0, 0))))
        a.add("Body", sh.box((1.0, 0.3, 2.4), dark).transformed(T(x, 0.85, -0.9)))
        brace = sh.box((0.25, 0.25, 4.6), frame)
        a.add("Body", brace.transformed(compose(T(x, 12.6, 1.1), R(38, 0, 0))))
    canopy = sh.extrude([(-2.5, -0.35), (2.5, -0.05), (2.5, 0.25), (-2.5, 0.35)], 20.0, panel((47, 60, 75)), bevel=0.0, corner_radius=0.0)
    a.add("Body", canopy.transformed(compose(T(0, 14.8, 0.5), R(0, 90, 0))))
    a.add("Glow", sh.box((18.0, 0.15, 0.2), None).transformed(T(0, 14.55, 2.95)))
    a.add("Body", sh.rounded_box((2.0, 2.8, 0.7), 0.06, 1, box, faces=["+z", "+x", "-x", "+y", "-y"]).transformed(T(6.5, 4.1, 0.1)))
    a.add("Body", sh.cylinder(0.16, 9.0, rust, bevel=0.0, segments=6).transformed(T(-7.2, 5.0, -0.05)))
    for y in (1.5, 8.5):
        a.add("Body", sh.box((0.6, 0.15, 0.4), dark).transformed(T(-7.2, y, -0.1)))
    landmark(a, IMMERSION, ["ToolsWorkshop", "UpgradeWorkshop", "QuestOffice", "ChaosExchange"], fit="box", keep=["SignPanel"], tint={"Glow": "CanopyTrim"},
             colliders=[box_collider("Wall", (18.0, 14.0, 1.5), (0, 7.0, -1.0)), box_collider("Footing", (19.0, 0.7, 4.0), (0, 0.35, -1.0))])
    return a
