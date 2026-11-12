import numpy as np

from wr3d import Asset, Material, register, T, R, compose
from wr3d import shapes as sh
from wr3d.materials import Surface, rgb, grime_amount
from wr3d.noise import smoothstep, mix

WORLDS = "ExpeditionWorlds"
VERDANT = f"{WORLDS}/VerdantFoundry"
FROST = f"{WORLDS}/FrostHarbor"
SKY = f"{WORLDS}/SkyRuins"
GATE = f"{WORLDS}/WorldsGate"
ALL = [VERDANT, FROST, SKY]

PALETTES = {
    "verdant": {"rock": (86, 92, 82), "cap": (74, 104, 58), "cap_amount": 0.55, "accent": (239, 183, 95), "color": (109, 206, 145)},
    "frost": {"rock": (112, 132, 148), "cap": (236, 243, 249), "cap_amount": 0.7, "accent": (239, 153, 94), "color": (129, 207, 230)},
    "sky": {"rock": (92, 90, 116), "cap": (150, 140, 196), "cap_amount": 0.15, "accent": (245, 199, 116), "color": (173, 161, 230)},
}


@register("terrain_rock")
def terrain_rock(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (90, 92, 88)))
    cap = rgb(p.get("cap", (74, 104, 58)))
    broad = ctx.noise(0.25, 4, 801)
    mid = ctx.noise(1.2, 4, 802)
    fine = ctx.noise(9.0, 3, 803)
    strata = 0.5 + 0.5 * np.sin(ctx.P[:, 1] * p.get("strata", 1.4) + broad * 4.0)
    tone = 0.72 + 0.22 * mid + 0.08 * fine + 0.1 * strata
    base = color[None, :] * tone[:, None]
    up = np.clip(ctx.N[:, 1], -1, 1)
    cover = smoothstep(0.35, 0.75, up + mid * 0.35 + broad * 0.2) * p.get("cap_amount", 0.5)
    cap_col = cap[None, :] * (0.85 + 0.2 * fine)[:, None]
    s.base = np.clip(mix(base, cap_col, cover[:, None]), 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.86 + 0.06 * fine - cover * p.get("cap_gloss", 0.1), 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = mid * 0.02 + fine * 0.006 + strata * 0.006 + cover * 0.01
    s.dirt = grime_amount(ctx, p.get("dirt", 0.25))
    return s


def terrain(world, **extra):
    pal = PALETTES[world]
    params = dict(color=pal["rock"], cap=pal["cap"], cap_amount=pal["cap_amount"], dirt=0.25)
    params.update(extra)
    return Material("terrain_rock", **params)


def jagged(mesh, seed, amount=0.12, scale=0.35):
    out = mesh.copy()
    rng = np.random.default_rng(seed)
    phase = rng.uniform(0, 100, 3)
    p = out.pos
    n = np.sin(p[:, 0] * scale * 2.1 + phase[0]) * np.cos(p[:, 2] * scale * 1.7 + phase[1]) + 0.5 * np.sin(p[:, 1] * scale * 2.9 + phase[2])
    n = n + rng.normal(0, 0.35, len(p))
    radial = np.linalg.norm(p, axis=1, keepdims=True)
    out.pos = p * (1 + amount * n[:, None] / np.maximum(radial.mean(), 1e-3) * radial.mean())
    return sh.recompute_normals(out)


def boulder(seed, size, mat, segments=10, rings=6, amount=0.14):
    ball = sh.sphere(1.0, mat, segments, rings)
    rng = np.random.default_rng(seed)
    ball.pos *= 1 + rng.normal(0, amount, (len(ball.pos), 1))
    ball.pos[:, 1] = np.maximum(ball.pos[:, 1], -0.55)
    ball.pos *= np.asarray(size) / 2.0
    ball.pos[:, 1] += size[1] * 0.275
    return sh.recompute_normals(ball)


def expedition_asset(name, budget, radius, atlas=512, front=180):
    a = Asset(name, budget=budget, atlas=atlas, ao_radius=0.6, ao_strength=0.55, edge_width=0.06, gradient=0.08, highlight=0.45, preview_radius=radius,
              views=[("FRONT 3/4", front + 35, 16), ("FRONT", front, 4), ("SIDE", front + 90, 6), ("TOP", front + 20, 50)])
    a.role("Body", "surface")
    return a


@register("foliage")
def foliage(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (72, 112, 64)))
    clumps = ctx.noise(p.get("scale", 2.2), 4, 811)
    fine = ctx.noise(14.0, 3, 812)
    light = smoothstep(-0.3, 0.6, clumps + 0.4 * np.clip(ctx.N[:, 1], -1, 1))
    tone = 0.55 + 0.45 * light + 0.12 * fine
    tip = smoothstep(0.55, 0.9, clumps + fine * 0.3) * p.get("tips", 0.3)
    base = color[None, :] * tone[:, None]
    s.base = np.clip(mix(base, rgb(p.get("tip", (150, 170, 80)))[None, :], tip[:, None]), 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.8 + 0.1 * fine, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = clumps * 0.03 + fine * 0.01
    s.dirt = np.zeros(ctx.n)
    return s


def leaves(color=(72, 112, 64), **extra):
    params = dict(color=color)
    params.update(extra)
    return Material("foliage", **params)
