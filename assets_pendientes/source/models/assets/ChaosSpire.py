import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _landmark_lib import landmark, box_collider
from _chaos_lib import basalt, obsidian, crystal, rock, grounded, crystal_cluster, VIOLET, PINK

H = 38.0


def build():
    a = Asset("ChaosSpire", budget=2000, atlas=1024, ao_radius=1.2, edge_width=0.08, gradient=0.06, highlight=0.45, preview_radius=22.0,
              views=[("FRONT 3/4", 215, 10), ("BACK 3/4", 35, 14), ("SIDE", 270, 4), ("TOP", 200, 45)])
    a.role("Body", "surface")
    a.role("Crystal", "glass", color=VIOLET, transparency=0.2)
    a.role("Core", "neon", color=PINK)

    stone = basalt(veins=0.8)
    a.add("Body", grounded(rock(8.0, stone, 4, squash=(1.0, 0.35, 0.8), segments=10, rings=5).transformed(T(0, 1.4, 0))))
    for seed, (x, z, r) in enumerate(((7.0, 3.0, 2.0), (-6.5, -2.5, 1.8), (2.0, -6.0, 1.6))):
        a.add("Body", grounded(rock(r, stone, 50 + seed, squash=(1.0, 0.8, 1.0), segments=7, rings=4).transformed(T(x, 0.8, z))))
    main = crystal(4.6, 30.0, None, facets=6, crown=0.28)
    a.add("Crystal", main.transformed(compose(T(0, 16.0, 0), R(0, 0, 6))))
    a.add("Core", crystal(1.2, 24.0, None, facets=5).transformed(compose(T(0, 15.0, 0), R(0, 0, 6))))
    a.add("Crystal", [p.transformed(T(0, 2.0, 0)) for p in crystal_cluster(None, 9, 6, 1.8, 10.0, 5.0, tilt=32)])
    for k, (ang, h, y) in enumerate(((20, 2.6, 30.0), (140, 2.0, 34.0), (250, 2.2, 27.0))):
        rad = np.radians(ang)
        a.add("Core", crystal(0.7, h, None, facets=4).transformed(compose(T(np.cos(rad) * 7.0, y, np.sin(rad) * 7.0), R(25 * k, 0, 30))))

    landmark(a, "Zones/ChaosCore/Landmarks", "FloatingCrystal", fit="box", colliders=[
        box_collider("Base", (14.0, 4.0, 11.0), (0, 2.0, 0)),
        box_collider("Crystal", (7.0, 28.0, 7.0), (0, 16.0, 0)),
    ])
    return a
