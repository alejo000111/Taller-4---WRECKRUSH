from FuelTank import build as fuel_tank
from _landmark_lib import landmark, box_collider


def build():
    a = fuel_tank()
    a.name = "LandmarkTank"
    landmark(a, "Zones/Industrial/Landmarks", "Tank", fit="box", colliders=[box_collider("Tank", (8.8, 11.0, 8.8), (0, 5.8, 0), shape="Cylinder")])
    return a
