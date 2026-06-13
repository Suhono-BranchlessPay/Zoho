"""Capture verify page screenshots for submission package."""

from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URLS_FILE = os.path.join(ROOT, "docs", "LIVE_VERIFY_URLS.json")
OUT_DIR = os.path.join(ROOT, "docs", "screenshots")


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Installing playwright...")
        os.system('"%s" -m pip install playwright -q' % sys.executable)
        os.system('"%s" -m playwright install chromium' % sys.executable)
        from playwright.sync_api import sync_playwright

    if not os.path.isfile(URLS_FILE):
        print("Run scripts/simulate_all_events.py first")
        return 1

    with open(URLS_FILE, encoding="utf-8") as handle:
        entries = json.load(handle)

    os.makedirs(OUT_DIR, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 1600})
        for entry in entries:
            url = entry.get("verify_url")
            event = str(entry.get("event_type", "event")).replace(".", "-")
            ref = str(entry.get("reference", "ref")).replace("/", "-")
            if not url:
                print("SKIP", event, "no verify_url")
                continue
            filename = "zoho-%s-%s.png" % (event, ref)
            path = os.path.join(OUT_DIR, filename)
            print("Screenshot", url, "->", filename)
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(2)
            page.screenshot(path=path, full_page=True)
        browser.close()

    print("Saved screenshots to", OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
