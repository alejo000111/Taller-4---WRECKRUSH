import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider
from _junktower_parts import crate, crush, fold, aim, i_beam, tire, chain, FACE_YAW, STEEL

YELLOW = (255, 210, 31)
ORANGE = (255, 122, 26)
CHARCOAL = (42, 44, 52)
INK = (22, 22, 26)
BLUE = (66, 104, 156)
RED = (168, 54, 44)
TEAL = (44, 138, 134)
MUSTARD = (222, 172, 44)
RUSTY = (150, 62, 24)
CREAM = (214, 206, 186)
BEACON_SCALE = 1.25

BALES = [
    ((9.2, 3.5, 7.6), (-0.2, 2.35, 0.15), (0.0, 10.0, 1.0), BLUE, (1, 1, -1)),
    ((8.4, 2.9, 6.8), (0.7, 5.65, -0.3), (-2.0, -24.0, 0.5), RED, (-1, 1, 1)),
    ((8.6, 3.4, 6.4), (0.1, 8.35, 0.35), (1.5, 6.0, -2.5), TEAL, (1, 1, 1)),
    ((7.6, 2.8, 6.6), (-0.6, 11.55, -0.2), (0.0, -18.0, 3.0), MUSTARD, (-1, 1, -1)),
    ((7.0, 3.2, 5.8), (0.3, 14.15, -0.6), (-3.0, 24.0, -1.0), RUSTY, (1, 1, 1)),
]


def bale_frame(spec):
    size, (x, y0, z), (rx, ry, rz) = spec[:3]
    return compose(T(x, y0 + size[1] / 2, z), R(rx, ry, rz))


def on_face(xf, face, local):
    return compose(xf, T(*local), R(0, FACE_YAW[face], 0))


def point(xf, local):
    return (xf @ np.append(np.asarray(local, dtype=np.float64), 1.0))[:3]


def build():
    a = Asset("JunkTower", budget=6000, atlas=1024, ao_radius=1.0, edge_width=0.1, preview_radius=11.5,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=ORANGE)

    dark = Material("junktower_scrap", color=(64, 64, 70), palette=[RUSTY, (96, 98, 106), (40, 40, 44)], layer=0.4, mix=0.45, glass=0.0, trim=0.1,
                    wear=0.45, chips=0.2, bloom=0.5, soot=0.55, seed=11)
    steel = Material("junktower_scrap", color=(70, 72, 80), wear=0.45, chips=0.22, bloom=0.35, soot=0.3, rough=0.5, seed=12)
    hazard = Material("hazard", color=YELLOW, color2=INK, width=0.45, wear=0.55, scratches=0.4, dirt=0.5)
    rubber = Material("rubber", color=(34, 34, 38), pattern="knurl", freq=4.0, depth=0.02, dirt=0.55)
    rim = Material("junktower_scrap", color=(150, 152, 158), wear=0.5, chips=0.15, bloom=0.6, soot=0.2, seed=13)

    a.add("Body", [i_beam(12.4, steel).transformed(compose(T(0, 0.31, z), R(0, 90, 0))) for z in (-4.2, 4.2)])
    plate = sh.rounded_box((12.2, 0.32, 11.8), 0.06, 1, steel, faces=["+x", "-x", "+y", "+z", "-z"], face_mats={"-z": hazard, "+z": hazard, "+x": hazard, "-x": hazard})
    plate.uv[plate.vchart == 2] *= 0.5
    a.add("Body", plate.transformed(T(0, 0.78, 0)))
    slab_size = (11.0, 1.6, 10.4)
    slab = crate(slab_size, (6, 2, 6), dark, faces=["+x", "-x", "+y", "+z", "-z"], uv_scale={"+y": 0.45})
    crush(slab, slab_size, 5, ripple=0.08, jitter=0.12, sag=0.06, dent=0.3, corner=(-1, 1, 1), twist=0.0)
    a.add("Body", slab.transformed(compose(T(0, 1.62, 0), R(0, 4, 0))))

    frames = []
    for i, spec in enumerate(BALES):
        size, _, _, color, corner = spec
        xf = bale_frame(spec)
        frames.append(xf)
        top = i == len(BALES) - 1
        others = [c for c in (BLUE, RED, TEAL, MUSTARD, CREAM, STEEL) if c != color]
        mat = Material("junktower_scrap", color=color, palette=others, layer=0.46, mix=0.2, segment=2.6, straps=(-size[0] * 0.3, size[0] * 0.3),
                       frame=np.linalg.inv(xf), seed=i + 1, wear=0.75 if top else 0.5, chips=0.12 if top else 0.2, bloom=0.85 if top else 0.4,
                       soot=0.35, streaks=0.5, glass=0.0 if top else 0.06)
        face_mats = {}
        if i == 0:
            face_mats["-z"] = mat.but(decals=[
                {"type": "text", "text": "JUNK", "center": (-1.7, 0.0), "height": 1.25, "angle": -5, "color": (238, 238, 230), "font": "impact", "wear": 0.55, "rough": 0.7},
            ])
        bale = crate(size, (7, 7, 6), mat, uv_scale={"+y": 1.0 if top else 0.55, "-y": 0.3}, face_mats=face_mats)
        crush(bale, size, i * 7 + 3, corner=corner)
        a.add("Body", bale.transformed(xf))

    for bale_index, face, local, tilt in ((0, "-z", (-2.6, -0.1, -3.8), 6), (2, "+x", (4.3, 0.05, 1.2), -8), (3, "+z", (-1.4, 0.0, 3.3), 10)):
        xf = on_face(frames[bale_index], face, local)
        a.add("Body", [part.transformed(compose(xf, R(tilt, 0, 0), R(0, 0, -90))) for part in tire(rubber, rim)])

    beam_mat = Material("junktower_scrap", color=(226, 178, 38), wear=0.6, chips=0.17, bloom=0.45, soot=0.3, streaks=0.4, seed=21)
    beam_dir = np.array([-0.5, 0.12, 1.0])
    beam_center = np.array([0.6, 7.1, -0.4])
    a.add("Body", i_beam(13.2, beam_mat).transformed(aim(beam_center, beam_dir)))
    beam_front = beam_center - beam_dir / np.linalg.norm(beam_dir) * 6.4

    pipe_mat = Material("junktower_scrap", color=(84, 86, 94), wear=0.5, chips=0.2, bloom=0.6, soot=0.4, seed=22)
    pipe = sh.tube(0.32, 0.22, 10.5, pipe_mat, bevel=0.0, segments=10)
    a.add("Body", pipe.transformed(compose(aim((-0.6, 13.1, -0.2), (1.0, -0.1, -0.3)), R(90, 0, 0))))

    hang = beam_front + np.array([0.0, -0.42, 0.05])
    path = [hang, hang + (-0.25, -2.4, -0.05), (hang[0] - 0.8, 1.75, hang[2] + 0.05), (hang[0] - 1.4, 1.12, hang[2] + 0.15), (hang[0] - 2.6, 1.1, hang[2] + 0.35)]
    a.add("Body", chain(path, Material("rust", steel=(96, 98, 104), amount=0.55)))

    door_mat = Material("junktower_scrap", color=CREAM, wear=0.6, chips=0.18, bloom=0.4, soot=0.3, seed=31, decals=[
        {"type": "rect", "center": (0.1, -0.42), "size": (2.6, 0.7), "radius": 0.1, "color": (34, 40, 48), "wear": 0.2, "rough": 0.2, "metal": 0.3},
        {"type": "rect", "center": (0.1, -0.42), "size": (2.6, 0.7), "radius": 0.1, "outline": 0.05, "color": (20, 20, 24), "wear": 0.2},
        {"type": "rect", "center": (1.15, 0.14), "size": (0.4, 0.1), "radius": 0.04, "color": (40, 40, 46), "wear": 0.2},
        {"type": "rect", "center": (0.0, 0.36), "size": (3.4, 0.05), "darken": 0.5, "raise": -0.006},
    ])
    door = crate((3.4, 1.9, 0.14), (5, 3, 1), door_mat)
    fold(door, 0, 0.42, -26, 1)
    a.add("Body", door.transformed(compose(T(-3.12, 7.15, -3.54), R(0, -159, 0), R(0, 0, 6))))

    hood_mat = Material("junktower_scrap", color=RED, wear=0.55, chips=0.18, bloom=0.5, soot=0.4, seed=33)
    hood = crate((3.6, 0.1, 3.0), (3, 1, 2), hood_mat)
    fold(hood, 2, 0.0, 30, 0)
    size4 = BALES[3][0]
    a.add("Body", hood.transformed(compose(frames[3], T(0.9, -size4[1] / 2 + 0.12, size4[2] / 2 + 0.2), R(0, 8, 0))))

    bumper_mat = Material("metal", color=(196, 200, 208), rough=0.24, polish=0.8, scratches=0.5, dirt=0.55)
    hz4 = size4[2] / 2
    bumper = [(-2.6, -0.62, -hz4 + 0.35), (-1.9, -0.72, -hz4 - 0.3), (-0.3, -0.85, -hz4 - 0.5), (1.3, -0.7, -hz4 - 0.38), (2.3, -0.55, -hz4 + 0.3)]
    a.add("Body", sh.sweep([point(frames[3], q) for q in bumper], 0.18, 5, bumper_mat, samples=12))

    frame_mat = Material("junktower_scrap", color=CREAM, wear=0.55, chips=0.15, bloom=0.5, seed=32)
    hx3 = BALES[2][0][0] / 2
    origin = np.array([-hx3 + 0.25, 0.4, 1.3])
    out = np.array([-1.0, 0.85, 0.0]) / np.linalg.norm([-1.0, 0.85, 0.0])
    side = np.array([0.0, 0.0, 1.0])
    twist = np.cross(out, side)
    shape = [(-1.4, -0.5, 0.0), (-1.25, 1.3, 0.08), (-0.75, 2.3, 0.35), (0.9, 2.05, -0.15), (1.35, 1.0, 0.15), (1.45, -0.5, 0.0)]
    pts = [point(frames[2], origin + side * s + out * t + twist * c) for s, t, c in shape]
    a.add("Body", sh.sweep(pts, 0.12, 4, frame_mat, samples=14))

    sign_face = Material("paint", color=YELLOW, wear=0.35, scratches=0.4, dirt=0.4, rough=0.45, decals=[
        {"type": "rect", "center": (0.0, 0.0), "size": (3.42, 1.82), "radius": 0.08, "outline": 0.09, "color": INK, "wear": 0.3},
        {"type": "text", "text": "DANGER", "center": (0.0, -0.22), "height": 0.74, "color": INK, "font": "impact", "wear": 0.3},
        {"type": "rect", "center": (0.0, 0.52), "size": (3.0, 0.42), "radius": 0.05, "color": INK, "wear": 0.3},
        {"type": "text", "text": "KEEP OUT", "center": (0.0, 0.53), "height": 0.28, "color": YELLOW, "font": "impact", "wear": 0.3},
        {"type": "rivets", "points": [(x, y) for x in (-1.55, 1.55) for y in (-0.75, 0.75)], "radius": 0.05, "height": 0.012, "color": (150, 152, 158)},
        {"type": "rect", "center": (-1.55, -0.2), "size": (0.08, 1.0), "darken": 0.35, "raise": -0.001},
        {"type": "rect", "center": (1.2, 0.1), "size": (0.06, 1.4), "darken": 0.25, "raise": -0.001},
    ])
    sign_back = Material("paint", color=CHARCOAL, wear=0.45, dirt=0.4)
    hz3 = BALES[2][0][2] / 2
    sign_xf = compose(frames[2], T(0.7, -0.05, -hz3 - 0.4), R(0, 0, -6))
    a.add("Body", sh.rounded_box((3.6, 2.0, 0.12), 0.04, 1, sign_back, face_mats={"-z": sign_face}).transformed(sign_xf))
    nail = point(frames[2], (0.65, 1.4, -hz3 - 0.05))
    wire = Material("rust", steel=(90, 92, 98), amount=0.5)
    for sx in (-1.5, 1.5):
        corner = point(sign_xf, (sx, 0.98, 0.0))
        mid = (corner + nail) / 2 + np.array([0.0, 0.06, -0.04])
        a.add("Body", sh.sweep([corner, mid, nail], 0.035, 4, wire, samples=4))

    base = point(frames[-1], (0.6, BALES[-1][0][1] / 2 - 0.3, 0.3))
    beacon_xf = compose(T(*base), S(BEACON_SCALE))
    housing = Material("junktower_scrap", color=CHARCOAL, wear=0.45, chips=0.22, bloom=0.3, soot=0.4, seed=41)
    cage = Material("metal", color=(60, 62, 70), rough=0.4, polish=0.6, dirt=0.4)
    shell = [
        sh.rounded_box((1.5, 0.45, 1.5), 0.05, 1, housing, faces=["+x", "-x", "+y", "+z", "-z"]).transformed(compose(T(0, 0.22, 0), R(0, 18, 0))),
        sh.rounded_box((0.5, 0.7, 0.5), 0.0, 1, housing, faces=["+x", "-x", "+z", "-z"]).transformed(compose(T(0, 0.8, 0), R(0, 18, 0))),
        sh.lathe([(0.0, 1.09), (0.66, 1.09), (0.66, 1.41), (0.56, 1.51), (0.0, 1.51)], 12, housing),
        sh.torus(0.62, 0.045, cage, segments=12, sides=4).transformed(T(0, 1.9, 0)),
    ]
    arch = [(0.62, 1.47), (0.62, 1.9), (0.48, 2.27), (0.0, 2.53), (-0.48, 2.27), (-0.62, 1.9), (-0.62, 1.47)]
    for ang in (45, 135):
        t = np.radians(ang)
        shell.append(sh.sweep([(r * np.cos(t), y, -r * np.sin(t)) for r, y in arch], 0.045, 4, cage, samples=9))
    a.add("Body", [m.transformed(beacon_xf) for m in shell])
    a.add("Glow", sh.lathe([(0.52, 1.45), (0.52, 1.77), (0.44, 2.13), (0.26, 2.35), (0.0, 2.43)], 12, None).transformed(beacon_xf))

    destructible(a, "ScrapYard")
    collider(a, "Hitbox", (11.0, 20.0, 11.0), (0, 10.0, 0))
    a.point("light", point(beacon_xf, (0.0, 1.95, 0.0)))
    a.point("label", (0, 21.5, 0))
    return a
