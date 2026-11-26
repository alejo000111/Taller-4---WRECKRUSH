import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
sys.path.insert(0, HERE)
sys.path.insert(0, ASSETS)
OUT = os.path.normpath(os.path.join(HERE, "..", "out"))


def load(name):
    import itertools
    from wr3d import shapes
    shapes._seeds = itertools.count(1)
    path = os.path.join(ASSETS, f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"wr_asset_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build()


def available():
    return sorted(f[:-3] for f in os.listdir(ASSETS) if f.endswith(".py") and not f.startswith("_"))


def main(argv):
    quick = "--quick" in argv
    no_preview = "--no-preview" in argv
    names = [a for a in argv if not a.startswith("--")]
    if not names or names == ["all"]:
        names = available()
    for name in names:
        start = time.time()
        asset = load(name)
        out_dir = os.path.join(OUT, asset.name)
        manifest = asset.build(out_dir, preview=not no_preview, quick=quick)
        roles = ", ".join(f"{r}:{v['triangles']}" for r, v in manifest["roles"].items())
        print(f"{asset.name}: {roles} | {manifest['texel_density']:.0f} px/stud | {time.time() - start:.1f}s -> {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1:])
