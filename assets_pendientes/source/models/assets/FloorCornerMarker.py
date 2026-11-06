from wr3d import Material, T
from wr3d import shapes as sh
from _building_lib import building_asset, steel
from _bay_lib import STATIONS, DESIGN, corner_brackets
from _landmark_lib import landmark

W, D = 12.0, 9.9


def build():
    a = building_asset("FloorCornerMarker", 300, 7.0, atlas=256)
    a.role("Glow", "neon", color=(202, 140, 57))
    channel = steel((40, 46, 56), dirt=0.5)
    a.add("Body", corner_brackets(W, D, 2.3, 2.1, 0.06, 0.03, channel))
    a.add("Glow", corner_brackets(W - 0.08, D - 0.08, 2.0, 1.8, 0.09, 0.045, None))
    names = ["DailyPad_Markers", "RebirthAltar_Markers", "QuestBoard_EdgeAccents", "ToolRack_EdgeAccents", "UpgradeStation_EdgeAccents", "ChaosShopTerminal_EdgeAccents"]
    landmark(a, [STATIONS, DESIGN], names, fit="box", tint={"Glow": "CornerLong"})
    return a
