import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel
from _bay_lib import STATIONS
from _landmark_lib import landmark

RADIUS = 7.0


def build():
    a = building_asset("FloorRingMarker", 400, 8.0, atlas=256)
    a.role("Glow", "neon", color=(202, 140, 57))
    channel = steel((40, 46, 56), dirt=0.5)
    for k in range(8):
        ang = k * 45.0
        rad = np.radians(ang)
        pos = T(np.cos(rad) * RADIUS, 0, -np.sin(rad) * RADIUS)
        a.add("Body", sh.box((0.3, 0.05, 1.9), channel).transformed(compose(pos, T(0, 0.025, 0), R(0, ang, 0))))
        a.add("Glow", sh.box((0.13, 0.08, 1.5), None).transformed(compose(pos, T(0, 0.04, 0), R(0, ang, 0))))
    landmark(a, STATIONS, "PetStation_Markers", fit="box", tint={"Glow": "RingMarker"})
    return a
