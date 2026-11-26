def landmark(asset, parent, name, fit="box", keep=(), colliders=(), pick=None, tint=None, hide=(), bounds_all=False):
    asset.meta.pop("destructible", None)
    asset.meta.pop("station", None)
    asset.meta.pop("scatter", None)
    asset.meta["model"] = {
        "parent": parent if isinstance(parent, list) else [parent],
        "name": name,
        "fit": fit,
        "keep": list(keep),
        "colliders": list(colliders),
    }
    if pick:
        asset.meta["model"]["pick"] = list(pick)
    if tint:
        asset.meta["model"]["tint"] = dict(tint)
    if hide:
        asset.meta["model"]["hide"] = list(hide)
    if bounds_all:
        asset.meta["model"]["bounds_all"] = True
    return asset


def patch(asset, targets, parts, remove=(), lift=0.0, uniform=False, keep_height=False, tint=None, functional=False, overlay=False):
    asset.meta["patch"] = {
        "targets": list(targets),
        "parts": list(parts),
        "remove": list(remove),
        "lift": float(lift),
        "uniform": bool(uniform),
        "keep_height": bool(keep_height),
        "functional": bool(functional),
        "overlay": bool(overlay),
    }
    if tint:
        asset.meta["patch"]["tint"] = {role: True for role in tint}
    return asset


def box_collider(name, size, center, shape="Block"):
    return {"name": name, "shape": shape, "size": [float(v) for v in size], "center": [float(v) for v in center], "rotation": [0.0, 0.0, 0.0]}
