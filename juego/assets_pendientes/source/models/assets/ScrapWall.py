import numpy as np

from wr3d import Material, T, R, compose, register
from wr3d import shapes as sh
from wr3d.materials import Surface, rgb, grime_amount
from wr3d.noise import smoothstep, mix
from _wall_lib import wall_asset, targets, corrugated_panel, post_line, SEGMENT

H = 6.0


@register("scrapwall_sheet")
def scrapwall_sheet(ctx, p):
    s = Surface(ctx.n)
    paint = rgb(p.get("color", (120, 110, 96)))
    broad = ctx.noise(0.35, 4, 201)
    patch = smoothstep(0.08, 0.2, broad + 0.25 * ctx.noise(1.6, 3, 202))
    streak = smoothstep(0.1, 0.45, ctx.noise_aniso((2.2, 0.12, 2.2), 3, 203)) * smoothstep(1.0, H, ctx.P[:, 1])
    rust = mix(rgb((150, 66, 28)), rgb((96, 42, 20)), smoothstep(-0.3, 0.3, ctx.noise(1.2, 3, 204)))
    base = paint[None, :] * (0.85 + 0.25 * ctx.noise(0.8, 3, 205))[:, None]
    base = mix(base, rust, patch)
    base = mix(base, rgb((110, 50, 22)), streak * 0.6)
    s.base = np.clip(base, 0, 1)
    s.paint = np.zeros(ctx.n)
    s.rough = np.clip(0.55 + 0.35 * patch, 0, 1)
    s.metal = np.clip(0.5 * (1 - patch), 0, 1)
    s.height = patch * ctx.noise(8.0, 2, 206) * 0.004
    low = 1 - smoothstep(0.0, 1.4, ctx.P[:, 1])
    s.dirt = np.clip(grime_amount(ctx, 0.4) + low * 0.6, 0, 0.85)
    return s


def build():
    a = wall_asset("ScrapWall", 900, height=H)
    targets(a, ["Zones/ScrapYard/Perimeter"])

    tones = [(150, 96, 60), (120, 116, 104), (90, 104, 116), (166, 132, 70)]
    posts = post_line(SEGMENT, 10.0)
    beam = Material("metal", color=(60, 58, 56), rough=0.6, polish=0.2, dirt=0.6, scratches=0.4)
    for k, x in enumerate(posts):
        sheet = Material("scrapwall_sheet", color=tones[k % len(tones)])
        panel = corrugated_panel(9.4, H - 0.4 + 0.2 * (k % 2), 0.35, 1.9, sheet)
        tilt = (-1.5, 1.0, -0.6, 1.4)[k % 4]
        a.add("Body", panel.transformed(compose(T(x, 0.0, 0.0), R(tilt, (k % 2) * 0.8, 0))))
        a.add("Body", sh.box((0.5, H + 0.6, 0.5), beam).transformed(T(x - 5.0, (H + 0.6) / 2, 0.0)))
    for sz in (-1, 1):
        for y in (1.2, H - 1.0):
            a.add("Body", sh.box((SEGMENT, 0.28, 0.3), beam).transformed(T(0, y, sz * 0.38)))
        a.add("Glow", sh.box((SEGMENT, 0.16, 0.16), None).transformed(T(0, 1.6, sz * 0.58)))
    for k, x in enumerate((-10.0, 10.0)):
        text = ["KEEP OUT", "SCRAP CO."][k]
        face = Material("paint", color=(230, 196, 40) if k == 0 else (210, 210, 200), under=(120, 100, 80), wear=0.5, scratches=0.4, rough=0.5, dirt=0.4, skin=False, decals=[
            {"type": "text", "text": text, "center": (0.0, 0.0), "height": 0.7, "color": (24, 22, 20), "font": "impact", "wear": 0.4},
        ])
        sign = sh.rounded_box((3.6, 1.3, 0.08), 0.0, 1, face, face_mats={"-z": face, "+z": face})
        a.add("Body", sign.transformed(compose(T(x, 3.4, (-0.62, 0.62)[k]), R(0, 0, (-3, 4)[k]))))
    wire = Material("metal", color=(110, 108, 104), rough=0.5, polish=0.3, dirt=0.4)
    pts = [(x, H + 0.4 + 0.25 * np.sin(x * 1.7), 0.15 * np.cos(x * 2.3)) for x in np.linspace(-SEGMENT / 2, SEGMENT / 2, 41)]
    a.add("Body", sh.sweep(pts, 0.05, 3, wire))
    return a
