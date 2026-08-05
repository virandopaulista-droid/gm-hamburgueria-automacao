#!/usr/bin/env python3
"""Picks ONE unused asset from content/gm_stories_manifest.json (any type --
image or video) and marks it used.

If the pool runs out of unused assets, it auto-resets (all marked unused
again) so the rotation never stalls.

Usage: select_gm_story.py
Prints one line: type<TAB>absolute_path
"""
import datetime
import json
import os
import random

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(PROJECT_DIR, "content", "gm_stories_manifest.json")
# Windows default kept for local runs; GitHub Actions sets GM_STORIES_DIR
# to the rclone-mounted path instead (no G:\ drive there).
ASSETS_DIR = os.environ.get(
    "GM_STORIES_DIR",
    r"G:\Meu Drive\Agência BEEF MTK\Clientes\GM - Hamburgueria\STORIES\Brenda - Stories",
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
    path = os.path.join(ASSETS_DIR, entry["file"])
    print(f"{entry['type']}\t{path}")


if __name__ == "__main__":
    main()
