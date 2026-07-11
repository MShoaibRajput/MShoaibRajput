#!/usr/bin/env python3
"""Remove background + boost local contrast (CLAHE) so the face reads clearly
once it's converted to monochrome ASCII."""
import sys
import numpy as np
import cv2
from PIL import Image
from rembg import remove

CLIP_LIMIT = 2.5   # tune: higher = punchier local contrast
TILE_GRID = (8, 8)


def prep(in_path, out_path):
    with open(in_path, "rb") as f:
        input_bytes = f.read()

    # 1. Background removal -> RGBA
    out_bytes = remove(input_bytes)
    img = Image.open(__import__("io").BytesIO(out_bytes)).convert("RGBA")

    rgba = np.array(img)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    # 2. CLAHE contrast boost on luminance (LAB L-channel) so the subject
    # has real highlights/shadows instead of being a flat/dark blob.
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=TILE_GRID)
    l2 = clahe.apply(l)
    lab2 = cv2.merge((l2, a, b))
    rgb2 = cv2.cvtColor(lab2, cv2.COLOR_LAB2RGB)

    out = np.dstack([rgb2, alpha])
    Image.fromarray(out, "RGBA").save(out_path)
    print(f"Wrote {out_path} ({out.shape[1]}x{out.shape[0]})")


if __name__ == "__main__":
    in_path = sys.argv[1] if len(sys.argv) > 1 else "photo.png"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep(in_path, out_path)
