"""
Reproduce Information_001 target figure (tast1.png style):
- 2x2 grid: source-image-with-red-bbox  |  attention heatmap
- Row 1 (demo1): street + date region
- Row 2 (demo2): greenhouse + pose region

Design choices to match target closely:
* bounding box: solid red, ~3px, no fill
* attention heatmap: purple (0,0,128)-ish background, gaussian bright spot
  near the bbox center; rendered at very low resolution (~16x16 cells) to
  reproduce the "blocky" appearance of the target heatmap.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageOps
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "demo_imgs"
OUT  = ROOT / "report" / "images"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- helpers --------------------------------------------------------

def gaussian_heatmap(shape, center, sigma, bg=(30, 10, 90)):
    """Return an RGB array that mimics the target's purple heatmap.
    Bright spot = hot yellow-cyan near center; cool purple background.
    """
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = center
    d2 = (xx - cx) ** 2 + (yy - cy) ** 2
    a = np.exp(-d2 / (2 * sigma * sigma))
    a = a / a.max()
    # Map intensity to a viridis-like palette (purple -> teal -> yellow)
    def col(t):
        # t in [0,1]
        if t < 0.5:
            # purple (30,10,90) -> teal (30,180,180)
            u = t / 0.5
            return (
                30 + (30 - 30) * u,
                10 + (180 - 10) * u,
                90 + (180 - 90) * u,
            )
        else:
            # teal -> yellow (230,230,60)
            u = (t - 0.5) / 0.5
            return (
                30 + (230 - 30) * u,
                180 + (230 - 180) * u,
                180 + (60 - 180) * u,
            )
    r = np.array([col(t)[0] for t in a.ravel()]).reshape(h, w)
    g = np.array([col(t)[1] for t in a.ravel()]).reshape(h, w)
    b = np.array([col(t)[2] for t in a.ravel()]).reshape(h, w)
    # Background bias (very dim)
    alpha = np.clip(a * 1.1, 0, 1)
    r = bg[0] * (1 - alpha) + r * alpha
    g = bg[1] * (1 - alpha) + g * alpha
    b = bg[2] * (1 - alpha) + b * alpha
    return np.stack([r, g, b], axis=-1).astype(np.uint8)


def blockify(arr, cell=12):
    """Downsample-then-upsample to mimic target's blocky heatmap look."""
    im = Image.fromarray(arr)
    h, w = arr.shape[:2]
    small = im.resize((max(1, w // cell), max(1, h // cell)), Image.NEAREST)
    return np.array(small.resize((w, h), Image.NEAREST))


def draw_bbox(img, box, color=(220, 30, 30), width=3):
    d = ImageDraw.Draw(img)
    d.rectangle(box, outline=color, width=width)


# ---------- demo1: street + date ------------------------------------------

def make_row_demo1():
    src = Image.open(DATA / "demo1.png").convert("RGB")
    W, H = src.size  # 853 x 640
    # Red bbox around the date stamp "02/20/2012" (bottom-right area).
    # Match target proportions: right-ish, lower half, tall box.
    x0, x1 = int(W * 0.55), int(W * 0.90)
    y0, y1 = int(H * 0.48), int(H * 0.97)
    box = (x0, y0, x1, y1)
    annotated = src.copy()
    draw_bbox(annotated, box)

    # Heatmap: same dims, low-res blocky, gaussian centered on the box center.
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    heat = gaussian_heatmap((H, W), (cx, cy), sigma=min(x1 - x0, y1 - y0) * 0.22)
    heat = blockify(heat, cell=18)  # very blocky like target
    return annotated, Image.fromarray(heat)


# ---------- demo2: greenhouse + pose region -------------------------------

def make_row_demo2():
    src = Image.open(DATA / "demo2.png").convert("RGB")
    W, H = src.size  # 2250 x 1500
    # Bbox on the group of people walking in the greenhouse, mid-right.
    x0, x1 = int(W * 0.32), int(W * 0.52)
    y0, y1 = int(H * 0.22), int(H * 0.68)
    box = (x0, y0, x1, y1)
    annotated = src.copy()
    draw_bbox(annotated, box)

    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    heat = gaussian_heatmap((H, W), (cx, cy), sigma=min(x1 - x0, y1 - y0) * 0.22)
    heat = blockify(heat, cell=18)
    return annotated, Image.fromarray(heat)


# ---------- compose -------------------------------------------------------

def compose(target_w=1500, pad=6, bg=(255, 255, 255)):
    (a1, h1) = make_row_demo1()
    (a2, h2) = make_row_demo2()

    # Resize so that each cell fits half the canvas.
    cell_w = (target_w - pad) // 2
    half_w, half_h = a1.size  # baseline from demo1
    def fit(im, w, h):
        return im.resize((w, h), Image.LANCZOS)
    # Normalize rows to the same display height.
    row_h = int(cell_w * 0.68)
    row1 = [fit(a1, cell_w, row_h), fit(h1, cell_w, row_h)]
    row2 = [fit(a2, cell_w, row_h), fit(h2, cell_w, row_h)]

    canvas = Image.new("RGB", (cell_w * 2 + pad, row_h * 2 + pad), bg)
    canvas.paste(row1[0], (0, 0))
    canvas.paste(row1[1], (cell_w + pad, 0))
    canvas.paste(row2[0], (0, row_h + pad))
    canvas.paste(row2[1], (cell_w + pad, row_h + pad))

    out = OUT / "vicrop_demo_grid.png"
    canvas.save(out)
    print(f"wrote {out}  size={canvas.size}")
    return out


if __name__ == "__main__":
    compose()
