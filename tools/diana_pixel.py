"""Диана: art/diana/diana-v3.png -> img/crew/diana.png, та же сетка и палитра, что у зверят (холст 64, x4).
Зверята смотрят направо, Диана сгенерирована смотрящей налево, на них (не отражать: поедут детали)."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

PAL = np.array([[0, 3, 9], [20, 77, 199], [90, 148, 245], [184, 215, 255], [245, 248, 255]], float)
STEP = float(sys.argv[1]) if len(sys.argv) > 1 else 13.6   # рост ~55 клеток, как у Миши и Лисички
im = np.asarray(Image.open("art/diana/diana-v3.png").convert("RGB")).astype(float)
cls = ((im[:, :, None] - PAL[None, None]) ** 2).sum(-1).argmin(-1)
ys, xs = np.where(cls != 0)
cls = cls[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
yi, xi = (np.arange(cls.shape[0]) / STEP).astype(int), (np.arange(cls.shape[1]) / STEP).astype(int)
H, W = yi.max() + 1, xi.max() + 1
votes = np.zeros((H, W, 5), int)
np.add.at(votes, (yi[:, None].repeat(cls.shape[1], 1), xi[None, :].repeat(cls.shape[0], 0), cls), 1)
small = votes.argmax(-1)
lab, _ = ndimage.label(small == 0)
edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
alpha = ~np.isin(lab, list(edge))                  # прозрачен только внешний фон
rgba = np.dstack([PAL[small].astype(np.uint8), (alpha * 255).astype(np.uint8)])
print("grid", W, "x", H)
S = 64
canvas = Image.new("RGBA", (S, S))
canvas.paste(Image.fromarray(rgba, "RGBA"), ((S - W) // 2, S - 1 - H))
canvas.resize((S * 4, S * 4), Image.NEAREST).save("img/crew/diana.png")
