"""
sync_engine.py
Responsible for 100% automated synchronization with BetMines.
Uses fast direct JSON API as primary method (1-2s response) and Playwright
headless browser as an automated fallback if needed.
Includes date-aware cache validation so stale matches from previous days
are automatically invalidated and refreshed.
"""

import json
import os
import sqlite3
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CACHE_FILE = DATA_DIR / "fixtures_cache.json"
DB_FILE = DATA_DIR / "betmines.db"

# Max cache lifetime before background auto-refresh (30 minutes)
MAX_CACHE_AGE_SECONDS = 1800

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
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fixtures_home_team ON fixtures(home_team)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fixtures_away_team ON fixtures(away_team)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fixtures_date ON fixtures(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fixtures_status ON fixtures(time_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fixtures_league ON fixtures(league_id)")
    conn.commit()
    conn.close()

init_db()

def get_target_date_str(target_day: str = "today") -> str:
    """Returns the YYYY-MM-DD string for yesterday, today, or tomorrow in UTC."""
    now = datetime.now(timezone.utc)
    if target_day == "yesterday":
        target = now - timedelta(days=1)
    elif target_day == "tomorrow":
        target = now + timedelta(days=1)
    else:
        target = now
    return target.strftime("%Y-%m-%d")

def get_date_range_iso(target_day: str = "today") -> Tuple[str, str]:
    """Calculates ISO from/to query window for BetMines API."""
    target_date = get_target_date_str(target_day)
    from_iso = f"{target_date}T00:00:00Z"
    to_iso = f"{target_date}T23:59:59Z"
    return from_iso, to_iso

def is_cache_valid(target_day: str = "today", max_age_seconds: int = MAX_CACHE_AGE_SECONDS) -> bool:
    """
    Checks if cache exists, is from the correct calendar date (e.g. today's date),
    and was updated within max_age_seconds.
    """
    if not CACHE_FILE.exists():
        return False
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        day_data = data.get(target_day)
        if not day_data or not day_data.get("fixtures"):
            return False

        # Verify that the cache corresponds to the actual current target date (e.g. 2026-10-31 for today)
        expected_date = get_target_date_str(target_day)
        cached_date = day_data.get("target_date")
        if cached_date and cached_date != expected_date:
            print(f"[*] Cache expired for '{target_day}': cached date {cached_date} != expected {expected_date}")
            return False

        # Verify age
        synced_at_str = day_data.get("synced_at")
        if not synced_at_str:
            return False
        
        synced_at = datetime.fromisoformat(synced_at_str)
        if synced_at.tzinfo is None:
            synced_at = synced_at.replace(tzinfo=timezone.utc)
        
        age = (datetime.now(timezone.utc) - synced_at).total_seconds()
        if age > max_age_seconds:
            print(f"[*] Cache for '{target_day}' is {int(age)}s old (max: {max_age_seconds}s). Refreshing...")
            return False

        return True
    except Exception as e:
        print(f"[-] Cache validation check error: {e}")
        return False

def fetch_betmines_direct_api(target_day: str = "today") -> List[Dict[str, Any]]:
    """
    Fast direct JSON API client. Responds in ~1-2 seconds with zero browser overhead.
    """
    from_iso, to_iso = get_date_range_iso(target_day)
    url = f"https://api.betmines.com/betmines/v1/fixtures/web?dateFormat=extended&platform=website&from={from_iso}&to={to_iso}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://betmines.com",
        "Referer": "https://betmines.com/"
    }

    print(f"[*] Direct BetMines API fetch for '{target_day}' ({from_iso} -> {to_iso})...")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as res:
        if res.status == 200:
            data = json.loads(res.read().decode("utf-8"))
            if isinstance(data, list) and len(data) > 0:
                print(f"[+] Successfully fetched {len(data)} fixtures directly from BetMines API.")
                return data
    return []

def fetch_betmines_playwright(target_day: str = "today", timeout_secs: int = 45) -> List[Dict[str, Any]]:
    """
    Fallback headless Playwright scraper when direct API is unreachable or protected.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[-] Playwright not installed for fallback.")
        return []

    day_path_map = {
        "today": "football-predictions-today",
        "tomorrow": "football-predictions-tomorrow",
        "yesterday": "football-predictions-yesterday"
    }
    path = day_path_map.get(target_day, "football-predictions-today")
    target_url = f"https://betmines.com/{path}"

    captured_fixtures = []
    print(f"[*] Fallback: Launching Playwright browser for {target_url} ...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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
                        print(f"[+] Playwright intercepted {len(data)} fixtures.")
                except Exception:
                    pass

        page.on("response", on_response)

        try:
            page.goto(target_url, wait_until="networkidle", timeout=timeout_secs * 1000)
            time.sleep(2)
        except Exception as e:
            print(f"[!] Playwright navigation warning: {e}")

        browser.close()

    return captured_fixtures

def fetch_betmines_fixtures(target_day: str = "today", timeout_secs: int = 60) -> List[Dict[str, Any]]:
    """
    Unified sync engine.
    1. Tries fast direct JSON API.
    2. Falls back to Playwright if needed.
    3. Persists to disk cache with calendar date verification and saves to SQLite.
    """
    captured_fixtures = []

    # Method 1: Fast direct API
    try:
        captured_fixtures = fetch_betmines_direct_api(target_day)
    except Exception as e:
        print(f"[-] Direct API error: {e}. Trying Playwright fallback...")

    # Method 2: Playwright fallback
    if not captured_fixtures:
        try:
            captured_fixtures = fetch_betmines_playwright(target_day, timeout_secs=timeout_secs)
        except Exception as e:
            print(f"[-] Playwright fallback error: {e}")

    # If both failed, return existing cached fixtures as safe fallback
    if not captured_fixtures:
        print("[!] Sync could not retrieve fresh fixtures. Falling back to existing cache if available.")
        return get_raw_cached_data(target_day)

    # Save to disk cache and database
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

    target_date_str = get_target_date_str(target_day)
    existing[target_day] = {
        "target_date": target_date_str,
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "count": len(fixtures),
        "fixtures": fixtures
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f)

def get_raw_cached_data(target_day: str = "today") -> List[Dict[str, Any]]:
    """Reads whatever is currently in the cache file without validation."""
    if not CACHE_FILE.exists():
        return []
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            day_data = data.get(target_day, {})
            return day_data.get("fixtures", [])
    except Exception:
        return []

def get_cached_fixtures(target_day: str = "today", auto_sync_if_stale: bool = True) -> List[Dict[str, Any]]:
    """
    Retrieves fixtures for target day.
    If cache is missing, expired, or belongs to yesterday/previous day,
    it automatically triggers an instant sync from BetMines!
    """
    valid = is_cache_valid(target_day)
    if not valid:
        if auto_sync_if_stale:
            print(f"[*] Cache is stale or from a previous day for '{target_day}'. Auto-syncing live fixtures now...")
            try:
                fresh = fetch_betmines_fixtures(target_day)
                if fresh:
                    return fresh
            except Exception as e:
                print(f"[-] Auto-sync failed: {e}")
        
    return get_raw_cached_data(target_day)

def get_sync_info(target_day: str = "today") -> Dict[str, Any]:
    expected_date = get_target_date_str(target_day)
    if not CACHE_FILE.exists():
        return {
            "synced_at": None,
            "target_date": expected_date,
            "count": 0,
            "status": "Never synced",
            "is_stale": True
        }
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            day_data = data.get(target_day, {})
            cached_date = day_data.get("target_date")
            synced_at = day_data.get("synced_at")
            count = day_data.get("count", 0)
            valid = is_cache_valid(target_day)

            return {
                "synced_at": synced_at,
                "target_date": cached_date or expected_date,
                "expected_date": expected_date,
                "count": count,
                "is_stale": not valid,
                "status": "Live & Synced" if valid else ("Outdated Date" if cached_date != expected_date else "Stale (Refreshing)")
            }
    except Exception:
        return {
            "synced_at": None,
            "target_date": expected_date,
            "count": 0,
            "status": "Error reading cache",
            "is_stale": True
        }

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
        target_date_str = get_target_date_str(target_day)
        cursor.execute("INSERT INTO sync_logs (target_date, match_count, status) VALUES (?, ?, ?)", (target_date_str, len(fixtures), "SUCCESS"))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[-] DB Save error: {e}")

if __name__ == "__main__":
    fixtures = fetch_betmines_fixtures("today")
    print(f"Done! Total matches loaded: {len(fixtures)}")
