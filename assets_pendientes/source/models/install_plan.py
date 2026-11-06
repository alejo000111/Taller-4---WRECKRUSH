import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "out"))
MODELS = os.path.normpath(os.path.join(HERE, "..", "roblox_model_ids.json"))
TEXTURES = os.path.normpath(os.path.join(HERE, "..", "roblox_texture_ids.json"))
PLAN = os.path.normpath(os.path.join(HERE, "..", "install_plan.json"))

KINDS = {
    "ScrapHammer": "tool", "PowerHammer": "tool", "Jackhammer": "tool", "TNTLauncher": "tool", "RocketRig": "tool",
    "PlasmaCannon": "tool", "ChaosRay": "tool", "VoidBlaster": "tool", "OwnerHammer": "tool",
    "ScrapCleaver": "tool", "WreckingMaul": "tool", "ArcWelder": "tool", "RailDriver": "tool", "SingularityLauncher": "tool", "OverlordHammer": "tool",
    "ScrapEgg": "egg", "IndustrialEgg": "egg", "ChaosEgg": "egg", "DowntownEgg": "egg", "FutureEgg": "egg", "CoreEgg": "egg",
    "EggIncubator": "incubator", "ShopKiosk": "kiosk",
}


def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv):
    models = load(MODELS)
    textures = load(TEXTURES)
    built = [d for d in os.listdir(OUT) if os.path.exists(os.path.join(OUT, d, "manifest.json")) and models.get(d, {}).get("model")]
    names = [a for a in argv if not a.startswith("--")] or sorted(built)
    plan = {}
    missing = []
    for name in names:
        manifest_path = os.path.join(OUT, name, "manifest.json")
        if not os.path.exists(manifest_path):
            missing.append(f"{name}: no build")
            continue
        manifest = load(manifest_path)
        meta = manifest.get("meta", {})
        kind = KINDS.get(name) or ("destructible" if meta.get("destructible") else "station" if meta.get("station") else "wall" if meta.get("wall") else "scatter" if meta.get("scatter") else "model" if meta.get("model") else "patch" if meta.get("patch") else "pet" if "pet" in meta else "ring" if meta.get("ring") else "rim" if meta.get("rim") else "frame" if meta.get("frame") else "place" if meta.get("place") else "prop")
        entry = {"kind": kind, "manifest": manifest, "model": models.get(name, {}).get("model"), "textures": textures.get(name, {})}
        if not entry["model"]:
            missing.append(f"{name}: no model asset id")
        if manifest.get("textures") and len(entry["textures"]) < 4:
            missing.append(f"{name}: textures not uploaded")
        plan[name] = entry
    with open(PLAN, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=1)
    print(f"plan: {len(plan)} assets -> {PLAN}")
    for m in missing:
        print("  missing", m)


if __name__ == "__main__":
    main(sys.argv[1:])
