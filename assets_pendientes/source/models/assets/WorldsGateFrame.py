from wr3d import Material, T, R, compose
from wr3d import shapes as sh
from _expedition_lib import GATE, expedition_asset
from _landmark_lib import landmark, box_collider


def build():
    a = expedition_asset("WorldsGateFrame", 2000, 18.0, atlas=512)
    a.role("Glow", "neon", color=(140, 206, 216))
    steel = Material("metal", color=(47, 56, 69), rough=0.35, polish=0.5, dirt=0.3, scratches=0.3)
    trim = Material("metal", color=(120, 150, 170), rough=0.3, polish=0.7, dirt=0.2)
    for x in (-13.0, 13.0):
        a.add("Body", sh.rounded_box((5.2, 1.2, 6.2), 0.1, 1, steel).transformed(T(x, 0.6, 0)))
        a.add("Body", sh.rounded_box((4.0, 17.8, 5.0), 0.2, 1, steel).transformed(T(x, 1.2 + 8.9, 0)))
        for z in (-2.55, 2.55):
            a.add("Glow", sh.box((0.5, 15.0, 0.1), None).transformed(T(x, 10.5, z)))
        a.add("Body", sh.rounded_box((4.6, 0.8, 5.6), 0.1, 1, trim).transformed(T(x, 19.3, 0)))
    a.add("Body", sh.rounded_box((26.0, 1.0, 2.0), 0.1, 1, steel).transformed(T(0, 14.4, 0)))
    for x in (-8.0, 0.0, 8.0):
        a.add("Body", sh.lathe([(1.0, 0.0), (1.6, 0.4), (1.6, 0.7), (1.2, 0.9)], 10, trim, smooth_angle=40).transformed(T(x, 14.9, 0)))
        a.add("Glow", sh.lathe([(1.15, 0.85), (1.35, 0.85), (1.35, 1.0), (1.15, 1.0)], 10, None, closed=True, smooth_angle=40).transformed(T(x, 14.9, 0)))
    a.add("Body", sh.rounded_box((31.6, 0.8, 2.2), 0.1, 1, steel).transformed(T(0, 20.1, 0)))
    a.add("Body", sh.rounded_box((31.6, 0.8, 2.2), 0.1, 1, steel).transformed(T(0, 29.9, 0)))
    for x in (-15.4, 15.4):
        a.add("Body", sh.rounded_box((0.8, 10.6, 2.2), 0.1, 1, steel).transformed(T(x, 25.0, 0)))
    for z in (-1.12, 1.12):
        a.add("Glow", sh.box((30.0, 0.15, 0.06), None).transformed(T(0, 20.5, z)))
        a.add("Glow", sh.box((30.0, 0.15, 0.06), None).transformed(T(0, 29.5, z)))
    landmark(a, GATE.rsplit("/", 1)[0], "WorldsGate", fit="none", keep=["Board", "Console", "WorldOrb"],
             colliders=[box_collider("PillarL", (4.0, 19.4, 5.0), (-13.0, 9.7, 0)), box_collider("PillarR", (4.0, 19.4, 5.0), (13.0, 9.7, 0))])
    return a
