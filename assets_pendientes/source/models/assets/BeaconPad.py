from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import ALL, expedition_asset
from _ground_lib import ring
from _landmark_lib import patch


def build():
    a = expedition_asset("BeaconPad", 800, 7.0, atlas=512)
    a.role("Glow", "neon", color=(200, 240, 255))
    metal = Material("metal", color=(62, 68, 78), rough=0.35, polish=0.5, dirt=0.35, scratches=0.35)
    a.add("Body", sh.lathe([(5.5, 0.0), (5.5, 0.8), (5.0, 1.3), (4.2, 1.6), (4.2, 2.0), (0.0, 2.0)], 16, metal, smooth_angle=30))
    a.add("Glow", ring(4.3, 4.6, 2.05, None, segments=24))
    a.add("Glow", ring(1.4, 1.8, 2.05, None, segments=16))
    for k in range(6):
        ang = k * 60.0
        a.add("Body", sh.box((1.2, 1.0, 0.8), metal).transformed(compose(R(0, ang, 0), T(5.2, 0.5, 0))))
        a.add("Glow", sh.box((2.0, 0.08, 0.25), None).transformed(compose(R(0, ang + 30, 0), T(3.0, 2.04, 0))))
    patch(a, ALL, ["Beacon1", "Beacon2", "Beacon3"], functional=True)
    return a
