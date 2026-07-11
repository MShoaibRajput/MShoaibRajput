#!/usr/bin/env python3
"""Render data/contributions.json into a GitHub-style contribution heatmap
SVG: a grid of boxes that reveal cell-by-cell (SMIL), a Less->More legend,
and real streak stats printed underneath.
"""
import json
from collections import defaultdict
from datetime import datetime

CELL = 11
GAP = 3
LEVEL_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BG = "none"
TEXT_COLOR = "#8b949e"
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
FONT_SIZE = 11
REVEAL_DUR = 0.012      # seconds per cell fade-in
REVEAL_STAGGER = 0.0022  # seconds delay increment per cell (by column)
MONTH_LABEL_H = 16
LEGEND_H = 22
FOOTER_H = 20


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load():
    with open("data/contributions.json") as f:
        return json.load(f)


def build(data, static=False):
    days = data["days"]
    stats = data["stats"]
    username = data["username"]

    # group into weeks (columns), Sun-Sat rows, matching GitHub's layout
    by_date = {d["date"]: d for d in days}
    if not days:
        weeks = []
    else:
        first = datetime.strptime(days[0]["date"], "%Y-%m-%d")
        # rewind to the most recent Sunday on/before first day
        offset = (first.weekday() + 1) % 7  # Mon=0..Sun=6 -> Sun=0
        start = first
        import datetime as dtmod
        start = first - dtmod.timedelta(days=offset)

        last = datetime.strptime(days[-1]["date"], "%Y-%m-%d")
        weeks = []
        cur_week = []
        d = start
        while d <= last:
            key = d.strftime("%Y-%m-%d")
            cell = by_date.get(key, {"date": key, "level": 0, "count": 0})
            cur_week.append(cell)
            if len(cur_week) == 7:
                weeks.append(cur_week)
                cur_week = []
            d += dtmod.timedelta(days=1)
        if cur_week:
            while len(cur_week) < 7:
                cur_week.append(None)
            weeks.append(cur_week)

    n_weeks = len(weeks)
    grid_w = n_weeks * (CELL + GAP)
    grid_h = 7 * (CELL + GAP)
    width = grid_w + 10
    height = MONTH_LABEL_H + grid_h + LEGEND_H + FOOTER_H + 10

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    parts.append(f'<rect width="100%" height="100%" fill="{BG}"/>')
    parts.append(
        f'<style>.lbl{{font-family:{FONT};font-size:{FONT_SIZE}px;fill:{TEXT_COLOR};}}</style>'
    )

    # month labels (only when the month changes going down a week's first day)
    last_month = None
    for wi, week in enumerate(weeks):
        first_day = next((c for c in week if c), None)
        if not first_day:
            continue
        dt = datetime.strptime(first_day["date"], "%Y-%m-%d")
        if dt.month != last_month:
            x = 5 + wi * (CELL + GAP)
            parts.append(f'<text class="lbl" x="{x}" y="{MONTH_LABEL_H - 4}">{dt.strftime("%b")}</text>')
            last_month = dt.month

    # cells
    for wi, week in enumerate(weeks):
        for di, cell in enumerate(week):
            if cell is None:
                continue
            x = 5 + wi * (CELL + GAP)
            y = MONTH_LABEL_H + di * (CELL + GAP)
            level = min(4, cell.get("level", 0))
            color = LEVEL_COLORS[level]
            delay = wi * REVEAL_STAGGER + di * (REVEAL_STAGGER * 0.3)
            title = f'{cell["count"]} contributions on {cell["date"]}'
            if static:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" '
                    f'fill="{color}" opacity="1"><title>{esc(title)}</title></rect>'
                )
            else:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" '
                    f'fill="{color}" opacity="0">'
                    f'<title>{esc(title)}</title>'
                    f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.4f}s" '
                    f'dur="{REVEAL_DUR:.4f}s" fill="freeze"/>'
                    f'</rect>'
                )

    # legend: Less -> More
    legend_y = MONTH_LABEL_H + grid_h + 14
    lx = 5
    parts.append(f'<text class="lbl" x="{lx}" y="{legend_y + 9}">Less</text>')
    lx += 34
    for i, c in enumerate(LEVEL_COLORS):
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
        lx += CELL + GAP
    parts.append(f'<text class="lbl" x="{lx + 2}" y="{legend_y + 9}">More</text>')

    # footer stats
    footer_y = legend_y + LEGEND_H
    footer = (
        f"{stats['total']} contributions in the last year  ·  "
        f"current streak {stats['current_streak']}  ·  longest streak {stats['longest_streak']}"
    )
    parts.append(f'<text class="lbl" x="5" y="{footer_y}">{esc(footer)}</text>')

    parts.append("</svg>")
    with open("contrib-heatmap.svg", "w") as f:
        f.write("\n".join(parts))
    print(f"Wrote contrib-heatmap.svg ({width}x{height}), {n_weeks} weeks")


if __name__ == "__main__":
    import os
    build(load(), static=os.environ.get("STATIC", "0") == "1")
