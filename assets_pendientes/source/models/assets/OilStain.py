from wr3d import Material
from _ground_lib import ground_asset, blob, slab
from _landmark_lib import patch


def build():
    a = ground_asset("OilStain", 200, 7.0)
    oil = Material("glossy", color=(18, 16, 14), rough=0.06, metal=0.2, dirt=0.05, decals=[])
    a.add("Body", slab(blob(13, 4.5, 4.0, points=28, rough=0.3), 0.04, oil))
    patch(a, ["Zones/ScrapYard/GroundDetail", "Zones/Industrial/GroundDetail"], ["OilStain"], lift=0.025)
    return a
