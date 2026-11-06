import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _chaos_lib import basalt, obsidian, crystal, VIOLET, PINK

SPHERE_Y = 11.0


def build():
    a = Asset("VoidReactor", budget=4000, atlas=1024, ao_radius=1.0, edge_width=0.07, gradient=0.06, highlight=0.45, preview_radius=10.6,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Void", "plain", color=(6, 4, 10), material="Glass")
    a.role("Glow", "neon", color=VIOLET)
    a.role("Pink", "neon", color=PINK)

    stone = basalt(veins=0.83, glow=VIOLET)
    metal = obsidian(rim_glow=0.25, glow=VIOLET)
    a.add("Body", sh.lathe([(0.0, 0.0), (6.8, 0.0), (6.8, 1.2), (6.3, 1.6), (0.0, 1.6)], 8, stone, smooth_angle=20, start=22.5))
    a.add("Glow", sh.lathe([(6.32, 1.61), (5.9, 1.61)], 8, None, smooth_angle=20, start=22.5))
    a.add("Body", sh.lathe([(0.0, 1.6), (5.4, 1.6), (5.4, 2.0), (5.0, 2.2), (0.0, 2.2)], 8, metal, smooth_angle=20, start=22.5))
    a.add("Body", sh.lathe([(0.0, 2.2), (3.2, 2.2), (3.0, 3.8), (2.4, 4.2), (0.0, 4.2)], 8, metal, smooth_angle=30, start=22.5))
    a.add("Glow", sh.lathe([(3.11, 3.0), (3.05, 3.4)], 8, None, smooth_angle=20, start=22.5))

    for k in range(4):
        ang = np.radians(45 + 90 * k)
        d = np.array([np.cos(ang), 0.0, np.sin(ang)])
        base = d * 4.6
        pylon = sh.lathe([(0.0, 0.0), (0.75, 0.0), (0.6, 8.0), (0.42, 12.5), (0.0, 12.8)], 6, metal, smooth_angle=20)
        a.add("Body", pylon.transformed(compose(T(base[0], 2.2, base[2]), R(0, 0, 0))))
        tip = base + np.array([0, 15.4, 0]) - d * 0.6
        a.add("Pink", crystal(0.45, 1.8, None, facets=5).transformed(compose(T(*tip), R(0, 0, 0))))
        a.add("Glow", sh.sweep([tuple(tip), (0.0, SPHERE_Y, 0.0)], 0.06, 4, None))
        a.add("Glow", sh.box((0.1, 7.0, 0.1), None).transformed(T(*(base * 0.86 + np.array([0, 7.5, 0])))))

    a.add("Void", sh.sphere(2.8, None, 16, 10).transformed(T(0, SPHERE_Y, 0)))
    a.add("Glow", sh.torus(3.6, 0.14, None, segments=20, sides=4).transformed(compose(T(0, SPHERE_Y, 0), R(70, 0, 15))))
    a.add("Glow", sh.torus(3.9, 0.12, None, segments=20, sides=4).transformed(compose(T(0, SPHERE_Y, 0), R(-60, 30, -10))))
    a.add("Pink", sh.torus(4.3, 0.1, None, segments=20, sides=4).transformed(compose(T(0, SPHERE_Y, 0), R(10, 0, 70))))
    a.add("Glow", sh.cylinder(0.25, SPHERE_Y - 4.2 - 2.8, None, bevel=0.0, segments=6).transformed(T(0, (SPHERE_Y - 2.8 + 4.2) / 2, 0)))
    a.add("Glow", sh.cylinder(0.2, 3.0, None, bevel=0.0, segments=6).transformed(T(0, SPHERE_Y + 2.8 + 1.5, 0)))
    halo = sh.lathe([(1.2, -0.15), (1.6, -0.15), (1.6, 0.15), (1.2, 0.15)], 12, metal, closed=True, smooth_angle=40)
    a.add("Body", halo.transformed(T(0, SPHERE_Y + 6.8, 0)))
    a.add("Glow", sh.lathe([(1.62, -0.06), (1.62, 0.06)], 12, None, smooth_angle=40).transformed(T(0, SPHERE_Y + 6.8, 0)))

    destructible(a, "ChaosCore")
    collider(a, "Hitbox", (6.4, 6.4, 6.4), (0, SPHERE_Y, 0), shape="Ball")
    collider(a, "Base", (13.6, 4.2, 13.6), (0, 2.1, 0), shape="Cylinder")
    for k in range(4):
        ang = np.radians(45 + 90 * k)
        collider(a, f"Pylon{k + 1}", (1.4, 12.8, 1.4), (np.cos(ang) * 4.6, 2.2 + 6.4, np.sin(ang) * 4.6))
    return a
