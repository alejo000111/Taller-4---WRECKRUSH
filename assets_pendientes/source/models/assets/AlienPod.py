import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _chaos_lib import basalt, rock, grounded, crystal, ALIEN

POD_Y = 3.9


def petal(mat):
    path = [(0.0, 0.0, 0.0), (0.0, 1.0, -0.95), (0.0, 2.2, -1.2), (0.0, 3.1, -1.0), (0.0, 3.6, -0.75)]
    return sh.sweep(path, 0.5, 5, mat, samples=8, taper=lambda u: 1.0 - 0.8 * u ** 1.4)


def build():
    a = Asset("AlienPod", budget=1500, atlas=512, ao_radius=0.6, edge_width=0.05, gradient=0.06, highlight=0.4, preview_radius=5.2,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Shell", "glass", color=(60, 200, 150), transparency=0.35)
    a.role("Glow", "neon", color=ALIEN)

    flesh = Material("rubber", color=(40, 60, 46), pattern="dots", freq=6.0, depth=0.006, dirt=0.3)
    stone = basalt(veins=0.83, glow=ALIEN)
    a.add("Body", grounded(rock(2.8, stone, 11, squash=(1.0, 0.25, 1.0), segments=10, rings=5).transformed(T(0, 0.55, 0))))
    for k in range(5):
        ang = np.radians(k * 72 + 20)
        d = np.array([np.cos(ang), 0.0, np.sin(ang)])
        path = [tuple(d * 1.2 + np.array([0, 1.4, 0])), tuple(d * 2.3 + np.array([0, 0.7, 0])), tuple(d * 3.2 + np.array([0, 0.15, 0]))]
        a.add("Body", sh.sweep(path, 0.32, 5, flesh, samples=6, taper=lambda u: 1.0 - 0.7 * u))
    for k in range(4):
        ang = k * 90 + 45
        a.add("Body", petal(flesh).transformed(compose(R(0, ang, 0), T(0, 1.2, -1.7), S(1.0, 1.0, 1.0))))

    shell = sh.lathe([(0.0, 1.3), (1.6, 1.6), (2.5, 2.8), (2.7, 3.9), (2.3, 5.2), (1.4, 6.1), (0.6, 6.6), (0.0, 6.7)], 14, None, smooth_angle=60)
    a.add("Shell", shell)
    a.add("Glow", sh.sphere(1.3, None, 12, 7).transformed(T(0, POD_Y, 0)))
    for k in range(5):
        ang = np.radians(k * 72)
        pts = []
        for t in np.linspace(0.0, 1.0, 7):
            y = 1.6 + t * 4.9
            r = float(np.interp(y, [1.3, 1.6, 2.8, 3.9, 5.2, 6.1, 6.6], [0.0, 1.6, 2.5, 2.7, 2.3, 1.4, 0.6])) + 0.04
            a_t = ang + 0.5 * t
            pts.append((np.cos(a_t) * r, y, np.sin(a_t) * r))
        a.add("Glow", sh.sweep(pts, 0.06, 4, None, samples=10))
    a.add("Body", sh.lathe([(0.0, 6.5), (0.75, 6.5), (0.6, 7.0), (0.0, 7.2)], 8, flesh, smooth_angle=40))
    for k, ang in enumerate((0, 120, 240)):
        a.add("Glow", crystal(0.16, 1.2, None, facets=4).transformed(compose(R(0, ang, 0), T(0.3, 7.4, 0), R(0, 0, -15))))

    destructible(a, "ChaosCore")
    collider(a, "Hitbox", (5.4, 5.4, 5.4), (0, POD_Y, 0), shape="Ball")
    collider(a, "Base", (6.0, 1.2, 6.0), (0, 0.6, 0), shape="Cylinder")
    return a
