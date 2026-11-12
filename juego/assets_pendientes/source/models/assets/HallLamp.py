from wr3d import Material, T
from wr3d import shapes as sh
from _hall_lib import HALL, hall_asset, gold, dark_metal
from _landmark_lib import landmark, box_collider


def build():
    a = hall_asset("HallLamp", 700, 8.0, atlas=512)
    a.role("Glow", "neon", color=(255, 200, 130))
    pole = dark_metal()
    trim = gold(0.25)
    a.add("Body", sh.lathe([(0.0, 0.0), (1.1, 0.0), (1.1, 0.3), (0.8, 0.6), (0.45, 1.2), (0.32, 2.0), (0.28, 12.4), (0.45, 12.7), (0.0, 12.75)], 8, pole, smooth_angle=35))
    for y in (2.1, 7.0, 12.2):
        a.add("Body", sh.lathe([(0.3, y - 0.12), (0.46, y - 0.12), (0.46, y + 0.12), (0.3, y + 0.12)], 8, trim, closed=True, smooth_angle=30))
    a.add("Glow", sh.lathe([(0.0, 12.75), (0.85, 12.9), (1.0, 13.8), (0.75, 14.25), (0.0, 14.3)], 8, None, smooth_angle=40))
    a.add("Body", sh.lathe([(0.0, 14.25), (1.1, 14.25), (0.6, 14.5), (0.15, 14.6), (0.0, 14.6)], 8, trim, smooth_angle=40))
    landmark(a, f"{HALL}/Decor", "HallLamp", fit="box", tint={"Glow": "LampHead"},
             colliders=[box_collider("Pole", (1.0, 14.6, 1.0), (0, 7.3, 0))])
    return a
