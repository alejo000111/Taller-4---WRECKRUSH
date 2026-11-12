from _expedition_lib import VERDANT, FROST, SKY, expedition_asset, terrain, boulder
from _landmark_lib import patch


def build():
    a = expedition_asset("VerdantRock", 400, 7.0)
    rock = terrain("verdant")
    a.add("Body", boulder(3, (10.0, 6.0, 8.0), rock, segments=11, rings=7))
    patch(a, [VERDANT], ["IslandCliff", "Outcrop"], remove=["Moss"])
    return a
