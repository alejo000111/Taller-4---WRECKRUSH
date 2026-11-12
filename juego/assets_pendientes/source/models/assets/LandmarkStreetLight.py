from StreetLamp import build as street_lamp, POLE_Z, POLE_TOP
from _landmark_lib import landmark, box_collider


def build():
    a = street_lamp()
    a.name = "LandmarkStreetLight"
    landmark(a, "Zones/Downtown/Landmarks", "StreetLight", fit="box", colliders=[box_collider("Pole", (0.6, POLE_TOP, 0.6), (0, POLE_TOP / 2, POLE_Z))])
    return a
