from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import ALL, expedition_asset
from _landmark_lib import patch


def build():
    a = expedition_asset("GateBeam", 700, 20.0, atlas=512)
    a.role("Glow", "neon", color=(239, 183, 95))
    metal = Material("metal", color=(58, 62, 70), rough=0.38, polish=0.5, dirt=0.4, scratches=0.4)
    plate = Material("paint", color=(40, 44, 52), under=(110, 110, 116), wear=0.3, scratches=0.3, rough=0.4, dirt=0.35, skin=False, decals=[
        {"type": "text", "text": "EXPEDITION", "center": (0.0, 0.0), "height": 1.0, "color": (230, 220, 200), "font": "impact", "wear": 0.3},
    ])
    for y in (0.25, 2.75):
        a.add("Body", sh.box((38.0, 0.5, 6.0), metal).transformed(T(0, y, 0)))
    for k in range(12):
        x = -17.5 + k * (35.0 / 11)
        for z in (-2.85, 2.85):
            a.add("Body", sh.box((0.3, 2.4, 0.3), metal).transformed(compose(T(x, 1.5, z), R(0, 0, 35 if k % 2 else -35))))
    a.add("Body", sh.box((16.0, 2.0, 0.2), plate).transformed(T(0, 1.5, -3.05)))
    a.add("Body", sh.box((16.0, 2.0, 0.2), plate).transformed(compose(T(0, 1.5, 3.05), R(0, 180, 0))))
    for z in (-2.6, 2.6):
        a.add("Glow", sh.box((36.0, 0.15, 0.15), None).transformed(T(0, -0.05, z)))
    patch(a, ALL, ["EntryArch"], tint=["Glow"])
    return a
