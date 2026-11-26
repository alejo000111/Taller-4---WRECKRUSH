from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset
from _bay_lib import DESIGN
from _future_lib import pearl, graphite, CYAN
from _landmark_lib import landmark


def build():
    a = building_asset("FutureServiceDetail", 900, 10.0, atlas=512)
    a.role("Glow", "neon", color=CYAN)
    shell = pearl(panel=1.4)
    core = graphite(panel=1.0)
    a.add("Body", sh.rounded_box((17.0, 0.4, 1.2), 0.12, 1, core).transformed(T(0, 9.1, -0.08)))
    a.add("Glow", sh.box((15.0, 0.08, 0.1), None).transformed(T(0, 8.86, 0.5)))
    for x in (-8.0, 8.0):
        fin = sh.extrude([(-0.35, -1.0), (0.35, -1.0), (0.35, 0.6), (0.0, 1.0), (-0.35, 0.6)], 9.0, shell, bevel=0.04, corner_radius=0.0)
        a.add("Body", fin.transformed(compose(T(x, 4.5, -0.08), R(-90, 0, 0))))
        a.add("Glow", sh.box((0.12, 6.0, 0.15), None).transformed(T(x, 4.5, 1.0)))
        a.add("Body", sh.rounded_box((1.0, 0.5, 2.1), 0.1, 1, core).transformed(T(x, 0.25, -0.08)))
    landmark(a, DESIGN, "FutureService_Detail", fit="box", tint={"Glow": "FinLight"})
    return a
