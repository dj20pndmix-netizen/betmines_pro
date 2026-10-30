"""
TikTok Automation Bot - Interactive Console Launcher
"""

import os
import sys
import json
import subprocess

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_profile")

def read_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def menu():
    while True:
        cfg = read_config()
        has_profile = os.path.exists(PROFILE_DIR)

        print("\n" + "=" * 55)
        print("          TIKTOK AUTO-LIKE & AUTO-FOLLOW BOT")
        print("=" * 55)
        print(f" Session Status:      {'[READY] Logged-in profile found' if has_profile else '[NOT LOGGED IN] Please run Login first'}")
        print(f" Current Mode:        {cfg.get('mode', 'foryou')} (Hashtag: #{cfg.get('target_hashtag', 'fyp')})")
        print(f" Limits:              {cfg.get('max_likes')} Likes | {cfg.get('max_follows')} Follows")
        print(f" Probabilities:       Like {int(cfg.get('like_probability', 0.75)*100)}% | Follow {int(cfg.get('follow_probability', 0.3)*100)}%")
        print("-" * 55)
        print(" 1. [First Step] Login / Manage TikTok Account")
        print(" 2. Start Bot on 'For You' Feed")
        print(" 3. Start Bot on a specific Hashtag")
        print(" 4. Adjust Settings (Limits, Probabilities, Delays)")
        print(" 5. Exit")
        print("=" * 55)

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            print("\nLaunching Login Helper...")
            subprocess.run([sys.executable, "login_helper.py"])

        elif choice == "2":
            cfg["mode"] = "foryou"
            save_config(cfg)
            print("\nStarting bot on 'For You' feed...")
            subprocess.run([sys.executable, "tiktok_bot.py"])

        elif choice == "3":
            hashtag = input("\nEnter hashtag (without #): ").strip().replace("#", "")
            if hashtag:
                cfg["mode"] = "hashtag"
                cfg["target_hashtag"] = hashtag
                save_config(cfg)
            print(f"\nStarting bot on #{cfg['target_hashtag']}...")
            subprocess.run([sys.executable, "tiktok_bot.py"])

        elif choice == "4":
            print("\n--- Adjust Bot Settings ---")
            try:
                nl = input(f"Max Likes per run [current: {cfg.get('max_likes')}]: ").strip()
                if nl: cfg["max_likes"] = int(nl)

                nf = input(f"Max Follows per run [current: {cfg.get('max_follows')}]: ").strip()
                if nf: cfg["max_follows"] = int(nf)

                lp = input(f"Like Probability % (1-100) [current: {int(cfg.get('like_probability')*100)}%]: ").strip()
                if lp: cfg["like_probability"] = round(float(lp) / 100.0, 2)

                fp = input(f"Follow Probability % (1-100) [current: {int(cfg.get('follow_probability')*100)}%]: ").strip()
                if fp: cfg["follow_probability"] = round(float(fp) / 100.0, 2)

                mw = input(f"Min watch time (sec) [current: {cfg.get('min_watch_seconds')}]: ").strip()
                if mw: cfg["min_watch_seconds"] = int(mw)

                mxw = input(f"Max watch time (sec) [current: {cfg.get('max_watch_seconds')}]: ").strip()
                if mxw: cfg["max_watch_seconds"] = int(mxw)

                save_config(cfg)
                print("[SUCCESS] Settings updated!")
            except Exception as e:
                print(f"[ERROR] Invalid input: {e}")

        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please enter 1 to 5.")

if __name__ == "__main__":
    menu()
