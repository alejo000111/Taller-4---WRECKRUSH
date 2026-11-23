import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _wall_lib import wall_asset, targets, post_line, SEGMENT
from _future_lib import pearl, graphite, INK

H = 6.0


def build():
    a = wall_asset("FutureWall", 900, height=H)
    targets(a, ["Zones/FutureDistrict/Perimeter"])

    profile = [(-1.0, 0.0), (1.0, 0.0), (1.0, 4.6), (0.6, H), (-0.6, H), (-1.0, 4.6)]
    for k, x in enumerate(post_line(SEGMENT, 10.0)):
        panel_mat = pearl(panel=5.0, decals=[
            {"type": "text", "text": f"SECTOR {k + 1}", "center": (-2.4, -1.6), "height": 0.45, "color": (90, 100, 130), "font": "impact", "wear": 0.0},
            {"type": "rect", "center": (2.6, -1.6), "size": (2.4, 0.08), "color": (34, 225, 255), "rough": 0.1, "wear": 0.0},
        ])
        panel = sh.extrude(np.asarray(profile), 9.7, panel_mat, bevel=0.15, corner_radius=0.0)
        a.add("Body", panel.transformed(compose(T(x, 0, 0), R(0, 90, 0))))
        post = graphite(panel=4.0)
        a.add("Body", sh.rounded_box((0.5, H + 0.4, 2.3), 0.1, 1, post).transformed(T(x - 5.0, (H + 0.4) / 2, 0)))
        a.add("Glow", sh.box((0.12, H - 0.6, 2.36), None).transformed(T(x - 5.0, H / 2, 0)))
    for sz in (-1, 1):
        a.add("Glow", sh.box((SEGMENT, 0.14, 0.06), None).transformed(T(0, 3.2, sz * 1.03)))
    a.add("Body", sh.rounded_box((SEGMENT, 0.3, 2.4), 0.0, 1, graphite(panel=4.0), faces=["+y", "+z", "-z"]).transformed(T(0, 0.15, 0)))
    return a
