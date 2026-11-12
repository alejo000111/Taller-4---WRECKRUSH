import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "materials"
SIZE = 1024


def value_noise(size, cells_x, cells_y, seed):
    rng = np.random.default_rng(seed)
    grid = rng.random((cells_y, cells_x))
    xs = np.linspace(0, cells_x, size, endpoint=False)
    ys = np.linspace(0, cells_y, size, endpoint=False)
    xi, yi = np.floor(xs).astype(int), np.floor(ys).astype(int)
    xf, yf = xs - xi, ys - yi
    xf, yf = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    x0, x1 = xi % cells_x, (xi + 1) % cells_x
    y0, y1 = yi % cells_y, (yi + 1) % cells_y
    a = grid[np.ix_(y0, x0)]
    b = grid[np.ix_(y0, x1)]
    c = grid[np.ix_(y1, x0)]
    d = grid[np.ix_(y1, x1)]
    fx, fy = xf[None, :], yf[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(size, cells, octaves, seed, stretch=(1, 1)):
    total = np.zeros((size, size))
    amplitude, weight = 1.0, 0.0
    for octave in range(octaves):
        scale = 2 ** octave
        total += amplitude * value_noise(size, cells * scale * stretch[0], cells * scale * stretch[1], seed + octave * 31)
        weight += amplitude
        amplitude *= 0.5
    return total / weight


def normal_from_height(height, strength):
    dx = np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)
    dy = np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)
    nx, ny, nz = -dx * strength, dy * strength, np.ones_like(height)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    stack = np.stack([nx / length, ny / length, nz / length], axis=-1)
    return ((stack + 1) * 127.5).clip(0, 255).astype(np.uint8)


def blur(field, radius):
    out = field.copy()
    for _ in range(radius):
        out = (out + np.roll(out, 1, 0) + np.roll(out, -1, 0) + np.roll(out, 1, 1) + np.roll(out, -1, 1)) / 5
    return out


def rgb(color):
    return np.array(color, dtype=float)


def paint(canvas, mask, color):
    canvas[mask] = color[mask] if color.ndim == 3 else color


def save(name, color, height, strength, roughness, metalness=None):
    folder = ROOT / name
    folder.mkdir(parents=True, exist_ok=True)
    Image.fromarray(color.clip(0, 255).astype(np.uint8), "RGB").save(folder / "color.png", optimize=True)
    Image.fromarray(normal_from_height(height, strength), "RGB").save(folder / "normal.png", optimize=True)
    Image.fromarray((roughness * 255).clip(0, 255).astype(np.uint8), "L").save(folder / "roughness.png", optimize=True)
    maps = ["color", "normal", "roughness"]
    if metalness is not None:
        Image.fromarray((metalness * 255).clip(0, 255).astype(np.uint8), "L").save(folder / "metalness.png", optimize=True)
        maps.append("metalness")
    return maps


def coords():
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    return xs, ys


def windows_grid(cols, rows, seed, lit_ratio, tint, lit_tint, frame, band):
    rng = np.random.default_rng(seed)
    xs, ys = coords()
    cell_w, cell_h = SIZE // cols, SIZE // rows
    lx, ly = xs % cell_w, ys % cell_h
    cx, cy = xs // cell_w, ys // cell_h
    grain = fbm(SIZE, 8, 4, seed)
    color = np.zeros((SIZE, SIZE, 3))
    color[:] = rgb((44, 46, 54))
    color += (grain[..., None] - 0.5) * 18
    height = 0.6 + grain * 0.05
    rough = np.full((SIZE, SIZE), 0.82)
    metal = np.zeros((SIZE, SIZE))
    mull = frame
    pane = (lx >= mull) & (lx < cell_w - mull) & (ly >= mull) & (ly < cell_h - band)
    inner = (lx >= mull + 5) & (lx < cell_w - mull - 5) & (ly >= mull + 5) & (ly < cell_h - band - 5)
    frame_ring = pane & ~inner
    color[frame_ring] = rgb((26, 27, 32))
    height[frame_ring] = 0.32
    rough[frame_ring] = 0.45
    metal[frame_ring] = 0.75
    lit = rng.random((rows, cols)) < lit_ratio
    blinds = rng.random((rows, cols)) < 0.35
    glow = rng.random((rows, cols))
    vertical = (ly - mull) / max(cell_h - band - mull, 1)
    sweep = 0.5 + 0.5 * np.sin((xs + ys * 0.6) / SIZE * np.pi * 2)
    glass = rgb(tint)[None, None, :] * (1.15 - 0.45 * vertical[..., None]) + sweep[..., None] * 22
    warm = rgb(lit_tint)[None, None, :] * (0.65 + 0.35 * glow[cy, cx][..., None]) * (1.05 - 0.25 * vertical[..., None])
    is_lit = lit[cy, cx] & inner
    is_dark = ~lit[cy, cx] & inner
    color[is_dark] = glass[is_dark]
    color[is_lit] = warm[is_lit]
    slats = blinds[cy, cx] & is_lit & ((ly // 7) % 2 == 0)
    color[slats] *= 0.82
    height[inner] = 0.0
    rough[is_dark] = 0.08
    rough[is_lit] = 0.35
    band_mask = ly >= cell_h - band
    color[band_mask] = rgb((58, 60, 68)) + (grain[band_mask][..., None] - 0.5) * 14
    height[band_mask] = 0.85
    edge = band_mask & (ly < cell_h - band + 4)
    color[edge] *= 0.7
    return color, height, rough, metal


def facade_glass():
    color, height, rough, metal = windows_grid(4, 4, 11, 0.16, (22, 52, 70), (255, 196, 118), 12, 30)
    return save("WR_FacadeGlass", color, height, 6, rough, metal)


def facade_night():
    color, height, rough, metal = windows_grid(4, 4, 23, 0.34, (20, 30, 52), (255, 176, 96), 10, 22)
    return save("WR_FacadeNight", color, height, 6, rough, metal)


def facade_brick():
    rng = np.random.default_rng(5)
    xs, ys = coords()
    brick_w, brick_h, mortar = 64, 32, 5
    row = ys // brick_h
    shift = (row % 2) * (brick_w // 2)
    bx = (xs + shift) % brick_w
    by = ys % brick_h
    brick_id = ((xs + shift) // brick_w) % (SIZE // brick_w) + row * 97
    tones = rng.random(100000)
    tone = tones[brick_id % 100000]
    grain = fbm(SIZE, 16, 4, 6)
    color = rgb((118, 54, 40))[None, None, :] * (0.78 + 0.32 * tone[..., None]) + (grain[..., None] - 0.5) * 30
    height = 0.7 + grain * 0.1
    is_mortar = (bx < mortar) | (by < mortar)
    color[is_mortar] = rgb((96, 92, 88)) + (grain[is_mortar][..., None] - 0.5) * 20
    height[is_mortar] = 0.45
    rough = np.where(is_mortar, 0.95, 0.85)
    cols, rows = 4, 4
    cell = SIZE // cols
    lx, ly = xs % cell, ys % cell
    cx, cy = xs // cell, ys // cell
    window = (lx >= 70) & (lx < cell - 70) & (ly >= 48) & (ly < 200)
    sash = window & ~((lx >= 80) & (lx < cell - 80) & (ly >= 58) & (ly < 190))
    glass = window & ~sash
    lit = rng.random((rows, cols)) < 0.3
    color[sash] = rgb((214, 210, 200))
    height[sash] = 0.5
    rough[sash] = 0.6
    vertical = (ly - 58) / 132
    dark = glass & ~lit[cy, cx]
    bright = glass & lit[cy, cx]
    color[dark] = (rgb((28, 34, 44))[None, None, :] * (1.2 - 0.4 * vertical[..., None]))[dark]
    color[bright] = (rgb((250, 190, 110))[None, None, :] * (1.0 - 0.25 * vertical[..., None]))[bright]
    middle = glass & (np.abs(lx - cell // 2) < 3)
    color[middle] = rgb((214, 210, 200))
    height[glass] = 0.05
    rough[glass] = 0.12
    sill = (lx >= 62) & (lx < cell - 62) & (ly >= 200) & (ly < 214)
    lintel = (lx >= 66) & (lx < cell - 66) & (ly >= 36) & (ly < 48)
    for mask in (sill, lintel):
        color[mask] = rgb((176, 168, 152)) + (grain[mask][..., None] - 0.5) * 16
        height[mask] = 0.95
        rough[mask] = 0.8
    return save("WR_FacadeBrick", color, height, 5, rough)


def facade_ribbon():
    xs, ys = coords()
    floor_h = SIZE // 4
    ly = ys % floor_h
    grain = fbm(SIZE, 8, 5, 41)
    color = rgb((150, 152, 156))[None, None, :] + (grain[..., None] - 0.5) * 26
    height = 0.7 + grain * 0.06
    rough = np.full((SIZE, SIZE), 0.8)
    metal = np.zeros((SIZE, SIZE))
    glass = (ly >= 92) & (ly < floor_h - 12)
    vertical = (ly - 92) / (floor_h - 104)
    sweep = 0.5 + 0.5 * np.sin((xs * 1.3 + ys * 0.4) / SIZE * np.pi * 2)
    tint = rgb((30, 64, 86))[None, None, :] * (1.15 - 0.5 * vertical[..., None]) + sweep[..., None] * 26
    color[glass] = tint[glass]
    height[glass] = 0.05
    rough[glass] = 0.06
    mullion = glass & ((xs % 128) < 8)
    color[mullion] = rgb((34, 36, 42))
    height[mullion] = 0.3
    rough[mullion] = 0.4
    metal[mullion] = 0.8
    sill = (ly >= 84) & (ly < 92)
    color[sill] = rgb((96, 98, 104))
    height[sill] = 0.9
    return save("WR_FacadeRibbon", color, height, 5, rough, metal)


def crack_mask(rng, count, length):
    mask = np.zeros((SIZE, SIZE))
    for _ in range(count):
        x, y = rng.integers(0, SIZE, 2)
        angle = rng.random() * np.pi * 2
        for _ in range(length):
            angle += rng.normal(0, 0.35)
            x = (x + np.cos(angle) * 2) % SIZE
            y = (y + np.sin(angle) * 2) % SIZE
            mask[int(y), int(x)] = 1
            if rng.random() < 0.012:
                angle += rng.choice([-1, 1]) * 0.9
    return np.clip(blur(mask, 1) * 3, 0, 1)


def asphalt():
    rng = np.random.default_rng(3)
    grain = fbm(SIZE, 64, 3, 50)
    broad = fbm(SIZE, 4, 4, 51)
    color = rgb((40, 41, 45))[None, None, :] * (0.85 + 0.3 * broad[..., None]) + (grain[..., None] - 0.5) * 34
    specks = rng.random((SIZE, SIZE)) > 0.985
    color[specks] += 38
    height = grain * 0.5 + broad * 0.2 + specks * 0.25
    patches = value_noise(SIZE, 6, 6, 52) > 0.78
    color[patches] *= 0.78
    height[patches] -= 0.05
    cracks = crack_mask(rng, 26, 260)
    color *= (1 - 0.55 * cracks)[..., None]
    height -= cracks * 0.6
    rough = 0.9 - specks * 0.2 - patches * 0.05
    return save("WR_Asphalt", color, height, 4, rough)


def sidewalk():
    rng = np.random.default_rng(9)
    xs, ys = coords()
    slab = SIZE // 2
    lx, ly = xs % slab, ys % slab
    sid = (xs // slab) + (ys // slab) * 2
    tone = rng.random(4)[sid]
    grain = fbm(SIZE, 32, 4, 60)
    stains = fbm(SIZE, 4, 4, 61)
    color = rgb((150, 151, 150))[None, None, :] * (0.88 + 0.16 * tone[..., None]) + (grain[..., None] - 0.5) * 22
    color *= (0.85 + 0.2 * stains)[..., None]
    joint = (lx < 8) | (ly < 8)
    color[joint] = rgb((64, 64, 66))
    height = 0.7 + grain * 0.1
    height[joint] = 0.0
    edge = ((lx < 14) | (ly < 14) | (lx > slab - 6) | (ly > slab - 6)) & ~joint
    height[edge] -= 0.08
    rough = np.where(joint, 0.95, 0.85)
    return save("WR_Sidewalk", color, height, 5, rough)


def deck_plate():
    rng = np.random.default_rng(13)
    xs, ys = coords()
    panel = SIZE // 2
    lx, ly = xs % panel, ys % panel
    brushed = fbm(SIZE, 8, 4, 70, stretch=(1, 16))
    wear = fbm(SIZE, 6, 5, 71)
    color = rgb((72, 76, 84))[None, None, :] + (brushed[..., None] - 0.5) * 30
    seam = (lx < 6) | (ly < 6)
    color[seam] = rgb((22, 23, 27))
    height = 0.6 + brushed * 0.04
    height[seam] = 0.0
    bevel = ((lx < 14) | (ly < 14) | (lx > panel - 8) | (ly > panel - 8)) & ~seam
    color[bevel] += 18
    height[bevel] = 0.5
    rough = 0.45 + (1 - wear) * 0.2
    metal = np.full((SIZE, SIZE), 0.88)
    for bx in (34, panel - 28):
        for by in (34, panel - 28):
            distance = np.sqrt((lx - bx) ** 2 + (ly - by) ** 2)
            bolt = distance < 11
            height[bolt] = 0.9 - distance[bolt] / 40
            color[bolt] = rgb((120, 124, 132)) - distance[bolt][..., None] * 3
            slot = bolt & (np.abs(lx - bx) < 2)
            color[slot] = rgb((30, 30, 34))
            height[slot] = 0.6
    scratches = np.zeros((SIZE, SIZE))
    for _ in range(140):
        x, y = rng.integers(0, SIZE, 2)
        angle = rng.random() * np.pi
        for step in range(rng.integers(20, 90)):
            scratches[int((y + np.sin(angle) * step) % SIZE), int((x + np.cos(angle) * step) % SIZE)] = 1
    color += scratches[..., None] * 40
    rough -= scratches * 0.2
    return save("WR_DeckPlate", color, height, 6, rough, metal)


def wall_panel():
    rng = np.random.default_rng(17)
    xs, ys = coords()
    pw, ph = SIZE // 2, SIZE // 4
    lx, ly = xs % pw, ys % ph
    pid = (xs // pw) + (ys // ph) * 2
    tone = rng.random(8)[pid]
    grain = fbm(SIZE, 16, 5, 80)
    streak = fbm(SIZE, 8, 3, 81, stretch=(1, 6))
    color = rgb((70, 72, 78))[None, None, :] * (0.86 + 0.2 * tone[..., None]) + (grain[..., None] - 0.5) * 24
    color *= (0.9 + 0.15 * streak)[..., None]
    seam = (lx < 8) | (ly < 8)
    color[seam] = rgb((30, 31, 35))
    height = 0.7 + grain * 0.08
    height[seam] = 0.0
    for hx in (pw // 4, pw // 2, 3 * pw // 4):
        for hy in (ph // 3, 2 * ph // 3):
            hole = np.sqrt((lx - hx) ** 2 + (ly - hy) ** 2) < 7
            color[hole] = rgb((36, 37, 41))
            height[hole] = 0.35
    rough = np.where(seam, 0.95, 0.86)
    return save("WR_WallPanel", color, height, 5, rough)


def rust_sheet():
    xs, ys = coords()
    ridge = 0.5 + 0.5 * np.sin(xs / 64 * np.pi * 2)
    rust_mask = fbm(SIZE, 6, 5, 90)
    streaks = fbm(SIZE, 16, 3, 91, stretch=(1, 8))
    rust = np.clip((rust_mask * 0.7 + streaks * 0.5 - 0.45) * 3, 0, 1)
    paint_color = rgb((104, 116, 122))[None, None, :] * (0.85 + 0.25 * ridge[..., None])
    rust_color = rgb((150, 76, 36))[None, None, :] * (0.6 + 0.5 * streaks[..., None]) * (0.85 + 0.2 * ridge[..., None])
    color = paint_color * (1 - rust[..., None]) + rust_color * rust[..., None]
    pits = fbm(SIZE, 64, 2, 92)
    height = ridge * 0.8 + pits * rust * 0.15
    rough = 0.55 + rust * 0.4
    metal = 0.45 * (1 - rust)
    return save("WR_RustSheet", color, height, 9, rough, metal)


def future_panel():
    rng = np.random.default_rng(29)
    tone = np.zeros((SIZE, SIZE))
    seams = np.zeros((SIZE, SIZE), dtype=bool)
    vents = np.zeros((SIZE, SIZE), dtype=bool)

    def split(x0, y0, x1, y1, depth):
        w, h = x1 - x0, y1 - y0
        if depth > 0 and (w > 160 or h > 160) and rng.random() < 0.85:
            if w >= h:
                cut = x0 + int(w * rng.uniform(0.35, 0.65)) // 32 * 32
                split(x0, y0, cut, y1, depth - 1)
                split(cut, y0, x1, y1, depth - 1)
            else:
                cut = y0 + int(h * rng.uniform(0.35, 0.65)) // 32 * 32
                split(x0, y0, x1, cut, depth - 1)
                split(x0, cut, x1, y1, depth - 1)
            return
        tone[y0:y1, x0:x1] = rng.random()
        seams[y0:y0 + 4, x0:x1] = True
        seams[y0:y1, x0:x0 + 4] = True
        if w > 120 and h > 90 and rng.random() < 0.3:
            vy, vx = y0 + 24, x0 + 24
            for slit in range(5):
                vents[vy + slit * 12: vy + slit * 12 + 5, vx: min(vx + 70, x1 - 20)] = True

    split(0, 0, SIZE, SIZE, 6)
    grain = fbm(SIZE, 16, 4, 100)
    color = rgb((226, 228, 232))[None, None, :] * (0.9 + 0.1 * tone[..., None]) + (grain[..., None] - 0.5) * 8
    color[seams] = rgb((70, 74, 82))
    color[vents] = rgb((40, 42, 48))
    height = 0.7 + tone * 0.05
    height[seams] = 0.0
    height[vents] = 0.2
    rough = np.full((SIZE, SIZE), 0.32)
    rough[seams] = 0.7
    metal = np.full((SIZE, SIZE), 0.08)
    return save("WR_FuturePanel", color, height, 5, rough, metal)


def main():
    built = {}
    for factory in (facade_glass, facade_night, facade_brick, facade_ribbon, asphalt, sidewalk, deck_plate, wall_panel, rust_sheet, future_panel):
        maps = factory()
        name = factory.__name__
        built[name] = maps
        print(name, maps)
    (ROOT / "index.json").write_text(json.dumps(built, indent=2))


if __name__ == "__main__":
    main()
