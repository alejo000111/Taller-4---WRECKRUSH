import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset
from _chaos_lib import basalt, crystal, VIOLET
from _ground_lib import ring
from _landmark_lib import landmark, box_collider


def build():
    a = building_asset("BeamPillarBase", 1400, 8.0)
    a.role("Glow", "neon", color=VIOLET)
    stone = basalt(veins=0.9)
    a.add("Body", sh.lathe([(0.0, 0.0), (6.0, 0.0), (6.0, 0.5), (5.4, 0.9), (4.6, 1.3), (3.0, 1.6), (0.0, 1.6)], 12, stone, smooth_angle=25, start=15))
    a.add("Glow", ring(5.7, 6.15, 0.55, None, segments=36))
    a.add("Glow", ring(2.4, 2.9, 1.7, None, segments=24))
    a.add("Body", sh.lathe([(2.4, 1.55), (2.4, 2.2), (2.0, 2.2), (2.0, 1.55)], 12, stone, closed=True, smooth_angle=30))
    for k in range(6):
        ang = np.radians(k * 60 + 15)
        x, z = np.cos(ang) * 4.4, np.sin(ang) * 4.4
        h = 1.6 + (k % 3) * 0.7
        a.add("Glow", crystal(0.35, h, None, facets=4).transformed(compose(T(x, 1.0, z), R(np.sin(ang) * 18, 0, -np.cos(ang) * 18))))
    landmark(a, "Zones/ChaosCore/Landmarks", "BeamPillar", fit="none", keep=["SkyBeam"], tint={"Glow": "BeamRing"},
             colliders=[box_collider("Base", (11.0, 1.6, 11.0), (0, 0.8, 0))])
    return a
