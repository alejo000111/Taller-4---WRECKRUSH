import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from RustyCar import (
    HALF_W, FRONT_AXLE, REAR_AXLE, TRACK, CABIN_Y, SILL_Y, ROOF_Y, BEZEL, HUBCAP, TIRE, LUG_R,
    side_extrude, top_extrude, plate_box, side_sheet, slanted_sheet, body_outline, arch_lip,
    windshield_z, rear_glass_z, c_pillar_z, arc_from_end, cabin, tumblehome, wheel,
)

TAXI = (255, 196, 22)
INK = (24, 24, 28)
CREAM = (238, 234, 222)
GLASS = (36, 52, 70)
LAMP = (255, 248, 220)
TAIL = (255, 48, 40)


def checker(sign, y0, rows=2, cell=0.34, z0=-5.9, z1=5.9):
    out = []
    count = int((z1 - z0) / cell)
    for i in range(count):
        for r in range(rows):
            if (i + r) % 2:
                continue
            z = z0 + (i + 0.5) * cell
            out.append({"type": "rect", "center": (z if sign < 0 else -z, -(y0 + (r - (rows - 1) / 2) * cell)), "size": (cell, cell), "color": INK, "wear": 0.15})
    return out


def side_decals(sign):
    def at(z, y):
        return (z if sign < 0 else -z, -y)

    out = [{"type": "rect", "center": at(0.0, 2.05), "size": (11.9, 0.72), "color": CREAM, "wear": 0.15}]
    out += checker(sign, 2.05)
    for z0, z1 in ((-2.3, 0.6), (0.62, 2.6)):
        out.append({"type": "rect", "center": at((z0 + z1) / 2, 1.95), "size": (z1 - z0, 2.14), "outline": 0.03, "darken": 0.55, "raise": -0.007})
        out.append({"type": "rect", "center": at(z1 - 0.36, 2.55), "size": (0.42, 0.08), "radius": 0.03, "color": (206, 208, 214), "metal": 1.0, "rough": 0.25, "wear": 0.2, "raise": 0.004})
    out.append({"type": "text", "text": "WRECK CAB", "center": at(-0.85, 1.32), "height": 0.34, "color": INK, "font": "impact", "wear": 0.15})
    out.append({"type": "text", "text": "$2.50 / MILE", "center": at(1.6, 1.36), "height": 0.2, "color": INK, "font": "bold", "wear": 0.15})
    out.append({"type": "text", "text": "07", "center": at(4.7, 1.5), "height": 0.62, "color": INK, "font": "impact", "wear": 0.2})
    out.append({"type": "rect", "center": at(-6.08, 1.95), "size": (0.38, 0.14), "radius": 0.03, "color": (240, 150, 40), "rough": 0.2, "wear": 0.1})
    out.append({"type": "rect", "center": at(6.12, 1.95), "size": (0.38, 0.14), "radius": 0.03, "color": (196, 36, 30), "rough": 0.2, "wear": 0.1})
    return out


def materials():
    paint = Material("paint", color=TAXI, under=(150, 152, 158), wear=0.2, scratches=0.3, rough=0.3, dirt=0.3, dirt_color=(64, 58, 50), skin=False)
    m = {"paint": paint, "left": paint.but(decals=side_decals(-1)), "right": paint.but(decals=side_decals(1))}
    m["fascia"] = paint.but(decals=[
        {"type": "rect", "center": (0.0, -0.02), "size": (3.1, 0.74), "radius": 0.08, "color": (20, 20, 22), "wear": 0.1, "raise": -0.02},
        *[{"type": "rect", "center": (0.0, -0.27 + k * 0.135), "size": (2.96, 0.05), "color": (196, 198, 204), "metal": 1.0, "rough": 0.25, "wear": 0.2, "raise": 0.004} for k in range(5)],
        {"type": "rect", "center": (0.0, -0.02), "size": (0.9, 0.36), "radius": 0.05, "color": INK, "wear": 0.1},
        {"type": "text", "text": "TAXI", "center": (0.0, -0.02), "height": 0.26, "color": TAXI, "font": "impact", "wear": 0.1},
        {"type": "rect", "center": (2.3, 0.46), "size": (0.6, 0.14), "radius": 0.04, "color": (240, 150, 40), "rough": 0.2, "wear": 0.1},
        {"type": "rect", "center": (-2.3, 0.46), "size": (0.6, 0.14), "radius": 0.04, "color": (240, 150, 40), "rough": 0.2, "wear": 0.1},
    ])
    m["tail"] = paint.but(decals=[
        {"type": "text", "text": "CITY CAB CO.", "center": (0.0, 0.02), "height": 0.24, "color": INK, "font": "black", "wear": 0.15},
    ])
    m["interior"] = Material("rustycar_cabin", dirt=0.2)
    m["trim"] = Material("metal", color=(40, 42, 48), rough=0.4, polish=0.5, dirt=0.3, scratches=0.2)
    m["chrome"] = Material("rustycar_chrome", color=(214, 218, 226), rust=-0.5)
    m["liner"] = Material("rubber", color=(26, 26, 28), pattern="dots", freq=5.0, depth=0.004, dirt=0.4)
    m["tail_lens"] = Material("glossy", color=(176, 26, 22), rough=0.15, dirt=0.15, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (1.4, 0.04), "darken": 0.5, "raise": -0.004},
    ])
    m["plate"] = Material("paint", color=(240, 236, 220), under=(150, 152, 158), wear=0.2, scratches=0.2, dirt=0.3, rough=0.5, skin=False, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (1.24, 0.5), "radius": 0.05, "outline": 0.035, "color": (34, 60, 130), "wear": 0.15},
        {"type": "text", "text": "CAB-707", "center": (0.0, 0.04), "height": 0.21, "color": (30, 52, 120), "font": "black", "wear": 0.15},
        {"type": "text", "text": "DOWNTOWN", "center": (0.0, -0.17), "height": 0.07, "color": (190, 40, 36), "font": "bold", "wear": 0.15},
    ])
    m["tire"] = Material("rustycar_tire", tread_v=(arc_from_end(TIRE, 4), arc_from_end(TIRE, 3)), ring_v=arc_from_end(TIRE, 1) + 0.06, pitch=0.34, dirt=0.25, dirt_color=(90, 84, 76))
    cap_total = arc_from_end(HUBCAP, 0)
    m["hubcap"] = Material("rustycar_chrome", color=(220, 224, 232), rust=-0.5, decals=[
        {"type": "rect", "center": (2.0, cap_total - 0.12), "size": (5.0, 0.02), "darken": 0.45, "raise": -0.004},
        {"type": "rect", "center": (2.0, cap_total - 0.4), "size": (5.0, 0.025), "darken": 0.4, "raise": -0.004},
    ])
    m["rim"] = m["hubcap"]
    m["lamp"] = Material("rustycar_chrome", color=(214, 218, 226), rust=-0.5)
    m["sign"] = Material("plastic", color=(250, 244, 226), rough=0.3, scuff=0.2, dirt=0.15)
    m["sign_face"] = Material("plastic", color=(250, 244, 226), rough=0.3, scuff=0.2, dirt=0.15, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (2.5, 0.7), "radius": 0.08, "outline": 0.06, "color": INK, "wear": 0.05},
        {"type": "text", "text": "TAXI", "center": (0.0, 0.02), "height": 0.5, "color": INK, "font": "impact", "wear": 0.05},
    ])
    return m


def lower_body(m):
    parts = [side_extrude(body_outline(), 2 * HALF_W, m["paint"], bevel=0.14, cap_mats=[m["left"], m["right"]])]
    for sx in (-1, 1):
        for cz in (FRONT_AXLE, REAR_AXLE):
            parts.append(side_extrude(arch_lip(cz), 0.14, m["trim"]).transformed(T(sx * 3.28, 0, 0)))
        face = "+x" if sx > 0 else "-x"
        parts.append(sh.rounded_box((0.05, 0.07, 12.8), 0.0, 1, m["chrome"], faces=[face, "+y", "-y", "+z", "-z"]).transformed(T(sx * 3.31, 2.6, 0.0)))
        parts.append(sh.rounded_box((0.06, 0.18, 5.2), 0.0, 1, m["trim"], faces=[face, "+y", "-y", "+z", "-z"]).transformed(T(sx * 3.31, 0.86, -0.12)))
    parts.append(plate_box((6.0, 1.08, 0.1), m["paint"], "-z", m["fascia"]).transformed(T(0, 1.96, -6.67)))
    parts.append(plate_box((5.8, 0.7, 0.08), m["paint"], "+z", m["tail"]).transformed(T(0, 2.08, 6.66)))
    for x in (-2.3, 2.3):
        parts.append(plate_box((1.3, 0.48, 0.1), m["tail_lens"], "+z").transformed(T(x, 2.06, 6.7)))
        parts.append(sh.lathe(BEZEL, 12, m["lamp"], smooth_angle=40).transformed(compose(T(x, 2.04, -6.7), R(-90, 0, 0))))
    outline = [(-3.0, 6.95), (3.0, 6.95), (3.3, 6.78), (3.36, 6.2), (3.24, 6.2), (3.2, 6.62), (2.95, 6.66), (-2.95, 6.66), (-3.2, 6.62), (-3.24, 6.2), (-3.36, 6.2), (-3.3, 6.78)]
    parts.append(top_extrude([(x, -z) for x, z in outline], 0.44, m["chrome"], bevel=0.05).transformed(T(0, 1.18, 0)))
    parts.append(top_extrude(outline, 0.44, m["chrome"], bevel=0.05).transformed(T(0, 1.16, 0)))
    parts.append(plate_box((1.3, 0.52, 0.04), m["plate"], "+z").transformed(T(0, 1.18, 6.97)))
    parts.append(side_extrude([(-2.55, 2.8), (-4.6, 2.96), (-6.44, 2.84), (-6.42, 2.94), (-4.6, 3.07), (-2.5, 2.91)], 6.0, m["paint"], bevel=0.05, smooth=30))
    parts.append(side_extrude([(3.62, 2.86), (6.38, 2.92), (6.5, 2.84), (6.55, 2.9), (6.43, 3.01), (3.62, 2.97)], 6.0, m["paint"], bevel=0.05, smooth=30))
    for z in (FRONT_AXLE, REAR_AXLE):
        parts.append(sh.rounded_box((4.4, 1.4, 2.5), 0.0, 1, m["liner"], faces=["+x", "-x", "-y", "+z", "-z"]).transformed(T(0, 1.8, z)))
    head = sh.rounded_box((0.16, 0.3, 0.42), 0.0, 1, m["trim"], face_mats={"+z": m["chrome"]})
    arm = sh.rounded_box((0.2, 0.07, 0.08), 0.0, 1, m["trim"])
    for sx in (-1, 1):
        parts.append(arm.transformed(compose(T(sx * 3.36, 2.86, -2.0), R(0, 0, sx * 35))))
        parts.append(head.transformed(T(sx * 3.42, 3.06, -2.0)))
    return parts


def roof_sign(m):
    body = sh.rounded_box((2.7, 0.78, 0.9), 0.12, 1, m["sign"], faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"-z": m["sign_face"], "+z": m["sign_face"]})
    base = sh.rounded_box((2.2, 0.12, 0.7), 0.03, 1, m["trim"], faces=["+x", "-x", "+y", "+z", "-z"])
    return [base.transformed(T(0, ROOF_Y + 0.33, 0.55)), body.transformed(T(0, ROOF_Y + 0.78, 0.55))]


def glazing():
    top = ROOF_Y + 0.02
    front_pane = [(windshield_z(SILL_Y) + 0.25, SILL_Y), (0.45, SILL_Y), (0.45, top), (windshield_z(ROOF_Y) + 0.25, top)]
    rear_pane = [(0.78, SILL_Y), (c_pillar_z(SILL_Y), SILL_Y), (c_pillar_z(ROOF_Y), top), (0.78, top)]
    parts = []
    for x in (-2.74, 2.74):
        parts.append(side_sheet(front_pane, x))
        parts.append(side_sheet(rear_pane, x))
    parts.append(slanted_sheet(5.0, CABIN_Y, windshield_z(CABIN_Y), 0.891, -1))
    parts.append(slanted_sheet(5.0, CABIN_Y, rear_glass_z(CABIN_Y), 0.718, 1))
    return parts


def build():
    a = Asset("TaxiCab", budget=3000, atlas=1024, ao_radius=1.0, edge_width=0.08, preview_radius=7.9,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.35)
    a.role("Glow", "neon", color=LAMP)
    a.role("Tail", "neon", color=TAIL)
    m = materials()
    a.add("Body", lower_body(m))
    a.add("Body", [tumblehome(part) for part in cabin(m)])
    a.add("Body", roof_sign(m))
    a.add("Glass", [tumblehome(part) for part in glazing()])
    lens = sh.lathe([(0.35, 0.07), (0.24, 0.12), (0.0, 0.14)], 10, None, smooth_angle=60)
    a.add("Glow", [lens.transformed(compose(T(x, 2.04, -6.7), R(-90, 0, 0))) for x in (-2.3, 2.3)])
    a.add("Glow", sh.box((2.0, 0.05, 0.5), None).transformed(T(0, ROOF_Y + 1.2, 0.55)))
    a.add("Tail", [sh.box((1.0, 0.3, 0.04), None).transformed(T(x, 2.06, 6.77)) for x in (-2.3, 2.3)])
    for x, z in ((-TRACK, FRONT_AXLE), (TRACK, FRONT_AXLE), (-TRACK, REAR_AXLE), (TRACK, REAR_AXLE)):
        a.add("Body", wheel(m, x, z, True))
    destructible(a, "Downtown")
    collider(a, "Hitbox", (6.8, 2.6, 13.6), (0, 1.6, 0))
    collider(a, "Cabin", (5.6, 1.8, 4.4), (0, 3.78, 0.5))
    collider(a, "Sign", (2.6, 0.9, 0.9), (0, ROOF_Y + 0.75, 0.55))
    return a
