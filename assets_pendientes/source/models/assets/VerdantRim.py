from _expedition_lib import VERDANT, terrain
from _rim_lib import rim_asset, arc_segment, colliders

RADIUS = 172.0
COUNT = 24
PROFILE = [(5.0, -12.0), (4.4, -4.0), (3.4, 3.0), (2.4, 7.5), (1.0, 9.6), (-1.0, 9.8), (-2.4, 8.2), (-3.0, 4.0), (-3.2, 0.5), (-3.0, -1.5)]


def build():
    a = rim_asset("VerdantRim", 300, 26.0)
    a.add("Body", arc_segment(PROFILE, RADIUS, COUNT, terrain("verdant", cap_amount=0.75), 61))
    a.meta["rim"] = {"targets": [{"path": VERDANT, "center": [0.0, -2880.0]}], "radius": RADIUS, "count": COUNT, "offset": 0.5,
                     "colliders": colliders(RADIUS, COUNT, -3.2, 2.0, 10.5)}
    return a
