from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _pet_lib import pet_asset, blob, eye, metal, painted


def build():
    a = pet_asset("ScrapCrow", 1500, 2.6)
    a.role("Glow", "neon", color=(255, 70, 40))
    body = metal((54, 56, 64))
    rust = painted((150, 92, 58), wear=0.6)
    beak = metal((200, 160, 70))
    leg = metal((90, 92, 100))
    a.add("Body", blob((1.3, 1.1, 1.9), body, 10, 6).transformed(compose(T(0, 0, 0.1), R(-12, 0, 0))))
    a.add("Body", blob((0.95, 0.9, 0.95), body, 8, 6).transformed(T(0, 0.65, -0.8)))
    a.add("Body", sh.frustum(0.22, 0.02, 0.8, beak, bevel=0.0, segments=6).transformed(compose(T(0, 0.58, -1.45), R(-90, 0, 0))))
    for side in (-1, 1):
        a.add("Glow", eye(0.11, None, 6, 4).transformed(T(side * 0.33, 0.78, -1.15)))
        for k in range(3):
            plate = sh.box((1.0 - k * 0.15, 0.08, 0.5), rust if k % 2 == 0 else body)
            a.add("Body", plate.transformed(compose(T(side * (0.75 + k * 0.28), 0.25 + k * 0.08, 0.1 + k * 0.12), R(0, side * 8, side * (-28 - k * 6)))))
        a.add("Body", sh.cylinder(0.05, 0.6, leg, bevel=0.0, segments=5).transformed(T(side * 0.25, -0.75, 0.2)))
        a.add("Body", sh.rounded_box((0.3, 0.06, 0.35), 0.02, 1, leg).transformed(T(side * 0.25, -1.05, 0.1)))
    for k in range(4):
        tail = sh.box((0.18, 0.06, 0.8), rust if k % 2 else body)
        a.add("Body", tail.transformed(compose(T(0, 0.05, 1.15), R(-15, -22 + k * 15, 0), T(0, 0, 0.35))))
    a.add("Body", sh.cylinder(0.08, 0.2, beak, bevel=0.0, segments=6).transformed(compose(T(0, 0.2, -0.85), R(90, 0, 0))))
    return a
