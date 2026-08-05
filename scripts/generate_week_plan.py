#!/usr/bin/env python3
"""Generates a week's posting plan for GM Hamburgueria and writes it to
content/week_plans/<monday>.json with status "pending_approval" -- nothing
gets posted from a plan until approve_week_plan.py flips that to "approved"
(same review-before-publish model as Bernardino's automation; unlike
TopTop's, GM does NOT pick content live at posting time).

Picks (from the manifests in content/, marking each pick "used" there so
the same item doesn't repeat until its pool cycles through):
  - 1 story per day, Mon-Sun (gm_stories_manifest.json)
  - 1 weekly feed post, Friday -- EITHER a reel OR a carousel of 5 photos,
    never both in the same week (gm_reels_manifest.json /
    gm_feed_manifest.json), chosen at random each week.

Usage: generate_week_plan.py [YYYY-MM-DD]
  Date is any day in the target week; defaults to next Monday. Prints the
  path to the generated plan file.
"""
import datetime
import json
import os
import random
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(PROJECT_DIR, "content")
PLANS_DIR = os.path.join(CONTENT_DIR, "week_plans")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_caption import TEMPLATES, FOOTER  # noqa: E402

WEEKDAY_NAMES = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]


def week_monday(date):
    return date - datetime.timedelta(days=date.weekday())


def load_manifest(name):
    path = os.path.join(CONTENT_DIR, name)
    with open(path, encoding="utf-8") as f:
        return json.load(f), path


def save_manifest(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def pick_unused(data, n=1):
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
    return picks


def main():
    if len(sys.argv) > 1:
        ref_date = datetime.date.fromisoformat(sys.argv[1])
    else:
        today = datetime.date.today()
        ref_date = today + datetime.timedelta(days=(7 - today.weekday()) % 7 or 7)
    monday = week_monday(ref_date)

    stories_data, stories_path = load_manifest("gm_stories_manifest.json")
    reels_data, reels_path = load_manifest("gm_reels_manifest.json")
    feed_data, feed_path = load_manifest("gm_feed_manifest.json")

    posts = []
    for i in range(7):
        day = monday + datetime.timedelta(days=i)
        pick = pick_unused(stories_data, 1)[0]
        posts.append({
            "date": day.isoformat(),
            "weekday": WEEKDAY_NAMES[i],
            "slot": "story",
            "items": [{"file": pick["file"], "type": pick["type"]}],
        })

    # One weekly feed post -- reel OR carousel, never both the same week.
    friday = monday + datetime.timedelta(days=4)
    weekly_kind = random.choice(["reel", "feed"])
    if weekly_kind == "reel":
        reel_pick = pick_unused(reels_data, 1)[0]
        posts.append({
            "date": friday.isoformat(),
            "weekday": "sexta",
            "slot": "reel",
            "items": [{
                "file": reel_pick["file"],
                "folder": reel_pick["folder"],
                "drive_folder_id": reel_pick["drive_folder_id"],
            }],
            "caption_text": random.choice(TEMPLATES["reel"]) + FOOTER,
        })
    else:
        feed_picks = pick_unused(feed_data, 5)
        posts.append({
            "date": friday.isoformat(),
            "weekday": "sexta",
            "slot": "feed",
            "items": [{"file": p["file"], "folder": p["folder"]} for p in feed_picks],
            "caption_text": random.choice(TEMPLATES["feed"]) + FOOTER,
        })

    posts.sort(key=lambda p: (p["date"], p["slot"] != "story"))

    plan = {
        "week_start": monday.isoformat(),
        "status": "pending_approval",
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "posts": posts,
    }

    os.makedirs(PLANS_DIR, exist_ok=True)
    plan_path = os.path.join(PLANS_DIR, f"{monday.isoformat()}.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    save_manifest(stories_data, stories_path)
    save_manifest(reels_data, reels_path)
    save_manifest(feed_data, feed_path)

    print(plan_path)


if __name__ == "__main__":
    main()
