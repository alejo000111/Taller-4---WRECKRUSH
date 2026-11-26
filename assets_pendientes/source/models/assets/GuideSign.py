from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _building_lib import building_asset, steel
from _bay_lib import ibeam
from _landmark_lib import landmark, box_collider


def build():
    a = building_asset("GuideSign", 900, 8.0, atlas=512)
    a.role("Glow", "neon", color=(255, 122, 26))
    post = steel((72, 76, 84))
    frame = steel((40, 44, 52))
    hazard = Material("hazard", color=(255, 210, 31), color2=(24, 24, 28), width=0.25, angle=45, wear=0.4, dirt=0.4)
    for x in (-5.0, 5.0):
        a.add("Body", ibeam(10.1, post, 0.45, 0.45).transformed(T(x, 0.0, 0.0)))
        a.add("Body", sh.box((1.2, 0.2, 1.2), frame).transformed(T(x, 0.1, 0.0)))
        a.add("Body", sh.box((0.5, 1.2, 0.5), hazard).transformed(T(x, 0.8, 0.0)))
    for y in (3.85, 10.15):
        a.add("Body", sh.box((13.5, 0.3, 0.45), frame).transformed(T(0, y, -0.1)))
    for x in (-6.6, 6.6):
        a.add("Body", sh.box((0.3, 6.6, 0.45), frame).transformed(T(x, 7.0, -0.1)))
    a.add("Body", sh.box((13.2, 6.2, 0.1), frame).transformed(T(0, 7.0, -0.35)))
    a.add("Glow", sh.box((13.0, 0.16, 0.5), None).transformed(T(0, 10.38, 0.0)))
    landmark(a, "PolishV10", ["ScrapYardGuide", "DowntownGuide", "IndustrialGuide", "MilitaryGuide", "FutureDistrictGuide", "ChaosCoreGuide", "CommunityBoard"],
             fit="box", keep=["Board"], tint={"Glow": "Trim"}, colliders=[box_collider("Sign", (13.6, 10.4, 0.6), (0, 5.2, 0))])
    return a
