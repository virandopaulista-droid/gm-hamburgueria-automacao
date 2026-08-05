#!/usr/bin/env python3
"""Checks whether now matches a scheduled GM Hamburgueria slot and, if so,
picks unused asset(s) from the relevant manifest pool and posts them
(Facebook + Instagram). No week-plan/approval step like Bernardino -- all
three pools (stories/reels/feed) are already-treated media, picked straight
from the categorized manifests, same model as TopTop Pizzaria's automation.

Schedule (adjust here if Rob wants different days/times):
  Every day   19:30 -> 1 story (image or video, from Brenda - Stories pool)
  Friday      11:00 -> 1 feed carousel (5 photos, from Imagens tratadas pool)
  Monday      18:00 -> 1 reel (from Videos Tratados/2026 pool)

Catch-up, not a narrow window: fires as soon as "now" is at or past a
scheduled time (same day), and keeps trying on every later tick until that
slot is marked posted for today -- GitHub's own cron schedule has proven
unreliable about landing near its configured time (see Bernardino's and
TopTop's automations), so a narrow match window can cause entire days to
silently post nothing.

Partial-failure safety: if posting crashes partway through (e.g. the FB leg
of a story succeeds but the Instagram leg errors), the slot is still marked
posted (so the next tick doesn't blindly retry and duplicate whatever
already went out for real) and a GitHub Issue is opened so a human can
check what actually posted. This is the same fix applied to Bernardino's
automation after a real duplicate-post incident on 2026-08-05 (see that
repo's poller.py for the original writeup) -- applied here from day one
instead of waiting to hit the same bug.

Defaults to --dry-run (prints what it would do, does NOT call Facebook).
Pass --live to actually publish.
"""
import datetime
import json
import os
import subprocess
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(PROJECT_DIR, "content", "posted_log.json")

# weekday(): Monday=0 ... Sunday=6
SCHEDULE = [
    {"slot": "story", "weekdays": {0, 1, 2, 3, 4, 5, 6}, "hour": 19, "minute": 30},
    {"slot": "feed", "weekdays": {4}, "hour": 11, "minute": 0},
    {"slot": "reel", "weekdays": {0}, "hour": 18, "minute": 0},
]

DRY_RUN = "--live" not in sys.argv[1:]


def _arg_value(name):
    args = sys.argv[1:]
    if name in args:
        idx = args.index(name)
        if idx + 1 < len(args):
            return args[idx + 1]
    return None


FORCE_SLOT = _arg_value("--force-slot")


def run(cmd):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
    if result.returncode != 0:
        print(f"ERRO rodando {cmd}:\n{result.stderr}", file=sys.stderr)
        raise SystemExit(1)
    return result.stdout.strip()


def bash(script_rel, *args):
    return run(["bash", os.path.join(SCRIPTS_DIR, script_rel), *args])


def python(script_rel, *args):
    return run([sys.executable, os.path.join(SCRIPTS_DIR, script_rel), *args])


def notify_once(marker, body):
    """Best-effort GitHub Issue notification -- never raises."""
    try:
        title = f"[poller] {marker}"
        check = subprocess.run(
            ["gh", "issue", "list", "--search", f'"{title}" in:title', "--state", "open", "--json", "number"],
            capture_output=True, text=True,
        )
        if check.returncode == 0 and check.stdout.strip() and check.stdout.strip() != "[]":
            return
        subprocess.run(["gh", "issue", "create", "--title", title, "--body", body], capture_output=True, text=True)
    except Exception as e:
        print(f"AVISO: notify_once falhou (nao critico): {e}", file=sys.stderr)


def handle_partial_failure(slot_label, exc, now):
    """A handler crashed mid-posting. Some items may have posted for real
    and some may not have -- there's no way to tell which from here. Marking
    "posted" unconditionally is the safer failure mode: it stops the next
    tick from blindly re-running the whole handler and re-posting whatever
    already went out for real. A human has to check Facebook/Instagram
    directly and manually post anything that's actually missing."""
    print(f"##[error] Falha ao publicar '{slot_label}': {exc}", file=sys.stderr)
    notify_once(
        f"post-falhou-{now.date().isoformat()}-{slot_label}",
        f"O poller tentou publicar '{slot_label}' ({now.date().isoformat()}) e um erro interrompeu a publicacao "
        "no meio (alguns itens podem ter saido de verdade, outros nao -- nao da pra saber automaticamente qual). "
        "Para nao arriscar duplicar o que ja saiu, esse slot foi marcado como publicado -- ele NAO sera tentado "
        "de novo automaticamente. Confira manualmente no Facebook/Instagram da GM Hamburgueria o que realmente "
        f"foi publicado, e publique manualmente qualquer item que estiver faltando.\n\nErro original: {exc}"
    )


def load_log():
    if not os.path.exists(LOG_PATH):
        return {}
    with open(LOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_log(log):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def handle_story():
    type_, path = python("select_gm_story.py").split("\t")
    print(f"Selecionado ({type_}): {path}")
    if DRY_RUN:
        print(f"[DRY-RUN] postaria story {type_}: {path}")
        return {"type": type_, "path": path}

    if type_ == "image":
        print(bash("post_story_all.sh", path))
    else:
        print(bash("post_story_video_fb.sh", path))
        fname = os.path.basename(path)
        # Story videos live in a single fixed folder (Brenda - Stories).
        folder_id = os.environ.get("GM_STORIES_DRIVE_FOLDER_ID", "1y80nVtlJv3wqhaV_2SG7HZf3R99nk_jw")
        video_url = python("resolve_drive_url.py", fname, folder_id)
        print(bash("post_story_video_instagram.sh", video_url))
    return {"type": type_, "path": path}


def handle_reel():
    fname, folder, drive_folder_id, path = python("select_gm_reel.py").split("\t")
    print(f"Selecionado: {path}")
    caption_file = python("make_caption.py", "reel")
    if DRY_RUN:
        print(f"[DRY-RUN] postaria reel: {path}")
        return {"path": path}

    print(bash("post_reel_fb.sh", path, caption_file))
    video_url = python("resolve_drive_url.py", fname, drive_folder_id)
    print(bash("post_reel_instagram.sh", caption_file, video_url))
    return {"path": path}


def handle_feed():
    lines = python("select_gm_feed.py", "5").splitlines()
    heic_paths = [line.split("\t", 1)[1] for line in lines]
    print(f"Selecionadas: {heic_paths}")
    caption_file = python("make_caption.py", "feed")
    if DRY_RUN:
        print(f"[DRY-RUN] postaria carrossel de feed: {heic_paths}")
        return {"paths": heic_paths}

    # Facebook/Instagram don't reliably accept raw HEIC -- convert each to
    # JPEG first (two-pass ffmpeg, see convert_heic_to_jpg.sh for why).
    jpg_paths = []
    for i, heic_path in enumerate(heic_paths):
        jpg_path = os.path.join(PROJECT_DIR, f"_tmp_feed_{i}.jpg")
        bash("convert_heic_to_jpg.sh", heic_path, jpg_path)
        jpg_paths.append(jpg_path)

    fb_output = bash("post_feed.sh", caption_file, "now", *jpg_paths)
    print(fb_output)

    for jpg_path in jpg_paths:
        try:
            os.remove(jpg_path)
        except OSError:
            pass

    ig_business_id = os.environ.get("IG_BUSINESS_ID", "").strip()
    if not ig_business_id:
        print("Instagram pulado (IG_BUSINESS_ID nao configurado ainda).")
        return {"paths": heic_paths}

    photo_urls = []
    for line in fb_output.splitlines():
        if line.startswith("PHOTO_URLS:"):
            photo_urls = json.loads(line[len("PHOTO_URLS:"):])
    if not photo_urls:
        print("AVISO: sem URL publica de foto, pulando Instagram.", file=sys.stderr)
        return {"paths": heic_paths}
    print(bash("post_instagram.sh", caption_file, *photo_urls))
    return {"paths": heic_paths}


HANDLERS = {"story": handle_story, "feed": handle_feed, "reel": handle_reel}


def main():
    now = datetime.datetime.now()
    today_key = now.date().isoformat()
    log = load_log()

    if FORCE_SLOT:
        key = f"{today_key}_{FORCE_SLOT}"
        if key in log:
            print("AVISO: esse slot ja foi marcado como publicado hoje.", file=sys.stderr)
            return
        print(f"Forcando slot '{FORCE_SLOT}' ({'DRY-RUN' if DRY_RUN else 'LIVE'})...")
        try:
            result = HANDLERS[FORCE_SLOT]()
        except Exception as exc:
            if not DRY_RUN:
                handle_partial_failure(FORCE_SLOT, exc, now)
                log[key] = {"posted_at": now.isoformat(timespec="seconds"), "partial_failure": str(exc)}
                save_log(log)
            raise
        if not DRY_RUN:
            log[key] = {"posted_at": now.isoformat(timespec="seconds"), **result}
            save_log(log)
        return

    for entry in SCHEDULE:
        if now.weekday() not in entry["weekdays"]:
            continue
        scheduled = now.replace(hour=entry["hour"], minute=entry["minute"], second=0, microsecond=0)
        if now < scheduled:
            continue
        key = f"{today_key}_{entry['slot']}"
        if key in log:
            continue

        print(f"Disparando slot '{entry['slot']}' ({'DRY-RUN' if DRY_RUN else 'LIVE'})...")
        try:
            result = HANDLERS[entry["slot"]]()
        except Exception as exc:
            if not DRY_RUN:
                handle_partial_failure(entry["slot"], exc, now)
                log[key] = {"posted_at": now.isoformat(timespec="seconds"), "partial_failure": str(exc)}
                save_log(log)
            raise

        if not DRY_RUN:
            log[key] = {"posted_at": now.isoformat(timespec="seconds"), **result}
            save_log(log)
        return

    print("Nenhum slot devido agora.")


if __name__ == "__main__":
    main()
