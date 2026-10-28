"""Пиксельная команда: art/refs-pixel/pixel-rpg-kigurumi.png -> img/crew/<id>.png
Сводим на ровную сетку (шаг ищем перебором) и строго к палитре айдентики, фон прозрачный."""
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = "art/refs-pixel/pixel-rpg-kigurumi.png"
PAL = np.array([[0, 3, 9], [20, 77, 199], [90, 148, 245], [184, 215, 255], [245, 248, 255]], float)
IDS = ["dispatcher", "scout", "maker", "typographer", "liner", "inspector"]  # лиса, заяц, медведь, кот, олень, волк

im = np.asarray(Image.open(SRC).convert("RGB")).astype(float)
cls = ((im[:, :, None] - PAL[None, None]) ** 2).sum(-1).argmin(-1)


# сетка у генератора неровная (FFT даёт шаг ~6.6 по x и ~7.5 по y), поэтому берём дробный шаг
# и в каждую клетку кладём самый частый цвет
STEP = float(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1 else 7.0
yi = (np.arange(cls.shape[0]) / STEP).astype(int)
xi = (np.arange(cls.shape[1]) / STEP).astype(int)
H, W = yi.max() + 1, xi.max() + 1
votes = np.zeros((H, W, 5), np.int32)
np.add.at(votes, (yi[:, None].repeat(cls.shape[1], 1), xi[None, :].repeat(cls.shape[0], 0), cls), 1)
small = votes.argmax(-1)
print("grid", W, "x", H)

body = small != 0
lab, n = ndimage.label(body)
sizes = ndimage.sum(body, lab, range(1, n + 1))
sprites = []
for k, name in enumerate(IDS):
    c0, c1 = (k % 3) * W // 3, (k % 3 + 1) * W // 3
    r0, r1 = (k // 3) * H // 2, (k // 3 + 1) * H // 2
    cell = lab[r0:r1, c0:c1]
    ids, cnt = np.unique(cell[cell > 0], return_counts=True)
    main = ids[cnt.argmax()]                       # сам персонаж, без искорок
    mask = ndimage.binary_closing(cell == main, iterations=1) & (small[r0:r1, c0:c1] != 0)
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    side = max(y1 - y0, x1 - x0) + 2
    rgba = np.zeros((side, side, 4), np.uint8)
    py, px = (side - (y1 - y0)) // 2, (side - (x1 - x0)) // 2
    sub = small[r0:r1, c0:c1][y0:y1, x0:x1]
    m = mask[y0:y1, x0:x1]
    rgba[py:py + sub.shape[0], px:px + sub.shape[1], :3] = PAL[sub].astype(np.uint8)
    rgba[py:py + sub.shape[0], px:px + sub.shape[1], 3] = m * 255
    sprites.append((name, rgba))

# общий холст по самому крупному (зая): у всех одинаковый размер пикселя, стоят по низу
S = max(r.shape[0] for _, r in sprites)
for name, rgba in sprites:
    img = Image.fromarray(rgba, "RGBA").crop(Image.fromarray(rgba, "RGBA").getbbox())
    canvas = Image.new("RGBA", (S, S))
    canvas.paste(img, ((S - img.width) // 2, S - 1 - img.height))
    canvas.resize((S * 4, S * 4), Image.NEAREST).save(f"img/crew/{name}.png")
    print(name, img.size, "on", S)
