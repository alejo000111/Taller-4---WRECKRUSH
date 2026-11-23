from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import SKY, expedition_asset
from _ground_lib import ring
from _landmark_lib import patch

RADIUS = 83.0


def build():
    a = expedition_asset("SkyArena", 1400, 90.0, atlas=512)
    a.role("Glow", "neon", color=(173, 161, 230))
    paint = Material("paint", color=(230, 190, 110), under=(90, 90, 96), wear=0.4, scratches=0.3, rough=0.5, dirt=0.3, skin=False)
    for r, w in ((80.0, 0.7), (62.0, 0.35), (40.0, 0.5), (14.0, 0.4)):
        arcs = 8 if r > 30 else 2
        for k in range(arcs):
            a.add("Body", sh.lathe([(r + w / 2, 0.0), (r + w / 2, 0.05), (r - w / 2, 0.05)], 64 // arcs if r > 30 else 16, paint, smooth_angle=30, arc=360.0 / arcs, start=k * 360.0 / arcs))
    for k in range(12):
        a.add("Body", sh.box((21.0, 0.05, 0.35), paint).transformed(compose(R(0, k * 30, 0), T(51.0, 0.025, 0))))
    for k in range(8):
        a.add("Glow", sh.lathe([(RADIUS - 1.9, 0.0), (RADIUS - 1.9, 0.07), (RADIUS - 2.4, 0.07)], 9, None, smooth_angle=30, arc=45.0, start=k * 45.0))
    a.add("Body", sh.box((0.05, 0.05, 0.05), paint).transformed(T(0, 0.025, 0)))
    patch(a, [SKY], ["Arena"], lift=0.4, keep_height=True, overlay=True)
    return a
