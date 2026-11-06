from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel
from _bay_lib import DESIGN
from _landmark_lib import landmark


def build():
    a = building_asset("DowntownServiceDetail", 700, 10.0, atlas=512)
    a.role("Glass", "glass", color=(140, 190, 220), transparency=0.55)
    frame = steel((47, 60, 75))
    bracket = steel((103, 119, 135))
    edge = panel((47, 60, 75), decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (15.0, 0.18), "color": (202, 140, 57), "wear": 0.3},
        {"type": "text", "text": "TRANSIT", "center": (-7.6, 0.0), "height": 0.16, "color": (220, 224, 230), "font": "black", "wear": 0.3},
    ])
    a.add("Body", sh.box((19.0, 0.3, 0.3), frame).transformed(T(0, 2.65, -1.4)))
    a.add("Body", sh.rounded_box((19.0, 0.45, 0.3), 0.04, 1, edge, faces=["+z", "+y", "-y", "+x", "-x"]).transformed(T(0, 2.55, 1.42)))
    for x in (-9.35, 0.0, 9.35):
        a.add("Body", sh.box((0.3, 0.3, 3.0), frame).transformed(T(x, 2.65, 0.0)))
    a.add("Glass", sh.box((18.4, 0.08, 2.7), None).transformed(T(0, 2.78, 0.0)))
    for x in (-8.0, 8.0):
        a.add("Body", sh.box((0.3, 2.5, 0.3), bracket).transformed(T(x, 1.25, -1.2)))
        a.add("Body", sh.box((0.22, 0.22, 3.0), bracket).transformed(compose(T(x, 1.5, -0.2), R(-50, 0, 0))))
    landmark(a, DESIGN, "DowntownService_Detail", fit="box")
    return a
