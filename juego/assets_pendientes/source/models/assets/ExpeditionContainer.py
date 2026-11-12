from wr3d import Material, T
from wr3d import shapes as sh
from _expedition_lib import FROST, expedition_asset
from _landmark_lib import patch

W, H, D = 17.0, 12.0, 28.0


def build():
    a = expedition_asset("ExpeditionContainer", 600, 17.0, atlas=512)
    a.role("Shell", "surface", skin="Shell", color=(66, 114, 145))
    shell = Material("corrugated", color=(255, 255, 255), under=(110, 104, 96), pitch=0.6, axis=0, depth=0.07, wear=0.35, scratches=0.4, rough=0.5, dirt=0.45, skin=True)
    frame = Material("metal", color=(60, 66, 72), rough=0.45, polish=0.3, dirt=0.5, scratches=0.4)
    snow = Material("terrain_rock", color=(236, 243, 249), cap=(240, 246, 250), cap_amount=1.0, dirt=0.0)
    a.add("Shell", sh.box((W - 0.6, H - 0.6, D - 0.6), shell).transformed(T(0, H / 2, 0)))
    for x in (-W / 2 + 0.3, W / 2 - 0.3):
        for z in (-D / 2 + 0.3, D / 2 - 0.3):
            a.add("Body", sh.box((0.7, H, 0.7), frame).transformed(T(x, H / 2, z)))
    for y in (0.3, H - 0.3):
        for x in (-W / 2 + 0.3, W / 2 - 0.3):
            a.add("Body", sh.box((0.6, 0.6, D), frame).transformed(T(x, y, 0)))
        for z in (-D / 2 + 0.3, D / 2 - 0.3):
            a.add("Body", sh.box((W, 0.6, 0.6), frame).transformed(T(0, y, z)))
    for x in (-3.0, -1.0, 1.0, 3.0):
        a.add("Body", sh.box((0.25, H - 1.6, 0.3), frame).transformed(T(x, H / 2, D / 2 - 0.1)))
    a.add("Body", sh.box((W - 1.0, 0.5, D - 1.0), snow).transformed(T(0, H + 0.2, 0)))
    patch(a, [FROST], ["FreightContainer"], remove=["ContainerRib"], tint=["Shell"])
    return a
