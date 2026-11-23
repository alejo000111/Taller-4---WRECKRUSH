from _frame_lib import frame_asset, sign_frame


def build():
    a = frame_asset("SignFrameService", 700, 10.0)
    sign_frame(a, 17.0, 3.0, 0.18, 0.3)
    a.meta["frame"] = {"part": "SignPanel", "size": [17.0, 3.0, 0.18], "scope": "Map"}
    return a
