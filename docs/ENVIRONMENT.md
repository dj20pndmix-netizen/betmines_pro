# Environment & Configuration Specification
**Project:** BetMines Pro Prediction & Synchronization Engine  
**Standard:** Master Professional App Development Standard (MPADS v1.0)  
**Revision:** 1.0.0

---

## 1. Centralized Environment Variables

| Variable Name | Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `PORT` | Integer | `8000` | Port on which the HTTP server listens. |
| `HOST` | String | `0.0.0.0` | Network interface binding. |
| `DATABASE_PATH` | Path | `data/betmines.db` | Local SQLite database file location. |
| `SYNC_INTERVAL_SECONDS` | Integer | `3600` | Autonomous background sync cadence (seconds). |
| `ENVIRONMENT` | String | `production` | Deployment stage (`development` or `production`). |
| `CORS_ORIGINS` | String | `*` | Comma-separated list of allowed CORS domains. |
