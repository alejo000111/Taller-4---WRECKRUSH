import json

import numpy as np

from gen_materials import ROOT, SIZE, value_noise, fbm, blur, rgb, save, coords, crack_mask


def road_paint():
    rng = np.random.default_rng(41)
    grain = fbm(SIZE, 80, 3, 400)
    broad = fbm(SIZE, 5, 4, 401)
    flakes = fbm(SIZE, 24, 4, 402)
    worn = np.clip((flakes * 0.7 + broad * 0.5 - 0.71) / 0.05, 0, 1)
    scuffs = np.clip((fbm(SIZE, 10, 3, 403, stretch=(1, 6)) - 0.7) / 0.05, 0, 1) * 0.5
    bare = np.clip(worn + scuffs, 0, 1)
    paint = rgb((236, 236, 232))[None, None, :] * (0.9 + 0.12 * broad[..., None]) + (grain[..., None] - 0.5) * 14
    under = rgb((104, 104, 108))[None, None, :] * (0.8 + 0.3 * grain[..., None])
    color = paint * (1 - bare[..., None]) + under * bare[..., None]
    specks = rng.random((SIZE, SIZE)) > 0.992
    color[specks] *= 0.7
    cracks = crack_mask(rng, 10, 180)
    color *= (1 - 0.45 * cracks)[..., None]
    grime = np.clip((fbm(SIZE, 3, 4, 404) - 0.5) * 2.2, 0, 1)
    color *= (1 - 0.18 * grime)[..., None]
    height = (1 - bare) * 0.35 + grain * 0.3 - cracks * 0.5
    rough = np.clip(0.55 + bare * 0.35 + grain * 0.08, 0, 1)
    return save("WR_RoadPaint", color, height, 3, rough)


FACTORIES = [road_paint]


def main():
    index_path = ROOT / "index.json"
    built = json.loads(index_path.read_text()) if index_path.exists() else {}
    for factory in FACTORIES:
        maps = factory()
        built[factory.__name__] = maps
        print(factory.__name__, maps)
    index_path.write_text(json.dumps(built, indent=2))


if __name__ == "__main__":
    main()
