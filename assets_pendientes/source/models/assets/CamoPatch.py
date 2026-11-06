from wr3d import Material
from _ground_lib import ground_asset, blob, slab
from _landmark_lib import patch
import _military_lib


def build():
    a = ground_asset("CamoPatch", 200, 7.0)
    turf = Material("military_camo", colors=[(84, 102, 58), (62, 78, 44), (110, 104, 70), (44, 52, 34)], scale=0.22, wear=0.0, scratches=0.0, dirt=0.3)
    a.add("Body", slab(blob(29, 5.0, 3.0, points=30, rough=0.26), 0.06, turf))
    patch(a, ["Zones/Military/GroundDetail"], ["CamoPatch"], lift=0.02)
    return a
