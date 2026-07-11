#!/usr/bin/env python3
"""Scrape a GitHub user's public contribution calendar -- no auth, no API
token, just the HTML GitHub already serves for the profile page graph.
Writes data/contributions.json: a flat list of {date, level, count} for the
last ~52 weeks, plus streak stats.
"""
import json
import os
import re
import sys
from datetime import datetime, date
import urllib.request

USERNAME = os.environ.get("GH_PROFILE_USER", "MShoaibRajput")
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


def parse_days(html):
    # Each calendar cell looks like:
    # data-date="2025-07-06" id="contribution-day-component-0-0" data-level="0"
    # Tooltips (separate <tool-tip> elements) hold the human count string,
    # keyed by for="contribution-day-component-W-D". We just need the level
    # for coloring; count is parsed from the tooltip if present.
    day_re = re.compile(r'data-date="(\d{4}-\d{2}-\d{2})"\s+id="([\w-]+)"\s+data-level="(\d)"')
    tooltip_re = re.compile(
        r'for="([\w-]+)">\s*([\d,]+|No)\s+contribution', re.IGNORECASE
    )

    days = {}
    for m in day_re.finditer(html):
        date_str, cell_id, level = m.groups()
        days[cell_id] = {"date": date_str, "level": int(level), "count": None}

    for m in tooltip_re.finditer(html):
        cell_id, count_str = m.groups()
        if cell_id in days:
            days[cell_id]["count"] = 0 if count_str.lower() == "no" else int(count_str.replace(",", ""))

    ordered = sorted(days.values(), key=lambda d: d["date"])
    for d in ordered:
        if d["count"] is None:
            d["count"] = d["level"]  # fallback estimate
    return ordered


def compute_streaks(days):
    total = sum(d["count"] for d in days)
    cur = 0
    longest = 0
    running = 0
    today = date.today()
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak: walk backwards from most recent day with data
    for d in reversed(days):
        if d["count"] > 0:
            cur += 1
        else:
            if datetime.strptime(d["date"], "%Y-%m-%d").date() == today:
                continue  # today may legitimately be 0 so far
            break
    return {"total": total, "longest_streak": longest, "current_streak": cur}


def main():
    try:
        html = fetch_html(URL)
    except Exception as e:
        print(f"Fetch failed ({e}); writing empty dataset.", file=sys.stderr)
        html = ""

    days = parse_days(html) if html else []
    stats = compute_streaks(days) if days else {"total": 0, "longest_streak": 0, "current_streak": 0}

    os.makedirs("data", exist_ok=True)
    out = {"username": USERNAME, "generated": datetime.utcnow().isoformat() + "Z", "stats": stats, "days": days}
    with open("data/contributions.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote data/contributions.json  ({len(days)} days, total={stats['total']})")


if __name__ == "__main__":
    main()
