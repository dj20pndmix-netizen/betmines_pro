from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_api_status():
    response = client.get("/api/status?day=today")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "count" in data
    assert "is_syncing" in data

def test_api_predictions():
    response = client.get("/api/predictions?day=today&market=all")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "matches" in data
    assert isinstance(data["matches"], list)

def test_api_golden_picks():
    response = client.get("/api/golden-picks?day=today")
    assert response.status_code == 200
    data = response.json()
    assert "winners_1x2" in data
    assert "bankers" in data
    assert "values" in data
    assert "btts" in data
    assert "goals" in data

def test_api_history():
    response = client.get("/api/history?day=yesterday")
    assert response.status_code == 200
    data = response.json()
    assert "total_finished" in data
    assert "one_x_two_win_rate" in data
    assert "history" in data

def test_api_generate_slip():
    payload = {
        "day": "today",
        "legs": 3,
        "mode": "bankers",
        "min_prob": 60.0
    }
    response = client.post("/api/generate-slip", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "total_odds" in data
    assert "legs" in data

def test_pwa_manifest_and_sw():
    res_manifest = client.get("/manifest.json")
    assert res_manifest.status_code == 200
    manifest = res_manifest.json()
    assert manifest["name"] == "BetMines Pro - AI Best Prediction Engine"
    assert manifest["display"] == "standalone"

def test_api_unbeaten_streaks():
    response = client.get("/api/unbeaten-streaks?day=today")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "streaks" in data
    assert "display_date" in data
    if data["streaks"]:
        first = data["streaks"][0]
        assert "team" in first
        assert "streak_count" in first
        assert "google_verified" in first
        assert "google_search_url" in first

def test_api_status_separation():
    # Test upcoming matches
    res_up = client.get("/api/predictions?day=today&status=upcoming")
    assert res_up.status_code == 200
    data_up = res_up.json()
    assert "counts" in data_up
    assert "upcoming" in data_up["counts"]
    # Check that no completed match is in upcoming
    for m in data_up["matches"]:
        is_finished = m["status"] in ["FT", "Finished", "AWARDED"] or (
            m.get("local_score") is not None and m.get("visitor_score") is not None and m["status"] not in ["LIVE", "HT"]
        )
        assert not is_finished, f"Finished match {m['match']} found in upcoming feed"

    # Test finished matches
    res_fin = client.get("/api/predictions?day=today&status=finished")
    assert res_fin.status_code == 200
    data_fin = res_fin.json()
    assert "total" in data_fin
    for m in data_fin["matches"]:
        is_finished = m["status"] in ["FT", "Finished", "AWARDED"] or (
            m.get("local_score") is not None and m.get("visitor_score") is not None and m["status"] not in ["LIVE", "HT"]
        )
        assert is_finished, f"Non-finished match {m['match']} found in finished feed"


    res_sw = client.get("/sw.js")
    assert res_sw.status_code == 200
    assert "CACHE_NAME" in res_sw.text
