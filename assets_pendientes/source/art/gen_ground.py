import json

import numpy as np

from gen_materials import ROOT, SIZE, value_noise, fbm, blur, rgb, save, coords, crack_mask


def worley(points_per_axis, seed, jitter=0.85):
    rng = np.random.default_rng(seed)
    n = points_per_axis
    cell = SIZE / n
    gx, gy = np.meshgrid(np.arange(n), np.arange(n), indexing="xy")
    px = (gx + 0.5 + (rng.random((n, n)) - 0.5) * jitter) * cell
    py = (gy + 0.5 + (rng.random((n, n)) - 0.5) * jitter) * cell
    xs, ys = coords()
    f1 = np.full((SIZE, SIZE), np.inf)
    f2 = np.full((SIZE, SIZE), np.inf)
    ids = np.zeros((SIZE, SIZE), dtype=np.int64)
    for j in range(n):
        for i in range(n):
            for oy in (-SIZE, 0, SIZE):
                for ox in (-SIZE, 0, SIZE):
                    d = np.hypot(xs - (px[j, i] + ox), ys - (py[j, i] + oy))
                    closer = d < f1
                    f2 = np.where(closer, f1, np.minimum(f2, d))
                    ids = np.where(closer, j * n + i, ids)
                    f1 = np.where(closer, d, f1)
    return f1, f2, ids


def stains(seed, cells=5, threshold=0.66, soft=0.08):
    field = fbm(SIZE, cells, 4, seed)
    return np.clip((field - threshold) / soft, 0, 1)


def scrap_dirt():
    rng = np.random.default_rng(11)
    grain = fbm(SIZE, 48, 4, 100)
    broad = fbm(SIZE, 4, 4, 101)
    color = rgb((92, 80, 64))[None, None, :] * (0.78 + 0.35 * broad[..., None]) + (grain[..., None] - 0.5) * 30
    pebbles = (fbm(SIZE, 96, 2, 102) > 0.68)
    color[pebbles] = color[pebbles] * 0.6 + rgb((150, 144, 132)) * 0.4
    oil = stains(103, 4, 0.64, 0.06)
    color = color * (1 - 0.6 * oil[..., None]) + rgb((20, 18, 22)) * 0.6 * oil[..., None]
    rust = stains(104, 9, 0.7, 0.05)
    color = color * (1 - 0.45 * rust[..., None]) + rgb((120, 62, 32)) * 0.45 * rust[..., None]
    xs, ys = coords()
    tracks = np.zeros((SIZE, SIZE))
    for offset in (300, 420, 760, 880):
        band = np.abs(((xs + 40 * np.sin(ys / SIZE * 2 * np.pi)) - offset)) < 26
        tracks += band * (0.5 + 0.5 * (np.sin(ys * 0.5) > 0.2))
    tracks = blur(np.clip(tracks, 0, 1), 2)
    color *= (1 - 0.18 * tracks)[..., None]
    shards = rng.random((SIZE, SIZE)) > 0.996
    shards = blur(shards.astype(float), 1) > 0.15
    color[shards] = rgb((160, 164, 170))
    height = grain * 0.5 + broad * 0.3 + pebbles * 0.35 - tracks * 0.25 + shards * 0.3
    rough = np.clip(0.92 - oil * 0.5 - shards * 0.5, 0, 1)
    metal = np.clip(shards * 0.9 + rust * 0.1, 0, 1)
    return save("WR_ScrapDirt", color, height, 5, rough, metal)


def factory_concrete():
    rng = np.random.default_rng(12)
    xs, ys = coords()
    slab = SIZE // 2
    lx, ly = xs % slab, ys % slab
    sid = (xs // slab) + (ys // slab) * 2
    tone = rng.random(4)[sid]
    grain = fbm(SIZE, 40, 4, 110)
    broad = fbm(SIZE, 3, 4, 111)
    color = rgb((118, 116, 112))[None, None, :] * (0.86 + 0.12 * tone[..., None] + 0.12 * broad[..., None]) + (grain[..., None] - 0.5) * 18
    oil = stains(112, 3, 0.66, 0.08)
    color = color * (1 - 0.55 * oil[..., None]) + rgb((30, 28, 26)) * 0.55 * oil[..., None]
    joint = (lx < 6) | (ly < 6)
    color[joint] = rgb((54, 52, 50))
    stripe = (np.abs(xs - slab // 2) < 18) & ((ys // 64) % 2 == 0)
    wear = fbm(SIZE, 20, 3, 113)
    stripe_mask = stripe & (wear > 0.42)
    color[stripe_mask] = color[stripe_mask] * 0.25 + rgb((230, 180, 30)) * 0.75
    cracks = crack_mask(rng, 10, 180)
    color *= (1 - 0.5 * cracks)[..., None]
    height = 0.6 + grain * 0.15 - cracks * 0.5
    height[joint] = 0.0
    rough = np.clip(0.88 - oil * 0.45 - stripe_mask * 0.2, 0, 1)
    return save("WR_FactoryConcrete", color, height, 5, rough)


def military_pavers():
    xs, ys = coords()
    f1, f2, ids = worley(10, 120, 0.7)
    edge = np.clip((f2 - f1) / 10.0, 0, 1)
    rng = np.random.default_rng(13)
    tone = rng.random(100)[ids]
    grain = fbm(SIZE, 48, 4, 121)
    dust = fbm(SIZE, 4, 4, 122)
    color = rgb((112, 112, 96))[None, None, :] * (0.8 + 0.2 * tone[..., None]) + (grain[..., None] - 0.5) * 20
    color = color * (1 - 0.35 * dust[..., None]) + rgb((140, 124, 90)) * 0.35 * dust[..., None]
    gap = edge < 0.18
    color[gap] = rgb((50, 48, 40))
    moss = stains(123, 6, 0.68, 0.05) * gap
    color[moss > 0.3] = rgb((70, 82, 48))
    height = np.clip(edge * 3, 0, 1) * 0.8 + grain * 0.12
    rough = np.where(gap, 0.97, 0.86)
    return save("WR_MilitaryPavers", color, height, 6, rough)


def tech_floor():
    xs, ys = coords()
    tile = SIZE // 4
    lx, ly = xs % tile, ys % tile
    tid = (xs // tile) + (ys // tile) * 4
    rng = np.random.default_rng(14)
    tone = rng.random(16)[tid]
    grain = fbm(SIZE, 64, 2, 130)
    color = rgb((30, 34, 48))[None, None, :] * (0.9 + 0.15 * tone[..., None]) + (grain[..., None] - 0.5) * 6
    seam = (lx < 4) | (ly < 4)
    color[seam] = rgb((10, 12, 18))
    inset = (lx > 24) & (lx < tile - 24) & (ly > 24) & (ly < tile - 24)
    border = inset & ((lx < 30) | (lx > tile - 30) | (ly < 30) | (ly > tile - 30))
    color[border] = rgb((52, 60, 82))
    accent = (tone > 0.6) & (np.abs(ly - tile // 2) < 3) & (lx > 40) & (lx < tile - 40)
    color[accent] = rgb((40, 200, 240))
    dots = (tone > 0.3) & (np.hypot(lx - 14, ly - 14) < 4)
    color[dots] = rgb((166, 77, 255))
    height = 0.6 + inset * 0.1 - border * 0.15 + grain * 0.03
    height[seam] = 0.0
    rough = np.where(accent | dots, 0.15, np.where(seam, 0.6, 0.3))
    metal = np.where(seam, 0.2, 0.55)
    return save("WR_TechFloor", color, height, 5, rough, metal)


def chaos_rock():
    f1, f2, ids = worley(8, 140, 0.9)
    edge = np.clip((f2 - f1) / 14.0, 0, 1)
    grain = fbm(SIZE, 40, 5, 141)
    broad = fbm(SIZE, 4, 4, 142)
    rng = np.random.default_rng(15)
    tone = rng.random(64)[ids]
    color = rgb((32, 24, 42))[None, None, :] * (0.7 + 0.35 * tone[..., None] + 0.3 * broad[..., None]) + (grain[..., None] - 0.5) * 14
    vein = edge < 0.12
    glow = np.clip(1 - edge / 0.12, 0, 1) * vein
    color = color * (1 - glow[..., None]) + rgb((190, 90, 255)) * glow[..., None]
    pink = stains(143, 6, 0.72, 0.04)
    color = color * (1 - 0.5 * pink[..., None]) + rgb((255, 59, 160)) * 0.5 * pink[..., None]
    height = np.clip(edge * 2.5, 0, 1) * 0.9 + grain * 0.25
    rough = np.clip(0.75 - glow * 0.6 - tone * 0.2, 0.05, 1)
    return save("WR_ChaosRock", color, height, 7, rough)


def vip_marble():
    xs, ys = coords()
    tile = SIZE // 2
    lx, ly = xs % tile, ys % tile
    warp = fbm(SIZE, 4, 5, 150) * 6
    veins = np.abs(np.sin((xs + ys) / SIZE * 2 * np.pi * 3 + warp))
    vein = np.clip((0.06 - veins) / 0.06, 0, 1) + np.clip((0.02 - np.abs(np.sin((xs - ys) / SIZE * 2 * np.pi * 5 + warp * 1.3))) / 0.02, 0, 1) * 0.5
    grain = fbm(SIZE, 32, 3, 151)
    color = rgb((26, 24, 30))[None, None, :] * (0.9 + 0.2 * grain[..., None]) + rgb((210, 200, 190)) * (np.clip(vein, 0, 1) * 0.7)[..., None]
    inlay = (np.abs(lx - tile // 2) < 5) | (np.abs(ly - tile // 2) < 5) | (lx < 6) | (ly < 6)
    color[inlay] = rgb((240, 190, 60))
    height = 0.7 - inlay * 0.05 + grain * 0.02
    rough = np.where(inlay, 0.2, 0.12 + grain * 0.1)
    metal = np.where(inlay, 1.0, 0.0)
    return save("WR_VIPMarble", color, height, 3, rough, metal)


def plaza_tiles():
    xs, ys = coords()
    tile = SIZE // 4
    lx, ly = xs % tile, ys % tile
    tid = (xs // tile) + (ys // tile) * 4
    rng = np.random.default_rng(16)
    tone = rng.random(16)[tid]
    grain = fbm(SIZE, 48, 4, 160)
    broad = fbm(SIZE, 3, 4, 161)
    base = rgb((66, 70, 82))
    color = base[None, None, :] * (0.85 + 0.2 * tone[..., None] + 0.12 * broad[..., None]) + (grain[..., None] - 0.5) * 14
    checker = ((xs // tile) + (ys // tile)) % 2 == 0
    color[checker] *= 0.88
    joint = (lx < 5) | (ly < 5)
    color[joint] = rgb((28, 30, 36))
    corner = (np.hypot(lx - tile / 2, ly - tile / 2) < 10) & checker
    color[corner] = rgb((255, 196, 40))
    scuff = stains(162, 5, 0.7, 0.06)
    color *= (1 - 0.15 * scuff)[..., None]
    height = 0.6 + grain * 0.1 - scuff * 0.05
    height[joint] = 0.0
    rough = np.where(joint, 0.95, 0.7 - 0.2 * scuff)
    rough = np.where(corner, 0.25, rough)
    metal = np.where(corner, 0.9, 0.0)
    return save("WR_PlazaTiles", color, height, 5, rough, metal)


FACTORIES = (scrap_dirt, factory_concrete, military_pavers, tech_floor, chaos_rock, vip_marble, plaza_tiles)


def main():
    index_path = ROOT / "index.json"
    built = json.loads(index_path.read_text()) if index_path.exists() else {}
    for factory in FACTORIES:
        maps = factory()
        built[factory.__name__] = maps
        print(factory.__name__, maps)
    index_path.write_text(json.dumps(built, indent=2))


if __name__ == "__main__":
    main()
