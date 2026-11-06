from wr3d import T
from wr3d import shapes as sh


def prop(asset, targets, anchor, replace, tint=None, ground=0.0):
    asset.meta["prop"] = {
        "targets": list(targets),
        "anchor": anchor,
        "replace": list(replace),
        "tint": dict(tint or {}),
        "ground": float(ground),
        "colliders": [],
    }
    return asset


def collider(asset, name, size, center, shape="Block", rotation=(0.0, 0.0, 0.0)):
    asset.meta["prop"]["colliders"].append({
        "name": name,
        "shape": shape,
        "size": [round(float(v), 4) for v in size],
        "center": [round(float(v), 4) for v in center],
        "rotation": [round(float(v), 4) for v in rotation],
    })
    return asset


def frame_ring(outer, inner, depth, mat):
    ox, oy = outer[0] / 2, outer[1] / 2
    ix, iy = inner[0] / 2, inner[1] / 2
    return [
        sh.box((outer[0], oy - iy, depth), mat).transformed(T(0, (oy + iy) / 2, 0)),
        sh.box((outer[0], oy - iy, depth), mat).transformed(T(0, -(oy + iy) / 2, 0)),
        sh.box((ox - ix, 2 * iy, depth), mat).transformed(T((ox + ix) / 2, 0, 0)),
        sh.box((ox - ix, 2 * iy, depth), mat).transformed(T(-(ox + ix) / 2, 0, 0)),
    ]
