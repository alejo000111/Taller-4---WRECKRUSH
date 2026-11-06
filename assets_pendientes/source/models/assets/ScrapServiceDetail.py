import numpy as np

from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel
from _bay_lib import DESIGN, ibeam
from _landmark_lib import landmark
import ScrapWall


def chain(length, mat, link=0.32):
    out = []
    count = int(length / link)
    for k in range(count):
        ring = sh.torus(0.12, 0.035, mat, segments=6, sides=3)
        out.append(ring.transformed(compose(T(0, -k * link, 0), R(0, 90 * (k % 2), 90))))
    return out


def build():
    a = building_asset("ScrapServiceDetail", 900, 10.0, atlas=512)
    rust = Material("scrapwall_sheet", color=(139, 80, 48))
    iron = steel((103, 119, 135), dirt=0.6)
    beam = ibeam(18.0, rust, 1.0, 0.8).transformed(compose(T(-9.0, 5.0, -0.24), R(0, 0, -90), T(0, 0, 0)))
    a.add("Body", beam.transformed(T(0, 0.0, 0)))
    for x in (-5.0, 5.0):
        a.add("Body", sh.cylinder(0.25, 4.6, rust, bevel=0.0, segments=6).transformed(T(x, 2.3, 0.26)))
        a.add("Body", sh.box((0.9, 0.2, 0.9), iron).transformed(T(x, 0.1, 0.26)))
    for x in (-6.0, 0.0, 6.0):
        a.add("Body", [p.transformed(T(x, 4.45, 0.66)) for p in chain(2.0, iron)])
        hook = sh.sweep([(0.0, 0.0, 0.0), (0.0, -0.35, 0.0), (0.18, -0.5, 0.0), (0.3, -0.35, 0.0)], 0.05, 4, iron, samples=6, caps=False)
        a.add("Body", hook.transformed(T(x, 2.45, 0.66)))
    landmark(a, DESIGN, "ScrapService_Detail", fit="box")
    return a
