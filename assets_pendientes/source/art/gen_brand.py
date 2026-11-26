from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from wr_lib import (BRAND, BUILD, avatar, headline, sledgehammer, CAP, FONT, INK, PAL, SRC, THUMBS, ASSETS, blur_filter, burst_points,
                    char_advances, cuboid, explosion, hazard_pattern, jag_line, lin_grad, pts, quad_chunk,
                    rad_grad, render_many, render_svg, shade, shard_points, skyline, text_width)

SKEW = -10
TAN = math.tan(math.radians(SKEW))


def svg_doc(w, h, defs, body, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" {extra}>'
            f'<defs>{defs}</defs>{body}</svg>')


def skew_group(cy, inner, skew=SKEW):
    return f'<g transform="translate(0 {cy:.1f}) skewX({skew}) translate(0 {-cy:.1f})">{inner}</g>'


def glyph_xs(text, size, x0, ls):
    xs, x = [], x0
    for a in char_advances(text, size):
        xs.append(x)
        x += a + ls
    return xs, x - ls - x0


def taper_poly(points, wmax, rng, w_end=0.0, wobble=0.25, start_w=None):
    n = len(points)
    left, right = [], []
    for i, (x, y) in enumerate(points):
        a = points[max(0, i - 1)]
        b = points[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = i / (n - 1)
        if start_w is not None:
            wv = start_w * (1 - t) + w_end * t
        else:
            wv = w_end + (wmax - w_end) * math.sin(math.pi * t) ** 0.6
        wv *= rng.uniform(1 - wobble, 1 + wobble)
        left.append((x + nx * wv / 2, y + ny * wv / 2))
        right.append((x - nx * wv / 2, y - ny * wv / 2))
    return left + right[::-1]


def crack_set(rng, main_pts, segs, amp, wmax, branches):
    line = []
    for i in range(len(main_pts) - 1):
        seg = jag_line(main_pts[i], main_pts[i + 1], segs, amp, rng)
        line += seg if i == 0 else seg[1:]
    polys = [taper_poly(line, wmax, rng)]
    for t, ang, length, w in branches:
        k = max(1, min(len(line) - 2, int(t * (len(line) - 1))))
        sx, sy = line[k]
        a = math.radians(ang)
        ex, ey = sx + math.cos(a) * length, sy + math.sin(a) * length
        bl = jag_line((sx, sy), (ex, ey), 4, length * 0.12, rng)
        polys.append(taper_poly(bl, w, rng, start_w=w, wobble=0.15))
    return polys


def star4(cx, cy, r, rot=0.0, k=0.28):
    out = []
    for i in range(8):
        a = rot + math.pi * i / 4
        rr = r if i % 2 == 0 else r * k
        out.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return out


def speed_line(x_tip, y, length, thick, direction=-1):
    x2 = x_tip + direction * length
    return [(x_tip, y - thick / 2), (x_tip + direction * thick * 0.2, y), (x_tip, y + thick / 2), (x2, y + thick * 0.08), (x2, y - thick * 0.08)]


def brushed_filter(fid, seed=3, fx=0.004, fy=0.55, alpha=0.5, color=(1, 1, 1)):
    r, g, b = color
    return (f'<filter id="{fid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{fx} {fy}" numOctaves="2" seed="{seed}"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 {r}  0 0 0 0 {g}  0 0 0 0 {b}  {alpha*2.2:.2f} 0 0 0 {-alpha*0.9:.2f}"/></filter>')


def grain_filter(fid, seed=9, freq=0.9, alpha=0.08):
    return (f'<filter id="{fid}" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="1" seed="{seed}"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  {alpha*4:.2f} 0 0 0 {-alpha*1.6:.2f}"/></filter>')


CHROME = [(0.00, "#FFFFFF"), (0.16, "#F1F3F7"), (0.38, "#BCC3CF"), (0.485, "#8C94A3"), (0.50, "#3A404C"),
          (0.58, "#4A515F"), (0.76, "#8D94A2"), (0.90, "#E9B98E"), (1.00, "#FFE2BC")]
FIRE = [(0.0, "#FFF6C2"), (0.30, "#FFD21F"), (0.62, "#FF7A1A"), (1.0, "#D8321A")]


LW, LH = 2048, 1024
WS = 540
WLS = -6
WB = 560
WOW = 22
RS = 205
RLS = 34


def logo_geometry(seed=11):
    rng = random.Random(seed)
    xs, tw = glyph_xs("WRECK", WS, 0, WLS)
    x0 = (LW - tw) / 2 - 10
    xs = [x + x0 for x in xs]
    cap = CAP * WS
    top = WB - cap
    cy = WB - cap / 2
    g = dict(xs=xs, x0=x0, x1=x0 + tw, top=top, cy=cy, cap=cap)
    adv = char_advances("WRECK", WS)
    W0, R0, E0, C0, K0 = xs
    cracks = []
    cracks += crack_set(rng, [(W0 + 60, top - 40), (W0 + 250, top + 170), (R0 + 120, top + 260), (E0 + 140, WB + 40)],
                        4, 20, 22, [(0.22, 160, 110, 12), (0.5, -30, 120, 11), (0.72, 40, 130, 12), (0.86, 130, 90, 9)])
    cracks += crack_set(rng, [(C0 + 150, top - 40), (C0 + 120, top + 200), (C0 + 200, WB + 40)],
                        5, 16, 18, [(0.35, -20, 160, 11), (0.62, 200, 90, 9)])
    cracks += crack_set(rng, [(K0 - 10, WB - 120), (K0 + 150, WB - 40), (K0 + 260, WB + 40)],
                        3, 10, 13, [])
    g["cracks"] = cracks
    frK = [(K0 + 110, top - 60), (K0 + adv[4] + 60, top - 60), (K0 + adv[4] + 60, top + 150)]
    frK += jag_line((K0 + adv[4] + 60, top + 150), (K0 + 160, top + 95), 5, 14, rng)[1:-1]
    frK += [(K0 + 160, top + 95), (K0 + 175, top + 40), (K0 + 120, top + 10)]
    frW = [(W0 - 70, WB - 120)]
    frW += jag_line((W0 - 70, WB - 120), (W0 + 150, WB - 10), 4, 16, rng)[1:-1]
    frW += [(W0 + 150, WB - 10), (W0 + 160, WB + 80), (W0 - 70, WB + 80)]
    frE = [(E0 + 120, top - 50), (E0 + adv[2] + 40, top - 50), (E0 + adv[2] + 40, top + 70)]
    frE += jag_line((E0 + adv[2] + 40, top + 70), (E0 + 150, top + 85), 3, 12, rng)[1:-1]
    frE += [(E0 + 150, top + 85)]
    g["frags"] = [(frK, 70, -96, 13), (frW, -60, 70, -11), (frE, 26, -64, 7)]
    return g


def wtext(g, attrs):
    xs = " ".join(f"{x:.1f}" for x in g["xs"])
    return f'<text x="{xs}" y="{WB}" font-family="{FONT}" font-size="{WS}" {attrs}>WRECK</text>'


def logo_svg(mode="color", seed=11):
    rng = random.Random(seed + 100)
    g = logo_geometry(seed)
    mono = mode != "color"
    mc = "#FFFFFF" if mode == "white" else "#000000"
    defs, body = [], []
    cy = g["cy"]
    bcx, bcy = LW / 2, 420
    full = 'maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="-600" y="-600" width="3400" height="2400"'

    rcap = CAP * RS
    p_top, p_bot = WB + 8, WB + 8 + rcap + 66
    rxs, rtw = glyph_xs("RUSH", RS, 0, RLS)
    p_w = rtw + 520
    p_x0 = LW / 2 - p_w / 2 + 8
    p_cy = (p_top + p_bot) / 2
    rx0 = LW / 2 - rtw / 2 + 8
    rxs = [x + rx0 for x in rxs]
    r_base = p_bot - (p_bot - p_top - rcap) / 2 + 2
    rt = lambda attrs: (f'<text x="{" ".join(f"{x:.1f}" for x in rxs)}" y="{r_base:.1f}" font-family="{FONT}" '
                        f'font-size="{RS}" {attrs}>RUSH</text>')
    plate = f'<rect x="{p_x0:.1f}" y="{p_top:.1f}" width="{p_w:.1f}" height="{p_bot - p_top:.1f}"'

    sl = []
    srng = random.Random(seed + 7)
    for i in range(16):
        y = srng.uniform(g["top"] + 10, p_bot - 10)
        x_tip = srng.uniform(g["x0"] + 40, g["x0"] + 260)
        length = srng.uniform(260, 620)
        th = srng.uniform(10, 26)
        col = srng.choice(["#FFFFFF", "#FFD21F", "#FF7A1A", "#FF7A1A"])
        sl.append((speed_line(x_tip, y, length, th), col))
    for i in range(7):
        y = srng.uniform(g["top"] + 60, p_bot - 40)
        x_tip = srng.uniform(g["x1"] - 160, g["x1"] - 40)
        length = srng.uniform(160, 330)
        th = srng.uniform(8, 18)
        col = srng.choice(["#FFFFFF", "#FFD21F", "#FF7A1A"])
        sl.append((speed_line(x_tip, y, length, th, direction=1), col))

    b_rx, b_ry = 930, 400
    brng = random.Random(seed + 3)
    pb1 = burst_points(bcx, bcy, 19, b_rx, b_ry, brng, inner=(0.70, 0.80), outer=(0.90, 1.0), jitter=0.35, rot=0.12)
    pb2 = burst_points(bcx, bcy, 17, b_rx * 0.86, b_ry * 0.80, brng, inner=(0.70, 0.80), outer=(0.88, 1.0), jitter=0.35, rot=0.3)
    pb3 = burst_points(bcx, bcy, 15, b_rx * 0.70, b_ry * 0.62, brng, inner=(0.72, 0.82), outer=(0.9, 1.0), jitter=0.3, rot=0.5)

    shards = []
    xs = g["xs"]
    shard_srcs = [(xs[4] + 260, g["top"] + 10, -0.6, 9), (xs[0] - 10, WB - 40, 2.6, 7), (xs[2] + 230, g["top"] - 10, -1.2, 6),
                  (xs[1] + 120, g["top"] + 40, -1.9, 4), (xs[3] + 220, WB + 10, 0.9, 4)]
    for sx, sy, base_a, cnt in shard_srcs:
        for j in range(cnt):
            a = base_a + rng.uniform(-0.75, 0.75)
            d = rng.uniform(60, 260)
            px, py = sx + math.cos(a) * d, sy + math.sin(a) * d * 0.8
            s = rng.uniform(9, 24)
            shards.append((shard_points(px, py, s, a, rng, stretch=1.9), a))
    sparks = [(rng.uniform(150, 1900), rng.uniform(40, 980), rng.uniform(10, 26)) for _ in range(26)]
    sparks = [(x, y, r) for x, y, r in sparks if not (g["x0"] - 20 < x < g["x1"] + 20 and g["top"] - 30 < y < p_bot + 30)]

    if not mono:
        defs.append(rad_grad("lg_glow", [(0, "#FF9A2A", 0.55), (0.45, "#FF6A1A", 0.22), (1, "#FF4A1A", 0)], user=(bcx, bcy, 1000)))
        defs.append(rad_grad("lg_b1", [(0, "#FF8A1F"), (0.7, "#F2531A"), (1, "#B8201A")], user=(bcx, bcy, b_rx)))
        defs.append(rad_grad("lg_b2", [(0, "#FFE15A"), (0.6, "#FFB21F"), (1, "#FF8A1A")], user=(bcx, bcy, b_rx * 0.86)))
        defs.append(rad_grad("lg_b3", [(0, "#FFFFFF"), (0.45, "#FFF7C8"), (1, "#FFE15A")], user=(bcx, bcy, b_rx * 0.7)))
        defs.append(f'<pattern id="lg_dots" width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
                    f'<circle cx="13" cy="13" r="5.5" fill="#B8201A"/></pattern>')
        defs.append(f'<mask id="lg_dotmask" {full}><polygon points="{pts(pb1)}" fill="white"/>'
                    f'<polygon points="{pts(pb2)}" fill="black"/></mask>')
        defs.append(lin_grad("lg_chrome", CHROME, user=(0, g["top"], 0, WB)))
        defs.append(lin_grad("lg_bevel", [(0, "#FFFFFF"), (0.45, "#E6EAF0"), (0.55, "#262A33"), (1, "#5B4030")], user=(0, g["top"], 0, WB)))
        defs.append(lin_grad("lg_fire", FIRE[::-1], user=(0, g["top"], 0, WB)))
        defs.append(lin_grad("lg_rush", [(0, "#FFF0A0"), (0.32, "#FFC21F"), (0.62, "#FF7A1A"), (1, "#E0401A")],
                             user=(0, r_base - rcap, 0, r_base)))
        defs.append(lin_grad("lg_plate", [(0, "#2A2D38"), (0.5, "#16171D"), (1, "#0A0A0D")], user=(0, p_top, 0, p_bot)))
        defs.append(lin_grad("lg_shard", [(0, "#FFFFFF"), (0.5, "#B9C0CC"), (0.52, "#59606E"), (1, "#C9CED8")]))
        defs.append(hazard_pattern("lg_haz", 46, PAL["yellow"], PAL["black"], angle=SKEW - 35))
        defs.append(brushed_filter("lg_brush", seed=4, alpha=0.55))
        defs.append(brushed_filter("lg_brushd", seed=8, alpha=0.5, color=(0, 0, 0)))
        defs.append(blur_filter("lg_blur16", 16))
        defs.append(blur_filter("lg_blur8", 7))
        defs.append(blur_filter("lg_blur30", 30))
        defs.append(f'<mask id="lg_face" {full}>{wtext(g, "fill=\"white\"")}</mask>')
        defs.append(f'<mask id="lg_sil" {full}>{wtext(g, f"fill=\"white\" stroke=\"white\" stroke-width=\"{2*WOW}\" stroke-linejoin=\"round\"")}</mask>')
        defs.append(f'<mask id="lg_rface" {full}>{rt("fill=\"white\"")}</mask>')
        hole = "".join(f'<polygon points="{pts(p)}" fill="black"/>' for p, *_ in g["frags"])
        defs.append(f'<mask id="lg_body" {full}><rect x="-600" y="-600" width="3400" height="2400" fill="white"/>{hole}</mask>')
        for i, (p, *_r) in enumerate(g["frags"]):
            defs.append(f'<mask id="lg_fr{i}" {full}><polygon points="{pts(p)}" fill="white"/></mask>')

        ex, ey, steps = 16, 26, 12
        st = []
        st.append(wtext(g, f'fill="#000" stroke="#000" stroke-width="{2*WOW+8}" stroke-linejoin="round" opacity="0.55" '
                           f'filter="url(#lg_blur16)" transform="translate(26 40)"'))
        for k in range(steps, 0, -1):
            st.append(wtext(g, f'fill="{INK}" stroke="{INK}" stroke-width="{2*WOW}" stroke-linejoin="round" '
                               f'transform="translate({ex*k/steps:.1f} {ey*k/steps:.1f})"'))
        for k in range(steps - 1, 0, -1):
            c = shade("#3B414D", 0.65 + 0.35 * (1 - k / steps))
            st.append(wtext(g, f'fill="{c}" stroke="{c}" stroke-width="{2*WOW-14}" stroke-linejoin="round" '
                               f'transform="translate({ex*k/steps:.1f} {ey*k/steps:.1f})"'))
        st.append(wtext(g, f'fill="{INK}" stroke="{INK}" stroke-width="{2*WOW}" stroke-linejoin="round"'))
        st.append(wtext(g, f'fill="none" stroke="#FF7A1A" stroke-width="{WOW*0.62:.1f}" stroke-linejoin="round" opacity="0.95"'))
        st.append(wtext(g, f'fill="none" stroke="{INK}" stroke-width="{WOW*0.2:.1f}" stroke-linejoin="round"'))
        st.append(wtext(g, 'fill="url(#lg_chrome)"'))
        face = []
        face.append(wtext(g, 'fill="none" stroke="url(#lg_bevel)" stroke-width="14" stroke-linejoin="round"'))
        face.append(f'<rect x="0" y="0" width="{LW}" height="{LH}" filter="url(#lg_brush)" opacity="0.55"/>')
        face.append(f'<rect x="0" y="0" width="{LW}" height="{LH}" filter="url(#lg_brushd)" opacity="0.45"/>')
        for _ in range(60):
            sx = rng.uniform(g["x0"], g["x1"])
            sy = rng.uniform(g["top"], WB)
            a = rng.uniform(-0.5, 0.5) + (math.pi * 0.25 if rng.random() < 0.5 else 0)
            L = rng.uniform(20, 90)
            col = "#FFFFFF" if rng.random() < 0.55 else "#20232A"
            face.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{sx + math.cos(a)*L:.1f}" y2="{sy + math.sin(a)*L:.1f}" '
                        f'stroke="{col}" stroke-width="{rng.uniform(1.5, 3.2):.1f}" opacity="{rng.uniform(0.35, 0.7):.2f}" stroke-linecap="round"/>')
        face.append(f'<rect x="{g["x0"] - 100:.1f}" y="{g["top"] + 18:.1f}" width="{g["x1"] - g["x0"] + 200:.1f}" height="16" fill="#FFFFFF" opacity="0.65"/>')
        for (rx_, ry_) in [(xs[0] + 66, g["top"] + 44), (xs[0] + 374, g["top"] + 44), (xs[1] + 60, WB - 40),
                           (xs[2] + 60, WB - 40), (xs[4] + 60, g["top"] + 44), (xs[3] + 60, g["top"] + 200)]:
            face.append(f'<circle cx="{rx_:.1f}" cy="{ry_:.1f}" r="11" fill="#5B6270" stroke="{INK}" stroke-width="4"/>'
                        f'<circle cx="{rx_ - 3:.1f}" cy="{ry_ - 3:.1f}" r="4" fill="#FFFFFF" opacity="0.9"/>')
        cr_glow = "".join(f'<polygon points="{pts(p)}" fill="#FF8A1F" stroke="#FF6A1A" stroke-width="26" stroke-linejoin="round"/>' for p in g["cracks"])
        face.append(f'<g filter="url(#lg_blur8)" opacity="0.85">{cr_glow}</g>')
        st.append(f'<g mask="url(#lg_face)">{"".join(face)}</g>')
        cr = "".join(f'<polygon points="{pts(p)}" fill="url(#lg_fire)" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>' for p in g["cracks"])
        cr_core = "".join(f'<polygon points="{pts(p)}" fill="#FFFBE6" transform="translate(0 0)" opacity="0.0"/>' for p in g["cracks"])
        st.append(f'<g mask="url(#lg_sil)">{cr}{cr_core}</g>')
        defs.append(f'<g id="lg_stack">{"".join(st)}</g>')

        body.append(f'<ellipse cx="{bcx}" cy="{bcy}" rx="1010" ry="520" fill="url(#lg_glow)"/>')
        for pnts, col in sl[::2]:
            body.append(f'<polygon points="{pts(pnts)}" fill="{col}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
        body.append(f'<polygon points="{pts(pb1)}" fill="#000" opacity="0.35" filter="url(#lg_blur16)" transform="translate(10 18)"/>')
        body.append(f'<polygon points="{pts(pb1)}" fill="url(#lg_b1)" stroke="{INK}" stroke-width="16" stroke-linejoin="round"/>')
        body.append(f'<rect x="0" y="0" width="{LW}" height="{LH}" fill="url(#lg_dots)" mask="url(#lg_dotmask)" opacity="0.55"/>')
        body.append(f'<polygon points="{pts(pb2)}" fill="url(#lg_b2)" stroke="#B8201A" stroke-width="6" stroke-linejoin="round"/>')
        body.append(f'<polygon points="{pts(pb3)}" fill="url(#lg_b3)"/>')
        drng = random.Random(seed + 21)
        for _ in range(16):
            a = drng.uniform(0, math.tau)
            px, py = bcx + math.cos(a) * b_rx * drng.uniform(0.9, 1.05), bcy + math.sin(a) * b_ry * drng.uniform(0.95, 1.15)
            if not (0 < py < LH - 20):
                continue
            s = drng.uniform(14, 30)
            c = drng.choice(["#3A3D47", "#5A5F6C", "#2B2E36"])
            body.append(f'<polygon points="{pts(quad_chunk(px, py, s, drng))}" fill="{c}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
        for pnts, col in sl[1::2]:
            body.append(f'<polygon points="{pts(pnts)}" fill="{col}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
        wr = [f'<g mask="url(#lg_body)"><use href="#lg_stack"/></g>']
        for i, (p, dx, dy, rot) in enumerate(g["frags"]):
            pcx = sum(q[0] for q in p) / len(p)
            pcy = sum(q[1] for q in p) / len(p)
            edge = f'<polygon points="{pts(p)}" fill="none" stroke="{INK}" stroke-width="12" stroke-linejoin="round" mask="url(#lg_sil)"/>'
            wr.append(edge)
            wr.append(f'<g transform="translate({dx} {dy}) rotate({rot} {pcx:.1f} {pcy:.1f})">'
                      f'<g mask="url(#lg_fr{i})"><use href="#lg_stack"/></g>{edge}</g>')
        body.append(skew_group(cy, "".join(wr)))
        pl = []
        pl.append(f'{plate} fill="#000" opacity="0.55" filter="url(#lg_blur16)" transform="translate(16 26)"/>')
        pl.append(f'{plate} fill="{INK}" stroke="{INK}" stroke-width="34" stroke-linejoin="round"/>')
        pl.append(f'{plate} fill="url(#lg_plate)" stroke="#FF7A1A" stroke-width="10" stroke-linejoin="round"/>')
        cap_w = 170
        for xa in (p_x0 + 14, p_x0 + p_w - cap_w - 14):
            pl.append(f'<rect x="{xa:.1f}" y="{p_top + 16:.1f}" width="{cap_w}" height="{p_bot - p_top - 32:.1f}" fill="url(#lg_haz)" stroke="{INK}" stroke-width="6"/>')
        pl.append(f'<rect x="{p_x0 + 8:.1f}" y="{p_top + 10:.1f}" width="{p_w - 16:.1f}" height="8" fill="#FFFFFF" opacity="0.12"/>')
        for k in range(8, 0, -1):
            pl.append(rt(f'fill="#000" stroke="#000" stroke-width="22" stroke-linejoin="round" transform="translate({k*1.2:.1f} {k*2.0:.1f})"'))
        for k in range(7, 0, -1):
            pl.append(rt(f'fill="#7A2A08" stroke="#7A2A08" stroke-width="10" stroke-linejoin="round" transform="translate({k*1.2:.1f} {k*2.0:.1f})"'))
        pl.append(rt(f'fill="{INK}" stroke="{INK}" stroke-width="22" stroke-linejoin="round"'))
        pl.append(rt('fill="url(#lg_rush)"'))
        pl.append(f'<g mask="url(#lg_rface)"><rect x="{p_x0:.1f}" y="{r_base - rcap + 10:.1f}" width="{p_w:.1f}" height="10" fill="#FFFFFF" opacity="0.6"/>'
                  f'<rect x="0" y="0" width="{LW}" height="{LH}" filter="url(#lg_brush)" opacity="0.25"/></g>')
        body.append(skew_group(p_cy, "".join(pl)))
        for p, a in shards:
            body.append(f'<polygon points="{pts(p)}" fill="url(#lg_shard)" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
        for x, y, r in sparks:
            body.append(f'<polygon points="{pts(star4(x, y, r, rot=0.2))}" fill="#FFE15A" stroke="#FF7A1A" stroke-width="3" stroke-linejoin="round"/>')
    else:
        defs.append(f'<mask id="lm_knock" {full}><rect x="-600" y="-600" width="3400" height="2400" fill="white"/>'
                    + skew_group(cy, wtext(g, f'fill="black" stroke="black" stroke-width="{2*WOW+48}" stroke-linejoin="round" transform="translate(8 13)"'))
                    + skew_group(p_cy, f'{plate} fill="black" stroke="black" stroke-width="70" stroke-linejoin="round"/>')
                    + '</mask>')
        ex, ey, steps = 16, 26, 10
        m = [f'<rect x="-600" y="-600" width="3400" height="2400" fill="black"/>']
        for k in range(steps, -1, -1):
            m.append(wtext(g, f'fill="white" stroke="white" stroke-width="{2*WOW}" stroke-linejoin="round" transform="translate({ex*k/steps:.1f} {ey*k/steps:.1f})"'))
        m.append(wtext(g, 'fill="black" stroke="black" stroke-width="16" stroke-linejoin="round"'))
        m.append(wtext(g, 'fill="white"'))
        crack_m = "".join(f'<polygon points="{pts(p)}" fill="black"/>' for p in g["cracks"])
        m.append(crack_m)
        defs.append(f'<mask id="lm_wfull" {full}>{"".join(m)}</mask>')
        hole = "".join(f'<polygon points="{pts(p)}" fill="black" stroke="black" stroke-width="10"/>' for p, *_ in g["frags"])
        defs.append(f'<mask id="lm_body" {full}><rect x="-600" y="-600" width="3400" height="2400" fill="white"/>{hole}</mask>')
        for i, (p, *_r) in enumerate(g["frags"]):
            defs.append(f'<mask id="lm_fr{i}" {full}><polygon points="{pts(p)}" fill="white" stroke="black" stroke-width="10"/></mask>')
        rm = (f'<rect x="-600" y="-600" width="3400" height="2400" fill="black"/>'
              f'{plate} fill="white" stroke="white" stroke-width="20" stroke-linejoin="round"/>'
              + rt('fill="black" stroke="black" stroke-width="18" stroke-linejoin="round"') + rt('fill="white"')
              + rt('fill="black"'))
        cap_w = 170
        for xa in (p_x0 + 14, p_x0 + p_w - cap_w - 14):
            for s in range(-3, 6):
                sx = xa + s * 46
                rm += (f'<polygon points="{pts([(sx, p_bot - 16), (sx + 23, p_bot - 16), (sx + 23 + (p_bot - p_top - 32) * 0.7, p_top + 16), (sx + (p_bot - p_top - 32) * 0.7, p_top + 16)])}" '
                       f'fill="black" clip-path="url(#lm_capclip{int(xa)})"/>')
            defs.append(f'<clipPath id="lm_capclip{int(xa)}"><rect x="{xa:.1f}" y="{p_top + 16:.1f}" width="{cap_w}" height="{p_bot - p_top - 32:.1f}"/></clipPath>')
        defs.append(f'<mask id="lm_plate" {full}>{rm}</mask>')
        bk = [f'<polygon points="{pts(pb1)}" fill="none" stroke="{mc}" stroke-width="18" stroke-linejoin="round"/>',
              f'<polygon points="{pts(pb3)}" fill="none" stroke="{mc}" stroke-width="10" stroke-linejoin="round" stroke-dasharray="40 26"/>']
        for pnts, col in sl:
            bk.append(f'<polygon points="{pts(pnts)}" fill="{mc}"/>')
        body.append(f'<g mask="url(#lm_knock)">{"".join(bk)}</g>')
        rect = f'<rect x="-600" y="-600" width="3400" height="2400" fill="{mc}" mask="url(#lm_wfull)"/>'
        wr = [f'<g mask="url(#lm_body)">{rect}</g>']
        for i, (p, dx, dy, rot) in enumerate(g["frags"]):
            pcx = sum(q[0] for q in p) / len(p)
            pcy = sum(q[1] for q in p) / len(p)
            wr.append(f'<g transform="translate({dx} {dy}) rotate({rot} {pcx:.1f} {pcy:.1f})"><g mask="url(#lm_fr{i})">{rect}</g></g>')
        body.append(skew_group(cy, "".join(wr)))
        body.append(skew_group(p_cy, f'<rect x="-600" y="-600" width="3400" height="2400" fill="{mc}" mask="url(#lm_plate)"/>'))
        for p, a in shards:
            body.append(f'<polygon points="{pts(p)}" fill="{mc}"/>')
        for x, y, r in sparks:
            body.append(f'<polygon points="{pts(star4(x, y, r, rot=0.2))}" fill="{mc}"/>')
    return svg_doc(LW, LH, "".join(defs), "".join(body))


TW, TH = 1920, 1080


def logo_embed(x, y, w, mode="color"):
    h = w * LH / LW
    return logo_svg(mode).replace(f'width="{LW}" height="{LH}"', f'x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"', 1)


def rays(cx, cy, n, r, fill, op, rot=0.0, width=0.5):
    out = []
    for i in range(n):
        a0 = rot + math.tau * i / n
        a1 = a0 + math.tau / n * width
        p = [(cx, cy), (cx + math.cos(a0) * r, cy + math.sin(a0) * r), (cx + math.cos(a1) * r, cy + math.sin(a1) * r)]
        out.append(f'<polygon points="{pts(p)}" fill="{fill}" opacity="{op}"/>')
    return "".join(out)


def vignette(gid, w, h, op=0.75):
    d = rad_grad(gid, [(0, "#000000", 0), (0.62, "#000000", 0), (1, "#000000", op)], user=(w / 2, h / 2, math.hypot(w, h) / 2))
    return d, f'<rect width="{w}" height="{h}" fill="url(#{gid})"/>'


def spark_field(rng, n, box, rmin, rmax, fill="#FFE15A", stroke="#FF7A1A", avoid=None):
    out = []
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        if avoid and avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]:
            continue
        out.append(f'<polygon points="{pts(star4(x, y, rng.uniform(rmin, rmax), rot=rng.uniform(0, 0.6)))}" fill="{fill}" stroke="{stroke}" stroke-width="3" stroke-linejoin="round"/>')
    return "".join(out)


def shard_ring(rng, cx, cy, n, rmin, rmax, smin, smax, fills, sw=5, squash=0.8):
    out = []
    for _ in range(n):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(rmin, rmax)
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d * squash
        out.append(f'<polygon points="{pts(shard_points(x, y, rng.uniform(smin, smax), a, rng, stretch=2.0))}" fill="{rng.choice(fills)}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    return "".join(out)


def chunk_field(rng, n, box, smin, smax, fills=("#3A3D47", "#5A5F6C", "#2B2E36", "#6E6A66"), sw=6):
    out = []
    x0, y0, x1, y1 = box
    for _ in range(n):
        out.append(f'<polygon points="{pts(quad_chunk(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(smin, smax), rng))}" fill="{rng.choice(fills)}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    return "".join(out)


def embers(rng, n, box, colors=("#FF7A1A", "#FFD21F", "#FF3B3B"), rmax=4.5):
    out = []
    x0, y0, x1, y1 = box
    for _ in range(n):
        out.append(f'<circle cx="{rng.uniform(x0, x1):.1f}" cy="{rng.uniform(y0, y1):.1f}" r="{rng.uniform(1.2, rmax):.1f}" fill="{rng.choice(colors)}" opacity="{rng.uniform(0.35, 0.95):.2f}"/>')
    return "".join(out)


def rubble_ground(rng, y, w, color="#121318", n=40, smin=18, smax=46):
    pnts = [(0, TH + 10), (0, y)]
    x = 0
    while x < w:
        x += rng.uniform(40, 110)
        pnts.append((x, y + rng.uniform(-28, 14)))
    pnts += [(w, TH + 10)]
    out = f'<polygon points="{pts(pnts)}" fill="{color}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
    return out + chunk_field(rng, n, (0, y - 10, w, y + 60), smin, smax)


def mark_svg(seed=5):
    S = 512
    rng = random.Random(seed)
    defs, body = [], []
    size = 360 / (text_width("WR", 1000, 0) / 1000)
    cap = CAP * size
    base = S / 2 + cap / 2 - 6
    cy = base - cap / 2
    defs.append(rad_grad("mk_b1", [(0, "#FF8A1F"), (0.7, "#F2531A"), (1, "#B8201A")], user=(256, 256, 240)))
    defs.append(rad_grad("mk_b2", [(0, "#FFFFFF"), (0.5, "#FFE15A"), (1, "#FFB21F")], user=(256, 256, 190)))
    defs.append(blur_filter("mk_bl", 8))
    pb1 = burst_points(256, 256, 13, 238, 222, rng, inner=(0.70, 0.80), outer=(0.92, 1.0), jitter=0.3, rot=0.1)
    pb2 = burst_points(256, 256, 11, 185, 170, rng, inner=(0.70, 0.80), outer=(0.9, 1.0), jitter=0.3, rot=0.35)
    body.append(f'<polygon points="{pts(pb1)}" fill="#000" opacity="0.45" filter="url(#mk_bl)" transform="translate(6 10)"/>')
    body.append(f'<polygon points="{pts(pb1)}" fill="url(#mk_b1)" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>')
    body.append(f'<polygon points="{pts(pb2)}" fill="url(#mk_b2)" stroke="#B8201A" stroke-width="4" stroke-linejoin="round"/>')
    hd, hb = headline([dict(text="WR", size=size, ls=-4, fill=CHROME)], S / 2 - 4, base, "mk", skew=SKEW, outline=18,
                      ring="#FF7A1A", extrude=(7, 12), shadow=False, anchor="middle")
    defs.append(hd)
    body.append(hb)
    tw = text_width("WR", size, -4)
    x0 = S / 2 - 4 - tw / 2
    cracks = crack_set(rng, [(x0 + tw * 0.62, base - cap - 20), (x0 + tw * 0.5, cy), (x0 + tw * 0.58, base + 20)], 4, 10, 12,
                       [(0.4, 200, 60, 7), (0.7, -20, 70, 7)])
    cr = "".join(f'<polygon points="{pts(p)}" fill="url(#lg_fire_mk)" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>' for p in cracks)
    defs.append(lin_grad("lg_fire_mk", FIRE[::-1], user=(0, base - cap, 0, base)))
    body.append(skew_group(cy, f'<g clip-path="url(#mk_c0)">{cr}</g>'))
    body.append(shard_ring(rng, 256, 256, 9, 205, 240, 8, 14, ["#FFFFFF", "#C9CED8", "#FFD21F"], sw=3, squash=0.95))
    for x, y, r in [(70, 120, 14), (440, 410, 12), (450, 110, 10), (80, 400, 9)]:
        body.append(f'<polygon points="{pts(star4(x, y, r, rot=0.2))}" fill="#FFE15A" stroke="#FF7A1A" stroke-width="3" stroke-linejoin="round"/>')
    return svg_doc(S, S, "".join(defs), "".join(body))


def car(x, y, s, body="#22E1FF", crush=0.0, gid="car"):
    dk = shade(body, 0.62)
    lt = shade(body, 1.35)
    sw = 9
    roof = [(108, -176 + crush * 28), (140, -176 + crush * 58), (168, -176 + crush * 72), (196, -176 + crush * 50), (236, -176 + crush * 18)]
    cab = [(66, -106)] + roof + [(276, -106)]
    glass = [(92, -112), (118, -166 + crush * 30), (158, -166 + crush * 64), (164, -112)]
    glass2 = [(178, -112), (180, -166 + crush * 56), (230, -166 + crush * 20), (252, -112)]
    bod = [(6, -36), (0, -70), (12, -106), (318, -110), (340, -82), (336, -36)]
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s})">']
    out.append(f'<ellipse cx="170" cy="4" rx="190" ry="20" fill="#000" opacity="0.5"/>')
    out.append(f'<polygon points="{pts(cab)}" fill="{dk}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    for gp in (glass, glass2):
        out.append(f'<polygon points="{pts(gp)}" fill="#BFF6FF" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    out.append(f'<path d="M118,-150 L140,-128 L132,-118 M150,-150 L138,-128 M196,-140 L214,-126 L206,-114" stroke="{INK}" stroke-width="4" fill="none"/>')
    out.append(f'<polygon points="{pts(bod)}" fill="{body}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    out.append(f'<rect x="14" y="-100" width="300" height="12" fill="{lt}" opacity="0.9"/>')
    out.append(f'<rect x="8" y="-74" width="328" height="16" fill="#FF7A1A" stroke="{INK}" stroke-width="4"/>')
    out.append(f'<line x1="170" y1="-104" x2="168" y2="-40" stroke="{INK}" stroke-width="5"/>')
    out.append(f'<rect x="318" y="-100" width="20" height="16" rx="3" fill="#FFF2A8" stroke="{INK}" stroke-width="4"/>')
    out.append(f'<rect x="2" y="-100" width="14" height="16" rx="3" fill="#FF3B3B" stroke="{INK}" stroke-width="4"/>')
    for wx in (74, 264):
        out.append(f'<circle cx="{wx}" cy="-34" r="38" fill="#16171D" stroke="{INK}" stroke-width="{sw}"/>'
                   f'<circle cx="{wx}" cy="-34" r="17" fill="#8D94A3" stroke="{INK}" stroke-width="4"/>'
                   f'<circle cx="{wx - 5}" cy="-39" r="5" fill="#FFFFFF" opacity="0.8"/>')
    out.append("</g>")
    return "".join(out)


def arc_streak(cx, cy, r, a0, a1, w, color, n=14):
    p = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        p.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    rng = random.Random(int(r))
    return f'<polygon points="{pts(taper_poly(p, w, rng, start_w=w, wobble=0.0))}" fill="{color}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'


def game_icon_svg(seed=8):
    S = 512
    rng = random.Random(seed)
    defs, body = [], []
    icx, icy = 252, 318
    defs.append(rad_grad("gi_sky", [(0, "#FFF2A8"), (0.18, "#FFB21F"), (0.42, "#FF6A1A"), (0.7, "#B8201A"), (1, "#3A0A14")], user=(icx, icy - 30, 420)))
    defs.append(lin_grad("gi_gnd", [(0, "#2A2D38"), (1, "#0A0A0D")]))
    defs.append(blur_filter("gi_bl", 6))
    body.append(f'<rect width="{S}" height="{S}" fill="url(#gi_sky)"/>')
    body.append(rays(icx, icy - 30, 22, 460, "#FFF2A8", 0.18, rot=0.1))
    for ex, ey, er, k in [(78, 150, 58, 1), (440, 128, 50, 2)]:
        d, b = explosion(ex, ey, er, rng, f"gi_e{k}", n=13, shards=6, chunks=5, sw=5, glow=False)
        defs.append(d)
        body.append(b)
    body.append(skyline(rng, -20, S + 20, 410, 110, 250, 46, 90, "#4A1018", win="#FFB21F", lit=0.18, gap=(0, 8), broken=0.5, win_size=(6, 8)))
    body.append(skyline(rng, -20, S + 20, 430, 50, 150, 40, 80, "#22080E", win="#FF7A1A", lit=0.12, gap=(0, 6), broken=0.4, win_size=(6, 8)))
    body.append(f'<rect x="0" y="420" width="{S}" height="92" fill="url(#gi_gnd)"/>')
    for a in (-160, -120, -60, -20, 10):
        ex_, ey_ = icx + math.cos(math.radians(a)) * 280, 470 + math.sin(math.radians(a)) * 30 + 30
        cp = jag_line((icx, 452), (ex_, ey_), 5, 8, rng)
        body.append(f'<polygon points="{pts(taper_poly(cp, 10, rng, start_w=12))}" fill="#FFB21F" stroke="{INK}" stroke-width="3"/>')
    pb = burst_points(icx, icy, 15, 220, 165, rng, inner=(0.55, 0.68), outer=(0.9, 1.0), jitter=0.3)
    pb2 = burst_points(icx, icy, 12, 140, 105, rng, inner=(0.58, 0.7), outer=(0.9, 1.0), jitter=0.3)
    body.append(f'<polygon points="{pts(pb)}" fill="#FFD21F" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>')
    body.append(f'<polygon points="{pts(pb2)}" fill="#FFFFFF"/>')
    body.append(car(86, 470, 1.0, body="#22E1FF", crush=1.0))
    hand_x, hand_y, th = 486, 132, -112
    body.append(f'<g opacity="0.9">{arc_streak(hand_x, hand_y, 330, -150, -118, 22, "#FFFFFF")}{arc_streak(hand_x, hand_y, 270, -146, -120, 14, "#FFF2A8")}{arc_streak(hand_x, hand_y, 210, -142, -122, 9, "#FFFFFF")}</g>')
    body.append(f'<g transform="translate({hand_x} {hand_y})">{sledgehammer(38, length=6.6, head_w=4.4, head_h=2.6, angle=th, hand=(0, 0), sw=8)}</g>')
    body.append(f'<polygon points="{pts(star4(icx + 6, icy + 4, 46, rot=0.4, k=0.22))}" fill="#FFFFFF" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    body.append(shard_ring(rng, icx, icy, 12, 60, 150, 7, 13, ["#BFF6FF", "#FFFFFF", "#22E1FF"], sw=3, squash=0.7))
    body.append(chunk_field(rng, 7, (icx - 170, icy - 120, icx + 170, icy - 40), 6, 12, sw=3))
    body.append(spark_field(rng, 14, (10, 20, 500, 420), 5, 11, avoid=(icx - 160, icy - 90, icx + 160, icy + 150)))
    vd, vb = vignette("gi_vig", S, S, 0.65)
    defs.append(vd)
    body.append(vb)
    body.append(f'<rect x="4" y="4" width="{S - 8}" height="{S - 8}" rx="10" fill="none" stroke="{INK}" stroke-width="8"/>')
    return svg_doc(S, S, "".join(defs), "".join(body))


def hazard_band(pid, y0, y1, w, slant=0.0, size=56):
    poly = [(-40, y0), (w + 40, y0 + slant), (w + 40, y1 + slant), (-40, y1)]
    return (f'<polygon points="{pts(poly)}" fill="url(#{pid})" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>'
            f'<polygon points="{pts(poly)}" fill="none" stroke="#FF7A1A" stroke-width="3" opacity="0.7" transform="translate(0 {-8 if y0 > 500 else 8})"/>')


def crane(x, y, h, color="#08080B"):
    out = [f'<rect x="{x}" y="{y - h}" width="34" height="{h}" fill="{color}"/>']
    for k in range(int(h // 60)):
        yy = y - h + k * 60
        out.append(f'<path d="M{x},{yy} L{x + 34},{yy + 60} M{x + 34},{yy} L{x},{yy + 60}" stroke="#1C1D24" stroke-width="4"/>')
    out.append(f'<rect x="{x - 420}" y="{y - h - 30}" width="560" height="30" fill="{color}"/>')
    out.append(f'<polygon points="{pts([(x - 10, y - h - 30), (x + 17, y - h - 110), (x + 44, y - h - 30)])}" fill="{color}"/>')
    out.append(f'<line x1="{x + 17}" y1="{y - h - 110}" x2="{x - 410}" y2="{y - h - 30}" stroke="{color}" stroke-width="5"/>')
    out.append(f'<line x1="{x - 330}" y1="{y - h}" x2="{x - 360}" y2="{y - h + 330}" stroke="{color}" stroke-width="5"/>')
    out.append(f'<circle cx="{x - 364}" cy="{y - h + 390}" r="62" fill="{color}" stroke="#2A1A10" stroke-width="5"/>')
    out.append(f'<circle cx="{x + 17}" cy="{y - h - 116}" r="7" fill="#FF3B3B"/>')
    return "".join(out)


def loading_svg(seed=21):
    W, H = TW, TH
    rng = random.Random(seed)
    defs, body = [], []
    defs.append(lin_grad("ld_bg", [(0, "#0A0A0D"), (0.55, "#17181F"), (1, "#0C0C10")]))
    defs.append(rad_grad("ld_glow", [(0, "#FF7A1A", 0.42), (0.45, "#FF5A1A", 0.16), (1, "#FF5A1A", 0)], user=(W * 0.5, H * 0.5, 900)))
    defs.append(lin_grad("ld_hor", [(0, "#FF6A1A", 0), (0.7, "#FF6A1A", 0.35), (1, "#FFB21F", 0.55)]))
    defs.append('<pattern id="ld_panel" width="320" height="180" patternUnits="userSpaceOnUse">'
                '<rect width="320" height="180" fill="none" stroke="#24262F" stroke-width="3"/>'
                '<rect x="2" y="2" width="316" height="3" fill="#2E313B"/>'
                + "".join(f'<circle cx="{cx}" cy="{cy}" r="5" fill="#262832" stroke="#0A0A0D" stroke-width="2"/>' for cx, cy in [(16, 16), (304, 16), (16, 164), (304, 164)])
                + '</pattern>')
    defs.append(hazard_pattern("ld_haz", 64, PAL["yellow"], PAL["black"], angle=-35))
    defs.append(blur_filter("ld_bl30", 30))
    defs.append(blur_filter("ld_bl6", 6))
    defs.append(grain_filter("ld_gr", seed=5, alpha=0.06))
    body.append(f'<rect width="{W}" height="{H}" fill="url(#ld_bg)"/>')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#ld_panel)" opacity="0.8"/>')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#ld_glow)"/>')
    body.append(f'<rect x="0" y="560" width="{W}" height="360" fill="url(#ld_hor)"/>')
    for _ in range(9):
        sx = rng.choice([rng.uniform(40, 560), rng.uniform(1360, 1880)])
        body.append(f'<ellipse cx="{sx:.0f}" cy="{rng.uniform(640, 760):.0f}" rx="{rng.uniform(90, 200):.0f}" ry="{rng.uniform(140, 260):.0f}" fill="#0A0A0D" opacity="0.55" filter="url(#ld_bl30)"/>')
    body.append(skyline(rng, -20, W + 20, 930, 200, 430, 90, 190, "#1B1C24", win="#FF9A3A", lit=0.12, gap=(0, 20), broken=0.25, win_size=(12, 16)))
    body.append(crane(1700, 930, 520, "#0F1015"))
    body.append(skyline(rng, -20, W + 20, 960, 90, 260, 80, 170, "#0D0D11", win="#FF7A1A", lit=0.07, gap=(0, 14), broken=0.35, win_size=(12, 16)))
    body.append(embers(rng, 90, (0, 380, W, 960)))
    body.append(f'<rect x="0" y="940" width="{W}" height="140" fill="#0A0A0D"/>')
    body.append(hazard_band("ld_haz", 958, 1030, W, slant=-20))
    body.append(hazard_band("ld_haz", 22, 70, W, slant=14))
    body.append(f'<rect x="0" y="0" width="{W}" height="22" fill="#0A0A0D"/>')
    for side in (0, 1):
        if side == 0:
            poly = [(0, 70), (120, 84), (60, 958), (0, 958)]
        else:
            poly = [(W, 84), (W - 120, 98), (W - 60, 938), (W, 938)]
        body.append(f'<polygon points="{pts(poly)}" fill="#14151B" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>')
        e = [poly[1], poly[2]]
        body.append(f'<line x1="{e[0][0]}" y1="{e[0][1]}" x2="{e[1][0]}" y2="{e[1][1]}" stroke="#FF7A1A" stroke-width="5" opacity="0.85"/>')
        body.append(f'<line x1="{e[0][0]}" y1="{e[0][1]}" x2="{e[1][0]}" y2="{e[1][1]}" stroke="#FF7A1A" stroke-width="20" opacity="0.35" filter="url(#ld_bl6)"/>')
    body.append(f'<rect width="{W}" height="{H}" filter="url(#ld_gr)" opacity="0.7"/>')
    vd, vb = vignette("ld_vig", W, H, 0.8)
    defs.append(vd)
    body.append(vb)
    return svg_doc(W, H, "".join(defs), "".join(body))


GOLD_FILL = [(0, "#FFFFFF"), (0.5, "#FFF3B0"), (0.52, "#FFD21F"), (1, "#FF9A1F")]
FIRE_FILL = [(0, "#FFFFFF"), (0.45, "#FFE15A"), (0.47, "#FFB21F"), (1, "#FF5A1A")]
VIOLET_FILL = [(0, "#FFFFFF"), (0.45, "#EBD2FF"), (0.47, "#C77DFF"), (1, "#7A2FD6")]


def thumb_svg(tid, sdefs, sbody, lines, hx, hy, logo_pos, ring="#FF7A1A"):
    hd, hb = headline(lines, hx, hy, f"{tid}_h", skew=SKEW, outline=24, ring=ring, extrude=(12, 20))
    vd, vb = vignette(f"{tid}_vig", TW, TH, 0.72)
    lx, ly, lw = logo_pos
    defs = sdefs + hd + vd + grain_filter(f"{tid}_gr", seed=3, alpha=0.05)
    body = sbody + vb + hb + f'<rect width="{TW}" height="{TH}" filter="url(#{tid}_gr)" opacity="0.6"/>' + logo_embed(lx, ly, lw)
    return svg_doc(TW, TH, defs, body)


def tower(x, y, w, h, d, front, win_on, rng, win_off="#262B36", lit=0.45, sw=10):
    wins = []
    cols = int((w - 30) // 52)
    rows = int((h - 30) // 64)
    ox = x + (w - cols * 52 + 16) / 2
    for r in range(rows):
        for c in range(cols):
            col = win_on if rng.random() < lit else win_off
            wins.append(f'<rect x="{ox + c * 52:.1f}" y="{y + 26 + r * 64:.1f}" width="36" height="44" fill="{col}" stroke="{INK}" stroke-width="3"/>')
    wins.append(f'<rect x="{x + 10}" y="{y + 10}" width="14" height="{h - 20}" fill="#FFFFFF" opacity="0.15"/>')
    return cuboid(x, y, w, h, d, front, sw=sw, extra_front="".join(wins))


def bill(x, y, w, h, rot):
    return (f'<g transform="rotate({rot:.1f} {x:.1f} {y:.1f})">'
            f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="#4CD474" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="{x - w / 2 + 8:.1f}" y="{y - h / 2 + 8:.1f}" width="{w - 16:.1f}" height="{h - 16:.1f}" fill="none" stroke="#1F8A40" stroke-width="3"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{h * 0.3:.1f}" fill="#2FA956" stroke="#1F8A40" stroke-width="3"/>'
            f'<text x="{x:.1f}" y="{y + h * 0.19:.1f}" font-family="{FONT}" font-size="{h * 0.5:.1f}" fill="#E9FFE9" text-anchor="middle">$</text></g>')


def coin(x, y, r):
    return (f'<ellipse cx="{x:.1f}" cy="{y + r * 0.14:.1f}" rx="{r:.1f}" ry="{r * 0.92:.1f}" fill="#C98A00" stroke="{INK}" stroke-width="6"/>'
            f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.92:.1f}" fill="#FFD21F" stroke="{INK}" stroke-width="6"/>'
            f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 0.7:.1f}" ry="{r * 0.64:.1f}" fill="none" stroke="#E0A800" stroke-width="5"/>'
            f'<text x="{x:.1f}" y="{y + r * 0.36:.1f}" font-family="{FONT}" font-size="{r:.1f}" fill="#B87800" text-anchor="middle">$</text>'
            f'<ellipse cx="{x - r * 0.35:.1f}" cy="{y - r * 0.4:.1f}" rx="{r * 0.2:.1f}" ry="{r * 0.12:.1f}" fill="#FFFFFF" opacity="0.8"/>')


def t1_svg(seed=31):
    rng = random.Random(seed)
    d, b = [], []
    ex, ey = 1400, 500
    d.append(lin_grad("t1_sky", [(0, "#1A0A1E"), (0.45, "#7A1A22"), (0.78, "#E2501A"), (1, "#FFB21F")]))
    d.append(rad_grad("t1_glow", [(0, "#FFE15A", 0.85), (0.35, "#FF7A1A", 0.45), (1, "#FF5A1A", 0)], user=(ex, ey, 950)))
    d.append(blur_filter("t1_bl", 22))
    b.append(f'<rect width="{TW}" height="{TH}" fill="url(#t1_sky)"/>')
    b.append(f'<rect width="{TW}" height="{TH}" fill="url(#t1_glow)"/>')
    b.append(rays(ex, ey, 26, 1800, "#FFE9A0", 0.13, rot=0.05))
    b.append(skyline(rng, -20, TW + 20, 900, 220, 480, 90, 180, "#3A1420", win="#FFB21F", lit=0.15, gap=(0, 16), broken=0.2))
    b.append(skyline(rng, -20, TW + 20, 970, 120, 320, 80, 170, "#1E0A12", win="#FF7A1A", lit=0.1, gap=(0, 12), broken=0.35))
    tw_ = tower(1210, 150, 360, 920, 110, "#5A6479", "#9FF3FF", rng)
    line = jag_line((1150, 540), (1730, 455), 7, 34, rng)
    d.append(f'<clipPath id="t1_lo"><polygon points="{pts(line + [(1730, 1100), (1150, 1100)])}"/></clipPath>')
    d.append(f'<clipPath id="t1_hi"><polygon points="{pts(line + [(1730, -400), (1150, -400)])}"/></clipPath>')
    for _ in range(12):
        a = rng.uniform(0, math.tau)
        b.append(f'<circle cx="{ex + math.cos(a) * 260:.0f}" cy="{ey + math.sin(a) * 200 - 80:.0f}" r="{rng.uniform(120, 200):.0f}" fill="#1A1218" opacity="0.7" filter="url(#t1_bl)"/>')
    b.append(f'<g clip-path="url(#t1_lo)">{tw_}</g>')
    b.append(f'<g transform="rotate(11 {ex} 480) translate(40 -140)"><g clip-path="url(#t1_hi)">{tw_}</g>'
             f'<polyline points="{pts(line)}" fill="none" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/></g>')
    ed, eb = explosion(ex, ey, 290, rng, "t1_ex", n=21, shards=20, chunks=16, sw=12)
    d.append(ed)
    b.append(eb)
    b.append(chunk_field(rng, 18, (980, 120, 1900, 760), 14, 42, sw=7))
    b.append(shard_ring(rng, ex, ey, 22, 330, 620, 12, 26, ["#BFF6FF", "#FFFFFF", "#9FF3FF"], sw=5))
    b.append(rubble_ground(rng, 1000, TW, n=36))
    b.append(spark_field(rng, 30, (900, 60, 1900, 980), 10, 24, avoid=(ex - 300, ey - 260, ex + 300, ey + 260)))
    lines = [dict(text="DESTROY", size=240, fill=FIRE_FILL), dict(text="THE CITY", size=176, dy=200, dx=34, fill=GOLD_FILL)]
    return thumb_svg("t1", "".join(d), "".join(b), lines, 80, 300, (36, 816, 470), ring="#FF3B3B")


def t2_svg(seed=32):
    rng = random.Random(seed)
    d, b = [], []
    cx, cy = 1330, 520
    d.append(rad_grad("t2_bg", [(0, "#FFF6C8"), (0.28, "#FFC21F"), (0.62, "#FF8A1A"), (1, "#6A2208")], user=(cx, cy, 1200)))
    d.append(blur_filter("t2_bl", 18))
    b.append(f'<rect width="{TW}" height="{TH}" fill="url(#t2_bg)"/>')
    b.append(rays(cx, cy, 30, 1900, "#FFF6C8", 0.28, rot=0.04))
    stacks = []
    for r in range(10, -1, -1):
        row_w = 1180 - r * 98
        n = max(1, int(row_w // 138))
        y = 1010 - r * 50
        x0 = cx + 30 - row_w / 2
        for i in range(n):
            sx = x0 + i * (row_w / n) + rng.uniform(-12, 12)
            band = f'<rect x="{sx + 62:.1f}" y="{y}" width="26" height="48" fill="#F5F5F7" stroke="{INK}" stroke-width="3"/>'
            stacks.append(cuboid(sx, y, 150, 48, 40, "#3CCB63", side="#23924A", top="#9AF0A8", sw=6, extra_front=band))
        if r % 2 == 0:
            for _ in range(2):
                stacks.append(coin(x0 + rng.uniform(40, row_w - 40), y - 10, rng.uniform(26, 38)))
        if r % 3 == 1:
            gx = x0 + rng.uniform(60, max(61, row_w - 200))
            stacks.append(cuboid(gx, y - 20, 120, 40, 36, "#FFC428", side="#C98A00", top="#FFF0A0", sw=6))
    b.append(f'<ellipse cx="{cx}" cy="1060" rx="760" ry="90" fill="#3A1406" opacity="0.6" filter="url(#t2_bl)"/>')
    b.append("".join(stacks))
    u = 56
    fan = "".join(bill(u + dx, 4.3 * u, 1.9 * u, 1.0 * u, rot) for dx, rot in [(-10, -25), (0, 0), (10, 25)])
    b.append(f'<ellipse cx="1300" cy="1010" rx="230" ry="34" fill="#000" opacity="0.4"/>')
    b.append(avatar(1190, 560, u, arm_l=150, arm_r=-150, face="grin", tool_svg_l=fan, tool_svg_r=fan))
    for _ in range(26):
        x, y = rng.uniform(40, 1900), rng.uniform(30, 1000)
        if x < 960 and y < 760:
            continue
        b.append(bill(x, y, rng.uniform(90, 150), rng.uniform(48, 70), rng.uniform(-60, 60)))
    for _ in range(10):
        b.append(coin(rng.uniform(900, 1900), rng.uniform(40, 500), rng.uniform(22, 36)))
    b.append(spark_field(rng, 34, (40, 30, 1900, 1040), 12, 28, fill="#FFFFFF", stroke="#FFD21F", avoid=(0, 0, 960, 780)))
    lines = [dict(text="GET", size=300, fill=GOLD_FILL), dict(text="RICH", size=320, dy=290, dx=-30, fill=GOLD_FILL)]
    return thumb_svg("t2", "".join(d), "".join(b), lines, 110, 350, (40, 820, 460), ring="#23924A")


def flame(x, y, s, fill="#C77DFF", core="#F3D9FF"):
    p = [(x - s, y), (x - s * 0.7, y - s * 1.3), (x - s * 0.3, y - s * 0.9), (x - s * 0.05, y - s * 2.3), (x + s * 0.3, y - s * 1.0), (x + s * 0.65, y - s * 1.6), (x + s, y)]
    q = [(x - s * 0.5, y), (x - s * 0.15, y - s * 1.1), (x + s * 0.5, y)]
    return (f'<polygon points="{pts(p)}" fill="{fill}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            f'<polygon points="{pts(q)}" fill="{core}"/>')


def bolt(rng, p0, p1, glow="#C77DFF", core="#FFFFFF", fid="t3_bl"):
    ln = jag_line(p0, p1, 9, 46, rng)
    return (f'<polyline points="{pts(ln)}" fill="none" stroke="{glow}" stroke-width="34" stroke-linejoin="round" opacity="0.8" filter="url(#{fid})"/>'
            f'<polyline points="{pts(ln)}" fill="none" stroke="{INK}" stroke-width="16" stroke-linejoin="round"/>'
            f'<polyline points="{pts(ln)}" fill="none" stroke="{core}" stroke-width="8" stroke-linejoin="round"/>')


def chaos_core(cx, cy, s, gid):
    t, bt, l, r, f = (cx, cy - s * 1.35), (cx, cy + s * 1.35), (cx - s, cy), (cx + s, cy), (cx - s * 0.12, cy + s * 0.08)
    d = rad_grad(gid, [(0, "#FFFFFF", 0.95), (0.3, "#E8C8FF", 0.7), (0.65, "#A64DFF", 0.35), (1, "#A64DFF", 0)], user=(cx, cy, s * 3.2))
    out = [f'<circle cx="{cx}" cy="{cy}" r="{s * 3.2:.1f}" fill="url(#{gid})"/>']
    for tri, col in [((t, l, f), "#F0DCFF"), ((t, f, r), "#C77DFF"), ((l, bt, f), "#7A2FD6"), ((f, bt, r), "#4A1580")]:
        out.append(f'<polygon points="{pts(tri)}" fill="{col}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    out.append(f'<polygon points="{pts([t, r, bt, l])}" fill="none" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>')
    out.append(f'<polygon points="{pts([(cx - s * 0.55, cy - s * 0.35), (cx - s * 0.12, cy - s * 1.0), (cx - s * 0.2, cy - s * 0.3)])}" fill="#FFFFFF" opacity="0.85"/>')
    return d, "".join(out)


def t3_svg(seed=33):
    rng = random.Random(seed)
    d, b = [], []
    vx, vy = 1330, 300
    d.append(rad_grad("t3_sky", [(0, "#F3D9FF"), (0.12, "#C77DFF"), (0.35, "#7A2FD6"), (0.7, "#2A0E4A"), (1, "#0B0614")], user=(vx, vy, 1300)))
    d.append(rad_grad("t3_core", [(0, "#000000"), (0.6, "#1A0630"), (1, "#7A2FD6")]))
    d.append(blur_filter("t3_bl", 14))
    d.append(blur_filter("t3_bl2", 40))
    b.append(f'<rect width="{TW}" height="{TH}" fill="url(#t3_sky)"/>')
    b.append(rays(vx, vy, 24, 1900, "#E8C8FF", 0.12, rot=0.2))
    rings = []
    for k in range(9):
        rx = 500 - k * 50
        col = ["#F3D9FF", "#A64DFF", "#5A1A9A"][k % 3]
        rings.append(f'<ellipse cx="{vx}" cy="{vy}" rx="{rx}" ry="{rx * 0.36:.0f}" fill="none" stroke="{col}" stroke-width="{20 - k}" '
                     f'stroke-dasharray="{rx * 0.9:.0f} {rx * 0.35:.0f}" stroke-dashoffset="{k * 97}" opacity="0.85"/>')
    b.append(f'<g transform="rotate(-8 {vx} {vy})"><ellipse cx="{vx}" cy="{vy}" rx="560" ry="210" fill="#A64DFF" opacity="0.45" filter="url(#t3_bl2)"/>'
             f'{"".join(rings)}<ellipse cx="{vx}" cy="{vy}" rx="120" ry="46" fill="url(#t3_core)" stroke="#FFFFFF" stroke-width="8"/></g>')
    for i in range(6):
        a0 = i * math.tau / 6
        sp = [(vx + math.cos(a0 + t * 2.4) * (520 - t * 420), vy + math.sin(a0 + t * 2.4) * (520 - t * 420) * 0.36) for t in [j / 12 for j in range(13)]]
        b.append(f'<polygon points="{pts(taper_poly(sp, 18, rng, start_w=20, wobble=0.1))}" fill="#F3D9FF" opacity="0.55" transform="rotate(-8 {vx} {vy})"/>')
    for p0, p1 in [((1010, 360), (820, 860)), ((1600, 380), (1780, 880)), ((1180, 420), (1090, 820)), ((1500, 400), (1440, 760))]:
        b.append(bolt(rng, p0, p1))
    b.append(skyline(rng, -20, TW + 20, 930, 200, 430, 90, 190, "#2A1240", win="#E8A8FF", lit=0.08, gap=(0, 18), broken=0.85))
    for _ in range(9):
        b.append(flame(rng.uniform(60, 1860), rng.uniform(640, 820), rng.uniform(26, 52)))
    b.append(skyline(rng, -20, TW + 20, 995, 100, 280, 80, 170, "#120820", win="#C77DFF", lit=0.06, gap=(0, 14), broken=0.9))
    for _ in range(16):
        x, y = rng.uniform(600, 1900), rng.uniform(420, 760)
        dx, dy = vx - x, vy - y
        L = math.hypot(dx, dy)
        b.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - dx / L * 90:.0f}" y2="{y - dy / L * 90:.0f}" stroke="#C77DFF" stroke-width="8" stroke-linecap="round" opacity="0.7"/>')
        b.append(f'<polygon points="{pts(quad_chunk(x, y, rng.uniform(12, 30), rng))}" fill="{rng.choice(["#2A2238", "#3A2F4E", "#1E1828"])}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    b.append(rubble_ground(rng, 1010, TW, color="#0E0718", n=34))
    b.append(spark_field(rng, 30, (40, 40, 1900, 1000), 9, 22, fill="#F3D9FF", stroke="#A64DFF", avoid=(0, 60, 1000, 560)))
    lines = [dict(text="NEW CHAOS", size=196, fill=VIOLET_FILL), dict(text="EVENT", size=250, dy=250, dx=30, fill=FIRE_FILL)]
    return thumb_svg("t3", "".join(d), "".join(b), lines, 70, 270, (1420, 850, 460), ring="#22E1FF")


def t4_svg(seed=34):
    rng = random.Random(seed)
    d, b = [], []
    ax, ay = 1306, 600
    d.append(rad_grad("t4_bg", [(0, "#8A3FE6"), (0.3, "#3A1270"), (0.7, "#150828"), (1, "#07040D")], user=(ax, ay - 60, 1250)))
    d.append(blur_filter("t4_bl", 18))
    d.append(blur_filter("t4_bl2", 36))
    b.append(f'<rect width="{TW}" height="{TH}" fill="url(#t4_bg)"/>')
    b.append(rays(ax, 220, 32, 2000, "#E8C8FF", 0.1, rot=0.1))
    b.append(embers(rng, 120, (0, 0, TW, TH), colors=("#C77DFF", "#22E1FF", "#F3D9FF"), rmax=4))
    au1 = burst_points(ax, ay - 40, 18, 360, 520, rng, inner=(0.62, 0.75), outer=(0.9, 1.05), jitter=0.4)
    au2 = burst_points(ax, ay - 20, 15, 280, 430, rng, inner=(0.6, 0.75), outer=(0.9, 1.0), jitter=0.4)
    b.append(f'<polygon points="{pts(au1)}" fill="#A64DFF" opacity="0.7" filter="url(#t4_bl)"/>')
    b.append(f'<polygon points="{pts(au2)}" fill="#E8C8FF" opacity="0.55" filter="url(#t4_bl)"/>')
    for _ in range(14):
        x = ax + rng.uniform(-300, 300)
        y = rng.uniform(250, 900)
        h = rng.uniform(80, 220)
        b.append(f'<polygon points="{pts([(x - 10, y), (x, y - h), (x + 10, y)])}" fill="{rng.choice(["#F3D9FF", "#22E1FF", "#C77DFF"])}" opacity="0.8"/>')
    b.append(f'<ellipse cx="{ax}" cy="1000" rx="360" ry="64" fill="none" stroke="#22E1FF" stroke-width="30" opacity="0.6" filter="url(#t4_bl)"/>')
    b.append(f'<ellipse cx="{ax}" cy="1000" rx="360" ry="64" fill="none" stroke="#22E1FF" stroke-width="10"/>')
    b.append(f'<ellipse cx="{ax}" cy="690" rx="420" ry="96" fill="none" stroke="#C77DFF" stroke-width="12" transform="rotate(-10 {ax} 690)"/>')
    b.append(avatar(1190, 540, 58, arm_l=165, arm_r=-165, face="shout"))
    b.append(f'<path d="M{ax - 420},690 A420 96 0 0 0 {ax + 420},690" fill="none" stroke="#F3D9FF" stroke-width="12" transform="rotate(-10 {ax} 690)"/>')
    cx_, cy_ = ax, 190
    for hx_ in (1080, 1532):
        b.append(f'<line x1="{hx_}" y1="350" x2="{cx_}" y2="{cy_}" stroke="#C77DFF" stroke-width="30" opacity="0.6" filter="url(#t4_bl)"/>'
                 f'<line x1="{hx_}" y1="350" x2="{cx_}" y2="{cy_}" stroke="#F3D9FF" stroke-width="8"/>')
    cd, cb = chaos_core(cx_, cy_, 78, "t4_cg")
    d.append(cd)
    b.append(cb)
    b.append(shard_ring(rng, cx_, cy_, 14, 140, 280, 10, 20, ["#C77DFF", "#F3D9FF", "#7A2FD6"], sw=4, squash=0.8))
    b.append(spark_field(rng, 26, (900, 30, 1900, 1000), 10, 24, fill="#F3D9FF", stroke="#A64DFF"))
    lines = [dict(text="REBIRTH", size=250, fill=VIOLET_FILL)]
    return thumb_svg("t4", "".join(d), "".join(b), lines, 70, 560, (40, 830, 460), ring="#22E1FF")


def blaster(x, y, ang, s=1.0):
    o = [f'<g transform="translate({x} {y}) rotate({ang:.2f}) scale({s})">']
    o.append(f'<polygon points="{pts([(-640, 40), (-900, 10), (-940, 220), (-620, 150)])}" fill="#2A2238" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>')
    o.append(f'<polygon points="{pts([(-470, 90), (-370, 90), (-320, 300), (-430, 320)])}" fill="#241C34" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>')
    o.append(f'<polygon points="{pts([(-660, -80), (-260, -112), (-230, 96), (-600, 120), (-680, 40)])}" fill="#352B4E" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>')
    o.append(f'<polygon points="{pts([(-640, -76), (-262, -106), (-258, -82), (-630, -56)])}" fill="#8A6FC4"/>')
    o.append(f'<polygon points="{pts([(-560, -100), (-400, -170), (-330, -112)])}" fill="#3A2F55" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>')
    o.append(f'<rect x="-500" y="-40" width="200" height="56" rx="8" fill="#C77DFF" stroke="{INK}" stroke-width="8"/>'
             f'<rect x="-488" y="-30" width="176" height="14" rx="5" fill="#F3D9FF"/>')
    o.append(f'<line x1="-640" y1="60" x2="-250" y2="40" stroke="#A64DFF" stroke-width="10"/>')
    o.append(f'<rect x="-270" y="-46" width="270" height="92" fill="#352B4E" stroke="{INK}" stroke-width="10"/>')
    for k in (-230, -170, -110):
        o.append(f'<rect x="{k}" y="-54" width="26" height="108" rx="4" fill="#A64DFF" stroke="{INK}" stroke-width="6"/>')
    o.append(f'<polygon points="{pts([(-10, -64), (50, -50), (50, 50), (-10, 64)])}" fill="#2A2238" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>')
    o.append(f'<ellipse cx="50" cy="0" rx="14" ry="40" fill="#FFFFFF" stroke="#C77DFF" stroke-width="6"/>')
    o.append("</g>")
    return "".join(o)


def t5_svg(seed=35):
    rng = random.Random(seed)
    d, b = [], []
    ix, iy = 1430, 560
    mx, my = 880, 770
    ang = math.degrees(math.atan2(iy - my, ix - mx))
    L = math.hypot(ix - mx, iy - my)
    d.append(lin_grad("t5_sky", [(0, "#07040D"), (0.6, "#2A0E4A"), (1, "#14082A")]))
    d.append(rad_grad("t5_glow", [(0, "#E8C8FF", 0.8), (0.3, "#A64DFF", 0.45), (1, "#A64DFF", 0)], user=(ix, iy, 900)))
    d.append(blur_filter("t5_bl", 22))
    b.append(f'<rect width="{TW}" height="{TH}" fill="url(#t5_sky)"/>')
    b.append(f'<rect width="{TW}" height="{TH}" fill="url(#t5_glow)"/>')
    b.append(rays(ix, iy, 26, 1900, "#E8C8FF", 0.1))
    b.append(skyline(rng, -20, TW + 20, 1000, 160, 380, 90, 180, "#1A0D2A", win="#C77DFF", lit=0.1, gap=(0, 16), broken=0.3))
    st = (tower(1360, 70, 220, 260, 70, "#3A3F4E", "#C77DFF", rng, win_off="#1A1C24", lit=0.3)
          + tower(1260, 300, 420, 320, 100, "#343949", "#C77DFF", rng, win_off="#1A1C24", lit=0.3)
          + tower(1170, 600, 600, 480, 120, "#2E3342", "#C77DFF", rng, win_off="#1A1C24", lit=0.3)
          + f'<rect x="1462" y="-20" width="16" height="96" fill="#2E3342" stroke="{INK}" stroke-width="6"/><circle cx="1470" cy="-12" r="12" fill="#FF3B3B"/>')
    b.append(st)
    for a in range(0, 360, 40):
        ra = math.radians(a + rng.uniform(-12, 12))
        cs = crack_set(rng, [(ix, iy), (ix + math.cos(ra) * rng.uniform(260, 420), iy + math.sin(ra) * rng.uniform(220, 380))], 6, 18, 16, [])
        b.append("".join(f'<polygon points="{pts(p)}" fill="#E8C8FF" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>' for p in cs))
    ed, eb = explosion(ix, iy, 250, rng, "t5_ex", n=20, shards=18, chunks=16, sw=12,
                       colors=("#FFFFFF", "#F3D9FF", "#C77DFF", "#A64DFF", "#4A1580"), shard_fill=None)
    d.append(ed)
    b.append(eb)
    beam = [f'<g transform="translate({mx} {my}) rotate({ang:.2f})">']
    beam.append(f'<rect x="0" y="-80" width="{L:.0f}" height="160" fill="#A64DFF" opacity="0.6" filter="url(#t5_bl)"/>')
    beam.append(f'<polygon points="{pts([(30, -36), (L, -58), (L, 58), (30, 36)])}" fill="#C77DFF" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>')
    beam.append(f'<polygon points="{pts([(30, -14), (L, -24), (L, 24), (30, 14)])}" fill="#FFFFFF"/>')
    for k in range(1, 6):
        beam.append(f'<ellipse cx="{k * L / 6:.0f}" cy="0" rx="20" ry="{56 + k * 4}" fill="none" stroke="#F3D9FF" stroke-width="7" opacity="0.9"/>')
    beam.append("</g>")
    b.append("".join(beam))
    b.append(chunk_field(rng, 20, (1050, 150, 1900, 900), 14, 40, fills=("#3A3F4E", "#2E3342", "#4A4F60"), sw=7))
    b.append(shard_ring(rng, ix, iy, 18, 300, 560, 12, 24, ["#F3D9FF", "#C77DFF", "#FFFFFF"], sw=5))
    b.append(rubble_ground(rng, 1015, TW, color="#0E0A16", n=30))
    b.append(f'<ellipse cx="{mx - 380}" cy="{my + 150}" rx="560" ry="200" fill="#A64DFF" opacity="0.55" filter="url(#t5_bl)" transform="rotate({ang:.1f} {mx - 380} {my + 150})"/>')
    b.append(blaster(mx, my, ang))
    b.append(f'<polygon points="{pts(star4(mx + 60, my - 22, 110, rot=0.3, k=0.2))}" fill="#FFFFFF" stroke="#C77DFF" stroke-width="6" stroke-linejoin="round"/>')
    b.append(spark_field(rng, 26, (700, 40, 1900, 1000), 9, 22, fill="#F3D9FF", stroke="#A64DFF", avoid=(ix - 260, iy - 240, ix + 260, iy + 240)))
    lines = [dict(text="ULTIMATE", size=210, fill=VIOLET_FILL), dict(text="TOOL", size=290, dy=270, dx=20, fill=GOLD_FILL)]
    return thumb_svg("t5", "".join(d), "".join(b), lines, 70, 260, (1440, 860, 440), ring="#A64DFF")


THUMB_SPECS = [
    ("t1", "thumbnail_01_destroy_the_city", t1_svg),
    ("t2", "thumbnail_02_get_rich", t2_svg),
    ("t3", "thumbnail_03_new_chaos_event", t3_svg),
    ("t4", "thumbnail_04_rebirth", t4_svg),
    ("t5", "thumbnail_05_ultimate_tool", t5_svg),
]
OPAQUE = [BRAND / "game_icon.png", BRAND / "loading_background.png"] + [THUMBS / f"{n}.png" for _, n, _ in THUMB_SPECS]
ALL_TARGETS = ["logo", "mono", "mark", "game", "loading"] + [t for t, _, _ in THUMB_SPECS]


def write_index():
    idx = {
        "Logo": "assets/brand/logo_main.png",
        "LogoWhite": "assets/brand/logo_white.png",
        "LogoBlack": "assets/brand/logo_black.png",
        "LogoIcon": "assets/brand/logo_icon.png",
        "GameIcon": "assets/brand/game_icon.png",
        "LoadingBackground": "assets/brand/loading_background.png",
    }
    for i, (_, n, _f) in enumerate(THUMB_SPECS, 1):
        idx[f"Thumbnail{i}"] = f"assets/thumbnails/{n}.png"
    (SRC / "index_brand.json").write_text(json.dumps(idx, indent=2), encoding="utf-8")
    return idx


def finalize():
    for p in OPAQUE:
        if p.exists():
            Image.open(p).convert("RGB").save(p, optimize=True)
    mk = BRAND / "logo_icon.png"
    if mk.exists():
        im = Image.open(mk).convert("RGBA")
        assert im.getpixel((0, 0))[3] == 0 and im.getpixel((511, 511))[3] == 0, "logo_icon corners not transparent"


def contact_sheet():
    cw, chh, gap = 480, 270, 16
    sheet = Image.new("RGB", (3 * cw + 4 * gap, 3 * chh + 4 * gap), (40, 40, 48))
    chk = Image.new("RGB", (256, 256), (200, 200, 200))
    dr = ImageDraw.Draw(chk)
    for yy in range(0, 256, 32):
        for xx in range(0, 256, 32):
            if (xx + yy) // 32 % 2:
                dr.rectangle([xx, yy, xx + 31, yy + 31], fill=(150, 150, 150))
    cells = [(BRAND / "logo_icon.png", 256), (BRAND / "game_icon.png", 256), (BRAND / "loading_background.png", None)]
    cells += [(THUMBS / f"{n}.png", None) for _, n, _ in THUMB_SPECS]
    for i, (p, sq) in enumerate(cells):
        if not p.exists():
            continue
        im = Image.open(p).convert("RGBA")
        x, y = gap + (i % 3) * (cw + gap), gap + (i // 3) * (chh + gap)
        if sq:
            bgc = chk.copy()
            im = im.resize((sq, sq), Image.LANCZOS)
            bgc.paste(im, (0, 0), im)
            sheet.paste(bgc, (x, y))
            if i == 1:
                sheet.paste(im.resize((64, 64), Image.LANCZOS).convert("RGB"), (x + 270, y + 10))
        else:
            sheet.paste(im.resize((cw, chh), Image.LANCZOS).convert("RGB"), (x, y))
    out = SRC / "contact_brand.png"
    sheet.save(out)
    return out


def build(targets):
    jobs = []
    if "logo" in targets:
        jobs.append(render_svg(logo_svg("color"), "logo_main", BRAND / "logo_main.png", LW, LH, save_svg=BRAND / "logo_main.svg"))
    if "mono" in targets:
        jobs.append(render_svg(logo_svg("white"), "logo_white", BRAND / "logo_white.png", LW, LH, save_svg=BRAND / "logo_white.svg"))
        jobs.append(render_svg(logo_svg("black"), "logo_black", BRAND / "logo_black.png", LW, LH, save_svg=BRAND / "logo_black.svg"))
    if "mark" in targets:
        jobs.append(render_svg(mark_svg(), "logo_icon", BRAND / "logo_icon.png", 512, 512, save_svg=BRAND / "logo_icon.svg"))
    if "game" in targets:
        jobs.append(render_svg(game_icon_svg(), "game_icon", BRAND / "game_icon.png", 512, 512, bg="#0A0A0D", save_svg=BRAND / "game_icon.svg"))
    if "loading" in targets:
        jobs.append(render_svg(loading_svg(), "loading_background", BRAND / "loading_background.png", TW, TH, bg="#0A0A0D",
                               save_svg=BRAND / "loading_background.svg"))
    for t, n, fn in THUMB_SPECS:
        if t in targets:
            jobs.append(render_svg(fn(), n, THUMBS / f"{n}.png", TW, TH, bg="#0A0A0D", save_svg=THUMBS / f"{n}.svg"))
    if jobs:
        render_many(jobs, timeout=300)
    finalize()
    write_index()
    return contact_sheet()


if __name__ == "__main__":
    t = sys.argv[1:] or ALL_TARGETS
    print("ok", t, build(t))
