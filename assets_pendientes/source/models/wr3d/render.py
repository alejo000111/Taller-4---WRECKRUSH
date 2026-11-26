import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .bake import rasterize
from .mesh import normalize


def to_linear(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def sample(img, uv):
    h, w = img.shape[:2]
    x = np.clip(uv[:, 0] * w - 0.5, 0, w - 1.001)
    y = np.clip(uv[:, 1] * h - 0.5, 0, h - 1.001)
    x0, y0 = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x - x0, y - y0
    if img.ndim == 3:
        fx, fy = fx[:, None], fy[:, None]
    return img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy) + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy


class Item:
    def __init__(self, pos, nrm, tri, kind="surface", color=(200, 200, 200), uv=None, tan=None, maps=None, transparency=0.0):
        self.pos = pos
        self.nrm = nrm
        self.tri = tri
        self.kind = kind
        self.color = np.asarray(color, dtype=np.float64) / 255.0
        self.uv = uv
        self.tan = tan
        self.maps = maps
        self.transparency = transparency


def _sky(d):
    t = np.clip(d[:, 1] * 0.5 + 0.5, 0, 1)[:, None]
    ground = np.array([0.035, 0.03, 0.05])
    horizon = np.array([0.22, 0.2, 0.32])
    sky = np.array([0.45, 0.5, 0.68])
    low = ground + (horizon - ground) * np.clip(t * 2, 0, 1)
    high = horizon + (sky - horizon) * np.clip(t * 2 - 1, 0, 1)
    out = np.where(t < 0.5, low, high)
    box = np.clip((d[:, 1] - 0.55) * 5, 0, 1)[:, None] * np.clip(1 - np.abs(d[:, 0]) * 1.3, 0, 1)[:, None]
    return out + box * np.array([2.2, 2.1, 2.0])


def _shade(albedo, rough, metal, n, v, lights):
    albedo_l = to_linear(albedo)
    f0 = 0.04 * (1 - metal[:, None]) + albedo_l * metal[:, None]
    diffuse_col = albedo_l * (1 - metal[:, None])
    a = np.clip(rough, 0.04, 1) ** 2
    ndv = np.clip((n * v).sum(1), 1e-3, 1)
    out = np.zeros_like(albedo_l)
    for ldir, lcol in lights:
        l = np.broadcast_to(ldir, n.shape)
        h = normalize(l + v)
        ndl = np.clip((n * l).sum(1), 0, 1)
        ndh = np.clip((n * h).sum(1), 0, 1)
        vdh = np.clip((v * h).sum(1), 0, 1)
        d = a * a / (np.pi * ((ndh * ndh) * (a * a - 1) + 1) ** 2)
        k = (a + 1e-4) / 2
        g = (ndl / (ndl * (1 - k) + k)) * (ndv / (ndv * (1 - k) + k))
        fres = f0 + (1 - f0) * ((1 - vdh) ** 5)[:, None]
        spec = fres * (d * g / np.maximum(4 * ndl * ndv, 1e-4))[:, None]
        out += (diffuse_col / np.pi * (1 - fres) + spec) * (ndl[:, None] * lcol)
    amb = _sky(n) * 0.55
    r = normalize(2 * (n * v).sum(1, keepdims=True) * n - v)
    env = _sky(r)
    blur = np.clip(rough, 0, 1)[:, None]
    env = env * (1 - blur * 0.75) + amb * blur * 0.75
    fres_env = f0 + (np.maximum(1 - rough, f0.mean(1))[:, None] - f0) * ((1 - ndv) ** 5)[:, None]
    out += diffuse_col * amb + env * fres_env
    return out


def _blur(img, sigma):
    if sigma <= 0:
        return img
    radius = int(sigma * 3)
    x = np.arange(-radius, radius + 1)
    k = np.exp(-(x * x) / (2 * sigma * sigma))
    k /= k.sum()
    out = img
    for axis in (0, 1):
        padded = np.pad(out, [(radius, radius) if a == axis else (0, 0) for a in range(out.ndim)], mode="edge")
        acc = np.zeros_like(out)
        for i, w in enumerate(k):
            sl = [slice(None)] * out.ndim
            sl[axis] = slice(i, i + out.shape[axis])
            acc += padded[tuple(sl)] * w
        out = acc
    return out


def _bloom(img, sigma):
    factor = max(1, int(sigma // 3))
    h, w = img.shape[:2]
    hh, ww = h // factor, w // factor
    small = img[:hh * factor, :ww * factor].reshape(hh, factor, ww, factor, 3).mean((1, 3))
    small = _blur(small, sigma / factor)
    channels = []
    for c in range(3):
        band = Image.fromarray(small[..., c].astype(np.float32), mode="F").resize((w, h), Image.BILINEAR)
        channels.append(np.asarray(band, dtype=np.float64))
    return np.stack(channels, -1)


def render_view(items, eye, target, width=640, height=480, fov=32.0, ss=2, background=None):
    W, H = width * ss, height * ss
    eye = np.asarray(eye, dtype=np.float64)
    forward = normalize(np.asarray(target, dtype=np.float64) - eye)
    up_hint = np.array([0.0, 1.0, 0.0]) if abs(forward[1]) < 0.98 else np.array([0.0, 0.0, -1.0])
    right = normalize(np.cross(forward, up_hint))
    up = np.cross(right, forward)
    tan_half = np.tan(np.radians(fov) / 2)
    aspect = W / H
    key = normalize(-forward * 0.55 + up * 0.75 - right * 0.55)
    fill = normalize(-forward * 0.7 + right * 0.8 + up * 0.15)
    rim = normalize(forward * 0.9 + up * 0.5 + right * 0.3)
    lights = [(key, np.array([2.9, 2.7, 2.45])), (fill, np.array([0.55, 0.65, 0.95])), (rim, np.array([1.3, 1.1, 1.6]))]
    yy = np.linspace(0, 1, H)[:, None, None]
    if background is None:
        top = np.array([0.07, 0.07, 0.13])
        bottom = np.array([0.02, 0.02, 0.035])
        frame = np.broadcast_to(top * (1 - yy) + bottom * yy, (H, W, 3)).copy()
    else:
        frame = np.broadcast_to(np.asarray(background), (H, W, 3)).copy()
    frame = to_linear(frame)
    glow = np.zeros((H, W, 3))
    zbuf = np.full((H, W), np.inf)
    passes = [[it for it in items if it.kind != "glass"], [it for it in items if it.kind == "glass"]]
    for pass_index, group in enumerate(passes):
        for it in group:
            rel = it.pos - eye
            xc = rel @ right
            yc = rel @ up
            zc = rel @ forward
            zc_safe = np.maximum(zc, 1e-3)
            sx = (xc / (zc_safe * tan_half * aspect) * 0.5 + 0.5) * W
            sy = (1 - (yc / (zc_safe * tan_half) * 0.5 + 0.5)) * H
            px = np.column_stack([sx, sy])
            tri = it.tri[(zc[it.tri] > 0.05).all(1)]
            if it.kind != "glass" and len(tri):
                p0, p1, p2 = it.pos[tri[:, 0]], it.pos[tri[:, 1]], it.pos[tri[:, 2]]
                facing = (np.cross(p1 - p0, p2 - p0) * (eye - p0)).sum(1) > 0
                tri = tri[facing]
            if len(tri) == 0:
                continue
            tri_id, bary, z = rasterize(px, tri, W, H, depth=zc)
            hit = tri_id >= 0
            if pass_index == 0:
                hit &= z < zbuf
            else:
                hit &= z < zbuf
            ys, xs = np.nonzero(hit)
            if len(ys) == 0:
                continue
            tv = tri[tri_id[ys, xs]]
            w = bary[ys, xs]
            invz = 1.0 / zc[tv]
            wp = w * invz
            wp /= wp.sum(1, keepdims=True)

            def interp(attr):
                return (attr[tv] * wp[..., None]).sum(1)

            P = interp(it.pos)
            N = normalize(interp(it.nrm))
            V = normalize(eye - P)
            if it.kind == "neon":
                c = to_linear(np.broadcast_to(it.color, (len(ys), 3)))
                col = c * 1.6 + 0.15
                glow[ys, xs] = c * 2.2
            elif it.kind == "surface" and it.maps is not None:
                uv = interp(it.uv)
                base = sample(it.maps["color"], uv)
                alpha = sample(it.maps["alpha"], uv)[:, None]
                albedo = base * alpha + it.color[None, :] * (1 - alpha)
                rough = sample(it.maps["roughness"], uv)
                metal = sample(it.maps["metalness"], uv)
                nts = sample(it.maps["normal"], uv)
                tan = interp(it.tan[:, :3])
                sign = np.where(interp(it.tan[:, 3:4])[:, 0] < 0, -1.0, 1.0)
                T = normalize(tan - N * (tan * N).sum(1, keepdims=True))
                B = np.cross(N, T) * sign[:, None]
                Nm = normalize(T * nts[:, 0:1] + B * nts[:, 1:2] + N * nts[:, 2:3])
                col = _shade(albedo, rough, metal, Nm, V, lights)
            elif it.kind == "glass":
                albedo = np.broadcast_to(it.color, (len(ys), 3))
                col = _shade(albedo, np.full(len(ys), 0.05), np.zeros(len(ys)), N, V, lights)
            else:
                albedo = np.broadcast_to(it.color, (len(ys), 3))
                metal = np.full(len(ys), 0.6 if it.kind == "foil" else 0.0)
                col = _shade(albedo, np.full(len(ys), 0.3 if it.kind == "foil" else 0.5), metal, N, V, lights)
            if it.kind == "glass":
                t = it.transparency
                frame[ys, xs] = frame[ys, xs] * t + col * (1 - t)
            else:
                frame[ys, xs] = col
                zbuf[ys, xs] = z[ys, xs]
    if glow.max() > 0:
        frame = frame + _bloom(glow, W / 90) * 0.9 + _bloom(glow, W / 30) * 0.5
    frame = frame / (1 + frame * 0.35)
    img = to_srgb(frame * 1.15)
    img = img.reshape(height, ss, width, ss, 3).mean((1, 3))
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def orbit(center, radius, azimuth, elevation, fov=32.0):
    az, el = np.radians(azimuth), np.radians(elevation)
    dist = radius / np.sin(np.radians(fov) / 2) * 1.08
    d = np.array([np.sin(az) * np.cos(el), np.sin(el), np.cos(az) * np.cos(el)])
    return np.asarray(center) + d * dist


def contact_sheet(items, center, radius, views, path, tile=(640, 480), title=None):
    tiles = []
    for name, az, el in views:
        eye = orbit(center, radius, az, el)
        tiles.append((name, render_view(items, eye, center, tile[0], tile[1])))
    cols = 2
    rows = (len(tiles) + 1) // 2
    sheet = Image.new("RGB", (tile[0] * cols, tile[1] * rows + (36 if title else 0)), (10, 10, 16))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    oy = 36 if title else 0
    if title:
        draw.text((12, 8), title, fill=(255, 210, 31), font=font)
    for i, (name, arr) in enumerate(tiles):
        x, y = (i % cols) * tile[0], (i // cols) * tile[1] + oy
        sheet.paste(Image.fromarray(arr), (x, y))
        draw.text((x + 10, y + 8), name, fill=(220, 220, 230), font=font)
    sheet.save(path)
    return path
