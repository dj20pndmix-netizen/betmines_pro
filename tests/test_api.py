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

    res_sw = client.get("/sw.js")
    assert res_sw.status_code == 200
    assert "CACHE_NAME" in res_sw.text
