# Setup Guide — Animated GitHub Profile

This walks you through deploying the files in `github-profile-template.zip` to
your live GitHub profile. Total time: ~10 minutes.

---

## 0. Prerequisites

- A GitHub account with username **`MShoaibRajput`** (the repo name must match this exactly — that's the trick that makes GitHub render it on your profile)
- `git` installed locally ([git-scm.com](https://git-scm.com/downloads))
- Optional, only if you want to re-tune the portrait later: Python 3.9+ with `pip`

Check git is installed:
```bash
git --version
```

---

## 1. Unzip the project

Download `github-profile-template.zip` and extract it:

```bash
unzip github-profile-template.zip -d MShoaibRajput
cd MShoaibRajput
```

You should see:
```
README.md
avi-ascii.svg
info-card.svg
contrib-heatmap.svg
requirements-local.txt
.gitignore
scripts/
  prep_photo.py
  make_ascii_svg.py
  make_info_card.py
  fetch_contributions.py
  render_heatmap_svg.py
  requirements.txt
data/
  contributions.json
.github/
  workflows/
    update-profile-art.yml
```

---

## 2. Create the special profile repository

On GitHub:

1. Click **+ → New repository** (top right)
2. Repository name: **`MShoaibRajput`** — must match your username exactly, case included
3. Set it to **Public** (private repos don't render on your profile)
4. **Do not** initialize with a README, .gitignore, or license — you already have these locally
5. Click **Create repository**

GitHub will show you an empty repo with a "push an existing repository" section — keep that page open, you'll need the URL.

---

## 3. Push your local files

From inside the `MShoaibRajput` folder:

```bash
git init
git add .
git commit -m "Initial commit: animated profile README"
git branch -M main
git remote add origin https://github.com/MShoaibRajput/MShoaibRajput.git
git push -u origin main
```

If prompted, sign in with your GitHub credentials (or a personal access token if you have 2FA — GitHub will guide you through this on first push).

Refresh your repo page — you should now see all the files, and GitHub will already render the README below the file list (the SVGs will show their **static first frame** in the repo view; the typing/reveal animation plays when loaded fresh, e.g. on your profile page).

---

## 4. Give the daily workflow permission to commit

The `update-profile-art.yml` workflow needs write access to push its own commits (the refreshed contribution graph) back to the repo.

1. Go to your repo → **Settings** tab
2. Left sidebar → **Actions → General**
3. Scroll to **Workflow permissions**
4. Select **Read and write permissions**
5. Click **Save**

---

## 5. Run the workflow once manually

The workflow is scheduled to run daily on its own, but trigger it once now so the real contribution graph appears immediately instead of waiting for tomorrow:

1. Go to your repo → **Actions** tab
2. Click **"Update profile art"** in the left sidebar
3. Click **Run workflow** (dropdown button, top right) → **Run workflow** (confirm)
4. Wait ~10–20 seconds, refresh — you should see a green checkmark
5. Check the **Commits** tab — you'll see an automated commit like `chore: refresh contribution graph` if your data changed

If it fails (red X), click into the run to see the log — the most common cause is step 4 (workflow permissions) not being saved yet.

---

## 6. View your live profile

Go to **`https://github.com/MShoaibRajput`** (your profile page, not the repo page). The README now renders there automatically, with the portrait typing in and the heatmap revealing cell by cell on load.

> Note: your account currently shows 0 public contributions in the last year, so the heatmap will be all gray until you start committing to public repos. That's accurate — not a bug. It'll fill in automatically as you work.

---

## 7. Ongoing — you don't need to do anything

Every day at 03:17 UTC, the GitHub Action:
1. Re-scrapes your public contribution calendar (no login, no token)
2. Re-renders `contrib-heatmap.svg`
3. Commits the update if anything changed

Nothing to maintain.

---

## Re-tuning things later (optional)

All of this needs the **local-only** deps (background removal + image processing), not the lightweight daily-workflow ones:

```bash
pip install -r requirements-local.txt --break-system-packages   # or use a venv
```

| Want to… | Edit | Then run |
|---|---|---|
| Use a different photo | — | `python scripts/prep_photo.py your-photo.jpg source-prepped.png` then `python scripts/make_ascii_svg.py` |
| Punchier/lighter face | `CONTRAST`, `GAMMA`, `WHITE_FLOOR` in `make_ascii_svg.py`; `CLIP_LIMIT` in `prep_photo.py` | `python scripts/make_ascii_svg.py` |
| Tighter/looser crop | `PAD_FRAC`, `SHOULDER_FRAC` in `make_ascii_svg.py` | same |
| Type faster/slower | `ROW_DUR`, `STAGGER` in `make_ascii_svg.py` | same |
| Change info card content | `ROWS` list in `make_info_card.py` | `python scripts/make_info_card.py` |
| Info card too tall/short | `H` in `make_info_card.py`, then re-match `width=` in `README.md` if needed | same |

Preview any SVG without pushing to GitHub by rendering a static frame:
```bash
STATIC=1 python scripts/make_ascii_svg.py
```
(add `STATIC=1` the same way for `make_info_card.py` and `render_heatmap_svg.py`) — this fills in the final frame instead of the animated reveal, so you can open it directly in a browser or image viewer to check it before committing.

After tuning, just commit and push the changed SVG(s) — no need to touch the workflow.

---

## Troubleshooting

**README isn't showing on my profile**
The repo name must be *exactly* your username, must be public, and must contain a `README.md` at the root. Double check spelling/case.

**SVGs show up broken/as plain text links**
Make sure the SVG files are committed at the repo root (not inside a subfolder unless you also update the `src=` paths in `README.md`).

**Workflow runs but nothing changes**
Normal if your contribution count hasn't changed since the last run — the workflow only commits when the data actually differs.

**Workflow fails with a permissions error**
Revisit step 4 — "Read and write permissions" must be saved under Settings → Actions → General.
