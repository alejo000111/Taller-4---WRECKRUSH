import json

import numpy as np
from PIL import Image

from gen_materials import ROOT, SIZE, fbm, rgb, save

FACE = 1024
SKY_DIR = ROOT / "WR_DuskSky"

FACES = {
    "Ft": lambda u, v: (u, -v, -np.ones_like(u)),
    "Bk": lambda u, v: (-u, -v, np.ones_like(u)),
    "Lf": lambda u, v: (np.ones_like(u), -v, u),
    "Rt": lambda u, v: (-np.ones_like(u), -v, -u),
    "Up": lambda u, v: (-v, np.ones_like(u), -u),
    "Dn": lambda u, v: (-v, -np.ones_like(u), u),
}


def lattice(ix, iy, iz, seed):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def noise3(x, y, z, seed):
    xi, yi, zi = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64), np.floor(z).astype(np.int64)
    fx, fy, fz = x - xi, y - yi, z - zi
    fx, fy, fz = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy), fz * fz * (3 - 2 * fz)
    total = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (fx if dx else 1 - fx) * (fy if dy else 1 - fy) * (fz if dz else 1 - fz)
                total = total + w * lattice(xi + dx, yi + dy, zi + dz, seed)
    return total


def fbm3(x, y, z, octaves, seed):
    total, amp, weight = 0.0, 1.0, 0.0
    for k in range(octaves):
        f = 2 ** k
        total = total + amp * noise3(x * f, y * f, z * f, seed + k * 17)
        weight += amp
        amp *= 0.5
    return total / weight


def smooth(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return a * (1 - t[..., None]) + b * t[..., None]


def sky_color(dx, dy, dz):
    elev = np.arcsin(np.clip(dy, -1, 1))
    up = np.clip(elev / (np.pi / 2), 0, 1)
    zenith = rgb((28, 26, 66))
    high = rgb((70, 52, 118))
    mid = rgb((168, 86, 120))
    low = rgb((246, 140, 88))
    rim = rgb((255, 196, 132))
    color = mix(np.broadcast_to(rim, dx.shape + (3,)), np.broadcast_to(low, dx.shape + (3,)), smooth(0.0, 0.05, up))
    color = mix(color, np.broadcast_to(mid, dx.shape + (3,)), smooth(0.04, 0.2, up))
    color = mix(color, np.broadcast_to(high, dx.shape + (3,)), smooth(0.16, 0.45, up))
    color = mix(color, np.broadcast_to(zenith, dx.shape + (3,)), smooth(0.4, 0.95, up))

    s = 3.2
    stretch = 1.0 / np.maximum(0.25, 1.2 * up + 0.25)
    body = fbm3(dx * s, dy * s * 4.5 * stretch, dz * s, 6, 11)
    wisp = fbm3(dx * s * 2.4, dy * s * 9.0, dz * s * 2.4, 4, 29)
    band = smooth(0.0, 0.03, up) * (1 - smooth(0.12, 0.42, up))
    cover = smooth(0.48, 0.66, body * 0.75 + wisp * 0.35) * band
    light = np.clip((body - 0.4) * 2.2 + (1 - up) * 0.6, 0, 1)
    cloud = mix(np.broadcast_to(rgb((74, 50, 96)), dx.shape + (3,)), np.broadcast_to(rgb((255, 150, 128)), dx.shape + (3,)), light)
    cloud = mix(cloud, np.broadcast_to(rgb((255, 214, 170)), dx.shape + (3,)), smooth(0.55, 0.9, light) * (1 - smooth(0.0, 0.15, up)))
    color = mix(color, cloud, cover * 0.92)

    cell = 160.0
    gx, gy, gz = np.floor(dx * cell), np.floor(dy * cell), np.floor(dz * cell)
    pick = lattice(gx.astype(np.int64), gy.astype(np.int64), gz.astype(np.int64), 5)
    star = (pick > 0.9965) * smooth(0.3, 0.7, up) * (1 - cover)
    twinkle = lattice(gx.astype(np.int64), gy.astype(np.int64), gz.astype(np.int64), 9)
    color = color + star[..., None] * (120 + 135 * twinkle[..., None])

    haze = rgb((70, 48, 82))
    color = mix(color, np.broadcast_to(haze, dx.shape + (3,)), smooth(0.0, -0.08, elev))
    return np.clip(color, 0, 255)


def skybox():
    SKY_DIR.mkdir(parents=True, exist_ok=True)
    grid = (np.arange(FACE) + 0.5) / FACE * 2 - 1
    u, v = np.meshgrid(grid, grid)
    for name, mapping in FACES.items():
        dx, dy, dz = mapping(u, v)
        length = np.sqrt(dx * dx + dy * dy + dz * dz)
        image = sky_color(dx / length, dy / length, dz / length)
        Image.fromarray(image.astype(np.uint8), "RGB").save(SKY_DIR / f"{name}.png", optimize=True)
        print("face", name)
    return list(FACES)


def cloud_sea():
    broad = fbm(SIZE, 3, 5, 900)
    puff = fbm(SIZE, 9, 4, 901)
    fine = fbm(SIZE, 40, 3, 902)
    tops = np.clip(broad * 0.55 + puff * 0.35 + fine * 0.1, 0, 1)
    lit = np.clip((tops - 0.35) * 2.2, 0, 1)
    shade = rgb((150, 150, 176))
    bright = rgb((246, 244, 250))
    color = shade[None, None, :] * (1 - lit[..., None]) + bright[None, None, :] * lit[..., None]
    height = tops * 0.8 + fine * 0.2
    rough = np.full((SIZE, SIZE), 0.95)
    return save("WR_CloudSea", color, height, 6, rough)


def main():
    index_path = ROOT / "index.json"
    built = json.loads(index_path.read_text()) if index_path.exists() else {}
    built["cloud_sea"] = cloud_sea()
    print("cloud_sea", built["cloud_sea"])
    index_path.write_text(json.dumps(built, indent=2))
    skybox()


if __name__ == "__main__":
    main()
