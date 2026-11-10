# Changelog
All notable changes to the BetMines Pro application are documented in this file in adherence with MPADS v1.0 standards.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-11-10

### Added
- **Core Scraping & Synchronization Engine**: Playwright-based headless Chromium request interceptor bypassing Cloudflare bot challenges to ingest live BetMines JSON feeds (`/fixtures/web`).
- **40+ Market Prediction Engine**: Evaluates 1X2, Double Chance, Total Goals (O/U 1.5, 2.5, 3.5, 4.5, 1st & 2nd Half), BTTS (FT, 1st & 2nd Half), Corners, and HT/FT double results.
- **Expected Value ($EV$) Calculator**: Automatically scores betting efficiency against live bookmaker decimal odds ($EV > 0$).
- **1X2 Outright Winner Highlight**: Dedicated 1X2 probability bar (`1`, `X`, `2`) on every match card with explicit favored winner indication.
- **Historical Outcome & Profit Tracking**: Automatic verification of finished matches against final scores with win-rate calculation and simulated flat-stake ROI units.
- **Smart Accumulator Slip Builder**: Generates multi-leg accumulator slips (3, 5, 7, 10 legs) by user-selected risk profile.
- **Progressive Web App (PWA)**: Android home-screen installation support with custom football (soccer ball) SVG/PNG icons, `manifest.json`, and `sw.js` Service Worker.
- **Cloud & Container Infrastructure**: Production-ready `Dockerfile`, `render.yaml`, `Procfile`, and automated Cloudflare HTTPS tunneling launcher (`start_phone.bat`).
- **Comprehensive MPADS Documentation**: Added `docs/ARCHITECTURE.md`, `docs/REQUIREMENTS.md`, `docs/SECURITY.md`, `docs/DATABASE.md`, `docs/TESTING.md`, `docs/DEPLOYMENT.md`, `docs/ENVIRONMENT.md`.
