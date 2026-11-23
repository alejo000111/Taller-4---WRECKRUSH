import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IDS = os.path.normpath(os.path.join(HERE, "..", "roblox_texture_ids.json"))
PATTERN = re.compile(r"/out/([^/]+)/[^/]+_(color|normal|roughness|metalness)\.png$")


def main(argv):
    with open(IDS, encoding="utf-8") as f:
        ids = json.load(f)
    updated = set()
    for path in argv:
        with open(path, encoding="utf-8") as f:
            mapping = json.load(f)
        for url, asset in mapping.items():
            match = PATTERN.search(url)
            if match:
                name, kind = match.groups()
                ids.setdefault(name, {})[kind] = asset
                updated.add(name)
    with open(IDS, "w", encoding="utf-8") as f:
        json.dump(ids, f, indent=2)
    print("updated:", ", ".join(sorted(updated)))


if __name__ == "__main__":
    main(sys.argv[1:])
