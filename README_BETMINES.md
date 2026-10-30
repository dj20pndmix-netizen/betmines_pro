# BetMines Pro - AI Best Prediction Engine & 100% Real-Time Sync

A full-stack football betting prediction & analytics application that syncs **100% in real-time** with [BetMines](https://betmines.com), evaluates all 40+ betting markets, and algorithmically chooses the highest-probability and highest-value predictions.

---

## 🚀 How to Launch the Application

Double-click `start.bat` or run in your terminal:

```bash
python start_app.py
```

This starts the backend engine on `http://127.0.0.1:8000` and automatically opens the interactive dashboard in your default browser.

---

## ⚡ Key Features

1. **100% Real-time BetMines Sync Engine**:
   - Uses Playwright headless Chromium with request interception to bypass Cloudflare bot protections.
   - Syncs all 300+ daily fixtures and historical records directly from `https://api.betmines.com/betmines/v1/fixtures/web`.
   - Supports **Today**, **Tomorrow**, and **Yesterday** datasets with one-click live refresh.
   - Stores data in local SQLite database (`data/betmines.db`) and JSON cache (`data/fixtures_cache.json`).

2. **Full Coverage of All 40+ Markets**:
   - **Match Winner (1X2)**: Home (1), Draw (X), Away (2)
   - **Double Chance**: 1X, 12, X2
   - **1st Half 1X2**: Home HT, Draw HT, Away HT
   - **Total Goals (Full Time)**: Over/Under 1.5, 2.5, 3.5, 4.5
   - **1st Half Goals**: Over/Under 0.5, 1.5
   - **2nd Half Goals**: Over/Under 0.5, 1.5
   - **Both Teams To Score (BTTS / GG-NG)**: Full Time (Yes/No), 1st Half (Yes/No), 2nd Half (Yes/No)
   - **Total Corners**: Over/Under 7.5, 8.5, 9.5, 10.5
   - **Half-Time / Full-Time**: HT 1 - FT 1, HT 2 - FT 2
   - **Team Streaks & Defense**: Clean Sheets, Goals Scored, Goals Conceded

3. **Intelligent "Best Prediction" Picker**:
   - **Banker Picks**: High-probability predictions ($\ge 80\%$) with secure odds.
   - **Value Edge Bets**: Automatically calculates Expected Value ($EV = (\text{Prob} \times \text{Odds}) - 1$) and highlights bets where the statistical probability beats the bookmaker margin ($EV > 0$).
   - **Golden Daily Selections**: Curated top 10 Bankers, Values, BTTS Specialists, and Goal Machines.

4. **Interactive Accumulator / Parlay Slip Generator**:
   - Select strategy mode (*Safe Bankers*, *Balanced Value*, *Value Bets Only*, *BTTS Combo*, *Over 2.5 Combo*).
   - Select number of legs (3, 5, 7, 10 legs).
   - Generates a customized slip with total odds and estimated winning probability.

5. **Full Odds & Markets Modal**:
   - Click "All Odds" on any match to inspect the complete probability meter and bookmaker decimal odds for every market.

6. **Export**:
   - One-click export of predictions to CSV.

---

## 📁 Project Structure

* [`start_app.py`](file:///c:/Users/user/Downloads/betmins/start_app.py): App launcher that starts the server and opens your browser.
* [`start.bat`](file:///c:/Users/user/Downloads/betmins/start.bat): Windows batch file for one-click startup.
* [`server.py`](file:///c:/Users/user/Downloads/betmins/server.py): FastAPI backend providing REST endpoints.
* [`sync_engine.py`](file:///c:/Users/user/Downloads/betmins/sync_engine.py): Playwright-based scraper and BetMines API synchronization engine.
* [`analyzer.py`](file:///c:/Users/user/Downloads/betmins/analyzer.py): Mathematical evaluation engine for predictions, EV calculations, and ranking.
* [`static/index.html`](file:///c:/Users/user/Downloads/betmins/static/index.html): Responsive dashboard UI (Tailwind CSS, Lucide icons).
* `data/`: SQLite database and cached fixtures.
