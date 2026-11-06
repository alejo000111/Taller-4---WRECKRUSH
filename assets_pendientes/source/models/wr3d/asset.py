import json
import os
import time

import numpy as np
from PIL import Image

from .bake import bake
from .gltf import compute_tangents, write_glb
from .mesh import Mesh
from .render import Item, contact_sheet

ROLE_KINDS = ("surface", "neon", "glass", "plain", "foil")

DEFAULT_VIEWS = [
    ("FRONT 3/4", 35, 18),
    ("BACK 3/4", 215, 22),
    ("SIDE", 90, 4),
    ("TOP", 160, 62),
]


class RoleSpec:
    def __init__(self, name, kind="surface", color=(255, 255, 255), skin=None, material=None, transparency=0.0, overlay=None):
        if kind not in ROLE_KINDS:
            raise ValueError(f"role kind must be one of {ROLE_KINDS}")
        self.name = name
        self.kind = kind
        self.color = tuple(int(c) for c in color)
        self.skin = skin
        self.material = material or {"surface": "Metal", "neon": "Neon", "glass": "Glass", "plain": "SmoothPlastic", "foil": "Foil"}[kind]
        self.transparency = transparency
        self.overlay = (skin is not None and kind == "surface") if overlay is None else overlay


class Asset:
    def __init__(self, name, budget, atlas=1024, ao_radius=0.4, ao_strength=0.6, normal_strength=1.0, max_triangles=20000, views=None, preview_radius=None, edge_width=0.05, vertex_edge=0.0, gradient=0.12, highlight=0.6):
        self.name = name
        self.atlas = atlas
        self.ao_radius = ao_radius
        self.ao_strength = ao_strength
        self.normal_strength = normal_strength
        self.max_triangles = max_triangles
        self.budget = budget
        self.edge_width = edge_width
        self.vertex_edge = vertex_edge
        self.gradient = gradient
        self.highlight = highlight
        self.roles = {}
        self.parts = {}
        self.points = {}
        self.views = views or DEFAULT_VIEWS
        self.preview_radius = preview_radius
        self.meta = {}

    def role(self, name, kind="surface", color=(255, 255, 255), skin=None, material=None, transparency=0.0, overlay=None):
        self.roles[name] = RoleSpec(name, kind, color, skin, material, transparency, overlay)
        self.parts.setdefault(name, [])
        return self

    def add(self, role, *meshes):
        if role not in self.roles:
            raise KeyError(f"declare role {role} first")
        for m in meshes:
            if isinstance(m, (list, tuple)):
                self.add(role, *m)
            elif m is not None:
                self.parts[role].append(m)
        return self

    def point(self, name, pos):
        self.points[name] = [float(x) for x in pos]
        return self

    def merged(self):
        out = {}
        for name, meshes in self.parts.items():
            m = Mesh.merge(meshes)
            if m is not None:
                out[name] = m
        return out

    def build(self, out_dir, preview=True, quick=False):
        start = time.time()
        os.makedirs(out_dir, exist_ok=True)
        merged = self.merged()
        if not merged:
            raise RuntimeError("asset has no geometry")
        total = sum(len(m.tri) for m in merged.values())
        detail = ", ".join(f"{n}:{len(m.tri)}" for n, m in merged.items())
        if total > 20000:
            raise RuntimeError(f"{self.name} has {total} triangles ({detail}); over the 20k hard limit")
        if total > self.budget:
            raise RuntimeError(f"{self.name} has {total} triangles ({detail}); budget is {self.budget}")
        for name, m in merged.items():
            if len(m.tri) > self.max_triangles:
                raise RuntimeError(f"role {name} has {len(m.tri)} triangles (limit {self.max_triangles})")
        surface_names = [n for n in merged if self.roles[n].kind == "surface"]
        all_tris = np.concatenate([m.pos[m.tri] for m in merged.values()])
        uvs = {n: np.zeros((len(m.pos), 2)) for n, m in merged.items()}
        maps = None
        k = 0.0
        if surface_names:
            atlas = 256 if quick else self.atlas
            maps, per_uv, k = bake([merged[n] for n in surface_names], [self.roles[n] for n in surface_names], all_tris, atlas, ao_radius=self.ao_radius, ao_strength=self.ao_strength, normal_strength=self.normal_strength, edge_width=self.edge_width, vertex_edge=self.vertex_edge, gradient=self.gradient, highlight=self.highlight)
            for n, uv in zip(surface_names, per_uv):
                uvs[n] = uv
            rgba = np.concatenate([maps["color"], maps["alpha"][..., None]], -1)
            Image.fromarray((np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(out_dir, f"{self.name}_color.png"))
            Image.fromarray((np.clip(maps["normal"] * 0.5 + 0.5, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB").save(os.path.join(out_dir, f"{self.name}_normal.png"))
            Image.fromarray((np.clip(maps["roughness"], 0, 1) * 255 + 0.5).astype(np.uint8), "L").save(os.path.join(out_dir, f"{self.name}_roughness.png"))
            Image.fromarray((np.clip(maps["metalness"], 0, 1) * 255 + 0.5).astype(np.uint8), "L").save(os.path.join(out_dir, f"{self.name}_metalness.png"))
        nodes = []
        tangents = {}
        manifest_roles = {}
        for n, m in merged.items():
            spec = self.roles[n]
            tan = compute_tangents(m.pos, m.nrm, uvs[n], m.tri)
            tangents[n] = tan
            nodes.append({"name": n, "pos": m.pos, "nrm": m.nrm, "uv": uvs[n], "tri": m.tri, "tan": tan, "color": spec.color})
            lo, hi = m.pos.min(0), m.pos.max(0)
            fallback = None
            if spec.kind == "surface" and not spec.overlay and maps is not None:
                h, w = maps["color"].shape[:2]
                xs = np.clip((uvs[n][:, 0] * w).astype(int), 0, w - 1)
                ys = np.clip((uvs[n][:, 1] * h).astype(int), 0, h - 1)
                fallback = [int(round(c * 255)) for c in maps["color"][ys, xs].mean(0)]
            manifest_roles[n] = {
                "kind": spec.kind,
                "material": spec.material,
                "color": list(spec.color),
                "skin": spec.skin,
                "overlay": bool(spec.overlay),
                "transparency": spec.transparency,
                "triangles": int(len(m.tri)),
                "vertices": int(len(m.pos)),
                "center": [float(x) for x in (lo + hi) / 2],
                "size": [float(x) for x in hi - lo],
            }
            if fallback:
                manifest_roles[n]["fallback"] = fallback
        glb_path = os.path.join(out_dir, f"{self.name}.glb")
        write_glb(glb_path, nodes)
        editable = {}
        for node in nodes:
            editable[node["name"]] = {
                "p": np.round(node["pos"], 4).ravel().tolist(),
                "n": np.round(node["nrm"], 3).ravel().tolist(),
                "u": np.round(node["uv"], 5).ravel().tolist(),
                "t": node["tri"].ravel().tolist(),
            }
        with open(os.path.join(out_dir, "editable.json"), "w", encoding="utf-8") as f:
            json.dump(editable, f, separators=(",", ":"))
        manifest = {
            "name": self.name,
            "atlas": self.atlas,
            "texel_density": float(k),
            "triangles": int(total),
            "budget": self.budget,
            "roles": manifest_roles,
            "points": self.points,
            "textures": {key: f"{self.name}_{key}.png" for key in ("color", "normal", "roughness", "metalness")} if surface_names else {},
            "meta": self.meta,
        }
        with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        if preview:
            items = []
            for n, m in merged.items():
                spec = self.roles[n]
                kind = spec.kind
                item_maps = maps if kind == "surface" else None
                items.append(Item(m.pos, m.nrm, m.tri, kind, spec.color, uvs[n], tangents[n], item_maps, spec.transparency))
            lo = np.min([m.pos.min(0) for m in merged.values()], axis=0)
            hi = np.max([m.pos.max(0) for m in merged.values()], axis=0)
            center = (lo + hi) / 2
            radius = self.preview_radius or np.linalg.norm(hi - lo) / 2
            tri_total = sum(len(m.tri) for m in merged.values())
            title = f"{self.name}  |  {tri_total} / {self.budget} tris  |  {len(merged)} parts  |  {k:.0f} px/stud"
            contact_sheet(items, center, radius, self.views, os.path.join(out_dir, "preview.png"), title=title)
        manifest["build_seconds"] = round(time.time() - start, 1)
        return manifest
