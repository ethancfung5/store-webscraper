import json
import os
import time
import requests
from bs4 import BeautifulSoup

# ================== SETTINGS ==================

URL = "https://forestcitycollectibles.com/collections/one-piece-sealed-1"

# Shopify "Dawn" style themes usually put product titles in h3.card__heading a
# If it ever stops working, we can tweak this selector.
ITEM_SELECTOR = "h3.card__heading a"

# How often to check (in seconds). Please keep this reasonably high to be polite.
SLEEP_SECONDS = 600  # 10 minutes

# Discord webhook for notifications
WEBHOOK_URL = ""

# File to store the last known list of items
SNAPSHOT_FILE = "one_piece_items_snapshot.json"

# ================== SCRAPING LOGIC ==================


def fetch_items():
    """
    Fetch the page and return a dict:
        { item_name: item_url, ... }
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (monitor script for personal use)"
    }
    resp = requests.get(URL, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    items = {}

    # grab all product title links
    for a in soup.select(ITEM_SELECTOR):
        name = a.get_text(strip=True)
        href = a.get("href", "").strip()

        if not name:
            continue

        # Make relative URLs absolute
        if href.startswith("/"):
            href = "https://forestcitycollectibles.com" + href

        items[name] = href or URL

    return items


# ================== DISCORD HELPER ==================


def send_discord_message(content: str):
    if not WEBHOOK_URL:
        print("[WARN] WEBHOOK_URL not set; would have sent:")
        print(content)
        return

    payload = {"content": content}
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        r.raise_for_status()
        print("[INFO] Sent Discord notification.")
    except Exception as e:
        print(f"[ERROR] Failed to send Discord message: {e}")


# ================== SNAPSHOT HELPERS ==================


def load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    try:
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not load snapshot file: {e}")
        return {}


def save_snapshot(items: dict):
    try:
        with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Snapshot saved with {len(items)} items.")
    except Exception as e:
        print(f"[ERROR] Failed to save snapshot: {e}")


# ================== MAIN MONITOR LOOP ==================


def main():
    print(f"Monitoring: {URL}")
    previous_items = load_snapshot()

    if not previous_items:
        # First run: save snapshot but don't spam Discord.
        print("[INFO] No previous snapshot found. Fetching initial list...")
        current_items = fetch_items()
        save_snapshot(current_items)
        print(f"[INFO] Initial snapshot has {len(current_items)} items.")
    else:
        print(f"[INFO] Loaded snapshot with {len(previous_items)} items.")

    while True:
        print(f"\n[INFO] Checking for updates...")
        try:
            current_items = fetch_items()
        except Exception as e:
            print(f"[ERROR] Could not fetch items: {e}")
            time.sleep(SLEEP_SECONDS)
            continue

        previous_items = load_snapshot()  # reload in case you edited it manually

        prev_names = set(previous_items.keys())
        curr_names = set(current_items.keys())

        added = curr_names - prev_names
        removed = prev_names - curr_names

        if added or removed:
            lines = [":rotating_light: **Forest City – One Piece Sealed page changed!**"]

            if added:
                lines.append("\n**Added:**")
                for name in sorted(added):
                    url = current_items.get(name, URL)
                    lines.append(f"- {name} ({url})")

            if removed:
                lines.append("\n**Removed:**")
                for name in sorted(removed):
                    url = previous_items.get(name, URL)
                    lines.append(f"- {name} ({url})")

            message = "\n".join(lines)
            print(message)
            send_discord_message(message)

            # Update snapshot so we don’t re-alert on the same change.
            save_snapshot(current_items)
        else:
            print("[INFO] No changes detected.")

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
