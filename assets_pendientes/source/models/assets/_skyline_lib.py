import numpy as np

from wr3d import Asset, Material, register, T, R, compose
from wr3d import shapes as sh
from wr3d.materials import Surface, rgb, grime_amount
from wr3d.noise import smoothstep, mix, hash01
from _landmark_lib import landmark
import _city_lib

WARM = (255, 188, 128)
BEACON = (255, 36, 36)
TOWERS = "Decor/SkylineNext/Towers"
SIDES = ["+x", "-x", "-z", "+y"]


@register("facade")
def facade(ctx, p):
    s = Surface(ctx.n)
    style = p.get("style", "punched")
    cw, ch = p.get("cell", (4.0, 4.0))
    wall = rgb(p.get("wall", (180, 184, 196)))
    glass = rgb(p.get("glass", (40, 54, 78)))
    frame = rgb(p.get("frame", (60, 64, 72)))
    lit_col = rgb(p.get("lit", (255, 214, 150)))
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    col = np.floor(u / cw)
    row = np.floor(v / ch)
    fu = u / cw - col
    fv = v / ch - row
    chart = np.broadcast_to(np.asarray(ctx.seed).astype(np.int64) % 89, (ctx.n,))
    cell_rand = hash01(col.astype(np.int64), row.astype(np.int64), chart, 11)
    band_rand = hash01(np.zeros(ctx.n, dtype=np.int64), row.astype(np.int64), chart, 5)
    if style == "curtain":
        mull = p.get("mullion", 0.12) / cw
        slab = p.get("slab", 0.16)
        frame_mask = np.maximum(1 - smoothstep(mull * 0.5, mull, np.minimum(fu, 1 - fu)), 1 - smoothstep(slab * 0.6, slab, fv))
        window = 1 - frame_mask
        solid = frame_mask
        solid_col = frame
    elif style == "ribbon":
        sill = p.get("sill", 0.42)
        mull = p.get("mullion", 0.08) / cw
        band = smoothstep(sill - 0.02, sill + 0.02, fv) * (1 - smoothstep(0.96, 0.99, fv))
        post = 1 - smoothstep(mull * 0.5, mull, np.minimum(fu, 1 - fu))
        window = band * (1 - post)
        solid = 1 - window
        solid_col = wall
    else:
        mx, top, bot = p.get("margin", (0.18, 0.2, 0.28))
        wu = smoothstep(mx - 0.03, mx, fu) * (1 - smoothstep(1 - mx, 1 - mx + 0.03, fu))
        wv = smoothstep(top - 0.03, top, fv) * (1 - smoothstep(1 - bot, 1 - bot + 0.03, fv))
        window = wu * wv
        solid = 1 - window
        solid_col = wall
    lit = (cell_rand < p.get("lit_ratio", 0.25)).astype(np.float64)
    if p.get("lit_rows", False):
        lit = np.maximum(lit * 0.3, (band_rand < p.get("lit_ratio", 0.25)).astype(np.float64))
    sky = smoothstep(-0.6, 0.6, ctx.noise(0.05, 2, 41) + (0.5 - fv) * 0.2)
    reflect = mix(glass[None, :] * 0.8, glass[None, :] * 1.35 + 0.05, sky)
    shade = 0.75 + 0.35 * cell_rand
    lit_tone = lit_col[None, :] * (0.8 + 0.25 * cell_rand)[:, None]
    pane = mix(reflect * shade[:, None], lit_tone, lit[:, None])
    var = ctx.noise(1.5, 3, 42)
    fine = ctx.noise(18.0, 2, 43)
    wall_tone = solid_col[None, :] * (0.9 + 0.08 * var + 0.04 * fine)[:, None]
    relief = np.zeros(ctx.n)
    if p.get("wall_kind") == "brick":
        bw, bh = p.get("brick", (1.0, 0.4))
        brow = np.floor(v / bh)
        bu = u + (brow % 2) * 0.5 * bw
        bcol = np.floor(bu / bw)
        du = np.minimum(bu / bw - bcol, 1 - (bu / bw - bcol)) * bw
        dv = np.minimum(v / bh - brow, 1 - (v / bh - brow)) * bh
        mortar = 1 - smoothstep(0.02, 0.05, np.minimum(du, dv))
        tone = hash01(bcol.astype(np.int64), brow.astype(np.int64), chart, 23)
        brick = solid_col[None, :] * (0.78 + 0.3 * tone + 0.06 * var)[:, None]
        wall_tone = mix(brick, rgb(p.get("mortar", (176, 168, 156)))[None, :] * (0.9 + 0.1 * var)[:, None], mortar[:, None])
        relief = -mortar * 0.004
    s.base = np.clip(mix(wall_tone, pane, window[:, None]), 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(mix(np.full(ctx.n, p.get("wall_rough", 0.7)) + 0.05 * fine, 0.08 + 0.3 * lit, window), 0, 1)
    s.metal = np.clip(window * (1 - lit) * p.get("glass_metal", 0.4) + solid * p.get("wall_metal", 0.0), 0, 1)
    s.height = -window * p.get("depth", 0.01) + fine * 0.0005 + relief * solid
    streak = smoothstep(0.3, 0.8, ctx.noise_aniso((4.0, 0.15, 4.0), 3, 44)) * p.get("streaks", 0.2)
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.25)) * solid + streak * 0.3 * solid, 0, 0.8)
    return s


def tower_asset(name, budget, radius):
    a = Asset(name, budget=budget, atlas=1024, ao_radius=3.0, ao_strength=0.5, edge_width=0.15, gradient=0.08, highlight=0.4, preview_radius=radius,
              views=[("FRONT 3/4", 215, 8), ("FRONT", 180, 2), ("SIDE", 270, 4), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 196, 40))
    a.role("Warm", "neon", color=WARM, transparency=0.25)
    a.role("Beacon", "neon", color=BEACON)
    return a


def block(size, mat, faces=None, face_mats=None):
    return sh.rounded_box(size, 0.0, 1, mat, faces=faces or SIDES, face_mats=face_mats)


def slab(size, mat, y):
    return block(size, mat, faces=["+x", "-x", "-z", "+y", "-y"]).transformed(T(0, y, 0))


def glow_ring(w, d, y, thick=0.5, out=0.25):
    pieces = []
    for z in (-d / 2 - out / 2, d / 2 + out / 2):
        pieces.append(sh.box((w + out * 2, thick, out), None).transformed(T(0, y, z)))
    for x in (-w / 2 - out / 2, w / 2 + out / 2):
        pieces.append(sh.box((out, thick, d), None).transformed(T(x, y, 0)))
    return pieces


def roof_kit(a, top, w, d, steel, seed, mast_h=26.0):
    rng = np.random.default_rng(seed)
    pw, pd = w * 0.36, d * 0.32
    px, pz = rng.uniform(-w * 0.15, w * 0.15), rng.uniform(0, d * 0.2)
    a.add("Body", block((pw, 4.5, pd), steel, faces=["+x", "-x", "-z", "+z", "+y"]).transformed(T(px, top + 2.25, pz)))
    vent = Material("metal", color=(84, 86, 92), rough=0.45, polish=0.3, dirt=0.4)
    for k in range(2):
        a.add("Body", sh.cylinder(1.4, 2.4, vent, bevel=0.0, segments=8).transformed(T(px + (k - 0.5) * pw * 0.5, top + 5.7, pz)))
    mx, mz = -w * 0.18, -d * 0.12
    a.add("Body", sh.cylinder(0.6, mast_h, steel, bevel=0.0, segments=6).transformed(T(mx, top + mast_h / 2, mz)))
    for y in (top + mast_h * 0.35, top + mast_h * 0.7):
        a.add("Body", sh.box((3.0, 0.3, 0.3), steel).transformed(T(mx, y, mz)))
    a.add("Beacon", sh.sphere(1.1, None, 6, 4).transformed(T(mx, top + mast_h + 1.0, mz)))
    return top + mast_h + 2.1


def install(a, names, pick=None, tint=("CrownLight", "Fin", "Halo", "BladeFace")):
    return landmark(a, TOWERS, names, fit="box", pick=pick, tint={"Glow": list(tint)})
