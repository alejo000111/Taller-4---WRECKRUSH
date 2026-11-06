import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
import _hammers_lib
import _launch_lib

HEAD_Y = 2.6
RED = (255, 40, 40)


def along_z(mesh, y=HEAD_Y, z=0.0, back=False):
    return mesh.transformed(compose(T(0, y, z), R(90 if back else -90, 0, 0)))


def build():
    a = Asset("OwnerHammer", budget=8000, ao_radius=0.4)
    a.role("Base", "surface")
    a.role("Gold", "surface")
    a.role("Glow", "neon", color=RED)

    obsidian = Material("launch_armor", color=(26, 23, 33), under=(120, 104, 150), wear=0.2, scratches=0.25, rough=0.28, metal=0.35, dirt=0.15,
                        lines_z=(-0.62, 0.62), lines_y=(HEAD_Y - 0.55, HEAD_Y + 0.55), line_width=0.014)
    shaft_mat = Material("metal", color=(30, 28, 38), rough=0.3, polish=0.7, dirt=0.15, skin=False)
    face_mat = Material("hammers_machined", color=(70, 66, 84), center=(0, HEAD_Y, -1.76), axis=(0, 0, -1), rings=[(0.7, 0.04), (0.86, 0.03)], zone=0.66, dents=0.3, polish=0.6)
    gold = Material("gold", color=(255, 196, 64), rough=0.22, dirt=0.12)
    band_gold = Material("gold", color=(255, 196, 64), rough=0.22, dirt=0.12, decals=[
        {"type": "rivets", "points": [(x, y) for x in (-0.82, 0.82) for y in (-0.62, 0.62)], "radius": 0.07, "height": 0.02},
    ])
    wrap = Material("wrap", color=(26, 22, 28), width=0.12, slope=0.4, dirt=0.2)

    a.add("Base", sh.lathe([(0, -1.86), (0.25, -1.86), (0.25, 1.95), (0, 1.95)], 10, shaft_mat))
    a.add("Base", sh.lathe([(0.25, -1.62), (0.31, -1.58), (0.315, -0.95), (0.305, -0.34), (0.25, -0.3)], 12, wrap))
    for y in (-1.35, -0.95, -0.55):
        a.add("Glow", sh.torus(0.315, 0.05, None, segments=20, sides=6).transformed(T(0, y, 0)))

    a.add("Gold", sh.lathe([(0, -2.12), (0.22, -2.12), (0.36, -2.04), (0.45, -1.92), (0.45, -1.84), (0.36, -1.76), (0.25, -1.62), (0, -1.62)], 20, gold, smooth_angle=35))
    for k in range(4):
        spike = sh.frustum(0.09, 0.0, 0.32, gold, bevel=0.0, segments=4).transformed(compose(T(0, -1.9, 0), R(0, k * 90 + 45, 0), T(0.44, 0, 0), R(0, 0, -100)))
        a.add("Gold", spike)
    a.add("Glow", sh.gem(0.21, 0.34, 8, None).transformed(compose(T(0, -2.24, 0), R(180, 0, 0))))
    a.add("Gold", sh.lathe([(0.25, 1.28), (0.4, 1.28), (0.48, 1.38), (0.4, 1.5), (0.52, 1.64), (0.52, 1.8), (0.25, 1.8)], 20, gold, smooth_angle=35))

    a.add("Base", sh.rounded_box((1.76, 1.76, 2.3), 0.18, 1, obsidian).transformed(T(0, HEAD_Y, 0)))
    for z in (-0.98, 0.98):
        band = sh.rounded_box((1.9, 1.9, 0.26), 0.06, 1, gold, face_mats={"+x": band_gold, "-x": band_gold, "+y": band_gold, "-y": band_gold})
        a.add("Gold", band.transformed(T(0, HEAD_Y, z)))

    a.add("Base", along_z(sh.lathe([(0, 0.0), (0.9, 0.0), (1.02, 0.14), (1.02, 0.46), (0.94, 0.56), (0.64, 0.56), (0.0, 0.52)], 28, face_mat, smooth_angle=35), z=-1.15))
    a.add("Glow", along_z(sh.cylinder(0.64, 0.08, None, bevel=0.0, segments=28), z=-1.68))
    a.add("Gold", sh.torus(1.0, 0.045, gold, segments=32, sides=5).transformed(compose(T(0, HEAD_Y, -1.48), R(90, 0, 0))))
    a.add("Gold", along_z(sh.lathe([(0, 0), (0.86, 0), (0.92, 0.12), (0.92, 0.3), (0.7, 0.42), (0, 0.42)], 24, gold, smooth_angle=35), z=1.15, back=True))
    a.add("Gold", along_z(sh.lathe([(0, 0), (0.42, 0), (0.36, 0.2), (0.08, 0.68), (0, 0.72)], 4, gold, smooth_angle=30, start=45), z=1.55, back=True))

    for side in (-1, 1):
        x = side * 0.89
        a.add("Gold", sh.tube(0.32, 0.22, 0.1, gold, bevel=0.02, segments=12).transformed(compose(T(x, HEAD_Y - 0.2, 0), R(0, 0, 90))))
        a.add("Glow", sh.gem(0.25, 0.3, 8, None).transformed(compose(T(x + side * 0.05, HEAD_Y - 0.2, 0), R(0, 0, -90 * side))))
        a.add("Glow", sh.box((0.06, 0.18, 1.5), None).transformed(T(x + side * 0.004, HEAD_Y + 0.46, 0)))
        for z in (-0.31, 0.31):
            claw = sh.frustum(0.06, 0.012, 0.22, gold, bevel=0.0, segments=4).transformed(compose(T(x + side * 0.06, HEAD_Y - 0.2, z), R(0, 0, -90 * side)))
            a.add("Gold", claw)

    a.add("Gold", sh.rounded_box((1.5, 0.16, 2.1), 0.04, 1, gold).transformed(T(0, HEAD_Y + 0.96, 0)))
    for z, h in ((-0.78, 0.42), (-0.4, 0.3), (0.0, 0.62), (0.4, 0.3), (0.78, 0.42)):
        cone = sh.frustum(0.17, 0.02, h, gold, bevel=0.0, segments=4)
        a.add("Gold", cone.transformed(compose(T(0, HEAD_Y + 1.04 + h / 2, z), R(0, 45, 0))))
    for z in (-0.78, 0.78):
        a.add("Glow", sh.gem(0.07, 0.12, 6, None).transformed(T(0, HEAD_Y + 1.5, z)))
    a.add("Glow", sh.gem(0.16, 0.26, 8, None).transformed(T(0, HEAD_Y + 1.78, 0)))

    feather = [(-0.1, 0.0), (-0.13, 0.55), (-0.05, 0.95), (0.0, 1.12), (0.06, 0.92), (0.13, 0.55), (0.1, 0.0)]
    for side in (-1, 1):
        for k, (fan, length) in enumerate(((12, 1.25), (38, 1.6), (64, 1.75), (90, 1.4))):
            blade = sh.extrude([(x, y * length) for x, y in feather], 0.05, gold, bevel=0.012, corner_radius=0.0)
            blade = blade.transformed(compose(T(side * 1.0, HEAD_Y + 0.15, 0.35), R(0, 0, -18 * side), R(fan, 0, 0), R(0, 90, 0)))
            a.add("Gold", blade)
        a.add("Glow", sh.gem(0.09, 0.16, 6, None).transformed(compose(T(side * 1.02, HEAD_Y + 1.05, 0.62), R(0, 0, -20 * side))))
        for tilt in (30, -30):
            rune = sh.box((0.03, 0.08, 0.42), None).transformed(compose(T(side * 0.885, HEAD_Y - 0.62, 0.0), R(tilt, 0, 0), T(0, 0, 0.18 * (1 if tilt > 0 else -1))))
            a.add("Glow", rune)
    for z in (-0.4, 0.4):
        a.add("Glow", sh.gem(0.06, 0.1, 6, None).transformed(T(0, HEAD_Y + 1.44, z)))
    a.point("muzzle", (0, HEAD_Y, -1.95))
    a.point("aura", (0, HEAD_Y, 0))
    a.point("grip", (0, -1.1, 0))
    return a
