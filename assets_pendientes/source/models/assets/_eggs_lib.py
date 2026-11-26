import copy

import numpy as np

from wr3d import shapes as sh
from wr3d import compose, T, R
from wr3d.xform import align_y
from wr3d.mesh import normalize, flat_shaded
from wr3d.materials import REGISTRY, rgb
from wr3d.noise import hash3, mix


class EggForm:
    def __init__(self, height=4.0, radius=1.47, taper=0.18, center_y=0.0, samples=600):
        self.height = height
        self.radius = radius
        self.taper = taper
        self.center_y = center_y
        t = np.linspace(0, np.pi, samples + 1)
        y = -np.cos(t) * height / 2
        r = radius * np.sin(t) * (1 - taper * (y / (height / 2)))
        r[0] = r[-1] = 0.0
        self.r = r
        self.y = y + center_y
        seg = np.hypot(np.diff(r), np.diff(y))
        self.s = np.concatenate([[0.0], np.cumsum(seg)])
        self.length = self.s[-1]
        dr = np.gradient(r, self.s)
        dy = np.gradient(y, self.s)
        ln = np.maximum(np.hypot(dr, dy), 1e-9)
        self.nr = dy / ln
        self.ny = -dr / ln
        self.r_max = r.max()
        self.s_equator = self.s[np.argmax(r)]

    def bottom(self):
        return self.center_y - self.height / 2

    def top(self):
        return self.center_y + self.height / 2

    def at(self, s):
        s = np.clip(np.asarray(s, dtype=np.float64), 0, self.length)
        r = np.interp(s, self.s, self.r)
        y = np.interp(s, self.s, self.y)
        nr = np.interp(s, self.s, self.nr)
        ny = np.interp(s, self.s, self.ny)
        n = np.maximum(np.hypot(nr, ny), 1e-9)
        return r, y, nr / n, ny / n

    def s_of_y(self, y):
        return float(np.interp(y, self.y, self.s))

    def r_of_y(self, y):
        return float(np.interp(y, self.y, self.r))

    def point(self, theta_deg, s, w=0.0):
        th = np.radians(theta_deg)
        r, y, nr, ny = self.at(s)
        rr = r + w * nr
        yy = y + w * ny
        return np.stack([rr * np.cos(th), yy, -rr * np.sin(th)], -1)

    def normal(self, theta_deg, s):
        th = np.radians(theta_deg)
        _, _, nr, ny = self.at(s)
        return np.stack([nr * np.cos(th), ny, -nr * np.sin(th)], -1)

    def profile(self, rings=40, s0=0.0, s1=None, offset=0.0):
        s1 = self.length if s1 is None else s1
        u = np.linspace(0, 1, rings + 1)
        ss = s0 + (s1 - s0) * (0.75 * u + 0.25 * (0.5 - 0.5 * np.cos(u * np.pi)))
        r, y, nr, ny = self.at(ss)
        pts = np.stack([r + offset * nr, y + offset * ny], 1)
        if s0 <= 0:
            pts[0, 0] = 0.0
        if s1 >= self.length:
            pts[-1, 0] = 0.0
        return pts

    def shell(self, mat, segments=56, rings=40, offset=0.0, seed=None):
        return sh.lathe(self.profile(rings, offset=offset), segments, mat, seed, smooth_angle=89, localize=False, r_ref=self.r_max)

    def stepped_band(self, rows, mat, segments=48, inset=0.04, seed=None, bevel_segments=2, arc=360.0, start=0.0):
        pts = []
        radii = []
        for i, (s0, s1, thick, bevel) in enumerate(rows):
            ss = np.linspace(s0, s1, max(2, int(np.ceil((s1 - s0) / 0.09)) + 1))
            r, y, nr, ny = self.at(ss)
            if i == 0:
                pts.append((r[0] - inset * nr[0], y[0] - inset * ny[0]))
                radii.append(0)
            for k in range(len(ss)):
                pts.append((r[k] + thick * nr[k], y[k] + thick * ny[k]))
                radii.append(bevel if k in (0, len(ss) - 1) else 0)
        r, y, nr, ny = self.at(rows[-1][1])
        pts.append((r - inset * nr, y - inset * ny))
        radii.append(0)
        prof = sh.round_polyline(pts, radii, bevel_segments)
        return sh.lathe(prof[::-1], segments, mat, seed, smooth_angle=50, r_ref=self.r_max, arc=arc, start=start)

    def _map(self, p, theta0, s0, lift):
        s = s0 + p[:, 1]
        r, _, _, _ = self.at(s)
        th = theta0 + np.degrees(p[:, 0] / np.maximum(r, 0.05))
        return self.point(th, s, p[:, 2] + lift)

    def wrap(self, mesh, theta_deg, s0, lift=0.0):
        out = mesh.copy()
        eps = 1e-4
        p = mesh.pos
        f0 = self._map(p, theta_deg, s0, lift)
        cols = []
        for k in range(3):
            d = np.zeros(3)
            d[k] = eps
            cols.append((self._map(p + d, theta_deg, s0, lift) - f0) / eps)
        J = np.stack(cols, -1)
        jinv_t = np.transpose(np.linalg.inv(J), (0, 2, 1))
        n = np.einsum("nij,nj->ni", jinv_t, mesh.nrm)
        out.pos = f0
        out.nrm = normalize(n)
        if np.mean(np.linalg.det(J)) < 0:
            out.tri = out.tri[:, ::-1].copy()
        return out

    def frame(self, theta_deg, s, lift=0.0, spin=0.0):
        p = self.point(theta_deg, s, lift)
        n = self.normal(theta_deg, s)
        th = np.radians(theta_deg)
        tangent = np.array([-np.sin(th), 0.0, -np.cos(th)])
        base = align_y(n)
        x_now = base[:3, :3] @ np.array([1.0, 0.0, 0.0])
        x_now = x_now - n * np.dot(x_now, n)
        target = tangent - n * np.dot(tangent, n)
        ang = np.degrees(np.arctan2(np.dot(np.cross(x_now, target), n), np.dot(x_now, target)))
        return compose(T(*p), base, R(0, ang + spin, 0))

    def place(self, mesh, theta_deg, s, lift=0.0, spin=0.0):
        return mesh.transformed(self.frame(theta_deg, s, lift, spin))


def hex_nut(radius, height, mat, chamfer=0.22, seed=None):
    prof = [(0, 0), (radius * 0.9, 0), (radius, height * chamfer), (radius, height * (1 - chamfer)), (radius * 0.84, height), (0, height)]
    m = sh.lathe(prof, 6, None, None, smooth_angle=20, localize=False, start=30)
    m = flat_shaded(m)
    m.edge[:] = 0.0
    m = sh._finish(m, mat, seed)
    m.pos[:, 1] -= height / 2
    return m


def low_rivet(radius, height, mat, segments=10):
    t = np.linspace(0, np.pi / 2, 4)
    prof = [(radius * 1.04, -height * 0.5)] + [(radius * np.cos(a), height * np.sin(a)) for a in t]
    prof[-1] = (0.0, height)
    return sh.lathe(prof, segments, mat, smooth_angle=60, localize=False)


def with_surface(ctx, kind, params, E=None):
    c = copy.copy(ctx)
    if E is not None:
        c.E = E
    return REGISTRY[kind](c, params)


def bake_paint(s, color):
    color = np.asarray(color, dtype=np.float64)
    col = np.broadcast_to(rgb(color), s.base.shape) if color.ndim == 1 else color
    s.base = mix(s.base, col * s.tint[:, None], np.clip(s.paint, 0, 1))
    s.paint = np.zeros(len(s.paint))
    return s


def theta_of(P):
    return np.degrees(np.arctan2(-P[:, 2], P[:, 0])) % 360.0


def ang_diff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def cell_hash(ix, iy, seed=0):
    ix = np.asarray(ix, dtype=np.int64)
    iy = np.asarray(iy, dtype=np.int64)
    return (hash3(ix, iy, np.zeros_like(ix), seed) & 0xFFFF) / 65535.0


def dome_height(d, radius, h):
    q = np.clip(1 - (d / radius) ** 2, 0, 1)
    return np.sqrt(q) * h
