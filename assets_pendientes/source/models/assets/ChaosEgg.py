import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _egg_common import shell, crack_path, egg_point, place


def build():
    a = Asset("ChaosEgg", budget=3600, ao_radius=0.4, edge_width=0.03)
    a.role("Shell", "surface")
    a.role("Glow", "neon", color=(255, 59, 160))
    a.role("Crystal", "surface")
    paths = [
        crack_path(80, 1.45, 115, -0.2, 14, 1),
        crack_path(200, 1.2, 175, -0.6, 16, 2),
        crack_path(320, 1.6, 290, 0.2, 12, 3),
        crack_path(20, -0.5, 60, -1.5, 12, 4, steps=6),
        crack_path(250, -0.2, 230, -1.4, 10, 5, steps=6),
    ]
    segments = [(np.asarray(p[i]), np.asarray(p[i + 1])) for p in paths for i in range(len(p) - 1)]
    obsidian = Material("egg_obsidian", color=(34, 20, 54), sheen=(166, 77, 255), glow=(255, 59, 160), cracks=segments, halo=0.08)
    crystal = Material("glossy", color=(130, 56, 220), rough=0.06, metal=0.2)
    a.add("Shell", shell(obsidian, 24, 16))
    for path in paths:
        a.add("Glow", sh.sweep(path, 0.03, 4, None, samples=len(path) * 2, taper=lambda t: 0.5 + 0.5 * np.sin(np.pi * t)))
    for theta, y, scale in ((100, 0.6, 1.6), (185, 0.2, 1.3), (305, 1.0, 1.45)):
        for j, (dth, dy, h, lean) in enumerate(((0, 0, 0.55, 0), (12, 0.12, 0.36, 25), (-10, -0.1, 0.3, -25))):
            gem = sh.gem(0.1 * scale, h * scale, 6, crystal)
            a.add("Crystal", place(gem.transformed(compose(R(0, 0, lean), T(0, h * scale * 0.3, 0))), theta + dth, y + dy, -0.02))
    for k in range(6):
        ang = np.radians(k * 60 + 15)
        r = 1.68 + 0.08 * np.sin(k * 2.0)
        y = -0.4 + 0.9 * np.sin(k * 1.3)
        shard = sh.gem(0.08, 0.3, 6, None)
        a.add("Glow", shard.transformed(compose(T(np.cos(ang) * r, y, -np.sin(ang) * r), R(k * 30, k * 50, k * 20))))
    for angle, y, size, tilt in ((35, -1.55, 0.26, 18), (165, -1.62, 0.2, -22), (270, -1.5, 0.3, 12)):
        base = egg_point(angle, y, 0.05)
        shard = sh.gem(size * 0.45, size * 1.8, 6, crystal).transformed(compose(T(*(base * np.array([1.18, 1.0, 1.18]))), R(tilt, angle, tilt)))
        a.add("Crystal", shard)
    return a
