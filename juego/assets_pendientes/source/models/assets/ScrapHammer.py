import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _hammers_lib import place

HEAD_Y = 1.75
PLATE_RIVETS = [(-0.24, -0.17), (0.24, -0.17), (-0.24, 0.17), (0.24, 0.17)]


def bend(mesh, amount):
    out = mesh.copy()
    y = out.pos[:, 1]
    out.pos[:, 2] += amount * (y - 0.4) ** 2
    sh.recompute_normals(out)
    return out


def build():
    a = Asset("ScrapHammer", budget=4000, ao_radius=0.35)
    a.role("Primary", "surface", color=(150, 152, 160), skin="Primary")
    a.role("Accent", "surface", color=(66, 68, 76), skin="Accent")
    a.role("Base", "surface")

    steel = Material("metal", color=(150, 152, 160), skin=True, hammered=0.45, rough=0.36, dirt=0.35)
    face_steel = Material("metal", color=(182, 184, 192), skin=True, polish=0.9, rough=0.22, brushed=True, dirt=0.2)
    dark = Material("metal", color=(66, 68, 76), skin=True, rough=0.42, dirt=0.4)
    bolt_mat = Material("metal", color=(120, 116, 110), rough=0.45, dirt=0.5, skin=False)
    wire = Material("rust", steel=(110, 104, 98), amount=0.7)
    wood = Material("wood", color=(150, 98, 56), axis="y", dirt=0.35)
    tape = Material("wrap", color=(54, 48, 42), width=0.12, slope=0.45, dirt=0.5)
    plate = Material("paint", color=(255, 122, 26), wear=0.6, dirt=0.45, scratches=0.55, skin=False, decals=[
        {"type": "text", "text": "07", "center": (0.0, 0.02), "height": 0.2, "color": (22, 20, 24), "font": "impact", "wear": 0.4},
        {"type": "rivets", "points": PLATE_RIVETS, "radius": 0.04, "color": (120, 118, 114), "height": 0.014},
    ])

    handle = sh.lathe([(0, -1.42), (0.18, -1.42), (0.21, -1.32), (0.205, -1.0), (0.19, -0.2), (0.175, 0.6), (0.168, 1.4), (0.165, 2.24), (0, 2.26)], 12, wood)
    a.add("Base", bend(handle, -0.018))
    a.add("Base", bend(sh.lathe([(0.17, -1.3), (0.238, -1.25), (0.244, -0.75), (0.238, -0.26), (0.17, -0.2)], 14, tape), -0.018))
    tail = [(0.2, -0.26, 0.05), (0.27, -0.36, 0.1), (0.31, -0.55, 0.08), (0.3, -0.72, 0.15)]
    a.add("Base", sh.sweep(tail, 0.022, 4, tape, samples=6))

    a.add("Accent", sh.lathe([(0, -1.6), (0.18, -1.6), (0.27, -1.53), (0.28, -1.4), (0.22, -1.32), (0, -1.31)], 14, dark))
    a.add("Accent", sh.torus(0.13, 0.03, dark, segments=12, sides=5).transformed(compose(T(0, -1.7, 0), R(90, 0, 0))))
    a.add("Accent", sh.tube(0.235, 0.15, 0.3, dark, bevel=0.03, segments=14).transformed(T(0, 1.18, 0)))
    for y in (-0.9, -0.42):
        a.add("Accent", sh.tube(0.255, 0.23, 0.07, dark, bevel=0.0, segments=14).transformed(T(0, y, 0)))
        a.add("Base", sh.box((0.08, 0.08, 0.1), bolt_mat).transformed(T(0.27, y, 0)))

    octagon = [(-0.3, -0.42), (0.3, -0.42), (0.42, -0.3), (0.42, 0.3), (0.3, 0.42), (-0.3, 0.42), (-0.42, 0.3), (-0.42, -0.3)]
    a.add("Primary", sh.extrude(octagon, 0.92, steel, bevel=0.04, corner_radius=0.0).transformed(T(0, HEAD_Y, -0.2)))
    for y in (HEAD_Y + 0.42, HEAD_Y - 0.42):
        boss = sh.cylinder(0.28, 0.12, steel, bevel=0.03, segments=14)
        a.add("Primary", boss.transformed(T(0, y + (0.04 if y > HEAD_Y else -0.04), -0.05)))
    bell = sh.lathe([(0, 0.0), (0.38, 0.0), (0.36, 0.08), (0.42, 0.16), (0.5, 0.26), (0.52, 0.36), (0.5, 0.44), (0.4, 0.48), (0, 0.5)], 18, face_steel, smooth_angle=35)
    a.add("Primary", bell.transformed(compose(T(0, HEAD_Y, -0.66), R(-90, 0, 0))))

    claw = [(-0.26, 0.34), (-0.6, 0.31), (-0.9, 0.18), (-1.12, -0.04), (-1.28, -0.32), (-1.36, -0.6), (-1.27, -0.5), (-1.12, -0.28), (-0.94, -0.12), (-0.7, -0.03), (-0.48, -0.04), (-0.26, -0.18)]
    for side in (-1, 1):
        prong = sh.extrude(claw, 0.16, steel, bevel=0.035, corner_radius=0.0)
        prong.pos[:, 2] *= np.interp(prong.pos[:, 0], [-1.36, -0.26], [0.45, 1.0])
        prong = prong.transformed(compose(T(side * 0.1, HEAD_Y, 0.0), R(0, 90, 0)))
        a.add("Primary", prong)

    wrap = sh.spring(0.5, 0.024, 3.2, 0.42, wire, sides=5, samples_per_turn=14)
    a.add("Base", wrap.transformed(compose(T(0, HEAD_Y, 0.02), R(90, 0, 0))))
    a.add("Accent", sh.box((0.07, 0.06, 0.3), dark).transformed(T(0, 2.25, 0)))

    for side in (-1, 1):
        patch = sh.rounded_box((0.05, 0.5, 0.62), 0.016, 1, plate)
        patch.pos[:, 0] += side * 0.03 * (patch.pos[:, 2] / 0.31) ** 2
        a.add("Base", patch.transformed(compose(T(side * 0.45, HEAD_Y + 0.01, -0.22), R(7 * side, 0, 0))))
        for dy, dz in ((0.2, -0.48), (-0.2, 0.06)):
            a.add("Base", place(sh.bolt(0.055, 0.05, bolt_mat), (side * 0.43, HEAD_Y + dy, dz), (side, 0, 0)))

    tape_band = Material("hazard", color=(255, 210, 31), color2=(22, 22, 26), width=0.07, wear=0.45, skin=False)
    ring = [(x * 1.06, y * 1.06) for x, y in octagon]
    a.add("Base", sh.extrude(ring, 0.16, tape_band, bevel=0.0, corner_radius=0.0, caps=False).transformed(T(0, HEAD_Y, 0.1)))
    pivot = np.array([0.0, HEAD_Y, -0.2])
    grow = compose(T(*pivot), S(1.12), T(*(-pivot)))
    for role in ("Primary",):
        a.parts[role] = [m.transformed(grow) for m in a.parts[role]]
    head_base = a.parts["Base"][5:]
    a.parts["Base"] = a.parts["Base"][:5] + [m.transformed(grow) for m in head_base]
    a.point("muzzle", (0, HEAD_Y, -1.3))
    a.point("grip", (0, -0.75, 0))
    return a
