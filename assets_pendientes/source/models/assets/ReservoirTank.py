import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import VERDANT, expedition_asset
from _landmark_lib import patch
import ScrapWall


def build():
    a = expedition_asset("ReservoirTank", 900, 11.0, atlas=512)
    body = Material("scrapwall_sheet", color=(91, 97, 77))
    band = Material("paint", color=(239, 183, 95), under=(110, 100, 90), wear=0.5, scratches=0.4, rough=0.45, dirt=0.45, skin=False)
    steel = Material("metal", color=(70, 74, 72), rough=0.45, polish=0.3, dirt=0.5)
    a.add("Body", sh.lathe([(0.0, 0.0), (8.0, 0.0), (8.0, 11.0), (7.2, 12.4), (4.0, 13.4), (0.0, 13.6)], 16, body, smooth_angle=30))
    for y in (3.5, 7.5):
        a.add("Body", sh.lathe([(7.95, y - 0.5), (8.5, y - 0.5), (8.5, y + 0.5), (7.95, y + 0.5)], 16, band, closed=True, smooth_angle=30))
    for k in range(2):
        a.add("Body", sh.box((0.18, 12.0, 0.18), steel).transformed(T(-0.6 + k * 1.2, 6.5, -8.35)))
    for y in np.arange(1.0, 12.5, 1.0):
        a.add("Body", sh.box((1.2, 0.12, 0.12), steel).transformed(T(0, y, -8.35)))
    a.add("Body", sh.cylinder(0.7, 1.4, steel, bevel=0.0, segments=8).transformed(compose(T(5.0, 2.0, -6.5), R(90, 0, 40))))
    patch(a, [VERDANT], ["Reservoir"], remove=["ReservoirBand"])
    return a
