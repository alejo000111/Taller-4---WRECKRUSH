from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel, panel, louvre, IMMERSION
from _landmark_lib import landmark, box_collider
import _city_lib

AMBER = (230, 150, 50)


def build():
    a = building_asset("ReclamationDepot", 2600, 42.0)
    a.role("Glow", "neon", color=AMBER)
    a.views = [("FRONT 3/4", 215, 14), ("FRONT", 180, 4), ("SIDE", 270, 6), ("TOP", 200, 50)]
    windows = [{"type": "rect", "center": (x, 2.5), "size": (7.0, 6.0), "color": (220, 130, 20), "rough": 0.1, "metal": 0.0, "wear": 0.0} for x in (-26.0, 26.0)]
    shell = Material("corrugated", color=(75, 95, 125), under=(120, 110, 100), pitch=0.6, axis=0, depth=0.06, wear=0.4, scratches=0.4, rough=0.45, dirt=0.5, skin=False, decals=windows)
    plain = shell.but(decals=[])
    roller = Material("corrugated", color=(90, 110, 135), under=(120, 110, 100), pitch=0.45, axis=1, depth=0.05, wear=0.45, scratches=0.4, rough=0.5, dirt=0.5, skin=False, decals=[
        {"type": "rect", "center": (0.0, 4.6), "size": (27.6, 0.9), "color": (255, 196, 30), "wear": 0.5},
    ])
    roof = steel((50, 65, 85))
    frame = steel((45, 55, 65))
    brick = Material("city_brick", color=(84, 72, 74), mortar=(120, 116, 110), brick=(1.0, 0.4), gap=0.05, wear=0.3, soot=0.3, dirt=0.5)
    board = Material("paint", color=(240, 245, 250), under=(140, 140, 146), wear=0.3, scratches=0.3, rough=0.4, dirt=0.45, skin=False)
    awning = panel((75, 95, 125))
    hazard = Material("hazard", color=(255, 196, 30), color2=(24, 24, 28), width=0.4, angle=45, wear=0.45, dirt=0.45)

    a.add("Body", sh.rounded_box((71.0, 20.0, 10.0), 0.0, 1, shell, faces=["-z", "+x", "-x", "+z"], face_mats={"+x": plain, "-x": plain, "+z": plain}).transformed(T(0, 10.0, 0.25)))
    a.add("Body", sh.rounded_box((74.0, 1.0, 14.0), 0.05, 1, roof, faces=["-z", "+x", "-x", "+z", "+y", "-y"]).transformed(T(0, 20.5, 0.25)))
    a.add("Body", sh.rounded_box((66.0, 3.0, 10.0), 0.0, 1, plain, faces=["-z", "+x", "-x", "+z"]).transformed(T(0, 22.5, 0.25)))
    a.add("Body", [p.transformed(T(x, 22.5, -4.85)) for x in (-16.0, 0.0, 16.0) for p in louvre(12.0, 2.0, 3, frame, frame)])
    a.add("Body", sh.rounded_box((70.0, 1.5, 12.0), 0.05, 1, roof, faces=["-z", "+x", "-x", "+z", "+y", "-y"]).transformed(T(0, 24.75, 0.25)))
    a.add("Body", sh.box((28.0, 13.0, 0.5), roller).transformed(T(0, 6.5, -5.0)))
    for x in (-14.4, 14.4):
        a.add("Body", sh.box((0.8, 14.0, 0.8), hazard).transformed(T(x, 7.0, -5.1)))
    a.add("Body", sh.box((29.6, 1.0, 0.8), frame).transformed(T(0, 13.4, -5.1)))
    slope = sh.extrude([(0.0, 0.0), (2.6, -0.8), (2.6, -1.0), (0.0, -0.25)], 30.0, awning, bevel=0.0, corner_radius=0.0)
    a.add("Body", slope.transformed(compose(T(0, 14.6, -4.75), R(0, 90, 0))))
    for x in (-13.0, 13.0):
        a.add("Body", sh.box((0.2, 0.2, 3.4), frame).transformed(compose(T(x, 15.1, -6.2), R(-22, 0, 0))))
    a.add("Body", sh.rounded_box((22.4, 3.4, 0.4), 0.05, 1, frame).transformed(T(0, 17.0, -4.95)))
    a.add("Body", sh.box((22.0, 3.0, 0.2), board).transformed(T(0, 17.0, -5.25)))
    for x in (-25.0, 25.0):
        a.add("Body", sh.rounded_box((22.0, 3.5, 2.0), 0.06, 1, brick, faces=["-z", "+x", "-x", "+y"]).transformed(T(x, 1.75, -4.75)))
        hedge = sh.rounded_box((21.0, 1.3, 1.6), 0.5, 1, Material("canvas", stripes=[(52, 104, 50), (62, 120, 58)], stripe_width=0.35, dirt=0.3))
        a.add("Body", hedge.transformed(T(x, 4.05, -4.75)))
        wx = -26.0 if x < 0 else 26.0
        for dx, dy, sx, sy in ((0, 3.25, 8.0, 0.5), (0, -3.25, 8.0, 0.5), (-3.75, 0, 0.5, 6.0), (3.75, 0, 0.5, 6.0)):
            a.add("Body", sh.box((sx, sy, 0.6), frame).transformed(T(wx + dx, 7.5 + dy, -4.9)))
        a.add("Glow", sh.box((8.4, 0.25, 0.2), None).transformed(T(wx, 11.1, -5.15)))
        a.add("Glow", sh.box((0.25, 6.8, 0.2), None).transformed(T(wx + (4.2 if x < 0 else -4.2), 7.5, -5.15)))
    for x in (-23.0, 23.0):
        a.add("Body", sh.rounded_box((6.0, 3.0, 4.0), 0.08, 1, panel((35, 40, 50)), faces=["-z", "+x", "-x", "+z", "+y"]).transformed(T(x, 26.5 + 1.5 - 1.0, 0.25)))
        a.add("Body", [p.transformed(T(x, 27.0, -1.85)) for p in louvre(5.0, 2.2, 3, frame, frame)])
    landmark(a, IMMERSION, "ReclamationDepot", fit="box", keep=["SignText"],
             colliders=[box_collider("Shell", (71.0, 21.0, 10.0), (0, 10.5, 0.25)), box_collider("Roof", (70.0, 4.5, 12.0), (0, 23.25, 0.25))])
    return a
