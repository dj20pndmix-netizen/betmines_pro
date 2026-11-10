# Quality Assurance & Testing Standard
**Project:** BetMines Pro Prediction & Synchronization Engine  
**Standard:** Master Professional App Development Standard (MPADS v1.0)  
**Revision:** 1.0.0

---

## 1. Testing Strategy

In compliance with MPADS Section 13, all critical computational, data ingestion, and API workflows are guarded with automated test suites:

1. **Unit Testing (`tests/test_analyzer.py`)**:
   - Mathematical Expected Value calculation accuracy ($EV$).
   - 1X2 determination, probabilities mapping, and double-chance logic.
   - Goals markets (O/U 1.5, 2.5, 3.5, 1st Half, 2nd Half).
   - BTTS Full Time & Half Time evaluation.
   - Finished game outcome verification (WON vs. LOST vs. PENDING).

2. **API & Integration Testing (`tests/test_api.py`)**:
   - HTTP response status code contracts.
   - Endpoint schema integrity (`/api/status`, `/api/predictions`, `/api/golden-picks`, `/api/history`, `/api/generate-slip`).
   - PWA manifest and Service Worker header and content checks.

3. **Database Integrity Testing (`tests/test_database.py`)**:
   - SQLite table creation, constraints, index presence, and upsert idempotency.

---

## 2. Test Execution Command

Run the complete test suite using `pytest`:

```bash
python -m pytest tests/ -v
```
