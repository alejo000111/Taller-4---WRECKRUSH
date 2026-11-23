import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

BLUE = (30, 128, 196)
NAVY = (18, 30, 56)
WHITE = (240, 240, 244)
YELLOW = (255, 210, 31)
RED = (232, 52, 44)
INK = (20, 20, 24)
GLASS = (120, 180, 210)

BOOTH = (7.0, 6.0, 4.4)
BOOTH_C = (0.0, 3.35, 0.6)
FRONT_Z = BOOTH_C[2] - BOOTH[2] / 2
ROOF_Y = BOOTH_C[1] + BOOTH[1] / 2


def interior_decals():
    shelves = [{"type": "rect", "center": (0.0, y), "size": (6.0, 0.06), "color": (70, 52, 36), "wear": 0.1} for y in (-1.95, -1.25, -0.55)]
    stock = []
    colors = [RED, YELLOW, (60, 200, 120), (166, 77, 255), WHITE, (255, 122, 26)]
    for row, y in enumerate((-2.2, -1.5, -0.8)):
        for k in range(12):
            x = -2.8 + k * 0.5 + 0.12 * (row % 2)
            stock.append({"type": "rect", "center": (x, y), "size": (0.34, 0.42), "color": colors[(k + row * 2) % len(colors)], "wear": 0.1})
    return [
        {"type": "rect", "center": (0.0, -1.5), "size": (6.3, 2.4), "color": (26, 28, 34), "wear": 0.0},
        *shelves, *stock,
        {"type": "circle", "center": (1.9, -1.05), "radius": 0.34, "color": (40, 34, 30), "wear": 0.0},
        {"type": "rect", "center": (1.9, -0.45), "size": (0.9, 0.7), "radius": 0.2, "color": (36, 70, 120), "wear": 0.0},
        {"type": "rect", "center": (0.0, 1.6), "size": (7.0, 0.05), "darken": 0.5, "raise": -0.005},
    ]


def side_ad(sign):
    return [
        {"type": "rect", "center": (0.0, 0.1), "size": (3.4, 3.6), "radius": 0.08, "color": YELLOW, "wear": 0.2},
        {"type": "rect", "center": (0.0, 0.1), "size": (3.4, 3.6), "radius": 0.08, "outline": 0.08, "color": INK, "wear": 0.2},
        {"type": "text", "text": "DAILY" if sign > 0 else "WRECK", "center": (0.0, -1.15), "height": 0.62, "color": INK, "font": "impact", "wear": 0.2},
        {"type": "text", "text": "WRECK" if sign > 0 else "TIMES", "center": (0.0, -0.45), "height": 0.62, "color": RED, "font": "impact", "wear": 0.2},
        {"type": "rect", "center": (0.0, 0.55), "size": (2.8, 1.1), "color": (60, 64, 74), "wear": 0.2},
        {"type": "text", "text": "CITY IN RUINS!", "center": (0.0, 0.55), "height": 0.3, "color": WHITE, "font": "impact", "wear": 0.2},
        {"type": "text", "text": "ONLY 50¢", "center": (0.0, 1.45), "height": 0.3, "color": INK, "font": "black", "wear": 0.2},
        *[{"type": "rect", "center": (0.0, y), "size": (7.0, 0.04), "darken": 0.35, "raise": -0.004} for y in (-2.4, 2.4)],
    ]


def back_decals():
    return [
        {"type": "rect", "center": (-2.2, 0.6), "size": (1.3, 4.2), "radius": 0.05, "outline": 0.04, "darken": 0.5, "raise": -0.006},
        {"type": "circle", "center": (-1.75, 0.6), "radius": 0.07, "color": (190, 194, 200), "metal": 1.0, "wear": 0.2},
        {"type": "rect", "center": (1.4, -1.6), "size": (2.0, 0.6), "color": (24, 26, 30), "wear": 0.1},
        *[{"type": "rect", "center": (1.4, -1.8 + k * 0.12), "size": (1.8, 0.04), "color": (110, 114, 122), "wear": 0.1} for k in range(4)],
        {"type": "text", "text": "STAFF ONLY", "center": (-2.2, -0.9), "height": 0.16, "color": WHITE, "font": "black", "wear": 0.3},
        *[{"type": "rect", "center": (x, 0.0), "size": (0.04, 6.0), "darken": 0.35, "raise": -0.004} for x in (-0.4, 3.1)],
    ]


def rack_covers(count, seed):
    rng = np.random.default_rng(seed)
    colors = [RED, YELLOW, (60, 200, 120), (166, 77, 255), (34, 225, 255), (255, 122, 26), WHITE]
    titles = ["BOOM", "CARS", "WRECK", "$$$", "TNT", "LOOT", "CHAOS", "SCRAP"]
    out = []
    width = 6.6 / count
    for k in range(count):
        x = -3.3 + (k + 0.5) * width
        col = colors[int(rng.integers(len(colors)))]
        out.append({"type": "rect", "center": (x, 0.0), "size": (width * 0.86, 0.62), "color": col, "wear": 0.15})
        out.append({"type": "text", "text": titles[int(rng.integers(len(titles)))], "center": (x, -0.18), "height": 0.15, "color": INK if col in (YELLOW, WHITE, (34, 225, 255)) else WHITE, "font": "impact", "wear": 0.15})
        out.append({"type": "rect", "center": (x, 0.12), "size": (width * 0.6, 0.22), "color": (40, 44, 52), "wear": 0.15})
    return out


def scallops(width, depth, count):
    pts = [(width / 2, 0.0), (-width / 2, 0.0)]
    step = width / count
    for i in range(count):
        x0 = -width / 2 + i * step
        for t in (0.0, 0.5):
            pts.append((x0 + t * step, -depth * (0.6 + 0.4 * np.sin(np.pi * t))))
    pts.append((width / 2, -depth * 0.6))
    return pts


def paper_bundle(mat, strap):
    stack = sh.rounded_box((0.62, 0.45, 1.0), 0.03, 1, mat, faces=["+x", "-x", "+y", "+z", "-z"])
    band = sh.rounded_box((0.66, 0.47, 0.07), 0.0, 1, strap, faces=["+x", "-x", "+y", "+z", "-z"])
    return [stack, band]


def build():
    a = Asset("NewsKiosk", budget=2500, atlas=1024, ao_radius=0.8, edge_width=0.07, preview_radius=6.2,
              views=[("FRONT 3/4", 215, 14), ("BACK 3/4", 35, 18), ("SIDE", 270, 6), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.55)
    a.role("Glow", "neon", color=YELLOW)

    paint = Material("paint", color=BLUE, under=(160, 164, 170), wear=0.25, scratches=0.35, rough=0.36, dirt=0.4, skin=False)
    booth = sh.rounded_box(BOOTH, 0.1, 1, paint, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={
        "-z": paint.but(decals=interior_decals()),
        "+x": paint.but(decals=side_ad(1)),
        "-x": paint.but(decals=side_ad(-1)),
        "+z": paint.but(decals=back_decals()),
    })
    a.add("Body", booth.transformed(T(*BOOTH_C)))

    concrete = Material("concrete", color=(176, 174, 168), dirt=0.55, decals=[
        {"type": "stripes", "center": (0.0, -2.75), "size": (8.6, 0.3), "width": 0.3, "color": YELLOW, "wear": 0.5},
    ])
    a.add("Body", sh.rounded_box((8.6, 0.35, 5.8), 0.06, 1, concrete, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 0.175, 0.1)))

    white = Material("paint", color=WHITE, under=(150, 152, 158), wear=0.3, scratches=0.3, rough=0.35, dirt=0.4, skin=False)
    frame_z = FRONT_Z - 0.06
    for y, size in ((5.92, (6.7, 0.18, 0.16)), (3.5, (6.7, 0.18, 0.16))):
        a.add("Body", sh.box(size, white).transformed(T(0, y, frame_z)))
    for x in (-3.28, -1.1, 1.1, 3.28):
        a.add("Body", sh.box((0.16, 2.6, 0.16), white).transformed(T(x, 4.71, frame_z)))
    a.add("Glass", sh.box((6.5, 2.3, 0.03), None).transformed(T(0, 4.71, FRONT_Z - 0.04)))

    wood = Material("wood", color=(186, 140, 70), axis="x", dirt=0.3)
    a.add("Body", sh.rounded_box((7.3, 0.22, 1.5), 0.04, 1, wood, faces=["+x", "-x", "+y", "-y", "-z"]).transformed(T(0, 3.42, FRONT_Z - 0.6)))
    counter = paint.but(decals=[
        {"type": "rect", "center": (0.0, 1.25), "size": (7.0, 0.2), "color": WHITE, "wear": 0.3},
        {"type": "text", "text": "NEWS • MAGS • SNACKS", "center": (0.0, -1.2), "height": 0.22, "color": WHITE, "font": "black", "wear": 0.3},
    ])
    a.add("Body", sh.rounded_box((7.0, 3.1, 1.2), 0.06, 1, paint, faces=["+x", "-x", "-z"], face_mats={"-z": counter}).transformed(T(0, 1.9, FRONT_Z - 0.6)))
    rack_mat = Material("metal", color=(170, 174, 182), rough=0.35, polish=0.6, dirt=0.3)
    for k, y in enumerate((1.25, 2.35)):
        covers = Material("plastic", color=(230, 230, 236), rough=0.3, decals=rack_covers(9, 11 + k))
        rack = sh.rounded_box((6.7, 0.75, 0.06), 0.0, 1, rack_mat, faces=["+x", "-x", "+y", "-y", "-z"], face_mats={"-z": covers})
        a.add("Body", rack.transformed(compose(T(0, y, FRONT_Z - 1.28), R(-14, 0, 0))))
        a.add("Body", sh.box((6.8, 0.06, 0.2), rack_mat).transformed(T(0, y - 0.38, FRONT_Z - 1.33)))

    roof = Material("paint", color=WHITE, under=(150, 152, 158), wear=0.3, scratches=0.3, rough=0.4, dirt=0.5, skin=False)
    a.add("Body", sh.rounded_box((7.8, 0.35, 5.4), 0.06, 1, roof).transformed(T(0, ROOF_Y + 0.17, 0.4)))

    canvas = Material("canvas", stripes=[BLUE, WHITE], stripe_width=0.62, axis=0, dirt=0.35)
    slope = sh.extrude([(0.0, 0.0), (1.7, -0.75), (1.7, -0.81), (0.0, -0.06)], 7.7, canvas, bevel=0.0, corner_radius=0.0)
    a.add("Body", slope.transformed(compose(T(0, ROOF_Y - 0.05, FRONT_Z + 0.05), R(0, 90, 0))))
    valance = sh.extrude(scallops(7.7, 0.42, 11), 0.05, canvas, bevel=0.0, corner_radius=0.0)
    a.add("Body", valance.transformed(T(0, ROOF_Y - 0.8, FRONT_Z - 1.68)))

    sign_face = Material("paint", color=INK, under=(150, 152, 158), wear=0.2, scratches=0.25, rough=0.4, dirt=0.3, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (5.7, 1.05), "radius": 0.1, "outline": 0.07, "color": YELLOW, "wear": 0.15},
        {"type": "text", "text": "NEWS", "center": (-0.75, 0.02), "height": 0.82, "color": YELLOW, "font": "impact", "wear": 0.15},
        {"type": "text", "text": "& MAGS", "center": (1.45, 0.06), "height": 0.4, "color": WHITE, "font": "impact", "wear": 0.15},
    ])
    sign = sh.rounded_box((6.0, 1.3, 0.3), 0.05, 1, roof, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"-z": sign_face, "+z": sign_face})
    a.add("Body", sign.transformed(T(0, ROOF_Y + 1.0, 0.0)))
    for x in (-2.4, 2.4):
        a.add("Body", sh.box((0.14, 0.4, 0.14), rack_mat).transformed(T(x, ROOF_Y + 0.4, 0.0)))
    a.add("Glow", sh.box((6.1, 0.1, 0.22), None).transformed(T(0, ROOF_Y + 1.7, 0.0)))

    paper = Material("paint", color=(226, 222, 206), under=(200, 196, 180), wear=0.0, scratches=0.0, rough=0.8, dirt=0.4, skin=False, decals=[
        *[{"type": "rect", "center": (0.0, y), "size": (1.2, 0.02), "darken": 0.25, "raise": -0.003} for y in np.linspace(-0.22, 0.22, 7)],
        {"type": "text", "text": "WRECK TIMES", "center": (0.0, 0.0), "height": 0.12, "color": INK, "font": "black", "wear": 0.2},
    ])
    twine = Material("wrap", color=(170, 140, 90), width=0.04, slope=0.0, dirt=0.3)
    for x, z, yaw, layers in ((3.92, -1.7, 6, 2), (-3.92, -1.9, -5, 1), (-3.9, 1.9, 4, 2), (3.9, 2.1, -6, 1)):
        for i in range(layers):
            for part in paper_bundle(paper, twine):
                a.add("Body", part.transformed(compose(T(x, 0.35 + 0.225 + i * 0.45, z), R(0, yaw + i * 7, 0))))

    destructible(a, "Downtown")
    collider(a, "Hitbox", (7.2, 6.4, 4.6), (0, 3.4, 0.6))
    collider(a, "Counter", (7.2, 3.5, 1.5), (0, 1.75, FRONT_Z - 0.65))
    collider(a, "Base", (8.6, 0.35, 5.8), (0, 0.175, 0.1))
    return a
