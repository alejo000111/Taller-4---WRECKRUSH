from __future__ import annotations

import json
import math
import random
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from wr_lib import ASSETS, BUILD, CAP, FONT, INK, PAL, SRC, burst_points, lin_grad, quad_chunk, rad_grad, render_many, shade, text_width, html_page

ICONS = ASSETS / "icons"
TEX = ASSETS / "textures"
SW = 8.0
SK = -10
G = {"defs": [], "n": 0, "tag": "a"}
LS = [(0.0, 1.0)]

GOLD = "#FFC428"
YEL = "#FFD21F"
ORA = "#FF7A1A"
RED = "#FF3B3B"
PUR = "#A64DFF"
CYA = "#22E1FF"
WHT = "#F5F5F7"
GRN = "#5BE36B"
OLV = "#8CC846"
STEEL = "#8D94A3"
DARKM = "#3A3F4B"
WOOD = "#9A6334"
SKIN = "#F5C935"


def reset(tag):
    G["defs"] = []
    G["n"] = 0
    G["tag"] = tag
    LS[:] = [(0.0, 1.0)]


def uid(p="u"):
    G["n"] += 1
    return f"{G['tag']}{p}{G['n']}"


def adddef(s):
    G["defs"].append(s)


def grp(tf, fn, rot=0.0, sc=1.0):
    r, s = LS[-1]
    LS.append((r + rot, s * sc))
    try:
        inner = fn() if callable(fn) else fn
    finally:
        LS.pop()
    return f'<g transform="{tf}">{inner}</g>'


def place(fn, x, y, k=1.0, a=0.0, **kw):
    return grp(f"translate({x:.1f} {y:.1f}) rotate({a:.1f}) scale({k:.3f})", lambda: fn(**kw), rot=a, sc=k)


def P(points):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points) + " Z"


def R(x, y, w, h, r=0.0):
    r = min(r, w / 2, h / 2)
    if r <= 0:
        return f"M{x:.1f},{y:.1f} h{w:.1f} v{h:.1f} h{-w:.1f} Z"
    return (f"M{x + r:.1f},{y:.1f} H{x + w - r:.1f} A{r:.1f},{r:.1f} 0 0 1 {x + w:.1f},{y + r:.1f} V{y + h - r:.1f} "
            f"A{r:.1f},{r:.1f} 0 0 1 {x + w - r:.1f},{y + h:.1f} H{x + r:.1f} A{r:.1f},{r:.1f} 0 0 1 {x:.1f},{y + h - r:.1f} "
            f"V{y + r:.1f} A{r:.1f},{r:.1f} 0 0 1 {x + r:.1f},{y:.1f} Z")


def E(cx, cy, rx, ry=None):
    ry = rx if ry is None else ry
    return (f"M{cx - rx:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 1 0 {cx + rx:.1f},{cy:.1f} "
            f"A{rx:.1f},{ry:.1f} 0 1 0 {cx - rx:.1f},{cy:.1f} Z")


def rotp(points, deg, cx=0.0, cy=0.0):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in points]


def arcpts(cx, cy, r, a0, a1, n=24):
    return [(cx + math.cos(math.radians(a0 + (a1 - a0) * i / n)) * r, cy + math.sin(math.radians(a0 + (a1 - a0) * i / n)) * r) for i in range(n + 1)]


def star_pts(cx, cy, r, k=0.45, n=5, rot=-90.0):
    out = []
    for i in range(2 * n):
        a = math.radians(rot + 180.0 * i / n)
        rr = r if i % 2 == 0 else r * k
        out.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return out


def gear_d(cx, cy, ro, ri, n, hole=0.0):
    out = []
    step = 360.0 / n
    for i in range(n):
        a = i * step
        for da, rr in ((-0.5 * step, ri), (-0.27 * step, ri), (-0.17 * step, ro), (0.17 * step, ro), (0.27 * step, ri)):
            t = math.radians(a + da)
            out.append((cx + math.cos(t) * rr, cy + math.sin(t) * rr))
    d = P(out)
    if hole:
        d += " " + E(cx, cy, hole)
    return d


def _off(k):
    r, s = LS[-1]
    a = math.radians(-r)
    v = k / s
    return v * math.cos(a) - v * math.sin(a), v * math.sin(a) + v * math.cos(a)


def cel(d, base, so=9.0, ho=7.0, dark=0.66, light=1.38, rule="nonzero", line=True, sw=SW, op=1.0):
    s = LS[-1][1]
    sx, sy = _off(-so)
    hx, hy = _off(ho)
    a, b = uid("c"), uid("c")
    adddef(f'<clipPath id="{a}"><path d="{d}" clip-rule="{rule}"/></clipPath>'
           f'<clipPath id="{b}"><path d="{d}" clip-rule="{rule}" transform="translate({hx:.2f} {hy:.2f})"/></clipPath>')
    fr = f'fill-rule="{rule}"'
    o = (f'<g opacity="{op}">' if op < 1 else "<g>")
    o += (f'<path d="{d}" {fr} fill="{shade(base, dark)}"/>'
          f'<g clip-path="url(#{a})"><path d="{d}" {fr} fill="{shade(base, light)}" transform="translate({sx:.2f} {sy:.2f})"/>'
          f'<g clip-path="url(#{b})"><path d="{d}" {fr} fill="{base}" transform="translate({sx:.2f} {sy:.2f})"/></g></g>')
    if line:
        o += f'<path d="{d}" {fr} fill="none" stroke="{INK}" stroke-width="{sw / s:.2f}" stroke-linejoin="round" stroke-linecap="round"/>'
    return o + "</g>"


def flat(d, fill, line=True, rule="nonzero", sw=SW, op=1.0):
    s = LS[-1][1]
    st = f' stroke="{INK}" stroke-width="{sw / s:.2f}" stroke-linejoin="round"' if line else ""
    return f'<path d="{d}" fill-rule="{rule}" fill="{fill}" opacity="{op}"{st}/>'


def blob(d, base, **kw):
    s = LS[-1][1]
    return f'<path d="{d}" fill="{INK}" stroke="{INK}" stroke-width="{2 * SW / s:.2f}" stroke-linejoin="round"/>' + cel(d, base, line=False, **kw)


def ln(d, color, w, cap="round", outline=True):
    s = LS[-1][1]
    o = ""
    if outline:
        o += f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w + SW / s:.2f}" stroke-linecap="{cap}" stroke-linejoin="round"/>'
    return o + f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w:.2f}" stroke-linecap="{cap}" stroke-linejoin="round"/>'


def spec(x, y, w, h, rot=0.0, op=0.85):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{min(w, h) / 2:.1f}" fill="#FFFFFF" '
            f'opacity="{op}" transform="rotate({rot:.1f} {x + w / 2:.1f} {y + h / 2:.1f})"/>')


def txt(s, cx, cy, size, fill, sw=None, skew=SK, stroke=INK):
    k = LS[-1][1]
    sw = (SW * 1.1 / k) if sw is None else sw
    by = cy + CAP * size / 2
    st = f' stroke="{stroke}" stroke-width="{sw:.2f}" paint-order="stroke" stroke-linejoin="round"' if sw > 0 else ""
    return (f'<g transform="translate({cx:.1f} {cy:.1f}) skewX({skew}) translate({-cx:.1f} {-cy:.1f})">'
            f'<text x="{cx:.1f}" y="{by:.1f}" text-anchor="middle" font-family="{FONT}" font-size="{size:.1f}" fill="{fill}"{st}>{s}</text></g>')


def aura(cx, cy, r, col, op=0.8):
    gid = uid("g")
    adddef(rad_grad(gid, [(0, col, op), (0.5, col, op * 0.4), (1, col, 0)]))
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="url(#{gid})"/>'


def sparkle(cx, cy, r, col="#FFFFFF"):
    return flat(P(star_pts(cx, cy, r, 0.3, 4, -90)), col, sw=SW * 0.7)


def snake(k):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9])", "_", k).lower()


def coin(col=GOLD, sym="$"):
    s = cel(E(10, 12, 92), shade(col, 0.72))
    s += cel(E(0, 0, 92), col)
    s += f'<circle r="66" fill="none" stroke="{shade(col, 0.68)}" stroke-width="9"/>'
    if sym:
        s += txt(sym, 2, 2, 118, "#FFF6C8", skew=0)
    s += spec(-62, -58, 40, 14, -42, 0.8)
    return s


def bill_stack(n=4, col=YEL):
    w, h = 176, 84
    top = -(h + (n - 1) * 12) / 2
    s = ""
    for i in range(n - 1, -1, -1):
        y = top + i * 12
        s += cel(R(-w / 2, y, w, h, 10), shade(col, 0.92 if i % 2 else 1.0))
    s += f'<path d="{R(-w / 2 + 12, top + 10, w - 24, h - 20, 6)}" fill="none" stroke="{shade(col, 0.62)}" stroke-width="5"/>'
    s += f'<ellipse cx="0" cy="{top + h / 2:.1f}" rx="26" ry="30" fill="{shade(col, 0.8)}" stroke="{shade(col, 0.55)}" stroke-width="4"/>'
    s += txt("$", 0, top + h / 2, 44, shade(col, 0.42), sw=0, skew=0)
    for cx in (-64, 64):
        s += f'<circle cx="{cx}" cy="{top + h / 2:.1f}" r="9" fill="{shade(col, 0.72)}"/>'
    s += cel(R(-46, top - 5, 26, h + (n - 1) * 12 + 10, 4), ORA, so=6, ho=5)
    s += spec(-w / 2 + 10, top + 6, 40, 9, 0, 0.7)
    return s


def cash_pile(n=1):
    lay = {1: [(0, 0, -6)], 2: [(-40, 14, -8), (44, 26, 6)], 3: [(-52, 30, -8), (52, 34, 7), (0, -16, -3)],
           4: [(-64, 38, -8), (64, 40, 8), (0, 50, 0), (-28, -22, -6), (30, -30, 5)]}[n]
    s = ""
    for x, y, a in lay:
        s += place(bill_stack, x, y, 0.62 if n > 1 else 0.85, a)
    return s


def coin_stack(n=3, col=GOLD):
    s = ""
    for i in range(n):
        y = 40 - i * 26
        s += cel(R(-62, y, 124, 30, 14), shade(col, 0.9 if i % 2 else 1.0), so=7)
        s += f'<path d="M-50,{y + 8} v14 M-30,{y + 8} v14 M-10,{y + 8} v14 M10,{y + 8} v14 M30,{y + 8} v14 M50,{y + 8} v14" stroke="{shade(col, 0.6)}" stroke-width="5"/>'
    return s


def nut(col="#9FC3CF"):
    hexa = P([(math.cos(math.radians(a)) * 60, math.sin(math.radians(a)) * 60) for a in range(0, 360, 60)])
    return cel(hexa + " " + E(0, 0, 24), col, rule="evenodd") + spec(-40, -36, 24, 9, -30, 0.7)


def bolt(col="#5E8FA3"):
    s = cel(R(-17, -30, 34, 130, 6), col, so=7)
    s += "".join(f'<path d="M-17,{y} L17,{y - 10}" stroke="{shade(col, 0.55)}" stroke-width="5"/>' for y in range(-6, 100, 16))
    s += cel(P([(-46, -60), (46, -60), (54, -42), (46, -24), (-46, -24), (-54, -42)]), shade(col, 1.15))
    return s


def gear(col="#7FB6C8", teeth=8, hole=30):
    return (cel(gear_d(0, 0, 100, 76, teeth, hole), col, rule="evenodd")
            + f'<circle r="52" fill="none" stroke="{shade(col, 0.72)}" stroke-width="8"/>' + spec(-62, -50, 34, 12, -45, 0.75))


def scrap_chunk():
    s = cel(P([(-98, 40), (-40, 30), (-10, 66), (-60, 92), (-104, 74)]), "#6C8D9A")
    s += place(gear, -20, -14, 0.72, 10, col="#78B4C6")
    s += place(bolt, 64, 6, 0.62, 35)
    s += place(nut, 40, 62, 0.62, 12)
    s += sparkle(-80, -80, 18, CYA) + sparkle(84, -66, 13, CYA)
    return s


def crystal(col=PUR, glow=True):
    T, UL, LL, B, LR, UR = (0, -100), (-56, -40), (-56, 40), (0, 100), (56, 40), (56, -40)
    a, b, c, d = (-18, -46), (-18, 46), (18, 46), (18, -46)
    k = LS[-1][1]
    s = flat(P([T, UL, LL, B, LR, UR]), shade(col, 0.6), sw=SW * 1.2)
    s += flat(P([T, UL, LL, B, b, a]), shade(col, 1.3), line=False)
    s += flat(P([T, a, b, B, c, d]), col, line=False)
    s += flat(P([T, d, c, B, LR, UR]), shade(col, 0.62), line=False)
    s += flat(P([T, a, d]), shade(col, 1.65), line=False)
    s += flat(P([B, b, c]), shade(col, 0.45), line=False)
    s += (f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]} M{d[0]},{d[1]} L{c[0]},{c[1]} M{a[0]},{a[1]} L{d[0]},{d[1]} '
          f'M{b[0]},{b[1]} L{c[0]},{c[1]}" stroke="{INK}" stroke-width="{3.5 / k:.2f}" opacity="0.7"/>')
    if glow:
        s += f'<path d="{P([(0, -34), (12, 0), (0, 34), (-12, 0)])}" fill="#FFFFFF" opacity="0.9"/>'
    s += spec(-46, -30, 12, 52, 0, 0.8)
    s += flat(P([T, UL, LL, B, LR, UR]), "none", sw=SW * 1.1)
    return s


def crystal_cluster(col=PUR):
    return (place(crystal, -58, 24, 0.62, -22, col=col) + place(crystal, 60, 26, 0.6, 20, col=col)
            + place(crystal, 0, -6, 0.92, 0, col=col))


def hammer(head=STEEL, handle=WOOD, hw=134, hh=64, L=176, band=None, grip="#2A2C34", rust=False, glowface=None, white=False):
    hy = -70
    dk = 0.8 if white else 0.66
    k = LS[-1][1]
    s = cel(R(-12, hy, 24, L, 8), handle, dark=dk)
    for i in range(3):
        s += cel(R(-15, hy + L - 70 + i * 21, 30, 15, 5), grip, so=6, ho=5, dark=dk)
    s += cel(R(-17, hy + L - 8, 34, 18, 7), grip, so=6, dark=dk)
    s += cel(R(-hw / 2, hy - hh / 2, hw, hh, 10), head, dark=dk)
    for x in (-hw / 2 - 12, hw / 2 - 12):
        s += cel(R(x, hy - hh / 2 - 7, 24, hh + 14, 7), shade(head, 0.85), so=7, dark=dk)
    if band:
        s += cel(R(-18, hy - hh / 2 - 3, 36, hh + 6, 4), band, so=7, dark=dk)
    if rust:
        for x, y, r in ((-34, hy - 12, 11), (22, hy + 14, 8), (40, hy - 18, 6)):
            s += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#B5652A" opacity="0.85"/>'
        s += f'<path d="{R(-14, hy + 70, 28, 26, 3)}" fill="#AEB4BC" stroke="{INK}" stroke-width="{4 / k:.2f}"/>'
    if glowface:
        s += cel(R(hw / 2 - 2, hy - hh / 2 + 4, 14, hh - 8, 4), glowface, so=5, ho=4, dark=0.8)
    s += spec(-hw / 2 + 14, hy - hh / 2 + 9, hw * 0.34, 10, 0, 0.75)
    return s


def cleaver(blade="#C4703C", edge="#C9D1DC", handle="#2A2C34", glow=YEL):
    s = cel(R(-12, -10, 24, 150, 8), handle)
    for i in range(3):
        s += cel(R(-15, 80 + i * 21, 30, 15, 5), "#5A5F6B", so=6, ho=5)
    s += cel(P([(-20, -120), (96, -96), (110, 14), (-20, 22)]), blade)
    s += cel(P([(96, -96), (122, -90), (134, 18), (110, 14)]), edge, so=6, ho=5)
    s += cel(R(-26, -128, 30, 156, 8), shade(blade, 0.8), so=7)
    s += cel(R(12, -34, 84, 12, 6), glow, so=5, ho=4, dark=0.8)
    for x, y in ((24, -86), (70, -78), (26, -6)):
        s += f'<circle cx="{x}" cy="{y}" r="7" fill="#8E949E" stroke="{INK}" stroke-width="3"/>'
    s += spec(-4, -108, 70, 10, 10, 0.7)
    return s


def wrench(col="#AEB6C4"):
    s = cel(R(-15, -40, 30, 140, 13) + " " + E(0, 82, 8), col, rule="evenodd")
    head = [(15, -106), *arcpts(0, -66, 44, -69, 249, 30)[1:-1], (-15, -106), (-15, -72), (15, -72)]
    s += cel(P(head), col)
    s += spec(-34, -86, 12, 26, 20, 0.7)
    return s


def tools_cross():
    return place(wrench, 0, 0, 0.82, 40) + place(hammer, 0, 6, 0.78, -40)


def jackhammer():
    k = LS[-1][1]
    s = cel(R(-92, -112, 184, 26, 12), "#2A2C34")
    s += cel(R(-104, -118, 48, 38, 14), ORA) + cel(R(56, -118, 48, 38, 14), ORA)
    s += cel(R(-15, -90, 30, 26, 4), STEEL)
    s += cel(R(-46, -68, 92, 112, 18), YEL)
    hz = uid("h")
    adddef(f'<clipPath id="{hz}"><rect x="-46" y="-6" width="92" height="24"/></clipPath>')
    s += f'<rect x="-46" y="-6" width="92" height="24" fill="{INK}"/>'
    s += f'<g clip-path="url(#{hz})">' + "".join(f'<path d="{P([(x, 18), (x + 12, 18), (x + 36, -6), (x + 24, -6)])}" fill="{YEL}"/>' for x in range(-80, 60, 24)) + "</g>"
    s += f'<path d="{R(-46, -6, 92, 24)}" fill="none" stroke="{INK}" stroke-width="{5 / k:.2f}"/>'
    s += "".join(f'<rect x="-30" y="{y}" width="60" height="6" rx="3" fill="{shade(YEL, 0.6)}"/>' for y in (-52, -40, -28))
    s += cel(R(-30, 42, 60, 22, 6), "#6B7280")
    s += cel(P([(-12, 62), (12, 62), (10, 108), (0, 124), (-10, 108)]), "#C3C9D3")
    s += spec(-38, -60, 12, 40, 0, 0.75)
    return s


def tnt_launcher():
    s = cel(P([(-110, -30), (-136, -40), (-136, 40), (-110, 30)]), "#2A2C34")
    s += cel(R(-30, 22, 28, 50, 6), "#2A2C34")
    s += cel(R(-112, -26, 194, 52, 10), "#E23B3B")
    s += cel(R(-46, -46, 34, 20, 5), "#2A2C34")
    for x in (-82, -60):
        s += cel(R(x, -30, 14, 60, 3), "#2A2C34", so=5, ho=4)
    for y in (-27, -9, 9):
        s += cel(R(90, y, 62, 18, 7), "#E8402F", so=6, ho=5)
        s += f'<rect x="114" y="{y + 2}" width="10" height="14" fill="{WHT}"/>'
    s += cel(R(72, -33, 22, 66, 6), "#2A2C34")
    s += ln("M150,-18 Q170,-40 160,-62", "#C9A060", 5)
    s += flat(P(star_pts(160, -66, 18, 0.35, 6, -90)), YEL, sw=SW * 0.6)
    s += spec(-100, -18, 120, 9, 0, 0.6)
    return s


def rocket():
    body = "M0,-110 C30,-80 34,-50 34,-20 L34,60 L-34,60 L-34,-20 C-34,-50 -30,-80 0,-110 Z"
    s = blob("M-26,74 Q-36,120 0,160 Q36,120 26,74 Z", ORA, dark=0.85)
    s += f'<path d="M-14,76 Q-18,108 0,134 Q18,108 14,76 Z" fill="{YEL}"/>'
    s += cel(P([(-34, 6), (-64, 58), (-64, 84), (-34, 60)]), RED)
    s += cel(P([(34, 6), (64, 58), (64, 84), (34, 60)]), RED)
    s += cel(P([(-22, 58), (22, 58), (28, 80), (-28, 80)]), "#4A505C")
    s += cel(body, "#EEF0F4", dark=0.72)
    s += cel("M0,-110 C22,-88 28,-68 30,-52 L-30,-52 C-28,-68 -22,-88 0,-110 Z", RED, so=7)
    s += cel(R(-34, 26, 68, 13), RED, so=6, ho=5)
    s += cel(E(0, -12, 15), "#7FE9FF", so=6, ho=5)
    s += spec(-26, -40, 10, 54, 0, 0.8)
    return s


def blaster(kind="plasma"):
    body, acc, dk = {"plasma": ("#D7DEE8", CYA, "#3A4250"), "chaos": ("#7B3BC9", "#E7B8FF", "#2C1A44"),
                     "void": ("#3A2160", "#B57BFF", "#160C26"), "arc": ("#D8382C", "#FF9A1F", "#2A2C34"),
                     "rail": ("#4A5634", "#C8FF3C", "#1E2418"), "singularity": ("#241830", "#C77DFF", "#100A18")}[kind]
    big = 1.25 if kind == "void" else 1.0
    s = cel(P([(-52, 8), (-16, 8), (-26, 80), (-64, 80)]), dk)
    s += cel(P([(-98, -30), (-132, -22), (-132, 20), (-100, 14)]), dk)
    s += cel(R(44, -22 * big, 64, 40 * big, 8), "#6B7484" if kind == "plasma" else dk)
    s += cel(P([(-100, -42), (32, -42), (56, -24), (56, 22), (-88, 22), (-104, 0)]), body)
    for i in range(3):
        s += cel(R(58 + i * 17, -28 * big, 10, 52 * big, 3), acc, so=5, ho=4)
    s += cel(R(-74, -66, 84, 26, 11), acc, so=6, ho=5)
    s += '<rect x="-64" y="-60" width="34" height="7" rx="3.5" fill="#FFFFFF" opacity="0.85"/>'
    s += cel(R(-60, -14, 70, 12, 5), acc, so=5, ho=4)
    if kind == "chaos":
        s += cel(E(116, -2, 14, 44), acc)
        s += cel(E(116, -2, 7, 24), "#FFFFFF", dark=0.8)
    s += spec(-88, -34, 70, 8, 0, 0.6)
    return s


def blaster_fx(kind):
    if kind == "plasma":
        return aura(0, 0, 70, CYA, 0.9), blob(E(0, 0, 30), "#BFF6FF", dark=0.75) + '<circle r="14" fill="#FFFFFF"/>'
    if kind == "chaos":
        b = [(-40, -10), (0, -26), (-6, -8), (40, -24), (14, 6), (20, -6), (-20, 10), (-14, -2)]
        return aura(0, 0, 70, PUR, 0.8), cel(P(b), "#E7B8FF", dark=0.7)
    if kind == "arc":
        b = [(-8, -46), (-30, 6), (-6, 6), (-18, 46), (26, -10), (2, -10), (14, -46)]
        return aura(0, 0, 70, CYA, 0.9), cel(P(b), "#BFF6FF", dark=0.75)
    if kind == "rail":
        return aura(0, 0, 66, "#C8FF3C", 0.8), cel(R(-64, -12, 128, 24, 12), "#EEFFB8", dark=0.75)
    if kind == "singularity":
        return aura(0, 0, 84, PUR, 0.9), vortex("#C77DFF") + '<circle r="22" fill="#100A18"/>'
    return (aura(0, 0, 80, "#7A3CFF", 0.9),
            blob(E(0, 0, 34), "#B57BFF", dark=0.7) + '<circle r="20" fill="#14081F"/>' + ln("M-12,-6 Q0,-18 12,-4", "#B57BFF", 4, outline=False))


def place2(fn, x, y, k=1.0, a=0.0, **kw):
    tf = f"translate({x:.1f} {y:.1f}) rotate({a:.1f}) scale({k:.3f})"
    res = {}

    def inner():
        res["v"] = fn(**kw)
        return res["v"][1]
    main = grp(tf, inner, a, k)
    return f'<g transform="{tf}">{res["v"][0]}</g>', main


def fist(col=SKIN):
    s = cel(R(-46, 52, 92, 50, 10), "#2A2C34")
    s += cel(R(-64, -30, 128, 96, 26), col)
    for i, x in enumerate((-64, -32, 0, 32)):
        s += cel(R(x, -70 + (4 if i in (0, 3) else 0), 32, 62, 14), shade(col, 1.0 if i % 2 else 0.96), so=7, ho=6)
        s += spec(x + 7, -62 + (4 if i in (0, 3) else 0), 12, 8, 0, 0.75)
    s += grp("rotate(-10)", lambda: cel(R(-74, 0, 96, 32, 16), col, so=7), rot=-10)
    return s


def bolt_d():
    return P([(24, -110), (-62, 12), (-8, 12), (-32, 110), (64, -24), (8, -24), (44, -110)])


def lightning(col=YEL):
    return cel(bolt_d(), col) + spec(4, -84, 10, 50, 28, 0.8)


def burst(cols=(ORA, YEL, "#FFF6C2"), seed=3, n=11, r=110):
    rng = random.Random(seed)
    p1 = burst_points(0, 0, n, r, r, rng, inner=(0.58, 0.68), outer=(0.92, 1.0))
    p2 = burst_points(0, 0, n - 2, r * 0.7, r * 0.7, rng, inner=(0.58, 0.7), outer=(0.9, 1.0))
    p3 = burst_points(0, 0, n - 4, r * 0.4, r * 0.4, rng, inner=(0.6, 0.72), outer=(0.9, 1.0))
    return cel(P(p1), cols[0], dark=0.75) + cel(P(p2), cols[1], so=7, dark=0.8) + flat(P(p3), cols[2], sw=SW * 0.6)


def explosion_glyph():
    rng = random.Random(8)
    s = ""
    for a in range(0, 360, 45):
        x, y = math.cos(math.radians(a + 20)) * 86, math.sin(math.radians(a + 20)) * 86
        s += blob(E(x, y, 34), "#4A4550", dark=0.75)
    s += burst(seed=5, r=104)
    for a in (30, 150, 260):
        x, y = math.cos(math.radians(a)) * 112, math.sin(math.radians(a)) * 112
        s += cel(P(quad_chunk(x, y, 16, rng)), "#6E6A66", so=5, ho=4)
    return s


def crosshair(col=RED):
    s = cel(E(0, 0, 86) + " " + E(0, 0, 62), col, rule="evenodd")
    for a in (0, 90, 180, 270):
        s += grp(f"rotate({a})", lambda: cel(R(-10, -112, 20, 44, 5), col, so=6, ho=5), rot=a)
    s += cel(P(star_pts(0, 0, 44, 0.45, 5)), YEL)
    s += spec(-14, -26, 10, 16, 30, 0.8)
    return s


def arrow_up(col=GRN):
    return cel(P([(0, -100), (74, -18), (30, -18), (30, 92), (-30, 92), (-30, -18), (-74, -18)]), col) + spec(-20, -12, 10, 70, 0, 0.6)


def magnet(col=RED):
    d = "M-88,-88 L-88,-5 A88,88 0 0 0 88,-5 L88,-88 L40,-88 L40,-5 A40,40 0 0 1 -40,-5 L-40,-88 Z"
    s = cel(d, col)
    s += cel(R(-88, -92, 48, 32, 4), "#D9DEE6", so=6, ho=5) + cel(R(40, -92, 48, 32, 4), "#D9DEE6", so=6, ho=5)
    s += spec(-78, -50, 10, 50, 0, 0.6)
    return s


def magnet_fx():
    s = ""
    for x in (-64, 64):
        for i, r in enumerate((26, 46)):
            s += ln(f"M{x - r},{-112 - i * 4} Q{x},{-130 - r} {x + r},{-112 - i * 4}", CYA, 7)
    return s


def sneaker(col=ORA):
    s = ""
    for y, l in ((-34, 54), (0, 70), (34, 46)):
        s += ln(f"M-150,{y} L{-150 + l},{y}", "#BFF6FF", 9)
    s += cel("M-96,40 L-92,-40 Q-90,-58 -72,-58 L-30,-58 Q-18,-58 -12,-46 L10,-10 Q20,0 40,4 L92,16 Q110,20 108,40 Z", col)
    s += cel("M-60,-6 L-20,-6 L20,28 L60,20 L-56,30 Z", YEL, so=5, ho=4)
    s += cel("M-104,38 L104,38 Q114,38 112,54 L108,66 Q106,72 96,72 L-96,72 Q-106,72 -106,62 L-106,46 Q-106,38 -104,38 Z", WHT, dark=0.75)
    for i in range(3):
        s += ln(f"M{-24 + i * 14},{-38 + i * 12} L{-4 + i * 14},{-46 + i * 12}", WHT, 5)
    s += spec(-86, -48, 10, 40, 0, 0.6)
    return s


def sack(col="#C98B4A", mark="+"):
    s = cel("M-30,-62 Q-74,-40 -88,10 Q-100,92 0,94 Q100,92 88,10 Q74,-40 30,-62 Z", col)
    s += cel("M-30,-72 L-56,-110 L-12,-92 L0,-114 L12,-92 L56,-110 L30,-72 Z", shade(col, 1.05), so=6)
    s += cel(R(-38, -80, 76, 20, 9), "#6B3E1E", so=6, ho=5)
    s += spec(-64, -10, 12, 56, 12, 0.5)
    if mark:
        s += cel(E(46, 50, 30), GRN, so=6, ho=5) + txt(mark, 46, 50, 56, WHT, sw=SW * 0.6 / LS[-1][1], skew=0)
    return s


def crown(col=GOLD, gem=RED):
    s = cel(P([(-92, 40), (-104, -58), (-50, -12), (0, -88), (50, -12), (104, -58), (92, 40)]), col)
    for x, y in ((-104, -58), (0, -88), (104, -58)):
        s += cel(E(x, y, 14), shade(col, 1.1), so=5, ho=4)
    s += cel(R(-96, 26, 192, 40, 10), shade(col, 0.92))
    for x, c in ((-56, CYA), (0, gem), (56, CYA)):
        s += cel(E(x, 46, 11), c, so=5, ho=4)
    s += spec(-70, -8, 10, 30, -18, 0.7)
    return s


def shield_d(s_=1.0):
    return f"M{-82 * s_:.1f},{-92 * s_:.1f} L{82 * s_:.1f},{-92 * s_:.1f} L{82 * s_:.1f},{0:.1f} Q{82 * s_:.1f},{70 * s_:.1f} 0,{110 * s_:.1f} Q{-82 * s_:.1f},{70 * s_:.1f} {-82 * s_:.1f},0 Z"


def shield(col, rim=None):
    rim = rim or shade(col, 0.75)
    return cel(shield_d(), rim) + cel(shield_d(0.78), col, so=7) + spec(-58, -74, 12, 60, 0, 0.55)


def chevron(cy, w=58, t=26, th=22, col=WHT):
    y = cy
    return cel(P([(-w, y + t), (0, y), (w, y + t), (w, y + t + th), (0, y + th), (-w, y + t + th)]), col, so=6, ho=5, dark=0.75)


def wings(col=WHT):
    s = ""
    for sgn in (-1, 1):
        pts_ = [(sgn * 70, -40), (sgn * 150, -86), (sgn * 140, -50), (sgn * 160, -40), (sgn * 140, -10), (sgn * 152, 0), (sgn * 120, 26), (sgn * 70, 30)]
        s += cel(P(pts_), col, dark=0.7)
    return s


def gift(col=RED, rib=YEL):
    s = cel(R(-84, -22, 168, 112, 10), col)
    s += cel(R(-16, -22, 32, 112, 3), rib, so=6, ho=5)
    s += grp("rotate(-24 -32 -70)", lambda: cel(E(-32, -70, 36, 20), rib), rot=-24)
    s += grp("rotate(24 32 -70)", lambda: cel(E(32, -70, 36, 20), rib), rot=24)
    s += cel(R(-98, -56, 196, 42, 10), shade(col, 1.08))
    s += cel(R(-18, -56, 36, 42, 3), rib, so=6, ho=5)
    s += cel(E(0, -64, 16), shade(rib, 0.9), so=5, ho=4)
    s += spec(-86, -48, 50, 9, 0, 0.6)
    return s


def clipboard():
    s = cel(R(-80, -94, 160, 198, 16), "#B9783E")
    s += cel(R(-62, -70, 124, 160, 8), WHT, dark=0.8)
    s += cel(R(-36, -112, 72, 36, 10), "#AEB6C4", so=6, ho=5)
    k = LS[-1][1]
    for i in range(3):
        y = -46 + i * 44
        s += f'<rect x="-48" y="{y}" width="24" height="24" rx="4" fill="#FFFFFF" stroke="{INK}" stroke-width="{5 / k:.2f}"/>'
        s += f'<rect x="-14" y="{y + 7}" width="62" height="10" rx="5" fill="#AEB6C4"/>'
        if i < 2:
            s += ln(f"M-44,{y + 10} L-36,{y + 19} L-20,{y - 6}", GRN, 7)
    return s


def cart(col=ORA, cargo=None):
    s = ln("M-84,-52 L-100,-84 L-130,-84", "#4A505C", 12)
    s += ln("M-62,30 L-72,54 L84,54", "#4A505C", 10)
    if cargo:
        cargo = cargo() if callable(cargo) else cargo
        s += cargo
    s += cel(P([(-86, -54), (98, -54), (78, 32), (-64, 32)]), col)
    k = LS[-1][1]
    s += "".join(f'<path d="M{x},-40 L{x - 4},20" stroke="{shade(col, 0.6)}" stroke-width="{6:.1f}" stroke-linecap="round"/>' for x in (-40, 0, 40))
    s += f'<path d="M-72,-14 L86,-14" stroke="{shade(col, 0.6)}" stroke-width="6"/>'
    for x in (-50, 62):
        s += cel(E(x, 74, 18), "#2A2C34", so=6, ho=5) + f'<circle cx="{x}" cy="74" r="6" fill="#AEB6C4"/>'
    s += spec(-70, -44, 60, 8, 0, 0.6)
    return s


def arc_arrow_pts(r, w, a0, a1, head=26.0):
    outer = arcpts(0, 0, r + w / 2, a0, a1, 20)
    inner = arcpts(0, 0, r - w / 2, a1, a0, 20)
    ha = math.radians(a1)
    tip_a = math.radians(a1 + head)
    hw = w * 1.05
    ho_ = (math.cos(ha) * (r + hw), math.sin(ha) * (r + hw))
    hi_ = (math.cos(ha) * (r - hw), math.sin(ha) * (r - hw))
    tip = (math.cos(tip_a) * r, math.sin(tip_a) * r)
    return outer + [ho_, tip, hi_] + inner


def rebirth(col=CYA, core=True):
    s = ""
    if core:
        s += place(crystal, 0, 0, 0.5, 0)
    s += cel(P(arc_arrow_pts(84, 30, 200, 330)), col)
    s += cel(P(arc_arrow_pts(84, 30, 20, 150)), col)
    return s


def flask(liq=YEL, emblem=None):
    k = LS[-1][1]
    s = cel(R(-24, -84, 48, 60, 6), "#CFE6EE", dark=0.78)
    s += cel(E(0, 30, 74), "#CFE6EE", dark=0.78)
    lc = uid("c")
    adddef(f'<clipPath id="{lc}"><circle cx="0" cy="30" r="64"/></clipPath>')
    s += f'<g clip-path="url(#{lc})"><path d="M-80,6 Q-40,-8 0,6 Q40,20 80,6 L80,120 L-80,120 Z" fill="{liq}"/>'
    s += f'<path d="M-80,60 Q0,130 80,60 L80,120 L-80,120 Z" fill="{shade(liq, 0.7)}"/>'
    s += f'<path d="M-80,6 Q-40,-8 0,6 Q40,20 80,6" fill="none" stroke="{shade(liq, 1.4)}" stroke-width="6"/></g>'
    s += f'<path d="{E(0, 30, 74)}" fill="none" stroke="{INK}" stroke-width="{SW / k:.2f}"/>'
    s += cel(R(-32, -96, 64, 18, 7), "#E8F4F8", so=5, ho=4, dark=0.78)
    s += cel(R(-20, -122, 40, 28, 7), "#9A6334", so=6, ho=5)
    s += f'<circle cx="-30" cy="78" r="7" fill="#FFFFFF" opacity="0.6"/><circle cx="34" cy="62" r="5" fill="#FFFFFF" opacity="0.6"/>'
    s += spec(-56, 0, 14, 44, 20, 0.85) + spec(-18, -76, 8, 34, 0, 0.7)
    if emblem:
        emblem = emblem() if callable(emblem) else emblem
        s += emblem
    return s


def tshirt(col=ORA):
    s = cel("M-40,-92 Q0,-72 40,-92 L98,-62 L78,-12 L56,-22 L56,92 L-56,92 L-56,-22 L-78,-12 L-98,-62 Z", col)
    s += cel("M-56,10 L56,10 L56,36 L-56,36 Z", WHT, so=5, ho=4, dark=0.75)
    s += cel("M-40,-92 Q0,-60 40,-92 Q0,-74 -40,-92 Z", "#2A2C34", so=4, ho=3)
    s += sparkle(78, -92, 18, YEL) + sparkle(-84, 40, 12, YEL)
    s += spec(-46, -54, 10, 50, 0, 0.5)
    return s


def padlock(col=GOLD):
    s = cel("M-48,-10 L-48,-44 A48,48 0 0 1 48,-44 L48,-10 L26,-10 L26,-44 A26,26 0 0 0 -26,-44 L-26,-10 Z", "#AEB6C4")
    s += cel(R(-72, -16, 144, 112, 18), col)
    s += flat(E(0, 26, 14) + " " + P([(-9, 30), (9, 30), (13, 62), (-13, 62)]), INK, line=False)
    s += spec(-60, -6, 40, 9, 0, 0.7)
    return s


def check(col=GRN):
    return cel(P([(-96, -2), (-58, -40), (-22, -6), (58, -88), (98, -50), (-22, 72)]), col)


def cross(col=RED):
    return cel(P([(-92, -56), (-56, -92), (0, -36), (56, -92), (92, -56), (36, 0), (92, 56), (56, 92), (0, 36), (-56, 92), (-92, 56), (-36, 0)]), col)


def arrow_right(col=ORA):
    return cel(P([(-92, -30), (6, -30), (6, -84), (100, 0), (6, 84), (6, 30), (-92, 30)]), col) + spec(-82, -20, 70, 9, 0, 0.6)


def wheel(x, y, r=26):
    return cel(E(x, y, r), "#22242B", so=6, ho=5) + cel(E(x, y, r * 0.46), "#B9C0CC", so=4, ho=3)


def car(col=RED, crushed=False):
    k = LS[-1][1]
    if crushed:
        body = "M-112,8 L-104,-12 L-60,-20 L-40,-40 L-10,-30 L10,-46 L52,-38 L70,-26 L102,-20 L114,-6 L112,24 L-108,26 Z"
        s = wheel(-62, 30) + wheel(70, 34, 22)
        s += cel(body, col)
        s += cel(P([(-34, -32), (-8, -24), (4, -36), (24, -32), (20, -20), (-40, -18)]), "#9FE6FF", so=5, ho=4)
        s += f'<path d="M-20,-28 L-12,-20 M8,-34 L14,-24" stroke="{INK}" stroke-width="{3 / k:.2f}"/>'
        s += f'<path d="M-80,-6 L-60,4 L-70,14 M30,-14 L44,0 L36,10" stroke="{INK}" stroke-width="{4 / k:.2f}" fill="none"/>'
    else:
        body = ("M-112,10 L-106,-14 Q-102,-22 -92,-24 L-52,-28 L-32,-62 Q-26,-70 -14,-70 L46,-70 Q58,-70 66,-60 "
                "L86,-30 L104,-24 Q114,-20 114,-8 L114,22 Q114,30 106,30 L-104,30 Q-112,30 -112,22 Z")
        s = cel(body, col)
        s += cel(P([(-24, -60), (14, -60), (14, -32), (-42, -32)]), "#9FE6FF", so=5, ho=4)
        s += cel(P([(24, -60), (50, -60), (70, -32), (24, -32)]), "#9FE6FF", so=5, ho=4)
        s += f'<path d="M18,-28 L18,22 M-36,-6 L-24,-6 M30,-6 L42,-6" stroke="{INK}" stroke-width="{4 / k:.2f}" stroke-linecap="round"/>'
        s += spec(-12, -58, 18, 8, 0, 0.8)
        s += wheel(-62, 30) + wheel(68, 30)
    s += cel(R(100, -18, 14, 12, 3), YEL, so=4, ho=3) + cel(R(-114, -16, 10, 12, 3), RED, so=4, ho=3)
    s += spec(-96, -18, 70, 7, 0, 0.6)
    return s


def cloud(col="#E6E9EF"):
    d = " ".join([E(-60, -20, 40), E(-8, -44, 54), E(52, -26, 44), E(86, 4, 30), E(-92, 6, 30), R(-100, -10, 196, 46, 23)])
    return blob(d, col, dark=0.78)


def flame_poly(cx, cy, r, tip, n=5, amp=16, seed=2):
    rng = random.Random(seed)
    ang = math.atan2(tip[1] - cy, tip[0] - cx)
    px, py = -math.sin(ang), math.cos(ang)
    L = math.hypot(tip[0] - cx, tip[1] - cy)
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        w = r * (1 - t) ** 0.8
        bx, by = cx + math.cos(ang) * L * t, cy + math.sin(ang) * L * t
        j = amp * (1 if i % 2 else -0.4) * (1 - t) * rng.uniform(0.6, 1.0)
        left.append((bx + px * (w + j), by + py * (w + j)))
        right.append((bx - px * (w + j), by - py * (w + j)))
    back = arcpts(cx, cy, r, math.degrees(ang) + 90, math.degrees(ang) + 270, 10)
    return left + right[::-1] + back[::-1][1:-1]


def meteor():
    s = blob(P(flame_poly(-24, 24, 74, (112, -112), seed=4)), ORA, dark=0.85)
    s += flat(P(flame_poly(-24, 24, 50, (62, -62), amp=10, seed=6)), YEL, line=False)
    rng = random.Random(12)
    rock = [(-24 + math.cos(math.radians(a)) * 62 * rng.uniform(0.85, 1.05), 24 + math.sin(math.radians(a)) * 62 * rng.uniform(0.85, 1.05)) for a in range(0, 360, 40)]
    s += cel(P(rock), "#7A5A4A", dark=0.6)
    for x, y, r in ((-44, 40, 14), (-6, 52, 9), (-14, 10, 11)):
        s += cel(E(x, y, r), shade("#7A5A4A", 0.8), so=-4, ho=-3, line=False)
    s += spec(-60, 0, 10, 30, 20, 0.5)
    return s


def crate(col="#C98B4A", mark="?"):
    k = LS[-1][1]
    x, y, w, h, dp = -84, -50, 150, 140, 40
    a = math.radians(-35)
    ox, oy = math.cos(a) * dp, math.sin(a) * dp
    s = flat(P([(x + w, y), (x + w + ox, y + oy), (x + w + ox, y + h + oy), (x + w, y + h)]), shade(col, 0.66))
    s += flat(P([(x, y), (x + ox, y + oy), (x + w + ox, y + oy), (x + w, y)]), shade(col, 1.3))
    s += cel(R(x, y, w, h, 4), col)
    s += f'<path d="{R(x + 12, y + 12, w - 24, h - 24, 2)}" fill="none" stroke="{shade(col, 0.6)}" stroke-width="10"/>'
    s += f'<path d="M{x + 16},{y + h - 20} L{x + w - 16},{y + 20}" stroke="{shade(col, 0.7)}" stroke-width="16" stroke-linecap="round"/>'
    for cx, cy in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
        s += f'<rect x="{cx - 10}" y="{cy - 10}" width="20" height="20" rx="4" fill="#8D94A3" stroke="{INK}" stroke-width="{4 / k:.2f}"/>'
    if mark:
        s += txt(mark, x + w / 2, y + h / 2, 92, YEL, skew=0)
    return s


def robot_head(col="#5A606E"):
    k = LS[-1][1]
    s = cel(P([(-72, -64), (-110, -120), (-60, -80)]), ORA) + cel(P([(72, -64), (110, -120), (60, -80)]), ORA)
    s += cel(R(-116, -20, 28, 64, 8), shade(col, 0.8)) + cel(R(88, -20, 28, 64, 8), shade(col, 0.8))
    s += cel(R(-92, -80, 184, 166, 32), col)
    s += flat(P([(-74, -30), (74, -30), (64, 18), (-64, 18)]), "#121318")
    s += flat(P([(-62, -20), (-14, -6), (-18, 8), (-58, 4)]), RED, line=False) + flat(P([(62, -20), (14, -6), (18, 8), (58, 4)]), RED, line=False)
    s += '<rect x="-48" y="-8" width="16" height="6" fill="#FFE1E1"/><rect x="32" y="-8" width="16" height="6" fill="#FFE1E1"/>'
    s += cel(R(-54, 36, 108, 32, 6), "#2A2C34", so=5, ho=4)
    s += "".join(f'<rect x="{x}" y="40" width="9" height="24" fill="{shade(col, 1.3)}"/>' for x in range(-42, 50, 18))
    s += "".join(f'<circle cx="{x}" cy="-62" r="6" fill="{shade(col, 1.4)}" stroke="{INK}" stroke-width="{3 / k:.2f}"/>' for x in (-70, 70))
    s += spec(-78, -66, 60, 10, 0, 0.6)
    return s


def vortex(col=PUR):
    s = ""
    for j in range(3):
        a0 = j * 120
        left, right = [], []
        for i in range(17):
            t = i / 16
            a = math.radians(a0 + t * 150)
            r = 26 + t * 86
            w = 26 * (1 - t) + 2
            left.append((math.cos(a) * (r + w), math.sin(a) * (r + w)))
            right.append((math.cos(a) * (r - w * 0.4), math.sin(a) * (r - w * 0.4)))
        s += cel(P(left + right[::-1]), shade(col, 1.0 if j % 2 else 0.85), so=6, ho=5)
    return s


def building(x, y, w, h, col, win=YEL, broken=False, seed=0):
    rng = random.Random(seed)
    k = LS[-1][1]
    if broken:
        top = [(x, y + 20)] + [(x + w * i / 4, y + rng.uniform(0, 34)) for i in range(1, 4)] + [(x + w, y + 10)]
        d = P([(x, y + h)] + top + [(x + w, y + h)])
    else:
        d = R(x, y, w, h, 3)
    s = cel(d, col)
    cols_ = max(1, int((w - 14) // 22))
    rows = int((h - 30) // 26)
    ox = x + (w - cols_ * 22 + 8) / 2
    for r in range(rows):
        for c in range(cols_):
            lit = rng.random() < 0.7
            s += f'<rect x="{ox + c * 22:.1f}" y="{y + 26 + r * 26 + (14 if broken else 0):.1f}" width="14" height="16" fill="{win if lit else shade(col, 0.6)}"/>'
    return s


def skyline_scene(broken=False, cols=("#5A6070", "#6B7282", "#4A505C"), win=YEL):
    s = building(-104, -30, 66, 130, cols[0], win, broken, 1)
    s += building(36, -50, 70, 150, cols[2], win, broken, 2)
    s += building(-46, -104, 90, 204, cols[1], win, broken, 3)
    if not broken:
        s += cel(R(-8, -134, 14, 32, 2), cols[1], so=5, ho=4)
    return s


def factory():
    k = LS[-1][1]
    s = cel(R(28, -110, 30, 120, 4), "#7A3A3A") + cel(R(66, -84, 26, 90, 4), "#7A3A3A")
    s += "".join(f'<rect x="{x}" y="{y}" width="{w}" height="10" fill="{WHT}" opacity="0.85"/>' for x, y, w in ((28, -96, 30), (66, -72, 26)))
    s += cel(P([(-110, 100), (-110, -10), (-70, -44), (-70, -10), (-30, -44), (-30, -10), (10, -44), (10, -10), (110, -10), (110, 100)]), "#B04A3A")
    s += "".join(f'<rect x="{x}" y="14" width="26" height="22" fill="{YEL}" stroke="{INK}" stroke-width="{4 / k:.2f}"/>' for x in (-92, -52, -12, 28, 68))
    s += cel(R(-30, 52, 60, 48, 3), "#2A2C34", so=5, ho=4)
    s += blob(E(44, -128, 20) + " " + E(64, -142, 16) + " " + E(80, -104, 14), "#C9CDD6", dark=0.75)
    return s


def tank(col="#6E8F3A"):
    k = LS[-1][1]
    s = ln("M10,-46 L118,-70", "#4A5E28", 16, cap="butt")
    s += cel(R(-110, 20, 220, 56, 28), "#2A2C34")
    for x in range(-80, 100, 40):
        s += cel(E(x, 48, 15), "#6B7280", so=4, ho=3)
    s += cel(P([(-118, 22), (118, 22), (98, -10), (-100, -10)]), col)
    s += cel("M-62,-10 L-50,-58 Q-40,-76 0,-76 Q40,-76 50,-58 L62,-10 Z", shade(col, 1.08))
    s += flat(P(star_pts(0, -40, 20, 0.42)), WHT, sw=SW * 0.6)
    s += spec(-46, -64, 40, 8, 0, 0.6)
    return s


def future_city():
    k = LS[-1][1]
    s = cel(P([(52, 100), (60, -30), (84, -60), (100, -30), (104, 100)]), "#3A6E86")
    s += cel(P([(-104, 100), (-98, -10), (-80, -36), (-62, -10), (-56, 100)]), "#3A6E86")
    s += cel(P([(-36, 100), (-30, -100), (0, -128), (30, -100), (36, 100)]), "#4F8AA6")
    for x, y0, y1 in ((0, -96, 92), (78, -34, 92), (-80, -16, 92)):
        s += f'<path d="M{x},{y0} L{x},{y1}" stroke="{CYA}" stroke-width="7" stroke-linecap="round"/>'
    s += cel(E(0, -54, 76, 16) + " " + E(0, -54, 40, 7), "#BFF6FF", rule="evenodd", so=5, ho=4)
    s += sparkle(-96, -80, 14, CYA) + sparkle(100, -100, 12, CYA)
    return s


def junk_pile():
    rng = random.Random(21)
    s = cel(P([(-118, 96), (-86, 20), (-40, -6), (20, -14), (78, 10), (118, 96)]), "#6B6460")
    for i in range(7):
        x, y = rng.uniform(-90, 90), rng.uniform(30, 86)
        s += cel(P(quad_chunk(x, y, rng.uniform(14, 24), rng)), rng.choice(["#8D94A3", "#A86A3A", "#5A606E"]), so=5, ho=4)
    s += place(car, 0, -40, 0.62, -12, col="#C0582E", crushed=True)
    s += cel(E(-82, 50, 30) + " " + E(-82, 50, 13), "#2A2C34", rule="evenodd", so=6, ho=5)
    s += place(gear, 84, 46, 0.3, 0, col="#9AA3B5")
    return s


def trefoil(r=60):
    d = ""
    for a in (-90, 30, 150):
        pts_ = arcpts(0, 0, r, a - 30, a + 30, 8) + arcpts(0, 0, r * 0.3, a + 30, a - 30, 4)
        d += P(pts_) + " "
    d += E(0, 0, r * 0.2)
    return d


def radiation_sign():
    return cel(E(0, 0, 80), YEL) + flat(trefoil(64), INK, line=False)


def mushroom():
    s = blob(R(-30, -20, 60, 120, 20) + " " + E(0, 100, 74, 22), "#E2662A", dark=0.75)
    s += blob(" ".join([E(-56, -46, 44), E(0, -72, 58), E(56, -46, 44), E(-30, -10, 38), E(30, -10, 38), E(-84, -12, 26), E(84, -12, 26)]), ORA, dark=0.75)
    s += f'<path d="{E(0, -70, 34, 22)}" fill="{YEL}"/><path d="{E(-50, -40, 20, 14)}" fill="{YEL}"/>'
    s += spec(-70, -70, 30, 10, -30, 0.6)
    return s


def gauge(col=RED):
    k = LS[-1][1]
    s = cel("M-100,40 A100,100 0 0 1 100,40 Z", "#2A2C34")
    for a0, a1, c in ((180, 240, GRN), (240, 300, YEL), (300, 360, RED)):
        s += f'<path d="{P(arcpts(0, 40, 88, a0, a1, 10) + arcpts(0, 40, 62, a1, a0, 10))}" fill="{c}"/>'
    s += f'<path d="M-100,40 A100,100 0 0 1 100,40 Z" fill="none" stroke="{INK}" stroke-width="{SW / k:.2f}" stroke-linejoin="round"/>'
    s += cel(P(rotp([(-8, 40), (0, -50), (8, 40)], 52, 0, 40)), WHT, so=4, ho=3, dark=0.75)
    s += cel(E(0, 40, 16), "#AEB6C4", so=5, ho=4)
    s += cel(R(-60, 56, 120, 34, 10), "#2A2C34", so=5, ho=4) + txt("MAX", 0, 73, 28, RED, sw=0, skew=0)
    return s


def toolbox(col=RED):
    s = place(hammer, -30, -46, 0.5, -20)
    s += place(wrench, 40, -50, 0.5, 18)
    s += cel("M-40,-40 L-40,-62 Q-40,-72 -30,-72 L30,-72 Q40,-72 40,-62 L40,-40 L28,-40 L28,-60 L-28,-60 L-28,-40 Z", "#2A2C34")
    s += cel(R(-100, -40, 200, 130, 12), col)
    s += cel(R(-100, -40, 200, 34, 10), shade(col, 1.1), so=6)
    s += cel(R(-20, -20, 40, 22, 4), "#AEB6C4", so=5, ho=4)
    s += spec(-88, -34, 60, 8, 0, 0.6)
    return s


def cracked_block(col="#8D94A3"):
    k = LS[-1][1]
    s = cel(R(-80, -40, 160, 120, 8), col)
    s += f'<path d="M-6,-40 L8,-6 L-14,20 L6,50 L-4,80 M8,-6 L44,10 L60,-2 M-14,20 L-52,30" fill="none" stroke="{INK}" stroke-width="{7 / k:.2f}" stroke-linejoin="round" stroke-linecap="round"/>'
    return s


def golden_hall(col=GOLD):
    k = LS[-1][1]
    s = cel(P([(-112, -18), (0, -78), (112, -18)]), col)
    s += cel(R(-104, 76, 208, 24, 4), shade(col, 0.9))
    for x in (-84, -40, 4, 48):
        s += cel(R(x, -14, 30, 90, 4), shade(col, 1.08), so=6, ho=5)
    s += cel(R(-112, -22, 224, 16, 3), shade(col, 0.85), so=5, ho=4)
    s += place(crown, 0, -104, 0.5, 0)
    return s


def starter_box():
    s = place(hammer, -36, -60, 0.48, -24)
    s += place(coin, 48, -74, 0.36, 0)
    s += place(coin, 18, -46, 0.3, 0)
    s += cel(R(-96, -30, 192, 120, 10), ORA)
    s += cel(P([(-96, -30), (-122, -66), (-30, -66), (-10, -30)]), shade(ORA, 1.15), so=6)
    s += cel(P([(96, -30), (122, -66), (30, -66), (10, -30)]), shade(ORA, 0.9), so=6)
    s += cel(R(-14, -30, 28, 120, 3), YEL, so=5, ho=4)
    s += flat(P(star_pts(0, 30, 34, 0.45)), WHT, sw=SW * 0.7)
    return s


def star(col=YEL):
    return cel(P(star_pts(0, 0, 100, 0.45)), col) + spec(-30, -50, 10, 30, 30, 0.7)


def crossed_hammers():
    return place(hammer, 0, 10, 0.72, -35, head=GOLD, band=ORA) + place(hammer, 0, 10, 0.72, 35, head=GOLD, band=ORA)


def alloy_plate():
    s = cel(R(-94, -6, 188, 66, 12), "#8E98A8", so=8)
    s += cel(R(-80, -54, 160, 62, 12), "#C3CBD6", so=8)
    for x in (-60, 60):
        s += flat(E(x, -34, 8), "#5E6573")
        s += flat(E(x, 26, 8), "#5E6573")
    return s + spec(-62, -46, 46, 9, 0, 0.75)


def copper_wire():
    s = ""
    for i in range(4):
        y = -48 + i * 24
        s += cel(E(0, y, 72, 26) + " " + E(0, y, 52, 14), shade("#E8823F", 1.0 - i * 0.06), rule="evenodd", so=5)
    s += ln("M60,30 Q104,50 94,98", "#E8823F", 13)
    return s + spec(-50, -66, 34, 8, -8, 0.7)


def circuit_board():
    s = cel(R(-94, -74, 188, 148, 14), "#3FAE6A", so=8)
    for d in ("M-70,-40 H-10 V-10 H40", "M-70,40 H0 V10", "M70,-50 V-10 H40", "M70,50 H20 V30"):
        s += ln(d, "#C9F7D6", 6, outline=False)
    s += cel(R(-44, -34, 54, 44, 6), "#2A2C34", so=4)
    s += cel(R(16, 10, 46, 36, 6), "#2A2C34", so=4)
    for x, y in ((-70, -40), (-70, 40), (70, -50), (70, 50)):
        s += flat(E(x, y, 9), GOLD)
    return s


def plasma_cell():
    s = cel(R(-48, -86, 96, 172, 26), "#3A3F4B", so=8)
    s += cel(R(-32, -62, 64, 124, 16), CYA, so=6)
    s += cel(R(-30, -104, 60, 22, 6), STEEL, so=4) + cel(R(-30, 82, 60, 22, 6), STEEL, so=4)
    return s + place(lightning, 0, 0, 0.42, col=WHT) + spec(-24, -54, 10, 60, 0, 0.6)


def colossus_plating():
    s = cel(R(-92, -82, 184, 164, 20), "#C4703C", so=8)
    s += place(gear, 0, 0, 0.56, col=ORA)
    for x in (-70, 70):
        for y in (-62, 62):
            s += flat(E(x, y, 8), "#5E4434")
    return s + spec(-70, -70, 40, 9, 0, 0.6)


def crusher_hydraulics():
    s = cel(R(-46, -94, 92, 118, 14), YEL, so=8)
    s += cel(R(-60, -104, 120, 22, 8), DARKM, so=4)
    s += cel(R(-15, 18, 30, 74, 8), "#D9DCE3", so=5)
    s += cel(R(-58, 84, 116, 22, 8), DARKM, so=4)
    for y in (-60, -30):
        s += flat(R(-46, y, 92, 10, 0), "#2A2C34", line=False)
    return s + spec(-34, -84, 12, 56, 0, 0.7)


def industrial_core():
    s = aura(0, 0, 96, ORA, 0.8)
    s += cel(E(0, 0, 60), ORA, so=8)
    s += flat(E(0, 0, 30), "#FFE3A0", line=False)
    for a in range(0, 180, 45):
        x, y = math.cos(math.radians(a)) * 74, math.sin(math.radians(a)) * 74
        s += ln(f"M{-x:.1f},{-y:.1f} L{x:.1f},{y:.1f}", DARKM, 9)
    return s + spec(-34, -40, 22, 9, -35, 0.8)


def warden_armor():
    s = shield(OLV)
    return s + flat(P(star_pts(0, 6, 40, 0.45)), YEL)


def overlord_heart():
    s = aura(0, 0, 110, "#FF3BA0", 0.85)
    return s + place(crystal, 0, 0, 0.9, col="#FF3BA0") + sparkle(70, -76, 16, ORA) + sparkle(-74, 64, 12, PUR)


def S(fn, x=128, y=128, k=1.0, a=0.0, **kw):
    return lambda: ("", place(fn, x, y, k, a, **kw))


def A(x, y, r, col, op=0.8):
    return lambda: (aura(x, y, r, col, op), "")


def SP(x, y, r, col="#FFFFFF"):
    return lambda: ("", sparkle(x, y, r, col))


def LN(d, col, w):
    return lambda: ("", ln(d, col, w))


def TX(s, x, y, size, fill):
    return lambda: ("", txt(s, x, y, size, fill))


def FX(kind, x, y, k):
    return lambda: place2(blaster_fx, x, y, k, 0, kind=kind)


def M(*parts):
    def f():
        b = m = ""
        for p in parts:
            pb, pm = p()
            b += pb
            m += pm
        return b, m
    return f


def sil_filter(fid, sd, dy, op=0.45):
    return (f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">'
            f'<feGaussianBlur in="SourceAlpha" stdDeviation="{sd:.2f}"/>'
            f'<feComponentTransfer result="o"><feFuncA type="linear" slope="9" intercept="-0.25"/></feComponentTransfer>'
            f'<feFlood flood-color="{INK}"/><feComposite in2="o" operator="in" result="ol"/>'
            f'<feOffset in="o" dx="{dy * 0.4:.2f}" dy="{dy:.2f}" result="so"/><feGaussianBlur in="so" stdDeviation="{sd * 1.3:.2f}" result="sb"/>'
            f'<feFlood flood-color="#000000" flood-opacity="{op}"/><feComposite in2="sb" operator="in" result="sh"/>'
            f'<feMerge><feMergeNode in="sh"/><feMergeNode in="ol"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<defs>{"".join(G["defs"])}</defs>{body}</svg>')


def subject(build, cx, cy, k, sd, dy):
    b, m = build()
    tf = f"translate({cx:.1f} {cy:.1f}) scale({k:.3f}) translate(-128 -128)"
    fid = uid("f")
    adddef(sil_filter(fid, sd, dy))
    return f'<g transform="{tf}">{b}</g><g filter="url(#{fid})"><g transform="{tf}">{m}</g></g>'


def label_svg(text, cx, by, maxw, size):
    size = min(size, maxw / max(1.0, text_width(text, 1.0)))
    gid = uid("g")
    adddef(lin_grad(gid, [(0, "#FFFFFF"), (0.45, "#FFF6C8"), (0.5, YEL), (1, ORA)], user=(0, by - CAP * size, 0, by)))
    cy = by - CAP * size / 2
    t = f'<text x="{cx:.1f}" y="{by:.1f}" text-anchor="middle" font-family="{FONT}" font-size="{size:.1f}" stroke-linejoin="round" paint-order="stroke"'
    return (f'<g transform="translate(0 {cy:.1f}) skewX({SK}) translate(0 {-cy:.1f})">'
            f'{t} fill="#000" stroke="#000" stroke-width="{size * 0.24:.1f}" opacity="0.55" transform="translate(4 8)">{text}</text>'
            f'{t} fill="{INK}" stroke="{INK}" stroke-width="{size * 0.2:.1f}">{text}</text>'
            f'{t} fill="url(#{gid})">{text}</text></g>')


def tile_svg(accent, build, label=None, seed=0):
    x0, sz, r = 20, 472, 104
    cy = 232 if label else 252
    bg, cp, hz, gl = uid("g"), uid("c"), uid("p"), uid("g")
    adddef(lin_grad(bg, [(0, "#30333F"), (0.5, "#1B1C24"), (1, "#0E0F13")]))
    adddef(f'<clipPath id="{cp}"><path d="{R(x0, x0, sz, sz, r)}"/></clipPath>')
    adddef(f'<pattern id="{hz}" width="56" height="56" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="22" height="56" fill="#FFFFFF"/></pattern>')
    adddef(rad_grad(gl, [(0, accent, 0.6), (0.55, accent, 0.16), (1, accent, 0)]))
    rng = random.Random(seed)
    b1 = burst_points(256, cy, 14, 250, 250, rng, inner=(0.5, 0.62), outer=(0.95, 1.08))
    b2 = burst_points(256, cy, 11, 175, 175, rng, inner=(0.55, 0.66), outer=(0.9, 1.0))
    s = f'<path d="{R(x0, x0, sz, sz, r)}" fill="url(#{bg})"/>'
    s += (f'<g clip-path="url(#{cp})"><rect width="512" height="512" fill="url(#{hz})" opacity="0.045"/>'
          f'<circle cx="256" cy="{cy}" r="270" fill="url(#{gl})"/>'
          f'<path d="{P(b1)}" fill="{accent}" opacity="0.13"/><path d="{P(b2)}" fill="{accent}" opacity="0.14"/>'
          f'<ellipse cx="256" cy="20" rx="320" ry="150" fill="#FFFFFF" opacity="0.06"/>'
          f'<rect y="420" width="512" height="92" fill="#000000" opacity="0.22"/></g>')
    s += f'<path d="{R(x0 + 13, x0 + 13, sz - 26, sz - 26, r - 13)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.13" stroke-width="3"/>'
    s += subject(build, 256, cy, 1.32 if label else 1.5, 2.6, 7)
    s += f'<path d="{R(x0, x0, sz, sz, r)}" fill="none" stroke="{INK}" stroke-width="24"/>'
    s += f'<path d="{R(x0, x0, sz, sz, r)}" fill="none" stroke="{accent}" stroke-width="12"/>'
    s += f'<path d="{R(x0 + 2, x0 + 2, sz - 4, sz - 4, r - 2)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="2"/>'
    if label:
        s += label_svg(label, 256, 468, 400, 112)
    return svg_doc(512, 512, s)


def glyph_svg(build, W=256):
    k = 0.92 * W / 256
    return svg_doc(W, W, subject(build, W / 2, W / 2, k, 1.4 * W / 256, 3.5 * W / 256))


METALS = {
    "bronze": [(0, "#FFD9B0"), (0.35, "#D98B4A"), (0.65, "#8A4F22"), (1, "#F0B07A")],
    "silver": [(0, "#FFFFFF"), (0.35, "#C9D1DC"), (0.65, "#7E8796"), (1, "#E6EBF2")],
    "gold": [(0, "#FFF3B0"), (0.35, "#FFC428"), (0.65, "#B87A0A"), (1, "#FFE27A")],
    "chaos": [(0, "#F0DCFF"), (0.35, "#A64DFF"), (0.65, "#4E1A8E"), (1, "#D6A6FF")],
    "legend": [(0, "#FFFFFF"), (0.25, "#FFE27A"), (0.5, "#FF9A1F"), (0.75, "#B85A0A"), (1, "#FFE27A")],
}


def medal_svg(metal, accent, build, label=None):
    mg, dg, cp, gl = uid("g"), uid("g"), uid("c"), uid("g")
    stops = METALS[metal]
    adddef(lin_grad(mg, stops, 0, 0, 1, 1))
    adddef(rad_grad(dg, [(0, "#30333F"), (1, "#0E0F13")]))
    adddef(f'<clipPath id="{cp}"><circle cx="256" cy="256" r="184"/></clipPath>')
    adddef(rad_grad(gl, [(0, accent, 0.65), (0.6, accent, 0.15), (1, accent, 0)]))
    rng = random.Random(len(label or "x") * 7 + len(metal))
    s = '<circle cx="256" cy="256" r="228" fill="#0A0A0D"/>'
    s += f'<circle cx="256" cy="256" r="220" fill="url(#{mg})"/>'
    s += f'<path d="M{256 - 206},{256} A206,206 0 0 1 {256 + 146},{256 - 146}" fill="none" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="6" stroke-linecap="round"/>'
    mid = stops[1][1]
    for i in range(16):
        a = math.radians(i * 22.5 + 11.25)
        s += f'<circle cx="{256 + math.cos(a) * 204:.1f}" cy="{256 + math.sin(a) * 204:.1f}" r="6.5" fill="{shade(mid, 1.35)}" stroke="#0A0A0D" stroke-width="3"/>'
    s += '<circle cx="256" cy="256" r="191" fill="#0A0A0D"/>'
    s += f'<circle cx="256" cy="256" r="184" fill="url(#{dg})"/>'
    bp = burst_points(256, 250, 12, 200, 200, rng, inner=(0.5, 0.62), outer=(0.95, 1.05))
    s += f'<g clip-path="url(#{cp})"><circle cx="256" cy="250" r="200" fill="url(#{gl})"/><path d="{P(bp)}" fill="{accent}" opacity="0.15"/></g>'
    s += '<circle cx="256" cy="256" r="181" fill="none" stroke="#FFFFFF" stroke-opacity="0.12" stroke-width="3"/>'
    s += subject(build, 256, 232 if label else 250, 1.08 if label else 1.22, 2.6, 7)
    if label:
        rib = accent
        for sg in (-1, 1):
            tail = [(256 + sg * 100, 370), (256 + sg * 144, 372), (256 + sg * 128, 394), (256 + sg * 144, 416), (256 + sg * 100, 412)]
            s += f'<path d="{P(tail)}" fill="{shade(rib, 0.6)}" stroke="#0A0A0D" stroke-width="7" stroke-linejoin="round"/>'
        s += f'<path d="{P([(146, 356), (366, 356), (372, 406), (140, 406)])}" fill="{rib}" stroke="#0A0A0D" stroke-width="8" stroke-linejoin="round"/>'
        s += f'<path d="{P([(150, 362), (362, 362), (363, 372), (149, 372)])}" fill="#FFFFFF" opacity="0.3"/>'
        s += label_svg(label, 256, 400, 190, 52)
    return svg_doc(512, 512, s)


def F_(kind, cx, cy, kb, mx, my, km, acc):
    return M(S(blaster, cx, cy, kb, -14, kind=kind), FX(kind, mx, my, km))


def flask_i(liq, emb, ek=0.32):
    return S(flask, 128, 136, 0.92, liq=liq, emblem=lambda: place(emb[0], 0, 40, ek, 0, **emb[1]))


def wreck_hit(head=STEEL, k=0.7, white=False):
    hk = dict(head=head, white=white)
    if white:
        hk.update(handle="#E6E9EF", grip="#C9CED8")
    return S(hammer, 104 + 52 * k / 0.7, 140 - 52 * k / 0.7, k, -135, **hk)


B = "badge"
GL = "glyph"
MD = "medal"
WR_CASH = M(S(bill_stack, 112, 112, 0.78, -10), S(coin, 178, 180, 0.42))

ICON_TABLE = [
    ("Cash", "currency", GL, None, WR_CASH, None),
    ("Scrap", "currency", GL, None, M(A(128, 128, 110, CYA, 0.35), S(scrap_chunk, 128, 132, 0.95)), None),
    ("ChaosCore", "currency", GL, None, M(A(128, 128, 118, PUR, 0.85), S(crystal, 128, 128, 1.04), SP(196, 60, 16), SP(60, 190, 12)), None),

    ("ZoneScrapYard", "zones", B, ORA, S(junk_pile, 128, 132, 1.0), None),
    ("ZoneDowntown", "zones", B, YEL, M(A(128, 100, 100, YEL, 0.35), S(skyline_scene, 128, 132, 1.0)), None),
    ("ZoneIndustrial", "zones", B, RED, S(factory, 128, 140, 0.95), None),
    ("ZoneMilitary", "zones", B, OLV, S(tank, 128, 140, 0.95), None),
    ("ZoneFuture", "zones", B, CYA, M(A(128, 110, 110, CYA, 0.5), S(future_city, 128, 138, 0.92)), None),
    ("ZoneChaosCore", "zones", B, PUR, M(A(128, 120, 115, PUR, 0.9), S(vortex, 128, 124, 1.0), S(crystal, 128, 120, 0.6)), None),
    ("ZoneVIP", "zones", B, GOLD, M(A(128, 120, 110, GOLD, 0.6), S(golden_hall, 128, 150, 0.92), SP(46, 70, 14), SP(212, 92, 12)), None),

    ("ToolScrapHammer", "tools", B, "#9AA3B5", S(hammer, 128, 134, 0.9, 35, head="#7C8494", rust=True), None),
    ("ToolPowerHammer", "tools", B, ORA, M(A(186, 70, 60, ORA, 0.8), S(hammer, 128, 136, 0.86, 35, head=DARKM, handle="#2A2C34", hw=150, hh=80, band=ORA, grip=ORA, glowface=YEL), SP(222, 112, 14, YEL), SP(204, 40, 10, YEL)), None),
    ("ToolJackhammer", "tools", B, YEL, M(S(burst, 148, 218, 0.34), S(jackhammer, 128, 110, 0.86, -10)), None),
    ("ToolTNTLauncher", "tools", B, RED, S(tnt_launcher, 118, 140, 0.72, -22), None),
    ("ToolRocketRig", "tools", B, "#E8EBF0", S(rocket, 132, 120, 0.8, 40), None),
    ("ToolPlasmaCannon", "tools", B, CYA, F_("plasma", 116, 138, 0.74, 204, 112, 0.7, CYA), None),
    ("ToolChaosRay", "tools", B, PUR, F_("chaos", 110, 140, 0.72, 214, 112, 0.6, PUR), None),
    ("ToolVoidBlaster", "tools", B, "#7A3CFF", F_("void", 112, 140, 0.74, 204, 114, 0.75, "#7A3CFF"), None),
    ("ToolOwnerHammer", "tools", B, GOLD, M(A(176, 76, 76, RED, 0.9), S(hammer, 128, 136, 0.9, 35, head="#17151D", handle="#17151D", hw=160, hh=86, band=GOLD, grip=RED, glowface=RED), SP(222, 108, 16, GOLD), SP(200, 36, 12, GOLD), SP(48, 200, 10, RED)), None),

    ("StatDamage", "stats", GL, None, M(S(burst, 128, 124, 1.0, cols=(RED, ORA, YEL)), S(fist, 128, 140, 0.76)), None),
    ("StatAttackSpeed", "stats", GL, None, M(LN("M20,92 L66,92", "#FFF3B0", 9), LN("M12,128 L58,128", "#FFF3B0", 9), LN("M24,164 L60,164", "#FFF3B0", 9), S(lightning, 140, 128, 1.0, 8)), None),
    ("StatCrit", "stats", GL, None, S(crosshair, 128, 128, 1.0), None),
    ("StatExplosion", "stats", GL, None, S(explosion_glyph, 128, 128, 0.9), None),
    ("StatCash", "stats", GL, None, M(S(coin, 112, 144, 0.8), S(arrow_up, 192, 84, 0.52)), None),
    ("StatScrap", "stats", GL, None, M(S(bolt, 104, 124, 0.9, 25), S(arrow_up, 194, 88, 0.52)), None),
    ("StatMagnet", "stats", GL, None, M(S(magnet_fx, 128, 150, 0.82), S(magnet, 128, 150, 0.82)), None),
    ("StatSpeed", "stats", GL, None, S(sneaker, 144, 128, 0.82), None),
    ("StatCapacity", "stats", GL, None, S(sack, 128, 128, 0.95), None),

    ("PassDoubleCash", "gamepasses", B, YEL, M(S(bill_stack, 116, 116, 0.74, -8), S(coin, 182, 170, 0.42), S(coin, 66, 178, 0.3)), "2X"),
    ("PassDoubleDamage", "gamepasses", B, RED, M(S(burst, 128, 124, 1.0, cols=(RED, ORA, YEL)), S(fist, 128, 140, 0.76)), "2X"),
    ("PassAutoScrap", "gamepasses", B, CYA, M(S(rebirth, 128, 128, 1.0, core=False), S(gear, 128, 128, 0.46, col="#78B4C6")), "AUTO"),
    ("PassMegaMagnet", "gamepasses", B, PUR, M(S(magnet_fx, 128, 150, 0.82), S(magnet, 128, 150, 0.82)), "5X"),
    ("PassVIP", "gamepasses", B, GOLD, M(A(128, 128, 110, GOLD, 0.6), S(crown, 128, 136, 1.0), SP(40, 60, 14), SP(220, 70, 12)), "VIP"),
    ("PassExtraLoadout", "gamepasses", B, ORA, S(tools_cross, 128, 128, 1.0), "+3"),
    ("PassFastAttack", "gamepasses", B, ORA, M(S(hammer, 116, 140, 0.8, 35, band=YEL), S(lightning, 186, 92, 0.52, 12)), "FAST"),
    ("PassVoidBlaster", "gamepasses", B, "#7A3CFF", F_("void", 112, 140, 0.74, 204, 114, 0.75, "#7A3CFF"), None),

    ("ProductCashSmall", "products", B, YEL, M(S(cash_pile, 124, 128, 1.0, n=1), S(coin, 186, 180, 0.36)), None),
    ("ProductCashMedium", "products", B, YEL, M(S(cash_pile, 128, 124, 1.0, n=2), S(coin, 70, 190, 0.32), S(coin, 194, 196, 0.34)), None),
    ("ProductCashLarge", "products", B, YEL, M(S(cash_pile, 128, 126, 1.0, n=3), S(coin, 46, 196, 0.3), S(coin, 210, 196, 0.32), S(coin, 128, 206, 0.3)), None),
    ("ProductCashMega", "products", B, GOLD, M(A(128, 128, 120, GOLD, 0.6), S(cash_pile, 128, 124, 1.0, n=4), S(coin, 40, 196, 0.3), S(coin, 216, 196, 0.32), SP(40, 54, 14), SP(220, 50, 16)), "MEGA"),
    ("ProductBoostCash", "products", B, YEL, flask_i(YEL, (coin, {})), "2X"),
    ("ProductBoostDamage", "products", B, RED, flask_i(RED, (fist, {}), 0.34), "2X"),
    ("ProductBoostCash3", "products", B, ORA, M(flask_i(YEL, (coin, {})), S(coin, 200, 80, 0.3), S(coin, 56, 90, 0.24)), "3X"),
    ("ProductRebirth", "products", B, CYA, M(A(128, 128, 90, PUR, 0.7), S(rebirth, 128, 128, 1.0)), None),
    ("ProductChaosBoost", "products", B, PUR, M(A(128, 150, 100, PUR, 0.6), flask_i(PUR, (crystal, {}), 0.34)), None),
    ("ProductMegaChaos", "products", B, PUR, M(A(128, 128, 120, PUR, 0.9), S(vortex, 128, 128, 1.05), S(crystal, 128, 124, 0.66), S(lightning, 60, 70, 0.32, -20), S(lightning, 198, 186, 0.3, 20)), "MEGA"),
    ("ProductNuclear", "products", B, "#9BE22D", M(A(128, 100, 110, ORA, 0.5), S(mushroom, 118, 120, 0.95), S(radiation_sign, 190, 186, 0.42)), "NUKE"),
    ("ProductStarterPack", "products", B, ORA, S(starter_box, 128, 140, 0.95), "STARTER"),

    ("BoostCash", "boosts", GL, None, flask_i(YEL, (coin, {})), None),
    ("BoostDamage", "boosts", GL, None, flask_i(RED, (fist, {}), 0.34), None),
    ("BoostScrap", "boosts", GL, None, flask_i(CYA, (gear, {"col": "#9AC6D4"}), 0.34), None),
    ("BoostChaos", "boosts", GL, None, flask_i(PUR, (crystal, {}), 0.34), None),

    ("EventChaos", "events", B, PUR, M(A(128, 128, 120, PUR, 0.9), S(vortex, 128, 128, 1.05), S(crystal, 128, 128, 0.52), S(lightning, 54, 70, 0.3, -25), S(lightning, 204, 186, 0.3, 25)), None),
    ("EventTotalWreck", "events", B, RED, M(S(burst, 128, 112, 1.05), S(car, 128, 158, 0.9, -8, col=RED, crushed=True)), None),
    ("EventGoldenCar", "events", B, GOLD, M(A(128, 128, 120, GOLD, 0.6), S(car, 128, 144, 0.95, -4, col=GOLD), SP(50, 74, 16), SP(206, 64, 12), SP(220, 196, 10)), None),
    ("EventCashRain", "events", B, YEL, M(S(bill_stack, 66, 172, 0.32, -25, n=1), S(bill_stack, 182, 196, 0.3, 20, n=1), S(coin, 124, 200, 0.24), S(coin, 206, 140, 0.2), S(coin, 46, 120, 0.18), S(coin, 120, 150, 0.2), S(cloud, 128, 84, 0.82)), None),
    ("EventMeteor", "events", B, ORA, S(meteor, 128, 128, 1.0), None),
    ("EventGiantCrate", "events", B, "#C98B4A", S(crate, 132, 138, 1.0), None),
    ("EventBoss", "events", B, RED, M(A(128, 128, 110, RED, 0.6), S(robot_head, 128, 138, 0.95)), None),

    ("TitleNewbie", "titles", GL, None, M(S(shield, 128, 124, 0.95, col="#9AA3B5"), S(chevron, 128, 124, 0.95, cy=-14)), None),
    ("TitleScrapRat", "titles", GL, None, M(S(shield, 128, 124, 0.95, col="#4F8AA6"), S(gear, 128, 112, 0.36, col="#BFE3EE"), S(chevron, 128, 124, 0.95, cy=34, w=46, t=20, th=16)), None),
    ("TitleDemolisher", "titles", GL, None, M(S(shield, 128, 124, 0.95, col=ORA), S(hammer, 128, 124, 0.52, 35)), None),
    ("TitleHeavyHitter", "titles", GL, None, M(S(shield, 128, 124, 0.95, col=RED), S(fist, 128, 120, 0.5), S(chevron, 128, 124, 0.95, cy=50, w=40, t=16, th=14)), None),
    ("TitleCityBreaker", "titles", GL, None, M(S(shield, 128, 124, 0.95, col=YEL), S(skyline_scene, 128, 122, 0.5, broken=True)), None),
    ("TitleChaosLord", "titles", GL, None, M(A(128, 128, 110, PUR, 0.6), S(shield, 128, 136, 0.85, col=PUR), S(crystal, 128, 138, 0.46), S(crown, 128, 36, 0.42)), None),
    ("TitleWreckLegend", "titles", GL, None, M(A(128, 128, 120, GOLD, 0.6), S(wings, 128, 116, 0.78), S(shield, 128, 138, 0.78, col=GOLD), S(star, 128, 132, 0.4), S(crown, 128, 40, 0.4)), None),
    ("TitleVIP", "titles", GL, None, M(A(128, 110, 100, GOLD, 0.6), S(crown, 128, 104, 0.95), TX("VIP", 128, 196, 70, YEL)), None),

    ("BadgeFirstWreck", "badges", MD, ("bronze", ORA), M(S(burst, 128, 110, 0.85), S(car, 128, 150, 0.82, -8, col=RED, crushed=True)), "FIRST"),
    ("BadgeWrecks100", "badges", MD, ("bronze", ORA), M(S(burst, 112, 160, 0.5), S(cracked_block, 108, 176, 0.58), wreck_hit()), "100"),
    ("BadgeWrecks1000", "badges", MD, ("silver", CYA), M(S(burst, 112, 160, 0.5), S(cracked_block, 108, 176, 0.58), wreck_hit(head="#C9D1DC")), "1K"),
    ("BadgeWrecks10000", "badges", MD, ("gold", GOLD), M(S(burst, 112, 160, 0.5, cols=(GOLD, YEL, WHT)), S(cracked_block, 108, 176, 0.58), wreck_hit(head=GOLD), SP(210, 200, 12)), "10K"),
    ("BadgeFirstRebirth", "badges", MD, ("bronze", CYA), M(A(128, 128, 90, PUR, 0.7), S(rebirth, 128, 128, 1.0)), "1"),
    ("BadgeRebirths10", "badges", MD, ("silver", CYA), M(A(128, 128, 90, PUR, 0.7), S(rebirth, 128, 128, 1.0)), "10"),
    ("BadgeRebirths100", "badges", MD, ("gold", PUR), M(A(128, 128, 90, PUR, 0.8), S(rebirth, 128, 128, 1.0)), "100"),
    ("BadgeChaosEvent", "badges", MD, ("chaos", PUR), M(A(128, 128, 120, PUR, 0.9), S(vortex, 128, 128, 1.05), S(crystal, 128, 128, 0.55)), None),
    ("BadgeCityDestroyer", "badges", MD, ("gold", RED), M(S(burst, 128, 96, 0.85), S(skyline_scene, 128, 146, 0.78, broken=True)), None),
    ("BadgeWreckLegend", "badges", MD, ("legend", GOLD), M(A(128, 128, 120, GOLD, 0.7), S(crossed_hammers, 128, 136, 1.0), S(crown, 128, 56, 0.5)), "LEGEND"),

    ("QuestDestroy", "quests", GL, None, M(S(burst, 104, 150, 0.5), S(cracked_block, 100, 182, 0.55), wreck_hit()), None),
    ("QuestDamage", "quests", GL, None, S(gauge, 128, 128, 1.0), None),
    ("QuestCash", "quests", GL, None, M(S(coin_stack, 100, 152, 0.8), S(coin, 172, 116, 0.55)), None),
    ("QuestTools", "quests", GL, None, S(toolbox, 128, 142, 0.95), None),
    ("QuestChaos", "quests", GL, None, M(A(128, 128, 110, PUR, 0.8), S(crystal_cluster, 128, 138, 0.92), S(lightning, 210, 60, 0.26, 20)), None),

    ("DailyCash", "daily", GL, None, M(S(cash_pile, 128, 118, 0.9, n=2), S(coin, 182, 182, 0.36), S(coin, 76, 192, 0.3)), None),
    ("DailyScrap", "daily", GL, None, M(S(gear, 96, 104, 0.52, col="#78B4C6"), S(gear, 172, 92, 0.36, col="#9AC6D4", teeth=6, hole=26), S(bolt, 82, 172, 0.46, 40), S(nut, 160, 170, 0.56)), None),
    ("DailyBoost", "daily", GL, None, flask_i(ORA, (lightning, {}), 0.34), None),
    ("DailySkin", "daily", GL, None, S(tshirt, 128, 128, 0.95), None),
    ("DailyCores", "daily", GL, None, M(A(128, 128, 110, PUR, 0.8), S(crystal_cluster, 128, 136, 0.95)), None),
    ("DailyMega", "daily", GL, None, M(S(burst, 128, 120, 1.05, cols=(GOLD, YEL, "#FFF6C2")), S(gift, 128, 142, 0.8, col=GOLD, rib=RED)), None),

    ("NavShop", "nav", GL, None, S(cart, 142, 128, 0.85), None),
    ("NavTools", "nav", GL, None, S(tools_cross, 128, 128, 1.0), None),
    ("NavUpgrades", "nav", GL, None, M(S(arrow_up, 128, 128, 1.0), S(lightning, 128, 150, 0.42)), None),
    ("NavQuests", "nav", GL, None, S(clipboard, 128, 134, 0.95), None),
    ("NavRebirth", "nav", GL, None, M(A(128, 128, 90, PUR, 0.7), S(rebirth, 128, 128, 1.0)), None),
    ("NavDaily", "nav", GL, None, S(gift, 128, 138, 0.95), None),
    ("NavSettings", "nav", GL, None, S(gear, 128, 128, 1.0, col="#AEB6C4", hole=34), None),
    ("NavChaosShop", "nav", GL, None, S(cart, 142, 134, 0.85, col=PUR, cargo=lambda: place(crystal, 6, -66, 0.5)), None),
    ("ButtonWreck", "nav", "glyph512", None, M(S(burst, 104, 156, 0.62, cols=(WHT, "#FFFFFF", "#FFFFFF")), S(cracked_block, 100, 186, 0.55, col=WHT), wreck_hit(head=WHT, white=True)), None),

    ("IconLock", "ui", GL, None, S(padlock, 128, 134, 1.0), None),
    ("IconCheck", "ui", GL, None, S(check, 128, 128, 1.0), None),
    ("IconClose", "ui", GL, None, S(cross, 128, 128, 0.95), None),
    ("IconArrow", "ui", GL, None, S(arrow_right, 128, 128, 1.0), None),
    ("MatAlloyPlate", "materials", GL, None, M(S(alloy_plate, 128, 132, 1.0)), None),
    ("MatCopperWire", "materials", GL, None, M(S(copper_wire, 128, 128, 1.0)), None),
    ("MatCircuitBoard", "materials", GL, None, M(S(circuit_board, 128, 128, 1.0)), None),
    ("MatPlasmaCell", "materials", GL, None, M(A(128, 128, 104, CYA, 0.5), S(plasma_cell, 128, 128, 1.0)), None),
    ("MatColossusPlating", "materials", GL, None, M(S(colossus_plating, 128, 128, 1.0)), None),
    ("MatCrusherHydraulics", "materials", GL, None, M(S(crusher_hydraulics, 128, 132, 1.0)), None),
    ("MatIndustrialCore", "materials", GL, None, M(S(industrial_core, 128, 128, 1.0)), None),
    ("MatWardenArmor", "materials", GL, None, M(S(warden_armor, 128, 124, 0.95)), None),
    ("MatVoidShard", "materials", GL, None, M(A(128, 128, 110, PUR, 0.8), S(crystal, 128, 128, 1.0)), None),
    ("MatOverlordHeart", "materials", GL, None, M(S(overlord_heart, 128, 128, 1.0)), None),
    ("ToolScrapCleaver", "tools", B, "#C4703C", M(A(150, 112, 70, ORA, 0.6), S(cleaver, 118, 140, 0.82, 28)), None),
    ("ToolWreckingMaul", "tools", B, YEL, M(A(176, 76, 76, YEL, 0.8), S(hammer, 128, 136, 0.9, 35, head="#F2B81C", handle="#2A2C34", hw=166, hh=94, band="#1A1A1E", grip="#5A5F6B"), SP(222, 112, 14, YEL), SP(50, 196, 10, ORA)), None),
    ("ToolArcWelder", "tools", B, "#FF5A2A", F_("arc", 116, 140, 0.74, 210, 112, 0.75, CYA), None),
    ("ToolRailDriver", "tools", B, "#9CCB2C", F_("rail", 112, 140, 0.74, 206, 112, 0.7, "#C8FF3C"), None),
    ("ToolSingularityLauncher", "tools", B, PUR, F_("singularity", 112, 142, 0.72, 206, 108, 0.62, PUR), None),
    ("ToolOverlordHammer", "tools", B, "#FF3BA0", M(A(176, 76, 80, "#FF3BD0", 0.9), S(crystal, 66, 70, 0.32, -30, col=PUR), S(crystal, 214, 186, 0.28, 25, col=PUR), S(hammer, 128, 136, 0.9, 35, head="#1E1428", handle="#1E1428", hw=164, hh=90, band="#FF8A1F", grip="#3A2A4A", glowface="#FF3BD0"), SP(222, 108, 16, "#FF3BD0")), None),
    ("BadgeBossSlayer", "badges", MD, ("silver", ORA), M(S(burst, 128, 112, 0.8), S(colossus_plating, 128, 128, 0.82)), "BOSS"),
    ("BadgeIslandConqueror", "badges", MD, ("legend", PUR), M(A(128, 128, 120, PUR, 0.8), S(overlord_heart, 128, 132, 0.86), S(crown, 128, 50, 0.45)), "6/6"),
    ("BadgeMasterSmith", "badges", MD, ("gold", ORA), M(A(128, 128, 100, ORA, 0.6), S(alloy_plate, 128, 150, 0.7), S(hammer, 128, 104, 0.62, -30)), "LV10"),
]


def _save_white(alpha, path):
    a = np.clip(alpha, 0, 1)
    h, w = a.shape
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = (a * 255 + 0.5).astype(np.uint8)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(path)


def _grid(n):
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    c = (n - 1) / 2
    return (x - c) / (n / 2), (y - c) / (n / 2)


def _poly_alpha(n, polys, ss=4, blur=0):
    im = Image.new("L", (n * ss, n * ss), 0)
    d = ImageDraw.Draw(im)
    for p, v in polys:
        d.polygon([(x * ss, y * ss) for x, y in p], fill=v)
    im = im.resize((n, n), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 255.0


def tex_glow(p):
    x, y = _grid(256)
    r = np.sqrt(x * x + y * y)
    _save_white(np.clip(1 - r, 0, 1) ** 2.2, p)


def tex_spark(p):
    x, y = _grid(128)
    q = (np.abs(x) ** 0.5 + np.abs(y) ** 0.5) ** 2
    core = np.clip((1 - q) * 3.0, 0, 1)
    r = np.sqrt(x * x + y * y)
    halo = np.clip(1 - r / 0.45, 0, 1) ** 2 * 0.6
    _save_white(np.maximum(core, halo), p)


def tex_smoke(p):
    rng = np.random.default_rng(7)
    n = 256
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    a = np.zeros((n, n), np.float32)
    for cx, cy, rr in ((128, 140, 70), (90, 120, 50), (166, 118, 54), (118, 86, 46), (150, 168, 48), (96, 166, 44)):
        d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / rr
        a = np.maximum(a, np.clip(1 - d, 0, 1) ** 1.3)
    noise = rng.random((32, 32)).astype(np.float32)
    nz = np.asarray(Image.fromarray((noise * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255.0
    a = a * (0.7 + 0.45 * nz)
    a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255.0
    edge = np.sqrt((x - 127.5) ** 2 + (y - 127.5) ** 2) / 128
    _save_white(a * np.clip((1 - edge) * 4, 0, 1) * 0.95, p)


def tex_shard(p):
    a = _poly_alpha(128, [([(14, 112), (64, 8), (116, 92)], 255), ([(64, 8), (70, 60), (116, 92)], 205)])
    _save_white(a, p)


def tex_ring(p):
    x, y = _grid(256)
    r = np.sqrt(x * x + y * y)
    inner = np.clip((r - 0.62) / 0.2, 0, 1) ** 1.5
    outer = np.clip((0.96 - r) / 0.05, 0, 1)
    _save_white(inner * outer, p)


def tex_hazard(p):
    w, h, ss = 512, 64, 4
    im = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(im)
    for k in range(-2, 10):
        x0 = k * 64
        d.polygon([((x0) * ss, h * ss), ((x0 + 32) * ss, h * ss), ((x0 + 96) * ss, 0), ((x0 + 64) * ss, 0)], fill=255)
    a = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255.0
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(p)


def tex_panel(p):
    rng = np.random.default_rng(3)
    n = 512
    streak = rng.random((n, 1)).astype(np.float32)
    fine = rng.random((n, n)).astype(np.float32)
    big = rng.random((16, 16)).astype(np.float32)
    bigu = np.asarray(Image.fromarray((big * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255.0
    rows = np.asarray(Image.fromarray((np.repeat(streak, n, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur((12, 0.6))), np.float32) / 255.0
    a = 0.05 + 0.10 * rows + 0.05 * fine + 0.06 * bigu
    _save_white(a, p)


def tex_button(p):
    n = 256
    y = np.linspace(0, 1, n, dtype=np.float32)[:, None] * np.ones((1, n), np.float32)
    a = np.clip(1 - y / 0.55, 0, 1) ** 1.6 * 0.85
    a[:6, :] = np.maximum(a[:6, :], 0.95)
    _save_white(a, p)


TEXTURES = [
    ("Glow", tex_glow), ("Spark", tex_spark), ("Smoke", tex_smoke), ("Shard", tex_shard), ("Ring", tex_ring),
    ("HazardStripe", tex_hazard), ("PanelTexture", tex_panel), ("ButtonTexture", tex_button),
]


def icon_path(key, cat):
    return ICONS / cat / f"{snake(key)}.png"


def build_icon(entry):
    key, cat, fam, acc, build, label = entry
    reset("i_")
    if fam == B:
        svg, w = tile_svg(acc, build, label, seed=len(key)), 512
    elif fam == MD:
        svg, w = medal_svg(acc[0], acc[1], build, label), 512
    elif fam == "glyph512":
        svg, w = glyph_svg(build, 512), 512
    else:
        svg, w = glyph_svg(build, 256), 256
    hdir = BUILD / "icons"
    hdir.mkdir(parents=True, exist_ok=True)
    html = hdir / f"{snake(key)}.html"
    html.write_text(html_page(svg, w, w), encoding="utf-8")
    return (html, icon_path(key, cat), w, w)


def write_index():
    idx = {}
    for key, cat, *_ in ICON_TABLE:
        p = icon_path(key, cat)
        if p.exists():
            idx[key] = p.relative_to(ASSETS).as_posix()
    for key, _ in TEXTURES:
        p = TEX / f"{snake(key)}.png"
        if p.exists():
            idx[key] = p.relative_to(ASSETS).as_posix()
    (SRC / "index_icons.json").write_text(json.dumps(idx, indent=2), encoding="utf-8")
    return idx


def contact_sheet():
    items = [(k, icon_path(k, c)) for k, c, *_ in ICON_TABLE] + [(k, TEX / f"{snake(k)}.png") for k, _ in TEXTURES]
    cols, cell, lab = 12, 128, 14
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * (cell + 2), rows * (cell + lab + 2)), (58, 61, 72, 255))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 10)
    except OSError:
        f = ImageFont.load_default()
    for i, (k, p) in enumerate(items):
        x, y = (i % cols) * (cell + 2), (i // cols) * (cell + lab + 2)
        if p.exists():
            im = Image.open(p).convert("RGBA")
            im.thumbnail((cell, cell), Image.LANCZOS)
            sheet.alpha_composite(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
        else:
            d.rectangle([x, y, x + cell, y + cell], outline=(255, 0, 0, 255), width=3)
        d.text((x + 2, y + cell + 1), k[:22], fill=(230, 230, 235, 255), font=f)
    if sheet.width > 1600:
        sheet = sheet.resize((1600, int(sheet.height * 1600 / sheet.width)), Image.LANCZOS)
    sheet.convert("RGB").save(SRC / "contact_icons.png")


def check_alpha():
    bad = []
    for key, cat, *_ in ICON_TABLE:
        p = icon_path(key, cat)
        if not p.exists():
            bad.append((key, "missing"))
            continue
        with Image.open(p) as im:
            im = im.convert("RGBA")
            w, h = im.size
            if any(im.getpixel(c)[3] != 0 for c in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))):
                bad.append((key, "corner alpha"))
            if im.getchannel("A").getextrema()[1] == 0:
                bad.append((key, "empty"))
    return bad


def main(keys):
    TEX.mkdir(parents=True, exist_ok=True)
    sel = [e for e in ICON_TABLE if not keys or e[0] in keys]
    for key, fn in TEXTURES:
        if not keys or key in keys:
            fn(TEX / f"{snake(key)}.png")
    jobs = [build_icon(e) for e in sel]
    for i in range(0, len(jobs), 14):
        render_many(jobs[i:i + 14])
        write_index()
    idx = write_index()
    contact_sheet()
    bad = check_alpha()
    allkeys = [e[0] for e in ICON_TABLE] + [k for k, _ in TEXTURES]
    missing = [k for k in allkeys if k not in idx]
    print(json.dumps({"written": len(idx), "expected": len(allkeys), "missing": missing, "alpha_issues": bad}))


if __name__ == "__main__":
    main(set(sys.argv[1:]))
