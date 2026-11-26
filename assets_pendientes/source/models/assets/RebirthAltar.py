import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _station_lib import station, collider, platform, sign_face
from _chaos_lib import basalt, obsidian, crystal, VIOLET, PINK

CORE_Y = 7.4


def rune_ring(radius, v, count=16):
    out = []
    for k in range(count):
        u = (k + 0.5) * 2 * np.pi * radius / count
        kind = k % 4
        if kind == 0:
            out.append({"type": "rect", "center": (u, v), "size": (0.12, 0.42), "color": VIOLET, "rough": 0.1, "wear": 0.0})
        elif kind == 1:
            out.append({"type": "circle", "center": (u, v), "radius": 0.18, "outline": 0.05, "color": VIOLET, "wear": 0.0})
        elif kind == 2:
            out.append({"type": "rect", "center": (u, v), "size": (0.34, 0.34), "angle": 45, "outline": 0.05, "color": VIOLET, "wear": 0.0})
        else:
            out.append({"type": "rect", "center": (u, v), "size": (0.42, 0.12), "color": VIOLET, "rough": 0.1, "wear": 0.0})
    return out


def build():
    a = Asset("RebirthAltar", budget=3500, atlas=1024, ao_radius=0.9, edge_width=0.07, gradient=0.06, highlight=0.45, preview_radius=7.2,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("FRONT", 180, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=VIOLET)
    a.role("Core", "neon", color=PINK)
    station(a, "RebirthAltar")
    platform(a, VIOLET)

    stone = basalt(veins=0.84, glow=VIOLET)
    lower = basalt(veins=0.86, glow=VIOLET, decals=rune_ring(5.0, 0.55))
    a.add("Body", sh.lathe([(0.0, 0.2), (5.0, 0.2), (5.0, 1.0), (4.8, 1.2), (0.0, 1.2)], 8, lower, smooth_angle=20, start=22.5, r_ref=5.0))
    a.add("Glow", sh.lathe([(4.82, 1.21), (4.2, 1.21)], 8, None, smooth_angle=20, start=22.5))
    a.add("Body", sh.lathe([(0.0, 1.2), (3.8, 1.2), (3.8, 2.0), (3.6, 2.2), (0.0, 2.2)], 8, obsidian(rim_glow=0.3, glow=VIOLET), smooth_angle=20, start=22.5))
    a.add("Glow", sh.lathe([(2.6, 2.21), (2.3, 2.21)], 16, None, smooth_angle=60))
    a.add("Body", sh.lathe([(0.0, 2.2), (1.2, 2.2), (0.9, 3.2), (0.5, 3.5), (0.0, 3.5)], 8, stone, smooth_angle=30))

    for k in range(4):
        ang = np.radians(45 + 90 * k)
        p = np.array([np.cos(ang) * 4.2, 1.2, np.sin(ang) * 4.2])
        spire = sh.lathe([(0.0, 0.0), (0.6, 0.0), (0.45, 4.6), (0.25, 5.2), (0.0, 5.3)], 4, obsidian(rim_glow=0.3, glow=VIOLET), smooth_angle=20, start=45)
        a.add("Body", spire.transformed(T(*p)))
        a.add("Core", crystal(0.32, 1.2, None, facets=4).transformed(T(p[0], p[1] + 5.8, p[2])))
        a.add("Glow", sh.box((0.06, 3.6, 0.06), None).transformed(T(p[0] - np.cos(ang) * 0.48, p[1] + 2.4, p[2] - np.sin(ang) * 0.48)))

    a.add("Core", sh.sphere(1.6, None, 16, 10).transformed(T(0, CORE_Y, 0)))
    a.add("Glow", sh.torus(2.8, 0.1, None, segments=24, sides=4).transformed(compose(T(0, CORE_Y, 0), R(20, 0, 10))))
    a.add("Glow", sh.torus(2.4, 0.08, None, segments=20, sides=4).transformed(compose(T(0, CORE_Y, 0), R(-30, 45, 0))))
    for k in range(3):
        ang = np.radians(k * 120)
        a.add("Body", crystal(0.4, 1.4, obsidian(rim_glow=0.6, glow=PINK), facets=4).transformed(compose(T(np.cos(ang) * 3.3, CORE_Y - 0.6 + 0.5 * k, np.sin(ang) * 3.3), R(20, k * 40, 15))))

    sign = sh.rounded_box((4.6, 1.0, 0.3), 0.06, 1, obsidian(), face_mats={"-z": sign_face("REBIRTH", VIOLET, (4.6, 1.0), height=0.65)})
    a.add("Body", sign.transformed(compose(T(0, 0.8, -4.75), R(-10, 0, 0))))

    collider(a, "Dais", (10.0, 2.2, 10.0), (0, 1.1, 0), shape="Cylinder")
    collider(a, "Core", (3.2, 3.2, 3.2), (0, CORE_Y, 0), shape="Ball")
    return a
