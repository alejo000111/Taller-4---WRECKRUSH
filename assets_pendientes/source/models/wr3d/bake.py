import numpy as np

from .materials import Ctx, evaluate, compose
from .mesh import normalize


def chart_entries(mesh):
    entries = []
    for ci in range(len(mesh.charts)):
        sel = np.nonzero(mesh.vchart == ci)[0]
        if len(sel) == 0:
            continue
        uv = mesh.uv[sel]
        entries.append((ci, sel, uv.min(0), uv.max(0)))
    return entries


def _shelf_pack(sizes, atlas, pad):
    order = sorted(range(len(sizes)), key=lambda i: -sizes[i][1])
    placements = [None] * len(sizes)
    x = y = shelf = 0
    for i in order:
        w, h = sizes[i]
        w += 2 * pad
        h += 2 * pad
        if w > atlas:
            return None
        if x + w > atlas:
            y += shelf
            x = 0
            shelf = 0
        if y + h > atlas:
            return None
        placements[i] = (x + pad, y + pad)
        x += w
        shelf = max(shelf, h)
    return placements


def pack(mesh, atlas=1024, pad=6):
    entries = chart_entries(mesh)
    dims = [(mx - mn) for _, _, mn, mx in entries]
    rotate = [d[1] > d[0] * 1.15 for d in dims]

    def sizes_for(k):
        out = []
        for d, rot in zip(dims, rotate):
            w = max(1, int(np.ceil(d[0] * k)) + 1)
            h = max(1, int(np.ceil(d[1] * k)) + 1)
            out.append((h, w) if rot else (w, h))
        return out

    lo, hi = 1.0, 4096.0
    best = None
    for _ in range(26):
        k = (lo + hi) / 2
        placed = _shelf_pack(sizes_for(k), atlas, pad)
        if placed is None:
            hi = k
        else:
            lo = k
            best = (k, placed)
    if best is None:
        raise RuntimeError("could not pack charts")
    k, placed = best
    atlas_uv = np.zeros((len(mesh.pos), 2))
    for (ci, sel, mn, mx), rot, (x0, y0) in zip(entries, rotate, placed):
        local = (mesh.uv[sel] - mn) * k
        if rot:
            span = (mx - mn)[0] * k
            local = np.column_stack([local[:, 1], span - local[:, 0]])
        atlas_uv[sel, 0] = (x0 + local[:, 0]) / atlas
        atlas_uv[sel, 1] = (y0 + local[:, 1]) / atlas
    return atlas_uv, k


def rasterize(px, tri, width, height, depth=None):
    tri_id = np.full((height, width), -1, dtype=np.int64)
    bary = np.zeros((height, width, 3))
    zbuf = None if depth is None else np.full((height, width), np.inf)
    a = px[tri[:, 0]]
    b = px[tri[:, 1]]
    c = px[tri[:, 2]]
    xmin = np.clip(np.floor(np.minimum(np.minimum(a[:, 0], b[:, 0]), c[:, 0]) - 0.5).astype(np.int64), 0, width - 1)
    xmax = np.clip(np.ceil(np.maximum(np.maximum(a[:, 0], b[:, 0]), c[:, 0]) + 0.5).astype(np.int64), 0, width - 1)
    ymin = np.clip(np.floor(np.minimum(np.minimum(a[:, 1], b[:, 1]), c[:, 1]) - 0.5).astype(np.int64), 0, height - 1)
    ymax = np.clip(np.ceil(np.maximum(np.maximum(a[:, 1], b[:, 1]), c[:, 1]) + 0.5).astype(np.int64), 0, height - 1)
    area = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    for t in np.nonzero(np.abs(area) > 1e-12)[0]:
        x0, x1, y0, y1 = xmin[t], xmax[t], ymin[t], ymax[t]
        if x1 < x0 or y1 < y0:
            continue
        xs = np.arange(x0, x1 + 1) + 0.5
        ys = np.arange(y0, y1 + 1) + 0.5
        gx, gy = np.meshgrid(xs, ys)
        ax, ay = a[t]
        bx, by = b[t]
        cx, cy = c[t]
        inv = 1.0 / area[t]
        w0 = ((bx - gx) * (cy - gy) - (by - gy) * (cx - gx)) * inv
        w1 = ((cx - gx) * (ay - gy) - (cy - gy) * (ax - gx)) * inv
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            continue
        sub_ids = tri_id[y0:y1 + 1, x0:x1 + 1]
        sub_bary = bary[y0:y1 + 1, x0:x1 + 1]
        if depth is not None:
            z = w0 * depth[tri[t, 0]] + w1 * depth[tri[t, 1]] + w2 * depth[tri[t, 2]]
            sub_z = zbuf[y0:y1 + 1, x0:x1 + 1]
            inside &= z < sub_z
            sub_z[inside] = z[inside]
        sub_ids[inside] = t
        sub_bary[inside, 0] = w0[inside]
        sub_bary[inside, 1] = w1[inside]
        sub_bary[inside, 2] = w2[inside]
    return tri_id, bary, zbuf


def dilate(values, filled, passes=8):
    vals = values.copy()
    mask = filled.copy()
    h, w = mask.shape
    for _ in range(passes):
        acc = np.zeros_like(vals)
        cnt = np.zeros((h, w))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                shifted_mask = np.zeros_like(mask)
                shifted_vals = np.zeros_like(vals)
                ys = slice(max(dy, 0), h + min(dy, 0))
                yd = slice(max(-dy, 0), h + min(-dy, 0))
                xs = slice(max(dx, 0), w + min(dx, 0))
                xd = slice(max(-dx, 0), w + min(-dx, 0))
                shifted_mask[yd, xd] = mask[ys, xs]
                shifted_vals[yd, xd] = vals[ys, xs]
                cnt += shifted_mask
                if vals.ndim == 3:
                    acc += shifted_vals * shifted_mask[..., None]
                else:
                    acc += shifted_vals * shifted_mask
        grow = (~mask) & (cnt > 0)
        if not grow.any():
            break
        if vals.ndim == 3:
            vals[grow] = acc[grow] / cnt[grow][:, None]
        else:
            vals[grow] = acc[grow] / cnt[grow]
        mask = mask | grow
    return vals, mask


def blur_masked(values, mask, passes=2):
    out = values.copy()
    h, w = mask.shape
    for _ in range(passes):
        acc = np.zeros_like(out)
        cnt = np.zeros((h, w))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ys = slice(max(dy, 0), h + min(dy, 0))
                yd = slice(max(-dy, 0), h + min(-dy, 0))
                xs = slice(max(dx, 0), w + min(dx, 0))
                xd = slice(max(-dx, 0), w + min(-dx, 0))
                m = np.zeros((h, w))
                v = np.zeros_like(out)
                m[yd, xd] = mask[ys, xs]
                v[yd, xd] = out[ys, xs]
                acc += v * m
                cnt += m
        out = np.where(mask & (cnt > 0), acc / np.maximum(cnt, 1), out)
    return out


class Occluder:
    def __init__(self, tris, resolution=112, samples_per_voxel=4.0, seed=7):
        lo = tris.reshape(-1, 3).min(0)
        hi = tris.reshape(-1, 3).max(0)
        extent = (hi - lo).max()
        self.voxel = extent / resolution
        self.origin = lo - self.voxel * 4
        dims = np.ceil((hi - lo) / self.voxel).astype(np.int64) + 9
        self.grid = np.zeros(dims, dtype=bool)
        a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
        areas = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
        counts = np.ceil(areas / (self.voxel * self.voxel) * samples_per_voxel).astype(np.int64) + 3
        rng = np.random.default_rng(seed)
        idx = np.repeat(np.arange(len(tris)), counts)
        r1 = np.sqrt(rng.random(len(idx)))
        r2 = rng.random(len(idx))
        pts = a[idx] * (1 - r1)[:, None] + b[idx] * (r1 * (1 - r2))[:, None] + c[idx] * (r1 * r2)[:, None]
        cells = np.floor((pts - self.origin) / self.voxel).astype(np.int64)
        cells = np.clip(cells, 0, dims - 1)
        self.grid[cells[:, 0], cells[:, 1], cells[:, 2]] = True
        self.dims = dims

    def occluded(self, pts):
        cells = np.floor((pts - self.origin) / self.voxel).astype(np.int64)
        ok = np.all((cells >= 0) & (cells < self.dims), axis=-1)
        cells = np.clip(cells, 0, self.dims - 1)
        return self.grid[cells[..., 0], cells[..., 1], cells[..., 2]] & ok


def hemisphere_dirs(count):
    i = np.arange(count) + 0.5
    r = np.sqrt(i / count)
    phi = i * np.pi * (3 - np.sqrt(5))
    return np.stack([r * np.cos(phi), r * np.sin(phi), np.sqrt(1 - r * r)], 1)


def ambient_occlusion(occ, P, N, radius, dirs=18, chunk=40000):
    local = hemisphere_dirs(dirs)
    radius = max(radius, occ.voxel * 4.0)
    steps = np.unique(np.geomspace(occ.voxel * 1.6, radius, 9))
    weights = np.clip(1 - steps / (radius * 1.15), 0.05, 1) ** 0.6
    out = np.ones(len(P))
    for s in range(0, len(P), chunk):
        p = P[s:s + chunk]
        n = N[s:s + chunk]
        helper = np.where(np.abs(n[:, 1:2]) < 0.9, np.array([[0.0, 1.0, 0.0]]), np.array([[1.0, 0.0, 0.0]]))
        t = normalize(np.cross(helper, n))
        b = np.cross(n, t)
        world = local[None, :, 0:1] * t[:, None, :] + local[None, :, 1:2] * b[:, None, :] + local[None, :, 2:3] * n[:, None, :]
        start = p + n * occ.voxel * 1.8
        hit = np.zeros(world.shape[:2])
        for dist, wgt in zip(steps, weights):
            q = start[:, None, :] + world * dist
            h = occ.occluded(q)
            hit = np.maximum(hit, h * wgt)
        out[s:s + chunk] = 1.0 - hit.mean(1)
    return out


def feature_edges(mesh, angle=20.0):
    t = mesh.tri
    keys = np.round(mesh.pos * 2000).astype(np.int64)
    _, weld = np.unique(keys, axis=0, return_inverse=True)
    weld = weld.reshape(-1)
    a, b, c = mesh.pos[t[:, 0]], mesh.pos[t[:, 1]], mesh.pos[t[:, 2]]
    fn = normalize(np.cross(b - a, c - a))
    ev = np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]])
    owner = np.tile(np.arange(len(t)), 3)
    opposite = np.concatenate([t[:, 2], t[:, 0], t[:, 1]])
    wa, wb = weld[ev[:, 0]], weld[ev[:, 1]]
    base = int(weld.max()) + 1
    key = np.minimum(wa, wb).astype(np.int64) * base + np.maximum(wa, wb)
    order = np.argsort(key, kind="stable")
    key_sorted = key[order]
    starts = np.concatenate([[0], np.nonzero(np.diff(key_sorted))[0] + 1])
    ends = np.concatenate([starts[1:], [len(key_sorted)]])
    sizes = ends - starts
    real = np.zeros(len(ev), dtype=bool)
    single = starts[sizes == 1]
    real[order[single]] = True
    pairs = starts[sizes == 2]
    i = order[pairs]
    j = order[pairs + 1]
    ti, tj = owner[i], owner[j]
    cos = np.clip((fn[ti] * fn[tj]).sum(1), -1, 1)
    sharp = cos < np.cos(np.radians(angle))
    convex = (fn[ti] * (mesh.pos[opposite[j]] - mesh.pos[ev[i, 0]])).sum(1) < 1e-6
    keep = sharp & convex
    real[i[keep]] = True
    real[j[keep]] = True
    return ev[real]


def edge_distance(segments_uv, chart_img, k, width, atlas):
    h, w = chart_img.shape
    mask = np.zeros((h, w), dtype=bool)
    if len(segments_uv):
        p0 = segments_uv[:, 0] * atlas
        p1 = segments_uv[:, 1] * atlas
        lengths = np.linalg.norm(p1 - p0, axis=1)
        counts = np.ceil(lengths * 2).astype(np.int64) + 2
        idx = np.repeat(np.arange(len(p0)), counts)
        offs = np.concatenate([np.linspace(0, 1, n) for n in counts])
        pts = p0[idx] + (p1[idx] - p0[idx]) * offs[:, None]
        xs = np.clip(np.floor(pts[:, 0]).astype(np.int64), 0, w - 1)
        ys = np.clip(np.floor(pts[:, 1]).astype(np.int64), 0, h - 1)
        mask[ys, xs] = True
    mask &= chart_img >= 0
    dist = np.full((h, w), np.inf)
    dist[mask] = 0.0
    radius = max(1, int(np.ceil(width * k)))
    shifts = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for step in range(1, radius + 1):
        grow = np.zeros_like(mask)
        use = shifts if step % 2 == 0 else shifts[:4]
        for dy, dx in use:
            ys = slice(max(dy, 0), h + min(dy, 0))
            yd = slice(max(-dy, 0), h + min(-dy, 0))
            xs = slice(max(dx, 0), w + min(dx, 0))
            xd = slice(max(-dx, 0), w + min(-dx, 0))
            nm = np.zeros_like(mask)
            nc = np.full((h, w), -2, dtype=chart_img.dtype)
            nm[yd, xd] = mask[ys, xs]
            nc[yd, xd] = chart_img[ys, xs]
            grow |= nm & (nc == chart_img)
        grow &= ~mask & (chart_img >= 0)
        if not grow.any():
            break
        dist[grow] = step
        mask |= grow
    return dist / k


def height_to_normal(height, k, strength=1.0):
    hp = np.pad(height, 1, mode="edge")
    dhdx = (hp[1:-1, 2:] - hp[1:-1, :-2]) * 0.5 * k
    dhdrow = (hp[2:, 1:-1] - hp[:-2, 1:-1]) * 0.5 * k
    n = np.stack([-dhdx * strength, dhdrow * strength, np.ones_like(height)], -1)
    return normalize(n)


def bake(meshes, roles, occluder_tris, atlas=1024, pad=6, ao_radius=0.4, ao_strength=0.6, normal_strength=1.0, edge_width=0.05, edge_angle=20.0, vertex_edge=0.0, gradient=0.12, highlight=0.6):
    combined = []
    role_of_vertex = []
    for i, (mesh, role) in enumerate(zip(meshes, roles)):
        combined.append(mesh)
        role_of_vertex.append(np.full(len(mesh.pos), i))
    from .mesh import Mesh
    merged = Mesh.merge(combined)
    vrole = np.concatenate(role_of_vertex)
    atlas_uv, k = pack(merged, atlas, pad)
    px = atlas_uv * atlas
    tri_id, bary, _ = rasterize(px, merged.tri, atlas, atlas)
    filled = tri_id >= 0
    ys, xs = np.nonzero(filled)
    t = tri_id[ys, xs]
    w = bary[ys, xs]
    tv = merged.tri[t]

    def interp(attr):
        if attr.ndim == 1:
            return (attr[tv] * w).sum(1)
        return (attr[tv] * w[..., None]).sum(1)

    P = interp(merged.pos)
    N = normalize(interp(merged.nrm))
    U = interp(merged.uv)
    chart = merged.vchart[tv[:, 0]]
    role = vrole[tv[:, 0]]
    chart_img = np.full((atlas, atlas), -1, dtype=np.int64)
    chart_img[ys, xs] = chart
    edges = merged.wedges
    seg_uv = np.stack([atlas_uv[edges[:, 0]], atlas_uv[edges[:, 1]]], 1) if len(edges) else np.zeros((0, 2, 2))
    dist = edge_distance(seg_uv, chart_img, k, edge_width, atlas)
    t_edge = 1.0 - np.clip(dist[ys, xs] / edge_width, 0, 1)
    E = np.maximum(t_edge * t_edge * (3 - 2 * t_edge), interp(merged.edge) * vertex_edge)
    occ = Occluder(occluder_tris)
    AO = ambient_occlusion(occ, P, N, ao_radius)
    ao_img = np.ones((atlas, atlas))
    ao_img[ys, xs] = AO
    ao_img = blur_masked(ao_img, filled, 2)
    AO = ao_img[ys, xs]
    seeds = np.array([c.seed for c in merged.charts], dtype=np.float64)
    count = len(P)
    color = np.zeros((count, 3))
    alpha = np.ones(count)
    rough = np.zeros(count)
    metal = np.zeros(count)
    height = np.zeros(count)
    texel = 1.0 / k
    groups = {}
    for ci, c in enumerate(merged.charts):
        groups.setdefault((id(c.material), ), []).append(ci)
    chart_role = {}
    for ci in range(len(merged.charts)):
        sel = np.nonzero(merged.vchart == ci)[0]
        if len(sel):
            chart_role[ci] = vrole[sel[0]]
    for key, chart_ids in groups.items():
        material = merged.charts[chart_ids[0]].material
        by_role = {}
        for ci in chart_ids:
            by_role.setdefault(chart_role.get(ci, 0), []).append(ci)
        for r, cids in by_role.items():
            sel = np.nonzero(np.isin(chart, cids))[0]
            if len(sel) == 0:
                continue
            ctx = Ctx(P[sel], N[sel], U[sel], E[sel], AO[sel], seeds[chart[sel]], texel)
            surface = evaluate(material, ctx)
            spec = roles[r]
            c, a, ro, me, he = compose(surface, ctx, material, spec.overlay, spec.color, ao_strength, gradient, highlight)
            color[sel], alpha[sel], rough[sel], metal[sel], height[sel] = c, a, ro, me, he
    maps = {}
    img = np.zeros((atlas, atlas, 3))
    img[ys, xs] = color
    maps["color"], _ = dilate(img, filled, pad + 2)
    img = np.ones((atlas, atlas))
    img[ys, xs] = alpha
    maps["alpha"], _ = dilate(img, filled, pad + 2)
    img = np.zeros((atlas, atlas))
    img[ys, xs] = rough
    maps["roughness"], _ = dilate(img, filled, pad + 2)
    img = np.zeros((atlas, atlas))
    img[ys, xs] = metal
    maps["metalness"], _ = dilate(img, filled, pad + 2)
    img = np.zeros((atlas, atlas))
    img[ys, xs] = height
    hmap, _ = dilate(img, filled, pad + 4)
    maps["normal"] = height_to_normal(hmap, k, normal_strength)
    maps["ao"] = ao_img
    offsets = np.cumsum([0] + [len(m.pos) for m in meshes])
    per_mesh_uv = [atlas_uv[offsets[i]:offsets[i + 1]] for i in range(len(meshes))]
    return maps, per_mesh_uv, k
