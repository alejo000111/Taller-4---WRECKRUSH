import numpy as np

from wr3d import Asset, Material, register, T, R, compose
from wr3d import shapes as sh
from wr3d.mesh import flat_shaded
from wr3d.materials import Surface, grime_amount, scratch_mask, rgb
from wr3d.noise import worley, smoothstep, ridged
from _launch_lib import pistol_grip, trigger_group, side_profile

AXIS_Y = 1.05
VOID = (14, 10, 22)
PURPLE = (150, 70, 255)


@register("void_obsidian")
def void_obsidian(ctx, p):
    s = Surface(ctx.n)
    f1, f2, cell = worley(ctx.Ps * p.get("cell_scale", 7.0), 81)
    seam = 1 - smoothstep(0.0, 0.07, f2 - f1)
    facet = ((cell & 255) / 255.0) * 0.18
    vein = smoothstep(0.82, 0.97, ridged(ctx.Ps * 2.6, 4, 2.0, 0.5, 82)) * p.get("veins", 0.8)
    sheen = smoothstep(0.2, 0.9, ctx.E)
    s.paint = np.clip(1 - vein - seam * 0.6, 0, 1)
    s.tint = np.clip(0.8 + facet + sheen * 0.2, 0, 1)
    vein_col = rgb(p.get("vein_color", (176, 110, 255)))
    s.base = np.clip(vein_col[None, :] * (0.6 + 0.4 * vein)[:, None] * vein[:, None] + rgb((40, 30, 60))[None, :] * seam[:, None], 0, 1)
    s.rough = np.clip(0.12 + 0.1 * seam + 0.05 * facet - 0.04 * sheen, 0.04, 1)
    s.metal = np.full(ctx.n, 0.45)
    s.height = -seam * 0.004 + facet * 0.002 - scratch_mask(ctx, 0.15) * 0.0006
    s.dirt = grime_amount(ctx, p.get("dirt", 0.1))
    return s


def forward(mesh, x=0.0, y=AXIS_Y, z=0.0):
    return mesh.transformed(compose(T(x, y, z), R(-90, 0, 0)))


def octagon_ring(radius, thickness, z):
    a = np.radians(22.5) + np.linspace(0, 2 * np.pi, 8, endpoint=False)
    pts = [(np.cos(t) * radius, AXIS_Y + np.sin(t) * radius, z) for t in a]
    path = []
    for i in range(8):
        p0, p1 = np.array(pts[i]), np.array(pts[(i + 1) % 8])
        for t in np.linspace(0, 1, 2, endpoint=False):
            path.append(p0 * (1 - t) + p1 * t)
    return sh.sweep(path, thickness, 4, None, closed=True)


def build():
    a = Asset("VoidBlaster", budget=8000, ao_radius=0.35)
    a.role("Primary", "surface", color=VOID, skin="Primary")
    a.role("AccentGlow", "neon", color=PURPLE, skin="Accent")
    a.role("Aura", "neon", color=(120, 40, 255), transparency=0.7)
    a.role("Base", "surface")

    obsidian = Material("void_obsidian", color=VOID, skin=True)
    crystal = Material("void_obsidian", color=VOID, skin=True, cell_scale=4.0, veins=0.4)
    dark = Material("metal", color=(24, 20, 34), rough=0.3, polish=0.7, dirt=0.15, skin=False)
    chrome = Material("chrome", color=(200, 196, 220), rough=0.12)
    rubber = Material("rubber", color=(18, 16, 22), pattern="knurl", freq=13.0)

    a.add("Base", pistol_grip(dark, rubber, dark, chrome, width=0.42))
    a.add("Base", trigger_group(dark, chrome))

    body_poly = [(-1.4, 0.55), (-1.4, 1.35), (-1.1, 1.62), (0.2, 1.62), (0.62, 1.42), (0.75, 1.1), (0.62, 0.62), (0.2, 0.48), (-1.1, 0.45)]
    body = side_profile(body_poly, 1.16, obsidian, bevel=0.05, corner_radius=0.0, corner_segments=1)
    a.add("Primary", flat_shaded(body))
    armor_poly = [(-1.0, 1.58), (0.1, 1.58), (0.4, 1.78), (-0.2, 2.05), (-0.85, 1.96)]
    a.add("Primary", flat_shaded(side_profile(armor_poly, 0.8, obsidian, bevel=0.04, corner_radius=0.0, corner_segments=1)))
    for side in (-1, 1):
        flank = [(-1.2, 0.7), (0.4, 0.7), (0.55, 1.05), (0.4, 1.4), (-1.2, 1.4)]
        plate = side_profile(flank, 0.1, crystal, bevel=0.03, corner_radius=0.0, corner_segments=1).transformed(T(side * 0.62, 0, 0))
        a.add("Primary", flat_shaded(plate))
        for y in (0.82, 1.28):
            path = [(side * 0.68, y, 0.35), (side * 0.69, y + 0.06, 0.05), (side * 0.69, y - 0.05, -0.25), (side * 0.68, y + 0.04, -0.55), (side * 0.66, y, -0.85)]
            a.add("AccentGlow", sh.sweep(path, 0.022, 4, None, samples=8))

    prong_poly = [(z, -y) for z, y in [(0.55, -0.16), (1.5, -0.1), (2.2, 0.02), (2.62, 0.2), (2.84, 0.42), (2.6, 0.34), (2.2, 0.2), (1.5, 0.14), (0.55, 0.16)]]
    for k in range(4):
        prong = side_profile(prong_poly, 0.3, obsidian, bevel=0.04, corner_radius=0.0, corner_segments=1)
        prong = prong.transformed(compose(T(0, AXIS_Y, 0), R(0, 0, k * 90), T(0, 0.62, 0)))
        a.add("Primary", flat_shaded(prong))
    for zc in (-1.1, -1.75):
        a.add("AccentGlow", octagon_ring(0.98, 0.055, zc))
        band = sh.tube(0.7, 0.5, 0.1, dark, bevel=0.0, segments=8)
        a.add("Base", band.transformed(compose(T(0, AXIS_Y, zc), R(90, 22.5, 0))))

    core = sh.sphere(0.36, None, 20, 12)
    core.pos += core.nrm * 0.03 * np.sin(core.pos[:, 1] * 18)[:, None]
    sh.recompute_normals(core)
    a.add("AccentGlow", core.transformed(T(0, AXIS_Y, -2.05)))
    a.add("Aura", sh.sphere(0.56, None, 18, 10).transformed(T(0, AXIS_Y, -2.05)))
    emitter = sh.lathe(sh.round_polyline([(0, 0), (0.3, 0), (0.3, 0.1), (0.2, 0.2), (0, 0.22)], [0, 0, 0.03, 0.03, 0], 1), 10, chrome)
    a.add("Base", forward(emitter, z=-0.72))

    for x, h, tilt in ((-0.3, 0.55, -20), (0.3, 0.55, 20), (0.0, 0.75, 0)):
        spike = sh.gem(0.11, h, 6, crystal).transformed(compose(T(x, 2.0 + h * 0.35, 0.45), R(-25, 0, tilt)))
        a.add("Primary", spike)

    cell = sh.lathe(sh.round_polyline([(0, 0), (0.5, 0), (0.5, 0.26), (0.38, 0.36), (0, 0.36)], [0, 0, 0.03, 0.04, 0], 2), 8, obsidian, smooth_angle=20, start=22.5)
    a.add("Primary", flat_shaded(cell.transformed(compose(T(0, AXIS_Y, 1.42), R(90, 0, 0)))))
    a.add("AccentGlow", sh.cylinder(0.3, 0.03, None, bevel=0.0, segments=10).transformed(compose(T(0, AXIS_Y, 1.8), R(90, 0, 0))))

    for k in range(9):
        ang = np.radians(k * 40)
        shard = sh.gem(0.05 + 0.02 * (k % 2), 0.22, 6, None)
        pos = (np.cos(ang) * 0.78, AXIS_Y + np.sin(ang) * 0.78, -2.05 + 0.12 * np.sin(k * 1.3))
        a.add("AccentGlow", shard.transformed(compose(T(*pos), R(0, 0, np.degrees(ang) - 90))))
    for tilt in (35, -35):
        orbit = sh.torus(0.46, 0.018, None, segments=24, sides=4)
        a.add("AccentGlow", orbit.transformed(compose(T(0, AXIS_Y, -2.05), R(tilt, 0, 60 if tilt > 0 else -60))))
    for zc in (-1.1, -1.75):
        for k in range(8):
            ang = 22.5 + k * 45
            spike = sh.frustum(0.06, 0.0, 0.26, chrome, bevel=0.0, segments=4)
            a.add("Base", spike.transformed(compose(T(0, AXIS_Y, zc), R(0, 0, ang - 90), T(0, 1.12, 0))))
    clusters = ((-0.42, 1.72, 0.9, -30), (0.42, 1.72, 0.9, 30), (-0.5, 1.5, -0.3, -45), (0.5, 1.5, -0.3, 45), (0.0, 0.42, 1.0, 180))
    for x, y, z, tilt in clusters:
        for j, (dx, h) in enumerate(((0.0, 0.42), (0.09, 0.28), (-0.08, 0.22))):
            g = sh.gem(0.07 + 0.02 * (j == 0), h, 6, crystal)
            a.add("Primary", g.transformed(compose(T(x + dx, y, z + dx * 0.6), R(-15 + j * 12, 0, tilt + j * 18), T(0, h * 0.35, 0))))
    for side in (-1, 1):
        a.add("AccentGlow", sh.box((0.035, 0.035, 1.5), None).transformed(T(side * 0.585, 1.6, -0.55)))
        a.add("AccentGlow", sh.box((0.035, 0.035, 1.3), None).transformed(T(side * 0.585, 0.5, -0.45)))
    flare = sh.lathe([(0.0, 0.0), (0.26, 0.0), (0.34, 0.12), (0.44, 0.22), (0.4, 0.26), (0.28, 0.16), (0.0, 0.16)], 16, chrome, smooth_angle=40)
    a.add("Base", forward(flare, z=-2.62))
    a.add("AccentGlow", sh.torus(0.42, 0.025, None, segments=20, sides=4).transformed(compose(T(0, AXIS_Y, -2.86), R(90, 0, 0))))
    a.point("muzzle", (0, AXIS_Y, -2.9))
    a.point("grip", (0, -0.1, 0))
    a.point("core", (0, AXIS_Y, -2.05))
    return a
