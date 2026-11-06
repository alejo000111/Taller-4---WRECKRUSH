"""WRECKRUSH brand asset library.

Shared helpers for every brand generator:
  * palette + paths
  * Edge headless renderer (HTML/SVG -> PNG, parallel batches, waits for the file)
  * SVG building blocks: bursts, shards, jagged cracks, skylines, cuboids,
    blocky avatar, explosions, headline text, hazard stripes.

Everything is plain SVG rendered by Microsoft Edge so the sources stay editable.
"""
from __future__ import annotations

import math
import os
import random
import shutil
import subprocess
import time
import uuid
from pathlib import Path

from PIL import Image, ImageFont

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SRC = Path(__file__).resolve().parent
ASSETS = SRC.parent
BRAND = ASSETS / "brand"
THUMBS = ASSETS / "thumbnails"
BUILD = SRC / "build"
PROFILE_BASE = Path(os.environ.get("TEMP", str(SRC))) / "wreckrush_edge_profiles"

for _d in (BRAND, THUMBS, BUILD):
    _d.mkdir(parents=True, exist_ok=True)

PAL = dict(
    black="#0A0A0D", dark="#16171D", dark2="#1E2029", white="#F5F5F7",
    orange="#FF7A1A", yellow="#FFD21F", red="#FF3B3B", purple="#A64DFF",
    cyan="#22E1FF", gold="#FFC428",
)
INK = PAL["black"]
FONT = "Impact, 'Arial Black', sans-serif"
_IMPACT = ImageFont.truetype(r"C:\Windows\Fonts\impact.ttf", 1000)
CAP = 0.791


def text_width(text: str, size: float, letter_spacing: float = 0.0) -> float:
    """Advance width of `text` in Impact (no kerning, like font-kerning:none)."""
    return _IMPACT.getlength(text) * size / 1000.0 + letter_spacing * len(text)


def char_advances(text: str, size: float):
    return [_IMPACT.getlength(c) * size / 1000.0 for c in text]


def html_page(svg: str, w: int, h: int, bg: str = "transparent") -> str:
    return (
        "<!doctype html><html><head><meta charset='utf-8'><style>"
        f"html,body{{margin:0;padding:0;background:{bg};overflow:hidden;width:{w}px;height:{h}px}}"
        "svg{display:block}text{font-kerning:none}"
        f"</style></head><body>{svg}</body></html>"
    )


def render_many(jobs, timeout: float = 120.0):
    """jobs: iterable of (html_path, png_path, w, h). Renders in parallel with Edge.

    Edge's launcher returns immediately and writes the screenshot later, so we
    poll each target until it exists with the right size and can be decoded.
    """
    jobs = [(Path(a), Path(b), int(w), int(h)) for a, b, w, h in jobs]
    PROFILE_BASE.mkdir(parents=True, exist_ok=True)
    pending = {}
    for html, png, w, h in jobs:
        png.parent.mkdir(parents=True, exist_ok=True)
        if png.exists():
            png.unlink()
        prof = PROFILE_BASE / uuid.uuid4().hex[:10]
        args = [
            EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--default-background-color=00000000", "--force-device-scale-factor=1",
            f"--user-data-dir={prof}", "--no-first-run", "--no-default-browser-check",
            "--disable-extensions", "--allow-file-access-from-files",
            "--virtual-time-budget=4000", f"--window-size={w},{h}",
            f"--screenshot={png}", html.resolve().as_uri(),
        ]
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pending[png] = (w, h, prof)
    deadline = time.time() + timeout
    done = []
    last_size = {}
    while pending and time.time() < deadline:
        for png in list(pending):
            w, h, prof = pending[png]
            if not png.exists():
                continue
            sz = png.stat().st_size
            if last_size.get(png) != sz:
                last_size[png] = sz
                continue
            try:
                with Image.open(png) as im:
                    im.load()
                    ok = im.size == (w, h)
            except Exception:
                ok = False
            if ok:
                done.append(png)
                del pending[png]
        time.sleep(0.4)
    if pending:
        raise RuntimeError(f"Edge render timed out for: {[str(p) for p in pending]}")
    time.sleep(1.0)
    shutil.rmtree(PROFILE_BASE, ignore_errors=True)
    return done


def render_svg(svg: str, name: str, out_png: Path, w: int, h: int, bg="transparent", save_svg: Path | None = None):
    """Write html wrapper (+ optional .svg source) and return a render job tuple."""
    html = BUILD / f"{name}.html"
    html.write_text(html_page(svg, w, h, bg), encoding="utf-8")
    if save_svg is not None:
        save_svg.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    return (html, Path(out_png), w, h)


def pts(points) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def burst_points(cx, cy, n, rx, ry, rng, inner=(0.55, 0.7), outer=(0.86, 1.0), rot=0.0, jitter=0.25):
    out = []
    for i in range(2 * n):
        a = rot + math.pi * i / n + rng.uniform(-jitter, jitter) * math.pi / n
        r = rng.uniform(*outer) if i % 2 == 0 else rng.uniform(*inner)
        out.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    return out


def jag_line(p0, p1, segs, amp, rng):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    out = [p0]
    for i in range(1, segs):
        t = i / segs + rng.uniform(-0.3, 0.3) / segs
        o = amp * rng.uniform(0.35, 1.0) * (1 if i % 2 else -1)
        out.append((p0[0] + dx * t + nx * o, p0[1] + dy * t + ny * o))
    out.append(p1)
    return out


def shard_points(cx, cy, size, angle, rng, stretch=1.8):
    """Irregular triangle elongated along `angle` (radians)."""
    out = []
    base = [0.0, 2.2, 4.1]
    for k, b in enumerate(base):
        a = b + rng.uniform(-0.35, 0.35)
        r = size * (stretch if k == 0 else rng.uniform(0.45, 0.8))
        x, y = math.cos(a) * r, math.sin(a) * r
        ca, sa = math.cos(angle), math.sin(angle)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def quad_chunk(cx, cy, size, rng, rot=None):
    """Irregular 4-6 sided rock/concrete chunk."""
    n = rng.randint(4, 6)
    rot = rng.uniform(0, math.tau) if rot is None else rot
    out = []
    for i in range(n):
        a = rot + math.tau * i / n + rng.uniform(-0.3, 0.3)
        r = size * rng.uniform(0.6, 1.0)
        out.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return out


def shade(hex_color: str, f: float) -> str:
    """Multiply (f<1 darker) or lighten towards white (f>1)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if f <= 1:
        r, g, b = r * f, g * f, b * f
    else:
        t = f - 1
        r, g, b = r + (255 - r) * t, g + (255 - g) * t, b + (255 - b) * t
    return "#%02X%02X%02X" % (int(max(0, min(255, r))), int(max(0, min(255, g))), int(max(0, min(255, b))))


def lin_grad(gid, stops, x1=0, y1=0, x2=0, y2=1, user=None):
    """stops: list of (offset, color[, opacity]). user=(x1,y1,x2,y2) for userSpaceOnUse."""
    s = "".join(
        f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{st[0]}"' if st else "") + "/>"
        for o, c, *st in stops
    )
    if user:
        x1, y1, x2, y2 = user
        return f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'
    return f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rad_grad(gid, stops, cx=0.5, cy=0.5, r=0.5, user=None, fx=None, fy=None):
    s = "".join(
        f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{st[0]}"' if st else "") + "/>"
        for o, c, *st in stops
    )
    if user:
        cx, cy, r = user
        f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
        return f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{r}"{f}>{s}</radialGradient>'
    return f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'


CHROME_STOPS = [
    (0.00, "#FFFFFF"), (0.20, "#E6E9EF"), (0.45, "#A2A9B7"), (0.50, "#5A606E"),
    (0.53, "#2E323C"), (0.62, "#7F8696"), (0.84, "#D6DBE3"), (1.00, "#FFFFFF"),
]
RING_STOPS = [(0.0, "#FFE04A"), (0.45, "#FF8A1F"), (1.0, "#E2381A")]


def blur_filter(fid, std, extra=""):
    return (f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%" color-interpolation-filters="sRGB">'
            f'<feGaussianBlur stdDeviation="{std}"/>{extra}</filter>')


def drop_shadow_filter(fid, dx, dy, std, opacity=0.6, color="#000"):
    return (f'<filter id="{fid}" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
            f'<feDropShadow dx="{dx}" dy="{dy}" stdDeviation="{std}" flood-color="{color}" flood-opacity="{opacity}"/></filter>')


def hazard_pattern(pid, size=40, c1="#FFD21F", c2="#0A0A0D", angle=-45):
    return (f'<pattern id="{pid}" width="{size}" height="{size}" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate({angle})"><rect width="{size}" height="{size}" fill="{c2}"/>'
            f'<rect width="{size/2}" height="{size}" fill="{c1}"/></pattern>')


def skyline(rng, x0, x1, base_y, hmin, hmax, wmin, wmax, color, win=None, lit=0.25,
            gap=(0, 14), broken=0.0, stroke=None, sw=0, roof=True, win_size=(10, 14)):
    """Row of building silhouettes. `broken` = probability of a jagged destroyed top."""
    out = []
    x = x0
    while x < x1:
        w = rng.uniform(wmin, wmax)
        h = rng.uniform(hmin, hmax)
        top = base_y - h
        if rng.random() < broken:

            n = rng.randint(3, 6)
            poly = [(x, base_y), (x, top + rng.uniform(0, h * 0.3))]
            for i in range(1, n):
                poly.append((x + w * i / n, top + rng.uniform(0, h * 0.45)))
            poly += [(x + w, top + rng.uniform(0, h * 0.3)), (x + w, base_y)]
            out.append(f'<polygon points="{pts(poly)}" fill="{color}"' +
                       (f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else "") + "/>")
            ytop_for_windows = top + h * 0.45
        else:
            out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h + 2:.1f}" fill="{color}"' +
                       (f' stroke="{stroke}" stroke-width="{sw}"' if stroke else "") + "/>")
            ytop_for_windows = top
            if roof and rng.random() < 0.45:
                rw = w * rng.uniform(0.2, 0.5)
                rx = x + rng.uniform(0, w - rw)
                rh = rng.uniform(10, 40)
                out.append(f'<rect x="{rx:.1f}" y="{top - rh:.1f}" width="{rw:.1f}" height="{rh + 1:.1f}" fill="{color}"/>')
                if rng.random() < 0.5:
                    ax = rx + rw / 2
                    out.append(f'<rect x="{ax - 2:.1f}" y="{top - rh - rng.uniform(30, 80):.1f}" width="4" height="{rh + 80:.1f}" fill="{color}"/>')
        if win:
            ww, wh = win_size
            cols = max(1, int((w - 16) // (ww + 10)))
            rows = int((base_y - ytop_for_windows - 20) // (wh + 12))
            ox = x + (w - cols * (ww + 10) + 10) / 2
            for r in range(rows):
                for c in range(cols):
                    if rng.random() < lit:
                        out.append(f'<rect x="{ox + c * (ww + 10):.1f}" y="{ytop_for_windows + 16 + r * (wh + 12):.1f}" '
                                   f'width="{ww}" height="{wh}" fill="{win}" opacity="{rng.uniform(0.55, 1):.2f}"/>')
        x += w + rng.uniform(*gap)
    return "".join(out)


def cuboid(x, y, w, h, d, front, side=None, top=None, stroke=INK, sw=8, ang=-35, extra_front="", rx=0):
    """Box with oblique depth toward upper-right. (x,y)=top-left of the front face."""
    side = side or shade(front, 0.68)
    top = top or shade(front, 1.25)
    a = math.radians(ang)
    ox, oy = math.cos(a) * d, math.sin(a) * d
    tp = [(x, y), (x + ox, y + oy), (x + w + ox, y + oy), (x + w, y)]
    sp = [(x + w, y), (x + w + ox, y + oy), (x + w + ox, y + h + oy), (x + w, y + h)]
    out = [
        f'<polygon points="{pts(sp)}" fill="{side}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>',
        f'<polygon points="{pts(tp)}" fill="{top}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{front}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>',
        extra_front,
    ]
    return "".join(out)


def explosion(cx, cy, r, rng, gid_prefix, n=18, smoke=True, shards=14, chunks=10,
              colors=("#FFFFFF", "#FFF2A8", "#FFD21F", "#FF7A1A", "#E2381A"), outline=INK, sw=10,
              shard_fill=None, glow=True, squash=1.0):
    """Layered cartoon explosion with smoke, shards and concrete chunks."""
    g = gid_prefix
    defs = rad_grad(f"{g}_core", [(0, colors[0]), (0.35, colors[1]), (0.7, colors[2]), (1, colors[3])])
    defs += rad_grad(f"{g}_outer", [(0, colors[2]), (0.6, colors[3]), (1, colors[4])])
    defs += rad_grad(f"{g}_glow", [(0, colors[2], 0.9), (0.4, colors[3], 0.55), (1, colors[4], 0)])
    out = []
    if glow:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 2.0}" fill="url(#{g}_glow)"/>')
    if smoke:
        for i in range(14):
            a = rng.uniform(0, math.tau)
            rr = r * rng.uniform(0.75, 1.05)
            pr = r * rng.uniform(0.28, 0.45)
            sx, sy = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8 * squash
            c = rng.choice(["#2A2730", "#35303A", "#221F27", "#3D3640"])
            out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{pr:.1f}" fill="{c}" stroke="{outline}" stroke-width="{sw*0.6:.1f}"/>')
    p1 = burst_points(cx, cy, n, r, r * squash, rng, inner=(0.62, 0.74), outer=(0.88, 1.06))
    p2 = burst_points(cx, cy, n - 3, r * 0.74, r * 0.74 * squash, rng, inner=(0.6, 0.72), outer=(0.88, 1.0))
    p3 = burst_points(cx, cy, n - 6, r * 0.45, r * 0.45 * squash, rng, inner=(0.62, 0.75), outer=(0.9, 1.0))
    out.append(f'<polygon points="{pts(p1)}" fill="url(#{g}_outer)" stroke="{outline}" stroke-width="{sw}" stroke-linejoin="round"/>')
    out.append(f'<polygon points="{pts(p2)}" fill="url(#{g}_core)"/>')
    out.append(f'<polygon points="{pts(p3)}" fill="{colors[0]}" opacity="0.95"/>')

    for i in range(chunks):
        a = rng.uniform(0, math.tau)
        rr = r * rng.uniform(0.9, 1.6)
        sx, sy = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.85
        s = r * rng.uniform(0.05, 0.11)
        c = rng.choice(["#3A3D47", "#5A5F6C", "#2B2E36", "#6E6A66"])
        out.append(f'<polygon points="{pts(quad_chunk(sx, sy, s, rng))}" fill="{c}" stroke="{outline}" stroke-width="{sw*0.6:.1f}" stroke-linejoin="round"/>')
    for i in range(shards):
        a = rng.uniform(0, math.tau)
        rr = r * rng.uniform(0.95, 1.55)
        sx, sy = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.85
        s = r * rng.uniform(0.035, 0.07)
        c = shard_fill or rng.choice([colors[2], colors[3], "#FFFFFF"])
        out.append(f'<polygon points="{pts(shard_points(sx, sy, s, a, rng))}" fill="{c}" stroke="{outline}" stroke-width="{sw*0.45:.1f}" stroke-linejoin="round"/>')
    return defs, "".join(out)


def avatar(x, y, u, rng=None, pose="idle", shirt="#FF7A1A", pants="#2B3550", skin="#F5C935",
           hat=True, tool=None, face="grin", arm_l=0.0, arm_r=0.0, leg_l=0.0, leg_r=0.0, sw=None,
           tool_svg_r="", tool_svg_l="", vest=True):
    """Blocky Roblox-style avatar. (x,y)= top-left of the torso front face. u = unit (torso is 4u x 4u).

    arm_l / arm_r: rotation in degrees around the shoulder (negative raises the right arm outward).
    tool_svg_r: svg drawn inside the right-arm group in arm-local coords (hand at (u, 4u)).
    """
    sw = sw or max(4, u * 0.13)
    d = u * 0.9
    out = []
    a = math.radians(-35)
    ox, oy = math.cos(a) * d, math.sin(a) * d

    def arm(xa, rot, tool_svg, color):

        px, py = xa + u, y + u * 0.5
        sleeve = cuboid(xa, y, 2 * u, 1.6 * u, d, color, sw=sw)
        hand = cuboid(xa, y + 1.6 * u, 2 * u, 2.4 * u, d, skin, sw=sw)
        cuff = f'<rect x="{xa + sw/2:.1f}" y="{y + 1.45*u:.1f}" width="{2*u - sw:.1f}" height="{0.3*u:.1f}" fill="{shade(color, 0.75)}"/>'
        return (f'<g transform="rotate({rot:.1f} {px:.1f} {py:.1f})">{hand}{sleeve}{cuff}'
                f'<g transform="translate({xa:.1f} {y:.1f})">{tool_svg}</g></g>')

    def leg(xl, rot, color):
        px, py = xl + u, y + 4 * u
        return (f'<g transform="rotate({rot:.1f} {px:.1f} {py:.1f})">'
                f'{cuboid(xl, y + 4 * u, 2 * u, 4 * u, d, color, sw=sw)}'
                f'{cuboid(xl, y + 7.2 * u, 2 * u, 0.8 * u, d, "#1B1C22", sw=sw)}</g>')


    out.append(arm(x - 2 * u, arm_l, tool_svg_l, shirt))
    out.append(leg(x, leg_l, pants))
    out.append(leg(x + 2 * u, leg_r, pants))
    torso_extra = ""
    if vest:

        torso_extra += (f'<rect x="{x + 0.35*u:.1f}" y="{y + 2.2*u:.1f}" width="{3.3*u:.1f}" height="{0.42*u:.1f}" fill="#F5F5F7" opacity="0.9"/>'
                        f'<rect x="{x:.1f}" y="{y + 3.45*u:.1f}" width="{4*u:.1f}" height="{0.55*u:.1f}" fill="#1E2029"/>'
                        f'<rect x="{x + 1.65*u:.1f}" y="{y + 3.45*u:.1f}" width="{0.7*u:.1f}" height="{0.55*u:.1f}" fill="#FFD21F" stroke="{INK}" stroke-width="{sw*0.5:.1f}"/>')
    torso_extra += f'<rect x="{x + sw:.1f}" y="{y + sw:.1f}" width="{0.5*u:.1f}" height="{3.2*u:.1f}" fill="#FFFFFF" opacity="0.18"/>'
    out.append(cuboid(x, y, 4 * u, 4 * u, d, shirt, sw=sw, extra_front=torso_extra))

    hx, hy, hw, hh = x + 0.8 * u, y - 2.25 * u, 2.4 * u, 2.25 * u
    out.append(cuboid(hx + 0.35 * u, hy + 1.6 * u, 1.7 * u, 0.7 * u, d * 0.6, skin, sw=sw))
    out.append(cuboid(hx, hy, hw, hh, d * 0.9, skin, sw=sw, rx=u * 0.35))

    ex = hx + hw * 0.3
    ex2 = hx + hw * 0.7
    ey = hy + hh * 0.42
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{u*0.17:.1f}" ry="{u*0.27:.1f}" fill="{INK}"/>'
               f'<ellipse cx="{ex2:.1f}" cy="{ey:.1f}" rx="{u*0.17:.1f}" ry="{u*0.27:.1f}" fill="{INK}"/>'
               f'<circle cx="{ex + u*0.05:.1f}" cy="{ey - u*0.1:.1f}" r="{u*0.06:.1f}" fill="#fff"/>'
               f'<circle cx="{ex2 + u*0.05:.1f}" cy="{ey - u*0.1:.1f}" r="{u*0.06:.1f}" fill="#fff"/>')

    out.append(f'<path d="M{ex - u*0.28:.1f},{ey - u*0.48:.1f} L{ex + u*0.22:.1f},{ey - u*0.32:.1f}" stroke="{INK}" stroke-width="{u*0.13:.1f}" stroke-linecap="round"/>'
               f'<path d="M{ex2 + u*0.28:.1f},{ey - u*0.48:.1f} L{ex2 - u*0.22:.1f},{ey - u*0.32:.1f}" stroke="{INK}" stroke-width="{u*0.13:.1f}" stroke-linecap="round"/>')
    my = hy + hh * 0.7
    if face == "grin":
        out.append(f'<path d="M{hx + hw*0.26:.1f},{my:.1f} Q{hx + hw*0.5:.1f},{my + u*0.75:.1f} {hx + hw*0.74:.1f},{my:.1f} Z" '
                   f'fill="{INK}" stroke="{INK}" stroke-width="{u*0.06:.1f}" stroke-linejoin="round"/>'
                   f'<path d="M{hx + hw*0.31:.1f},{my + u*0.05:.1f} L{hx + hw*0.69:.1f},{my + u*0.05:.1f} L{hx + hw*0.66:.1f},{my + u*0.18:.1f} L{hx + hw*0.34:.1f},{my + u*0.18:.1f} Z" fill="#fff"/>')
    elif face == "shout":
        out.append(f'<ellipse cx="{hx + hw*0.5:.1f}" cy="{my + u*0.12:.1f}" rx="{u*0.3:.1f}" ry="{u*0.3:.1f}" fill="{INK}"/>')
    else:
        out.append(f'<path d="M{hx + hw*0.3:.1f},{my:.1f} Q{hx + hw*0.5:.1f},{my + u*0.4:.1f} {hx + hw*0.7:.1f},{my:.1f}" fill="none" stroke="{INK}" stroke-width="{u*0.12:.1f}" stroke-linecap="round"/>')

    out.append(f'<rect x="{hx + u*0.18:.1f}" y="{hy + u*0.18:.1f}" width="{u*0.28:.1f}" height="{hh*0.55:.1f}" rx="{u*0.12:.1f}" fill="#fff" opacity="0.35"/>')
    if hat:

        bx, by = hx - 0.35 * u, hy + 0.15 * u
        out.append(f'<path d="M{bx:.1f},{by + 0.1*u:.1f} L{bx + hw + 0.7*u + ox*0.9:.1f},{by + 0.1*u + oy*0.9:.1f} L{bx + hw + 0.95*u + ox*0.9:.1f},{by + 0.42*u + oy*0.9:.1f} L{bx - 0.15*u:.1f},{by + 0.42*u:.1f} Z" '
                   f'fill="#E0A800" stroke="{INK}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>')
        dome = (f'M{hx - 0.1*u:.1f},{by + 0.15*u:.1f} C{hx - 0.1*u:.1f},{hy - 1.2*u:.1f} {hx + hw + 0.1*u + ox*0.9:.1f},{hy - 1.25*u + oy*0.5:.1f} '
                f'{hx + hw + 0.1*u + ox*0.9:.1f},{by + 0.15*u + oy*0.9:.1f} Z')
        out.append(f'<path d="{dome}" fill="#FFD21F" stroke="{INK}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>')
        out.append(f'<path d="M{hx + hw*0.45:.1f},{hy - 0.75*u:.1f} L{hx + hw*0.45 + ox*0.3:.1f},{by + 0.1*u:.1f}" stroke="#E0A800" stroke-width="{u*0.35:.1f}"/>'
                   f'<path d="M{hx + 0.25*u:.1f},{hy - 0.35*u:.1f} Q{hx + 0.6*u:.1f},{hy - 0.8*u:.1f} {hx + 1.2*u:.1f},{hy - 0.85*u:.1f}" stroke="#FFF6C8" stroke-width="{u*0.16:.1f}" fill="none" stroke-linecap="round"/>')
    out.append(arm(x + 4 * u, arm_r, tool_svg_r, shirt))
    return "".join(out)


def sledgehammer(u, length=7.5, head_w=3.6, head_h=2.0, sw=None, angle=0.0, hand=(1.0, 4.0)):
    """Sledgehammer in arm-local coords. The grip sits at `hand` (in units); the
    handle points along `angle` degrees (0 = straight up from the hand)."""
    sw = sw or max(4, u * 0.13)
    hx, hy = hand[0] * u, hand[1] * u
    L = length * u
    hwid = 0.55 * u
    g = []
    g.append(f'<g transform="rotate({angle:.1f} {hx:.1f} {hy:.1f})">')

    g.append(f'<rect x="{hx - hwid/2:.1f}" y="{hy - L:.1f}" width="{hwid:.1f}" height="{L + 0.8*u:.1f}" rx="{hwid*0.3:.1f}" fill="#3B2A1E" stroke="{INK}" stroke-width="{sw:.1f}"/>')
    g.append(f'<rect x="{hx - hwid/2 + sw*0.4:.1f}" y="{hy - L:.1f}" width="{hwid*0.28:.1f}" height="{L:.1f}" fill="#7A5A3E"/>')

    for i in range(4):
        g.append(f'<rect x="{hx - hwid/2:.1f}" y="{hy - 0.9*u + i*0.42*u:.1f}" width="{hwid:.1f}" height="{0.26*u:.1f}" fill="#FF7A1A" stroke="{INK}" stroke-width="{sw*0.5:.1f}"/>')

    W, H = head_w * u, head_h * u
    x0, y0 = hx - W / 2, hy - L - H * 0.75
    g.append(cuboid(x0, y0, W, H, 0.9 * u, "#8D94A3", side="#5C6270", top="#C9CED8", sw=sw))
    g.append(f'<rect x="{x0 + W*0.36:.1f}" y="{y0:.1f}" width="{W*0.28:.1f}" height="{H:.1f}" fill="#FF7A1A" stroke="{INK}" stroke-width="{sw*0.7:.1f}"/>')
    g.append(f'<rect x="{x0 + sw*0.6:.1f}" y="{y0 + sw*0.6:.1f}" width="{W*0.3:.1f}" height="{H*0.22:.1f}" fill="#FFFFFF" opacity="0.55"/>')
    g.append("</g>")
    return "".join(g)


def headline(lines, x, y, gid, skew=-10, outline=26, ring=None, extrude=(10, 16), extrude_color="#1A0F08",
             shadow=True, anchor="start"):
    """lines: list of dicts {text, size, fill (gradient stops), dy (baseline offset from previous), dx, ls}
    Returns (defs, svg). (x,y) = baseline of the first line."""
    defs = []
    body = []
    if shadow:
        defs.append(f'<filter id="{gid}_sh" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>')
    by = y
    for i, ln in enumerate(lines):
        size = ln["size"]
        by = by + ln.get("dy", 0) if i else y
        lx = x + ln.get("dx", 0)
        ls = ln.get("ls", 0)
        tw = text_width(ln["text"], size, ls)
        if anchor == "middle":
            lx -= tw / 2
        cap = CAP * size
        stops = ln.get("fill", [(0, "#FFFFFF"), (0.55, "#FFF3B0"), (0.56, "#FFD21F"), (1, "#FF9A1F")])
        defs.append(lin_grad(f"{gid}_f{i}", stops, user=(0, by - cap, 0, by)))
        ow = ln.get("outline", outline)
        rg = ln.get("ring", ring)
        t = (f'<text x="{lx:.1f}" y="{by:.1f}" font-family="{FONT}" font-size="{size}" letter-spacing="{ls}" '
             f'stroke-linejoin="round" paint-order="stroke"')
        cy = by - cap / 2
        grp = [f'<g transform="translate(0 {cy:.1f}) skewX({skew}) translate(0 {-cy:.1f})">']
        if shadow:
            grp.append(f'{t} fill="#000" stroke="#000" stroke-width="{ow*2+6}" opacity="0.7" filter="url(#{gid}_sh)" transform="translate(14 26)">{ln["text"]}</text>')
        ex, ey = extrude
        steps = 8
        for k in range(steps, 0, -1):
            col = "#000000" if k == steps else ln.get("extrude_color", extrude_color)
            grp.append(f'{t} fill="{col}" stroke="{col}" stroke-width="{ow*2}" transform="translate({ex*k/steps:.1f} {ey*k/steps:.1f})">{ln["text"]}</text>')
        grp.append(f'{t} fill="{INK}" stroke="{INK}" stroke-width="{ow*2}">{ln["text"]}</text>')
        if rg:
            grp.append(f'{t} fill="{rg}" stroke="{rg}" stroke-width="{ow*0.95:.1f}">{ln["text"]}</text>')
            grp.append(f'{t} fill="{INK}" stroke="{INK}" stroke-width="{ow*0.35:.1f}">{ln["text"]}</text>')
        grp.append(f'{t} fill="url(#{gid}_f{i})">{ln["text"]}</text>')

        defs.append(f'<clipPath id="{gid}_c{i}"><text x="{lx:.1f}" y="{by:.1f}" font-family="{FONT}" font-size="{size}" letter-spacing="{ls}">{ln["text"]}</text></clipPath>')
        grp.append(f'<rect x="{lx - 50:.1f}" y="{by - cap - 10:.1f}" width="{tw + 100:.1f}" height="{cap*0.16:.1f}" fill="#FFFFFF" opacity="0.45" clip-path="url(#{gid}_c{i})"/>')
        grp.append("</g>")
        body.append("".join(grp))
    return "".join(defs), "".join(body)
