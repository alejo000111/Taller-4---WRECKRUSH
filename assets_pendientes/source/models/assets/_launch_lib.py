import numpy as np

from wr3d import Material, register, T, R, compose
from wr3d import shapes as sh
from wr3d.noise import fbm, ridged, worley, smoothstep, mix
from wr3d.materials import Surface, wear_mask, scratch_mask, grime_amount, rgb

FORWARD = R(-90, 0, 0)
SIDEWAYS = R(0, 90, 0)


def along_z(mesh, x=0.0, y=0.0, z=0.0):
    return mesh.transformed(compose(T(x, y, z), FORWARD))


def side_profile(poly, width, mat, x=0.0, bevel=0.03, corner_radius=None, corner_segments=1, cap_mats=None):
    m = sh.extrude(poly, width, mat, bevel=bevel, corner_radius=corner_radius, corner_segments=corner_segments, cap_mats=cap_mats)
    return m.transformed(compose(T(x, 0, 0), SIDEWAYS))


def ring_points(count, radius, start=0.0):
    a = np.radians(start) + np.linspace(0, 2 * np.pi, count, endpoint=False)
    return np.stack([np.cos(a) * radius, np.sin(a) * radius], 1)


def bolt_ring(center, radius, count, mat, size=0.045, height=0.03, start=0.0, face=-1, kind="bolt"):
    cx, cy, cz = center
    out = []
    for px, py in ring_points(count, radius, start):
        if kind == "bolt":
            b = sh.bolt(size, height, mat)
        else:
            b = sh.rivet(size, height, mat)
        out.append(b.transformed(compose(T(cx + px, cy + py, cz + face * height * 0.5), R(-90 * face, 0, 0))))
    return out


def radial_bolts(center, radius, count, mat, size=0.04, height=0.03, start=0.0, length_axis="z", kind="bolt"):
    cx, cy, cz = center
    out = []
    for a in np.radians(start) + np.linspace(0, 2 * np.pi, count, endpoint=False):
        d = np.array([np.cos(a), np.sin(a), 0.0])
        b = sh.bolt(size, height, mat) if kind == "bolt" else sh.rivet(size, height, mat)
        from wr3d import align_y
        out.append(b.transformed(compose(T(cx + d[0] * (radius + height * 0.35), cy + d[1] * (radius + height * 0.35), cz), align_y(d))))
    return out


GRIP_OUTLINE = [
    (0.23, 0.64), (0.25, 0.42), (0.2, 0.33), (0.25, 0.2), (0.2, 0.08), (0.25, -0.05), (0.2, -0.17),
    (0.25, -0.3), (0.23, -0.5), (0.28, -0.6), (0.27, -0.7), (-0.33, -0.7), (-0.34, -0.6),
    (-0.29, -0.5), (-0.33, -0.15), (-0.29, 0.25), (-0.27, 0.64),
]

GRIP_PANEL = [
    (0.17, 0.38), (0.14, 0.33), (0.19, 0.2), (0.14, 0.08), (0.19, -0.05), (0.14, -0.17), (0.18, -0.3),
    (0.16, -0.48), (-0.24, -0.48), (-0.27, -0.15), (-0.23, 0.25), (-0.21, 0.38),
]


def pistol_grip(frame_mat, panel_mat, cap_mat, screw_mat, width=0.38):
    parts = []
    parts.append(side_profile(GRIP_OUTLINE, width, frame_mat, bevel=0.04, corner_radius=0.0))
    parts.append(side_profile(GRIP_PANEL, width + 0.07, panel_mat, bevel=0.025, corner_radius=0.0))
    base = sh.rounded_box((width + 0.08, 0.1, 0.66), 0.035, 1, cap_mat).transformed(T(0, -0.72, 0.03))
    parts.append(base)
    return parts


TRIGGER_GUARD = [(0.2, 0.15), (0.5, 0.15), (0.66, 0.28), (0.66, 0.66), (0.57, 0.66), (0.57, 0.32), (0.48, 0.24), (0.2, 0.24)]
TRIGGER = [(0.27, 0.66), (0.37, 0.66), (0.37, 0.52), (0.34, 0.42), (0.28, 0.35), (0.255, 0.39), (0.29, 0.47), (0.29, 0.58)]


def trigger_group(guard_mat, trigger_mat):
    guard = side_profile(TRIGGER_GUARD, 0.11, guard_mat, bevel=0.02, corner_radius=0.0)
    trig = side_profile(TRIGGER, 0.08, trigger_mat, bevel=0.015, corner_radius=0.0)
    return [guard, trig]


@register("launch_paper")
def _paper(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (214, 40, 36)))
    fiber = ctx.noise_aniso(np.array([90.0, 6.0, 6.0]), 2, 3)
    wrinkle = ridged(ctx.Ps * p.get("wrinkle_scale", 5.0), 3, 2.0, 0.5, 41)
    blot = ctx.noise(2.5, 4, 42)
    fray = smoothstep(0.55, 1.0, ctx.E) * (0.6 + 0.4 * ctx.noise(30.0, 2, 43))
    tone = 0.9 + 0.06 * fiber + 0.08 * blot - 0.12 * smoothstep(0.6, 0.95, wrinkle) - 0.18 * fray
    s.base = np.clip(color[None, :] * tone[:, None], 0, 1)
    s.base = mix(s.base, rgb(p.get("fade", (240, 200, 160))), fray * 0.35)
    s.rough = np.clip(0.8 + 0.06 * fiber, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = wrinkle * 0.0022 + fiber * 0.0003
    s.dirt = grime_amount(ctx, p.get("dirt", 0.25))
    return s


@register("launch_leather")
def _leather(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (92, 58, 36)))
    f1, f2, _ = worley(ctx.Ps * p.get("grain", 26.0), 44)
    pores = smoothstep(0.0, 0.25, f2 - f1)
    blot = ctx.noise(3.0, 4, 45)
    rub = smoothstep(0.25, 0.9, ctx.E) * 0.6 + smoothstep(0.2, 0.7, ctx.noise(4.0, 3, 46)) * 0.25
    tone = 0.82 + 0.16 * pores + 0.1 * blot + 0.3 * rub
    s.base = np.clip(color[None, :] * tone[:, None], 0, 1)
    s.rough = np.clip(0.62 - 0.2 * rub + 0.1 * (1 - pores), 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = pores * 0.0016 + blot * 0.0006
    s.dirt = grime_amount(ctx, p.get("dirt", 0.35))
    return s


@register("launch_armor")
def _armor(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (40, 44, 58)))
    under = rgb(p.get("under", (120, 128, 140)))
    wear = wear_mask(ctx, p.get("wear", 0.35))
    scr = scratch_mask(ctx, p.get("scratches", 0.3))
    var = ctx.noise(2.0, 3, 47)
    groove = np.zeros(ctx.n)
    width = p.get("line_width", 0.012)
    for axis, values in ((2, p.get("lines_z", ())), (1, p.get("lines_y", ())), (0, p.get("lines_x", ()))):
        for v in values:
            d = np.abs(ctx.P[:, axis] - v)
            groove = np.maximum(groove, 1 - smoothstep(width * 0.5, width, d))
    s.paint = (1 - wear) * (1 - scr * 0.6) * (1 - groove)
    s.tint = np.clip(0.94 + 0.06 * var - scr * 0.12, 0, 1)
    s.base = np.clip(under[None, :] * (0.9 + 0.12 * ctx.noise(9.0, 3, 48))[:, None], 0, 1)
    s.base = mix(s.base, rgb((14, 15, 20)), groove)
    s.rough = np.clip(p.get("rough", 0.36) + 0.06 * var, 0.05, 1)
    s.rough = mix(s.rough, 0.28, wear)
    s.metal = mix(np.full(ctx.n, p.get("metal", 0.15)), 1.0, np.maximum(wear, scr * 0.5) * (1 - groove))
    s.metal = s.metal * (1 - groove)
    s.height = ctx.noise(50.0, 2, 49) * 0.0002 - wear * 0.003 - scr * 0.001 - groove * 0.006
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.3)) + groove * 0.3, 0, 0.9)
    return s
