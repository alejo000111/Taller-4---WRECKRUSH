from wr3d import T
from _expedition_lib import SKY, expedition_asset
from _chaos_lib import crystal_cluster
from _landmark_lib import patch


def build():
    a = expedition_asset("SkyCrystal", 300, 8.0, atlas=256)
    a.role("Crystal", "glass", color=(173, 161, 230), transparency=0.1)
    a.parts.pop("Body", None)
    a.roles.pop("Body", None)
    a.add("Crystal", crystal_cluster(None, 23, 4, 2.0, 13.0, 1.6, tilt=20))
    patch(a, [SKY], ["SkyShard"], tint=["Crystal"])
    return a
