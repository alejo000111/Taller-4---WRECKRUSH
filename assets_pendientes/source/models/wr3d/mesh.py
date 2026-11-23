import numpy as np


class Chart:
    def __init__(self, material, seed=0):
        self.material = material
        self.seed = seed


def normalize(v):
    v = np.asarray(v, dtype=np.float64)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-12)


class Mesh:
    def __init__(self, pos, nrm, uv, tri, edge=None, vchart=None, charts=None, wedges=None):
        self.pos = np.asarray(pos, dtype=np.float64).reshape(-1, 3)
        self.nrm = normalize(np.asarray(nrm, dtype=np.float64).reshape(-1, 3))
        self.uv = np.asarray(uv, dtype=np.float64).reshape(-1, 2)
        self.tri = np.asarray(tri, dtype=np.int64).reshape(-1, 3)
        n = len(self.pos)
        self.edge = np.zeros(n) if edge is None else np.asarray(edge, dtype=np.float64).reshape(-1)
        self.vchart = np.zeros(n, dtype=np.int64) if vchart is None else np.asarray(vchart, dtype=np.int64).reshape(-1)
        self.charts = list(charts) if charts else [Chart(None)]
        self.wedges = np.zeros((0, 2), dtype=np.int64) if wedges is None else np.asarray(wedges, dtype=np.int64).reshape(-1, 2)

    def copy(self):
        return Mesh(self.pos.copy(), self.nrm.copy(), self.uv.copy(), self.tri.copy(), self.edge.copy(), self.vchart.copy(), [Chart(c.material, c.seed) for c in self.charts], self.wedges.copy())

    @property
    def triangle_count(self):
        return len(self.tri)

    def transformed(self, m):
        m = np.asarray(m, dtype=np.float64)
        out = self.copy()
        out.pos = self.pos @ m[:3, :3].T + m[:3, 3]
        normal_matrix = np.linalg.inv(m[:3, :3]).T
        out.nrm = normalize(self.nrm @ normal_matrix.T)
        if np.linalg.det(m[:3, :3]) < 0:
            out.tri = out.tri[:, ::-1].copy()
        return out

    def material(self, mat, seed=None):
        for i, c in enumerate(self.charts):
            c.material = mat
            if seed is not None:
                c.seed = seed + i
        return self

    def seeded(self, seed):
        for i, c in enumerate(self.charts):
            c.seed = seed + i * 7919
        return self

    def flipped(self):
        out = self.copy()
        out.tri = out.tri[:, ::-1].copy()
        out.nrm = -out.nrm
        return out

    def clean(self, eps=1e-12):
        a = self.pos[self.tri[:, 0]]
        b = self.pos[self.tri[:, 1]]
        c = self.pos[self.tri[:, 2]]
        area = np.linalg.norm(np.cross(b - a, c - a), axis=1)
        self.tri = self.tri[area > eps]
        used = np.zeros(len(self.pos), dtype=bool)
        used[self.tri.ravel()] = True
        if not used.all():
            remap = np.cumsum(used) - 1
            self.pos = self.pos[used]
            self.nrm = self.nrm[used]
            self.uv = self.uv[used]
            self.edge = self.edge[used]
            self.vchart = self.vchart[used]
            self.tri = remap[self.tri]
            if len(self.wedges):
                keep = used[self.wedges].all(1)
                self.wedges = remap[self.wedges[keep]]
        return self

    def bounds(self):
        return self.pos.min(axis=0), self.pos.max(axis=0)

    def area(self):
        a = self.pos[self.tri[:, 0]]
        b = self.pos[self.tri[:, 1]]
        c = self.pos[self.tri[:, 2]]
        return 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1).sum()

    @staticmethod
    def merge(meshes):
        meshes = [m for m in meshes if m is not None and len(m.tri)]
        if not meshes:
            return None
        pos, nrm, uv, tri, edge, vchart, charts, wedges = [], [], [], [], [], [], [], []
        offset = 0
        chart_offset = 0
        for m in meshes:
            pos.append(m.pos)
            nrm.append(m.nrm)
            uv.append(m.uv)
            tri.append(m.tri + offset)
            wedges.append(m.wedges + offset)
            edge.append(m.edge)
            vchart.append(m.vchart + chart_offset)
            charts.extend(m.charts)
            offset += len(m.pos)
            chart_offset += len(m.charts)
        return Mesh(np.concatenate(pos), np.concatenate(nrm), np.concatenate(uv), np.concatenate(tri), np.concatenate(edge), np.concatenate(vchart), charts, np.concatenate(wedges))


def grid_border(rows, cols):
    out = []
    for c in range(cols - 1):
        out.append((c, c + 1))
        out.append(((rows - 1) * cols + c, (rows - 1) * cols + c + 1))
    for r in range(rows - 1):
        out.append((r * cols, (r + 1) * cols))
        out.append((r * cols + cols - 1, (r + 1) * cols + cols - 1))
    return np.asarray(out, dtype=np.int64).reshape(-1, 2)


def row_pairs(row, cols):
    c = np.arange(cols - 1)
    return np.stack([row * cols + c, row * cols + c + 1], 1)


def col_pairs(col, rows, cols):
    r = np.arange(rows - 1)
    return np.stack([r * cols + col, (r + 1) * cols + col], 1)


def grid_triangles(rows, cols, offset=0, flip=False):
    r = np.arange(rows - 1)
    c = np.arange(cols - 1)
    rr, cc = np.meshgrid(r, c, indexing="ij")
    a = rr * cols + cc
    b = a + 1
    d = a + cols
    e = d + 1
    if flip:
        t1 = np.stack([a, b, d], -1)
        t2 = np.stack([b, e, d], -1)
    else:
        t1 = np.stack([a, d, b], -1)
        t2 = np.stack([b, d, e], -1)
    return (np.concatenate([t1.reshape(-1, 3), t2.reshape(-1, 3)]) + offset).astype(np.int64)


def flat_shaded(mesh):
    t = mesh.tri
    pos = mesh.pos[t].reshape(-1, 3)
    uv = mesh.uv[t].reshape(-1, 2)
    edge = mesh.edge[t].reshape(-1)
    vchart = mesh.vchart[t].reshape(-1)
    a, b, c = mesh.pos[t[:, 0]], mesh.pos[t[:, 1]], mesh.pos[t[:, 2]]
    fn = normalize(np.cross(b - a, c - a))
    nrm = np.repeat(fn, 3, axis=0)
    tri = np.arange(len(pos)).reshape(-1, 3)
    return Mesh(pos, nrm, uv, tri, edge, vchart, mesh.charts)
