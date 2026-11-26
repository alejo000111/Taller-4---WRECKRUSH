import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, blob, eye, metal
import _chaos_lib


def build():
    a = pet_asset("ChaosDragon", 4200, 3.4)
    a.role("Glow", "neon", color=(255, 59, 160))
    a.role("Eyes", "neon", color=(255, 160, 40))
    obsidian = Material("chaos_obsidian")
    plate = metal((150, 110, 60))
    crystal = Material("glossy", color=(150, 60, 220), metal=0.1, rough=0.08)
    membrane = Material("glossy", color=(90, 40, 120), metal=0.0, rough=0.3)
    a.add("Body", blob((1.1, 1.0, 1.9), obsidian, 12, 8).transformed(compose(T(0, 0, 0.1), R(-15, 0, 0))))
    a.add("Glow", sh.sphere(0.28, None, 10, 6).transformed(T(0, 0.05, -0.75)))
    a.add("Body", sh.tube(0.38, 0.28, 0.12, plate, segments=12).transformed(compose(T(0, 0.05, -0.78), R(90, 0, 0))))
    a.add("Body", sh.sweep([(0, 0.35, -0.6), (0, 0.8, -0.95), (0, 1.05, -1.2)], 0.24, 8, obsidian, samples=6, taper=lambda t: 1.0 - 0.2 * t))
    a.add("Body", blob((0.7, 0.55, 0.95), obsidian, 10, 7).transformed(T(0, 1.15, -1.45)))
    a.add("Body", sh.rounded_box((0.45, 0.22, 0.45), 0.08, 1, obsidian).transformed(T(0, 1.02, -1.88)))
    for side in (-1, 1):
        a.add("Eyes", sh.gem(0.08, 0.22, 4, None, crown=0.2).transformed(compose(T(side * 0.2, 1.25, -1.82), R(0, 0, side * 70))))
        horn = [(side * 0.22, 1.4, -1.35), (side * 0.38, 1.7, -1.2), (side * 0.42, 1.95, -0.95)]
        a.add("Body", sh.sweep(horn, 0.08, 5, plate, samples=6, taper=lambda t: 1.0 - 0.8 * t))
        wing = np.array([(0.0, 0.0), (1.6, 0.5), (2.1, 0.1), (1.7, -0.3), (1.2, -0.25), (0.7, -0.45), (0.2, -0.3)])
        mesh = sh.extrude(wing, 0.05, membrane, bevel=0.0, corner_radius=0.0)
        a.add("Body", mesh.transformed(compose(T(side * 0.35, 0.45, 0.1), R(0, 0, side * 20), R(0, 0 if side > 0 else 180, 0), R(90, 0, 0))))
        a.add("Body", sh.sweep([(side * 0.35, 0.45, 0.1), (side * 1.2, 1.0, 0.2), (side * 1.9, 0.75, 0.3)], 0.06, 5, plate, samples=6))
        for z in (-0.4, 0.55):
            a.add("Body", sh.rounded_box((0.22, 0.6, 0.26), 0.08, 1, obsidian).transformed(compose(T(side * 0.42, -0.62, z), R(10, 0, 0))))
    tail = [(0, -0.05, 0.95), (0, -0.2, 1.5), (0.15, -0.1, 2.0), (0.35, 0.15, 2.35)]
    a.add("Body", sh.sweep(tail, 0.2, 7, obsidian, samples=10, taper=lambda t: 1.0 - 0.7 * t))
    a.add("Body", sh.gem(0.18, 0.6, 5, crystal, crown=0.25).transformed(compose(T(0.42, 0.25, 2.5), R(60, 0, -30))))
    for k in range(4):
        a.add("Body", sh.gem(0.12, 0.42, 4, crystal, crown=0.2).transformed(compose(T(0, 0.55 - k * 0.05, -0.4 + k * 0.35), R(-20, 0, 0))))
    return a
