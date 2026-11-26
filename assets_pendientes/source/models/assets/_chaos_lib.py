import numpy as np

from wr3d import Material, register, T, R, S, compose
from wr3d import shapes as sh
from wr3d.materials import Surface, rgb, grime_amount
from wr3d.noise import smoothstep, mix, ridged

VIOLET = (166, 77, 255)
PINK = (255, 59, 160)
CYAN = (34, 225, 255)
ALIEN = (60, 220, 160)
BASALT = (34, 30, 40)


@register("chaos_basalt")
def chaos_basalt(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", BASALT))
    glow = rgb(p.get("glow", VIOLET))
    n = ctx.noise(1.2, 5, 111)
    fine = ctx.noise(14.0, 3, 112)
    cracks = ridged(ctx.Ps * p.get("crack_scale", 0.9), 4, 2.0, 0.5, 113)
    vein = smoothstep(p.get("veins", 0.82), 0.97, cracks)
    tone = 0.75 + 0.3 * n + 0.1 * fine
    base = color[None, :] * tone[:, None]
    base = mix(base, glow[None, :] * 0.9, vein * p.get("vein_glow", 0.85))
    s.base = np.clip(base, 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.78 + 0.1 * fine - vein * 0.5, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = n * 0.01 + fine * 0.003 - vein * 0.01
    s.dirt = grime_amount(ctx, p.get("dirt", 0.2))
    return s


@register("chaos_obsidian")
def chaos_obsidian(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (14, 10, 22)))
    glow = rgb(p.get("glow", PINK))
    sheen = 0.5 + 0.5 * np.sin(ctx.noise(0.8, 3, 121) * 6.0)
    fine = ctx.noise(20.0, 2, 122)
    rim = smoothstep(0.4, 1.0, np.clip(ctx.E, 0, 1))
    s.base = np.clip(color[None, :] * (0.9 + 0.25 * sheen + 0.05 * fine)[:, None] + glow[None, :] * (rim * p.get("rim_glow", 0.35))[:, None], 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.08 + 0.06 * fine, 0, 1)
    s.metal = np.full(ctx.n, 0.2)
    s.height = fine * 0.0006
    s.dirt = np.zeros(ctx.n)
    return s


def basalt(decals=(), **params):
    return Material("chaos_basalt", decals=list(decals), **params)


def obsidian(decals=(), **params):
    return Material("chaos_obsidian", decals=list(decals), **params)


def rock(radius, mat, seed, squash=(1.0, 0.7, 1.0), jitter=0.16, segments=8, rings=5):
    mesh = sh.sphere(radius, mat, segments, rings)
    rng = np.random.default_rng(seed)
    mesh.pos *= 1 + rng.normal(0, jitter, (len(mesh.pos), 1))
    mesh.pos *= np.asarray(squash)
    mesh = sh.recompute_normals(mesh)
    return mesh


def grounded(mesh, floor=0.0):
    out = mesh.copy()
    out.pos[:, 1] = np.maximum(out.pos[:, 1], floor)
    return sh.recompute_normals(out)


def crystal(radius, height, mat, facets=6, crown=0.35):
    return sh.gem(radius, height, facets, mat, crown=crown)


def crystal_cluster(mat, seed, count, base_radius, height, spread, tilt=24.0):
    rng = np.random.default_rng(seed)
    out = []
    for k in range(count):
        ang = rng.uniform(0, 360)
        dist = spread * (0.0 if k == 0 else rng.uniform(0.45, 1.0))
        h = height * (1.0 if k == 0 else rng.uniform(0.35, 0.7))
        r = base_radius * (1.0 if k == 0 else rng.uniform(0.4, 0.65))
        lean = 0.0 if k == 0 else rng.uniform(tilt * 0.6, tilt)
        place = compose(R(0, ang, 0), T(dist, 0, 0), R(0, 0, -lean), T(0, h / 2 - r * 0.4, 0))
        out.append(crystal(r, h, mat).transformed(place))
    return out
