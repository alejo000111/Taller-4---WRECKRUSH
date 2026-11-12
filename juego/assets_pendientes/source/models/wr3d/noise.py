import numpy as np

_GRADS = np.array([
    [1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0],
    [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
    [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1],
    [1, 1, 0], [-1, 1, 0], [0, -1, 1], [0, -1, -1],
], dtype=np.float64)


def hash3(ix, iy, iz, seed=0):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ ((seed * 2654435761) & 0xFFFFFFFF)
    h = h & 0xFFFFFFFF
    h = ((h ^ (h >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
    h = ((h ^ (h >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
    return h ^ (h >> 16)


def hash01(ix, iy, iz, seed=0):
    return (hash3(ix, iy, iz, seed) & 0xFFFFFF) / float(0xFFFFFF)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def mix(a, b, t):
    t = np.asarray(t)
    a_shape, b_shape = np.shape(a), np.shape(b)
    vector = (a_shape[-1:] == (3,) or b_shape[-1:] == (3,)) and t.ndim == 1 and t.shape[0] != 3
    if np.ndim(a) > np.ndim(t) or np.ndim(b) > np.ndim(t) or vector:
        t = t[..., None]
    return a + (b - a) * t


def perlin(p, seed=0):
    p = np.asarray(p, dtype=np.float64)
    base = np.floor(p)
    f = p - base
    i = base.astype(np.int64)
    w = f * f * f * (f * (f * 6.0 - 15.0) + 10.0)
    out = np.zeros(p.shape[:-1])
    for dx in (0, 1):
        wx = w[..., 0] if dx else 1.0 - w[..., 0]
        for dy in (0, 1):
            wy = w[..., 1] if dy else 1.0 - w[..., 1]
            for dz in (0, 1):
                wz = w[..., 2] if dz else 1.0 - w[..., 2]
                h = hash3(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz, seed) & 15
                g = _GRADS[h]
                d0 = f[..., 0] - dx
                d1 = f[..., 1] - dy
                d2 = f[..., 2] - dz
                out += (g[..., 0] * d0 + g[..., 1] * d1 + g[..., 2] * d2) * wx * wy * wz
    return out


def fbm(p, octaves=4, lacunarity=2.0, gain=0.5, seed=0):
    p = np.asarray(p, dtype=np.float64)
    total = np.zeros(p.shape[:-1])
    amp, norm, freq = 1.0, 0.0, 1.0
    for o in range(octaves):
        total += perlin(p * freq + o * 17.31, seed + o * 101) * amp
        norm += amp
        amp *= gain
        freq *= lacunarity
    return total / norm


def ridged(p, octaves=4, lacunarity=2.0, gain=0.5, seed=0):
    p = np.asarray(p, dtype=np.float64)
    total = np.zeros(p.shape[:-1])
    amp, norm, freq = 1.0, 0.0, 1.0
    for o in range(octaves):
        n = 1.0 - np.abs(perlin(p * freq + o * 9.7, seed + o * 37))
        total += n * n * amp
        norm += amp
        amp *= gain
        freq *= lacunarity
    return total / norm


def worley(p, seed=0, jitter=0.9):
    p = np.asarray(p, dtype=np.float64)
    base = np.floor(p)
    f = p - base
    i = base.astype(np.int64)
    f1 = np.full(p.shape[:-1], 1e9)
    f2 = np.full(p.shape[:-1], 1e9)
    cell = np.zeros(p.shape[:-1], dtype=np.int64)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                h = hash3(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz, seed)
                ox = ((h & 1023) / 1023.0 - 0.5) * jitter + 0.5
                oy = (((h >> 10) & 1023) / 1023.0 - 0.5) * jitter + 0.5
                oz = (((h >> 20) & 1023) / 1023.0 - 0.5) * jitter + 0.5
                d = np.sqrt((dx + ox - f[..., 0]) ** 2 + (dy + oy - f[..., 1]) ** 2 + (dz + oz - f[..., 2]) ** 2)
                closer = d < f1
                f2 = np.where(closer, f1, np.minimum(f2, d))
                cell = np.where(closer, h, cell)
                f1 = np.where(closer, d, f1)
    return f1, f2, cell


def worley2(uv, seed=0, jitter=0.9):
    uv = np.asarray(uv, dtype=np.float64)
    p = np.concatenate([uv, np.zeros(uv.shape[:-1] + (1,))], axis=-1)
    base = np.floor(p)
    f = p - base
    i = base.astype(np.int64)
    f1 = np.full(uv.shape[:-1], 1e9)
    f2 = np.full(uv.shape[:-1], 1e9)
    cell = np.zeros(uv.shape[:-1], dtype=np.int64)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            h = hash3(i[..., 0] + dx, i[..., 1] + dy, i[..., 2], seed)
            ox = ((h & 1023) / 1023.0 - 0.5) * jitter + 0.5
            oy = (((h >> 10) & 1023) / 1023.0 - 0.5) * jitter + 0.5
            d = np.sqrt((dx + ox - f[..., 0]) ** 2 + (dy + oy - f[..., 1]) ** 2)
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            cell = np.where(closer, h, cell)
            f1 = np.where(closer, d, f1)
    return f1, f2, cell
