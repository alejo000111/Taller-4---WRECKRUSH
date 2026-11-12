import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from upload import api_key, multipart, call, wait_operation, USER_ID, API

HERE = os.path.dirname(os.path.abspath(__file__))
IDS = os.path.normpath(os.path.join(HERE, "..", "..", "roblox_animation_ids.json"))


def upload(name, xml, key):
    request = {
        "assetType": "Animation",
        "displayName": f"WR_{name}"[:50],
        "description": f"WRECKRUSH {name} animation",
        "creationContext": {"creator": {"userId": USER_ID}},
    }
    body, ctype = multipart({"request": json.dumps(request)}, {"fileContent": (f"{name}.rbxmx", xml.encode("utf-8"), "model/x-rbxm")})
    op = call("POST", f"{API}/assets", key, body, ctype)
    path = op.get("path") or f"operations/{op.get('operationId')}"
    response = wait_operation(path, key)
    return str(response.get("assetId"))


def preview(names):
    import library
    out = os.path.join(HERE, "out")
    os.makedirs(out, exist_ok=True)
    bundle = {name: seq.to_dict() for name, seq in library.build_all().items() if not names or name in names}
    with open(os.path.join(out, "preview.json"), "w", encoding="utf-8") as f:
        json.dump(bundle, f)
    print("preview:", ", ".join(bundle))


def main(names):
    import library
    key = api_key()
    ids = json.load(open(IDS, encoding="utf-8")) if os.path.exists(IDS) else {}
    sequences = library.build_all()
    for name, seq in sequences.items():
        if names and name not in names:
            continue
        xml = seq.to_rbxmx()
        out = os.path.join(HERE, "out")
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, f"{name}.rbxmx"), "w", encoding="utf-8") as f:
            f.write(xml)
        try:
            asset = upload(name, xml, key)
        except RuntimeError as e:
            print(f"{name}: FAILED {e}")
            continue
        ids[name] = asset
        with open(IDS, "w", encoding="utf-8") as f:
            json.dump(ids, f, indent=2)
        print(f"{name}: rbxassetid://{asset}")


if __name__ == "__main__":
    if "--preview" in sys.argv:
        preview([a for a in sys.argv[1:] if not a.startswith("--")])
    else:
        main(sys.argv[1:])
