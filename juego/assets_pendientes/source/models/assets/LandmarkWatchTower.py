from WatchTower import build as watch_tower, DECK_Y, WALL_H
from _landmark_lib import landmark, box_collider


def build():
    a = watch_tower()
    a.name = "LandmarkWatchTower"
    landmark(a, "Zones/Military/Landmarks", "WatchTower", fit="box", colliders=[
        box_collider("Cabin", (11.4, WALL_H + 0.6, 11.4), (0, DECK_Y + (WALL_H + 0.6) / 2, 0)),
        box_collider("Legs", (9.0, DECK_Y, 9.0), (0, DECK_Y / 2, 0)),
    ])
    return a
