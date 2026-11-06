import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from RustyCar import FRONT_AXLE, REAR_AXLE, TRACK, ROOF_Y, TIRE, HUBCAP, arc_from_end, side_extrude, cabin, tumblehome, wheel
from TaxiCab import lower_body, glazing

GOLD = (255, 196, 40)
INK = (30, 22, 10)
GLASS = (90, 60, 20)
SCALE = S(1.1, 1.0, 1.1)


def gold(decals=()):
    return Material("gold", color=GOLD, rough=0.18, scratches=0.15, dirt=0.1, decals=list(decals))


def side_decals(sign):
    def at(z, y):
        return (z if sign < 0 else -z, -y)

    return [
        {"type": "rect", "center": at(0.0, 2.05), "size": (11.6, 0.1), "color": (255, 240, 170), "metal": 1.0, "rough": 0.1, "wear": 0.0},
        {"type": "text", "text": "$", "center": at(-0.85, 1.6), "height": 0.8, "color": (200, 140, 20), "font": "impact", "wear": 0.0, "raise": -0.004},
        *[{"type": "rect", "center": at((z0 + z1) / 2, 1.95), "size": (z1 - z0, 2.14), "outline": 0.03, "darken": 0.4, "raise": -0.006} for z0, z1 in ((-2.3, 0.6), (0.62, 2.6))],
    ]


def materials():
    paint = gold()
    m = {"paint": paint, "left": gold(side_decals(-1)), "right": gold(side_decals(1))}
    m["fascia"] = gold([
        {"type": "rect", "center": (0.0, -0.02), "size": (3.1, 0.74), "radius": 0.08, "color": (24, 18, 8), "wear": 0.0, "raise": -0.02},
        *[{"type": "rect", "center": (0.0, -0.27 + k * 0.135), "size": (2.96, 0.05), "color": (255, 220, 110), "metal": 1.0, "rough": 0.1, "wear": 0.0, "raise": 0.004} for k in range(5)],
        {"type": "text", "text": "$", "center": (0.0, -0.02), "height": 0.5, "color": (255, 230, 120), "font": "impact", "wear": 0.0},
    ])
    m["tail"] = gold([{"type": "text", "text": "GOLDEN WRECK", "center": (0.0, 0.02), "height": 0.24, "color": INK, "font": "black", "wear": 0.0}])
    m["interior"] = Material("rustycar_cabin", dirt=0.1)
    m["trim"] = Material("metal", color=(30, 26, 20), rough=0.3, polish=0.7, dirt=0.15)
    m["chrome"] = Material("gold", color=(255, 226, 120), rough=0.1, scratches=0.05, dirt=0.05)
    m["liner"] = Material("rubber", color=(26, 24, 22), pattern="dots", freq=5.0, depth=0.004, dirt=0.3)
    m["tail_lens"] = Material("glossy", color=(176, 26, 22), rough=0.12, dirt=0.1)
    m["plate"] = gold([
        {"type": "rect", "center": (0.0, 0.0), "size": (1.24, 0.5), "radius": 0.05, "outline": 0.035, "color": INK, "wear": 0.0},
        {"type": "text", "text": "RICH-1", "center": (0.0, 0.03), "height": 0.24, "color": INK, "font": "black", "wear": 0.0},
    ])
    m["tire"] = Material("rustycar_tire", tread_v=(arc_from_end(TIRE, 4), arc_from_end(TIRE, 3)), ring_v=arc_from_end(TIRE, 1) + 0.06, pitch=0.34, dirt=0.15, dirt_color=(90, 84, 76))
    m["hubcap"] = Material("gold", color=(255, 216, 90), rough=0.12, dirt=0.05)
    m["rim"] = m["hubcap"]
    m["lamp"] = m["chrome"]
    return m


def build():
    a = Asset("GoldenCar", budget=3500, atlas=1024, ao_radius=1.0, edge_width=0.08, gradient=0.08, highlight=0.7, preview_radius=8.6,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glass", "glass", color=GLASS, transparency=0.3)
    a.role("Glow", "neon", color=(255, 236, 150))
    a.role("Tail", "neon", color=(255, 48, 40))
    m = materials()
    a.add("Body", lower_body(m))
    a.add("Body", [tumblehome(part) for part in cabin(m)])
    a.add("Glass", [tumblehome(part) for part in glazing()])
    lens = sh.lathe([(0.35, 0.07), (0.24, 0.12), (0.0, 0.14)], 10, None, smooth_angle=60)
    a.add("Glow", [lens.transformed(compose(T(x, 2.04, -6.7), R(-90, 0, 0))) for x in (-2.3, 2.3)])
    a.add("Tail", [sh.box((1.0, 0.3, 0.04), None).transformed(T(x, 2.06, 6.77)) for x in (-2.3, 2.3)])
    for x, z in ((-TRACK, FRONT_AXLE), (TRACK, FRONT_AXLE), (-TRACK, REAR_AXLE), (TRACK, REAR_AXLE)):
        a.add("Body", wheel(m, x, z, True))

    wing = side_extrude([(5.6, 3.95), (6.9, 3.95), (6.9, 4.12), (5.6, 4.12)], 6.6, m["paint"], bevel=0.04)
    a.add("Body", wing)
    for x in (-2.5, 2.5):
        a.add("Body", sh.box((0.22, 1.1, 0.5), m["trim"]).transformed(T(x, 3.45, 6.2)))
    a.add("Glow", sh.gem(0.38, 0.7, 6, None).transformed(compose(T(0, 3.05, -6.0), R(90, 0, 0))))
    for sx in (-1, 1):
        a.add("Glow", sh.box((0.05, 0.08, 11.6), None).transformed(T(sx * 3.36, 2.05, 0.0)))
    a.add("Glow", sh.box((0.6, 0.06, 2.6), None).transformed(T(0, ROOF_Y + 0.08, 0.7)))

    for role in a.parts:
        a.parts[role] = [mesh.transformed(SCALE) for mesh in a.parts[role]]

    destructible(a, "Event")
    collider(a, "Hitbox", (7.5, 2.6, 15.0), (0, 1.6, 0))
    collider(a, "Cabin", (6.2, 1.8, 4.8), (0, 3.78, 0.55))
    return a
