import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
from _destructible import destructible, collider

ORANGE = (200, 90, 40)
GREY = (120, 124, 132)
YELLOW = (255, 210, 31)
WHITE = (236, 236, 232)

LENGTH = 9.6
R_OUT = 0.8
R_IN = 0.6
SKID_Z = 3.4


def tube_profile():
    h = LENGTH / 2
    return [(R_IN, -h), (R_OUT, -h), (R_OUT, h), (R_IN, h)]


def tube_bands():
    pts = np.asarray(tube_profile() + [tube_profile()[0]])
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(seg)])
    total = arc[-1]
    return {"bottom": (total - arc[1], total - arc[0]), "outer": (total - arc[2], total - arc[1]), "top": (total - arc[3], total - arc[2])}


BANDS = tube_bands()
RING = 2 * np.pi * R_OUT


def pipe_material(color, seed, label=None, caps=None):
    lo, hi = BANDS["outer"]
    decals = []
    for end in ("bottom", "top"):
        a, b = BANDS[end]
        if caps:
            decals.append({"type": "rect", "center": (RING / 2, (a + b) / 2), "size": (RING + 0.2, b - a + 0.02), "color": caps, "wear": 0.3, "rough": 0.5})
        decals.append({"type": "rect", "center": (RING / 2, (b if end == "bottom" else a)), "size": (RING + 0.2, 0.05), "darken": 0.3, "raise": -0.004})
    if label:
        decals.append({"type": "text", "text": label, "center": (RING * 0.25, lo + (hi - lo) * 0.5), "height": 0.32, "color": WHITE, "font": "impact", "wear": 0.4, "angle": 90})
        decals.append({"type": "rect", "center": (RING * 0.25, lo + (hi - lo) * 0.18), "size": (0.6, 0.12), "color": YELLOW, "wear": 0.4})
    if color == GREY:
        return Material("metal", color=GREY, rough=0.4, polish=0.4, dirt=0.45, scratches=0.4, decals=decals)
    return Material("paint", color=color, under=(110, 104, 98), wear=0.45, scratches=0.4, rough=0.45, dirt=0.5, skin=False, decals=decals)


def pipe(mat):
    mesh = sh.lathe(tube_profile(), 10, mat, closed=True, smooth_angle=40, r_ref=R_OUT)
    return mesh.transformed(R(90, 0, 0))


def build():
    a = Asset("PipeStack", budget=2000, atlas=1024, ao_radius=0.7, edge_width=0.05, preview_radius=6.2,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")

    wood = Material("wood", color=(120, 74, 44), axis="x", dirt=0.5)
    stake_wood = Material("wood", color=(132, 84, 50), axis="y", dirt=0.45)
    strap = Material("metal", color=(70, 72, 80), rough=0.45, polish=0.4, dirt=0.5)

    for z in (-SKID_Z, SKID_Z):
        a.add("Body", sh.rounded_box((7.6, 0.5, 0.8), 0.04, 1, wood, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 0.25, z)))
        for x in (-3.55, 3.55):
            a.add("Body", sh.rounded_box((0.36, 3.4, 0.36), 0.03, 1, stake_wood, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(compose(T(x, 1.9, z), R(0, 0, -np.sign(x) * 4))))

    rows = [(4, 0.5 + R_OUT), (3, 0.5 + R_OUT + np.sqrt(3) * R_OUT), (2, 0.5 + R_OUT + 2 * np.sqrt(3) * R_OUT)]
    palette = [ORANGE, GREY, ORANGE, ORANGE, GREY, ORANGE, GREY, ORANGE, ORANGE]
    labels = ["6\" SCH 40", None, "LOT 7", None, "6\" SCH 40", None, None, "HOLD", None]
    caps = [YELLOW, None, None, (60, 160, 230), YELLOW, None, (232, 52, 44), None, YELLOW]
    k = 0
    for count, y in rows:
        for i in range(count):
            x = (i - (count - 1) / 2) * 2 * R_OUT * 1.01
            shift = ((k * 37) % 7 - 3) * 0.12
            mat = pipe_material(palette[k], k, labels[k], caps[k])
            a.add("Body", pipe(mat).transformed(compose(T(x, y, shift), R(0, 0, k * 40))))
            k += 1

    for z in (-2.0, 2.0):
        top = rows[2][1] + R_OUT
        path = [(-3.3, 0.5, z), (-3.3, rows[0][1] + 0.4, z), (-1.6, top + 0.08, z), (1.6, top + 0.08, z), (3.3, rows[0][1] + 0.4, z), (3.3, 0.5, z)]
        a.add("Body", sh.sweep(path, 0.06, 4, strap, samples=14))

    destructible(a, "Industrial")
    collider(a, "Hitbox", (7.0, rows[2][1] + R_OUT, 9.6), (0, (rows[2][1] + R_OUT) / 2, 0))
    collider(a, "Skids", (7.6, 0.5, 7.6), (0, 0.25, 0))
    return a
