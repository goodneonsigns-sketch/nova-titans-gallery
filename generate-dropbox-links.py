#!/usr/bin/env python3
"""
Generate Dropbox temporary links for ALL game photos.

Uses /2/files/get_temporary_link (requires files.content.read scope).
Links are valid for 4 hours, so this script should be run just before
building and deploying the site (use regenerate-and-deploy.sh).

Saves progress to dropbox-links.json after each game folder so it can be
safely interrupted and resumed.

Usage:
    python3 generate-dropbox-links.py
    python3 generate-dropbox-links.py --folder 2-12       # only one folder
    python3 generate-dropbox-links.py --reset             # clear and restart
    python3 generate-dropbox-links.py --concurrency 5     # parallel workers (default 3)
"""

import json
import os
import sys
import time
import argparse
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ── Dropbox credentials ──────────────────────────────────────────────────────
APP_KEY       = "kxu7o7wdx0uevph"
APP_SECRET    = "6w18phfie9ezqu9"
REFRESH_TOKEN = "DhoQFza7ABkAAAAAAAAAAeen66ezZWe7xggwMReo9UVYSAipgz8V7qdCEB41ntvS"

# ── Files ────────────────────────────────────────────────────────────────────
GAME_PHOTOS_FILE  = "game-photos.json"
OUTPUT_FILE       = "dropbox-links.json"

# ── Rate-limit / retry config ────────────────────────────────────────────────
DELAY_BETWEEN_CALLS = 0.15   # seconds between individual API calls per worker
DELAY_AFTER_FOLDER  = 0.5    # extra pause after each game folder
MAX_RETRIES         = 5
RETRY_BASE          = 2.0    # exponential back-off base (seconds)

# ── Thread-safe token refresh ────────────────────────────────────────────────
_token_lock   = threading.Lock()
_access_token = None


def refresh_access_token():
    global _access_token
    with _token_lock:
        print("🔑 Refreshing Dropbox access token...")
        resp = requests.post(
            "https://api.dropboxapi.com/oauth2/token",
            data={
                "grant_type":    "refresh_token",
                "refresh_token": REFRESH_TOKEN,
                "client_id":     APP_KEY,
                "client_secret": APP_SECRET,
            },
            timeout=30,
        )
        resp.raise_for_status()
        _access_token = resp.json()["access_token"]
        print("✅ Token refreshed")
        return _access_token


def get_token():
    global _access_token
    if not _access_token:
        refresh_access_token()
    return _access_token


# ── Dropbox API helpers ───────────────────────────────────────────────────────

def get_temporary_link(path: str, retry: int = 0) -> str | None:
    """
    Get a temporary download link for a Dropbox file path.
    Returns URL (valid ~4 hours) or None on failure.
    """
    try:
        resp = requests.post(
            "https://api.dropboxapi.com/2/files/get_temporary_link",
            headers={
                "Authorization": f"Bearer {get_token()}",
                "Content-Type":  "application/json",
            },
            json={"path": path},
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        if retry < MAX_RETRIES:
            wait = RETRY_BASE ** retry
            time.sleep(wait)
            return get_temporary_link(path, retry + 1)
        print(f"    ❌ Network error for {path}: {e}")
        return None

    if resp.status_code == 200:
        return resp.json()["link"]

    if resp.status_code == 401:
        refresh_access_token()
        if retry < 1:
            return get_temporary_link(path, retry + 1)

    if resp.status_code == 429:
        wait = int(resp.headers.get("Retry-After", str(int(RETRY_BASE ** retry))))
        wait = max(wait, int(RETRY_BASE ** retry))
        print(f"    ⏳ Rate-limited. Waiting {wait}s...")
        time.sleep(wait)
        if retry < MAX_RETRIES:
            return get_temporary_link(path, retry + 1)

    if resp.status_code in (500, 503):
        if retry < MAX_RETRIES:
            wait = RETRY_BASE ** retry
            time.sleep(wait)
            return get_temporary_link(path, retry + 1)

    print(f"    ❌ Error {resp.status_code} for {path}: {resp.text[:200]}")
    return None


# ── Progress helpers ──────────────────────────────────────────────────────────

def load_progress() -> dict:
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            return json.load(f)
    return {}


def save_progress(data: dict):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Per-folder processing ─────────────────────────────────────────────────────

_print_lock = threading.Lock()


def fetch_one(file_info: dict) -> tuple[str, str | None]:
    """Fetch temp link for one file. Returns (path, url_or_None)."""
    path = file_info["path"]
    url  = get_temporary_link(path)
    time.sleep(DELAY_BETWEEN_CALLS)
    return path, url


def process_folder(folder: str, files: list, saved: dict, concurrency: int) -> dict:
    """
    Fetch temporary links for all files in the folder.
    Skips files already in `saved`.
    Returns updated dict: path → temp URL.
    """
    result     = dict(saved)
    already    = set(result.keys())
    todo       = [f for f in files if f["path"] not in already]
    total      = len(files)
    n_done     = len(already)

    print(f"  📁 {folder}: {total} files total, {n_done} cached, {len(todo)} to fetch")

    if not todo:
        return result

    completed  = 0
    errors     = 0

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(fetch_one, fi): fi for fi in todo}
        for fut in as_completed(futures):
            path, url = fut.result()
            completed += 1
            if url:
                result[path] = url
            else:
                errors += 1
            if completed % 20 == 0 or completed == len(todo):
                pct = int((n_done + completed) / total * 100)
                with _print_lock:
                    print(f"    [{pct:3d}%] {n_done+completed}/{total}"
                          f"  (errors so far: {errors})")

    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate Dropbox temporary links for all game photos"
    )
    parser.add_argument("--folder",      help="Process only this game folder (e.g. 2-12)")
    parser.add_argument("--reset",       action="store_true",
                        help="Clear dropbox-links.json and start fresh")
    parser.add_argument("--concurrency", type=int, default=3,
                        help="Parallel workers (default: 3)")
    args = parser.parse_args()

    if args.reset and os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print("🗑️  Cleared existing dropbox-links.json")

    # Warm up token
    refresh_access_token()

    # Load game data
    with open(GAME_PHOTOS_FILE) as f:
        game_data = json.load(f)

    # Load existing progress
    progress = load_progress()

    # Which folders?
    folders = [args.folder] if args.folder else sorted(game_data.keys())
    folders = [f for f in folders if f in game_data]

    if not folders:
        print(f"❌ No matching folders. Available: {list(game_data.keys())}")
        sys.exit(1)

    total_files = sum(len(game_data[f].get("all_files", [])) for f in folders)
    cached_files = sum(len(progress.get(f, {})) for f in folders)
    print(f"\n🚀 Processing {len(folders)} folder(s), "
          f"{total_files} total files, {cached_files} already cached")
    print(f"   Concurrency: {args.concurrency} workers\n")

    start_time = time.time()
    grand_total = 0
    grand_done  = 0

    for folder in folders:
        files = game_data[folder].get("all_files", [])
        if not files:
            print(f"⏭️  {folder}: no all_files, skipping")
            continue

        saved = progress.get(folder, {})
        print(f"\n{'─'*60}")

        updated = process_folder(folder, files, saved, args.concurrency)
        progress[folder] = updated

        save_progress(progress)  # persist after every folder

        n_done  = len(updated)
        n_total = len(files)
        grand_total += n_total
        grand_done  += n_done
        print(f"  ✅ {folder}: {n_done}/{n_total} links saved")

        time.sleep(DELAY_AFTER_FOLDER)

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"🎉 Done in {elapsed:.0f}s — {grand_done}/{grand_total} links saved to {OUTPUT_FILE}")

    # Summary
    print("\nPer-folder summary:")
    for folder in folders:
        n = len(progress.get(folder, {}))
        t = len(game_data[folder].get("all_files", []))
        icon = "✅" if n == t else "⚠️ "
        print(f"  {icon} {folder:15s} {n:4d}/{t:4d}")

    if grand_done < grand_total:
        missing = grand_total - grand_done
        print(f"\n⚠️  {missing} files could not be linked. Re-run to retry.")
        sys.exit(1)


if __name__ == "__main__":
    main()
