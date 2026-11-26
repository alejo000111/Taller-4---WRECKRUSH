import itertools

import numpy as np

from .mesh import Mesh, grid_triangles, grid_border, row_pairs, col_pairs, normalize, flat_shaded
from .xform import R, S

_seeds = itertools.count(1)


def next_seed():
    return next(_seeds) * 1013


def orient(mesh):
    t = mesh.tri
    a, b, c = mesh.pos[t[:, 0]], mesh.pos[t[:, 1]], mesh.pos[t[:, 2]]
    fn = np.cross(b - a, c - a)
    vn = mesh.nrm[t[:, 0]] + mesh.nrm[t[:, 1]] + mesh.nrm[t[:, 2]]
    bad = (fn * vn).sum(1) < 0
    mesh.tri[bad] = mesh.tri[bad][:, ::-1]
    return mesh


def recompute_normals(mesh):
    t = mesh.tri
    a, b, c = mesh.pos[t[:, 0]], mesh.pos[t[:, 1]], mesh.pos[t[:, 2]]
    fn = np.cross(b - a, c - a)
    acc = np.zeros_like(mesh.pos)
    for k in range(3):
        np.add.at(acc, t[:, k], fn)
    keys = np.round(mesh.pos * 1e4).astype(np.int64)
    _, inverse = np.unique(np.concatenate([keys, mesh.vchart[:, None]], 1), axis=0, return_inverse=True)
    inverse = inverse.reshape(-1)
    summed = np.zeros((inverse.max() + 1, 3))
    np.add.at(summed, inverse, acc)
    mesh.nrm = normalize(summed[inverse])
    return mesh


def _finish(mesh, mat, seed):
    mesh.clean()
    orient(mesh)
    if mat is not None:
        mesh.material(mat)
    mesh.seeded(next_seed() if seed is None else seed)
    return mesh


def _axis_samples(h, r, seg, interior):
    if r <= 1e-9:
        xs = np.linspace(-h, h, interior + 2)
        return xs, xs.copy()
    inner = h - r
    phis = np.linspace(0.0, np.pi / 4, seg + 1)
    left = -inner - r * np.tan(phis[::-1])
    left_arc = -inner - r * phis[::-1]
    mid = np.linspace(-inner, inner, interior + 2)[1:-1]
    right = inner + r * np.tan(phis)
    right_arc = inner + r * phis
    if inner <= 1e-9:
        return np.concatenate([left, right[1:]]), np.concatenate([left_arc, right_arc[1:]])
    return np.concatenate([left, mid, right]), np.concatenate([left_arc, mid, right_arc])


_FACES = [
    ((1, 0, 0), (0, 0, -1), (0, -1, 0)),
    ((-1, 0, 0), (0, 0, 1), (0, -1, 0)),
    ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
    ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
    ((0, 0, 1), (1, 0, 0), (0, -1, 0)),
    ((0, 0, -1), (-1, 0, 0), (0, -1, 0)),
]

FACE_INDEX = {"+x": 0, "-x": 1, "+y": 2, "-y": 3, "+z": 4, "-z": 5}


def rounded_box(size, radius=0.04, segments=1, mat=None, seed=None, interior=0, faces=None, face_mats=None):
    size = np.asarray(size, dtype=np.float64)
    h = size / 2.0
    r = float(min(radius, h.min() * 0.999)) if radius > 0 else 0.0
    inner = h - r
    parts = []
    used = []
    for index, (n, u3, v3) in enumerate(_FACES):
        if faces is not None and index not in [FACE_INDEX.get(f, f) for f in faces]:
            continue
        n, u3, v3 = (np.asarray(x, dtype=np.float64) for x in (n, u3, v3))
        ua, va, na = int(np.argmax(np.abs(u3))), int(np.argmax(np.abs(v3))), int(np.argmax(np.abs(n)))
        xs_u, arc_u = _axis_samples(h[ua], r, segments, interior)
        xs_v, arc_v = _axis_samples(h[va], r, segments, interior)
        gu, gv = np.meshgrid(xs_u, xs_v, indexing="xy")
        au, av = np.meshgrid(arc_u, arc_v, indexing="xy")
        p = (n * h[na])[None, :] + gu.reshape(-1, 1) * u3 + gv.reshape(-1, 1) * v3
        if r > 0:
            q = np.clip(p, -inner, inner)
            d = p - q
            dl = np.linalg.norm(d, axis=1, keepdims=True)
            nrm = np.where(dl > 1e-12, d / np.maximum(dl, 1e-12), n)
            p = q + nrm * r
            edge = np.clip(np.arccos(np.clip((nrm * n).sum(1), -1, 1)) / (np.pi / 4), 0, 1) ** 1.3
        else:
            nrm = np.repeat(n[None], len(p), 0)
            edge = np.zeros(len(p))
        uv = np.stack([au.ravel(), av.ravel()], 1)
        parts.append(Mesh(p, nrm, uv, grid_triangles(len(xs_v), len(xs_u)), edge, wedges=grid_border(len(xs_v), len(xs_u))))
        used.append(index)
    mesh = _finish(Mesh.merge(parts), mat, seed)
    if face_mats:
        names = {v: k for k, v in FACE_INDEX.items()}
        for chart_index, face_index in enumerate(used):
            key = names[face_index]
            if key in face_mats and chart_index < len(mesh.charts):
                mesh.charts[chart_index].material = face_mats[key]
    return mesh


def box(size, mat=None, seed=None):
    return rounded_box(size, 0.0, 1, mat, seed)


def round_polyline(points, radii, segments=1, closed=False):
    pts = np.asarray(points, dtype=np.float64)
    n = len(pts)
    radii = np.broadcast_to(np.asarray(radii, dtype=np.float64), (n,))
    out = []
    for i in range(n):
        p = pts[i]
        if radii[i] <= 0 or (not closed and (i == 0 or i == n - 1)):
            out.append(p)
            continue
        a, b = pts[i - 1], pts[(i + 1) % n]
        la, lb = np.linalg.norm(p - a), np.linalg.norm(b - p)
        if la < 1e-9 or lb < 1e-9:
            out.append(p)
            continue
        d0, d1 = (p - a) / la, (b - p) / lb
        turn = np.arccos(np.clip(np.dot(d0, d1), -1, 1))
        if turn < 1e-3:
            out.append(p)
            continue
        t = radii[i] * np.tan(turn / 2)
        t = min(t, 0.45 * la, 0.45 * lb)
        p0, p1 = p - d0 * t, p + d1 * t
        for s in np.linspace(0, 1, segments + 1):
            out.append((1 - s) ** 2 * p0 + 2 * (1 - s) * s * p + s * s * p1)
    return np.asarray(out)


def _turns(pts, closed):
    n = len(pts)
    turns = np.zeros(n)
    for i in range(n):
        if not closed and (i == 0 or i == n - 1):
            continue
        a, p, b = pts[i - 1], pts[i], pts[(i + 1) % n]
        la, lb = np.linalg.norm(p - a), np.linalg.norm(b - p)
        if la < 1e-9 or lb < 1e-9:
            continue
        turns[i] = np.arccos(np.clip(np.dot((p - a) / la, (b - p) / lb), -1, 1))
    return turns


def _localize(pts, closed, min_turn=np.radians(4)):
    pts = np.asarray(pts, dtype=np.float64)
    n = len(pts)
    if n < 3:
        return pts
    turns = _turns(pts, closed)
    seg_count = n if closed else n - 1
    lengths = np.array([np.linalg.norm(pts[(i + 1) % n] - pts[i]) for i in range(seg_count)])
    out = []
    for i in range(seg_count):
        a, b = pts[i], pts[(i + 1) % n]
        out.append(a)
        length = lengths[i]
        if length < 1e-9:
            continue
        prev_len = lengths[i - 1] if (closed or i > 0) else length
        next_len = lengths[(i + 1) % seg_count] if (closed or i + 1 < seg_count) else length
        direction = (b - a) / length
        if turns[i] > min_turn and length > 3 * prev_len:
            out.append(a + direction * min(prev_len * 1.2, length / 3))
        if turns[(i + 1) % n] > min_turn and length > 3 * next_len:
            out.append(b - direction * min(next_len * 1.2, length / 3))
    if not closed:
        out.append(pts[-1])
    return np.asarray(out)


def lathe(profile, segments=16, mat=None, seed=None, smooth_angle=40.0, arc=360.0, start=0.0, r_ref=None, closed=False, localize=False, wear_turn=45.0):
    prof = np.asarray(profile, dtype=np.float64)
    if localize:
        prof = _localize(prof, closed)
    n = len(prof)
    seg_count = n if closed else n - 1
    seg_dir, seg_nrm = [], []
    for i in range(seg_count):
        d = prof[(i + 1) % n] - prof[i]
        length = np.linalg.norm(d)
        d = d / length if length > 1e-12 else np.array([0.0, 1.0])
        seg_dir.append(d)
        seg_nrm.append(np.array([d[1], -d[0]]))
    rows_pos, rows_nrm, rows_edge, rows_arc = [], [], [], []
    arc_len = 0.0
    limit = np.radians(smooth_angle)
    for i in range(n):
        has_in = closed or i > 0
        has_out = closed or i < n - 1
        if i > 0:
            arc_len += np.linalg.norm(prof[i] - prof[i - 1])
        if has_in and has_out:
            nin, nout = seg_nrm[i - 1], seg_nrm[i % seg_count]
            turn = np.arccos(np.clip(np.dot(seg_dir[i - 1], seg_dir[i % seg_count]), -1, 1))
            if turn > limit:
                for nn in (nin, nout):
                    rows_pos.append(prof[i])
                    rows_nrm.append(nn)
                    rows_edge.append(1.0)
                    rows_arc.append(arc_len)
            else:
                rows_pos.append(prof[i])
                rows_nrm.append(normalize(nin + nout))
                rows_edge.append(min(1.0, turn / np.radians(wear_turn)))
                rows_arc.append(arc_len)
        else:
            nn = seg_nrm[i % seg_count] if has_out else seg_nrm[i - 1]
            rows_pos.append(prof[i])
            rows_nrm.append(nn)
            rows_edge.append(0.0)
            rows_arc.append(arc_len)
    if closed:
        arc_len += np.linalg.norm(prof[0] - prof[-1])
        rows_pos.append(rows_pos[0])
        rows_nrm.append(rows_nrm[0])
        rows_edge.append(rows_edge[0])
        rows_arc.append(arc_len)
    rows_pos = np.asarray(rows_pos)
    rows_nrm = np.asarray(rows_nrm)
    rows_edge = np.asarray(rows_edge)
    rows_arc = np.asarray(rows_arc)
    total = rows_arc.max()
    thetas = np.radians(start) + np.linspace(0, np.radians(arc), segments + 1)
    rr = rows_pos[:, 0][:, None]
    yy = rows_pos[:, 1][:, None]
    ct, st = np.cos(thetas)[None, :], np.sin(thetas)[None, :]
    shape = (len(rr), len(thetas))
    pos = np.stack([rr * ct, np.broadcast_to(yy, shape), -rr * st], -1).reshape(-1, 3)
    nr = rows_nrm[:, 0][:, None]
    ny = rows_nrm[:, 1][:, None]
    nrm = np.stack([nr * ct, np.broadcast_to(ny, shape), -nr * st], -1).reshape(-1, 3)
    ref = r_ref if r_ref is not None else max(rows_pos[:, 0].max(), 1e-3)
    uu = np.broadcast_to((thetas - thetas[0])[None, :] * ref, shape)
    vv = np.broadcast_to((total - rows_arc)[:, None], shape)
    uv = np.stack([uu, vv], -1).reshape(-1, 2)
    edge = np.broadcast_to(rows_edge[:, None], shape).reshape(-1)
    tri = grid_triangles(len(rows_pos), len(thetas))
    marked = [row_pairs(i, len(thetas)) for i in range(len(rows_pos)) if rows_edge[i] >= 0.5 and rows_pos[i, 0] > 1e-6]
    if not closed:
        for i in (0, len(rows_pos) - 1):
            if rows_pos[i, 0] > 1e-6:
                marked.append(row_pairs(i, len(thetas)))
    wedges = np.concatenate(marked) if marked else None
    return _finish(Mesh(pos, nrm, uv, tri, edge.copy(), wedges=wedges), mat, seed)


def profile_rect(r_in, r_out, y0, y1, bevel=0.03, segments=1, inner_bevel=None):
    ib = bevel if inner_bevel is None else inner_bevel
    if r_in <= 0:
        pts = [(0, y0), (r_out, y0), (r_out, y1), (0, y1)]
        return round_polyline(pts, [0, bevel, bevel, 0], segments)
    pts = [(r_in, y0), (r_out, y0), (r_out, y1), (r_in, y1)]
    return round_polyline(pts, [ib, bevel, bevel, ib], segments, closed=True)


def cylinder(radius, height, mat=None, seed=None, bevel=0.03, segments=16, bevel_segments=1):
    prof = profile_rect(0, radius, -height / 2, height / 2, bevel, bevel_segments)
    return lathe(prof, segments, mat, seed)


def frustum(r_bottom, r_top, height, mat=None, seed=None, bevel=0.03, segments=16, bevel_segments=1):
    pts = [(0, -height / 2), (r_bottom, -height / 2), (r_top, height / 2), (0, height / 2)]
    return lathe(round_polyline(pts, [0, bevel, bevel, 0], bevel_segments), segments, mat, seed)


def tube(r_out, r_in, height, mat=None, seed=None, bevel=0.02, segments=16, bevel_segments=1):
    prof = profile_rect(r_in, r_out, -height / 2, height / 2, bevel, bevel_segments)
    return lathe(prof, segments, mat, seed, closed=True)


def torus(major, minor, mat=None, seed=None, segments=20, sides=6):
    a = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    prof = np.stack([major + minor * np.cos(a), minor * np.sin(a)], 1)
    return lathe(prof, segments, mat, seed, closed=True, smooth_angle=89, localize=False, r_ref=major)


def sphere(radius, mat=None, seed=None, segments=16, rings=10):
    t = np.linspace(-np.pi / 2, np.pi / 2, rings + 1)
    prof = np.stack([radius * np.cos(t), radius * np.sin(t)], 1)
    prof[0, 0] = prof[-1, 0] = 0.0
    return lathe(prof, segments, mat, seed, smooth_angle=89, localize=False)


def ellipsoid(size, mat=None, seed=None, segments=12, rings=8):
    return sphere(0.5, mat, seed, segments, rings).transformed(S(*size))


def egg_profile(height, radius, taper=0.18, rings=14):
    t = np.linspace(0, np.pi, rings + 1)
    y = -np.cos(t) * height / 2
    r = radius * np.sin(t) * (1 - taper * (y / (height / 2)))
    r[0] = r[-1] = 0.0
    return np.stack([r, y], 1)


def egg(height, radius, mat=None, seed=None, taper=0.18, segments=24, rings=14):
    return lathe(egg_profile(height, radius, taper, rings), segments, mat, seed, smooth_angle=89, localize=False)


def capsule(radius, length, mat=None, seed=None, segments=12, rings=4):
    t = np.linspace(-np.pi / 2, 0, rings + 1)
    bottom = np.stack([radius * np.cos(t), -length / 2 + radius * np.sin(t)], 1)
    top = np.stack([radius * np.cos(t[::-1]), length / 2 - radius * np.sin(t[::-1])], 1)
    prof = np.concatenate([bottom, top])
    prof[0, 0] = prof[-1, 0] = 0.0
    return lathe(prof, segments, mat, seed, smooth_angle=89, localize=False)


def dome(radius, height, mat=None, seed=None, segments=10, rings=3):
    t = np.linspace(0, np.pi / 2, rings + 1)
    prof = np.stack([radius * np.cos(t), height * np.sin(t)], 1)
    prof = np.concatenate([[[0.0, 0.0]], prof])
    prof[-1, 0] = 0.0
    return lathe(prof, segments, mat, seed, smooth_angle=60)


def _signed_area(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def triangulate(poly):
    poly = np.asarray(poly, dtype=np.float64)
    idx = list(range(len(poly)))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 20000:
        guard += 1
        found = False
        m = len(idx)
        arr = poly[idx]
        for k in range(m):
            i0, i1, i2 = (k - 1) % m, k, (k + 1) % m
            a, b, c = arr[i0], arr[i1], arr[i2]
            cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            if cross < -1e-12:
                continue
            others = np.delete(arr, [i0, i1, i2], axis=0)
            if len(others):
                v0, v1 = c - a, b - a
                v2 = others - a
                d00, d01, d11 = v0 @ v0, v0 @ v1, v1 @ v1
                d02, d12 = v2 @ v0, v2 @ v1
                denom = d00 * d11 - d01 * d01
                if abs(denom) > 1e-18:
                    u = (d11 * d02 - d01 * d12) / denom
                    v = (d00 * d12 - d01 * d02) / denom
                    if np.any((u > 1e-9) & (v > 1e-9) & (u + v < 1 - 1e-9)):
                        continue
            tris.append((idx[i0], idx[i1], idx[i2]))
            idx.pop(i1)
            found = True
            break
        if not found:
            tris.append((idx[-1], idx[0], idx[1]))
            idx.pop(0)
    if len(idx) == 3:
        tris.append(tuple(idx))
    return np.asarray(tris, dtype=np.int64)


def extrude(polygon, depth, mat=None, seed=None, bevel=0.03, bevel_segments=1, corner_radius=None, corner_segments=1, caps=True, smooth_angle=35.0, cap_mats=None):
    poly = np.asarray(polygon, dtype=np.float64)
    if _signed_area(poly) < 0:
        poly = poly[::-1]
    cr = bevel if corner_radius is None else corner_radius
    if cr > 0:
        poly = round_polyline(poly, cr, corner_segments, closed=True)
    n = len(poly)
    nxt, prv = np.roll(poly, -1, 0), np.roll(poly, 1, 0)
    d_out = normalize(nxt - poly)
    d_in = normalize(poly - prv)
    n_out = np.stack([d_out[:, 1], -d_out[:, 0]], 1)
    n_in = np.stack([d_in[:, 1], -d_in[:, 0]], 1)
    turn = np.arccos(np.clip((d_in * d_out).sum(1), -1, 1))
    hard = turn > np.radians(smooth_angle)
    avg = normalize(n_in + n_out)
    miter = avg / np.maximum(np.cos(turn / 2), 0.35)[:, None]
    seglen = np.linalg.norm(nxt - poly, axis=1)
    perim = np.concatenate([[0.0], np.cumsum(seglen)])
    cols_pt, cols_nrm, cols_miter, cols_u, cols_edge = [], [], [], [], []
    for i in range(n):
        e2 = 1.0 if hard[i] else min(1.0, turn[i] / np.radians(45))
        normals = (n_in[i], n_out[i]) if hard[i] else (avg[i],)
        for nn in normals:
            cols_pt.append(poly[i])
            cols_nrm.append(nn)
            cols_miter.append(miter[i])
            cols_u.append(perim[i])
            cols_edge.append(e2)
    cols_pt.append(poly[0])
    cols_nrm.append(n_in[0] if hard[0] else avg[0])
    cols_miter.append(miter[0])
    cols_u.append(perim[-1])
    cols_edge.append(cols_edge[0])
    if hard[0]:
        cols_pt, cols_nrm, cols_miter, cols_u, cols_edge = cols_pt[1:], cols_nrm[1:], cols_miter[1:], cols_u[1:], cols_edge[1:]
    cols_pt = np.asarray(cols_pt)
    cols_nrm = np.asarray(cols_nrm)
    cols_miter = np.asarray(cols_miter)
    cols_u = np.asarray(cols_u)
    cols_edge = np.asarray(cols_edge)
    b = float(min(bevel, depth / 2 * 0.999)) if bevel > 0 else 0.0
    if b > 0:
        phis = np.linspace(0, np.pi / 2, bevel_segments + 1)
        rows = [(-1, ph) for ph in phis[::-1]] + [(1, ph) for ph in phis]
    else:
        rows = [(-1, 0.0), (1, 0.0)]
    pos, nrm, uv, edge = [], [], [], []
    v_acc = 0.0
    prev = None
    for s, ph in rows:
        inset = b * (1 - np.cos(ph))
        z = s * (depth / 2 - b + b * np.sin(ph))
        if prev is not None:
            v_acc += np.hypot(z - prev[0], inset - prev[1])
        prev = (z, inset)
        p2 = cols_pt - cols_miter * inset
        pos.append(np.column_stack([p2, np.full(len(p2), z)]))
        nrm.append(np.column_stack([cols_nrm * np.cos(ph), np.full(len(p2), s * np.sin(ph))]))
        uv.append(np.column_stack([cols_u, np.full(len(p2), v_acc)]))
        bevel_edge = np.sin(2 * ph) if b > 0 else 0.0
        edge.append(np.maximum(cols_edge * np.cos(ph) ** 2, bevel_edge))
    pos = np.concatenate(pos)
    nrm = np.concatenate(nrm)
    uv = np.concatenate(uv)
    edge = np.concatenate(edge)
    uv[:, 1] = v_acc - uv[:, 1]
    ncols = len(cols_pt)
    marked = [row_pairs(r, ncols) for r, (sg, ph) in enumerate(rows) if b <= 0 or abs(ph) < 1e-9 or abs(ph - np.pi / 2) < 1e-9]
    marked += [col_pairs(c, len(rows), ncols) for c in range(ncols) if cols_edge[c] >= 0.5]
    parts = [Mesh(pos, nrm, uv, grid_triangles(len(rows), ncols), edge, wedges=np.concatenate(marked) if marked else None)]
    if caps:
        inner = poly - miter * b
        tris = triangulate(inner)
        for s in (1, -1):
            p3 = np.column_stack([inner, np.full(n, s * depth / 2)])
            nn = np.tile([0.0, 0.0, float(s)], (n, 1))
            cap_uv = np.column_stack([inner[:, 0] * s, -inner[:, 1]])
            loop = np.stack([np.arange(n), np.roll(np.arange(n), -1)], 1)
            parts.append(Mesh(p3, nn, cap_uv, tris, np.zeros(n), wedges=loop))
    mesh = _finish(Mesh.merge(parts), mat, seed)
    if cap_mats:
        for i, cm in enumerate(cap_mats):
            if cm is not None and i + 1 < len(mesh.charts):
                mesh.charts[i + 1].material = cm
    return mesh


def wedge(size, mat=None, seed=None, bevel=0.02):
    sx, sy, sz = size
    poly = [(-sz / 2, -sy / 2), (sz / 2, -sy / 2), (-sz / 2, sy / 2)]
    m = extrude(poly, sx, None, None, bevel=bevel)
    return _finish(m.transformed(R(0, 90, 0)), mat, seed)


def prism(sides, radius, height, mat=None, seed=None, bevel=0.02, rotation=0.0):
    a = np.radians(rotation) + np.linspace(0, 2 * np.pi, sides, endpoint=False)
    poly = np.stack([radius * np.cos(a), radius * np.sin(a)], 1)
    m = extrude(poly, height, None, None, bevel=bevel, corner_radius=bevel * 0.6)
    return _finish(m.transformed(R(-90, 0, 0)), mat, seed)


def gem(radius, height, facets=8, mat=None, seed=None, crown=0.35):
    prof = [(0, -height / 2), (radius, height * (crown - 0.5) * 0.4), (radius * 0.62, height / 2 - height * 0.08), (0, height / 2)]
    m = lathe(prof, facets, None, None, smooth_angle=1, localize=False)
    m = flat_shaded(m)
    m.edge[:] = 0.4
    return _finish(m, mat, seed)


def rivet(radius, height=None, mat=None, seed=None, segments=8):
    height = radius * 0.6 if height is None else height
    return dome(radius, height, mat, seed, segments, 4)


def bolt(radius, height, mat=None, seed=None):
    return prism(6, radius, height, mat, seed, bevel=min(radius, height) * 0.18)


def catmull_rom(points, samples):
    pts = np.asarray(points, dtype=np.float64)
    if len(pts) < 3:
        t = np.linspace(0, 1, samples)[:, None]
        return pts[0] * (1 - t) + pts[-1] * t
    ext = np.concatenate([[2 * pts[0] - pts[1]], pts, [2 * pts[-1] - pts[-2]]])
    segs = len(pts) - 1
    out = []
    for s in np.linspace(0, segs, samples):
        i = min(int(np.floor(s)), segs - 1)
        t = s - i
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        t2, t3 = t * t, t * t * t
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return np.asarray(out)


def sweep(path, radius, sides=6, mat=None, seed=None, samples=None, caps=True, taper=None, closed=False):
    pts = catmull_rom(path, samples) if samples else np.asarray(path, dtype=np.float64)
    if closed:
        pts = np.concatenate([pts, pts[:1]])
    m = len(pts)
    tang = normalize(np.gradient(pts, axis=0))
    if closed:
        tang[-1] = tang[0] = normalize(pts[1] - pts[-2])
    ref = np.array([0.0, 1.0, 0.0]) if abs(tang[0][1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    nrm0 = normalize(np.cross(np.cross(tang[0], ref), tang[0]))
    frames_n = [nrm0]
    for i in range(1, m):
        prev_n = frames_n[-1]
        v = np.cross(tang[i - 1], tang[i])
        s = np.linalg.norm(v)
        if s < 1e-9:
            frames_n.append(prev_n)
            continue
        axis = v / s
        ang = np.arctan2(s, np.dot(tang[i - 1], tang[i]))
        c, sn = np.cos(ang), np.sin(ang)
        rot = prev_n * c + np.cross(axis, prev_n) * sn + axis * np.dot(axis, prev_n) * (1 - c)
        frames_n.append(normalize(rot - tang[i] * np.dot(rot, tang[i])))
    frames_n = np.asarray(frames_n)
    frames_b = np.cross(tang, frames_n)
    lengths = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    scale = np.ones(m) if taper is None else np.array([taper(t) for t in lengths / max(lengths[-1], 1e-9)])
    ang = np.linspace(0, 2 * np.pi, sides + 1)
    ca, sa = np.cos(ang)[None, :, None], np.sin(ang)[None, :, None]
    dirs = ca * frames_n[:, None, :] + sa * frames_b[:, None, :]
    pos = pts[:, None, :] + dirs * (radius * scale)[:, None, None]
    uu = np.broadcast_to(ang[None, :] * radius, (m, sides + 1))
    vv = np.broadcast_to(lengths[:, None], (m, sides + 1))
    parts = [Mesh(pos.reshape(-1, 3), dirs.reshape(-1, 3), np.stack([uu, vv], -1).reshape(-1, 2), grid_triangles(m, sides + 1))]
    if caps and not closed:
        for idx, sign in ((0, -1.0), (m - 1, 1.0)):
            ring = pos[idx, :-1]
            center = pts[idx]
            cpos = np.concatenate([[center], ring])
            cn = np.tile(tang[idx] * sign, (len(cpos), 1))
            local = cpos - center
            cuv = np.column_stack([local @ frames_n[idx], local @ frames_b[idx]])
            k = np.arange(1, sides + 1)
            tri = np.column_stack([np.zeros(sides, dtype=np.int64), k, np.roll(k, -1)])
            parts.append(Mesh(cpos, cn, cuv, tri, wedges=np.stack([k, np.roll(k, -1)], 1)))
    return _finish(Mesh.merge(parts), mat, seed)


def spring(radius, wire, turns, length, mat=None, seed=None, sides=8, samples_per_turn=24):
    t = np.linspace(0, 1, int(turns * samples_per_turn) + 1)
    a = t * turns * 2 * np.pi
    path = np.stack([radius * np.cos(a), (t - 0.5) * length, -radius * np.sin(a)], 1)
    return sweep(path, wire, sides, mat, seed)


def mirrored(mesh, axis="x"):
    s = {"x": (-1, 1, 1), "y": (1, -1, 1), "z": (1, 1, -1)}[axis]
    return mesh.transformed(S(*s))


def plane(size, mat=None, seed=None, divisions=(1, 1)):
    sx, sz = size
    xs = np.linspace(-sx / 2, sx / 2, divisions[0] + 1)
    zs = np.linspace(-sz / 2, sz / 2, divisions[1] + 1)
    gx, gz = np.meshgrid(xs, zs, indexing="xy")
    pos = np.column_stack([gx.ravel(), np.zeros(gx.size), gz.ravel()])
    nrm = np.tile([0.0, 1.0, 0.0], (len(pos), 1))
    uv = np.column_stack([gx.ravel(), gz.ravel()])
    return _finish(Mesh(pos, nrm, uv, grid_triangles(len(zs), len(xs))), mat, seed)
