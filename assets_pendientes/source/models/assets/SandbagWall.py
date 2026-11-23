import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _military_lib import SAND, KHAKI, STENCIL

BAG = (2.6, 0.95, 1.5)
FOOTING_H = 0.3


def sandbag(mat, rng):
    hx, hy, hz = BAG[0] / 2, BAG[1] / 2, BAG[2] / 2
    bag = sh.rounded_box(BAG, 0.42, 1, mat, faces=["+x", "-x", "+y", "+z", "-z"])
    x, y, z = bag.pos[:, 0], bag.pos[:, 1], bag.pos[:, 2]
    end = np.clip(np.abs(x) / hx, 0, 1) ** 2
    bag.pos[:, 1] = y * (1 - 0.32 * end) - hy * 0.1 * end * np.sign(y)
    bag.pos[:, 2] = z * (1 - 0.22 * end)
    bag.pos[:, 1] += np.where(y > 0, 0.08 * (1 - end), 0.0)
    bag.pos += rng.normal(0, 0.025, bag.pos.shape)
    return sh.recompute_normals(bag)


def build():
    a = Asset("SandbagWall", budget=2000, atlas=1024, ao_radius=0.6, edge_width=0.04, gradient=0.1, highlight=0.3, preview_radius=6.6,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("FRONT", 180, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")

    rng = np.random.default_rng(12)
    tones = [SAND, KHAKI, (170, 152, 108), (196, 178, 132)]
    ties = [{"type": "rect", "center": (0.0, 0.0), "size": (0.06, 1.2), "darken": 0.5, "raise": -0.006}]
    bags = []
    rows = [(4, (-0.82, 0.82), 0.0), (4, (0.0,), 0.5), (4, (0.0,), 0.0), (3, (0.0,), 0.5)]
    y = FOOTING_H + BAG[1] * 0.42
    for r, (count, depths, stagger) in enumerate(rows):
        for zc in depths:
            for i in range(count):
                x = (i - (count - 1) / 2) * (BAG[0] * 1.02) + stagger * 0.3 * (1 if r % 2 else -1)
                mat = Material("military_burlap", color=tones[int(rng.integers(len(tones)))], dirt=0.5, decals=ties if rng.random() < 0.5 else [])
                bag = sandbag(mat, rng)
                yaw = rng.normal(0, 3)
                roll = rng.normal(0, 2)
                bags.append(bag.transformed(compose(T(x, y + rng.normal(0, 0.03), zc + rng.normal(0, 0.06)), R(roll, yaw, rng.normal(0, 2)))))
        y += BAG[1] * 0.82
    a.add("Body", bags)

    concrete = Material("concrete", color=(150, 146, 132), dirt=0.6, decals=[
        {"type": "stripes", "center": (0.0, -1.55), "size": (11.6, 0.3), "width": 0.3, "color": (255, 210, 31), "wear": 0.6},
    ])
    a.add("Body", sh.rounded_box((11.6, FOOTING_H, 3.4), 0.04, 1, concrete, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, FOOTING_H / 2, 0)))
    sign = Material("paint", color=(86, 100, 56), under=(120, 110, 90), wear=0.4, scratches=0.4, rough=0.6, dirt=0.5, skin=False, decals=[
        {"type": "text", "text": "SECTOR 4", "center": (0.0, -0.1), "height": 0.3, "color": STENCIL, "font": "impact", "wear": 0.4},
        {"type": "text", "text": "NO ENTRY", "center": (0.0, 0.25), "height": 0.2, "color": (255, 210, 31), "font": "black", "wear": 0.4},
    ])
    plate = sh.rounded_box((1.6, 0.9, 0.06), 0.0, 1, sign, faces=["-z", "+x", "-x", "+y", "-y", "+z"])
    a.add("Body", plate.transformed(compose(T(-2.6, 2.3, -0.82 - BAG[2] / 2 - 0.05), R(-8, 0, 3))))

    destructible(a, "Military")
    top = FOOTING_H + BAG[1] * 0.42 + 3 * BAG[1] * 0.82 + BAG[1] * 0.5
    collider(a, "Hitbox", (11.4, top, 1.8), (0, top / 2, 0))
    collider(a, "Base", (11.6, 1.4, 3.4), (0, 0.7, 0))
    return a
