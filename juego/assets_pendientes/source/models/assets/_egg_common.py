import numpy as np

from wr3d import register, T, R, compose, align_y
from wr3d import shapes as sh
from wr3d.materials import Surface, grime_amount, scratch_mask, wear_mask, rgb
from wr3d.noise import worley, smoothstep, mix, hash3

EGG_H = 4.0
EGG_R = 1.5
TAPER = 0.18


def egg_radius(y, height=EGG_H, radius=EGG_R, taper=TAPER):
    t = np.arccos(np.clip(-y / (height / 2), -1, 1))
    return radius * np.sin(t) * (1 - taper * (y / (height / 2)))


def egg_normal(theta_deg, y, height=EGG_H, radius=EGG_R, taper=TAPER):
    eps = 1e-3
    r0, r1 = egg_radius(y - eps, height, radius, taper), egg_radius(y + eps, height, radius, taper)
    dr = (r1 - r0) / (2 * eps)
    nr, ny = 1.0, -dr
    n = np.hypot(nr, ny)
    th = np.radians(theta_deg)
    return np.array([nr / n * np.cos(th), ny / n, -nr / n * np.sin(th)])


def egg_point(theta_deg, y, lift=0.0, height=EGG_H, radius=EGG_R, taper=TAPER):
    r = egg_radius(y, height, radius, taper)
    th = np.radians(theta_deg)
    p = np.array([r * np.cos(th), y, -r * np.sin(th)])
    return p + egg_normal(theta_deg, y, height, radius, taper) * lift


def shell(mat, segments=16, rings=12, height=EGG_H, radius=EGG_R, taper=TAPER):
    return sh.lathe(sh.egg_profile(height, radius, taper, rings), segments, mat, smooth_angle=89, start=90)


def band(y0, y1, lift, mat, segments=16, height=EGG_H, radius=EGG_R):
    ys = np.linspace(y0, y1, 3)
    outer = [(egg_radius(y, height, radius) + lift, y) for y in ys]
    prof = [(egg_radius(y0, height, radius) - 0.02, y0)] + outer + [(egg_radius(y1, height, radius) - 0.02, y1)]
    return sh.lathe(prof, segments, mat, smooth_angle=50, start=90, closed=False)


def place(mesh, theta_deg, y, lift=0.0, spin=0.0, height=EGG_H, radius=EGG_R):
    p = egg_point(theta_deg, y, lift, height, radius)
    n = egg_normal(theta_deg, y, height, radius)
    return mesh.transformed(compose(T(*p), align_y(n), R(0, spin, 0)))


def _cell_hash(cell):
    return (cell & 0xFFFF) / 65535.0


@register("egg_scrap_plates")
def egg_scrap_plates(ctx, p):
    s = Surface(ctx.n)
    paint = rgb(p.get("color", (255, 122, 26)))
    scrap = rgb(p.get("scrap", (128, 130, 138)))
    f1, f2, cell = worley(ctx.P * p.get("scale", 1.55), 91)
    h = _cell_hash(cell)
    seam = 1 - smoothstep(0.0, 0.05, f2 - f1)
    bead = (1 - smoothstep(0.05, 0.09, f2 - f1)) * (1 - seam)
    g1, _, _ = worley(ctx.P * 7.0, 92)
    rivet = (1 - smoothstep(0.1, 0.16, g1)) * smoothstep(0.09, 0.12, f2 - f1) * (1 - smoothstep(0.16, 0.22, f2 - f1))
    bare = h < 0.18
    tint = 0.86 + 0.18 * ((h * 7.31) % 1.0)
    wear = wear_mask(ctx, p.get("wear", 0.35)) * 0.6
    chips = smoothstep(0.55, 0.7, ctx.noise(6.0, 3, 93)) * 0.5
    paint_amt = np.where(bare, 0.0, 1.0) * (1 - np.maximum(wear, chips))
    base_metal = scrap[None, :] * (0.85 + 0.2 * ctx.noise(5.0, 3, 94))[:, None]
    s.base = mix(base_metal, paint[None, :] * tint[:, None], paint_amt)
    s.base = mix(s.base, rgb((40, 34, 30)), seam * 0.8)
    s.base = mix(s.base, rgb((170, 150, 120)), bead * 0.35)
    s.base = mix(s.base, rgb((150, 150, 156)), rivet)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(np.where(paint_amt > 0.5, 0.45, 0.32) + 0.1 * seam - 0.1 * rivet, 0.05, 1)
    s.metal = np.clip(1 - paint_amt + rivet, 0, 1) * 0.9
    s.height = -seam * 0.012 + bead * 0.004 + rivet * 0.012 + h * 0.004 - scratch_mask(ctx, 0.3) * 0.001
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.3)) + seam * 0.3, 0, 0.8)
    return s


@register("egg_armor")
def egg_armor(ctx, p):
    s = Surface(ctx.n)
    color = rgb(p.get("color", (255, 59, 59)))
    theta = np.degrees(np.arctan2(-ctx.P[:, 2], ctx.P[:, 0])) % 360.0
    y = ctx.P[:, 1]
    groove = np.zeros(ctx.n)
    for ly in p.get("latitudes", (-0.95, 0.95)):
        groove = np.maximum(groove, 1 - smoothstep(0.012, 0.03, np.abs(y - ly)))
    step = p.get("meridian_step", 60.0)
    dtheta = np.abs(((theta + step / 2) % step) - step / 2)
    r = np.maximum(np.sqrt(ctx.P[:, 0] ** 2 + ctx.P[:, 2] ** 2), 0.05)
    mer = 1 - smoothstep(0.012, 0.03, np.radians(dtheta) * r)
    groove = np.maximum(groove, mer * (np.abs(y) < 1.6))
    bolts = np.zeros(ctx.n)
    for ly in p.get("latitudes", (-0.95, 0.95)):
        for k in range(int(360 / step)):
            th = k * step + step / 2
            d = np.sqrt((np.radians(((theta - th + 180) % 360) - 180) * r) ** 2 + (y - (ly + 0.12 * np.sign(ly))) ** 2)
            bolts = np.maximum(bolts, np.sqrt(np.clip(1 - (d / 0.07) ** 2, 0, 1)))
    wear = smoothstep(0.6, 0.75, ctx.noise(5.0, 3, 95)) * p.get("chips", 0.4)
    under = rgb((140, 142, 150))
    s.base = mix(color[None, :] * (0.92 + 0.08 * ctx.noise(2.0, 3, 96))[:, None], under, wear)
    s.base = mix(s.base, rgb((40, 30, 30)), groove * 0.85)
    s.base = mix(s.base, rgb((90, 92, 100)) * (0.8 + 0.4 * bolts[:, None]), (bolts > 0.01) * 1.0)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.38 + 0.2 * groove - 0.12 * (bolts > 0.01) - 0.1 * wear, 0, 1)
    s.metal = np.clip(wear + (bolts > 0.01), 0, 1) * 0.9
    s.height = -groove * 0.012 + bolts * 0.014 - scratch_mask(ctx, 0.3) * 0.001
    s.dirt = np.clip(grime_amount(ctx, p.get("dirt", 0.3)) + groove * 0.25, 0, 0.8)
    return s


def _segment_distance(points, segments):
    best = np.full(len(points), np.inf)
    for a, b in segments:
        ab = b - a
        t = np.clip(((points - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
        best = np.minimum(best, np.linalg.norm(points - (a + t[:, None] * ab), axis=1))
    return best


@register("egg_obsidian")
def egg_obsidian(ctx, p):
    s = Surface(ctx.n)
    f1, f2, cell = worley(ctx.P * p.get("scale", 2.2), 97)
    h = _cell_hash(cell)
    edge = 1 - smoothstep(0.0, 0.05, f2 - f1)
    base = rgb(p.get("color", (34, 20, 54)))
    sheen = rgb(p.get("sheen", (166, 77, 255)))
    tone = 0.75 + 0.35 * h
    s.base = base[None, :] * tone[:, None]
    s.base = mix(s.base, sheen * 0.55, edge * 0.6)
    glow = rgb(p.get("glow", (255, 59, 160)))
    segs = p.get("cracks", [])
    if segs:
        d = _segment_distance(ctx.P, segs)
        halo = np.exp(-d / p.get("halo", 0.09))
        s.base = mix(s.base, glow * 0.95, halo * 0.85)
        s.height = -halo * 0.006
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.1 + 0.08 * edge + 0.05 * h, 0, 1)
    s.metal = np.full(ctx.n, 0.35)
    s.height = s.height - edge * 0.006 + h * 0.003
    s.dirt = grime_amount(ctx, p.get("dirt", 0.05))
    return s


def crack_path(theta0, y0, theta1, y1, jag, seed, lift=0.025, steps=9):
    rng = np.random.default_rng(seed)
    pts = []
    for i, t in enumerate(np.linspace(0, 1, steps)):
        th = theta0 + (theta1 - theta0) * t + (rng.uniform(-jag, jag) if 0 < i < steps - 1 else 0)
        y = y0 + (y1 - y0) * t
        pts.append(egg_point(th, y, lift))
    return pts


@register("egg_gauge")
def egg_gauge(ctx, p):
    s = Surface(ctx.n)
    c = np.asarray(p["center"], dtype=np.float64)
    n = np.asarray(p["normal"], dtype=np.float64)
    n = n / np.linalg.norm(n)
    up = np.array([0.0, 1.0, 0.0]) - n * n[1]
    up /= np.linalg.norm(up)
    right = np.cross(up, n)
    d = ctx.P - c
    x, y = d @ right, d @ up
    rho = np.sqrt(x * x + y * y)
    phi = np.degrees(np.arctan2(x, y))
    radius = p.get("radius", 0.22)
    face = rho < radius * 0.86
    ring = (rho >= radius * 0.86)
    ticks = np.zeros(ctx.n)
    for a in range(-120, 121, 30):
        ticks = np.maximum(ticks, (np.abs(phi - a) < 2.5) & (rho > radius * 0.58) & (rho < radius * 0.8))
    red_zone = (phi > 70) & (phi < 120) & (rho > radius * 0.66) & (rho < radius * 0.8)
    na = np.radians(p.get("needle", 45.0))
    nx, ny = np.sin(na), np.cos(na)
    along = x * nx + y * ny
    across = np.abs(-x * ny + y * nx)
    needle = (across < 0.012) & (along > -0.02) & (along < radius * 0.72)
    hub = rho < 0.03
    col = np.where(face[:, None], rgb((236, 230, 212)), rgb((70, 72, 80)))
    col = np.where(red_zone[:, None], rgb((220, 40, 40)), col)
    col = np.where((ticks > 0)[:, None], rgb((30, 30, 34)), col)
    col = np.where(needle[:, None], rgb((210, 30, 30)), col)
    col = np.where(hub[:, None], rgb((30, 30, 34)), col)
    s.base = col
    s.rough = np.where(face, 0.25, 0.35)
    s.metal = np.where(ring, 0.9, 0.0)
    s.height = np.where(ring, 0.004, 0.0) + needle * 0.002
    s.dirt = grime_amount(ctx, 0.15)
    return s
