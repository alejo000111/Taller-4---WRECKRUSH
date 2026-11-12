import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh

YELLOW = (255, 210, 31)
INK = (18, 18, 22)
PLATFORM = (12.0, 0.4, 10.0)


def station(asset, target, parent="Plaza"):
    asset.meta["station"] = {"target": target, "parent": parent, "colliders": []}
    return asset


def collider(asset, name, size, center, shape="Block", rotation=(0.0, 0.0, 0.0)):
    asset.meta["station"]["colliders"].append({
        "name": name,
        "shape": shape,
        "size": [round(float(v), 4) for v in size],
        "center": [round(float(v), 4) for v in center],
        "rotation": [round(float(v), 4) for v in rotation],
    })
    return asset


def platform(asset, accent, glow_role="Glow"):
    top = Material("diamondplate", color=(70, 72, 80), pitch=0.45, dirt=0.4)
    side = Material("hazard", color=YELLOW, color2=INK, width=0.3, angle=45, wear=0.35, dirt=0.35)
    deck = sh.rounded_box(PLATFORM, 0.06, 1, side, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"+y": top})
    asset.add("Body", deck)
    edge = Material("metal", color=(36, 38, 44), rough=0.35, polish=0.6, dirt=0.3)
    for z in (-PLATFORM[2] / 2, PLATFORM[2] / 2):
        asset.add("Body", sh.box((PLATFORM[0] + 0.2, 0.14, 0.2), edge).transformed(T(0, 0.27, z)))
    for x in (-PLATFORM[0] / 2, PLATFORM[0] / 2):
        asset.add("Body", sh.box((0.2, 0.14, PLATFORM[2]), edge).transformed(T(x, 0.27, 0)))
    for z in (-PLATFORM[2] / 2 - 0.11, PLATFORM[2] / 2 + 0.11):
        asset.add(glow_role, sh.box((PLATFORM[0] - 0.6, 0.08, 0.04), None).transformed(T(0, 0.08, z)))
    collider(asset, "Platform", PLATFORM, (0.0, 0.0, 0.0))
    return asset


def sign_face(text, accent, size, height=None, sub=None):
    w, h = size
    decals = [
        {"type": "rect", "center": (0.0, 0.0), "size": (w - 0.2, h - 0.2), "radius": 0.12, "outline": 0.1, "color": accent, "wear": 0.1},
        {"type": "text", "text": text, "center": (0.0, -0.08 if sub else 0.02), "height": height or h * 0.55, "color": (245, 245, 250), "font": "impact", "wear": 0.1},
    ]
    if sub:
        decals.append({"type": "text", "text": sub, "center": (0.0, h * 0.3), "height": h * 0.16, "color": accent, "font": "black", "wear": 0.1})
    return Material("paint", color=(22, 22, 28), under=(120, 120, 128), wear=0.15, scratches=0.2, rough=0.4, dirt=0.25, skin=False, decals=decals)


def steel(color=(54, 56, 64)):
    return Material("metal", color=color, rough=0.38, polish=0.6, dirt=0.35, scratches=0.3)


def painted(color, decals=()):
    return Material("paint", color=color, under=(130, 132, 140), wear=0.3, scratches=0.35, rough=0.4, dirt=0.35, skin=False, decals=list(decals))
