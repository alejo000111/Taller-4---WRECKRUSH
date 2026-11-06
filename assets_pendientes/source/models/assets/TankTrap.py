import numpy as np

from wr3d import Asset, Material, T, R, compose, align_y
from wr3d import shapes as sh
from _landmark_lib import landmark, box_collider
import ScrapWall


def ibeam(length, mat, w=0.5):
    h = w / 2
    f = 0.1
    poly = [(-h, -h), (h, -h), (h, -h + f), (0.06, -h + f), (0.06, h - f), (h, h - f), (h, h), (-h, h), (-h, h - f), (-0.06, h - f), (-0.06, -h + f), (-h, -h + f)]
    return sh.extrude(poly, length, mat, bevel=0.02, corner_radius=0.0)


def build():
    a = Asset("TankTrap", budget=800, atlas=512, ao_radius=0.4, edge_width=0.04, preview_radius=3.4,
              views=[("FRONT 3/4", 215, 16), ("BACK 3/4", 35, 20), ("SIDE", 270, 6), ("TOP", 200, 55)])
    a.role("Body", "surface")
    steel = Material("scrapwall_sheet", color=(90, 92, 84))
    tilt = align_y(np.array([1.0, 1.0, 1.0]) / np.sqrt(3.0)).T
    lift = 3.0 / np.sqrt(3.0) + 0.25
    for frame in (R(0, 90, 0), R(-90, 0, 0), np.eye(4)):
        beam = ibeam(6.0, steel)
        a.add("Body", beam.transformed(compose(T(0, lift, 0), tilt, frame)))
    plate = Material("metal", color=(70, 72, 66), rough=0.5, dirt=0.5)
    a.add("Body", sh.box((0.9, 0.9, 0.9), plate).transformed(compose(T(0, lift, 0), tilt)))
    landmark(a, "Zones/Military/Landmarks", "TankTrap", fit="box", colliders=[box_collider("Trap", (4.0, 3.6, 4.0), (0, 1.8, 0))])
    return a
