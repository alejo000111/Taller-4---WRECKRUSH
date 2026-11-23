from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, eye, metal


def build():
    a = pet_asset("ReactorCube", 2200, 2.6)
    a.role("Glow", "neon", color=(34, 225, 255))
    a.role("Ring", "surface")
    frame = metal((64, 68, 78))
    panel = Material("diamondplate", color=(130, 134, 142), pitch=0.18, dirt=0.3)
    hazard = Material("hazard", color=(255, 196, 40), color2=(26, 26, 30), width=0.2, angle=45)
    a.add("Glow", sh.sphere(0.6, None, 12, 8))
    for axis in range(3):
        for sign in (-1, 1):
            rot = [(0, 0, 0), (0, 0, 90), (90, 0, 0)][axis]
            offset = [(0, sign * 0.78, 0), (sign * 0.78, 0, 0), (0, 0, sign * 0.78)][axis]
            for k in (-1, 1):
                slat = sh.rounded_box((1.5, 0.12, 0.55), 0.04, 1, panel)
                a.add("Body", slat.transformed(compose(T(*offset), R(*rot), T(0, 0, k * 0.42))))
    for x in (-0.8, 0.8):
        for y in (-0.8, 0.8):
            a.add("Body", sh.box((0.16, 0.16, 1.76), hazard).transformed(T(x, y, 0)))
            a.add("Body", sh.box((0.16, 1.76, 0.16), frame).transformed(T(x, 0, y)))
            a.add("Body", sh.box((1.76, 0.16, 0.16), frame).transformed(T(0, x, y)))
    a.add("Ring", sh.torus(1.35, 0.07, frame, 24, 5).transformed(R(20, 0, 15)))
    for k in range(4):
        a.add("Glow", eye(0.07).transformed(compose(R(20, 0, 15), R(0, k * 90, 0), T(1.35, 0, 0))))
    return a
