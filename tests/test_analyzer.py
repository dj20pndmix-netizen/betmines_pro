import pytest
from analyzer import safe_float, calc_ev, evaluate_bet_outcome, analyze_fixture, get_golden_picks

def test_safe_float():
    assert safe_float("1.85") == 1.85
    assert safe_float(2.5) == 2.5
    assert safe_float(None) is None
    assert safe_float("") is None
    assert safe_float("invalid") is None
    assert safe_float(-1.0) is None

def test_calc_ev():
    # 70% probability at 1.50 odds -> (0.70 * 1.50) - 1 = 1.05 - 1 = +0.05 (+5% edge)
    ev = calc_ev(70.0, 1.50)
    assert ev == 0.05
    # Negative EV
    ev_neg = calc_ev(40.0, 2.00)
    assert ev_neg == -0.20
    # None cases
    assert calc_ev(0.0, 1.50) is None
    assert calc_ev(50.0, None) is None

def test_evaluate_bet_outcome_1x2():
    # Home Win: 2 - 1
    assert evaluate_bet_outcome("1", 2, 1, "FT") == "WON"
    assert evaluate_bet_outcome("X", 2, 1, "FT") == "LOST"
    assert evaluate_bet_outcome("2", 2, 1, "FT") == "LOST"
    assert evaluate_bet_outcome("1X", 2, 1, "FT") == "WON"
    assert evaluate_bet_outcome("12", 2, 1, "FT") == "WON"
    assert evaluate_bet_outcome("X2", 2, 1, "FT") == "LOST"

    # Draw: 1 - 1
    assert evaluate_bet_outcome("X", 1, 1, "FT") == "WON"
    assert evaluate_bet_outcome("1X", 1, 1, "FT") == "WON"
    assert evaluate_bet_outcome("X2", 1, 1, "FT") == "WON"
    assert evaluate_bet_outcome("12", 1, 1, "FT") == "LOST"

    # Pending match
    assert evaluate_bet_outcome("1", None, None, "NS") == "PENDING"

def test_evaluate_bet_outcome_goals_and_btts():
    # Match: 3 - 1 (Total 4 goals)
    assert evaluate_bet_outcome("O15", 3, 1, "FT") == "WON"
    assert evaluate_bet_outcome("O25", 3, 1, "FT") == "WON"
    assert evaluate_bet_outcome("O35", 3, 1, "FT") == "WON"
    assert evaluate_bet_outcome("U25", 3, 1, "FT") == "LOST"
    assert evaluate_bet_outcome("BTTS_Y", 3, 1, "FT") == "WON"
    assert evaluate_bet_outcome("BTTS_N", 3, 1, "FT") == "LOST"

    # Clean sheet match: 2 - 0
    assert evaluate_bet_outcome("BTTS_Y", 2, 0, "FT") == "LOST"
    assert evaluate_bet_outcome("BTTS_N", 2, 0, "FT") == "WON"

def test_analyze_fixture_structure():
    mock_fixture = {
        "id": 1001,
        "localTeam": {"id": 10, "name": "Team Alpha"},
        "visitorTeam": {"id": 20, "name": "Team Beta"},
        "league": {"id": 1, "name": "Champions League", "country": "Europe"},
        "dateTime": "2026-11-10T19:00:00Z",
        "timeStatus": "FT",
        "localTeamScore": 3,
        "visitorTeamScore": 1,
        "prediction": "1",
        "bestOddProbability": 75,
        "predictionOddValue": 1.45,
        "probability": {
            "home": 75.0,
            "draw": 15.0,
            "away": 10.0,
            "home_draw": 90.0,
            "draw_away": 25.0,
            "home_away": 85.0,
            "over_1_5": 85.0,
            "over_2_5": 65.0,
            "btts": 60.0
        },
        "fixtureOdd": {
            "odd1": 1.45,
            "oddx": 4.20,
            "odd2": 7.50,
            "odd1x": 1.12,
            "oddOver15": 1.25,
            "oddOver25": 1.80,
            "oddGoal": 1.95
        }
    }

    result = analyze_fixture(mock_fixture)
    assert result["id"] == 1001
    assert result["match"] == "Team Alpha vs Team Beta"
    assert "pred_1x2" in result
    assert result["pred_1x2"]["pick"] == "1"
    assert result["pred_1x2"]["outcome"] == "WON"
    assert len(result["all_markets"]) > 5

    # Test golden picks grouping
    golden = get_golden_picks([mock_fixture])
    assert "winners_1x2" in golden
    assert "bankers" in golden
    assert "values" in golden

def test_10m_interval_market():
    mock_fixture = {
        "id": 2002,
        "localTeam": {"id": 11, "name": "Arsenal"},
        "visitorTeam": {"id": 22, "name": "Chelsea"},
        "league": {"id": 2, "name": "Premier League", "country": "England"},
        "dateTime": "2026-11-11T16:00:00Z",
        "timeStatus": "FT",
        "localTeamScore": 0,
        "visitorTeamScore": 0,
        "probability": {
            "home": 55.0,
            "draw": 25.0,
            "away": 20.0,
            "under_0_5_ht": 65.0,
            "over_0_5_ht": 35.0,
            "under_2_5": 58.0
        },
        "fixtureOdd": {
            "odd1": 1.80,
            "oddx": 3.60,
            "odd2": 4.50
        }
    }

    result = analyze_fixture(mock_fixture)
    assert "pred_10m" in result
    p10 = result["pred_10m"]
    assert p10["interval"] == "00:01-09:59"
    assert p10["draw_prob"] >= 75.0
    assert round(p10["home_prob"] + p10["draw_prob"] + p10["away_prob"], 1) == 100.0
    assert p10["outcome"] == "WON"  # 0-0 FT settles 10M_X as WON

    # Check 10M markets are in all_markets
    market_codes = {m["code"] for m in result["all_markets"]}
    assert "10M_1" in market_codes
    assert "10M_X" in market_codes
    assert "10M_2" in market_codes

    # Check filtering by 10min
    from analyzer import get_ranked_predictions
    ranked_10m = get_ranked_predictions([mock_fixture], market_filter="10min", status_filter="finished")
    assert len(ranked_10m) == 1
    assert ranked_10m[0]["selected_pick"]["code"] in ["10M_X", "10M_1", "10M_2"]
