from wr3d import Material, T
from wr3d import shapes as sh
from _expedition_lib import ALL, expedition_asset
from _landmark_lib import patch


def build():
    a = expedition_asset("InlaySegment", 120, 11.0, atlas=256)
    a.role("Glow", "neon", color=(109, 206, 145))
    metal = Material("metal", color=(54, 58, 66), rough=0.4, polish=0.4, dirt=0.4)
    a.add("Body", sh.rounded_box((20.9, 0.12, 1.0), 0.0, 1, metal, faces=["+y", "+x", "-x", "+z", "-z"]).transformed(T(0, 0.06, 0)))
    a.add("Glow", sh.box((19.6, 0.08, 0.35), None).transformed(T(0, 0.12, 0)))
    patch(a, ALL, ["Inlay"], keep_height=True, tint=["Glow"])
    return a
