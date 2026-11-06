import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _station_lib import station, collider, platform, sign_face, steel, painted, YELLOW, INK

ORANGE = (255, 122, 26)
WALL_Z = 1.9


def pegboard_material():
    holes = []
    for x in np.linspace(-4.4, 4.4, 23):
        for y in np.linspace(-3.2, 3.2, 17):
            holes.append((x, y))
    decals = [{"type": "rivets", "points": holes, "radius": 0.05, "color": (24, 20, 16), "height": -0.006}]
    outlines = [
        ((-4.0, -2.2), (0.35, 2.0), 0), ((-3.5, -2.6), (0.9, 0.4), 0),
        ((4.0, -2.0), (0.3, 2.4), 25), ((3.4, 2.2), (2.2, 0.6), -10),
        ((-3.8, 2.4), (0.25, 1.6), 0), ((-1.4, 2.6), (1.8, 0.25), 0),
    ]
    for center, size, angle in outlines:
        decals.append({"type": "rect", "center": center, "size": size, "radius": 0.08, "outline": 0.05, "color": (250, 250, 250), "angle": angle, "wear": 0.3})
    return Material("wood", color=(150, 112, 70), axis="x", ring_freq=4.0, dirt=0.35, decals=decals)


def hammer(handle_mat, head_mat, length=4.2):
    parts = [sh.cylinder(0.22, length, handle_mat, bevel=0.04, segments=8).transformed(T(0, length / 2, 0))]
    parts.append(sh.cylinder(0.27, 0.9, Material("rubber", color=(30, 30, 34), pattern="ribs", freq=14.0), bevel=0.04, segments=8).transformed(T(0, 0.5, 0)))
    head = sh.rounded_box((1.8, 0.95, 0.95), 0.12, 1, head_mat)
    parts.append(head.transformed(T(0, length + 0.35, 0)))
    face = sh.cylinder(0.45, 0.25, head_mat, bevel=0.05, segments=10).transformed(compose(T(1.0, length + 0.35, 0), R(0, 0, 90)))
    parts.append(face)
    return parts


def build():
    a = Asset("ToolRack", budget=4500, atlas=1024, ao_radius=0.9, edge_width=0.07, preview_radius=7.8,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("FRONT", 180, 6), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=ORANGE)
    station(a, "ToolRack")
    platform(a, ORANGE)

    frame = steel()
    beam = painted(YELLOW, [{"type": "stripes", "center": (0.0, 3.6), "size": (1.0, 1.4), "width": 0.25, "color": INK, "wear": 0.3}])
    for x in (-5.2, 5.2):
        post = sh.extrude([(-0.4, -0.4), (0.4, -0.4), (0.4, -0.28), (0.1, -0.28), (0.1, 0.28), (0.4, 0.28), (0.4, 0.4), (-0.4, 0.4), (-0.4, 0.28), (-0.1, 0.28), (-0.1, -0.28), (-0.4, -0.28)], 9.2, beam, bevel=0.02, corner_radius=0.0)
        a.add("Body", post.transformed(compose(T(x, 4.8, WALL_Z - 0.3), R(90, 0, 0))))
    a.add("Body", sh.rounded_box((9.6, 7.2, 0.3), 0.04, 1, frame, face_mats={"-z": pegboard_material(), "+z": painted((54, 56, 64), [{"type": "text", "text": "WRECK TOOLS", "center": (0.0, 0.0), "height": 1.0, "color": (90, 94, 104), "font": "impact", "wear": 0.3}])}).transformed(T(0, 4.8, WALL_Z)))
    a.add("Body", sh.box((10.0, 0.25, 0.5), frame).transformed(T(0, 1.15, WALL_Z - 0.1)))
    a.add("Body", sh.rounded_box((11.4, 1.7, 0.7), 0.08, 1, frame, face_mats={"-z": sign_face("TOOLS", ORANGE, (11.4, 1.7), sub=None)}).transformed(T(0, 9.6, WALL_Z - 0.3)))
    a.add("Glow", sh.box((11.0, 0.12, 0.12), None).transformed(T(0, 8.65, WALL_Z - 0.55)))

    hooks = steel((120, 124, 132))
    heads = [painted((235, 96, 30)), painted(YELLOW), painted((120, 150, 110))]
    wood = Material("wood", color=(120, 70, 40), axis="y", dirt=0.3)
    for k, x in enumerate((-2.9, 0.0, 2.9)):
        tilt = (-4, 3, -2)[k]
        for part in hammer(wood, heads[k], 3.6):
            a.add("Body", part.transformed(compose(T(x, 2.1, WALL_Z - 0.75), R(0, 0, tilt))))
        a.add("Body", sh.cylinder(0.08, 0.6, hooks, bevel=0.0, segments=6).transformed(compose(T(x, 6.2, WALL_Z - 0.4), R(90, 0, 0))))

    top = Material("wood", color=(132, 90, 54), axis="x", ring_freq=5.0, dirt=0.45, decals=[
        {"type": "circle", "center": (-2.2, 0.3), "radius": 0.5, "darken": 0.25, "raise": 0.0},
        {"type": "rect", "center": (1.0, -0.4), "size": (1.8, 0.1), "angle": 20, "darken": 0.3, "raise": -0.004},
    ])
    a.add("Body", sh.rounded_box((8.4, 0.4, 3.0), 0.06, 1, top).transformed(T(0, 2.85, -2.5)))
    drawers = painted((62, 66, 76), [
        *[{"type": "rect", "center": (x, y), "size": (1.7, 0.6), "radius": 0.05, "outline": 0.04, "darken": 0.5, "raise": -0.006} for x in (-2.8, -0.9) for y in (-0.5, 0.25)],
        *[{"type": "rect", "center": (x, y), "size": (0.6, 0.1), "radius": 0.05, "color": (190, 194, 200), "metal": 1.0, "wear": 0.2} for x in (-2.8, -0.9) for y in (-0.5, 0.25)],
    ])
    a.add("Body", sh.rounded_box((4.2, 2.2, 2.6), 0.05, 1, painted((62, 66, 76)), faces=["+x", "-x", "+y", "-z", "+z"], face_mats={"-z": drawers}).transformed(T(-1.9, 1.55, -2.5)))
    for x in (3.8,):
        for z in (-3.7, -1.3):
            a.add("Body", sh.box((0.25, 2.45, 0.25), frame).transformed(T(x, 1.42, z)))
    a.add("Body", sh.box((0.25, 0.2, 2.6), frame).transformed(T(3.8, 0.6, -2.5)))

    vise = steel((44, 70, 120))
    a.add("Body", sh.rounded_box((1.2, 0.8, 1.0), 0.08, 1, vise).transformed(T(-3.4, 3.45, -3.4)))
    a.add("Body", sh.rounded_box((1.2, 0.8, 0.4), 0.06, 1, vise).transformed(T(-3.4, 3.45, -4.15)))
    a.add("Body", sh.cylinder(0.08, 1.4, steel((170, 174, 182)), bevel=0.0, segments=6).transformed(compose(T(-3.4, 3.3, -4.5), R(0, 0, 90))))
    box = painted((200, 40, 36), [{"type": "rect", "center": (0.0, 0.0), "size": (1.6, 0.08), "darken": 0.5, "raise": -0.004}])
    a.add("Body", sh.rounded_box((2.0, 0.9, 1.0), 0.08, 1, box).transformed(T(2.4, 3.5, -2.2)))
    a.add("Body", sh.sweep([(1.8, 3.95, -2.2), (1.9, 4.35, -2.2), (2.9, 4.35, -2.2), (3.0, 3.95, -2.2)], 0.06, 4, steel((170, 174, 182)), samples=6))
    lamp = steel((40, 42, 48))
    a.add("Body", sh.sweep([(4.4, 3.05, -1.6), (4.4, 4.6, -1.6), (3.6, 5.4, -2.2)], 0.07, 5, lamp, samples=6))
    shade = sh.lathe([(0.0, 0.0), (0.2, 0.0), (0.55, -0.45), (0.5, -0.5), (0.0, -0.1)], 10, lamp, smooth_angle=40)
    a.add("Body", shade.transformed(T(3.5, 5.55, -2.3)))
    a.add("Glow", sh.lathe([(0.45, -0.46), (0.0, -0.3)], 10, None, smooth_angle=40).transformed(T(3.5, 5.55, -2.3)))

    collider(a, "Bench", (8.4, 2.9, 3.0), (0, 1.65, -2.5))
    collider(a, "Wall", (11.2, 9.6, 1.0), (0, 4.8, WALL_Z - 0.3))
    a.point("prompt", (0, 4.8, WALL_Z - 0.4))
    return a
