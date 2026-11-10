import sqlite3
from sync_engine import DB_FILE, init_db, save_to_db

def test_database_schema_and_indexes():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Verify tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cursor.fetchall()}
    assert "fixtures" in tables
    assert "sync_logs" in tables

    # Verify indexes exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = {r[0] for r in cursor.fetchall()}
    assert "idx_fixtures_date" in indexes
    assert "idx_fixtures_status" in indexes
    assert "idx_fixtures_league" in indexes

    conn.close()

def test_fixture_upsert_idempotency():
    init_db()
    test_fixture = {
        "id": 999999,
        "date": "2026-11-10",
        "dateTime": "2026-11-10T20:00:00Z",
        "league": {"id": 8, "name": "Premier League", "country": "England"},
        "localTeam": {"id": 1, "name": "Arsenal"},
        "visitorTeam": {"id": 2, "name": "Chelsea"},
        "timeStatus": "FT",
        "localTeamScore": 2,
        "visitorTeamScore": 1
    }

    # First insert
    save_to_db("today", [test_fixture])

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT local_score, visitor_score FROM fixtures WHERE id=999999")
    row = c.fetchone()
    assert row == (2, 1)

    # Second upsert with updated score
    test_fixture["localTeamScore"] = 3
    save_to_db("today", [test_fixture])

    c.execute("SELECT COUNT(*) FROM fixtures WHERE id=999999")
    count = c.fetchone()[0]
    assert count == 1  # No duplicate rows created

    c.execute("SELECT local_score FROM fixtures WHERE id=999999")
    updated_score = c.fetchone()[0]
    assert updated_score == 3  # Updated atomically

    # Cleanup test row
    c.execute("DELETE FROM fixtures WHERE id=999999")
    conn.commit()
    conn.close()
