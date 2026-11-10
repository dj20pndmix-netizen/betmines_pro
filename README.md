# BetMines Pro - AI Best Prediction Engine & 100% Real-Time Sync

A professional full-stack football betting prediction & analytics application that syncs in real-time with [BetMines](https://betmines.com), evaluates 40+ betting markets, provides Google-verified undefeated team streaks, and algorithmically identifies banker and high-EV value bets.

---

## 🚀 How to Launch the Application

### Option 1: One-Click Startup (Recommended)
Double-click `start.bat` or run in your terminal:
```bash
python run.py
```
*(or `python start_app.py`)*

This starts the backend engine on `http://127.0.0.1:8000` and automatically opens the interactive dashboard in your default browser.

### Option 2: Android & Mobile Installation (PWA)
Double-click `start_phone.bat` or run:
```bash
python run_phone_app.py
```
This launches a secure HTTPS Cloudflare tunnel. Open the generated HTTPS URL on your phone's Chrome browser and tap **"Install App"** to add BetMines Pro directly to your home screen!

---

## ⚡ Key Features

1. **100% Real-time BetMines Sync Engine**:
   - Ultra-fast native API sync (~1.5s) with automated Playwright headless Chromium fallback.
   - Date-aware cache validation ensuring live, fresh fixtures are retrieved upon date change.
   - Auto-syncs **Today**, pre-fetches **Tomorrow**, and records **Yesterday** scores.
   - Stores data in indexed SQLite database (`data/betmines.db`) and local cache (`data/fixtures_cache.json`).

2. **🔥 Unbeaten Streaks (Google Verified)**:
   - Evaluates active undefeated runs across all active fixtures.
   - Cross-verifies active form with direct Google Sports search links.
   - Employs a 12-hour disk cache (`data/google_streaks_cache.json`) to prevent rate limits.

3. **Strict Match Status Partitioning**:
   - Strictly separates **Upcoming Matches**, **Live In-Play**, and **Finished Matches**.
   - Finished matches are never mixed with upcoming predictions.

4. **Intelligent "Best Prediction" Picker**:
   - **Banker Picks**: High-probability predictions ($\ge 80\%$) with secure odds.
   - **Value Edge Bets**: Automatically calculates Expected Value ($EV = (\text{Prob} \times \text{Odds}) - 1$) and highlights bets where the statistical probability beats the bookmaker margin ($EV > 0$).
   - **Golden Daily Selections**: Curated top 10 Bankers, Values, BTTS Specialists, and Goal Machines.

5. **Interactive Accumulator / Parlay Slip Generator**:
   - Select strategy mode (*Safe Bankers*, *Balanced Value*, *Value Bets Only*, *BTTS Combo*, *Over 2.5 Combo*).
   - Select number of legs (3, 5, 7, 10 legs).
   - Generates a customized slip with total odds and estimated winning probability.

6. **Automatic 24-Hour Midnight Rollover**:
   - Background poller checks the date every 30 seconds.
   - Automatically switches datasets to the new day at midnight without manual refreshes.

---

## 📁 Project Structure

* [`run.py`](file:///c:/Users/user/Downloads/betmins/run.py): Universal launch script for BetMines Pro.
* [`start_app.py`](file:///c:/Users/user/Downloads/betmins/start_app.py): App launcher that starts the server and opens your browser.
* [`start.bat`](file:///c:/Users/user/Downloads/betmins/start.bat): Windows batch file for one-click startup.
* [`start_phone.bat`](file:///c:/Users/user/Downloads/betmins/start_phone.bat) / [`run_phone_app.py`](file:///c:/Users/user/Downloads/betmins/run_phone_app.py): Secure HTTPS tunnel launcher for mobile devices.
* [`server.py`](file:///c:/Users/user/Downloads/betmins/server.py): FastAPI backend providing REST endpoints.
* [`sync_engine.py`](file:///c:/Users/user/Downloads/betmins/sync_engine.py): BetMines API synchronization engine.
* [`streaks_engine.py`](file:///c:/Users/user/Downloads/betmins/streaks_engine.py): Undefeated streaks calculator with Google Sports verification.
* [`analyzer.py`](file:///c:/Users/user/Downloads/betmins/analyzer.py): Mathematical evaluation engine for predictions, EV calculations, and ranking.
* [`static/index.html`](file:///c:/Users/user/Downloads/betmins/static/index.html): Responsive dashboard UI (Tailwind CSS, Lucide icons).
* [`tests/`](file:///c:/Users/user/Downloads/betmins/tests): Pytest automated test suite (15/15 passing).
