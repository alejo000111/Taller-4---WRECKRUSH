import json

import numpy as np

from gen_materials import ROOT, SIZE, value_noise, fbm, blur, rgb, save, coords, crack_mask


def moss_floor():
    rng = np.random.default_rng(71)
    broad = fbm(SIZE, 4, 4, 700)
    mid = fbm(SIZE, 14, 4, 701)
    grain = fbm(SIZE, 90, 3, 702)
    soil = rgb((58, 50, 40))[None, None, :] * (0.8 + 0.4 * mid[..., None])
    moss = rgb((70, 86, 58))[None, None, :] * (0.72 + 0.4 * broad[..., None] + 0.25 * mid[..., None]) + (grain[..., None] - 0.5) * 26
    cover = np.clip((broad * 0.7 + mid * 0.5 - 0.42) / 0.12, 0, 1)
    color = soil * (1 - cover[..., None]) + moss * cover[..., None]
    leaves = rng.random((SIZE, SIZE)) > 0.9975
    leaves = blur(leaves.astype(float), 2) > 0.08
    tint = np.where(rng.random((SIZE, SIZE)) > 0.5, 1.0, 0.0)[..., None]
    leaf_col = rgb((150, 104, 44)) * tint + rgb((110, 130, 60)) * (1 - tint)
    color = np.where(leaves[..., None], leaf_col, color)
    roots = crack_mask(rng, 14, 260)
    color = color * (1 - 0.35 * roots[..., None]) + rgb((80, 62, 44)) * 0.35 * roots[..., None]
    height = mid * 0.4 + grain * 0.35 + cover * 0.25 + roots * 0.3 + leaves * 0.2
    rough = np.clip(0.9 - leaves * 0.2, 0, 1)
    return save("WR_MossFloor", color, height, 4, rough)


def snow_field():
    rng = np.random.default_rng(72)
    broad = fbm(SIZE, 3, 4, 710)
    drift = fbm(SIZE, 8, 4, 711, stretch=(1, 3))
    grain = fbm(SIZE, 120, 2, 712)
    color = rgb((232, 240, 246))[None, None, :] * (0.86 + 0.12 * broad[..., None] + 0.04 * grain[..., None])
    blue = np.clip((drift - 0.55) / 0.2, 0, 1)
    color = color * (1 - 0.18 * blue[..., None]) + rgb((170, 196, 222)) * 0.18 * blue[..., None]
    sparkle = rng.random((SIZE, SIZE)) > 0.996
    color[sparkle] = rgb((255, 255, 255))
    height = drift * 0.5 + grain * 0.15 + broad * 0.3
    rough = np.clip(0.75 - sparkle * 0.5 - blue * 0.1, 0, 1)
    return save("WR_SnowField", color, height, 3, rough)


def sky_stone():
    rng = np.random.default_rng(73)
    grain = fbm(SIZE, 70, 3, 720)
    broad = fbm(SIZE, 5, 4, 721)
    xs, ys = coords()
    cell = SIZE / 4
    fx = (xs % cell) / cell
    fy = ((ys + (np.floor(xs / cell) % 2) * cell / 2) % cell) / cell
    seam = np.clip(1 - np.minimum(np.minimum(fx, 1 - fx), np.minimum(fy, 1 - fy)) * cell / 4, 0, 1)
    tile_id = (np.floor(xs / cell) * 7 + np.floor((ys + (np.floor(xs / cell) % 2) * cell / 2) / cell) * 13) % 5
    color = rgb((92, 92, 120))[None, None, :] * (0.82 + 0.06 * tile_id[..., None] + 0.2 * broad[..., None]) + (grain[..., None] - 0.5) * 16
    color *= (1 - 0.45 * seam)[..., None]
    veins = crack_mask(rng, 12, 220)
    color = color * (1 - 0.5 * veins[..., None]) + rgb((176, 150, 230)) * 0.5 * veins[..., None]
    height = grain * 0.3 + broad * 0.2 - seam * 0.6 - veins * 0.2
    rough = np.clip(0.7 + grain * 0.1 - veins * 0.3, 0, 1)
    return save("WR_SkyStone", color, height, 4, rough)


FACTORIES = [moss_floor, snow_field, sky_stone]


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
