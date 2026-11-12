from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel
from _bay_lib import DESIGN
from _landmark_lib import landmark, box_collider

SPIN = 60.42


def build():
    a = building_asset("DetailBench", 1400, 4.5, atlas=512)
    top = Material("wood", color=(196, 140, 86), dirt=0.45)
    frame = steel((70, 80, 95))
    bright = Material("metal", color=(160, 168, 178), rough=0.3, polish=0.7, dirt=0.3)
    drawer = panel((70, 80, 95), decals=[
        {"type": "rect", "center": (-1.6, 0.0), "size": (2.4, 0.08), "color": (40, 46, 56), "wear": 0.2},
        {"type": "rect", "center": (1.6, 0.0), "size": (2.4, 0.08), "color": (40, 46, 56), "wear": 0.2},
    ])
    handle_wood = Material("wood", color=(220, 160, 100), dirt=0.3)
    red = Material("paint", color=(200, 50, 40), under=(120, 120, 120), wear=0.4, scratches=0.4, rough=0.4, dirt=0.3, skin=False)

    parts = []
    parts.append(sh.rounded_box((7.0, 0.4, 3.0), 0.06, 1, top).transformed(T(0, 3.8, 0)))
    for sx in (-1, 1):
        for sz in (-1, 1):
            parts.append(sh.box((0.35, 3.6, 0.35), frame).transformed(T(sx * 3.2, 1.8, sz * 1.2)))
        parts.append(sh.box((0.15, 0.25, 2.1), frame).transformed(T(sx * 3.2, 0.73, 0)))
    for sz in (-1, 1):
        parts.append(sh.box((6.1, 0.25, 0.15), frame).transformed(T(0, 0.73, sz * 1.2)))
    parts.append(sh.rounded_box((6.1, 0.8, 2.7), 0.04, 1, drawer, faces=["-z", "+z", "+x", "-x", "-y"]).transformed(T(0, 3.2, 0)))
    parts.append(sh.box((1.0, 0.15, 0.2), bright).transformed(T(0, 3.2, -1.42)))
    parts.append(sh.box((6.0, 0.15, 2.4), frame).transformed(T(0, 1.0, 0)))
    parts.append(sh.box((1.2, 0.2, 1.2), frame).transformed(T(-2.4, 4.1, -0.6)))
    parts.append(sh.box((0.8, 0.6, 0.6), bright).transformed(T(-2.4, 4.5, -0.45)))
    parts.append(sh.box((0.8, 0.6, 0.5), bright).transformed(T(-2.4, 4.5, -1.15)))
    parts.append(sh.cylinder(0.1, 1.2, bright, bevel=0.0, segments=6).transformed(compose(T(-2.4, 4.4, -1.3), R(90, 0, 0))))
    parts.append(sh.cylinder(0.05, 0.8, bright, bevel=0.0, segments=5).transformed(compose(T(-2.4, 4.4, -1.85), R(0, 0, 90))))
    parts.append(sh.cylinder(0.08, 1.17, handle_wood, bevel=0.0, segments=6).transformed(compose(T(1.4, 4.08, 0.5), R(0, 90, 90))))
    parts.append(sh.box((0.3, 0.3, 0.85), red).transformed(T(0.75, 4.08, 0.5)))
    parts.append(sh.box((0.2, 0.05, 1.26), bright).transformed(compose(T(2.4, 4.03, -0.3), R(0, 70, 0))))
    for dz, r in ((-0.6, 0.2), (0.6, 0.25)):
        parts.append(sh.cylinder(r, 0.05, bright, bevel=0.0, segments=8).transformed(compose(T(2.4, 4.03, -0.3), R(0, 70, 0), T(0, 0, dz))))
    spin = R(0, SPIN, 0)
    a.add("Body", [p.transformed(spin) for p in parts])
    landmark(a, DESIGN, ["DetailBench_1", "DetailBench_2"], fit="none",
             colliders=[box_collider("Bench", (5.0, 4.0, 5.0), (0, 2.0, 0))])
    return a
