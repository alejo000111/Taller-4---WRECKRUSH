import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _landmark_lib import landmark, box_collider
from _future_lib import pearl, graphite, CYAN, VIOLET

W = 15.6
H = 92.0


def build():
    a = Asset("NeonSpire", budget=2500, atlas=1024, ao_radius=1.5, edge_width=0.1, gradient=0.06, highlight=0.5, preview_radius=50.0,
              views=[("FRONT 3/4", 215, 8), ("BACK 3/4", 35, 12), ("FRONT", 180, 4), ("TOP", 200, 45)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=CYAN)
    a.role("Accent", "neon", color=VIOLET)

    glass = Material("glossy", color=(16, 20, 34), rough=0.06, metal=0.4, dirt=0.03, decals=[
        *[{"type": "rect", "center": (0.0, y), "size": (12.0, 0.12), "color": (60, 80, 120), "wear": 0.0} for y in np.arange(-40.0, 40.0, 3.0)],
    ])
    shaft = sh.lathe([(0.0, 3.0), (7.0, 3.0), (6.2, 50.0), (5.2, 78.0), (0.0, 78.0)], 6, glass, smooth_angle=10, start=30, r_ref=7.0)
    a.add("Body", shaft)
    plinth = graphite(panel=6.0)
    a.add("Body", sh.lathe([(0.0, 0.0), (W / 2, 0.0), (W / 2, 2.2), (7.0, 3.0), (0.0, 3.0)], 6, plinth, smooth_angle=10, start=30))
    for k in range(6):
        ang = np.radians(30 + k * 60)
        p0 = np.array([np.cos(ang) * 7.0, 3.0, -np.sin(ang) * 7.0])
        p1 = np.array([np.cos(ang) * 5.2, 78.0, -np.sin(ang) * 5.2])
        a.add("Body", sh.sweep([tuple(p0 * [1.03, 1, 1.03]), tuple(p1 * [1.03, 1, 1.03])], 0.45, 4, pearl(panel=6.0)))
        a.add("Glow", sh.sweep([tuple(p0 * [1.09, 1, 1.09]), tuple(p1 * [1.09, 1, 1.09])], 0.12, 3, None))
    for y, r in ((20.0, 7.0), (40.0, 6.6), (60.0, 5.9)):
        a.add("Body", sh.lathe([(r - 0.2, y - 0.4), (r + 0.8, y - 0.4), (r + 0.8, y + 0.4), (r - 0.2, y + 0.4)], 6, pearl(panel=6.0), closed=True, smooth_angle=10, start=30))
        a.add("Accent", sh.torus(r + 1.6, 0.12, None, segments=18, sides=4).transformed(T(0, y + 1.6, 0)))
    a.add("Body", sh.lathe([(0.0, 78.0), (5.6, 78.0), (4.0, 82.0), (1.2, 86.0), (0.0, 87.0)], 6, pearl(panel=6.0), smooth_angle=10, start=30))
    a.add("Glow", sh.lathe([(0.0, 86.0), (0.5, 86.0), (0.0, H)], 6, None, smooth_angle=10))

    landmark(a, "Zones/FutureDistrict/Landmarks", "NeonTower", fit="box", colliders=[box_collider("Tower", (13.0, 80.0, 13.0), (0, 40.0, 0))])
    return a
