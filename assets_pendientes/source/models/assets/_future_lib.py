import numpy as np

from wr3d import Material, register
from wr3d.materials import Surface, rgb, grime_amount, scratch_mask
from wr3d.noise import smoothstep, mix

CYAN = (34, 225, 255)
VIOLET = (166, 77, 255)
PINK = (255, 59, 160)
PEARL = (232, 236, 244)
GRAPHITE = (30, 34, 46)
INK = (14, 16, 22)


@register("future_panel")
def future_panel(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", PEARL))
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    size = p.get("panel", 1.6)
    gap = p.get("gap", 0.03)
    fu = (u / size + 0.5) % 1.0
    fv = (v / (size * 0.6) + 0.5) % 1.0
    du = np.minimum(fu, 1 - fu) * size
    dv = np.minimum(fv, 1 - fv) * size * 0.6
    seam = 1 - smoothstep(gap * 0.5, gap, np.minimum(du, dv))
    var = ctx.noise(1.5, 3, 101)
    fine = ctx.noise(30.0, 2, 102)
    tile = smoothstep(-0.2, 0.2, ctx.noise(0.8, 2, 103))
    scr = scratch_mask(ctx, p.get("scratches", 0.15))
    rim = smoothstep(0.5, 1.0, np.clip(ctx.E, 0, 1))
    tone = 0.92 + 0.05 * var + 0.03 * fine + 0.03 * tile - seam * 0.5
    s.base = np.clip(color[None, :] * tone[:, None] + (rim * 0.08)[:, None], 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(p.get("rough", 0.22) + 0.06 * fine + seam * 0.3 + scr * 0.2, 0, 1)
    s.metal = np.full(ctx.n, p.get("metal", 0.1))
    s.height = -seam * 0.006 + fine * 0.0003 - scr * 0.0006
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.12)) + seam * 0.15, 0, 0.85)
    return s


def pearl(decals=(), **params):
    base = dict(color=PEARL, panel=1.6, dirt=0.12)
    base.update(params)
    return Material("future_panel", decals=list(decals), **base)


def graphite(decals=(), **params):
    base = dict(color=GRAPHITE, panel=1.2, rough=0.3, metal=0.5, dirt=0.15)
    base.update(params)
    return Material("future_panel", decals=list(decals), **base)


def glow_lines(width, height, color, count=3, thickness=0.06, vertical=False):
    out = []
    for k in range(count):
        t = (k + 1) / (count + 1)
        if vertical:
            out.append({"type": "rect", "center": (-width / 2 + t * width, 0.0), "size": (thickness, height * 0.9), "color": color, "rough": 0.1, "wear": 0.0})
        else:
            out.append({"type": "rect", "center": (0.0, -height / 2 + t * height), "size": (width * 0.9, thickness), "color": color, "rough": 0.1, "wear": 0.0})
    return out
