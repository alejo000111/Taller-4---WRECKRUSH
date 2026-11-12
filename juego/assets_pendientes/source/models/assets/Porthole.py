from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import FROST, expedition_asset
from _landmark_lib import patch


def build():
    a = expedition_asset("Porthole", 200, 2.0, atlas=256, front=270)
    a.role("Glow", "neon", color=(129, 207, 230))
    brass = Material("gold", color=(190, 150, 80), rough=0.35, dirt=0.3)
    a.add("Body", sh.torus(1.25, 0.2, brass, segments=14, sides=5).transformed(compose(T(0, 1.5, 0), R(0, 0, 90))))
    a.add("Glow", sh.cylinder(1.1, 0.1, None, bevel=0.0, segments=14).transformed(compose(T(-0.05, 1.5, 0), R(0, 0, 90))))
    patch(a, [FROST], ["Porthole"], tint=["Glow"])
    return a
