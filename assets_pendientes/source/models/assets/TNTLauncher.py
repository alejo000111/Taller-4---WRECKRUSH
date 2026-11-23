import numpy as np

from wr3d import Asset, Material, T, R, compose
from wr3d import shapes as sh
import _hammers_lib
from _launch_lib import pistol_grip, trigger_group, side_profile

AXIS_Y = 1.4
RED = (255, 59, 59)
YELLOW = (255, 210, 31)


def forward(mesh, x=0.0, y=AXIS_Y, z=0.0):
    return mesh.transformed(compose(T(x, y, z), R(-90, 0, 0)))


def arc_v(profile, y, min_r=0.3):
    pts = np.asarray(profile)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(seg)])
    for i in range(len(pts) - 1):
        (r0, y0), (r1, y1) = pts[i], pts[i + 1]
        if min(r0, r1) >= min_r and min(y0, y1) <= y <= max(y0, y1) and y1 != y0:
            t = (y - y0) / (y1 - y0)
            return arc[-1] - (arc[i] + t * seg[i])
    return arc[-1] / 2


def build():
    a = Asset("TNTLauncher", budget=6000, ao_radius=0.35)
    a.role("Primary", "surface", color=RED, skin="Primary")
    a.role("AccentTrim", "surface", color=YELLOW, skin="Accent")
    a.role("Glow", "neon", color=(255, 160, 40))
    a.role("Base", "surface")

    tube_prof = [(0.0, -1.5), (0.38, -1.5), (0.47, -1.42), (0.47, 1.7), (0.56, 1.84), (0.56, 2.08), (0.46, 2.12), (0.36, 2.04), (0.36, 1.7), (0.0, 1.7)]
    r_ref = 0.56
    v_mid = arc_v(tube_prof, 0.2)
    stencil = [{"type": "text", "text": "TNT", "center": (u, v_mid), "height": 0.36, "angle": ang, "color": (250, 244, 230), "font": "impact", "wear": 0.4} for u, ang in ((np.pi / 2 * r_ref, 90), (3 * np.pi / 2 * r_ref, -90))]
    paint = Material("paint", color=RED, wear=0.45, scratches=0.4, dirt=0.35, rough=0.4, decals=stencil)
    band = Material("paint", color=YELLOW, wear=0.45, scratches=0.3, dirt=0.3, decals=[{"type": "stripes", "center": (1.75, 0.1), "size": (3.6, 0.3), "width": 0.11, "color": (22, 22, 26), "wear": 0.4}])
    dark = Material("metal", color=(50, 52, 58), rough=0.42, polish=0.6, dirt=0.35, skin=False)
    ring_plain = Material("metal", color=(50, 52, 58), rough=0.42, polish=0.6, dirt=0.35, skin=False)
    ring_dark = Material("metal", color=(50, 52, 58), rough=0.42, polish=0.6, dirt=0.35, skin=False, decals=[{"type": "rivets", "points": [(u, 0.11) for u in np.linspace(0.25, 3.1, 3)], "radius": 0.045, "height": 0.012}])
    steel = Material("metal", color=(160, 162, 170), rough=0.3, polish=0.8, dirt=0.3, skin=False)
    leather = Material("launch_leather", color=(96, 62, 38), grain=26.0)
    wood = Material("wood", color=(120, 80, 48), axis="z")
    paper = Material("launch_paper", color=(214, 40, 36), decals=[{"type": "text", "text": "TNT", "center": (0.25, 0.62), "height": 0.17, "angle": 90, "color": (250, 236, 200), "font": "impact", "wear": 0.2}])
    tape = Material("wrap", color=(150, 132, 100), width=0.07, slope=0.1, dirt=0.4)
    fuse = Material("wrap", color=(60, 48, 36), width=0.03, slope=1.2, dirt=0.3)
    rubber = Material("rubber", color=(30, 28, 30), pattern="ribs", freq=10.0)

    a.add("Base", pistol_grip(dark, leather, dark, steel, width=0.4))
    a.add("Base", trigger_group(dark, steel))

    receiver = sh.rounded_box((0.62, 0.44, 1.5), 0.06, 1, dark).transformed(T(0, 0.8, -0.12))
    a.add("Base", receiver)

    a.add("Primary", forward(sh.lathe(tube_prof, 24, paint, start=90, r_ref=r_ref, smooth_angle=35)))
    for zc in (-1.98, 1.42):
        a.add("Base", forward(sh.tube(0.53, 0.44, 0.22, ring_dark, bevel=0.02, segments=24), z=zc))
    for zc in (-1.2, 0.6):
        hb = sh.tube(0.5, 0.45, 0.2, band, bevel=0.015, segments=24)
        a.add("AccentTrim", forward(hb, z=zc))

    bundle_y = AXIS_Y + 0.62
    for x, y in ((-0.17, bundle_y), (0.17, bundle_y), (0.0, bundle_y + 0.28), (-0.34, bundle_y - 0.05), (0.34, bundle_y - 0.05)):
        stick = sh.lathe([(0, -0.66), (0.14, -0.66), (0.15, -0.62), (0.15, 0.62), (0.14, 0.66), (0, 0.66)], 12, paper, start=90)
        a.add("Base", forward(stick, x=x, y=y, z=0.1))
    for zc in (-0.32, 0.5):
        wrap = sh.tube(0.52, 0.46, 0.12, tape, bevel=0.0, segments=16)
        wrap = wrap.transformed(compose(T(0, bundle_y + 0.1, zc), R(-90, 0, 0), sh_scale(1.0, 1.0, 0.85)))
        a.add("Base", wrap)
    for zc in (-0.55, 0.75):
        strap = sh.box((1.12, 0.08, 0.12), dark).transformed(T(0, AXIS_Y + 0.46, zc))
        a.add("Base", strap)
    path = [(0.0, bundle_y + 0.28, 0.76), (0.03, bundle_y + 0.38, 0.86), (0.08, bundle_y + 0.62, 0.9), (0.1, 2.76, 0.92)]
    a.add("Base", sh.sweep(path, 0.025, 4, fuse, samples=6))
    a.add("Glow", sh.sphere(0.07, None, 8, 4).transformed(T(0.1, 2.8, 0.92)))
    for k in range(5):
        ang = k * 72
        spark = sh.frustum(0.03, 0.0, 0.16, None, bevel=0.0, segments=4).transformed(compose(T(0.1, 2.8, 0.92), R(ang, ang * 0.7, 30), T(0, 0.08, 0)))
        a.add("Glow", spark)

    post = side_profile([(-0.12, 0.0), (0.12, 0.0), (0.06, 0.24), (-0.04, 0.24)], 0.06, steel, bevel=0.0, corner_radius=0.0)
    a.add("Base", post.transformed(T(0, AXIS_Y + 0.5, -1.85)))
    for side in (-1, 1):
        ear = side_profile([(-0.1, 0.0), (0.1, 0.0), (0.1, 0.16), (-0.1, 0.12)], 0.05, steel, bevel=0.0, corner_radius=0.0)
        a.add("Base", ear.transformed(T(side * 0.07, AXIS_Y + 0.46, 1.05)))

    fg = sh.lathe([(0, -0.34), (0.15, -0.34), (0.17, -0.28), (0.15, 0.2), (0.1, 0.32), (0, 0.32)], 14, wood)
    a.add("Base", fg.transformed(T(0, 0.62, -1.3)))
    a.add("Base", sh.box((0.26, 0.14, 0.34), dark).transformed(T(0, 0.95, -1.3)))

    pad = sh.rounded_box((0.56, 0.76, 0.3), 0.1, 1, Material("rubber", color=(30, 28, 30), pattern="dots", freq=6.0)).transformed(T(0, 1.3, 1.82))
    a.add("Base", pad)
    a.add("Base", sh.box((0.2, 0.2, 0.28), dark).transformed(T(0, 1.3, 1.6)))

    for k in range(8):
        ang = k * 45 + 22.5
        tooth = sh.box((0.13, 0.16, 0.16), ring_plain)
        a.add("Base", tooth.transformed(compose(T(0, AXIS_Y, -2.16), R(0, 0, ang), T(0, 0.55, 0))))
    for x in (-0.34, 0.34):
        fz = [(x, bundle_y + 0.08, 0.76), (x * 1.2, bundle_y + 0.3, 0.9), (x * 1.3, bundle_y + 0.42, 1.08)]
        a.add("Base", sh.sweep(fz, 0.02, 4, fuse, samples=5))
    sling = [(0.42, AXIS_Y - 0.1, 1.42), (0.5, AXIS_Y - 0.55, 0.9), (0.48, AXIS_Y - 0.72, 0.0), (0.5, AXIS_Y - 0.55, -1.2), (0.42, AXIS_Y - 0.12, -1.98)]
    a.add("Base", sh.sweep(sling, 0.045, 4, leather, samples=14))
    scope = sh.lathe([(0, -0.34), (0.1, -0.34), (0.1, -0.24), (0.075, -0.2), (0.075, 0.2), (0.11, 0.26), (0.11, 0.34), (0, 0.34)], 12, ring_plain, smooth_angle=35)
    a.add("Base", forward(scope, x=-0.38, y=AXIS_Y + 0.62, z=-0.9))
    for z in (-0.75, -1.05):
        a.add("Base", sh.box((0.08, 0.22, 0.08), ring_plain).transformed(T(-0.36, AXIS_Y + 0.47, z)))
    a.add("Glow", forward(sh.cylinder(0.075, 0.01, None, bevel=0.0, segments=10), x=-0.38, y=AXIS_Y + 0.62, z=-1.25))
    a.point("muzzle", (0, AXIS_Y, -2.2))
    a.point("grip", (0, -0.1, 0))
    return a


def sh_scale(x, y, z):
    from wr3d import S
    return S(x, y, z)
