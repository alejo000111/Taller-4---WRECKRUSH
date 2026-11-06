import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _landmark_lib import landmark, box_collider
from _chaos_lib import grounded
import ScrapWall


def build():
    a = Asset("ScrapHeap", budget=2000, atlas=1024, ao_radius=1.0, edge_width=0.06, preview_radius=9.0,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")

    dirt = Material("scrapwall_sheet", color=(96, 84, 70))
    mound = sh.sphere(6.2, dirt, 12, 7)
    rng = np.random.default_rng(14)
    mound.pos *= 1 + rng.normal(0, 0.1, (len(mound.pos), 1))
    mound.pos *= np.array([1.0, 0.45, 0.85])
    a.add("Body", grounded(sh.recompute_normals(mound)))
    tones = [(176, 40, 32), (40, 90, 160), (220, 180, 40), (90, 96, 104), (60, 140, 90)]
    for k in range(9):
        color = tones[k % len(tones)]
        mat = Material("paint", color=color, under=(130, 70, 40), wear=0.7, scratches=0.6, rough=0.5, dirt=0.5, skin=False)
        size = (rng.uniform(2.0, 4.6), rng.uniform(0.15, 0.5), rng.uniform(1.2, 3.0))
        ang = rng.uniform(0, 2 * np.pi)
        dist = rng.uniform(0.0, 4.5)
        y = 2.8 * (1 - (dist / 6.2) ** 2) + 0.2
        plate = sh.rounded_box(size, 0.0, 1, mat)
        a.add("Body", plate.transformed(compose(T(np.cos(ang) * dist, y, np.sin(ang) * dist * 0.85), R(rng.uniform(-40, 40), rng.uniform(0, 180), rng.uniform(-40, 40)))))
    rubber = Material("rubber", color=(26, 26, 28), pattern="ribs", freq=10.0)
    for k in range(4):
        ang = rng.uniform(0, 2 * np.pi)
        t = sh.lathe([(0.7, -0.4), (1.3, -0.4), (1.45, 0.0), (1.3, 0.4), (0.7, 0.4)], 12, rubber, closed=True, smooth_angle=50)
        dist = rng.uniform(2.0, 5.0)
        y = 2.6 * (1 - (dist / 6.2) ** 2) + 0.3
        a.add("Body", t.transformed(compose(T(np.cos(ang) * dist, y, np.sin(ang) * dist * 0.85), R(rng.uniform(20, 80), rng.uniform(0, 180), 0))))
    pipe = Material("scrapwall_sheet", color=(120, 120, 124))
    for k in range(3):
        ang = rng.uniform(0, 2 * np.pi)
        p = sh.cylinder(0.3, rng.uniform(4.0, 7.0), pipe, bevel=0.0, segments=6)
        a.add("Body", p.transformed(compose(T(np.cos(ang) * 2.0, 2.0, np.sin(ang) * 2.0), R(rng.uniform(30, 70), rng.uniform(0, 180), 0))))
    door = Material("paint", color=(40, 90, 160), under=(130, 70, 40), wear=0.6, scratches=0.5, rough=0.5, dirt=0.5, skin=False)
    a.add("Body", sh.rounded_box((3.4, 2.4, 0.15), 0.04, 1, door).transformed(compose(T(1.5, 3.2, -1.0), R(-25, 30, 15))))

    landmark(a, "Zones/ScrapYard/Landmarks", "ScrapPile", fit="box", colliders=[box_collider("Heap", (10.0, 4.0, 9.0), (0, 2.0, 0))])
    return a
