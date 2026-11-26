from _frame_lib import frame_asset, sign_frame


def build():
    a = frame_asset("SignFrameGate", 700, 9.0)
    sign_frame(a, 14.0, 8.0, 0.6, 0.7)
    a.meta["frame"] = {"part": "Sign", "size": [14.0, 8.0, 0.6], "scope": "Map"}
    return a
