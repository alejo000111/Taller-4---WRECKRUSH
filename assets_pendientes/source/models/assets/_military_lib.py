import os
import tempfile

import numpy as np
from PIL import Image, ImageDraw

from wr3d import Material, register
from wr3d.materials import Surface, rgb, grime_amount, wear_mask, scratch_mask
from wr3d.noise import smoothstep, mix

OLIVE = (86, 100, 56)
OLIVE_DARK = (58, 66, 40)
SAND = (186, 166, 120)
KHAKI = (150, 136, 98)
STENCIL = (232, 224, 196)
YELLOW = (255, 210, 31)
INK = (22, 22, 20)
RED = (200, 44, 36)


def olive(color=OLIVE, decals=(), **params):
    base = dict(under=(110, 104, 92), wear=0.35, scratches=0.4, rough=0.6, metal=0.05, dirt=0.5, dirt_color=(84, 70, 50), skin=False)
    base.update(params)
    return Material("paint", color=color, decals=list(decals), **base)


def camo_metal(decals=(), **params):
    base = dict(wear=0.35, dirt=0.5)
    base.update(params)
    return Material("military_camo", decals=list(decals), **base)


@register("military_camo")
def military_camo(ctx, p):
    s = Surface(ctx.n)
    colors = [rgb(c) for c in p.get("colors", [OLIVE, OLIVE_DARK, (120, 110, 76), (40, 42, 34)])]
    scale = p.get("scale", 0.35)
    n1 = ctx.noise(scale, 4, 91)
    n2 = ctx.noise(scale * 1.7, 4, 92)
    base = np.tile(colors[0], (ctx.n, 1))
    base = mix(base, np.tile(colors[1], (ctx.n, 1)), smoothstep(0.08, 0.12, n1))
    base = mix(base, np.tile(colors[2], (ctx.n, 1)), smoothstep(0.12, 0.16, n2) * (1 - smoothstep(0.08, 0.12, n1)))
    base = mix(base, np.tile(colors[3], (ctx.n, 1)), smoothstep(0.28, 0.32, n1 + 0.4 * n2))
    var = ctx.noise(4.0, 3, 93)
    wear = wear_mask(ctx, p.get("wear", 0.35))
    scr = scratch_mask(ctx, p.get("scratches", 0.35))
    bare = np.maximum(wear, scr * 0.6)
    s.base = np.clip(mix(base * (0.92 + 0.12 * var)[:, None], rgb((120, 118, 110)), bare * 0.8), 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.66 + 0.06 * var - bare * 0.25, 0, 1)
    s.metal = np.clip(bare * 0.7, 0, 1)
    s.height = ctx.noise(30.0, 2, 94) * 0.0005 - bare * 0.003
    mud = (1 - smoothstep(0.3, p.get("mud", 2.0), ctx.P[:, 1])) * (0.5 + 0.5 * smoothstep(-0.3, 0.3, ctx.noise(1.2, 3, 95)))
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.45)) + mud * 0.6, 0, 0.85)
    return s


@register("military_burlap")
def military_burlap(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", SAND))
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    weave = 0.5 + 0.5 * np.sin(u * 90) * np.sin(v * 90)
    var = ctx.noise(2.5, 4, 96)
    patch = smoothstep(0.1, 0.5, ctx.noise(0.8, 3, 97))
    tone = 0.82 + 0.1 * weave + 0.12 * var - 0.08 * patch
    s.base = np.clip(color[None, :] * tone[:, None], 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.92 - 0.05 * weave, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = weave * 0.0015 + var * 0.003
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.5)) + (1 - smoothstep(0.0, 1.2, ctx.P[:, 1])) * 0.4, 0, 0.85)
    return s


def star_mask(size=256):
    path = os.path.join(tempfile.gettempdir(), f"wr_star_{size}.png")
    if not os.path.exists(path):
        img = Image.new("L", (size, size), 0)
        c = size / 2
        pts = []
        for k in range(10):
            r = size * (0.48 if k % 2 == 0 else 0.19)
            a = np.radians(-90 + k * 36)
            pts.append((c + r * np.cos(a), c + r * np.sin(a)))
        ImageDraw.Draw(img).polygon(pts, fill=255)
        img.save(path)
    return path


def star(center, size, color, wear=0.4, angle=0.0):
    return [{"type": "image", "path": star_mask(), "center": center, "size": size, "color": color, "wear": wear, "angle": angle}]


@register("military_track")
def military_track(ctx, p):
    s = Surface(ctx.n)
    pitch = p.get("pitch", 0.42)
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    t = (u / pitch) % 1.0
    link = smoothstep(0.08, 0.16, t) * (1 - smoothstep(0.84, 0.92, t))
    grouser = 1 - smoothstep(0.03, 0.08, np.abs(t - 0.5))
    pin = 1 - smoothstep(0.08, 0.14, np.abs(((v / p.get("width", 2.2)) % 1.0) - 0.5))
    var = ctx.noise(5.0, 3, 98)
    worn = smoothstep(0.4, 1.0, np.clip(ctx.E, 0, 1)) * 0.5 + grouser * 0.3
    tone = 0.28 + 0.12 * link + 0.08 * var + worn * 0.35
    s.base = np.clip(np.stack([tone * 0.95, tone * 0.93, tone * 0.9], 1), 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.7 - worn * 0.3, 0, 1)
    s.metal = np.clip(0.5 + worn * 0.4, 0, 1)
    s.height = link * 0.02 + grouser * 0.025 - (1 - link) * 0.01 + pin * 0.002
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.6)) + (1 - link) * 0.4, 0, 0.85)
    return s
