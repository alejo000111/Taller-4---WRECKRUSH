import math

import numpy as np

R15 = {
    "HumanoidRootPart": None,
    "LowerTorso": "HumanoidRootPart",
    "UpperTorso": "LowerTorso",
    "Head": "UpperTorso",
    "RightUpperArm": "UpperTorso",
    "RightLowerArm": "RightUpperArm",
    "RightHand": "RightLowerArm",
    "LeftUpperArm": "UpperTorso",
    "LeftLowerArm": "LeftUpperArm",
    "LeftHand": "LeftLowerArm",
    "RightUpperLeg": "LowerTorso",
    "RightLowerLeg": "RightUpperLeg",
    "RightFoot": "RightLowerLeg",
    "LeftUpperLeg": "LowerTorso",
    "LeftLowerLeg": "LeftUpperLeg",
    "LeftFoot": "LeftLowerLeg",
}

PRIORITY = {"Idle": 0, "Movement": 1, "Action": 2, "Action2": 3, "Action3": 4, "Action4": 5}
EASING_STYLE = {"Linear": 0, "Constant": 1, "Elastic": 2, "Cubic": 3, "Bounce": 4}
EASING_DIRECTION = {"In": 0, "Out": 1, "InOut": 2}


def euler(rx=0.0, ry=0.0, rz=0.0):
    x, y, z = (math.radians(v) for v in (rx, ry, rz))
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rot_x = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    rot_y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rot_z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return rot_x @ rot_y @ rot_z


def cframe_xml(pos, rot):
    values = [pos[0], pos[1], pos[2]] + [rot[i][j] for i in range(3) for j in range(3)]
    tags = ["X", "Y", "Z", "R00", "R01", "R02", "R10", "R11", "R12", "R20", "R21", "R22"]
    return '<CoordinateFrame name="CFrame">' + "".join(f"<{t}>{v:.6f}</{t}>" for t, v in zip(tags, values)) + "</CoordinateFrame>"


class Sequence:
    def __init__(self, name, priority="Action", loop=False):
        self.name = name
        self.priority = priority
        self.loop = loop
        self.frames = []
        self.markers = []

    def key(self, time, poses, style="Cubic", direction="InOut"):
        self.frames.append({"time": float(time), "poses": poses, "style": style, "direction": direction})
        return self

    def marker(self, time, name):
        self.markers.append((float(time), name))
        return self

    def keyed(self):
        return {joint for frame in self.frames for joint in frame["poses"]}

    def to_dict(self):
        frames = []
        for frame in sorted(self.frames, key=lambda f: f["time"]):
            poses = {}
            for joint, data in frame["poses"].items():
                rot = euler(*data.get("rot", (0.0, 0.0, 0.0)))
                pos = data.get("pos", (0.0, 0.0, 0.0))
                poses[joint] = [float(v) for v in pos] + [float(rot[i][j]) for i in range(3) for j in range(3)]
            frames.append({"time": frame["time"], "style": frame["style"], "direction": frame["direction"], "poses": poses})
        return {"name": self.name, "priority": self.priority, "loop": self.loop, "frames": frames, "markers": self.markers}

    def joints(self):
        used = set()
        for frame in self.frames:
            for joint in frame["poses"]:
                node = joint
                while node:
                    used.add(node)
                    node = R15[node]
        return used

    def to_rbxmx(self):
        counter = [0]

        def ref():
            counter[0] += 1
            return f"RBX{counter[0]}"

        used = self.joints()
        keyed = self.keyed()
        frames = [dict(f, poses=dict(f["poses"])) for f in sorted(self.frames, key=lambda f: f["time"])]
        last = {}
        for frame in frames:
            for joint in keyed:
                if joint in frame["poses"]:
                    last[joint] = frame["poses"][joint]
                elif joint in last:
                    frame["poses"][joint] = last[joint]
        out = ['<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">']
        out.append(f'<Item class="KeyframeSequence" referent="{ref()}"><Properties>'
                   f'<bool name="Loop">{"true" if self.loop else "false"}</bool>'
                   f'<token name="Priority">{PRIORITY[self.priority]}</token>'
                   f'<float name="AuthoredHipHeight">2</float>'
                   f'<string name="Name">{self.name}</string></Properties>')

        def pose(joint, frame):
            data = frame["poses"].get(joint)
            if data is None:
                pos, rot, weight = (0.0, 0.0, 0.0), np.eye(3), 0
            else:
                rot = euler(*data.get("rot", (0.0, 0.0, 0.0)))
                pos = data.get("pos", (0.0, 0.0, 0.0))
                weight = 1
            children = [j for j, parent in R15.items() if parent == joint and j in used]
            inner = "".join(pose(child, frame) for child in children)
            return (f'<Item class="Pose" referent="{ref()}"><Properties>{cframe_xml(pos, rot)}'
                    f'<token name="EasingDirection">{EASING_DIRECTION[frame["direction"]]}</token>'
                    f'<token name="EasingStyle">{EASING_STYLE[frame["style"]]}</token>'
                    f'<string name="Name">{joint}</string><float name="Weight">{weight}</float></Properties>{inner}</Item>')

        for frame in frames:
            out.append(f'<Item class="Keyframe" referent="{ref()}"><Properties><string name="Name">Keyframe</string>'
                       f'<float name="Time">{frame["time"]:.4f}</float></Properties>')
            out.append(pose("HumanoidRootPart", frame))
            for time, name in self.markers:
                if abs(time - frame["time"]) < 1e-4:
                    out.append(f'<Item class="KeyframeMarker" referent="{ref()}"><Properties><string name="Name">{name}</string><string name="Value"></string></Properties></Item>')
            out.append("</Item>")
        out.append("</Item></roblox>")
        return "".join(out)
