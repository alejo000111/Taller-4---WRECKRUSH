import numpy as np

from wr3d import Asset, Material, T, R, S, compose
from wr3d import shapes as sh
from _destructible import destructible, collider, animate


def island_boss(name, budget, eye, core, hitbox, roles=("ArmL", "ArmR"), motions=None, radius=24.0):
    a = Asset(name, budget=budget, atlas=1024, ao_radius=1.2, ao_strength=0.6, edge_width=0.08, gradient=0.1, highlight=0.5, preview_radius=radius,
              views=[("FRONT 3/4", 215, 10), ("FRONT", 180, 4), ("SIDE", 270, 6), ("BACK 3/4", 35, 14)])
    a.role("Body", "surface")
    for role in roles:
        a.role(role, "surface")
    a.role("Eyes", "neon", color=eye)
    a.role("Core", "neon", color=core)
    destructible(a, "Event")
    size, center = hitbox
    collider(a, "Hitbox", size, center)
    for role, kind in (motions or {"ArmL": "Arm", "ArmR": "Arm", "Core": "Core"}).items():
        animate(a, role, kind)
    a.meta["destructible"]["sockets"] = []
    return a


def socket(a, name, center, yaw=0.0):
    a.meta["destructible"]["sockets"].append({"name": name, "center": [float(v) for v in center], "rotation": [0.0, float(yaw), 0.0]})


def ring_sockets(a, prefix, count, radius, heights, start=0.0):
    for i in range(count):
        angle = np.radians(start + i * 360.0 / count)
        x, z = -np.sin(angle) * radius, -np.cos(angle) * radius
        yaw = np.degrees(angle)
        socket(a, f"{prefix}{i + 1}", (x, heights[i % len(heights)], z), yaw)


def part_asset(name, budget, glow, hitbox, radius=8.0, motion=None):
    a = Asset(name, budget=budget, atlas=512, ao_radius=0.5, ao_strength=0.55, edge_width=0.06, gradient=0.08, highlight=0.5, preview_radius=radius,
              views=[("FRONT 3/4", 215, 12), ("FRONT", 180, 4), ("SIDE", 270, 6), ("TOP", 200, 50)])
    a.role("Body", "surface")
    a.role("Glow", "neon", color=glow)
    destructible(a, "Event")
    size, center = hitbox
    collider(a, "Hitbox", size, center)
    if motion:
        animate(a, "Glow", motion)
    return a


def tire(radius, width, mat, rim_mat=None, segments=14):
    out = sh.torus(radius - width * 0.35, width * 0.5, mat, segments, 6)
    if rim_mat is not None:
        hub = sh.cylinder(radius * 0.55, width * 0.7, rim_mat, bevel=0.06, segments=10)
        out = [out, hub.transformed(T(0, -width * 0.35, 0))]
    return out


def add_all(a, role, meshes, m):
    if not isinstance(meshes, (list, tuple)):
        meshes = [meshes]
    for mesh in meshes:
        a.add(role, mesh.transformed(m))


def piston(a, role, start, end, outer, inner, mat_outer, mat_inner):
    start, end = np.asarray(start, float), np.asarray(end, float)
    direction = end - start
    length = np.linalg.norm(direction)
    mid = start + direction * 0.55
    a.add(role, sh.sweep([tuple(start), tuple(mid)], outer, 8, mat_outer, samples=2))
    a.add(role, sh.sweep([tuple(mid - direction * 0.05), tuple(end)], inner, 8, mat_inner, samples=2))
    return length


def spikes(a, role, base, count, length, radius, mat, spread=35.0, tilt=20.0, seed=1):
    rng = np.random.default_rng(seed)
    for i in range(count):
        yaw = -spread + 2 * spread * (i / max(count - 1, 1)) + rng.uniform(-6, 6)
        pitch = tilt + rng.uniform(-8, 8)
        size = length * rng.uniform(0.75, 1.15)
        spike = sh.gem(radius * rng.uniform(0.8, 1.2), size, 6, mat, crown=0.15)
        a.add(role, spike.transformed(compose(T(*base), R(0, yaw, 0), R(-pitch, 0, 0))))


def scale_asset(a, factor):
    for role, meshes in a.parts.items():
        a.parts[role] = [m.transformed(S(factor)) for m in meshes]
    info = a.meta["destructible"]
    for item in info["colliders"]:
        item["center"] = [round(v * factor, 4) for v in item["center"]]
        item["size"] = [round(v * factor, 4) for v in item["size"]]
    for item in info.get("sockets", []):
        item["center"] = [round(v * factor, 4) for v in item["center"]]
    return a
