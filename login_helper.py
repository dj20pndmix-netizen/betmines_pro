"""
TikTok Login & Session Setup Helper
Uses Playwright persistent context so login credentials, cookies, and tokens
remain saved securely on your local machine in the 'tiktok_profile' folder.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_profile")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

def launch_login():
    print("=" * 60)
    print("           TIKTOK MANUAL LOGIN HELPER")
    print("=" * 60)
    print(f"Profile directory: {PROFILE_DIR}")
    print("\n1. A browser window will now open.")
    print("2. Please log into your TikTok account manually (QR code, email, etc.).")
    print("3. Solve any verification puzzles or 2FA if prompted.")
    print("4. Once you are fully logged in and on the feed, return here and press Enter.")
    print("=" * 60)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            channel="chromium",
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--start-maximized",
            ],
            ignore_default_args=["--enable-automation"],
        )

        page = context.pages[0] if context.pages else context.new_page()

        # Add stealth scripts to hide automation
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        print("\nNavigating to TikTok login page...")
        try:
            page.goto("https://www.tiktok.com/login", wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Notice during navigation: {e}")

        print("\nBrowser is open! Waiting for you to complete your login...")
        input("\n>>> Press [ENTER] once you are successfully logged into TikTok in the browser... <<<")

        print("\nVerifying session and saving cookies...")
        time.sleep(2)
        cookies = context.cookies("https://www.tiktok.com")
        session_id_exists = any("sessionid" in c["name"].lower() for c in cookies)

        if session_id_exists:
            print("[SUCCESS] Session ID detected! Your login state has been saved.")
        else:
            print("[INFO] Session saved to profile folder. Make sure you were fully logged in.")

        print(f"All session data is persisted in: {PROFILE_DIR}")
        context.close()
        print("Done! You can now run the automation bot.")

if __name__ == "__main__":
    launch_login()
