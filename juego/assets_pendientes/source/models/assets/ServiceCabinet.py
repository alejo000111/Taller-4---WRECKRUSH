from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel
from _bay_lib import DESIGN
from _landmark_lib import landmark, box_collider


def build():
    a = building_asset("ServiceCabinet", 800, 4.0, atlas=512)
    body = panel((47, 60, 75), decals=[
        {"type": "rect", "center": (0.0, -2.1), "size": (2.6, 0.4), "color": (202, 140, 57), "wear": 0.4},
        {"type": "text", "text": "TOOLS", "center": (0.0, -2.1), "height": 0.3, "color": (20, 22, 26), "font": "black", "wear": 0.3},
    ])
    drawer = panel((103, 119, 135))
    dark = steel((25, 32, 44))
    rust = Material("rust", amount=0.5, steel=(139, 80, 48))
    rubber = Material("rubber", color=(30, 30, 32), pattern="ribs", freq=8.0)

    a.add("Body", sh.rounded_box((3.4, 0.4, 2.4), 0.05, 1, dark).transformed(T(0, 0.2, -0.06)))
    a.add("Body", sh.rounded_box((3.0, 5.0, 2.0), 0.08, 1, body, faces=["+z", "+x", "-x", "-z", "+y"]).transformed(T(0, 2.9, -0.06)))
    for y in (4.35, 3.1, 1.85):
        a.add("Body", sh.rounded_box((2.7, 1.1, 0.12), 0.03, 1, drawer, faces=["+z", "+x", "-x", "+y", "-y"]).transformed(T(0, y, 1.0)))
        a.add("Body", sh.box((1.0, 0.12, 0.18), dark).transformed(T(0, y + 0.2, 1.12)))
    a.add("Body", sh.box((1.0, 0.4, 0.3), rust).transformed(T(0, 5.6, 0.54)))
    a.add("Body", sh.torus(0.42, 0.12, rubber, segments=10, sides=4).transformed(compose(T(1.3, 4.6, 1.0), R(90, 0, 0))))
    a.add("Body", sh.cylinder(0.08, 0.6, dark, bevel=0.0, segments=5).transformed(compose(T(1.3, 5.0, 0.8), R(90, 0, 0))))
    landmark(a, DESIGN, ["ServiceCabinet_1", "ServiceCabinet_2"], fit="box",
             colliders=[box_collider("Cabinet", (3.4, 5.4, 2.4), (0, 2.7, -0.06))])
    return a
