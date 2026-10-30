"""
TikTok Automation Bot - Auto-Like & Auto-Follow
Automates liking and following on TikTok's For You feed or Hashtag feeds
with humanized intervals, randomized watch durations, and safety limits.
"""

import os
import sys
import json
import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_profile")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Warning: {CONFIG_FILE} not found. Using defaults.")
        return {
            "mode": "foryou",
            "target_hashtag": "fyp",
            "max_likes": 25,
            "max_follows": 10,
            "like_probability": 0.75,
            "follow_probability": 0.30,
            "min_watch_seconds": 6,
            "max_watch_seconds": 15,
            "min_delay_between_actions": 3,
            "max_delay_between_actions": 7,
            "headless": False
        }
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def random_delay(min_sec, max_sec):
    duration = round(random.uniform(min_sec, max_sec), 2)
    time.sleep(duration)
    return duration

class TikTokBot:
    def __init__(self, config):
        self.config = config
        self.likes_count = 0
        self.follows_count = 0
        self.videos_seen = 0

    def run(self):
        print("=" * 60)
        print("         TIKTOK AUTOMATION BOT (LIKES & FOLLOWS)")
        print("=" * 60)
        print(f"Target Mode:          {self.config.get('mode', 'foryou').upper()}")
        if self.config.get("mode") == "hashtag":
            print(f"Hashtag:              #{self.config.get('target_hashtag')}")
        print(f"Max Likes Cap:        {self.config.get('max_likes')}")
        print(f"Max Follows Cap:      {self.config.get('max_follows')}")
        print(f"Like Probability:     {int(self.config.get('like_probability', 0.75) * 100)}%")
        print(f"Follow Probability:   {int(self.config.get('follow_probability', 0.30) * 100)}%")
        print(f"Watch Duration:       {self.config.get('min_watch_seconds')}-{self.config.get('max_watch_seconds')}s per video")
        print("=" * 60)

        if not os.path.exists(PROFILE_DIR):
            print("\n[!] WARNING: Profile folder 'tiktok_profile' not found.")
            print("Please run 'python login_helper.py' first to sign into your account!")
            return

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                headless=self.config.get("headless", False),
                channel="chromium",
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 850},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars",
                ],
                ignore_default_args=["--enable-automation"],
            )

            page = context.pages[0] if context.pages else context.new_page()

            # Anti-bot detection script override
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            try:
                if self.config.get("mode") == "hashtag":
                    tag = self.config.get("target_hashtag", "fyp").strip("#")
                    target_url = f"https://www.tiktok.com/tag/{tag}"
                else:
                    target_url = "https://www.tiktok.com/foryou"

                print(f"\n[+] Navigating to: {target_url}")
                page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
                random_delay(4, 7)

                # Check if in hashtag mode and need to open the first video
                if self.config.get("mode") == "hashtag":
                    self._open_first_hashtag_video(page)

                # Dismiss any initial modal popups (e.g. login prompt if guest, or cookie disclaimer)
                self._dismiss_modals(page)

                # Main automation loop
                self._automation_loop(page)

            except KeyboardInterrupt:
                print("\n[!] Bot stopped manually by user (Ctrl+C).")
            except Exception as e:
                print(f"\n[!] Error during automation: {e}")
            finally:
                print("\n" + "=" * 60)
                print("SESSION SUMMARY:")
                print(f"  Videos Watched:   {self.videos_seen}")
                print(f"  Likes Given:      {self.likes_count} / {self.config.get('max_likes')}")
                print(f"  Follows Given:    {self.follows_count} / {self.config.get('max_follows')}")
                print("=" * 60)
                context.close()

    def _open_first_hashtag_video(self, page):
        print("[+] Locating first video in hashtag grid...")
        video_selectors = [
            'div[data-e2e="challenge-item"] a',
            'div[class*="DivItemContainerV2"] a',
            'a[href*="/video/"]',
        ]
        for sel in video_selectors:
            try:
                first_video = page.locator(sel).first
                if first_video.is_visible(timeout=5000):
                    first_video.click()
                    print("[+] Opened first video in modal.")
                    random_delay(3, 5)
                    return True
            except Exception:
                continue
        print("[!] Could not auto-open first video in hashtag. Will attempt feed mode.")
        return False

    def _dismiss_modals(self, page):
        """Attempts to close generic popups or cookie bars."""
        dismiss_selectors = [
            'button:has-text("Decline optional cookies")',
            'button:has-text("Accept all")',
            '[data-e2e="modal-close-inner-button"]',
            'div[role="dialog"] button[aria-label="Close"]',
        ]
        for sel in dismiss_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    random_delay(1, 2)
            except Exception:
                pass

    def _automation_loop(self, page):
        max_likes = self.config.get("max_likes", 25)
        max_follows = self.config.get("max_follows", 10)

        while self.likes_count < max_likes or self.follows_count < max_follows:
            self.videos_seen += 1
            print(f"\n--- [Video #{self.videos_seen}] ---")

            # 1. Watch video for randomized realistic duration
            watch_time = random_delay(
                self.config.get("min_watch_seconds", 6),
                self.config.get("max_watch_seconds", 15)
            )
            print(f"[Watch] Watched video for {watch_time}s")

            # Random slight mouse jitter to simulate human browsing
            self._simulate_human_jitter(page)

            # 2. Check if we should Like
            if self.likes_count < max_likes:
                if random.random() <= self.config.get("like_probability", 0.75):
                    liked = self._try_like_current_video(page)
                    if liked:
                        self.likes_count += 1
                        print(f"[LIKE] Liked video! (Total: {self.likes_count}/{max_likes})")
                    else:
                        print("[LIKE] Skipped (already liked or button not found)")
                else:
                    print("[LIKE] Skipped by probability roll")

            # Brief pause between like & follow
            random_delay(
                self.config.get("min_delay_between_actions", 2),
                self.config.get("max_delay_between_actions", 5)
            )

            # 3. Check if we should Follow
            if self.follows_count < max_follows:
                if random.random() <= self.config.get("follow_probability", 0.30):
                    followed = self._try_follow_creator(page)
                    if followed:
                        self.follows_count += 1
                        print(f"[FOLLOW] Followed creator! (Total: {self.follows_count}/{max_follows})")
                    else:
                        print("[FOLLOW] Skipped (already followed or button not found)")
                else:
                    print("[FOLLOW] Skipped by probability roll")

            # Check if all caps reached
            if self.likes_count >= max_likes and self.follows_count >= max_follows:
                print("\n[+] Both like and follow targets reached! Ending session safely.")
                break

            # 4. Scroll to next video
            self._go_to_next_video(page)
            random_delay(2, 4)

    def _simulate_human_jitter(self, page):
        try:
            x = random.randint(200, 700)
            y = random.randint(200, 600)
            page.mouse.move(x, y, steps=5)
        except Exception:
            pass

    def _try_like_current_video(self, page):
        """Finds the like button on the active video and clicks it if not already liked."""
        # Common TikTok like selectors
        like_btn_selectors = [
            'button[data-e2e="browse-like-icon"]',
            'button[data-e2e="like-icon"]',
            'span[data-e2e="browse-like-icon"]',
            'span[data-e2e="like-icon"]',
            'button[aria-label*="Like this video"]',
            'button[aria-label*="like this video"]',
        ]

        for sel in like_btn_selectors:
            try:
                # Find visible like buttons
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    # Check if already liked (aria-pressed or SVG fill color)
                    aria_pressed = btn.get_attribute("aria-pressed")
                    if aria_pressed == "true":
                        return False # already liked

                    # Check inner SVG or color
                    html_content = btn.inner_html()
                    if 'fill="rgba(254, 44, 85' in html_content or '#fe2c55' in html_content:
                        return False # already liked

                    btn.click()
                    return True
            except Exception:
                continue

        # Fallback: TikTok web supports pressing 'L' hotkey for active video!
        try:
            page.keyboard.press("l")
            return True
        except Exception:
            return False

    def _try_follow_creator(self, page):
        """Finds the Follow button for the current video's creator."""
        follow_selectors = [
            'button[data-e2e="feed-follow-button"]',
            'button[data-e2e="follow-button"]',
            'button:has-text("Follow")',
        ]

        for sel in follow_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    text = btn.inner_text().strip()
                    # Only click if button explicitly says "Follow" (not "Following" or "Friends")
                    if text.lower() == "follow":
                        btn.click()
                        return True
            except Exception:
                continue
        return False

    def _go_to_next_video(self, page):
        """Navigates to the next video via keyboard ArrowDown or next button."""
        print("[Nav] Moving to next video...")
        try:
            # First try down arrow button if present in modal
            arrow_btn = page.locator('[data-e2e="arrow-right"]').first
            if arrow_btn.is_visible(timeout=1000):
                arrow_btn.click()
                return
        except Exception:
            pass

        # Primary method: keyboard navigation
        try:
            page.keyboard.press("ArrowDown")
        except Exception:
            page.mouse.wheel(0, 600)

if __name__ == "__main__":
    cfg = load_config()
    bot = TikTokBot(cfg)
    bot.run()
