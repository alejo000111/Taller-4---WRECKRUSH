import numpy as np

from wr3d import Material, T, R, S, compose
from wr3d import shapes as sh
from _wall_lib import wall_asset, targets, SEGMENT
from _chaos_lib import basalt, obsidian, crystal, grounded, rock

H = 6.0


def build():
    a = wall_asset("ChaosWall", 900, height=H)
    targets(a, ["Zones/ChaosCore/Perimeter"])

    stone = basalt(veins=0.82)
    glass = obsidian(rim_glow=0.45)
    a.add("Body", sh.rounded_box((SEGMENT, H - 1.6, 1.6), 0.0, 1, stone, faces=["+z", "-z", "+y"]).transformed(T(0, (H - 1.6) / 2, 0)))
    rng = np.random.default_rng(31)
    x = -SEGMENT / 2 + 1.2
    k = 0
    while x < SEGMENT / 2 - 1.0:
        h = rng.uniform(2.0, 3.6)
        r = rng.uniform(0.7, 1.1)
        shard = crystal(r, h, glass, facets=4, crown=0.4)
        a.add("Body", shard.transformed(compose(T(x, H - 1.6 + h * 0.3, rng.uniform(-0.2, 0.2)), R(rng.uniform(-8, 8), rng.uniform(0, 90), rng.uniform(-12, 12)))))
        if k % 3 == 0:
            a.add("Glow", sh.gem(0.25, 0.9, 4, None).transformed(T(x + 0.8, H - 1.0, rng.choice([-0.85, 0.85]))))
        x += rng.uniform(1.6, 2.6)
        k += 1
    for sz in (-1, 1):
        a.add("Glow", sh.box((SEGMENT, 0.1, 0.06), None).transformed(T(0, 0.6, sz * 0.83)))
    return a
