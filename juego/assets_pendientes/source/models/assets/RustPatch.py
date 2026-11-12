from wr3d import Material
from _ground_lib import ground_asset, blob, slab
from _landmark_lib import patch
import ScrapWall


def build():
    a = ground_asset("RustPatch", 200, 7.0)
    rust = Material("scrapwall_sheet", color=(128, 70, 40))
    a.add("Body", slab(blob(7, 5.0, 4.0, points=30, rough=0.24), 0.05, rust))
    patch(a, ["Zones/ScrapYard/GroundDetail"], ["RustPatch"], lift=0.02)
    return a
