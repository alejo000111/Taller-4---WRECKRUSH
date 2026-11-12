from wr3d import Material, T
from wr3d import shapes as sh
from _expedition_lib import ALL, expedition_asset
from _landmark_lib import patch


def build():
    a = expedition_asset("PathBollard", 300, 3.0, atlas=256)
    a.role("Glow", "neon", color=(255, 214, 150))
    metal = Material("metal", color=(70, 74, 80), rough=0.4, polish=0.4, dirt=0.4, scratches=0.4)
    a.add("Body", sh.lathe([(0.0, 0.0), (0.65, 0.0), (0.65, 0.2), (0.5, 0.35), (0.45, 2.7), (0.6, 2.85), (0.6, 3.0), (0.0, 3.0)], 10, metal, smooth_angle=35))
    a.add("Glow", sh.lathe([(0.0, 3.0), (0.5, 3.0), (0.55, 3.25), (0.4, 3.45), (0.0, 3.5)], 10, None, smooth_angle=40))
    patch(a, ALL, ["PathPost"], remove=["PathCap"], keep_height=True)
    return a
