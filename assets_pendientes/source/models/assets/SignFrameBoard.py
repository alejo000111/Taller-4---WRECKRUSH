from wr3d import T
from wr3d import shapes as sh
from _building_lib import steel
from _frame_lib import frame_asset, sign_frame

LEG_X = 7.0
LEG_LENGTH = 8.0
LEG_TOP = 9.0 / 2 + 0.8 - 0.12


def build():
    a = frame_asset("SignFrameBoard", 900, 13.0)
    a.role("Leg", "surface")
    sign_frame(a, 22.0, 9.0, 1.0, 0.8)
    post = steel((46, 50, 58))
    for side in (-1, 1):
        a.add("Leg", sh.rounded_box((1.0, LEG_LENGTH, 1.0), 0.1, 1, post).transformed(T(side * LEG_X, -LEG_TOP - LEG_LENGTH / 2, 0)))
    a.meta["frame"] = {
        "part": ["Board", "EncounterBoard"],
        "size": [22.0, 9.0, 1.0],
        "scope": "Map",
        "legs": {"role": "Leg", "x": LEG_X, "top": LEG_TOP, "sink": 0.4},
    }
    return a
