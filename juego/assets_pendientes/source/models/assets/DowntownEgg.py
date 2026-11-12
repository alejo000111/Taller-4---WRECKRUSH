from wr3d import Asset, Material, T
from wr3d import shapes as sh
from _egg_common import shell, band, place, EGG_H


def build():
    a = Asset("DowntownEgg", budget=3400, ao_radius=0.4, edge_width=0.035)
    a.role("Shell", "surface")
    a.role("Band", "surface")
    a.role("Glow", "neon", color=(60, 210, 255))
    taxi = Material("egg_armor", color=(255, 196, 40), latitudes=(-1.05, 1.05), meridian_step=45.0, chips=0.3, dirt=0.3)
    checks = [{"type": "rect", "center": (0.11 + u * 0.44 + (0.22 if row else 0.0), 0.12 + row * 0.22), "size": (0.21, 0.21), "radius": 0.0, "color": (22, 22, 26), "wear": 0.0, "raise": 0.0} for row in (0, 1) for u in range(23)]
    checker = Material("metal", color=(238, 236, 228), rough=0.45, polish=0.3, dirt=0.3, skin=False, decals=checks)
    steel = Material("metal", color=(84, 88, 98), rough=0.38, polish=0.65, dirt=0.3, skin=False)
    sign = Material("metal", color=(40, 150, 70), rough=0.4, polish=0.5, dirt=0.2, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (0.62, 0.2), "radius": 0.03, "color": (236, 240, 236), "wear": 0.0, "raise": 0.004},
    ])
    a.add("Shell", shell(taxi, 24, 16))
    a.add("Band", band(-0.3, 0.16, 0.07, checker, 24))
    for y in (-1.05, 1.05):
        a.add("Band", band(y - 0.05, y + 0.05, 0.035, steel, 24))
    for theta in range(0, 360, 45):
        for k, y in enumerate((0.42, 0.68, 1.3, -0.62, -1.3)):
            if (theta // 45 + k) % 3 == 0:
                continue
            window = sh.box((0.18, 0.04, 0.16), None)
            a.add("Glow", place(window, theta + 22.5, y, 0.015))
    plate = sh.rounded_box((0.78, 0.06, 0.3), 0.02, 1, sign)
    a.add("Band", place(plate, 90, -0.75, 0.04))
    a.add("Band", place(plate, 270, -0.75, 0.04))
    top = EGG_H / 2 - 0.06
    a.add("Band", sh.cylinder(0.05, 0.42, steel, bevel=0.01, segments=8).transformed(T(0, top + 0.2, 0)))
    a.add("Band", sh.rounded_box((0.22, 0.52, 0.2), 0.04, 1, steel).transformed(T(0, top + 0.66, 0)))
    for k in range(3):
        a.add("Glow", sh.sphere(0.06, None, 8, 5).transformed(T(0, top + 0.82 - k * 0.15, -0.11)))
    for theta in (30, 150, 270):
        cone = sh.frustum(0.12, 0.03, 0.34, Material("paint", color=(255, 122, 26), under=(80, 40, 20), wear=0.3), bevel=0.0, segments=8)
        a.add("Band", place(cone, theta, -1.55, -0.02))
    return a
