"""Портреты команды: растр из art/ -> двухцветный SVG в img/crew/.
Каждый персонаж = все связные куски, чей центр попадает в его клетку сетки 3x2."""
import numpy as np, re, os, vtracer
from PIL import Image, ImageFilter
from scipy import ndimage

BLUE, PALE = "#144DC7", "#B8D7FF"
TMP = "art/tmp"


def classes(path, cols):
    src = Image.open(path).convert("RGB")
    src = src.resize((src.width * 2, src.height * 2), Image.LANCZOS).filter(ImageFilter.MedianFilter(5))
    im = np.asarray(src).astype(float)
    return ((im[:, :, None, :] - np.array(cols, float)[None, None]) ** 2).sum(-1).argmin(-1)


def trace(mask, name, fill):
    Image.fromarray(np.where(mask, 0, 255).astype("uint8")).convert("RGB").save(f"{TMP}/{name}.png")
    vtracer.convert_image_to_svg_py(f"{TMP}/{name}.png", f"{TMP}/{name}.svg", colormode="binary", mode="spline",
                                    filter_speckle=8, corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=2)
    paths = re.findall(r"<path[^>]*/>", open(f"{TMP}/{name}.svg").read())
    return [p.replace('fill="#000000"', f'fill="{fill}"') for p in paths if "#000000" in p]


def export(cls, cell, name, blue_cls, bg_cls):
    """cell = (col,row) в сетке 3x2"""
    h, w = cls.shape
    sil = cls != bg_cls
    lab, n = ndimage.label(ndimage.binary_dilation(sil, iterations=10))
    cx, cy = (cell[0] + .5) * w / 3, (cell[1] + .5) * h / 2
    keep = np.zeros_like(sil)
    for j, (y, x) in enumerate(ndimage.center_of_mass(np.ones_like(lab), lab, range(1, n + 1)), 1):
        if int(x // (w / 3)) == cell[0] and int(y // (h / 2)) == cell[1]:
            keep |= lab == j
    sil &= keep
    blue = (cls == blue_cls) & keep
    ys, xs = np.where(sil)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    s = int(max(y1 - y0, x1 - x0) * 1.08)
    oy, ox = y0 - (s - (y1 - y0)) // 2, x0 - (s - (x1 - x0)) // 2

    def box(m):
        out = np.zeros((s, s), bool)
        sy, sx = max(oy, 0), max(ox, 0)
        sub = m[sy:oy + s, sx:ox + s]
        out[sy - oy:sy - oy + sub.shape[0], sx - ox:sx - ox + sub.shape[1]] = sub
        return out
    paths = trace(box(sil), name + "_sil", PALE) + trace(box(blue), name + "_blue", BLUE)
    open(f"img/crew/{name}.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}">' + "".join(paths) + "</svg>")


os.makedirs(TMP, exist_ok=True)
# основной лист: чёрный=синий, молочный=голубой, серый фон
bw = classes("art/crew-v8-bw.png", [[37, 32, 26], [253, 250, 243], [199, 190, 180]])
for name, cell in {"scout": (0, 0), "maker": (1, 0), "dispatcher": (0, 1), "inspector": (1, 1), "liner": (2, 1)}.items():
    export(bw, cell, name, 0, 2)
# кот из v1: уже синий на тёмном
v1 = classes("art/crew-v1.png", [[20, 77, 199], [184, 215, 255], [0, 3, 9], [235, 242, 255]])
v1[v1 == 3] = 1
export(v1, (0, 1), "typographer", 0, 2)
print("ok")
