#!/usr/bin/env python3
"""Picks ONE unused video from content/gm_reels_manifest.json and marks it
used. Reels live across several month subfolders of 'Videos Tratados/2026',
so each manifest entry carries its own 'folder' (for local/rclone path
resolution) and 'drive_folder_id' (for resolve_drive_url.py's public-URL
scraping on the Instagram leg).

If the pool runs out of unused assets, it auto-resets.

Usage: select_gm_reel.py
Prints one line: file<TAB>folder<TAB>drive_folder_id<TAB>absolute_path
"""
import datetime
import json
import os
import random

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(PROJECT_DIR, "content", "gm_reels_manifest.json")
# Windows default kept for local runs; GitHub Actions sets GM_VIDEOS_DIR to
# the rclone-mounted 'Videos Tratados/2026' path instead.
BASE_DIR = os.environ.get(
    "GM_VIDEOS_DIR",
    r"G:\Meu Drive\Agência BEEF MTK\Clientes\GM - Hamburgueria\Vídeos Tratados\2026",
)


def load():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    data = load()
    assets = data["assets"]
    pool = [a for a in assets if not a["used"]]
    if not pool:
        for a in assets:
            a["used"] = False
            a["used_at"] = None
        pool = assets
    entry = random.choice(pool)
    entry["used"] = True
    entry["used_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    save(data)
    path = os.path.join(BASE_DIR, entry["folder"], entry["file"])
    print(f"{entry['file']}\t{entry['folder']}\t{entry['drive_folder_id']}\t{path}")


if __name__ == "__main__":
    main()
