import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _military_lib import olive, star, OLIVE_DARK, STENCIL, YELLOW, INK, SAND, KHAKI
from SandbagWall import sandbag

SHELL_Z0 = -7.0
SHELL_Z1 = 9.0
SHELL_TOP = 7.6
OBS_Y = SHELL_TOP
OBS_TOP = 10.6


def concrete(decals=(), color=(150, 152, 146)):
    return Material("concrete", color=color, dirt=0.55, decals=list(decals))


def form_ties(width, height, cols, rows):
    out = []
    for i in range(cols):
        for j in range(rows):
            out.append({"type": "circle", "center": (-width / 2 + (i + 0.5) * width / cols, -height / 2 + (j + 0.5) * height / rows), "radius": 0.08, "darken": 0.6, "raise": -0.01})
    for i in range(1, cols):
        out.append({"type": "rect", "center": (-width / 2 + i * width / cols, 0.0), "size": (0.04, height), "darken": 0.35, "raise": -0.005})
    return out


def shell_front():
    return concrete([
        {"type": "text", "text": "B-12", "center": (-6.6, -5.7), "height": 2.2, "color": (40, 42, 38), "font": "impact", "wear": 0.45},
        {"type": "rect", "center": (6.6, -5.9), "size": (4.6, 1.3), "color": YELLOW, "wear": 0.35},
        {"type": "text", "text": "DANGER", "center": (6.6, -5.9), "height": 0.9, "color": INK, "font": "impact", "wear": 0.35},
        {"type": "text", "text": "AUTHORIZED PERSONNEL ONLY", "center": (6.6, -4.9), "height": 0.32, "color": INK, "font": "impact", "wear": 0.4},
        *[{"type": "rect", "center": (x, -3.9), "size": (0.04, 7.0), "darken": 0.35, "raise": -0.005} for x in (-9.0, -3.0, 3.0, 9.0)],
        {"type": "rect", "center": (0.0, -4.3), "size": (24.0, 0.05), "darken": 0.35, "raise": -0.005},
    ])


def flag(mat):
    sheet = sh.plane((2.4, 1.6), mat, divisions=(8, 2))
    sheet = sheet.transformed(R(90, 0, 0))
    x = sheet.pos[:, 0] + 1.2
    sheet.pos[:, 2] += 0.18 * np.sin(x * 2.4) * (x / 2.4)
    sheet = sh.recompute_normals(sheet)
    back = sheet.flipped()
    return [sheet, back]


def build():
    a = Asset("Bunker", budget=6000, atlas=1024, ao_radius=1.6, edge_width=0.12, preview_radius=15.0,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=(255, 210, 31))

    slab = concrete([{"type": "stripes", "center": (0.0, -9.8), "size": (24.0, 0.5), "width": 0.4, "color": YELLOW, "wear": 0.5}], color=(120, 120, 116))
    a.add("Body", sh.rounded_box((24.0, 0.6, 20.0), 0.05, 1, slab, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(T(0, 0.3, 1.0)))

    body_mat = concrete(form_ties(16.0, 7.6, 6, 3))
    poly = [(-12.4, 0.6), (12.4, 0.6), (10.2, SHELL_TOP), (-10.2, SHELL_TOP)]
    shell = sh.extrude(poly, SHELL_Z1 - SHELL_Z0, body_mat, bevel=0.15, corner_radius=0.0, cap_mats=[concrete(), shell_front()])
    shell = shell.transformed(T(0, 0, (SHELL_Z0 + SHELL_Z1) / 2))
    a.add("Body", shell)
    earth = Material("military_burlap", color=(112, 104, 72), dirt=0.6)
    for sx in (-1, 1):
        berm = sh.extrude([(0.0, 0.6), (1.4, 0.6), (0.0, 4.0)], SHELL_Z1 - SHELL_Z0 - 1.0, earth, bevel=0.2, corner_radius=0.0)
        a.add("Body", berm.transformed(compose(T(sx * 12.2, 0, (SHELL_Z0 + SHELL_Z1) / 2), S(sx, 1, 1))))

    top_view = [(3.2, 0.0), (9.6, 0.0), (9.6, 2.0), (4.6, 3.2), (3.2, 3.2)]
    for sx in (-1, 1):
        bastion = sh.extrude([(x, y) for x, y in top_view], 3.6, concrete(form_ties(6.4, 3.2, 3, 1)), bevel=0.12, corner_radius=0.0)
        bastion = bastion.transformed(compose(T(0, 0.6 + 1.8, SHELL_Z0), S(sx, 1, 1), R(-90, 0, 0), S(1, 1, -1)))
        a.add("Body", bastion)

    door_mat = Material("diamondplate", color=(110, 104, 88), pitch=0.4, dirt=0.6, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (4.2, 4.8), "outline": 0.08, "darken": 0.5, "raise": -0.01},
        {"type": "rivets", "points": [(x, y) for x in (-1.9, 1.9) for y in np.linspace(-2.1, 2.1, 6)], "radius": 0.08, "color": (90, 90, 86), "height": 0.02},
    ])
    a.add("Body", sh.rounded_box((4.4, 5.0, 0.4), 0.05, 1, door_mat, faces=["-z", "+x", "-x", "+y", "-y"]).transformed(T(0, 3.1, SHELL_Z0 - 0.15)))
    wheel = olive((70, 70, 66), metal=0.6, wear=0.3)
    a.add("Body", sh.torus(0.55, 0.07, wheel, segments=12, sides=4).transformed(compose(T(1.2, 3.1, SHELL_Z0 - 0.45), R(90, 0, 0))))
    for ang in (0, 60, 120):
        a.add("Body", sh.box((1.05, 0.07, 0.07), wheel).transformed(compose(T(1.2, 3.1, SHELL_Z0 - 0.45), R(0, 0, ang))))
    hazard = Material("hazard", color=YELLOW, color2=INK, width=0.35, angle=45, wear=0.4, dirt=0.4)
    for x in (-2.6, 2.6):
        a.add("Body", sh.rounded_box((0.6, 5.6, 0.5), 0.04, 1, hazard).transformed(T(x, 3.4, SHELL_Z0 - 0.25)))
    a.add("Body", sh.rounded_box((5.8, 0.6, 0.5), 0.04, 1, hazard).transformed(T(0, 6.2, SHELL_Z0 - 0.25)))

    obs = concrete(form_ties(12.0, 3.0, 4, 1) + [{"type": "rect", "center": (0.0, -0.2), "size": (8.0, 0.6), "color": (14, 14, 14), "wear": 0.0, "raise": -0.03}])
    a.add("Body", sh.rounded_box((12.0, OBS_TOP - OBS_Y - 0.6, 9.0), 0.1, 1, concrete(), faces=["+x", "-x", "+z", "-z"], face_mats={"-z": obs}).transformed(T(0, (OBS_Y + OBS_TOP - 0.6) / 2, 0.5)))
    a.add("Body", sh.rounded_box((13.0, 0.6, 10.0), 0.08, 1, concrete(color=(132, 134, 128))).transformed(T(0, OBS_TOP - 0.3, 0.5)))
    a.add("Body", sh.box((8.4, 0.25, 0.9), concrete(color=(132, 134, 128))).transformed(T(0, OBS_Y + 1.25, -4.4)))

    rng = np.random.default_rng(5)
    for k, (x, z, yaw) in enumerate([(-8.0, -4.2, 4), (-8.0, -2.6, -3), (-8.0, -3.4, 90), (7.6, 5.4, 2), (7.6, 6.9, -4), (8.2, 3.6, 88)]):
        mat = Material("military_burlap", color=[SAND, KHAKI][k % 2], dirt=0.5)
        bag = sandbag(mat, rng)
        layer = 1 if k in (2, 5) else 0
        a.add("Body", bag.transformed(compose(T(x, SHELL_TOP + 0.4 + layer * 0.75, z), R(0, yaw, 0))))

    vent = olive((80, 82, 76), metal=0.5, wear=0.4)
    for x, z in ((-7.5, 6.0), (-5.0, 6.8)):
        a.add("Body", sh.lathe([(0.0, 0.0), (0.4, 0.0), (0.4, 0.9), (0.75, 1.0), (0.7, 1.25), (0.0, 1.4)], 10, vent, smooth_angle=40).transformed(T(x, SHELL_TOP, z)))
    mast = olive((60, 62, 56), metal=0.5)
    a.add("Body", sh.cylinder(0.1, 3.0, mast, bevel=0.0, segments=6).transformed(T(4.5, OBS_TOP + 1.5, 4.0)))
    a.add("Glow", sh.sphere(0.28, None, 8, 4).transformed(T(4.5, OBS_TOP + 3.15, 4.0)))
    a.add("Body", sh.cylinder(0.08, 5.0, mast, bevel=0.0, segments=6).transformed(T(-9.5, SHELL_TOP + 2.5, 8.0)))
    cloth = Material("canvas", stripes=[YELLOW], stripe_width=1.0, axis=0, dirt=0.3, decals=star((0.0, 0.0), 1.1, INK, wear=0.2))
    a.add("Body", [part.transformed(T(-9.5 + 1.25, SHELL_TOP + 4.1, 8.0)) for part in flag(cloth)])

    destructible(a, "Military")
    collider(a, "Hitbox", (22.0, SHELL_TOP, SHELL_Z1 - SHELL_Z0), (0, SHELL_TOP / 2, (SHELL_Z0 + SHELL_Z1) / 2))
    collider(a, "Slab", (24.0, 0.6, 20.0), (0, 0.3, 1.0))
    collider(a, "Observation", (12.0, OBS_TOP - OBS_Y, 9.0), (0, (OBS_Y + OBS_TOP) / 2, 0.5))
    collider(a, "LeftBastion", (6.0, 3.6, 3.0), (-6.4, 2.4, SHELL_Z0 - 1.5))
    collider(a, "RightBastion", (6.0, 3.6, 3.0), (6.4, 2.4, SHELL_Z0 - 1.5))
    return a

