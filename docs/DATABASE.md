# Database Design & Data Integrity Manual
**Project:** BetMines Pro Prediction & Synchronization Engine  
**Standard:** Master Professional App Development Standard (MPADS v1.0)  
**Revision:** 1.0.0

---

## 1. Relational Schema Architecture (SQLite)

The persistence layer uses a normalized relational architecture with high-speed indexes located at `data/betmines.db`.

```
+-----------------------------------------------------------+
|                        FIXTURES                           |
+-----------------------------------------------------------+
| id (INTEGER PRIMARY KEY)                                  |
| date (TEXT)                                               |
| date_time (TEXT)                                          |
| league_id (INTEGER)                                       |
| league_name (TEXT)                                        |
| country (TEXT)                                            |
| home_team_id (INTEGER)                                    |
| home_team (TEXT)                                          |
| away_team_id (INTEGER)                                    |
| away_team (TEXT)                                          |
| time_status (TEXT)                                        |
| local_score (INTEGER, NULLABLE)                           |
| visitor_score (INTEGER, NULLABLE)                         |
| raw_json (TEXT - Full Ingested Payload)                   |
| updated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)          |
+-----------------------------------------------------------+
         ^
         |
+-----------------------------------------------------------+
|                       SYNC_LOGS                           |
+-----------------------------------------------------------+
| id (INTEGER PRIMARY KEY AUTOINCREMENT)                    |
| target_date (TEXT)                                        |
| match_count (INTEGER)                                     |
| synced_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)           |
| status (TEXT)                                             |
+-----------------------------------------------------------+
```

---

## 2. Performance Indexes

To guarantee instant filtering and query responses (<10ms) across thousands of records:

1. `idx_fixtures_date` ON `fixtures(date)`: Accelerates day-based partitioning.
2. `idx_fixtures_status` ON `fixtures(time_status)`: Accelerates live vs. finished match partitioning.
3. `idx_fixtures_league` ON `fixtures(league_id)`: Speeds up tournament-level aggregations.

---

## 3. Data Integrity & Concurrency Controls

- **Atomic Upserts**: `INSERT OR REPLACE INTO fixtures` guarantees that fixture updates (such as in-play scores or final outcomes) update existing rows without duplicate primary keys.
- **Transaction Safety**: All batch operations execute within explicit transaction contexts (`conn.commit()`).
- **Data Validation**: Score attributes are converted to nullable integers; nested dictionaries are sanitized before execution.

---

## 4. Backup & Restoration Procedures

### Backup Execution
```bash
# Atomic SQLite online backup
sqlite3 data/betmines.db ".backup 'data/betmines_backup.db'"
```

### Restoration Execution
```bash
cp data/betmines_backup.db data/betmines.db
```
