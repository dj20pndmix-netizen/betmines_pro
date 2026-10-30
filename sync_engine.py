"""
sync_engine.py
Responsible for 100% synchronization with BetMines.
Uses Playwright with automated headless browser and request interception
to bypass Cloudflare and directly extract the rich /fixtures/web API data.
"""

import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CACHE_FILE = DATA_DIR / "fixtures_cache.json"
DB_FILE = DATA_DIR / "betmines.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sync_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_date TEXT,
        match_count INTEGER,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fixtures (
        id INTEGER PRIMARY KEY,
        date TEXT,
        date_time TEXT,
        league_id INTEGER,
        league_name TEXT,
        country TEXT,
        home_team_id INTEGER,
        home_team TEXT,
        away_team_id INTEGER,
        away_team TEXT,
        time_status TEXT,
        local_score INTEGER,
        visitor_score INTEGER,
        raw_json TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

def fetch_betmines_fixtures(target_day: str = "today", timeout_secs: int = 60) -> List[Dict[str, Any]]:
    """
    Launches headless Playwright, navigates to target day's page on betmines.com,
    intercepts the /fixtures/web JSON API response, and returns the parsed list of fixtures.
    """
    from playwright.sync_api import sync_playwright

    day_path_map = {
        "today": "football-predictions-today",
        "tomorrow": "football-predictions-tomorrow",
        "yesterday": "football-predictions-yesterday"
    }
    path = day_path_map.get(target_day, "football-predictions-today")
    target_url = f"https://betmines.com/{path}"

    captured_fixtures = []

    print(f"[*] Starting sync with BetMines: {target_url} ...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()

        def on_response(response):
            nonlocal captured_fixtures
            url = response.url
            if "fixtures/web" in url and response.status == 200:
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        captured_fixtures = data
                        print(f"[+] Successfully intercepted {len(data)} fixtures from: {url}")
                except Exception as e:
                    print(f"[-] Error decoding fixtures JSON: {e}")

        page.on("response", on_response)

        try:
            page.goto(target_url, wait_until="networkidle", timeout=timeout_secs * 1000)
            # Give short buffer for async hydration
            time.sleep(2)
        except Exception as e:
            print(f"[!] Navigation notice: {e}")

        browser.close()

    if not captured_fixtures:
        print("[!] No fixtures intercepted via network. Checking if cached data exists.")
        return get_cached_fixtures(target_day)

    # Save to disk cache
    save_cache(target_day, captured_fixtures)
    save_to_db(target_day, captured_fixtures)

    return captured_fixtures

def save_cache(target_day: str, fixtures: List[Dict[str, Any]]):
    existing = {}
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = {}

    existing[target_day] = {
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "count": len(fixtures),
        "fixtures": fixtures
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f)

def get_cached_fixtures(target_day: str = "today") -> List[Dict[str, Any]]:
    if not CACHE_FILE.exists():
        return []
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            day_data = data.get(target_day, {})
            return day_data.get("fixtures", [])
    except Exception:
        return []

def get_sync_info(target_day: str = "today") -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        return {"synced_at": None, "count": 0, "status": "Never synced"}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            day_data = data.get(target_day, {})
            return {
                "synced_at": day_data.get("synced_at"),
                "count": day_data.get("count", 0),
                "status": "Synced" if day_data.get("count", 0) > 0 else "Empty"
            }
    except Exception:
        return {"synced_at": None, "count": 0, "status": "Error reading cache"}

def save_to_db(target_day: str, fixtures: List[Dict[str, Any]]):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        for f in fixtures:
            f_id = f.get("id")
            if not f_id:
                continue
            country_val = f.get("league", {}).get("country")
            country_str = country_val.get("name") if isinstance(country_val, dict) else str(country_val or "")
            cursor.execute("""
            INSERT OR REPLACE INTO fixtures 
            (id, date, date_time, league_id, league_name, country, home_team_id, home_team, away_team_id, away_team, time_status, local_score, visitor_score, raw_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                f_id,
                f.get("date"),
                f.get("dateTime"),
                f.get("league", {}).get("id"),
                f.get("league", {}).get("name"),
                country_str,
                f.get("localTeam", {}).get("id"),
                f.get("localTeam", {}).get("name"),
                f.get("visitorTeam", {}).get("id"),
                f.get("visitorTeam", {}).get("name"),
                f.get("timeStatus"),
                f.get("localTeamScore"),
                f.get("visitorTeamScore"),
                json.dumps(f)
            ))
        cursor.execute("INSERT INTO sync_logs (target_date, match_count, status) VALUES (?, ?, ?)", (target_day, len(fixtures), "SUCCESS"))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[-] DB Save error: {e}")

if __name__ == "__main__":
    fixtures = fetch_betmines_fixtures("today")
    print(f"Done! Total matches loaded: {len(fixtures)}")
