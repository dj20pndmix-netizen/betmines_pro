"""
server.py
FastAPI Web Server for BetMines Sync & Best Prediction Engine.
Provides clean REST APIs and serves a real-time responsive Dashboard UI.
Automated date-aware synchronization ensures today's matches are always shown.
"""

import csv
import io
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Query, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sync_engine import (
    fetch_betmines_fixtures,
    get_cached_fixtures,
    get_sync_info,
    get_target_date_str,
    is_cache_valid
)
from analyzer import (
    analyze_fixture,
    get_ranked_predictions,
    get_golden_picks,
    get_history_performance
)
from streaks_engine import identify_unbeaten_streaks

app = FastAPI(
    title="BetMines Pro Sync & Prediction Engine",
    description="100% Real-time synchronization with BetMines & AI Best Prediction Engine",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global sync state
SYNC_LOCK = threading.Lock()
IS_SYNCING = False
LAST_SYNC_ERROR: Optional[str] = None

def do_background_sync(target_day: str):
    global IS_SYNCING, LAST_SYNC_ERROR
    with SYNC_LOCK:
        IS_SYNCING = True
        LAST_SYNC_ERROR = None
        try:
            fetch_betmines_fixtures(target_day)
        except Exception as e:
            LAST_SYNC_ERROR = str(e)
            print(f"[-] Background sync error for '{target_day}': {e}")
        finally:
            IS_SYNCING = False

def autonomous_sync_loop():
    """Independent background worker that keeps BetMines live fixtures and scores automated."""
    print("[*] Autonomous sync worker started. Checking fixtures immediately...")
    while True:
        try:
            # 1. Sync today's fixtures and live scores regularly
            if not is_cache_valid("today", max_age_seconds=900):
                print("[*] Autonomous worker: Syncing today's fixtures...")
                do_background_sync("today")

            # 2. Pre-fetch tomorrow's fixtures ahead of time
            if not is_cache_valid("tomorrow", max_age_seconds=3600):
                print("[*] Autonomous worker: Pre-fetching tomorrow's fixtures...")
                do_background_sync("tomorrow")
            
            # 3. Sync yesterday's matches for final scores and verifications
            if not is_cache_valid("yesterday", max_age_seconds=3600):
                print("[*] Autonomous worker: Syncing yesterday's fixtures...")
                do_background_sync("yesterday")

        except Exception as e:
            print(f"[-] Autonomous sync error: {e}")

        # Check every 15 minutes
        time.sleep(900)

# Launch independent background sync thread on startup
threading.Thread(target=autonomous_sync_loop, daemon=True).start()

def format_display_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%A, %d %b %Y")
    except Exception:
        return date_str

@app.get("/api/status")
def get_status(day: str = Query("today")):
    info = get_sync_info(day)
    target_date = info["target_date"]
    return {
        "status": "Syncing..." if IS_SYNCING else info["status"],
        "is_syncing": IS_SYNCING,
        "synced_at": info["synced_at"],
        "target_date": target_date,
        "display_date": format_display_date(target_date),
        "count": info["count"],
        "is_stale": info.get("is_stale", False),
        "last_error": LAST_SYNC_ERROR,
        "current_time": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/sync")
def trigger_sync(background_tasks: BackgroundTasks, day: str = Query("today")):
    global IS_SYNCING
    if IS_SYNCING:
        return {"success": False, "message": "A sync is already in progress. Please wait."}
    
    background_tasks.add_task(do_background_sync, day)
    return {"success": True, "message": f"Sync with BetMines for '{day}' has been initiated."}

@app.get("/api/unbeaten-streaks")
def get_unbeaten_streaks_api(day: str = Query("today"), limit: int = Query(30)):
    fixtures = get_cached_fixtures(day, auto_sync_if_stale=True)
    target_date = get_target_date_str(day)
    streaks = identify_unbeaten_streaks(fixtures, max_results=limit)
    return {
        "total": len(streaks),
        "target_date": target_date,
        "display_date": format_display_date(target_date),
        "streaks": streaks
    }

@app.get("/api/golden-picks")
def golden_picks(day: str = Query("today")):
    fixtures = get_cached_fixtures(day, auto_sync_if_stale=True)
    if not fixtures:
        return {"winners_1x2": [], "bankers": [], "values": [], "btts": [], "goals": [], "unbeaten": []}
    picks = get_golden_picks(fixtures)
    streaks = identify_unbeaten_streaks(fixtures, max_results=12)
    picks["unbeaten"] = streaks
    return picks

@app.get("/api/history")
def history_performance(day: str = Query("yesterday")):
    fixtures = get_cached_fixtures(day, auto_sync_if_stale=True)
    if not fixtures:
        # Fallback to query all fixtures from SQLite database
        import sqlite3
        conn = sqlite3.connect("data/betmines.db")
        cursor = conn.cursor()
        cursor.execute("SELECT raw_json FROM fixtures WHERE local_score IS NOT NULL")
        rows = cursor.fetchall()
        conn.close()
        fixtures = [json.loads(r[0]) for r in rows if r[0]]

    return get_history_performance(fixtures)

@app.get("/api/predictions")
def list_predictions(
    day: str = Query("today"),
    status: str = Query("upcoming"),
    market: str = Query("all"),
    min_prob: float = Query(0.0),
    min_odds: float = Query(0.0),
    value_only: bool = Query(False),
    league: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    fixtures = get_cached_fixtures(day, auto_sync_if_stale=True)
    target_date = get_target_date_str(day)

    # Compute status counts across all fixtures
    finished_statuses = {"FT", "AET", "PEN", "Finished", "After Extra Time", "AWARDED"}
    live_statuses = {"LIVE", "HT", "1H", "2H", "ET", "P"}

    finished_count = sum(
        1 for f in fixtures 
        if f.get("timeStatus") in finished_statuses 
        or (f.get("localTeamScore") is not None and f.get("timeStatus") not in live_statuses)
    )
    live_count = sum(1 for f in fixtures if f.get("timeStatus") in live_statuses)
    upcoming_count = max(len(fixtures) - finished_count - live_count, 0)

    counts = {
        "upcoming": upcoming_count,
        "live": live_count,
        "finished": finished_count,
        "total": len(fixtures)
    }

    if not fixtures:
        return {
            "total": 0,
            "target_date": target_date,
            "display_date": format_display_date(target_date),
            "counts": counts,
            "matches": []
        }

    # Pre-compute unbeaten streaks map to attach Google-verified badges to matches
    streaks = identify_unbeaten_streaks(fixtures, max_results=50)
    streaks_by_fid = {s["fixture_id"]: s for s in streaks}

    if market.lower() == "unbeaten":
        # Format streaks as ranked predictions
        matched_results = []
        for s in streaks:
            fid = s["fixture_id"]
            matched_results.append({
                "id": fid,
                "match": s["match"],
                "league": s["league"],
                "local_team": s["team"] if s["is_home"] else s["opponent"],
                "visitor_team": s["opponent"] if s["is_home"] else s["team"],
                "date_time": s["date_time"],
                "status": s["status"],
                "local_score": s["local_score"],
                "visitor_score": s["visitor_score"],
                "selected_pick": {
                    "code": s["pick_code"],
                    "name": s["recommended_pick"],
                    "category": "Unbeaten Streak",
                    "prob": s["unbeaten_prob"],
                    "odds": s["odds"],
                    "is_value": True,
                    "ev": round(((s["unbeaten_prob"] / 100.0) * s["odds"]) - 1.0, 3)
                },
                "pred_1x2": {
                    "pick": "1" if s["is_home"] else "2",
                    "label": f"{s['team']} ({s['streak_type']})",
                    "prob": s["win_prob"],
                    "odds": s["odds"],
                    "home_prob": s["win_prob"] if s["is_home"] else s["opponent_win_prob"],
                    "draw_prob": s["draw_prob"],
                    "away_prob": s["opponent_win_prob"] if s["is_home"] else s["win_prob"]
                },
                "unbeaten_streak": s
            })

        if search:
            s_q = search.lower()
            matched_results = [r for r in matched_results if s_q in r["match"].lower() or s_q in r["league"].lower()]

        return {
            "total": len(matched_results),
            "target_date": target_date,
            "display_date": format_display_date(target_date),
            "counts": counts,
            "matches": matched_results
        }

    ranked = get_ranked_predictions(
        fixtures=fixtures,
        market_filter=market,
        min_prob=min_prob,
        min_odds=min_odds,
        value_only=value_only,
        league_filter=league,
        status_filter=status
    )

    # Attach unbeaten streak metadata where applicable
    for r in ranked:
        fid = r.get("id")
        if fid in streaks_by_fid:
            r["unbeaten_streak"] = streaks_by_fid[fid]

    if search:
        s = search.lower()
        ranked = [r for r in ranked if s in r["match"].lower() or s in r["league"].lower()]

    return {
        "total": len(ranked),
        "target_date": target_date,
        "display_date": format_display_date(target_date),
        "counts": counts,
        "matches": ranked
    }

@app.get("/api/fixture/{fixture_id}")
def get_fixture_details(fixture_id: int, day: str = Query("today")):
    fixtures = get_cached_fixtures(day, auto_sync_if_stale=True)
    for f in fixtures:
        if f.get("id") == fixture_id:
            return analyze_fixture(f)
    raise HTTPException(status_code=404, detail="Fixture not found")

class SlipRequest(BaseModel):
    day: str = "today"
    legs: int = 5
    mode: str = "bankers"  # bankers, balanced, high_value, btts_only, over25_only
    min_prob: float = 60.0

@app.post("/api/generate-slip")
def generate_slip(req: SlipRequest):
    fixtures = get_cached_fixtures(req.day, auto_sync_if_stale=True)
    if not fixtures:
        return {"legs": [], "total_odds": 1.0, "estimated_prob": 0.0}

    candidates = []
    for f in fixtures:
        a = analyze_fixture(f)
        for m in a["all_markets"]:
            if req.mode == "bankers" and m["prob"] >= 78.0 and (m["odds"] or 0) >= 1.15:
                candidates.append((m["prob"], a, m))
            elif req.mode == "balanced" and 65.0 <= m["prob"] <= 85.0 and (m["odds"] or 0) >= 1.35:
                candidates.append((m["prob"] * (m["odds"] or 1.0), a, m))
            elif req.mode == "high_value" and m.get("is_value") and (m["odds"] or 0) >= 1.60:
                candidates.append(((m.get("ev") or 0) * 100, a, m))
            elif req.mode == "btts_only" and m["category"] == "BTTS" and m["prob"] >= req.min_prob:
                candidates.append((m["prob"], a, m))
            elif req.mode == "over25_only" and m["code"] == "O25" and m["prob"] >= req.min_prob:
                candidates.append((m["prob"], a, m))

    # Sort and pick unique matches
    candidates.sort(key=lambda x: x[0], reverse=True)
    seen_matches = set()
    selected = []
    total_odds = 1.0
    accumulated_prob = 1.0

    for score, fixture_analysis, market in candidates:
        m_id = fixture_analysis["id"]
        if m_id in seen_matches:
            continue
        seen_matches.add(m_id)
        selected.append({
            "fixture_id": m_id,
            "match": fixture_analysis["match"],
            "league": fixture_analysis["league"],
            "date_time": fixture_analysis["date_time"],
            "pick": market["name"],
            "market_code": market["code"],
            "category": market["category"],
            "prob": market["prob"],
            "odds": market["odds"] or 1.20
        })
        total_odds *= (market["odds"] or 1.20)
        accumulated_prob *= (market["prob"] / 100.0)
        if len(selected) >= req.legs:
            break

    return {
        "count": len(selected),
        "total_odds": round(total_odds, 2),
        "estimated_prob_pct": round(accumulated_prob * 100.0, 2),
        "legs": selected
    }

@app.get("/api/export")
def export_csv(
    day: str = Query("today"),
    market: str = Query("all"),
    min_prob: float = Query(0.0)
):
    fixtures = get_cached_fixtures(day, auto_sync_if_stale=True)
    ranked = get_ranked_predictions(fixtures, market_filter=market, min_prob=min_prob)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Match", "League", "Date/Time", "Top Pick", "Category", "Probability (%)", "Odds", "Is Value Bet"])

    for r in ranked:
        pick = r["selected_pick"]
        writer.writerow([
            r["match"],
            r["league"],
            r["date_time"],
            pick["name"],
            pick["category"],
            pick["prob"],
            pick["odds"] or "",
            "YES" if pick.get("is_value") else "NO"
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=betmines_{day}_predictions.csv"}
    )

@app.get("/manifest.json")
def get_manifest():
    manifest_path = static_dir / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return JSONResponse(content=json.load(f))
    return JSONResponse(content={})

@app.get("/sw.js")
def get_service_worker():
    sw_path = static_dir / "sw.js"
    if sw_path.exists():
        with open(sw_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), media_type="application/javascript")
    return HTMLResponse(content="", media_type="application/javascript")

# Static files / UI
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def index_page():
    index_file = static_dir / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h2>BetMines Pro Dashboard - Loading...</h2>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
