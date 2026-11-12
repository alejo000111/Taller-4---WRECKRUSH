import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "out"))
IDS = os.path.normpath(os.path.join(HERE, "..", "roblox_model_ids.json"))
USER_ID = "1807873151"
API = "https://apis.roblox.com/assets/v1"
KEY_FILE = os.path.join(os.path.expanduser("~"), ".roblox", "wreckrush_api_key.txt")


def api_key():
    key = os.environ.get("ROBLOX_API_KEY", "").strip()
    if not key and os.path.exists(KEY_FILE):
        with open(KEY_FILE, encoding="utf-8-sig") as f:
            key = f.read().strip()
    if not key:
        raise SystemExit(f"No API key found. Paste it into {KEY_FILE}")
    return key


def multipart(fields, files):
    boundary = uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
    for name, (filename, data, ctype) in files.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\nContent-Type: {ctype}\r\n\r\n'.encode()
        body += data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def call(method, url, key, data=None, ctype=None):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("x-api-key", key)
    if ctype:
        req.add_header("Content-Type", ctype)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:400]}")
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            if attempt == 3:
                raise RuntimeError(f"network: {e}")
            time.sleep(5 * (attempt + 1))


def wait_operation(path, key):
    for _ in range(120):
        status = call("GET", f"{API}/{path}", key)
        if status.get("done"):
            if "error" in status:
                raise RuntimeError(json.dumps(status["error"]))
            return status.get("response", {})
        time.sleep(2)
    raise RuntimeError(f"operation {path} timed out")


def upload_model(name, key):
    path = os.path.join(OUT, name, f"{name}.glb")
    with open(path, "rb") as f:
        data = f.read()
    request = {
        "assetType": "Model",
        "displayName": f"WR_{name}"[:50],
        "description": f"WRECKRUSH {name} mesh",
        "creationContext": {"creator": {"userId": USER_ID}},
    }
    body, ctype = multipart({"request": json.dumps(request)}, {"fileContent": (f"{name}.glb", data, "model/gltf-binary")})
    op = call("POST", f"{API}/assets", key, body, ctype)
    op_path = op.get("path") or f"operations/{op.get('operationId')}"
    response = wait_operation(op_path, key)
    return str(response.get("assetId")), hashlib.sha1(data).hexdigest(), response.get("moderationResult", {})


def main(argv):
    key = api_key()
    force = "--force" in argv
    names = [a for a in argv if not a.startswith("--")]
    if not names:
        names = sorted(d for d in os.listdir(OUT) if os.path.exists(os.path.join(OUT, d, f"{d}.glb")))
    ids = {}
    if os.path.exists(IDS):
        with open(IDS, encoding="utf-8") as f:
            ids = json.load(f)
    for name in names:
        glb = os.path.join(OUT, name, f"{name}.glb")
        with open(glb, "rb") as f:
            digest = hashlib.sha1(f.read()).hexdigest()
        if not force and ids.get(name, {}).get("sha1") == digest:
            print(f"{name}: unchanged ({ids[name]['model']})")
            continue
        try:
            asset_id, digest, moderation = upload_model(name, key)
        except RuntimeError as e:
            print(f"{name}: FAILED {e}")
            continue
        entry = ids.get(name, {})
        entry.update({"model": asset_id, "sha1": digest, "uploaded": time.strftime("%Y-%m-%d %H:%M:%S"), "moderation": moderation.get("moderationState")})
        ids[name] = entry
        with open(IDS, "w", encoding="utf-8") as f:
            json.dump(ids, f, indent=2)
        print(f"{name}: model asset {asset_id} ({entry['moderation']})")


if __name__ == "__main__":
    main(sys.argv[1:])
