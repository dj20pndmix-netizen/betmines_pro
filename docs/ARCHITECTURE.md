# Software Architecture Document (SAD)
**Project:** BetMines Pro Prediction & Synchronization Engine  
**Standard:** Master Professional App Development Standard (MPADS v1.0)  
**Classification:** Universal Software Engineering Standard  
**Revision:** 1.0.0

---

## 1. Architectural Style & Overview

BetMines Pro is engineered as a **Modular Layered Monolith** optimized for reliability, data integrity, low latency, and zero-maintenance continuous operation across Cloud and Edge environments (Android PWA, Desktop, Web).

```
+-------------------------------------------------------------------------+
|                  Client Layer (PWA / Mobile / Desktop)                  |
|  - Standalone PWA (manifest.json, sw.js ServiceWorker offline cache)    |
|  - Responsive Tailwind CSS Engine & Interactive Lucide Iconography      |
|  - Real-time 1X2 Probabilities Bar, All-Odds Modal & Accumulator Tool   |
+-------------------------------------------------------------------------+
                                    |  HTTPS / JSON API
                                    v
+-------------------------------------------------------------------------+
|                    API & Presentation Layer (FastAPI)                   |
|  - Strict CORS Policy & Request Validation                              |
|  - RESTful Endpoints (/api/predictions, /api/golden-picks, /api/history)|
|  - Background Async Tasks & Export Service (CSV / JSON)                 |
+-------------------------------------------------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+-----------------------+                       +-----------------------+
|  Mathematical & AI    |                       |  Data Ingestion &     |
|  Prediction Engine    |                       |  Sync Service         |
|  (analyzer.py)        |                       |  (sync_engine.py)     |
| - Expected Value (EV) |                       | - Headless Chromium   |
| - 40+ Market Scorer   |                       |   Playwright Intercept|
| - 1X2 Consensus Logic |                       | - Automated Scheduler |
| - Historical Verifier |                       | - Resilient Retry &   |
+-----------------------+                       |   Cloudflare Bypass   |
            |                                   +-----------------------+
            |                                               |
            +-----------------------+-----------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                    Data Layer (SQLite & JSON Cache)                     |
|  - Write-Ahead Logging (WAL) Mode for High Concurrency                  |
|  - Indexed Schema (fixtures, sync_logs, schema_migrations)             |
|  - Atomic Upserts with Referential & Data Type Integrity                |
+-------------------------------------------------------------------------+
```

---

## 2. Separation of Concerns & Modules

1. **Presentation / API (`server.py`)**:
   - Exposes validated REST endpoints.
   - Enforces authentication / CORS boundaries.
   - Coordinates background workers and serves the PWA application shell.

2. **Analytical Engine (`analyzer.py`)**:
   - Pure, deterministic mathematical evaluation.
   - Evaluates:
     - 1X2 Match Winner & Double Chance.
     - 1st Half / 2nd Half Outright & Goal Totals.
     - Total Goals Over/Under (1.5, 2.5, 3.5, 4.5).
     - Both Teams to Score (BTTS Full Time, HT, 2H).
     - Total Corners (Over/Under 7.5, 8.5, 9.5, 10.5).
     - Half-Time / Full-Time Double Results.
   - Calculates mathematical Expected Value ($EV = (\text{Prob} \times \text{Odds}) - 1$).
   - Verifies finished game outcomes against real final scores.

3. **Ingestion & Synchronization Engine (`sync_engine.py`)**:
   - Responsible for robust network communication and bypassing anti-bot challenges.
   - Intercepts live JSON payloads (`/fixtures/web`).
   - Persists raw and normalized data atomically.

4. **Persistence Layer (`data/betmines.db`)**:
   - Local relational database with indexed queries for date, status, and league.
   - Preserves historical records for multi-year accuracy auditing.

---

## 3. Component Boundaries & Dependencies

- **Zero Coupling between Analysis and Ingestion**: The analytical engine does not perform network operations. It receives structured fixture models, ensuring testability.
- **Fail-Safe Caching**: If live network ingestion encounters transient network partitions, the analytical engine immediately serves from the local SQLite persistent cache without service interruption.

---

## 4. Concurrency & Thread Safety

- SQLite access is guarded with standard connection pooling and atomic transactions.
- Ingestion execution is protected by an in-memory re-entrant lock (`SYNC_LOCK`), preventing race conditions and duplicate concurrent scraping jobs.
