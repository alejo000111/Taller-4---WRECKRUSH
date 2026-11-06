import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _prop_lib import prop, collider, frame_ring
from _station_lib import steel, painted, YELLOW, INK

PILLAR_X = 7.4
LINTEL_Y = 18.2
SIGN_Y = 22.2
SIGN = (17.0, 5.6, 0.8)
TARGETS = ["Portals/" + z for z in ("ScrapYard", "Downtown", "Industrial", "Military", "FutureDistrict", "ChaosCore", "VIP", "Hall")]


def pillar(mat, band):
    body = sh.lathe([(0.0, 0.0), (1.9, 0.0), (1.9, 1.6), (1.6, 1.9), (1.35, 15.6), (1.7, 15.9), (1.7, 17.0), (0.0, 17.0)], 6, mat, smooth_angle=20, start=30, r_ref=1.9)
    base = sh.lathe([(1.92, 0.15), (1.92, 1.5)], 6, band, smooth_angle=20, start=30, r_ref=1.92)
    return [body, base]


def build():
    a = Asset("PortalArch", budget=2500, atlas=1024, ao_radius=0.9, edge_width=0.07, preview_radius=13.0,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 14), ("FRONT", 180, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.meta["anchor_height"] = SIGN_Y
    a.role("Glow", "neon", color=(255, 122, 26))
    prop(a, TARGETS, "Sign", ["Pillar", "PillarGlow", "Lintel", "LintelGlow"], tint={"Glow": "PillarGlow"})

    armor = steel((40, 42, 50))
    plates = Material("metal", color=(40, 42, 50), rough=0.38, polish=0.6, dirt=0.35, scratches=0.3, decals=[
        {"type": "rivets", "points": [(u, v) for u in np.linspace(0.4, 11.0, 6) for v in (1.0, 14.0)], "radius": 0.1, "color": (110, 114, 122), "height": 0.02},
        *[{"type": "rect", "center": (5.7, v), "size": (12.0, 0.05), "darken": 0.5, "raise": -0.006} for v in (4.0, 8.0, 12.0)],
    ])
    band = Material("hazard", color=YELLOW, color2=INK, width=0.35, angle=45, wear=0.35, dirt=0.35)
    for sx in (-1, 1):
        a.add("Body", [p.transformed(T(sx * PILLAR_X, 0, 0)) for p in pillar(plates, band)])
        a.add("Glow", sh.box((0.35, 13.0, 0.35), None).transformed(T(sx * (PILLAR_X - 1.45), 8.6, 0)))
        a.add("Body", sh.cylinder(0.5, 0.6, armor, bevel=0.05, segments=8).transformed(T(sx * PILLAR_X, 17.3, 0)))

    lintel = sh.extrude([(-9.6, -1.3), (9.6, -1.3), (10.4, -0.6), (10.4, 0.9), (9.6, 1.3), (-9.6, 1.3), (-10.4, 0.9), (-10.4, -0.6)], 2.8, plates, bevel=0.08, corner_radius=0.0)
    a.add("Body", lintel.transformed(T(0, LINTEL_Y, 0)))
    chevrons = painted((40, 42, 50), [{"type": "stripes", "center": (0.0, 0.0), "size": (19.0, 0.7), "width": 0.5, "color": YELLOW, "wear": 0.3}])
    for sz in (-1, 1):
        a.add("Body", sh.rounded_box((19.0, 0.8, 0.1), 0.0, 1, chevrons, faces=["-z" if sz < 0 else "+z"]).transformed(T(0, LINTEL_Y - 0.2, sz * 1.45)))
    a.add("Glow", sh.box((13.0, 0.2, 2.0), None).transformed(T(0, LINTEL_Y - 1.35, 0)))

    frame = steel((26, 28, 34))
    outer = (SIGN[0] + 1.6, SIGN[1] + 1.4)
    inner = (SIGN[0] - 0.1, SIGN[1] - 0.1)
    a.add("Body", [p.transformed(T(0, SIGN_Y, 0)) for p in frame_ring(outer, inner, SIGN[2] + 0.6, frame)])
    for sz in (-1, 1):
        a.add("Glow", [p.transformed(T(0, SIGN_Y, sz * (SIGN[2] / 2 + 0.32))) for p in frame_ring((outer[0] - 0.3, outer[1] - 0.3), (outer[0] - 0.7, outer[1] - 0.7), 0.06, None)])
    for sx in (-1, 1):
        a.add("Body", sh.box((0.5, SIGN_Y - SIGN[1] / 2 - LINTEL_Y - 1.0, 0.5), frame).transformed(T(sx * 6.0, (SIGN_Y - SIGN[1] / 2 + LINTEL_Y + 1.3) / 2, 0)))
        a.add("Glow", sh.sphere(0.35, None, 8, 4).transformed(T(sx * (outer[0] / 2 - 0.2), SIGN_Y + outer[1] / 2 + 0.25, 0)))

    for sx in (-1, 1):
        collider(a, f"Pillar{'L' if sx < 0 else 'R'}", (3.4, 17.0, 3.4), (sx * PILLAR_X, 8.5, 0))
    collider(a, "Lintel", (20.8, 2.6, 2.8), (0, LINTEL_Y, 0))
    return a
