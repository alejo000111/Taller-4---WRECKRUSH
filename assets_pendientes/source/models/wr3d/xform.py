import numpy as np


def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def S(x=1.0, y=None, z=None):
    y = x if y is None else y
    z = x if z is None else z
    return np.diag([x, y, z, 1.0])


def _rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1.0]])


def _ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1.0]])


def _rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])


def R(x=0.0, y=0.0, z=0.0):
    return _rx(np.radians(x)) @ _ry(np.radians(y)) @ _rz(np.radians(z))


def axis_angle(axis, degrees):
    a = np.asarray(axis, dtype=np.float64)
    a = a / np.linalg.norm(a)
    t = np.radians(degrees)
    c, s = np.cos(t), np.sin(t)
    x, y, z = a
    m = np.eye(4)
    m[:3, :3] = [
        [c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
        [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
        [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)],
    ]
    return m


def look_at(eye, target, up=(0.0, 1.0, 0.0)):
    eye = np.asarray(eye, dtype=np.float64)
    forward = np.asarray(target, dtype=np.float64) - eye
    forward /= np.linalg.norm(forward)
    up = np.asarray(up, dtype=np.float64)
    if abs(np.dot(forward, up)) > 0.999:
        up = np.array([0.0, 0.0, 1.0]) if abs(forward[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    true_up = np.cross(right, forward)
    m = np.eye(4)
    m[:3, 0] = right
    m[:3, 1] = true_up
    m[:3, 2] = -forward
    m[:3, 3] = eye
    return m


def align_y(direction):
    d = np.asarray(direction, dtype=np.float64)
    d = d / np.linalg.norm(d)
    y = np.array([0.0, 1.0, 0.0])
    axis = np.cross(y, d)
    s = np.linalg.norm(axis)
    if s < 1e-9:
        return np.eye(4) if d[1] > 0 else _rx(np.pi)
    return axis_angle(axis / s, np.degrees(np.arctan2(s, np.dot(y, d))))


def compose(*mats):
    m = np.eye(4)
    for x in mats:
        m = m @ x
    return m
