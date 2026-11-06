import numpy as np

from wr3d import Material, register, T, compose, align_y
from wr3d import shapes as sh
from wr3d.materials import REGISTRY, Surface, scratch_mask, grime_amount, wear_mask, rgb, _sample_mask
from wr3d.noise import worley, smoothstep, mix


def _axis_frame(ctx, p):
    center = np.asarray(p.get("center", (0.0, 0.0, 0.0)), dtype=np.float64)
    axis = np.asarray(p.get("axis", (0.0, 0.0, -1.0)), dtype=np.float64)
    axis = axis / np.linalg.norm(axis)
    d = ctx.P - center
    along = d @ axis
    radial = np.linalg.norm(d - along[:, None] * axis, axis=1)
    return axis, along, radial


@register("hammers_machined")
def machined(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (176, 178, 186)))
    axis, along, radial = _axis_frame(ctx, p)
    facing = smoothstep(0.6, 0.95, ctx.N @ axis)
    marks = 0.5 + 0.5 * np.sin(radial * p.get("ring_freq", 240.0))
    var = ctx.noise(3.0, 4, 5)
    fine = ctx.noise(20.0, 3, 6)
    groove = np.zeros(ctx.n)
    for r, w in p.get("rings", ()):
        groove = np.maximum(groove, 1 - smoothstep(w * 0.35, w * 0.5, np.abs(radial - r)))
    groove *= facing
    zone = 1 - smoothstep(p.get("zone", 0.45) - 0.03, p.get("zone", 0.45) + 0.03, radial)
    f1, _, _ = worley(ctx.Ps * p.get("dent_scale", 9.0), 51)
    dents = (1 - smoothstep(0.0, 0.2, f1)) * smoothstep(-0.1, 0.4, ctx.noise(1.6, 2, 52)) * p.get("dents", 0.6) * facing
    polish = smoothstep(0.25, 0.9, np.clip(ctx.E, 0, 1)) * p.get("polish", 0.8)
    scr = scratch_mask(ctx, p.get("scratches", 0.3))
    shade = 0.9 + 0.05 * var + 0.04 * fine + 0.06 * marks * facing + 0.14 * polish - 0.42 * groove - 0.1 * dents + 0.08 * zone * facing - 0.08 * scr
    s.base = np.clip(color[None, :] * shade[:, None], 0, 1)
    s.rough = np.clip(p.get("rough", 0.26) + 0.05 * fine - 0.05 * marks * facing - 0.1 * polish + 0.3 * groove + 0.12 * dents - 0.06 * zone * facing, 0.05, 1)
    s.metal = np.ones(ctx.n)
    s.height = 0.0004 * marks * facing - 0.006 * groove - 0.003 * dents - 0.0008 * scr
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.2)) + groove * 0.25, 0, 0.8)
    return s


HEAT_STOPS = np.array([
    (0.00, (150, 152, 158)),
    (0.30, (196, 168, 96)),
    (0.48, (178, 104, 52)),
    (0.64, (122, 62, 128)),
    (0.80, (60, 88, 168)),
    (1.00, (42, 46, 62)),
], dtype=object)


def _heat_color(t):
    keys = np.array([k for k, _ in HEAT_STOPS], dtype=np.float64)
    cols = np.array([rgb(c) for _, c in HEAT_STOPS])
    out = np.zeros((len(t), 3))
    for ch in range(3):
        out[:, ch] = np.interp(t, keys, cols[:, ch])
    return out


@register("hammers_heat")
def heat(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (92, 94, 102)))
    axis, along, radial = _axis_frame(ctx, p)
    length = p.get("length", 0.5)
    t = np.clip(along / length + 0.07 * ctx.noise(4.0, 3, 61), 0, 1)
    tint = _heat_color(t)
    var = ctx.noise(3.0, 4, 62)
    fine = ctx.noise(22.0, 3, 63)
    polish = smoothstep(0.3, 0.9, np.clip(ctx.E, 0, 1)) * p.get("polish", 0.5)
    amount = p.get("amount", 0.8) * smoothstep(0.05, 0.3, t)
    base = color[None, :] * (0.9 + 0.08 * var + 0.05 * fine + 0.2 * polish)[:, None]
    s.base = np.clip(mix(base, tint * (0.95 + 0.1 * var)[:, None], amount), 0, 1)
    soot = smoothstep(0.75, 1.0, t) * smoothstep(-0.2, 0.5, ctx.noise(6.0, 3, 64)) * p.get("soot", 0.5)
    s.base = mix(s.base, rgb((22, 20, 22)), soot * (1 - polish))
    s.rough = np.clip(p.get("rough", 0.3) + 0.06 * fine - 0.12 * polish + 0.4 * soot, 0.05, 1)
    s.metal = np.clip(1 - soot * 0.7, 0, 1)
    s.height = scratch_mask(ctx, 0.2) * -0.0008 + soot * 0.0008 * fine
    s.dirt = grime_amount(ctx, p.get("dirt", 0.2))
    return s


@register("hammers_stamped")
def stamped(ctx, p):
    base = p["base"]
    s = REGISTRY[base.kind](ctx, base.params)
    u, v = ctx.U[:, 0], ctx.U[:, 1]
    for st in p.get("stamps", ()):
        mask = st["mask"]
        cu, cv = st.get("center", (0.0, 0.0))
        ang = np.radians(st.get("angle", 0.0))
        du, dv = u - cu, v - cv
        ru = du * np.cos(ang) + dv * np.sin(ang)
        rv = -du * np.sin(ang) + dv * np.cos(ang)
        mh, mw = mask.shape
        w, h = st["size"]
        cov = _sample_mask(mask, (ru / w + 0.5) * (mw - 1), (rv / h + 0.5) * (mh - 1))
        if not np.any(cov > 0):
            continue
        if st.get("wear", 0) > 0:
            cov = cov * (1 - wear_mask(ctx, st["wear"]) * 0.8)
        col = rgb(st.get("color", (255, 255, 255)))
        if st.get("keep_color"):
            s.base = s.base * (1 + st.get("brighten", 0.0) * cov)[:, None]
        else:
            s.base = mix(s.base, np.broadcast_to(col, s.base.shape) * (0.92 + 0.08 * ctx.noise(6.0, 2, 71))[:, None], cov)
            s.paint = s.paint * (1 - cov)
        if "metal" in st:
            s.metal = mix(s.metal, st["metal"], cov)
        if "rough" in st:
            s.rough = mix(s.rough, st["rough"], cov)
        s.height = s.height + cov * st.get("raise", -0.003)
    return s


def place(mesh, pos, normal=(0.0, 1.0, 0.0)):
    return mesh.transformed(compose(T(*pos), align_y(normal)))


def hex_bolt(radius, height, mat, washer=None):
    prof = sh.round_polyline([(0, 0), (radius * 1.0, 0), (radius, height * 0.62), (radius * 0.72, height), (0, height)], [0, 0, 0.012, 0.01, 0], 2)
    head = sh.lathe(prof, 6, mat, smooth_angle=50, localize=False, start=30)
    if washer is None:
        return head
    ring = sh.lathe([(0, 0), (radius * 1.35, 0), (radius * 1.35, washer), (0, washer)], 14, mat, smooth_angle=50, localize=False)
    return [ring, head.transformed(T(0, washer * 0.6, 0))]


def ribbed_profile(r0, r1, y0, y1, ribs, base, peak, steps=6, flare=0.03):
    pts = [(r0, y0), (base + flare, y0 + 0.005), (base + flare, y0 + 0.04)]
    span = (y1 - 0.04) - (y0 + 0.04)
    for k in range(ribs):
        for j in range(steps):
            t = (k + j / steps) / ribs
            y = y0 + 0.04 + t * span
            bump = np.sin(np.pi * (j / steps)) ** 2
            pts.append((base + (peak - base) * bump, y))
    pts += [(base + flare, y1 - 0.04), (base + flare, y1 - 0.005), (r1, y1)]
    return pts
