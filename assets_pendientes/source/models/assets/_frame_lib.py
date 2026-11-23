from wr3d import Asset, Material, T
from wr3d import shapes as sh
from _building_lib import steel


def frame_asset(name, budget, radius):
    a = Asset(name, budget=budget, atlas=512, ao_radius=0.25, ao_strength=0.5, edge_width=0.05, gradient=0.06, highlight=0.5, preview_radius=radius,
              views=[("FRONT 3/4", 200, 10), ("FRONT", 180, 2), ("SIDE", 270, 2), ("BACK", 0, 4)])
    a.role("Body", "surface")
    return a


def sign_frame(a, width, height, thickness, border, lip=None, depth=0.16):
    bar = steel((46, 50, 58))
    cap = Material("hazard", color=(255, 196, 40), color2=(26, 26, 30), width=0.22, angle=45, wear=0.35, dirt=0.3)
    lip = min(0.12, border * 0.25) if lip is None else lip
    deep = thickness + 2 * depth
    bevel = min(0.06, border * 0.2)
    span_x = width + 2 * border - 2 * lip
    offset_y = height / 2 + border / 2 - lip
    offset_x = width / 2 + border / 2 - lip
    for sign in (-1, 1):
        a.add("Body", sh.box((span_x, border, deep), bar).transformed(T(0, sign * offset_y, 0)))
        a.add("Body", sh.box((border, height - 2 * lip, deep), bar).transformed(T(sign * offset_x, 0, 0)))
    size = border * 1.4
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * (width / 2 + border / 2 - lip)
            y = sy * (height / 2 + border / 2 - lip)
            a.add("Body", sh.rounded_box((size, size, deep + 0.08), bevel, 1, cap).transformed(T(x, y, 0)))
    return a
