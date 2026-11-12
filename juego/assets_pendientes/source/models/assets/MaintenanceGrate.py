from wr3d import Material, T
from wr3d import shapes as sh
from _building_lib import building_asset, steel, IMMERSION
from _landmark_lib import landmark


def build():
    a = building_asset("MaintenanceGrate", 120, 5.0, atlas=256)
    slots = [{"type": "rect", "center": (x, 0.0), "size": (0.9, 3.4), "radius": 0.08, "color": (14, 16, 20), "rough": 0.9, "wear": 0.0} for x in (-3.25, -1.95, -0.65, 0.65, 1.95, 3.25)]
    grate = Material("metal", color=(103, 119, 135), rough=0.45, polish=0.3, dirt=0.6, scratches=0.5, decals=slots + [
        {"type": "text", "text": "WR", "center": (0.0, 1.85), "height": 0.22, "color": (60, 66, 76), "font": "black", "wear": 0.3},
    ])
    rim = steel((60, 66, 76), dirt=0.6)
    a.add("Body", sh.rounded_box((7.6, 0.08, 3.6), 0.0, 1, grate, faces=["+y"]).transformed(T(0, 0.06, 0)))
    for z in (-1.9, 1.9):
        a.add("Body", sh.rounded_box((8.0, 0.1, 0.2), 0.0, 1, rim, faces=["+y", "+z", "-z", "+x", "-x"]).transformed(T(0, 0.05, z)))
    for x in (-3.9, 3.9):
        a.add("Body", sh.rounded_box((0.2, 0.1, 3.6), 0.0, 1, rim, faces=["+y", "+x", "-x"]).transformed(T(x, 0.05, 0)))
    landmark(a, IMMERSION, "MaintenanceGrate", fit="box")
    return a
