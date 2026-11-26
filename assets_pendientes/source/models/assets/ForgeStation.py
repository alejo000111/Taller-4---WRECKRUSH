from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import steel


def build():
    a = Asset("ForgeStation", budget=4000, atlas=1024, ao_radius=0.6, ao_strength=0.6, edge_width=0.06, gradient=0.1, highlight=0.5, preview_radius=11.0,
              views=[("FRONT 3/4", 215, 14), ("FRONT", 180, 6), ("SIDE", 270, 8), ("BACK 3/4", 35, 18)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 120, 30))
    dark = steel((44, 46, 52))
    iron = Material("metal", color=(70, 70, 74), rough=0.45, polish=0.4, dirt=0.6, scratches=0.5, hammered=0.6)
    brick = Material("concrete", color=(120, 70, 56), dirt=0.7)
    hazard = Material("hazard", color=(255, 196, 40), color2=(26, 26, 30), width=0.22, angle=45)
    plate = Material("diamondplate", color=(110, 112, 118), dirt=0.6)
    wood = Material("wood", color=(110, 76, 46), dirt=0.5)
    a.add("Body", sh.rounded_box((13.0, 0.6, 11.0), 0.2, 1, plate).transformed(T(0, 0.3, 0)))
    a.add("Body", sh.box((13.2, 0.3, 0.8), hazard).transformed(T(0, 0.65, -5.2)))
    a.add("Body", sh.rounded_box((6.0, 7.0, 5.0), 0.5, 1, brick).transformed(T(3.0, 4.1, 2.4)))
    a.add("Body", sh.rounded_box((4.2, 2.6, 0.4), 0.2, 1, dark).transformed(T(3.0, 3.4, -0.15)))
    a.add("Glow", sh.box((3.4, 1.8, 0.2), None).transformed(T(3.0, 3.4, -0.3)))
    a.add("Body", sh.cylinder(1.1, 6.0, iron, bevel=0.08, segments=10).transformed(T(4.4, 10.6, 3.4)))
    a.add("Body", sh.cylinder(1.4, 0.6, dark, segments=10).transformed(T(4.4, 13.7, 3.4)))
    a.add("Body", sh.rounded_box((1.6, 2.0, 2.6), 0.2, 1, dark).transformed(T(-3.2, 1.6, -0.4)))
    anvil = [sh.rounded_box((4.2, 1.0, 2.2), 0.25, 1, iron).transformed(T(-3.2, 3.0, -0.4)),
             sh.rounded_box((2.2, 1.0, 1.6), 0.25, 1, iron).transformed(T(-3.2, 2.2, -0.4))]
    for mesh in anvil:
        a.add("Body", mesh)
    a.add("Body", sh.wedge((1.6, 0.9, 2.0), iron).transformed(compose(T(-5.9, 3.0, -0.4), R(0, 90, 0))))
    a.add("Body", sh.rounded_box((0.5, 2.6, 0.5), 0.1, 1, wood).transformed(compose(T(-2.6, 4.4, -0.6), R(0, 0, 30))))
    a.add("Body", sh.rounded_box((1.4, 0.8, 0.8), 0.15, 1, iron).transformed(compose(T(-2.0, 5.4, -0.6), R(0, 0, 30))))
    a.add("Body", sh.rounded_box((5.0, 5.0, 0.4), 0.2, 1, plate).transformed(T(-3.0, 4.0, 4.6)))
    for k in range(3):
        a.add("Body", sh.box((0.25, 3.0, 0.25), dark).transformed(T(-4.6 + k * 1.6, 4.4, 4.2)))
        a.add("Body", sh.rounded_box((1.0, 0.7, 0.5), 0.1, 1, iron).transformed(T(-4.6 + k * 1.6, 5.8, 4.1)))
    a.add("Body", sh.cylinder(0.9, 1.4, dark, segments=10).transformed(T(0.2, 1.3, -3.4)))
    a.add("Glow", sh.cylinder(0.75, 0.2, None, segments=10).transformed(T(0.2, 2.0, -3.4)))
    a.meta["place"] = {"targets": [{"path": "Plaza", "center": [74.0, 0.0, 30.0], "yaw": 90.0}]}
    return a
