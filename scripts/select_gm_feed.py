#!/usr/bin/env python3
"""Picks N unused images from content/gm_feed_manifest.json for a feed
carousel and marks them used. Images live across several month subfolders
of 'Imagens tratadas/Ano 2026', so each manifest entry carries its own
'folder' for local/rclone path resolution.

All source files are .HEIC -- conversion to .jpg happens downstream in
poller.py (Facebook/Instagram don't reliably accept raw HEIC uploads), not
here. This script only selects and prints the original .HEIC paths.

If the pool has fewer than N unused assets left, it auto-resets first.

Usage: select_gm_feed.py [n]   (n defaults to 5)
Prints n lines: folder<TAB>absolute_path
"""
import datetime
import json
import os
import random
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(PROJECT_DIR, "content", "gm_feed_manifest.json")
# Windows default kept for local runs; GitHub Actions sets GM_IMAGES_DIR to
# the rclone-mounted 'Imagens tratadas' path instead.
BASE_DIR = os.environ.get(
    "GM_IMAGES_DIR",
    r"G:\Meu Drive\Agência BEEF MTK\Clientes\GM - Hamburgueria\Imagens tratadas",
)


def load():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    data = load()
    assets = data["assets"]
    pool = [a for a in assets if not a["used"]]
    if len(pool) < n:
        for a in assets:
            a["used"] = False
            a["used_at"] = None
        pool = assets
    picks = random.sample(pool, min(n, len(pool)))
    now = datetime.datetime.now().isoformat(timespec="seconds")
    for entry in picks:
        entry["used"] = True
        entry["used_at"] = now
    save(data)
    for entry in picks:
        path = os.path.join(BASE_DIR, entry["folder"], entry["file"])
        print(f"{entry['folder']}\t{path}")


if __name__ == "__main__":
    main()
