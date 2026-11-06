def destructible(asset, zone):
    asset.meta["destructible"] = {"zone": zone, "colliders": []}
    return asset


def collider(asset, name, size, center, shape="Block", rotation=(0.0, 0.0, 0.0)):
    if shape not in ("Block", "Cylinder", "Ball"):
        raise ValueError("collider shape must be Block, Cylinder or Ball")
    asset.meta["destructible"]["colliders"].append({
        "name": name,
        "shape": shape,
        "size": [round(float(v), 4) for v in size],
        "center": [round(float(v), 4) for v in center],
        "rotation": [round(float(v), 4) for v in rotation],
    })
    return asset


def animate(asset, role, kind):
    asset.meta["destructible"].setdefault("motion", {})[role] = kind
    return asset
