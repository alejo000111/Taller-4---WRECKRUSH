import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _prop_lib import prop, collider, frame_ring
from _station_lib import steel, painted, YELLOW, INK

PILLAR_X = 20.0
LINTEL_Y = 21.3
SIGN_Y = 28.0
SIGN = (46.0, 9.4, 1.2)
TARGETS = ["Zones/" + z + "/GateArch" for z in ("ScrapYard", "Downtown", "Industrial", "Military", "FutureDistrict", "ChaosCore")] + ["VIPArea/GateArch"]


def tower(mat, band, cap):
    parts = [sh.rounded_box((5.2, 2.0, 5.2), 0.12, 1, band, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 1.0, 0))]
    shaft = sh.lathe([(0.0, 2.0), (2.9, 2.0), (2.5, 19.0), (0.0, 19.0)], 4, mat, smooth_angle=10, start=45, r_ref=2.9)
    parts.append(shaft)
    parts.append(sh.rounded_box((5.0, 1.4, 5.0), 0.12, 1, cap).transformed(T(0, 19.7, 0)))
    for y in (6.0, 12.0):
        parts.append(sh.rounded_box((4.6, 0.5, 4.6), 0.06, 1, cap).transformed(T(0, y, 0)))
    return parts


def build():
    a = Asset("ZoneGateArch", budget=3000, atlas=1024, ao_radius=1.4, edge_width=0.1, preview_radius=27.0,
              views=[("FRONT 3/4", 215, 12), ("BACK 3/4", 35, 14), ("FRONT", 180, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.meta["anchor_height"] = SIGN_Y
    a.role("Glow", "neon", color=(255, 122, 26))
    a.role("Frame", "neon", color=(183, 87, 18))
    prop(a, TARGETS, "ZoneSign", ["GatePillar", "PillarGlow", "Lintel", "LintelGlow", "ZoneSignFrame"], tint={"Glow": "PillarGlow", "Frame": "ZoneSignFrame"})

    plates = Material("metal", color=(38, 40, 48), rough=0.38, polish=0.55, dirt=0.4, scratches=0.3, decals=[
        {"type": "rivets", "points": [(u, v) for u in np.linspace(0.6, 22.0, 9) for v in (1.0, 8.0, 16.0)], "radius": 0.14, "color": (110, 114, 122), "height": 0.025},
        *[{"type": "rect", "center": (11.6, v), "size": (24.0, 0.07), "darken": 0.5, "raise": -0.008} for v in (4.0, 12.0)],
    ])
    band = Material("hazard", color=YELLOW, color2=INK, width=0.5, angle=45, wear=0.4, dirt=0.4)
    cap = steel((60, 62, 70))
    for sx in (-1, 1):
        a.add("Body", [p.transformed(T(sx * PILLAR_X, 0, 0)) for p in tower(plates, band, cap)])
        for sz in (-1, 1):
            a.add("Glow", sh.box((0.5, 15.0, 0.25), None).transformed(T(sx * PILLAR_X, 10.5, sz * 2.75)))
        lamp = steel((34, 36, 42))
        a.add("Body", sh.rounded_box((1.4, 0.8, 1.0), 0.08, 1, lamp).transformed(compose(T(sx * PILLAR_X, 20.9, -2.0), R(-40, 0, 0))))

    truss = steel((48, 50, 58))
    beam = sh.rounded_box((44.0, 1.0, 1.0), 0.06, 1, truss)
    for y, z in ((LINTEL_Y - 1.2, -1.6), (LINTEL_Y - 1.2, 1.6), (LINTEL_Y + 1.2, -1.6), (LINTEL_Y + 1.2, 1.6)):
        a.add("Body", beam.transformed(T(0, y, z)))
    for x in np.linspace(-17.0, 17.0, 9):
        for z in (-1.6, 1.6):
            a.add("Body", sh.sweep([(x - 2.1, LINTEL_Y - 1.2, z), (x + 2.1, LINTEL_Y + 1.2, z)], 0.18, 4, truss))
        a.add("Body", sh.box((0.4, 0.4, 3.2), truss).transformed(T(x, LINTEL_Y - 1.2, 0)))
    a.add("Glow", sh.box((36.0, 0.25, 2.2), None).transformed(T(0, LINTEL_Y - 1.85, 0)))

    frame = steel((26, 28, 34))
    outer = (SIGN[0] + 2.4, SIGN[1] + 2.2)
    inner = (SIGN[0] - 0.1, SIGN[1] - 0.1)
    a.add("Body", [p.transformed(T(0, SIGN_Y, 0)) for p in frame_ring(outer, inner, SIGN[2] + 0.8, frame)])
    for sz in (-1, 1):
        a.add("Frame", [p.transformed(T(0, SIGN_Y, sz * (SIGN[2] / 2 + 0.42))) for p in frame_ring((outer[0] - 0.4, outer[1] - 0.4), (outer[0] - 1.0, outer[1] - 1.0), 0.08, None)])
    for x in (-14.0, 0.0, 14.0):
        a.add("Body", sh.box((0.7, SIGN_Y - SIGN[1] / 2 - LINTEL_Y - 1.4, 0.7), frame).transformed(T(x, (SIGN_Y - SIGN[1] / 2 + LINTEL_Y + 1.5) / 2, 0)))

    for sx in (-1, 1):
        collider(a, f"Tower{'L' if sx < 0 else 'R'}", (5.2, 20.4, 5.2), (sx * PILLAR_X, 10.2, 0))
    collider(a, "Truss", (44.0, 3.4, 4.2), (0, LINTEL_Y, 0))
    collider(a, "SignFrame", (outer[0], outer[1], SIGN[2] + 0.8), (0, SIGN_Y, 0))
    return a
