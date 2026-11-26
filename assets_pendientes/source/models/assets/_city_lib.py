import numpy as np

from wr3d import Material, register, T, R, compose
from wr3d import shapes as sh
from wr3d.materials import Surface, rgb, grime_amount, wear_mask
from wr3d.noise import smoothstep, mix, hash01


@register("city_brick")
def city_brick(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (170, 74, 52)))
    mortar_col = rgb(p.get("mortar", (190, 182, 168)))
    bw, bh = p.get("brick", (0.78, 0.3))
    gap = p.get("gap", 0.035)
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    row = np.floor(v / bh)
    shift = (row % 2) * 0.5 * bw
    col = np.floor((u + shift) / bw)
    fu = (u + shift) / bw - col
    fv = v / bh - row
    du = np.minimum(fu, 1 - fu) * bw
    dv = np.minimum(fv, 1 - fv) * bh
    edge = np.minimum(du, dv)
    mortar = 1 - smoothstep(gap * 0.5, gap, edge)
    chart = np.broadcast_to(np.asarray(ctx.seed).astype(np.int64) % 97, (ctx.n,))
    tone = hash01(col.astype(np.int64), row.astype(np.int64), chart, 7)
    var = ctx.noise(3.0, 3, 61)
    fine = ctx.noise(24.0, 2, 62)
    brick = color[None, :] * (0.78 + 0.32 * tone + 0.08 * var + 0.06 * fine)[:, None]
    dark = smoothstep(0.82, 0.95, tone)
    brick = mix(brick, brick * 0.62, dark * 0.6)
    wear = wear_mask(ctx, p.get("wear", 0.3))
    base = mix(brick, mortar_col * (0.9 + 0.1 * var)[:, None], mortar)
    base = mix(base, base * 0.85 + 0.1, wear * 0.3)
    s.base = np.clip(base, 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.82 + 0.08 * fine + 0.06 * mortar, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = (1 - mortar) * 0.006 + fine * 0.0008 - wear * 0.002
    soot = smoothstep(0.3, 0.9, ctx.noise(0.6, 3, 63)) * p.get("soot", 0.2)
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.35)) + soot, 0, 0.85)
    return s


@register("city_stone")
def city_stone(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (196, 190, 176)))
    var = ctx.noise(2.0, 4, 71)
    fine = ctx.noise(30.0, 2, 72)
    speck = smoothstep(0.55, 0.7, ctx.noise(60.0, 1, 73))
    s.base = np.clip(color[None, :] * (0.88 + 0.1 * var + 0.04 * fine - 0.08 * speck)[:, None], 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.72 + 0.1 * fine, 0, 1)
    s.metal = np.zeros(ctx.n)
    s.height = fine * 0.001 + var * 0.001
    streak = smoothstep(0.2, 0.7, ctx.noise_aniso((6.0, 0.4, 6.0), 3, 74)) * p.get("streaks", 0.25)
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.35)) + streak * 0.4, 0, 0.85)
    return s


def frame_box(size, mat, open_face="+z"):
    faces = [f for f in ("+x", "-x", "+y", "-y", "+z", "-z") if f != open_face]
    return sh.rounded_box(size, 0.0, 1, mat, faces=faces)


def window_frame(width, height, depth, bar, mat, face="-z"):
    out = []
    z = -depth / 2 if face == "-z" else depth / 2
    for y in (-height / 2 + bar / 2, height / 2 - bar / 2):
        out.append(sh.box((width, bar, depth), mat).transformed(T(0, y, 0)))
    for x in (-width / 2 + bar / 2, width / 2 - bar / 2):
        out.append(sh.box((bar, height - 2 * bar, depth), mat).transformed(T(x, 0, 0)))
    return out


def scallops(width, depth, count):
    pts = [(width / 2, 0.0), (-width / 2, 0.0)]
    step = width / count
    for i in range(count):
        x0 = -width / 2 + i * step
        for t in (0.0, 0.5):
            pts.append((x0 + t * step, -depth * (0.6 + 0.4 * np.sin(np.pi * t))))
    pts.append((width / 2, -depth * 0.6))
    return pts


def awning(width, depth, drop, mat, valance=0.42, count=None):
    slope = sh.extrude([(0.0, 0.0), (depth, -drop), (depth, -drop - 0.06), (0.0, -0.06)], width, mat, bevel=0.0, corner_radius=0.0)
    parts = [slope.transformed(R(0, 90, 0))]
    edge = sh.extrude(scallops(width, valance, count or max(4, int(width / 0.7))), 0.05, mat, bevel=0.0, corner_radius=0.0)
    parts.append(edge.transformed(T(0, -drop, -depth)))
    return parts


def shrub(mat, seed, radius=0.8):
    rng = np.random.default_rng(seed)
    parts = []
    for k in range(3):
        ball = sh.sphere(radius * (0.7 + 0.25 * rng.random()), mat, 8, 5)
        ball.pos *= 1 + rng.normal(0, 0.08, (len(ball.pos), 1))
        ball = sh.recompute_normals(ball)
        angle = k * 2.1 + rng.random()
        parts.append(ball.transformed(T(np.cos(angle) * radius * 0.45, radius * (0.55 + 0.2 * rng.random()), np.sin(angle) * radius * 0.35)))
    return parts
