import json
import struct

import numpy as np

from .mesh import normalize


def compute_tangents(pos, nrm, uv, tri):
    p0, p1, p2 = pos[tri[:, 0]], pos[tri[:, 1]], pos[tri[:, 2]]
    w0, w1, w2 = uv[tri[:, 0]], uv[tri[:, 1]], uv[tri[:, 2]]
    e1, e2 = p1 - p0, p2 - p0
    d1, d2 = w1 - w0, w2 - w0
    r = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    r = np.where(np.abs(r) < 1e-14, 1e-14, r)
    sdir = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) / r[:, None]
    tdir = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) / r[:, None]
    tan1 = np.zeros_like(pos)
    tan2 = np.zeros_like(pos)
    for k in range(3):
        np.add.at(tan1, tri[:, k], sdir)
        np.add.at(tan2, tri[:, k], tdir)
    t = tan1 - nrm * (nrm * tan1).sum(1, keepdims=True)
    bad = np.linalg.norm(t, axis=1) < 1e-9
    if bad.any():
        helper = np.where(np.abs(nrm[bad, 1:2]) < 0.9, np.array([[0.0, 1.0, 0.0]]), np.array([[1.0, 0.0, 0.0]]))
        t[bad] = np.cross(helper, nrm[bad])
    t = normalize(t)
    w = np.where((np.cross(nrm, t) * -tan2).sum(1) < 0, -1.0, 1.0)
    return np.column_stack([t, w])


def write_glb(path, nodes, generator="wr3d"):
    blob = bytearray()
    views, accessors, meshes, gnodes, materials = [], [], [], [], []

    def add(array, component, kind, target, minmax=False):
        data = np.ascontiguousarray(array, dtype="<u4" if component == 5125 else "<f4")
        raw = data.tobytes()
        while len(blob) % 4:
            blob.append(0)
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(raw), "target": target})
        blob.extend(raw)
        acc = {"bufferView": len(views) - 1, "componentType": component, "count": int(len(data) if data.ndim == 1 else data.shape[0]), "type": kind}
        if minmax:
            acc["min"] = [float(x) for x in data.min(0)]
            acc["max"] = [float(x) for x in data.max(0)]
        accessors.append(acc)
        return len(accessors) - 1

    for node in nodes:
        pos = np.asarray(node["pos"], dtype=np.float64)
        nrm = np.asarray(node["nrm"], dtype=np.float64)
        uv = np.asarray(node["uv"], dtype=np.float64)
        tri = np.asarray(node["tri"], dtype=np.int64)
        tan = node.get("tan")
        if tan is None:
            tan = compute_tangents(pos, nrm, uv, tri)
        attrs = {
            "POSITION": add(pos, 5126, "VEC3", 34962, True),
            "NORMAL": add(nrm, 5126, "VEC3", 34962),
            "TANGENT": add(tan, 5126, "VEC4", 34962),
            "TEXCOORD_0": add(uv, 5126, "VEC2", 34962),
        }
        indices = add(tri.reshape(-1), 5125, "SCALAR", 34963)
        color = node.get("color", (255, 255, 255))
        materials.append({"name": node["name"], "pbrMetallicRoughness": {"baseColorFactor": [color[0] / 255, color[1] / 255, color[2] / 255, 1.0], "metallicFactor": 0.0, "roughnessFactor": 0.5}})
        meshes.append({"name": node["name"], "primitives": [{"attributes": attrs, "indices": indices, "material": len(materials) - 1}]})
        gnodes.append({"name": node["name"], "mesh": len(meshes) - 1})
    while len(blob) % 4:
        blob.append(0)
    doc = {
        "asset": {"version": "2.0", "generator": generator},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(gnodes)))}],
        "nodes": gnodes,
        "meshes": meshes,
        "materials": materials,
        "accessors": accessors,
        "bufferViews": views,
        "buffers": [{"byteLength": len(blob)}],
    }
    js = json.dumps(doc, separators=(",", ":")).encode("utf-8")
    while len(js) % 4:
        js += b" "
    total = 12 + 8 + len(js) + 8 + len(blob)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, total))
        f.write(struct.pack("<I4s", len(js), b"JSON"))
        f.write(js)
        f.write(struct.pack("<I4s", len(blob), b"BIN\x00"))
        f.write(bytes(blob))
