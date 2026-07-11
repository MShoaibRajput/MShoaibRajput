#!/usr/bin/env python3
"""Convert source-prepped.png (RGBA, background removed) into a monochrome
'typing' ASCII portrait SVG. GitHub strips <script>, but SMIL/CSS animation
inside an <img>-loaded SVG still runs -- so the reveal animates with zero JS.

Usage:
    python make_ascii_svg.py                # animated (starts blank, types in)
    STATIC=1 python make_ascii_svg.py        # renders the final frame only (for preview)
"""
import os
import numpy as np
from PIL import Image

# ---- tunables -------------------------------------------------------------
COLS = 100                # ascii grid width (characters)
CHAR_ASPECT = 0.52        # monospace cell width/height ratio (visual correction)
AUTO_CROP = True          # crop to subject bounding box (from alpha) + padding
PAD_FRAC = 0.03           # padding around bounding box, as fraction of box size
SHOULDER_FRAC = 0.62      # keep this fraction of subject height, from the top (head+chest)
CONTRAST = 1.28           # extra linear contrast on top of CLAHE
GAMMA = 0.88              # <1 brightens midtones
WHITE_FLOOR = 0.06        # minimum brightness for any visible (non-bg) cell
COLOR = "#c9d1d9"         # monochrome ink color (GitHub dark-mode fg gray)
BG = "none"               # transparent background
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
FONT_SIZE = 8.6
ROW_DUR = 0.05            # seconds each row takes to fully type
STAGGER = 0.035           # seconds delay added per subsequent row

RAMP = " .:-=+*#%@"       # dark -> light is reversed below since bg is dark


def load_and_crop(path):
    img = Image.open(path).convert("RGBA")
    if not AUTO_CROP:
        return img
    arr = np.array(img)
    alpha = arr[:, :, 3]
    mask = alpha > 40
    ys, xs = np.where(mask)
    y0, y1 = ys.min(), ys.max()
    x0, x1 = xs.min(), xs.max()
    bw, bh = x1 - x0, y1 - y0
    pad_x = int(bw * PAD_FRAC)
    pad_y = int(bh * PAD_FRAC)
    x0 = max(0, x0 - pad_x)
    x1 = min(img.width, x1 + pad_x)
    y0 = max(0, y0 - pad_y)
    # keep only head+shoulders: cut off at SHOULDER_FRAC of subject height
    y1 = min(img.height, y0 + int(bh * SHOULDER_FRAC) + pad_y)
    return img.crop((x0, y0, x1, y1))


def to_ascii_grid(img):
    w, h = img.size
    cell_w = w / COLS
    cell_h = cell_w / CHAR_ASPECT
    rows = max(1, int(h / cell_h))

    arr = np.array(img).astype(np.float32)
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3] / 255.0
    lum = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]) / 255.0

    grid_chars = []
    grid_alpha = []
    for r in range(rows):
        y0, y1 = int(r * cell_h), min(h, int((r + 1) * cell_h))
        row_chars = []
        row_alpha = []
        for c in range(COLS):
            x0, x1 = int(c * cell_w), min(w, int((c + 1) * cell_w))
            if y1 <= y0 or x1 <= x0:
                row_chars.append(" ")
                row_alpha.append(0.0)
                continue
            block_a = alpha[y0:y1, x0:x1]
            a_mean = float(block_a.mean())
            if a_mean < 0.25:
                row_chars.append(" ")
                row_alpha.append(0.0)
                continue
            block_l = lum[y0:y1, x0:x1]
            # weight luminance by alpha so soft edges don't get polluted by transparent px
            w_sum = block_a.sum()
            l_mean = float((block_l * block_a).sum() / w_sum) if w_sum > 0 else 0.0

            l_mean = (l_mean - 0.5) * CONTRAST + 0.5
            l_mean = max(0.0, min(1.0, l_mean))
            l_mean = l_mean ** GAMMA
            l_mean = max(WHITE_FLOOR, l_mean)

            idx = min(len(RAMP) - 1, int(l_mean * (len(RAMP) - 1)))
            ch = RAMP[idx]
            row_chars.append(ch if ch != " " else ".")
            row_alpha.append(a_mean)
        grid_chars.append(row_chars)
        grid_alpha.append(row_alpha)
    return grid_chars, grid_alpha, cell_w, cell_h * (COLS / COLS)


def esc(c):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(c, c)


def build_svg(grid_chars, grid_alpha, out_path, static=False):
    rows = len(grid_chars)
    cols = COLS
    cell_w = FONT_SIZE * CHAR_ASPECT
    cell_h = FONT_SIZE * 1.0
    width = cols * cell_w
    height = rows * cell_h

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.1f} {height:.1f}" '
        f'width="{width:.0f}" height="{height:.0f}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="{BG}"/>')
    parts.append(
        f'<style>text{{font-family:{FONT};font-size:{FONT_SIZE}px;fill:{COLOR};'
        f'white-space:pre;}}</style>'
    )

    for r, row in enumerate(grid_chars):
        y = (r + 0.82) * cell_h
        line = "".join(esc(ch) for ch in row)
        if not line.strip():
            continue
        delay = r * STAGGER
        if static:
            parts.append(f'<text x="0" y="{y:.2f}" opacity="1">{line}</text>')
        else:
            parts.append(
                f'<text x="0" y="{y:.2f}" opacity="0">{line}'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="{ROW_DUR:.3f}s" fill="freeze"/>'
                f'</text>'
            )
    parts.append("</svg>")
    with open(out_path, "w") as f:
        f.write("\n".join(parts))
    print(f"Wrote {out_path}  ({cols}x{rows} chars, {width:.0f}x{height:.0f}px)")


if __name__ == "__main__":
    static = os.environ.get("STATIC", "0") == "1"
    img = load_and_crop("source-prepped.png")
    grid_chars, grid_alpha, cw, ch = to_ascii_grid(img)
    build_svg(grid_chars, grid_alpha, "avi-ascii.svg", static=static)
