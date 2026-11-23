from rbxanim import Sequence

HOLD_HEAVY = {
    "UpperTorso": {"rot": (0, -12, 0)},
    "Head": {"rot": (0, 10, 0)},
    "RightUpperArm": {"rot": (62, 0, 12)},
    "RightLowerArm": {"rot": (48, 0, 0)},
    "RightHand": {"rot": (0, 0, 0)},
    "LeftUpperArm": {"rot": (58, 0, 52)},
    "LeftLowerArm": {"rot": (42, 0, 0)},
}

HOLD_GUN = {
    "UpperTorso": {"rot": (0, -14, 0)},
    "Head": {"rot": (-4, 12, 0)},
    "RightUpperArm": {"rot": (72, 0, 6)},
    "RightLowerArm": {"rot": (18, 0, 0)},
    "RightHand": {"rot": (0, 0, 0)},
    "LeftUpperArm": {"rot": (78, 0, 54)},
    "LeftLowerArm": {"rot": (22, 0, 0)},
}

HOLD_DRILL = {
    "UpperTorso": {"rot": (-12, -6, 0)},
    "Head": {"rot": (8, 4, 0)},
    "RightUpperArm": {"rot": (34, 0, 4)},
    "RightLowerArm": {"rot": (22, 0, 0)},
    "RightHand": {"rot": (0, 0, 0)},
    "LeftUpperArm": {"rot": (38, 0, 48)},
    "LeftLowerArm": {"rot": (26, 0, 0)},
}

LEGS_REST = {
    "LowerTorso": {"pos": (0, 0, 0)},
    "RightUpperLeg": {"rot": (0, 0, 0)},
    "RightLowerLeg": {"rot": (0, 0, 0)},
    "LeftUpperLeg": {"rot": (0, 0, 0)},
    "LeftLowerLeg": {"rot": (0, 0, 0)},
}


def crouch(depth, lean=0.0):
    thigh = 22 * depth
    return {
        "LowerTorso": {"pos": (0, -0.5 * depth, 0), "rot": (lean, 0, 0)},
        "RightUpperLeg": {"rot": (thigh, 0, 0)},
        "RightLowerLeg": {"rot": (-2 * thigh, 0, 0)},
        "LeftUpperLeg": {"rot": (thigh, 0, 0)},
        "LeftLowerLeg": {"rot": (-2 * thigh, 0, 0)},
    }


def pose(*parts):
    merged = {}
    for part in parts:
        merged.update(part)
    return merged


def hold(name, base, sway):
    seq = Sequence(name, "Movement", loop=True)
    breathe = dict(base)
    breathe["UpperTorso"] = {"rot": tuple(v + d for v, d in zip(base["UpperTorso"]["rot"], (sway, 0, 0)))}
    breathe["RightUpperArm"] = {"rot": tuple(v + d for v, d in zip(base["RightUpperArm"]["rot"], (-sway, 0, 0)))}
    seq.key(0.0, base, "Cubic", "InOut")
    seq.key(1.2, breathe, "Cubic", "InOut")
    seq.key(2.4, base, "Cubic", "InOut")
    return seq


def hammer_smash():
    seq = Sequence("WRHammerSmash", "Action")
    seq.key(0.0, pose(HOLD_HEAVY, LEGS_REST), "Cubic", "Out")
    seq.key(0.18, pose({
        "UpperTorso": {"rot": (14, -18, 0)},
        "Head": {"rot": (-6, 12, 0)},
        "RightUpperArm": {"rot": (168, 0, 8)},
        "RightLowerArm": {"rot": (34, 0, 0)},
        "RightHand": {"rot": (-20, 0, 0)},
        "LeftUpperArm": {"rot": (152, 0, 46)},
        "LeftLowerArm": {"rot": (30, 0, 0)},
    }, crouch(0.2, 4)), "Cubic", "In")
    seq.key(0.3, pose({
        "UpperTorso": {"rot": (-28, 6, 0)},
        "Head": {"rot": (14, -4, 0)},
        "RightUpperArm": {"rot": (36, 0, 4)},
        "RightLowerArm": {"rot": (4, 0, 0)},
        "RightHand": {"rot": (16, 0, 0)},
        "LeftUpperArm": {"rot": (42, 0, 50)},
        "LeftLowerArm": {"rot": (10, 0, 0)},
    }, crouch(0.9, -6)), "Cubic", "InOut")
    seq.marker(0.3, "Impact")
    seq.key(0.62, pose(HOLD_HEAVY, LEGS_REST))
    return seq


def hammer_sweep():
    seq = Sequence("WRHammerSweep", "Action")
    seq.key(0.0, pose(HOLD_HEAVY, LEGS_REST), "Cubic", "Out")
    seq.key(0.16, pose({
        "UpperTorso": {"rot": (4, -52, 0)},
        "Head": {"rot": (0, 38, 0)},
        "RightUpperArm": {"rot": (78, 0, 64)},
        "RightLowerArm": {"rot": (52, 0, 0)},
        "RightHand": {"rot": (0, 0, -20)},
        "LeftUpperArm": {"rot": (70, 0, 58)},
        "LeftLowerArm": {"rot": (46, 0, 0)},
    }, crouch(0.35)), "Cubic", "In")
    seq.key(0.3, pose({
        "UpperTorso": {"rot": (-8, 46, 0)},
        "Head": {"rot": (6, -30, 0)},
        "RightUpperArm": {"rot": (86, 0, -24)},
        "RightLowerArm": {"rot": (6, 0, 0)},
        "RightHand": {"rot": (0, 0, 24)},
        "LeftUpperArm": {"rot": (80, 0, 26)},
        "LeftLowerArm": {"rot": (14, 0, 0)},
    }, crouch(0.6)), "Cubic", "InOut")
    seq.marker(0.3, "Impact")
    seq.key(0.6, pose(HOLD_HEAVY, LEGS_REST))
    return seq


def hammer_slam():
    seq = Sequence("WRHammerSlam", "Action")
    seq.key(0.0, pose(HOLD_HEAVY, LEGS_REST), "Cubic", "Out")
    seq.key(0.26, pose({
        "UpperTorso": {"rot": (22, -8, 0)},
        "Head": {"rot": (-10, 6, 0)},
        "RightUpperArm": {"rot": (178, 0, 18)},
        "RightLowerArm": {"rot": (52, 0, 0)},
        "RightHand": {"rot": (-26, 0, 0)},
        "LeftUpperArm": {"rot": (172, 0, 24)},
        "LeftLowerArm": {"rot": (48, 0, 0)},
    }, crouch(0.15, 6)), "Cubic", "In")
    seq.key(0.38, pose({
        "UpperTorso": {"rot": (-36, 0, 0)},
        "Head": {"rot": (20, 0, 0)},
        "RightUpperArm": {"rot": (26, 0, 6)},
        "RightLowerArm": {"rot": (0, 0, 0)},
        "RightHand": {"rot": (22, 0, 0)},
        "LeftUpperArm": {"rot": (32, 0, 50)},
        "LeftLowerArm": {"rot": (4, 0, 0)},
    }, crouch(1.2, -10)), "Bounce", "Out")
    seq.marker(0.38, "Impact")
    seq.key(0.54, pose({
        "UpperTorso": {"rot": (-30, 0, 0)},
        "RightUpperArm": {"rot": (32, 0, 6)},
        "LeftUpperArm": {"rot": (36, 0, 50)},
    }, crouch(1.0, -8)), "Cubic", "InOut")
    seq.key(0.8, pose(HOLD_HEAVY, LEGS_REST))
    return seq


def drill_pulse():
    seq = Sequence("WRDrillPulse", "Action")
    down = pose(HOLD_DRILL, crouch(0.35, -4), {
        "UpperTorso": {"rot": (-18, -6, 0)},
        "RightUpperArm": {"rot": (28, 0, 4)},
        "LeftUpperArm": {"rot": (32, 0, 48)},
    })
    up = pose(HOLD_DRILL, crouch(0.2), {
        "UpperTorso": {"rot": (-10, -4, 2)},
        "RightUpperArm": {"rot": (38, 0, 2)},
        "LeftUpperArm": {"rot": (42, 0, 46)},
    })
    seq.key(0.0, pose(HOLD_DRILL, LEGS_REST), "Linear", "InOut")
    for i, t in enumerate((0.05, 0.1, 0.15, 0.2, 0.25, 0.3)):
        seq.key(t, down if i % 2 == 0 else up, "Linear", "InOut")
    seq.marker(0.05, "Impact")
    seq.key(0.42, pose(HOLD_DRILL, LEGS_REST))
    return seq


def launcher_fire():
    seq = Sequence("WRLauncherFire", "Action")
    seq.key(0.0, pose(HOLD_GUN), "Cubic", "Out")
    seq.key(0.06, pose({
        "UpperTorso": {"rot": (16, -16, 0)},
        "Head": {"rot": (-10, 12, 0)},
        "RightUpperArm": {"rot": (112, 0, 6)},
        "RightLowerArm": {"rot": (26, 0, 0)},
        "RightHand": {"rot": (-14, 0, 0)},
        "LeftUpperArm": {"rot": (104, 0, 52)},
        "LeftLowerArm": {"rot": (36, 0, 0)},
    }), "Cubic", "Out")
    seq.marker(0.0, "Fire")
    seq.key(0.5, pose(HOLD_GUN))
    return seq


def blaster_fire():
    seq = Sequence("WRBlasterFire", "Action")
    seq.key(0.0, pose(HOLD_GUN), "Cubic", "Out")
    seq.key(0.05, pose({
        "UpperTorso": {"rot": (8, -15, 0)},
        "Head": {"rot": (-6, 12, 0)},
        "RightUpperArm": {"rot": (96, 0, 6)},
        "RightLowerArm": {"rot": (18, 0, 0)},
        "RightHand": {"rot": (-8, 0, 0)},
        "LeftUpperArm": {"rot": (88, 0, 54)},
        "LeftLowerArm": {"rot": (30, 0, 0)},
    }), "Cubic", "Out")
    seq.marker(0.0, "Fire")
    seq.key(0.32, pose(HOLD_GUN))
    return seq


def beam_fire():
    seq = Sequence("WRBeamFire", "Action")
    braced = pose(HOLD_GUN, {
        "UpperTorso": {"rot": (-6, -14, 0)},
        "RightUpperArm": {"rot": (86, 0, 6)},
        "LeftUpperArm": {"rot": (82, 0, 54)},
    })
    kick = pose(braced, {
        "UpperTorso": {"rot": (-2, -15, 1)},
        "RightUpperArm": {"rot": (90, 0, 5)},
        "LeftUpperArm": {"rot": (86, 0, 53)},
    })
    seq.key(0.0, pose(HOLD_GUN), "Cubic", "Out")
    seq.key(0.08, braced, "Linear", "InOut")
    seq.key(0.16, kick, "Linear", "InOut")
    seq.key(0.24, braced, "Linear", "InOut")
    seq.key(0.32, kick, "Cubic", "InOut")
    seq.marker(0.08, "Fire")
    seq.key(0.5, pose(HOLD_GUN))
    return seq


def build_all():
    sequences = [
        hold("WRHoldHeavy", HOLD_HEAVY, 3),
        hold("WRHoldGun", HOLD_GUN, 2),
        hold("WRHoldDrill", HOLD_DRILL, 2),
        hammer_smash(),
        hammer_sweep(),
        hammer_slam(),
        drill_pulse(),
        launcher_fire(),
        blaster_fire(),
        beam_fire(),
    ]
    return {seq.name: seq for seq in sequences}
