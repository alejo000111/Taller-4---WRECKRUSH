from __future__ import annotations

import base64
import io
import sys

from PIL import Image, ImageEnhance, ImageFilter

from gen_brand import FIRE_FILL, GOLD_FILL, SKEW, VIOLET_FILL, TH, TW, grain_filter, logo_embed, svg_doc, vignette
from wr_lib import BUILD, THUMBS, headline, lin_grad, render_many, render_svg

CAPTURES = THUMBS / "captures"

SHOTS = {
    "t6": {
        "file": "thumbnail_06_boss_islands",
        "capture": "boss_islands.jpg",
        "crop_top": 40,
        "grade": (1.12, 1.06, 1.04),
        "shade": ("left", 0.62),
        "lines": [
            dict(text="BOSS", size=260, fill=FIRE_FILL),
            dict(text="ISLANDS", size=200, dy=210, dx=24, fill=VIOLET_FILL),
            dict(text="6 NEW BOSSES", size=104, dy=150, dx=40, fill=GOLD_FILL, outline=18),
        ],
        "headline": (76, 300),
        "anchor": "start",
        "logo": (36, 816, 470),
        "ring": "#FF3BA0",
    },
    "t7": {
        "file": "thumbnail_07_boss_tools",
        "capture": "boss_tools.jpg",
        "crop_top": 18,
        "grade": (1.1, 1.05, 1.03),
        "shade": ("top", 0.55),
        "lines": [dict(text="FORGE BOSS TOOLS", size=168, fill=FIRE_FILL)],
        "headline": (960, 205),
        "anchor": "middle",
        "logo": (1450, 872, 430),
        "ring": "#FF7A1A",
    },
    "t8": {
        "file": "thumbnail_08_mythic_pets",
        "capture": "pets.jpg",
        "crop_top": 0,
        "grade": (1.14, 1.06, 1.1),
        "shade": ("bottom", 0.6),
        "lines": [dict(text="MYTHIC PETS", size=220, fill=VIOLET_FILL)],
        "headline": (960, 1030),
        "anchor": "middle",
        "logo": (36, 24, 400),
        "ring": "#A64DFF",
    },
}


def prepare(spec):
    with Image.open(CAPTURES / spec["capture"]) as src:
        im = src.convert("RGB")
    w, h = im.size
    keep = round(w * TH / TW)
    top = min(spec["crop_top"], h - keep)
    im = im.crop((0, top, w, top + keep)).resize((TW, TH), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
    color, contrast, brightness = spec["grade"]
    im = ImageEnhance.Color(im).enhance(color)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Brightness(im).enhance(brightness)
    buffer = io.BytesIO()
    im.save(buffer, "JPEG", quality=93)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def shade_layer(tid, side, opacity):
    gid = f"{tid}_shade"
    stops = [(0, "#05030A", opacity), (1, "#05030A", 0)]
    if side == "left":
        grad = lin_grad(gid, stops, x1=0, y1=0, x2=0.62, y2=0)
    elif side == "top":
        grad = lin_grad(gid, stops, x1=0, y1=0, x2=0, y2=0.4)
    else:
        grad = lin_grad(gid, stops, x1=0, y1=1, x2=0, y2=0.62)
    return grad, f'<rect width="{TW}" height="{TH}" fill="url(#{gid})"/>'


def build_svg(tid, spec):
    photo = prepare(spec)
    grad, shade = shade_layer(tid, *spec["shade"])
    body = f'<image href="{photo}" x="0" y="0" width="{TW}" height="{TH}" preserveAspectRatio="xMidYMid slice"/>' + shade
    hx, hy = spec["headline"]
    hd, hb = headline(spec["lines"], hx, hy, f"{tid}_h", skew=SKEW, outline=24, ring=spec["ring"], extrude=(12, 20), anchor=spec["anchor"])
    vd, vb = vignette(f"{tid}_vig", TW, TH, 0.6)
    lx, ly, lw = spec["logo"]
    defs = grad + hd + vd + grain_filter(f"{tid}_gr", seed=3, alpha=0.05)
    content = body + vb + hb + f'<rect width="{TW}" height="{TH}" filter="url(#{tid}_gr)" opacity="0.5"/>' + logo_embed(lx, ly, lw)
    return svg_doc(TW, TH, defs, content)


def main(targets):
    BUILD.mkdir(parents=True, exist_ok=True)
    jobs = []
    for tid in targets:
        spec = SHOTS[tid]
        svg = build_svg(tid, spec)
        jobs.append(render_svg(svg, spec["file"], THUMBS / f"{spec['file']}.png", TW, TH, bg="#000000"))
    render_many(jobs)
    return [SHOTS[t]["file"] for t in targets]


if __name__ == "__main__":
    print(main(sys.argv[1:] or list(SHOTS)))
