#!/usr/bin/env python3
"""Generate a neofetch-style 'info card' SVG: a monochrome panel listing
name / title / stack / highlights, each line typing in with a staggered
SMIL animation to match the ASCII portrait's reveal timing.

Usage:
    python make_info_card.py             # animated
    STATIC=1 python make_info_card.py    # final frame only, for preview
"""
import os

# ---- EDIT ME ---------------------------------------------------------------
HOST = "MShoaibRajput@github"

ROWS = [
    ("Name", "Muhammad Shoaib"),
    ("Role", "AI/ML Engineer · Full-Stack Developer"),
    ("Focus", "Application Dev · Computer Engineering"),
    ("Stack", "NestJS · PostgreSQL/Prisma · Redis · Socket.io"),
    ("Frontend", "React · Next.js"),
    ("Cloud", "AWS (Lambda, S3, API Gateway, Amplify)"),
    ("AI/CV", "Python · Computer Vision · YOLOv8"),
    ("Approach", "Vibe coder — build fast, iterate faster"),
]
# -----------------------------------------------------------------------------

COLOR = "#c9d1d9"
ACCENT = "#58a6ff"
DIM = "#6e7681"
BG = "none"
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
FONT_SIZE = 14.5
LINE_H = 27
PAD_X = 22
PAD_TOP = 30
H = 420                  # total card height (match portrait height)
W = 490
LABEL_COL = 108           # x-offset where values start
ROW_DUR = 0.28
STAGGER = 0.10
START_DELAY = 0.4         # small offset so the card starts just after the portrait


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(static=False):
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="{BG}"/>')
    parts.append(
        f'<style>'
        f'.mono{{font-family:{FONT};font-size:{FONT_SIZE}px;white-space:pre;}}'
        f'.label{{fill:{ACCENT};}}'
        f'.val{{fill:{COLOR};}}'
        f'.dim{{fill:{DIM};}}'
        f'.cursor{{fill:{COLOR};}}'
        f'</style>'
    )

    y = PAD_TOP
    # header: user@host
    header = f"{HOST}"
    if static:
        parts.append(f'<text class="mono label" x="{PAD_X}" y="{y}" opacity="1">{esc(header)}</text>')
    else:
        parts.append(
            f'<text class="mono label" x="{PAD_X}" y="{y}" opacity="0">{esc(header)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{START_DELAY:.2f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/></text>'
        )
    y += LINE_H
    rule = "-" * len(header)
    if static:
        parts.append(f'<text class="mono dim" x="{PAD_X}" y="{y}" opacity="1">{esc(rule)}</text>')
    else:
        d = START_DELAY + STAGGER
        parts.append(
            f'<text class="mono dim" x="{PAD_X}" y="{y}" opacity="0">{esc(rule)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{d:.2f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/></text>'
        )
    y += int(LINE_H * 1.15)

    for i, (label, value) in enumerate(ROWS):
        delay = START_DELAY + (i + 2) * STAGGER
        label_txt = f"{label}:"
        if static:
            parts.append(f'<text class="mono label" x="{PAD_X}" y="{y}" opacity="1">{esc(label_txt)}</text>')
            parts.append(f'<text class="mono val" x="{PAD_X + LABEL_COL}" y="{y}" opacity="1">{esc(value)}</text>')
        else:
            parts.append(
                f'<text class="mono label" x="{PAD_X}" y="{y}" opacity="0">{esc(label_txt)}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="{ROW_DUR:.2f}s" fill="freeze"/></text>'
            )
            parts.append(
                f'<text class="mono val" x="{PAD_X + LABEL_COL}" y="{y}" opacity="0">{esc(value)}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay + 0.05:.2f}s" '
                f'dur="{ROW_DUR:.2f}s" fill="freeze"/></text>'
            )
        y += LINE_H

    # small accent swatches row (like neofetch color blocks) — purely decorative
    swatch_y = y + 6
    colors = [ACCENT, "#3fb950", "#d29922", "#f85149", COLOR, DIM]
    for i, c in enumerate(colors):
        x = PAD_X + i * 20
        delay = START_DELAY + (len(ROWS) + 3) * STAGGER
        if static:
            parts.append(f'<rect x="{x}" y="{swatch_y}" width="14" height="14" rx="2" fill="{c}" opacity="1"/>')
        else:
            parts.append(
                f'<rect x="{x}" y="{swatch_y}" width="14" height="14" rx="2" fill="{c}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect>'
            )

    parts.append("</svg>")
    out = "\n".join(parts)
    with open("info-card.svg", "w") as f:
        f.write(out)
    print(f"Wrote info-card.svg ({W}x{H})")


if __name__ == "__main__":
    build_svg(static=os.environ.get("STATIC", "0") == "1")
