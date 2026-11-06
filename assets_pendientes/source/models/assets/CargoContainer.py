from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from ScrapContainer import (
    WALL_MID, WALL_HEIGHT, CHARCOAL, STEEL, YELLOW, INK,
    paint, sheet, slab, corner_post, castings, bottom_rail, roof, door_leaf, lock_gear, fuse,
    right_door_stencils, left_door_stencils,
)

BLUE = (30, 110, 170)
DEEP = (20, 70, 110)
WHITE = (236, 238, 242)


def side_stencils():
    return [
        {"type": "rect", "center": (1.0, -1.3), "size": (14.6, 2.6), "radius": 0.2, "color": WHITE, "wear": 0.15},
        {"type": "text", "text": "WRECKRUSH", "center": (1.0, -1.28), "height": 2.0, "color": DEEP, "font": "impact", "wear": 0.15},
        {"type": "text", "text": "GLOBAL  DEMOLITION  LOGISTICS", "center": (1.0, 0.45), "height": 0.42, "color": WHITE, "font": "impact", "wear": 0.15},
        {"type": "circle", "center": (-8.2, -1.25), "radius": 1.1, "color": YELLOW, "wear": 0.15},
        {"type": "text", "text": "W", "center": (-8.2, -1.2), "height": 1.2, "color": INK, "font": "impact", "wear": 0.15},
        {"type": "text", "text": "WRKU 552013 7", "center": (7.9, -3.55), "height": 0.4, "color": WHITE, "font": "impact", "wear": 0.15},
        {"type": "text", "text": "45G1", "center": (9.4, -2.95), "height": 0.32, "color": WHITE, "font": "impact", "wear": 0.15},
    ]


def end_stencils():
    return [
        {"type": "text", "text": "WRKU 552013 7", "center": (2.1, -3.6), "height": 0.38, "color": WHITE, "font": "impact", "wear": 0.15},
        {"type": "circle", "center": (0.0, -0.4), "radius": 1.3, "color": YELLOW, "wear": 0.15},
        {"type": "text", "text": "W", "center": (0.0, -0.35), "height": 1.4, "color": INK, "font": "impact", "wear": 0.15},
    ]


def recolor(stencils):
    out = []
    for d in stencils:
        d = dict(d)
        if d.get("color") == (234, 224, 198):
            d["color"] = WHITE
        if d.get("text", "").startswith("WRCK 402719"):
            d["text"] = d["text"].replace("WRCK 402719", "WRKU 552013")
        if d.get("text") == "22G1":
            d["text"] = "45G1"
        out.append(d)
    return out


def blue(color=BLUE, **params):
    base = dict(wear=0.18, patches=0.12, streaks=0.3, fade=0.25)
    base.update(params)
    return paint(color, **base)


def build():
    a = Asset("CargoContainer", budget=3500, atlas=1024, ao_radius=1.0, edge_width=0.1, preview_radius=13.6,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")

    frame = blue(DEEP, wear=0.3)
    rails = blue(DEEP, wear=0.3)
    dark = blue(CHARCOAL, wear=0.3, fade=0.1)
    roof_mat = blue((26, 96, 150), patches=0.3, top_rust=0.15, fade=0.2, streaks=0.0, gradient=0.0, highlight=0.3, ripple=(1, 0.58, 0.03))
    cavity = blue((34, 30, 28), wear=0.1, fade=0.0, grime=0.8)
    bar_mat = blue(STEEL, wear=0.3, fade=0.1)
    handle_mat = Material("paint", color=YELLOW, under=STEEL, wear=0.35, scratches=0.3, dirt=0.35, rough=0.45)
    hazard = Material("hazard", color=YELLOW, color2=CHARCOAL, width=0.32, angle=45, under=STEEL, wear=0.35, scratches=0.3, dirt=0.45)
    gasket = Material("rubber", color=(26, 24, 24), pattern="ribs", freq=6.0)

    parts = [castings()]
    for sx in (-1, 1):
        for sz in (-1, 1):
            parts.append(corner_post(frame, 8.4, 0.8).transformed(S(sx, 1, sz)))
    for sx in (-1, 1):
        out = "+x" if sx > 0 else "-x"
        inn = "-x" if sx > 0 else "+x"
        parts += bottom_rail(sx, rails, cavity)
        parts += [slab((0.45, 0.62, 11.05), (sx * 4.675, 9.61, zc), rails, [out, inn, "+y", "-y"]) for zc in (-5.525, 5.525)]
    parts.append(slab((8.1, 0.86, 0.55), (0.0, 0.47, -11.675), rails, ["-z", "+y"], face_mats={"-z": hazard}))
    parts.append(slab((8.1, 0.62, 0.55), (0.0, 9.61, -11.675), rails, ["-z", "+z", "+y", "-y"]))
    parts.append(slab((8.1, 0.96, 0.5), (0.0, 0.52, 11.45), rails, ["+z", "+y"], face_mats={"+z": hazard}))
    parts.append(slab((8.1, 0.92, 0.5), (0.0, 9.46, 11.45), rails, ["+z", "-z", "+y", "-y"]))

    plus_x = sheet(22.3, WALL_HEIGHT, 20, 0.26, blue(stencils=side_stencils()), levels=(0.0, 0.26, 0.5, 0.74, 1.0), dents=[(6.6, 1.4, 1.6, 0.3), (-3.0, -2.2, 1.8, 0.12)], pieces=2)
    minus_x = sheet(22.3, WALL_HEIGHT, 20, 0.26, blue(stencils=side_stencils()), levels=(0.0, 0.3, 0.54, 0.78, 1.0), dents=[(-6.0, 0.8, 1.8, 0.26)], pieces=2)
    end_wall = sheet(8.3, WALL_HEIGHT, 6, 0.25, blue(stencils=end_stencils()), levels=(0.0, 0.32, 0.6, 1.0), crest=0.36, slope=0.12)
    skins = [
        plus_x.transformed(compose(T(4.52, WALL_MID, 0.0), R(0, 90, 0))),
        minus_x.transformed(compose(T(-4.52, WALL_MID, 0.0), R(0, -90, 0))),
        end_wall.transformed(compose(T(0.0, WALL_MID, -11.45), R(0, 180, 0))),
        roof(roof_mat),
    ]

    parts.append(slab((0.14, 8.0, 0.06), (0.0, 5.0, 11.33), gasket, ["+z"]))
    parts += door_leaf(1, frame, blue(stencils=recolor(right_door_stencils())), dark, [])
    parts += door_leaf(-1, frame, blue(stencils=recolor(left_door_stencils())), dark, [])
    parts += lock_gear(bar_mat, dark, handle_mat)

    body, _ = fuse(parts, scale=0.8, height=8.6)
    a.add("Body", body, skins)

    destructible(a, "Industrial")
    collider(a, "Hitbox", (10.0, 10.0, 24.0), (0.0, 5.0, 0.0))
    return a
