from wr3d import Material, T
from wr3d import shapes as sh
from _skyline_lib import tower_asset, block, slab, glow_ring, roof_kit, install

W, D = 41.0, 35.0


def build():
    a = tower_asset("GlassTowerA", 900, 160.0)
    curtain = Material("facade", style="curtain", cell=(4.5, 4.0), mullion=0.18, slab=0.14, frame=(196, 206, 218), glass=(70, 116, 156), lit=(240, 240, 220), lit_ratio=0.1, glass_metal=0.55, dirt=0.15)
    podium = Material("facade", style="curtain", cell=(6.0, 7.0), mullion=0.3, slab=0.08, frame=(170, 172, 180), glass=(40, 56, 74), lit=(255, 220, 170), lit_ratio=0.6, dirt=0.2)
    trim = Material("metal", color=(176, 184, 196), rough=0.28, polish=0.7, dirt=0.2)
    dark = Material("metal", color=(54, 56, 64), rough=0.4, polish=0.4, dirt=0.4)

    a.add("Body", block((W, 15.0, D), podium).transformed(T(0, 7.5, 0)))
    a.add("Body", slab((W + 1.0, 1.0, D + 1.0), trim, 15.5))
    a.add("Warm", sh.box((28.0, 9.0, 0.25), None).transformed(T(0, 5.5, -D / 2 - 0.15)))
    a.add("Body", sh.box((W - 6.0, 0.6, 3.6), trim).transformed(T(0, 10.6, -D / 2 - 1.8)))

    sw, sd, s0, s1 = 35.0, 29.0, 16.0, 168.0
    a.add("Body", block((sw, s1 - s0, sd), curtain).transformed(T(0, (s0 + s1) / 2, 0)))
    for x in (-sw / 2, sw / 2):
        a.add("Body", block((1.0, s1 - s0, 1.0), trim, faces=["+x", "-x", "-z"]).transformed(T(x, (s0 + s1) / 2, -sd / 2)))
    a.add("Body", slab((36.0, 1.4, 30.0), trim, 168.7))
    uw, ud, u0, u1 = 27.0, 21.0, 169.4, 258.0
    a.add("Body", block((uw, u1 - u0, ud), curtain.but(lit_ratio=0.14)).transformed(T(0, (u0 + u1) / 2, 0)))
    a.add("Glow", glow_ring(uw, ud, u1 - 0.4, thick=0.6, out=0.3))
    roof = sh.extrude([(-uw / 2, 0.0), (uw / 2, 0.0), (uw / 2, 2.0), (-uw / 2, 12.0)], ud, curtain.but(lit_ratio=0.0), bevel=0.0, corner_radius=0.0)
    a.add("Body", roof.transformed(T(0, u1, 0)))
    a.add("Body", slab((uw + 0.8, 0.8, ud + 0.8), dark, u1 + 0.2))
    roof_kit(a, u1 + 2.6, uw * 0.6, ud * 0.6, dark, 11, mast_h=30.0)
    install(a, ["GlassTower"], pick=(2, 0))
    return a
