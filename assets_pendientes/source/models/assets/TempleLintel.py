from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import SKY, expedition_asset
from _temple_lib import marble, GOLD
from _landmark_lib import patch

W, H, L = 14.0, 7.0, 72.0


def build():
    a = expedition_asset("TempleLintel", 900, 38.0, atlas=1024, front=270)
    stone = marble((205, 176, 120), (240, 220, 170))
    carved = Material("paint", color=(205, 176, 120), under=(150, 130, 90), wear=0.2, scratches=0.2, rough=0.4, dirt=0.4, skin=False, decals=[
        *[{"type": "rect", "center": (z, 0.0), "size": (2.2, 2.2), "radius": 1.1, "outline": 0.25, "color": (120, 96, 60), "wear": 0.2} for z in range(-33, 34, 6)],
        *[{"type": "rect", "center": (z + 3.0, 0.0), "size": (0.4, 2.6), "color": (120, 96, 60), "wear": 0.2} for z in range(-33, 28, 6)],
    ])
    a.add("Body", sh.rounded_box((W - 1.0, 2.6, L - 1.0), 0.06, 1, stone).transformed(T(0, 1.3, 0)))
    a.add("Body", sh.rounded_box((W - 0.4, 2.8, L - 0.4), 0.06, 1, stone, faces=["+y", "-y", "+z", "-z"], face_mats=None).transformed(T(0, 4.0, 0)))
    for x in (-(W - 0.4) / 2, (W - 0.4) / 2):
        a.add("Body", sh.box((0.08, 2.4, L - 1.0), carved).transformed(compose(T(x + (0.05 if x > 0 else -0.05), 4.0, 0), R(0, 90 if x > 0 else -90, 0), R(0, -90 if x > 0 else 90, 0))))
    a.add("Body", sh.rounded_box((W, 1.4, L), 0.08, 1, stone).transformed(T(0, H - 0.7, 0)))
    patch(a, [SKY], ["TempleLintel"])
    return a
