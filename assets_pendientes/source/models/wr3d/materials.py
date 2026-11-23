import os

import numpy as np

from .noise import fbm, perlin, ridged, worley, worley2, smoothstep, mix, hash3

REGISTRY = {}


def register(name):
    def wrap(fn):
        REGISTRY[name] = fn
        return fn
    return wrap


class Material:
    def __init__(self, kind, **params):
        self.kind = kind
        self.params = params

    def but(self, **params):
        merged = dict(self.params)
        merged.update(params)
        return Material(self.kind, **merged)

    def __repr__(self):
        return f"Material({self.kind})"


def rgb(c):
    c = np.asarray(c, dtype=np.float64)
    return c / 255.0 if c.max() > 1.0 else c


class Ctx:
    def __init__(self, P, N, U, E, AO, seed, texel):
        self.P = P
        self.N = N
        self.U = U
        self.E = E
        self.AO = AO
        self.seed = seed
        self.texel = texel
        self.n = len(P)
        offs = np.stack([(seed * 0.0137) % 97.0, (seed * 0.0291) % 89.0, (seed * 0.0173) % 83.0], 1)
        self.Ps = P + offs

    def noise(self, scale, octaves=4, offset=0, gain=0.5):
        return fbm(self.Ps * scale + offset * 31.7, octaves, 2.0, gain, int(offset))

    def noise_aniso(self, scale_vec, octaves=3, offset=0):
        return fbm(self.Ps * np.asarray(scale_vec) + offset * 13.3, octaves, 2.0, 0.5, int(offset) + 5)

    def uv_noise(self, scale, octaves=3, offset=0):
        p = np.column_stack([self.U * scale, (self.seed % 1000.0) * 0.731 + offset])
        return fbm(p, octaves, 2.0, 0.5, int(offset) + 11)


class Surface:
    def __init__(self, n):
        self.base = np.full((n, 3), 0.5)
        self.paint = np.zeros(n)
        self.tint = np.ones(n)
        self.rough = np.full(n, 0.5)
        self.metal = np.zeros(n)
        self.height = np.zeros(n)
        self.dirt = np.zeros(n)


def wear_mask(ctx, amount, scale=1.0):
    if amount <= 0:
        return np.zeros(ctx.n)
    n1 = ctx.noise(7.0 * scale, 4, 3)
    n2 = ctx.noise(23.0 * scale, 3, 4)
    e = np.clip(ctx.E, 0, 1) ** 0.8
    m = e * (0.85 + 0.55 * n1) + 0.22 * n2 * e
    t = 1.08 - amount * 0.8
    edge_chips = smoothstep(t - 0.05, t + 0.05, m)
    spots = smoothstep(0.58 - amount * 0.12, 0.64 - amount * 0.12, ctx.noise(11.0 * scale, 3, 9)) * amount * 0.8
    return np.clip(np.maximum(edge_chips, spots * smoothstep(0.1, 0.6, n2 + 0.5)), 0, 1)


def scratch_mask(ctx, amount, scale=1.0):
    if amount <= 0:
        return np.zeros(ctx.n)
    total = np.zeros(ctx.n)
    rots = [np.array([[0.8, 0.6, 0.0], [-0.6, 0.8, 0.0], [0.0, 0.0, 1.0]]), np.array([[0.2, 0.0, 0.98], [0.0, 1.0, 0.0], [-0.98, 0.0, 0.2]])]
    for k, rot in enumerate(rots):
        q = ctx.Ps @ rot.T
        line = np.abs(perlin(q * np.array([30.0, 1.4, 1.4]) * scale, 70 + k))
        s = 1.0 - smoothstep(0.0, 0.035, line)
        gate = smoothstep(0.15, 0.45, ctx.noise(1.7 * scale, 2, 40 + k))
        total = np.maximum(total, s * gate)
    return np.clip(total * amount, 0, 1)


def grime_amount(ctx, amount):
    if amount <= 0:
        return np.zeros(ctx.n)
    cav = np.clip(1.0 - ctx.AO, 0, 1) ** 1.1
    blotch = smoothstep(0.1, 0.7, ctx.noise(2.6, 4, 21)) * 0.35
    return np.clip((cav * 1.4 + blotch * (0.4 + cav)) * amount, 0, 0.85)


@register("paint")
def _paint(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (200, 200, 200)))
    under = rgb(p.get("under", (150, 152, 158)))
    wear = wear_mask(ctx, p.get("wear", 0.45), p.get("wear_scale", 1.0))
    scr = scratch_mask(ctx, p.get("scratches", 0.35))
    var = ctx.noise(2.2, 3, 1)
    s.paint = (1.0 - wear) * (1.0 - scr * 0.6)
    s.tint = np.clip(0.95 + 0.06 * var - scr * 0.15, 0, 1)
    metal_var = ctx.noise(9.0, 3, 2)
    s.base = np.clip(under[None, :] * (0.88 + 0.16 * metal_var)[:, None], 0, 1)
    s.base = mix(s.base, color[None, :] * 0.55, (1 - wear) * scr * 0.5)
    s.rough = np.clip(p.get("rough", 0.42) + 0.07 * var, 0.05, 1)
    s.rough = mix(s.rough, 0.3, wear)
    s.metal = mix(np.full(ctx.n, p.get("metal", 0.08)), 1.0, np.maximum(wear, scr * 0.5))
    peel = ctx.noise(55.0, 2, 3) * 0.00025
    s.height = peel - wear * p.get("chip_depth", 0.004) - scr * 0.0012
    s.dirt = grime_amount(ctx, p.get("dirt", 0.35))
    return s


@register("metal")
def _metal(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (168, 170, 178)))
    var = ctx.noise(3.0, 4, 5)
    fine = ctx.noise(18.0, 3, 6)
    brushed = p.get("brushed", False)
    if brushed:
        streak = ctx.uv_noise(np.array([1.2, 60.0]), 3, 7)
    else:
        streak = np.zeros(ctx.n)
    polish = smoothstep(0.25, 0.9, np.clip(ctx.E, 0, 1)) * p.get("polish", 0.6)
    hammered = p.get("hammered", 0.0)
    dent = np.zeros(ctx.n)
    if hammered > 0:
        f1, f2, _ = worley(ctx.Ps * p.get("hammer_scale", 9.0), 12)
        dent = (f2 - f1)
        dent = smoothstep(0.0, 0.35, dent)
    shade = 0.9 + 0.08 * var + 0.05 * fine + 0.06 * streak + polish * 0.18
    s.base = np.clip(color[None, :] * shade[:, None], 0, 1)
    s.paint = np.full(ctx.n, 1.0) * (1 - polish * 0.7)
    s.tint = np.clip(shade, 0, 1)
    s.rough = np.clip(p.get("rough", 0.34) + 0.08 * fine + 0.1 * streak - polish * 0.15 + 0.12 * hammered * (1 - dent), 0.04, 1)
    s.metal = np.full(ctx.n, p.get("metal", 1.0))
    s.height = 0.0006 * streak + hammered * 0.006 * (dent - 0.5) + scratch_mask(ctx, p.get("scratches", 0.25)) * -0.001
    s.dirt = grime_amount(ctx, p.get("dirt", 0.3))
    return s


@register("rubber")
def _rubber(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (30, 30, 34)))
    pattern = p.get("pattern", "ribs")
    freq = p.get("freq", 9.0)
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    if pattern == "ribs":
        h = np.abs(np.sin(v * freq * np.pi))
        h = smoothstep(0.15, 0.6, h)
    elif pattern == "knurl":
        a = np.sin((u + v) * freq * np.pi)
        b = np.sin((u - v) * freq * np.pi)
        h = smoothstep(-0.2, 0.6, np.minimum(a, b))
    elif pattern == "dots":
        f1, _, _ = worley2(ctx.U * freq, 3, 0.15)
        h = 1 - smoothstep(0.18, 0.32, f1)
    else:
        h = np.zeros(ctx.n)
    var = ctx.noise(6.0, 3, 8)
    wear = smoothstep(0.4, 1.0, ctx.E) * 0.5
    s.base = np.clip(color[None, :] * (0.9 + 0.12 * var + 0.25 * wear)[:, None] * (0.85 + 0.25 * h)[:, None], 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(p.get("rough", 0.82) - 0.15 * wear - 0.08 * h, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = h * p.get("depth", 0.012) + var * 0.0004
    s.dirt = grime_amount(ctx, p.get("dirt", 0.25))
    return s


@register("wood")
def _wood(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (128, 86, 52)))
    axis = {"x": 0, "y": 1, "z": 2}[p.get("axis", "y")]
    other = [i for i in range(3) if i != axis]
    q = ctx.Ps.copy()
    warp = ctx.noise(1.5, 3, 15) * 0.6
    radial = np.sqrt(q[:, other[0]] ** 2 + q[:, other[1]] ** 2) * p.get("ring_freq", 22.0) + warp * 4 + q[:, axis] * 0.6
    rings = 0.5 + 0.5 * np.sin(radial)
    rings = smoothstep(0.2, 0.95, rings)
    stretch = np.ones(3) * 40.0
    stretch[axis] = 1.5
    streaks = ctx.noise_aniso(stretch, 3, 16)
    tone = 0.78 + 0.18 * rings + 0.12 * streaks
    rub = smoothstep(0.3, 0.9, ctx.E) * 0.25
    s.base = np.clip(color[None, :] * (tone + rub)[:, None], 0, 1)
    s.base = mix(s.base, color[None, :] * 0.55, smoothstep(0.55, 0.9, ctx.noise(9.0, 3, 17)) * 0.35)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(p.get("rough", 0.62) + 0.1 * streaks - rub * 0.3, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = (rings - 0.5) * 0.0015 + streaks * 0.0008
    s.dirt = grime_amount(ctx, p.get("dirt", 0.35))
    return s


@register("wrap")
def _wrap(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (46, 40, 36)))
    width = p.get("width", 0.16)
    slope = p.get("slope", 0.35)
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    phase = (v + u * slope) / width
    f = phase - np.floor(phase)
    seam = 1 - smoothstep(0.0, 0.12, f)
    lift = smoothstep(0.0, 0.85, f)
    weave = 0.5 + 0.5 * np.sin(u * 140) * np.sin(v * 140)
    var = ctx.noise(4.0, 3, 18)
    s.base = np.clip(color[None, :] * (0.82 + 0.2 * lift - 0.35 * seam + 0.08 * weave + 0.1 * var)[:, None], 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(p.get("rough", 0.78) + 0.1 * seam - 0.05 * weave, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = lift * 0.006 - seam * 0.004 + weave * 0.0006
    s.dirt = grime_amount(ctx, p.get("dirt", 0.45))
    return s


@register("gold")
def _gold(ctx, p):
    q = dict(color=p.get("color", (255, 196, 64)), rough=p.get("rough", 0.24), polish=0.8, scratches=p.get("scratches", 0.2), dirt=p.get("dirt", 0.15))
    s = _metal(ctx, q)
    patina = np.clip(1 - ctx.AO, 0, 1) * 0.8
    s.base = mix(s.base, rgb((120, 70, 20)), patina * 0.5)
    return s


@register("chrome")
def _chrome(ctx, p):
    s = _metal(ctx, dict(color=p.get("color", (232, 234, 240)), rough=p.get("rough", 0.08), polish=0.3, scratches=0.1, dirt=p.get("dirt", 0.1)))
    return s


@register("plastic")
def _plastic(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (210, 210, 214)))
    var = ctx.noise(3.0, 3, 19)
    scuff = smoothstep(0.35, 1.0, ctx.E) * p.get("scuff", 0.5) * smoothstep(-0.2, 0.4, ctx.noise(12.0, 3, 20))
    scr = scratch_mask(ctx, p.get("scratches", 0.2))
    s.base = np.clip(color[None, :] * (0.95 + 0.05 * var)[:, None] + (scuff * 0.18)[:, None], 0, 1)
    s.paint = np.full(ctx.n, 1.0) * (1 - scuff * 0.8)
    s.tint = np.clip(0.96 + 0.04 * var - scr * 0.1, 0, 1)
    s.rough = np.clip(p.get("rough", 0.45) + 0.06 * var + scuff * 0.2, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = ctx.noise(60.0, 2, 21) * 0.0002 - scr * 0.0006
    s.dirt = grime_amount(ctx, p.get("dirt", 0.3))
    return s


@register("glossy")
def _glossy(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (20, 22, 30)))
    var = ctx.noise(4.0, 3, 22)
    s.base = np.clip(color[None, :] * (0.95 + 0.1 * var)[:, None], 0, 1)
    s.rough = np.clip(p.get("rough", 0.12) + 0.04 * var, 0, 1)
    s.metal = np.full(ctx.n, p.get("metal", 0.0))
    s.height = np.zeros(ctx.n)
    s.dirt = grime_amount(ctx, p.get("dirt", 0.1))
    return s


@register("hazard")
def _hazard(ctx, p):
    s = _paint(ctx, dict(p, color=(255, 255, 255)))
    c1 = rgb(p.get("color", (255, 206, 30)))
    c2 = rgb(p.get("color2", (24, 24, 28)))
    width = p.get("width", 0.22)
    ang = np.radians(p.get("angle", 45.0))
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    t = (u * np.cos(ang) + v * np.sin(ang)) / width
    stripe = smoothstep(0.47, 0.53, np.abs((t % 2.0) - 1.0))
    col = mix(c2[None, :].repeat(ctx.n, 0), c1[None, :].repeat(ctx.n, 0), stripe)
    painted = s.paint.copy()
    s.base = mix(s.base, col * s.tint[:, None], painted)
    s.paint = np.zeros(ctx.n)
    return s


@register("carbon")
def _carbon(ctx, p):
    s = Surface(ctx.n)
    scale = p.get("scale", 0.06)
    u, v = ctx.U[:, 0] / scale, ctx.U[:, 1] / scale
    cu, cv = np.floor(u), np.floor(v)
    checker = ((cu + cv) % 2).astype(np.float64)
    fu, fv = u - cu, v - cv
    across = np.where(checker > 0.5, np.sin(fu * np.pi), np.sin(fv * np.pi))
    tone = 0.08 + 0.1 * across + 0.05 * checker
    s.base = np.clip(np.stack([tone, tone, tone * 1.1], 1), 0, 1)
    s.rough = np.full(ctx.n, p.get("rough", 0.28)) - 0.1 * across
    s.metal = np.full(ctx.n, 0.15)
    s.height = across * 0.0015
    s.dirt = grime_amount(ctx, p.get("dirt", 0.15))
    return s


@register("rust")
def _rust(ctx, p):
    s = _metal(ctx, dict(color=p.get("steel", (120, 118, 116)), rough=0.5, polish=0.2))
    amount = p.get("amount", 0.6)
    n = ctx.noise(3.5, 5, 23) + 0.3 * ctx.noise(14.0, 3, 24)
    mask = smoothstep(0.25 - amount * 0.6, 0.45 - amount * 0.6, n + (1 - ctx.AO) * 0.6)
    rust_col = mix(rgb((150, 62, 24)), rgb((92, 38, 18)), smoothstep(-0.4, 0.5, ctx.noise(9.0, 3, 25)))
    s.base = mix(s.base, rust_col, mask)
    s.paint = s.paint * (1 - mask)
    s.rough = mix(s.rough, 0.88, mask)
    s.metal = mix(s.metal, 0.1, mask)
    s.height = s.height + mask * ctx.noise(30.0, 3, 26) * 0.003
    return s


@register("concrete")
def _concrete(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (128, 128, 130)))
    n = ctx.noise(4.0, 5, 27)
    f1, _, _ = worley(ctx.Ps * 22.0, 28)
    pits = 1 - smoothstep(0.0, 0.12, f1)
    s.base = np.clip(color[None, :] * (0.88 + 0.14 * n - 0.25 * pits)[:, None], 0, 1)
    s.rough = np.clip(0.88 + 0.05 * n, 0, 1)
    s.height = n * 0.002 - pits * 0.004
    s.dirt = grime_amount(ctx, p.get("dirt", 0.5))
    return s


@register("diamondplate")
def _diamond(ctx, p):
    s = _metal(ctx, dict(color=p.get("color", (150, 154, 162)), rough=0.38, polish=0.5, dirt=p.get("dirt", 0.45)))
    pitch = p.get("pitch", 0.35)
    u, v = ctx.U[:, 0] / pitch, ctx.U[:, 1] / pitch
    cu, cv = np.floor(u), np.floor(v)
    fu, fv = u - cu - 0.5, v - cv - 0.5
    flip = ((cu + cv) % 2) > 0.5
    a = np.where(flip, fu + fv, fu - fv)
    b = np.where(flip, fu - fv, fu + fv)
    bead = (1 - smoothstep(0.06, 0.12, np.abs(a))) * (1 - smoothstep(0.28, 0.36, np.abs(b)))
    s.height = s.height + bead * 0.015
    s.base = s.base * (1 + 0.12 * bead[:, None])
    s.rough = s.rough - 0.12 * bead
    return s


@register("corrugated")
def _corrugated(ctx, p):
    s = _paint(ctx, p)
    pitch = p.get("pitch", 0.4)
    axis = p.get("axis", 0)
    t = ctx.U[:, axis] / pitch
    wave = 0.5 + 0.5 * np.cos(t * 2 * np.pi)
    s.height = s.height + wave * p.get("depth", 0.05)
    s.tint = np.clip(s.tint * (0.9 + 0.1 * wave), 0, 1)
    return s


@register("canvas")
def _canvas(ctx, p):
    s = Surface(ctx.n)
    colors = [rgb(c) for c in p.get("stripes", [(255, 210, 31), (24, 24, 28)])]
    width = p.get("stripe_width", 0.8)
    axis = p.get("axis", 0)
    idx = np.floor(ctx.U[:, axis] / width).astype(np.int64) % len(colors)
    col = np.stack(colors)[idx]
    weave = 0.5 + 0.5 * np.sin(ctx.U[:, 0] * 260) * np.sin(ctx.U[:, 1] * 260)
    var = ctx.noise(2.0, 4, 29)
    fade = smoothstep(-0.2, 0.8, ctx.noise(1.2, 3, 30)) * 0.12
    s.base = np.clip(col * (0.9 + 0.08 * weave + 0.06 * var - fade)[:, None], 0, 1)
    s.rough = np.clip(0.85 - 0.05 * weave, 0, 1)
    s.height = weave * 0.0012 + var * 0.003
    s.dirt = grime_amount(ctx, p.get("dirt", 0.4))
    return s


@register("screen")
def _screen(ctx, p):
    s = _glossy(ctx, dict(color=p.get("color", (12, 16, 24)), rough=0.08))
    lines = 0.5 + 0.5 * np.sin(ctx.U[:, 1] * p.get("line_freq", 220.0))
    s.base = np.clip(s.base * (0.9 + 0.15 * lines)[:, None], 0, 1)
    return s


@register("energy")
def _energy(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (150, 70, 255)))
    n = ctx.noise(5.0, 4, 31)
    r = ridged(ctx.Ps * 4.0, 4, 2.0, 0.5, 32)
    glow = smoothstep(0.55, 0.95, r)
    s.base = np.clip(color[None, :] * (0.35 + 0.65 * glow + 0.1 * n)[:, None], 0, 1)
    s.rough = np.full(ctx.n, 0.2)
    s.height = glow * 0.003
    return s


FONTS = {
    "impact": "C:/Windows/Fonts/impact.ttf",
    "bold": "C:/Windows/Fonts/arialbd.ttf",
    "black": "C:/Windows/Fonts/ariblk.ttf",
    "mono": "C:/Windows/Fonts/consolab.ttf",
}

_decal_cache = {}


def _text_mask(text, font, px_height):
    from PIL import Image, ImageDraw, ImageFont
    key = (text, font, px_height)
    if key in _decal_cache:
        return _decal_cache[key]
    path = FONTS.get(font, font)
    if not os.path.exists(path):
        path = FONTS["bold"]
    f = ImageFont.truetype(path, px_height)
    bbox = f.getbbox(text)
    w, h = bbox[2] - bbox[0] + 8, bbox[3] - bbox[1] + 8
    img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(img).text((4 - bbox[0], 4 - bbox[1]), text, font=f, fill=255)
    arr = np.asarray(img, dtype=np.float64) / 255.0
    _decal_cache[key] = arr
    return arr


def _sample_mask(mask, x, y):
    h, w = mask.shape
    inside = (x >= 0) & (x < w - 1) & (y >= 0) & (y < h - 1)
    xi = np.clip(x, 0, w - 2)
    yi = np.clip(y, 0, h - 2)
    x0, y0 = np.floor(xi).astype(np.int64), np.floor(yi).astype(np.int64)
    fx, fy = xi - x0, yi - y0
    v = (mask[y0, x0] * (1 - fx) * (1 - fy) + mask[y0, x0 + 1] * fx * (1 - fy) + mask[y0 + 1, x0] * (1 - fx) * fy + mask[y0 + 1, x0 + 1] * fx * fy)
    return np.where(inside, v, 0.0)


def decal_coverage(ctx, d):
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    kind = d.get("type", "text")
    cu, cv = d.get("center", (0.0, 0.0))
    ang = np.radians(d.get("angle", 0.0))
    du, dv = u - cu, v - cv
    ru = du * np.cos(ang) + dv * np.sin(ang)
    rv = -du * np.sin(ang) + dv * np.cos(ang)
    if kind == "text":
        height = d.get("height", 0.3)
        mask = _text_mask(d["text"], d.get("font", "impact"), 160)
        mh, mw = mask.shape
        scale = (mh - 8) / height
        x = ru * scale + mw / 2
        y = rv * scale + mh / 2
        return _sample_mask(mask, x, y)
    if kind == "rect":
        hw, hh = d["size"][0] / 2, d["size"][1] / 2
        r = d.get("radius", 0.0)
        qx = np.abs(ru) - (hw - r)
        qy = np.abs(rv) - (hh - r)
        dist = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
        aa = ctx.texel
        cov = 1 - smoothstep(-aa, aa, dist)
        if d.get("outline"):
            cov = cov * smoothstep(-aa, aa, dist + d["outline"])
        return cov
    if kind == "circle":
        dist = np.sqrt(ru ** 2 + rv ** 2) - d["radius"]
        aa = ctx.texel
        cov = 1 - smoothstep(-aa, aa, dist)
        if d.get("outline"):
            cov = cov * smoothstep(-aa, aa, dist + d["outline"])
        return cov
    if kind == "stripes":
        hw, hh = d["size"][0] / 2, d["size"][1] / 2
        inside = (np.abs(ru) <= hw) & (np.abs(rv) <= hh)
        width = d.get("width", 0.15)
        t = (ru + rv) / width
        stripe = smoothstep(0.45, 0.55, np.abs((t % 2.0) - 1.0))
        return np.where(inside, stripe, 0.0)
    if kind == "rivets":
        pts = np.asarray(d["points"], dtype=np.float64)
        r = d.get("radius", 0.04)
        dmin = np.full(ctx.n, np.inf)
        for pu, pv in pts:
            dmin = np.minimum(dmin, np.sqrt((u - pu) ** 2 + (v - pv) ** 2))
        aa = ctx.texel
        return 1 - smoothstep(r - aa, r + aa, dmin)
    if kind == "image":
        from PIL import Image
        key = ("img", d["path"])
        if key not in _decal_cache:
            _decal_cache[key] = np.asarray(Image.open(d["path"]).convert("L"), dtype=np.float64) / 255.0
        mask = _decal_cache[key]
        mh, mw = mask.shape
        size = d.get("size", 0.5)
        scale = mh / size
        return _sample_mask(mask, ru * scale + mw / 2, rv * scale + mh / 2)
    return np.zeros(ctx.n)


def _dome(ctx, d):
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    r = d.get("radius", 0.04)
    dmin = np.full(ctx.n, np.inf)
    for pu, pv in np.asarray(d["points"], dtype=np.float64):
        dmin = np.minimum(dmin, np.sqrt((u - pu) ** 2 + (v - pv) ** 2))
    return np.sqrt(np.clip(1 - (dmin / r) ** 2, 0, 1))


def apply_decals(ctx, s, decals):
    for d in decals:
        cov = decal_coverage(ctx, d)
        if not np.any(cov > 0):
            continue
        if d.get("type") == "rivets":
            dome = _dome(ctx, d)
            shade = 0.82 + 0.3 * dome
            if "color" in d:
                col = rgb(d["color"])
                s.base = mix(s.base, np.broadcast_to(col, s.base.shape) * shade[:, None], cov)
                s.paint = s.paint * (1 - cov)
                s.metal = mix(s.metal, d.get("metal", 1.0), cov)
            else:
                s.base = s.base * (1 + (shade - 1) * cov)[:, None]
                s.tint = np.clip(s.tint * (1 + (shade - 1) * cov), 0, 1)
            s.rough = mix(s.rough, d.get("rough", 0.35), cov)
            s.height = s.height + dome * d.get("height", 0.012)
            continue
        if "darken" in d:
            k = d["darken"] * cov
            s.base = s.base * (1 - k)[:, None]
            s.tint = np.clip(s.tint * (1 - k), 0, 1)
            s.rough = mix(s.rough, d.get("rough", s.rough), cov) if "rough" in d else s.rough
            s.height = s.height + cov * d.get("raise", -0.004)
            continue
        worn = wear_mask(ctx, d.get("wear", 0.35)) if d.get("wear", 0.35) > 0 else np.zeros(ctx.n)
        cov = cov * (1 - worn * 0.85)
        col = rgb(d.get("color", (255, 255, 255)))
        s.base = mix(s.base, np.broadcast_to(col, s.base.shape) * (0.95 + 0.05 * ctx.noise(5.0, 2, 33))[:, None], cov)
        s.paint = s.paint * (1 - cov)
        s.metal = mix(s.metal, d.get("metal", 0.0), cov)
        s.rough = mix(s.rough, d.get("rough", 0.5), cov)
        s.height = s.height + cov * d.get("raise", -0.0006)
    return s


def evaluate(material, ctx):
    if material is None:
        material = Material("plastic")
    fn = REGISTRY.get(material.kind)
    if fn is None:
        raise KeyError(f"unknown material kind {material.kind}")
    s = fn(ctx, material.params)
    if material.params.get("decals"):
        apply_decals(ctx, s, material.params["decals"])
    return s


def compose(surface, ctx, material, overlay, paint_color, ao_strength, gradient=0.12, highlight=0.6):
    params = material.params if material is not None else {}
    skin = params.get("skin", material is not None and material.kind in ("paint", "metal", "plastic"))
    paint = np.clip(surface.paint, 0, 1)
    overlay = bool(overlay and skin)
    if not overlay:
        paint_color = rgb(params.get("color", paint_color))
    gradient = params.get("gradient", gradient)
    highlight = params.get("highlight", highlight)
    ao = mix(1.0, np.clip(ctx.AO, 0, 1), ao_strength * params.get("ao", 1.0))
    shade = 1.0 + gradient * np.clip(ctx.N[:, 1], -1, 1)
    hl = np.clip(ctx.E, 0, 1) ** 1.5 * highlight * 0.32
    dirt_col = rgb(params.get("dirt_color", (52, 42, 34)))
    g = np.clip(surface.dirt, 0, 1)
    base = surface.base * (ao * shade)[:, None]
    base = base + (1 - base) * hl[:, None]
    base = mix(base, dirt_col, g)
    f = np.clip(surface.tint * ao * np.minimum(shade, 1.0), 0, 1)
    if overlay:
        h = np.clip(hl + np.maximum(shade - 1.0, 0.0) * 0.45, 0, 0.6)
        a_p = 1 - f * (1 - g) * (1 - h)
        c_num = dirt_col[None, :] * (g * (1 - h))[:, None] + h[:, None]
        c_p = c_num / np.maximum(a_p, 1e-4)[:, None]
        alpha = paint * a_p + (1 - paint)
        color = (paint * a_p)[:, None] * c_p + (1 - paint)[:, None] * base
        color = color / np.maximum(alpha, 1e-4)[:, None]
    else:
        painted = paint_color[None, :] * (f * np.maximum(shade, 1.0))[:, None]
        painted = painted + (1 - painted) * hl[:, None]
        painted = mix(painted, dirt_col, g)
        color = mix(base, painted, paint)
        alpha = np.ones(ctx.n)
    rough = np.clip(surface.rough + g * 0.25 - hl * 0.2, 0.04, 1)
    metal = np.clip(surface.metal * (1 - g * 0.6), 0, 1)
    return np.clip(color, 0.015, 0.97), np.clip(alpha, 0, 1), rough, metal, surface.height
