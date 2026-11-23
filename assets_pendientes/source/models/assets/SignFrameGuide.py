from _frame_lib import frame_asset, sign_frame


def build():
    a = frame_asset("SignFrameGuide", 700, 8.0)
    sign_frame(a, 13.0, 6.0, 0.5, 0.45)
    a.meta["frame"] = {"part": "Board", "size": [13.0, 6.0, 0.5], "scope": "Map"}
    return a
