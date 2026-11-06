import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import VERDANT, expedition_asset
from _landmark_lib import patch

W, H, D = 35.0, 3.0, 49.0


def build():
    a = expedition_asset("SawRoof", 600, 26.0, atlas=512)
    a.role("Glow", "neon", color=(239, 183, 95))
    roof = Material("corrugated", color=(47, 66, 59), under=(110, 96, 80), pitch=0.5, axis=1, depth=0.05, wear=0.5, rough=0.5, dirt=0.55, skin=False)
    teeth = 4
    step = D / teeth
    pts = [(-D / 2, 0.0)]
    for k in range(teeth):
        z0 = -D / 2 + k * step
        pts.append((z0 + step * 0.82, H))
        pts.append((z0 + step * 0.82, 0.4))
        pts.append((z0 + step, 0.4))
    pts[-1] = (D / 2, 0.0)
    prism = sh.extrude(np.asarray(pts), W, roof, bevel=0.0, corner_radius=0.0, smooth_angle=20)
    a.add("Body", prism.transformed(R(0, 90, 0)))
    for k in range(teeth):
        z = -D / 2 + k * step + step * 0.82
        a.add("Glow", sh.box((W - 1.0, H - 0.8, 0.1), None).transformed(T(0, 0.4 + (H - 0.4) / 2, -z + 0.06)))
    patch(a, [VERDANT], ["SawRoof"])
    return a
