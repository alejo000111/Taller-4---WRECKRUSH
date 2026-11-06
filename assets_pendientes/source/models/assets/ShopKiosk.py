import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh

YELLOW = (255, 210, 31)
CHARCOAL = (42, 44, 52)
SCREEN_CENTER = (0.0, 6.8, 3.7)


def i_beam(height, mat):
    w, f, t = 0.32, 0.1, 0.07
    poly = [(-w, -w), (w, -w), (w, -w + f), (t, -w + f), (t, w - f), (w, w - f), (w, w), (-w, w), (-w, w - f), (-t, w - f), (-t, -w + f), (-w, -w + f)]
    return sh.extrude(poly, height, mat, bevel=0.02, corner_radius=0.0).transformed(R(-90, 0, 0))


def scallop_strip(width, depth, count):
    pts = [(width / 2, 0.0), (-width / 2, 0.0)]
    step = width / count
    for i in range(count):
        x0 = -width / 2 + i * step
        for t in (0.0, 0.25, 0.5, 0.75):
            x = x0 + t * step
            y = -depth * (0.55 + 0.45 * np.sin(np.pi * t))
            pts.append((x, y))
    pts.append((width / 2, -depth * 0.55))
    return pts


def build():
    a = Asset("ShopKiosk", budget=9000, atlas=1024, ao_radius=1.1, edge_width=0.12, preview_radius=9.0,
              views=[("FRONT 3/4", 215, 14), ("FRONT", 180, 6), ("SIDE", 270, 10), ("COUNTER", 200, 28)])
    a.role("Structure", "surface")
    a.role("Awning", "surface")
    a.role("Props", "surface")
    a.role("Screen", "surface")
    a.role("Glow", "neon", color=YELLOW)

    steel = Material("metal", color=(70, 74, 84), rough=0.4, polish=0.6, dirt=0.4, skin=False)
    deck = Material("diamondplate", color=(78, 82, 92), pitch=0.45, dirt=0.45)
    wall = Material("corrugated", color=CHARCOAL, pitch=0.42, axis=0, depth=0.05, wear=0.3, dirt=0.35, skin=False)
    beam = Material("paint", color=YELLOW, wear=0.45, scratches=0.4, dirt=0.4, skin=False)
    plate = Material("metal", color=(60, 62, 70), rough=0.42, dirt=0.45, skin=False, decals=[
        {"type": "rivets", "points": [(-0.36, -0.36), (0.36, -0.36), (-0.36, 0.36), (0.36, 0.36)], "radius": 0.06, "height": 0.018},
    ])
    counter_front = Material("paint", color=CHARCOAL, wear=0.35, dirt=0.35, skin=False, decals=[
        {"type": "stripes", "center": (0.0, -1.42), "size": (9.8, 0.42), "width": 0.32, "color": YELLOW, "wear": 0.4},
        {"type": "stripes", "center": (0.0, 1.42), "size": (9.8, 0.42), "width": 0.32, "color": YELLOW, "wear": 0.4},
        {"type": "rect", "center": (0.0, 0.0), "size": (4.6, 1.3), "radius": 0.12, "color": (24, 24, 28), "wear": 0.3},
        {"type": "text", "text": "SHOP", "center": (0.0, 0.02), "height": 0.95, "color": YELLOW, "font": "impact", "wear": 0.3},
        {"type": "rivets", "points": [(x, y) for x in (-4.7, -2.6, 2.6, 4.7) for y in (-0.9, 0.9)], "radius": 0.07, "color": (150, 152, 160), "height": 0.02},
    ])
    counter_side = Material("paint", color=CHARCOAL, wear=0.35, dirt=0.35, skin=False)
    top = Material("metal", color=(150, 154, 164), rough=0.3, polish=0.8, brushed=True, dirt=0.3, skin=False)
    canvas = Material("canvas", stripes=[YELLOW, (22, 22, 26)], stripe_width=1.0, axis=0, dirt=0.35)
    sign_face = Material("paint", color=(24, 24, 28), wear=0.25, dirt=0.25, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (6.6, 1.1), "radius": 0.1, "color": YELLOW, "outline": 0.08, "wear": 0.2},
        {"type": "text", "text": "WRECK MART", "center": (0.0, 0.02), "height": 0.72, "color": YELLOW, "font": "impact", "wear": 0.3},
    ])
    bezel = Material("metal", color=(30, 32, 38), rough=0.35, polish=0.6, dirt=0.25, skin=False)
    screen = Material("screen", color=(10, 14, 22))
    wood = Material("wood", color=(150, 104, 60), axis="x", dirt=0.4, decals=[
        {"type": "text", "text": "FRAGILE", "center": (0.0, 0.0), "height": 0.22, "color": (180, 40, 30), "font": "impact", "wear": 0.4},
    ])
    cash_top = Material("paint", color=(84, 196, 92), wear=0.1, dirt=0.15, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (0.22, 0.62), "color": (236, 226, 196), "wear": 0.1},
        {"type": "text", "text": "$", "center": (0.3, 0.0), "height": 0.3, "color": (40, 110, 50), "font": "black", "wear": 0.1},
        {"type": "text", "text": "$", "center": (-0.3, 0.0), "height": 0.3, "color": (40, 110, 50), "font": "black", "wear": 0.1},
    ])
    cash_side = Material("canvas", stripes=[(84, 196, 92), (64, 156, 72)], stripe_width=0.035, axis=1, dirt=0.1)
    gold = Material("gold", color=(255, 196, 64), rough=0.25)
    register = Material("plastic", color=(56, 60, 70), rough=0.4, skin=False)
    keypad = Material("plastic", color=(56, 60, 70), rough=0.4, skin=False, decals=[
        {"type": "rect", "center": (-0.3 + (k % 3) * 0.3, -0.2 + (k // 3) * 0.2), "size": (0.22, 0.14), "radius": 0.03, "color": (220, 220, 226), "wear": 0.3} for k in range(9)
    ])
    lcd = Material("screen", color=(20, 60, 30))

    a.add("Structure", sh.rounded_box((12.0, 0.4, 10.0), 0.06, 1, steel, face_mats={"+y": deck}))
    for x0, z0, sx, sz in ((0, -5.0, 12.05, 0.09), (0, 5.0, 12.05, 0.09), (-6.0, 0, 0.09, 10.05), (6.0, 0, 0.09, 10.05)):
        a.add("Glow", sh.box((sx, 0.09, sz), None).transformed(T(x0, 0.2, z0)))

    a.add("Structure", sh.rounded_box((11.4, 10.2, 0.6), 0.08, 1, steel, face_mats={"-z": wall}).transformed(T(0, 5.3, 4.3)))
    for side in (-1, 1):
        a.add("Structure", sh.rounded_box((0.5, 10.2, 3.4), 0.06, 1, steel, face_mats={("+x" if side > 0 else "-x"): wall, ("-x" if side > 0 else "+x"): wall}).transformed(T(side * 5.45, 5.3, 2.4)))
    a.add("Structure", sh.rounded_box((11.8, 0.4, 4.6), 0.08, 1, steel).transformed(T(0, 10.6, 2.3)))

    for x in (-5.55, 5.55):
        a.add("Structure", i_beam(10.0, beam).transformed(T(x, 5.2, -4.2)))
        a.add("Structure", sh.box((1.0, 0.12, 1.0), plate).transformed(T(x, 0.26, -4.2)))

    a.add("Structure", sh.rounded_box((10.0, 3.4, 2.6), 0.08, 1, counter_side, face_mats={"-z": counter_front}).transformed(T(0, 1.9, -2.4)))
    a.add("Structure", sh.rounded_box((10.5, 0.24, 3.0), 0.05, 1, top).transformed(T(0, 3.72, -2.4)))
    a.add("Glow", sh.box((10.4, 0.07, 0.07), None).transformed(T(0, 3.58, -3.92)))

    tilt = np.degrees(np.arctan2(1.4, 6.4))
    a.add("Awning", sh.rounded_box((12.2, 0.12, 6.6), 0.03, 1, canvas).transformed(compose(T(0, 9.62, -2.1), R(-tilt, 0, 0))))
    valance = sh.extrude(scallop_strip(12.2, 0.55, 14), 0.06, canvas, bevel=0.0, corner_radius=0.0)
    a.add("Awning", valance.transformed(T(0, 8.92, -5.42)))
    a.add("Structure", sh.cylinder(0.08, 12.3, steel, bevel=0.0, segments=8).transformed(compose(T(0, 8.94, -5.36), R(0, 0, 90))))
    for x in (-5.55, 5.55):
        a.add("Structure", sh.sweep([(x, 6.6, -4.2), (x, 8.0, -4.8), (x, 8.9, -5.32)], 0.07, 6, steel, samples=6))

    a.add("Structure", sh.rounded_box((7.2, 1.5, 0.5), 0.06, 1, steel, face_mats={"-z": sign_face}).transformed(T(0, 11.6, 1.2)))
    for x0, y0, sx, sy in ((0, 12.38, 7.3, 0.08), (0, 10.82, 7.3, 0.08), (-3.64, 11.6, 0.08, 1.64), (3.64, 11.6, 0.08, 1.64)):
        a.add("Glow", sh.box((sx, sy, 0.08), None).transformed(T(x0, y0, 0.93)))

    a.add("Screen", sh.rounded_box((7.5, 3.5, 0.24), 0.05, 1, bezel, face_mats={"-z": screen}).transformed(T(SCREEN_CENTER[0], SCREEN_CENTER[1], SCREEN_CENTER[2] + 0.12)))
    a.add("Screen", sh.sweep([(3.9, 5.2, 3.95), (4.3, 3.0, 3.98), (4.4, 0.4, 3.98)], 0.06, 4, Material("rubber", color=(24, 24, 28)), samples=6))

    a.add("Props", sh.rounded_box((1.9, 0.8, 1.3), 0.06, 1, register).transformed(T(3.0, 4.24, -2.3)))
    a.add("Props", sh.rounded_box((1.4, 0.12, 0.9), 0.03, 1, register, face_mats={"+y": keypad}).transformed(compose(T(3.0, 4.72, -2.45), R(-18, 0, 0))))
    a.add("Props", sh.rounded_box((1.0, 0.55, 0.12), 0.03, 1, register, face_mats={"-z": lcd}).transformed(compose(T(3.0, 5.0, -1.9), R(10, 0, 0))))
    for dx, dz, level in ((-3.2, -2.5, 0), (-3.2, -2.5, 1), (-2.0, -2.2, 0), (-3.2, -2.5, 2), (-2.0, -2.2, 1)):
        brick = sh.rounded_box((1.0, 0.3, 0.62), 0.0, 1, cash_side, face_mats={"+y": cash_top})
        a.add("Props", brick.transformed(compose(T(dx + level * 0.05, 4.0 + level * 0.3, dz), R(0, level * 9, 0))))
    for dx, dz, h in ((-0.6, -2.0, 0.08), (-0.45, -2.15, 0.16), (-0.75, -2.25, 0.1)):
        a.add("Props", sh.cylinder(0.26, h, gold, bevel=0.02, segments=10).transformed(T(dx, 3.84 + h / 2, dz)))
    for x, z, s in ((-4.5, 2.9, 1.3), (4.4, 3.0, 1.1), (4.7, 2.0, 0.8)):
        a.add("Props", sh.rounded_box((s, s, s), 0.05, 1, wood).transformed(compose(T(x, 0.2 + s / 2, z), R(0, 12 * x, 0))))

    shade_mat = Material("metal", color=(40, 42, 50), rough=0.4, polish=0.6, dirt=0.3, skin=False)
    for x in (-3.2, 0.0, 3.2):
        a.add("Structure", sh.cylinder(0.03, 1.3, shade_mat, bevel=0.0, segments=6).transformed(T(x, 8.75, -3.3)))
        shade = sh.lathe([(0.1, -0.06), (0.5, -0.34), (0.58, -0.38), (0.55, -0.32), (0.12, 0.0)], 14, shade_mat, closed=False, smooth_angle=35)
        a.add("Structure", shade.transformed(T(x, 8.12, -3.3)))
        a.add("Glow", sh.sphere(0.17, None, 10, 6).transformed(T(x, 7.86, -3.3)))
    open_face = Material("paint", color=(18, 18, 22), wear=0.2, skin=False, decals=[
        {"type": "text", "text": "OPEN", "center": (0.0, -0.12), "height": 0.42, "color": (255, 59, 160), "font": "impact", "wear": 0.0},
        {"type": "text", "text": "24/7", "center": (0.0, 0.3), "height": 0.22, "color": (34, 225, 255), "font": "impact", "wear": 0.0},
    ])
    a.add("Props", sh.rounded_box((1.5, 1.0, 0.12), 0.03, 1, shade_mat, face_mats={"-z": open_face}).transformed(T(5.55, 6.4, -4.6)))
    for x0, y0, sx, sy in ((5.55, 6.92, 1.56, 0.05), (5.55, 5.88, 1.56, 0.05), (4.79, 6.4, 0.05, 1.06), (6.31, 6.4, 0.05, 1.06)):
        a.add("Glow", sh.box((sx, sy, 0.05), None).transformed(T(x0, y0, -4.68)))
    shelf_mat = Material("metal", color=(90, 94, 104), rough=0.4, polish=0.6, dirt=0.35, skin=False)
    label_colors = [(255, 59, 59), (34, 225, 255), (255, 210, 31), (166, 77, 255), (80, 220, 110)]
    for side in (-1, 1):
        x = side * 4.85
        for k, y in enumerate((2.6, 4.2, 5.8)):
            a.add("Structure", sh.box((0.7, 0.08, 2.6), shelf_mat).transformed(T(x, y, 2.5)))
            for j in range(4):
                z = 1.55 + j * 0.62
                col = label_colors[(k * 4 + j + (side > 0)) % len(label_colors)]
                if (j + k) % 2 == 0:
                    can = Material("plastic", color=col, rough=0.35, skin=False, decals=[{"type": "rect", "center": (0.3, 0.25), "size": (3.0, 0.12), "color": (240, 240, 240), "wear": 0.2}])
                    a.add("Props", sh.cylinder(0.17, 0.5, can, bevel=0.02, segments=10).transformed(T(x, y + 0.3, z)))
                else:
                    box_mat = Material("paint", color=col, wear=0.25, dirt=0.2, skin=False, decals=[{"type": "rect", "center": (0.0, 0.0), "size": (0.24, 0.24), "radius": 0.04, "color": (24, 24, 28), "wear": 0.1}])
                    a.add("Props", sh.rounded_box((0.42, 0.56, 0.42), 0.03, 1, box_mat).transformed(T(x, y + 0.32, z)))
    ac_face = Material("metal", color=(170, 174, 184), rough=0.4, polish=0.6, dirt=0.4, skin=False, decals=[
        {"type": "circle", "center": (0.0, 0.0), "radius": 0.5, "color": (40, 42, 48), "outline": 0.05, "wear": 0.2},
        {"type": "circle", "center": (0.0, 0.0), "radius": 0.12, "color": (40, 42, 48), "wear": 0.1},
    ])
    a.add("Structure", sh.rounded_box((2.2, 1.0, 1.4), 0.06, 1, shelf_mat, face_mats={"+y": ac_face}).transformed(T(-2.8, 11.3, 3.2)))
    a.add("Structure", sh.sweep([(-1.7, 11.0, 3.6), (-1.0, 10.95, 3.9), (-0.6, 10.82, 4.1)], 0.07, 6, shade_mat, samples=6))
    bin_mat = Material("paint", color=(46, 120, 70), wear=0.4, dirt=0.4, skin=False, decals=[{"type": "text", "text": "SCRAP", "center": (2.3, 0.5), "height": 0.22, "color": (240, 240, 240), "font": "impact", "wear": 0.3}])
    a.add("Props", sh.lathe([(0.0, 0.0), (0.42, 0.0), (0.48, 1.2), (0.5, 1.25), (0.0, 1.25)], 14, bin_mat).transformed(T(-6.6, -0.2, -3.4)))
    a.add("Props", sh.lathe([(0.0, 0.0), (0.54, 0.0), (0.52, 0.1), (0.3, 0.2), (0.0, 0.22)], 14, shade_mat).transformed(T(-6.6, 1.05, -3.4)))
    mat_face = Material("canvas", stripes=[(30, 30, 36), (40, 40, 48)], stripe_width=0.2, axis=0, decals=[
        {"type": "text", "text": "WELCOME WRECKER", "center": (0.0, 0.0), "height": 0.32, "angle": 180, "color": (255, 210, 31), "font": "impact", "wear": 0.5},
    ])
    a.add("Props", sh.rounded_box((5.0, 0.05, 1.5), 0.02, 1, mat_face).transformed(T(0, 0.22, -5.85)))
    for side in (-1, 1):
        face = "+x" if side > 0 else "-x"
        poster = Material("paint", color=(20, 20, 26), wear=0.3, skin=False, decals=[
            {"type": "rect", "center": (0.0, 0.0), "size": (1.6, 2.4), "radius": 0.08, "color": (166, 77, 255) if side > 0 else (255, 122, 26), "wear": 0.3},
            {"type": "text", "text": "2X" if side > 0 else "NEW", "center": (0.0, -0.45), "height": 0.7, "color": (255, 255, 255), "font": "impact", "wear": 0.3},
            {"type": "text", "text": "CASH" if side > 0 else "TOOLS", "center": (0.0, 0.45), "height": 0.4, "color": (255, 210, 31), "font": "impact", "wear": 0.3},
        ])
        frame = Material("metal", color=(30, 32, 38), rough=0.4, skin=False)
        a.add("Props", sh.rounded_box((0.06, 2.6, 1.8), 0.01, 1, frame, face_mats={face: poster}).transformed(T(side * 5.73, 5.4, 2.4)))
    a.point("prompt", (0, 3.9, -2.4))
    a.point("label", (0, 13.6, 0))
    a.point("screen", SCREEN_CENTER)
    a.point("light", (0, 5.0, -2.0))
    a.meta["screen_size"] = (7.0, 3.0)
    a.meta["footprint"] = (12.0, 10.0)
    return a
