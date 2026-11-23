from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import steel


def build():
    a = Asset("RecyclerStation", budget=4000, atlas=1024, ao_radius=0.6, ao_strength=0.6, edge_width=0.06, gradient=0.1, highlight=0.5, preview_radius=11.0,
              views=[("FRONT 3/4", 215, 14), ("FRONT", 180, 6), ("SIDE", 270, 8), ("BACK 3/4", 35, 18)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(34, 225, 255))
    green = Material("paint", color=(70, 120, 90), under=(90, 90, 92), wear=0.5, scratches=0.5, rough=0.5, metal=0.3, dirt=0.6)
    dark = steel((40, 42, 46))
    iron = Material("metal", color=(84, 86, 90), rough=0.45, polish=0.35, dirt=0.6, scratches=0.5)
    rubber = Material("rubber", color=(30, 30, 32), dirt=0.4)
    hazard = Material("hazard", color=(255, 196, 40), color2=(26, 26, 30), width=0.22, angle=45)
    plate = Material("diamondplate", color=(110, 112, 118), dirt=0.6)
    rust = Material("paint", color=(150, 90, 56), under=(90, 70, 60), wear=0.6, scratches=0.5, rough=0.6, metal=0.3, dirt=0.6)
    a.add("Body", sh.rounded_box((13.0, 0.6, 11.0), 0.2, 1, plate).transformed(T(0, 0.3, 0)))
    a.add("Body", sh.box((13.2, 0.3, 0.8), hazard).transformed(T(0, 0.65, -5.2)))
    a.add("Body", sh.rounded_box((6.4, 6.0, 6.0), 0.5, 1, green).transformed(T(2.4, 3.6, 1.6)))
    hopper = sh.frustum(3.0, 4.6, 3.0, iron, bevel=0.1, segments=4).transformed(compose(T(2.4, 8.1, 1.6), R(0, 45, 0)))
    a.add("Body", hopper)
    a.add("Body", sh.box((6.6, 0.8, 6.2), hazard).transformed(T(2.4, 6.8, 1.6)))
    for k in range(4):
        a.add("Body", sh.cylinder(0.6, 4.6, dark, segments=8).transformed(compose(T(2.4, 5.4, 0.0 + k * 1.1), R(0, 0, 90))))
    a.add("Body", sh.rounded_box((7.0, 0.8, 2.6), 0.2, 1, rubber).transformed(compose(T(-3.0, 2.6, -1.6), R(0, 0, -12))))
    for x in (-6.0, 0.0):
        a.add("Body", sh.box((0.5, 2.2, 2.8), dark).transformed(T(x, 1.4, -1.6)))
    a.add("Body", sh.rounded_box((4.0, 2.4, 3.6), 0.3, 1, rust).transformed(T(-4.2, 1.8, 2.8)))
    for k in range(5):
        a.add("Body", sh.box((0.9, 0.5, 0.7), iron if k % 2 else rust).transformed(compose(T(-5.0 + k * 0.5, 3.2, 2.4 + (k % 3) * 0.6), R(k * 20, k * 37, 0))))
    a.add("Body", sh.rounded_box((3.0, 2.0, 0.5), 0.2, 1, dark).transformed(T(2.4, 4.6, -1.5)))
    a.add("Glow", sh.box((2.4, 1.4, 0.2), None).transformed(T(2.4, 4.6, -1.8)))
    a.add("Glow", sh.box((6.6, 0.25, 0.25), None).transformed(T(2.4, 6.3, -1.45)))
    a.meta["place"] = {"targets": [{"path": "Plaza", "center": [-74.0, 0.0, 32.0], "yaw": -90.0}]}
    return a
