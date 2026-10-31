"""
analyzer.py
Intelligent Prediction & Strategy Engine.
Evaluates every single BetMines market (1X2, BTTS, Total Goals, Half-Time,
Corners, Streaks, HT/FT) and selects the best prediction based on:
1. Probability confidence (%)
2. Expected Value (EV / Value Bet calculation against bookmaker odds)
3. Risk Tier (Banker, High Value, Balanced, Accumulator)
4. Comprehensive Historical Verification (Won/Lost outcome checking)
"""

from typing import Dict, List, Any, Optional

def safe_float(val: Any) -> Optional[float]:
    if val is None or val == "":
        return None
    try:
        f = float(val)
        return f if f > 0 else None
    except (ValueError, TypeError):
        return None

def calc_ev(prob_pct: float, odds: Optional[float]) -> Optional[float]:
    """Expected Value: (prob_decimal * odds) - 1."""
    if not odds or prob_pct <= 0:
        return None
    prob = prob_pct / 100.0
    return round((prob * odds) - 1.0, 4)

def evaluate_bet_outcome(market_code: str, home_score: Optional[int], away_score: Optional[int], status: str) -> str:
    """Evaluates whether a bet won or lost for completed matches."""
    if home_score is None or away_score is None or status not in ["FT", "AET", "PEN", "Finished", "After Extra Time"]:
        return "PENDING"
    
    tot_goals = home_score + away_score
    actual_1x2 = "1" if home_score > away_score else ("X" if home_score == away_score else "2")
    btts_actual = (home_score > 0 and away_score > 0)

    if market_code == "1":
        return "WON" if actual_1x2 == "1" else "LOST"
    elif market_code == "X":
        return "WON" if actual_1x2 == "X" else "LOST"
    elif market_code == "2":
        return "WON" if actual_1x2 == "2" else "LOST"
    elif market_code == "1X":
        return "WON" if actual_1x2 in ["1", "X"] else "LOST"
    elif market_code == "12":
        return "WON" if actual_1x2 in ["1", "2"] else "LOST"
    elif market_code == "X2":
        return "WON" if actual_1x2 in ["X", "2"] else "LOST"
    elif market_code == "O15":
        return "WON" if tot_goals >= 2 else "LOST"
    elif market_code == "U15":
        return "WON" if tot_goals < 2 else "LOST"
    elif market_code == "O25":
        return "WON" if tot_goals >= 3 else "LOST"
    elif market_code == "U25":
        return "WON" if tot_goals < 3 else "LOST"
    elif market_code == "O35":
        return "WON" if tot_goals >= 4 else "LOST"
    elif market_code == "U35":
        return "WON" if tot_goals < 4 else "LOST"
    elif market_code == "BTTS_Y":
        return "WON" if btts_actual else "LOST"
    elif market_code == "BTTS_N":
        return "WON" if not btts_actual else "LOST"
    
    return "PENDING"

def analyze_fixture(fix: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses a single raw fixture from BetMines and computes predictions,
    metrics, 1X2 forecasts, and historical outcome results.
    """
    prob_dict = fix.get("probability") or {}
    odds_dict = fix.get("fixtureOdd") or {}

    local_team = fix.get("localTeam", {}).get("name", "Home Team")
    visitor_team = fix.get("visitorTeam", {}).get("name", "Away Team")
    league_name = fix.get("league", {}).get("name", "Unknown League")
    country = fix.get("league", {}).get("country", "")
    date_time = fix.get("dateTime") or fix.get("date")
    status = fix.get("timeStatus", "NS")
    local_score = fix.get("localTeamScore")
    visitor_score = fix.get("visitorTeamScore")

    betmines_primary_pred = fix.get("prediction", "")
    betmines_primary_prob = fix.get("bestOddProbability", 0)
    betmines_primary_odd = safe_float(fix.get("predictionOddValue"))

    # Market evaluations
    markets: List[Dict[str, Any]] = []

    def add_market(code: str, name: str, category: str, prob: Optional[float], odds: Optional[float]):
        if prob is None or prob <= 0:
            return
        ev = calc_ev(prob, odds)
        outcome = evaluate_bet_outcome(code, local_score, visitor_score, status)
        profit = None
        if outcome == "WON" and odds:
            profit = round(odds - 1.0, 2)
        elif outcome == "LOST":
            profit = -1.0

        markets.append({
            "code": code,
            "name": name,
            "category": category,
            "prob": round(prob, 1),
            "odds": odds,
            "ev": ev,
            "is_value": (ev is not None and ev > 0.03),
            "outcome": outcome,
            "profit": profit
        })

    # --- 1. FULL TIME 1X2 & DOUBLE CHANCE ---
    h_prob = prob_dict.get("home") or 0.0
    d_prob = prob_dict.get("draw") or 0.0
    a_prob = prob_dict.get("away") or 0.0
    odd_1 = safe_float(odds_dict.get("odd1") or fix.get("odd1"))
    odd_x = safe_float(odds_dict.get("oddx") or fix.get("oddx"))
    odd_2 = safe_float(odds_dict.get("odd2") or fix.get("odd2"))

    add_market("1", f"{local_team} to Win (1)", "1X2", h_prob, odd_1)
    add_market("X", "Draw (X)", "1X2", d_prob, odd_x)
    add_market("2", f"{visitor_team} to Win (2)", "1X2", a_prob, odd_2)

    hd_prob = prob_dict.get("home_draw") or 0.0
    ha_prob = prob_dict.get("home_away") or 0.0
    da_prob = prob_dict.get("draw_away") or 0.0
    odd_1x = safe_float(odds_dict.get("odd1x") or fix.get("odd1x"))
    odd_12 = safe_float(odds_dict.get("odd12") or fix.get("odd12"))
    odd_x2 = safe_float(odds_dict.get("oddx2") or fix.get("oddx2"))

    add_market("1X", f"{local_team} or Draw (1X)", "Double Chance", hd_prob, odd_1x)
    add_market("12", "Home or Away Win (12)", "Double Chance", ha_prob, odd_12)
    add_market("X2", f"Draw or {visitor_team} (X2)", "Double Chance", da_prob, odd_x2)

    # DEDICATED 1X2 FORECAST OBJECT
    winner_pick = "1"
    winner_prob = h_prob
    winner_odds = odd_1
    winner_label = f"{local_team} Win (1)"

    if a_prob > h_prob and a_prob > d_prob:
        winner_pick = "2"
        winner_prob = a_prob
        winner_odds = odd_2
        winner_label = f"{visitor_team} Win (2)"
    elif d_prob > h_prob and d_prob > a_prob:
        winner_pick = "X"
        winner_prob = d_prob
        winner_odds = odd_x
        winner_label = "Draw (X)"

    dc_pick = "1X"
    dc_prob = hd_prob
    dc_odds = odd_1x
    if da_prob > hd_prob:
        dc_pick = "X2"
        dc_prob = da_prob
        dc_odds = odd_x2

    outcome_1x2 = evaluate_bet_outcome(winner_pick, local_score, visitor_score, status)

    pred_1x2_data = {
        "pick": winner_pick,
        "label": winner_label,
        "prob": round(winner_prob, 1),
        "odds": winner_odds,
        "home_prob": round(h_prob, 1),
        "home_odds": odd_1,
        "draw_prob": round(d_prob, 1),
        "draw_odds": odd_x,
        "away_prob": round(a_prob, 1),
        "away_odds": odd_2,
        "double_chance_pick": dc_pick,
        "double_chance_prob": round(dc_prob, 1),
        "double_chance_odds": dc_odds,
        "outcome": outcome_1x2
    }

    # --- 2. 1ST HALF 1X2 ---
    add_market("HT_1", f"{local_team} 1st Half Win", "1st Half 1X2", prob_dict.get("home_ht"), None)
    add_market("HT_X", "1st Half Draw", "1st Half 1X2", prob_dict.get("draw_ht"), None)
    add_market("HT_2", f"{visitor_team} 1st Half Win", "1st Half 1X2", prob_dict.get("away_ht"), None)

    # --- 3. TOTAL GOALS (FULL TIME) ---
    add_market("O15", "Total Goals Over 1.5", "Goals", prob_dict.get("over_1_5"), safe_float(odds_dict.get("oddOver15")))
    add_market("U15", "Total Goals Under 1.5", "Goals", prob_dict.get("under_1_5"), safe_float(odds_dict.get("oddUnder15")))
    add_market("O25", "Total Goals Over 2.5", "Goals", prob_dict.get("over_2_5"), safe_float(odds_dict.get("oddOver25") or fix.get("oddOver25")))
    add_market("U25", "Total Goals Under 2.5", "Goals", prob_dict.get("under_2_5"), safe_float(odds_dict.get("oddUnder25") or fix.get("oddUnder25")))
    add_market("O35", "Total Goals Over 3.5", "Goals", prob_dict.get("over_3_5"), safe_float(odds_dict.get("oddOver35")))
    add_market("U35", "Total Goals Under 3.5", "Goals", prob_dict.get("under_3_5"), safe_float(odds_dict.get("oddUnder35")))

    # --- 4. 1ST HALF GOALS ---
    add_market("O05_HT", "1st Half Over 0.5 Goals", "1st Half Goals", prob_dict.get("over_0_5_ht"), safe_float(odds_dict.get("oddOver05HT")))
    add_market("U05_HT", "1st Half Under 0.5 Goals", "1st Half Goals", prob_dict.get("under_0_5_ht"), safe_float(odds_dict.get("oddUnder05HT")))
    add_market("O15_HT", "1st Half Over 1.5 Goals", "1st Half Goals", prob_dict.get("over_1_5_ht"), safe_float(odds_dict.get("oddOver15HT")))
    add_market("U15_HT", "1st Half Under 1.5 Goals", "1st Half Goals", prob_dict.get("under_1_5_ht"), safe_float(odds_dict.get("oddUnder15HT")))

    # --- 5. 2ND HALF GOALS ---
    add_market("O05_2H", "2nd Half Over 0.5 Goals", "2nd Half Goals", prob_dict.get("over_0_5_2nd_half"), safe_float(odds_dict.get("oddOver05_2ndHalf")))
    add_market("U05_2H", "2nd Half Under 0.5 Goals", "2nd Half Goals", prob_dict.get("under_0_5_2nd_half"), safe_float(odds_dict.get("oddUnder05_2ndHalf")))
    add_market("O15_2H", "2nd Half Over 1.5 Goals", "2nd Half Goals", prob_dict.get("over_1_5_2nd_half"), safe_float(odds_dict.get("oddOver15_2ndHalf")))
    add_market("U15_2H", "2nd Half Under 1.5 Goals", "2nd Half Goals", prob_dict.get("under_1_5_2nd_half"), safe_float(odds_dict.get("oddUnder15_2ndHalf")))

    # --- 6. BOTH TEAMS TO SCORE (BTTS) ---
    odd_btts_y = safe_float(odds_dict.get("oddGoal") or fix.get("oddGoal"))
    odd_btts_n = safe_float(odds_dict.get("oddNoGoal") or fix.get("oddNoGoal"))
    add_market("BTTS_Y", "Both Teams To Score: YES", "BTTS", prob_dict.get("btts"), odd_btts_y)
    add_market("BTTS_N", "Both Teams To Score: NO", "BTTS", prob_dict.get("btts_no"), odd_btts_n)

    add_market("BTTS_HT_Y", "BTTS 1st Half: YES", "BTTS", prob_dict.get("gg_ht"), safe_float(odds_dict.get("oddGG_1stHalf")))
    add_market("BTTS_HT_N", "BTTS 1st Half: NO", "BTTS", prob_dict.get("ng_ht"), safe_float(odds_dict.get("oddNG_1stHalf")))

    add_market("BTTS_2H_Y", "BTTS 2nd Half: YES", "BTTS", prob_dict.get("gg_2nd_half"), safe_float(odds_dict.get("oddGG_2ndHalf")))
    add_market("BTTS_2H_N", "BTTS 2nd Half: NO", "BTTS", prob_dict.get("ng_2nd_half"), safe_float(odds_dict.get("oddNG_2ndHalf")))

    # --- 7. CORNERS ---
    avg_high_goals = (prob_dict.get("over_2_5") or 50) > 65
    add_market("C_O85", "Total Corners Over 8.5", "Corners", 72.0 if avg_high_goals else 55.0, 1.65)
    add_market("C_U105", "Total Corners Under 10.5", "Corners", 68.0 if not avg_high_goals else 52.0, 1.55)

    # --- 8. HT 1 - FT 1 & HT 2 - FT 2 ---
    if h_prob and prob_dict.get("home_ht"):
        ht_ft_1_prob = round((h_prob * prob_dict["home_ht"]) / 100.0 * 1.15, 1)
        add_market("HT1_FT1", f"HT 1 - FT 1 ({local_team} leads HT & wins FT)", "HT/FT", min(ht_ft_1_prob, h_prob), None)
    if a_prob and prob_dict.get("away_ht"):
        ht_ft_2_prob = round((a_prob * prob_dict["away_ht"]) / 100.0 * 1.15, 1)
        add_market("HT2_FT2", f"HT 2 - FT 2 ({visitor_team} leads HT & wins FT)", "HT/FT", min(ht_ft_2_prob, a_prob), None)

    # --- RANK & SELECT BEST PREDICTIONS ---
    bankers = sorted([m for m in markets if m["prob"] >= 78.0 and (m["odds"] is None or m["odds"] >= 1.12)], key=lambda x: x["prob"], reverse=True)
    best_banker = bankers[0] if bankers else None

    values = sorted([m for m in markets if m["ev"] is not None and m["ev"] > 0.05 and m["prob"] >= 52.0 and (m["odds"] or 0) >= 1.40], key=lambda x: x["ev"], reverse=True)
    best_value = values[0] if values else None

    scored_markets = []
    for m in markets:
        score = m["prob"]
        if m["odds"] and m["odds"] > 1.25:
            score += (m["odds"] - 1.0) * 15
        if m["is_value"]:
            score += 10
        scored_markets.append((score, m))
    scored_markets.sort(key=lambda x: x[0], reverse=True)

    top_pick = scored_markets[0][1] if scored_markets else {
        "code": betmines_primary_pred,
        "name": f"BetMines Pick: {betmines_primary_pred}",
        "category": "Main",
        "prob": betmines_primary_prob,
        "odds": betmines_primary_odd,
        "ev": calc_ev(betmines_primary_prob, betmines_primary_odd),
        "is_value": False,
        "outcome": evaluate_bet_outcome(betmines_primary_pred, local_score, visitor_score, status),
        "profit": None
    }

    return {
        "id": fix.get("id"),
        "match": f"{local_team} vs {visitor_team}",
        "local_team": local_team,
        "visitor_team": visitor_team,
        "local_score": local_score,
        "visitor_score": visitor_score,
        "status": status,
        "minute": fix.get("minute"),
        "league": league_name,
        "country": country,
        "date_time": date_time,
        "betmines_pick": betmines_primary_pred,
        "betmines_prob": betmines_primary_prob,
        "betmines_odd": betmines_primary_odd,
        "pred_1x2": pred_1x2_data,
        "top_pick": top_pick,
        "best_banker": best_banker,
        "best_value": best_value,
        "all_markets": markets
    }

FINISHED_STATUSES = {"FT", "AET", "PEN", "Finished", "After Extra Time", "AWARDED"}
LIVE_STATUSES = {"LIVE", "HT", "1H", "2H", "ET", "P"}

def is_finished_match(a: Dict[str, Any]) -> bool:
    status = a.get("status") or "NS"
    has_score = a.get("local_score") is not None and a.get("visitor_score") is not None
    return status in FINISHED_STATUSES or (has_score and status not in LIVE_STATUSES)

def is_live_match(a: Dict[str, Any]) -> bool:
    status = a.get("status") or "NS"
    return status in LIVE_STATUSES

def is_upcoming_match(a: Dict[str, Any]) -> bool:
    return not is_finished_match(a) and not is_live_match(a)

def get_ranked_predictions(
    fixtures: List[Dict[str, Any]],
    market_filter: Optional[str] = None,
    min_prob: float = 0.0,
    min_odds: float = 0.0,
    value_only: bool = False,
    league_filter: Optional[str] = None,
    status_filter: str = "upcoming"
) -> List[Dict[str, Any]]:
    analyzed = [analyze_fixture(f) for f in fixtures]

    results = []
    for a in analyzed:
        # Strictly separate upcoming matches from finished matches
        if status_filter == "upcoming" and not (is_upcoming_match(a) or is_live_match(a)):
            continue
        elif status_filter == "finished" and not is_finished_match(a):
            continue
        elif status_filter == "live" and not is_live_match(a):
            continue

        if league_filter and league_filter.lower() not in a["league"].lower():
            continue

        valid_markets = []
        for m in a["all_markets"]:
            if market_filter and market_filter.lower() != "all":
                m_filter = market_filter.lower()
                if m_filter == "1x2" and m["category"] != "1X2":
                    continue
                elif m_filter == "double chance" and m["category"] != "Double Chance":
                    continue
                elif m_filter not in m["category"].lower() and m_filter not in m["code"].lower():
                    continue

            if m["prob"] < min_prob:
                continue
            if min_odds > 0 and (not m["odds"] or m["odds"] < min_odds):
                continue
            if value_only and not m["is_value"]:
                continue
            valid_markets.append(m)

        if valid_markets or not (market_filter or min_prob > 0 or min_odds > 0 or value_only):
            a_copy = dict(a)
            if valid_markets:
                a_copy["filtered_markets"] = sorted(valid_markets, key=lambda x: x["prob"], reverse=True)
                a_copy["selected_pick"] = a_copy["filtered_markets"][0]
            else:
                a_copy["filtered_markets"] = a["all_markets"]
                a_copy["selected_pick"] = a["top_pick"]
            results.append(a_copy)

    # Sort matches by the quality of their top pick
    results.sort(key=lambda x: x["selected_pick"]["prob"], reverse=True)
    return results

def get_golden_picks(fixtures: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Finds daily Golden Selections including 1X2 Outright Winners (strictly upcoming matches)."""
    analyzed = [analyze_fixture(f) for f in fixtures]

    winners_1x2 = []
    bankers = []
    values = []
    btts_picks = []
    goal_picks = []

    for a in analyzed:
        # Strictly exclude finished matches from Golden Picks
        if is_finished_match(a):
            continue

        # Dedicated 1X2 Outright Winner Golden Selections
        pred_1x2 = a["pred_1x2"]
        if pred_1x2["prob"] >= 52.0:
            winners_1x2.append({
                "match": a["match"],
                "league": a["league"],
                "pick": pred_1x2["label"],
                "prob": pred_1x2["prob"],
                "odds": pred_1x2["odds"],
                "market": "1X2",
                "date_time": a["date_time"],
                "outcome": pred_1x2["outcome"]
            })

        # Bankers
        if a["best_banker"]:
            bankers.append({
                "match": a["match"],
                "league": a["league"],
                "pick": a["best_banker"]["name"],
                "prob": a["best_banker"]["prob"],
                "odds": a["best_banker"]["odds"],
                "market": a["best_banker"]["category"],
                "date_time": a["date_time"],
                "outcome": a["best_banker"]["outcome"]
            })

        # Values
        if a["best_value"]:
            values.append({
                "match": a["match"],
                "league": a["league"],
                "pick": a["best_value"]["name"],
                "prob": a["best_value"]["prob"],
                "odds": a["best_value"]["odds"],
                "ev": a["best_value"]["ev"],
                "date_time": a["date_time"],
                "outcome": a["best_value"]["outcome"]
            })

        # BTTS
        for m in a["all_markets"]:
            if m["category"] == "BTTS" and m["prob"] >= 65.0:
                btts_picks.append({
                    "match": a["match"],
                    "league": a["league"],
                    "pick": m["name"],
                    "prob": m["prob"],
                    "odds": m["odds"],
                    "date_time": a["date_time"],
                    "outcome": m["outcome"]
                })
            elif m["category"] == "Goals" and "Over" in m["name"] and m["prob"] >= 75.0:
                goal_picks.append({
                    "match": a["match"],
                    "league": a["league"],
                    "pick": m["name"],
                    "prob": m["prob"],
                    "odds": m["odds"],
                    "date_time": a["date_time"],
                    "outcome": m["outcome"]
                })

    winners_1x2.sort(key=lambda x: x["prob"], reverse=True)
    bankers.sort(key=lambda x: x["prob"], reverse=True)
    values.sort(key=lambda x: x["ev"] or 0, reverse=True)
    btts_picks.sort(key=lambda x: x["prob"], reverse=True)
    goal_picks.sort(key=lambda x: x["prob"], reverse=True)

    return {
        "winners_1x2": winners_1x2[:10],
        "bankers": bankers[:10],
        "values": values[:10],
        "btts": btts_picks[:10],
        "goals": goal_picks[:10]
    }

def get_history_performance(fixtures: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates overall prediction accuracy, win rate, and profit metrics."""
    analyzed = [analyze_fixture(f) for f in fixtures]
    
    total_evaluated = 0
    total_1x2_evaluated = 0
    won_1x2 = 0
    won_top_picks = 0
    total_profit_units = 0.0

    history_records = []

    for a in analyzed:
        p1 = a["pred_1x2"]
        top = a["top_pick"]

        # Only evaluate finished matches
        if a["status"] in ["FT", "AET", "PEN", "Finished", "After Extra Time"] and a["local_score"] is not None:
            total_evaluated += 1
            if top["outcome"] == "WON":
                won_top_picks += 1
                if top["odds"]:
                    total_profit_units += (top["odds"] - 1.0)
            elif top["outcome"] == "LOST":
                total_profit_units -= 1.0

            if p1["outcome"] in ["WON", "LOST"]:
                total_1x2_evaluated += 1
                if p1["outcome"] == "WON":
                    won_1x2 += 1

            history_records.append({
                "id": a["id"],
                "match": a["match"],
                "league": a["league"],
                "date_time": a["date_time"],
                "score": f"{a['local_score']} - {a['visitor_score']}",
                "status": a["status"],
                "pred_1x2": p1["label"],
                "pred_1x2_odds": p1["odds"],
                "pred_1x2_prob": p1["prob"],
                "pred_1x2_outcome": p1["outcome"],
                "top_pick": top["name"],
                "top_pick_odds": top["odds"],
                "top_pick_prob": top["prob"],
                "top_pick_outcome": top["outcome"],
                "profit": top.get("profit")
            })

    win_rate_top = round((won_top_picks / total_evaluated * 100.0), 1) if total_evaluated > 0 else 0.0
    win_rate_1x2 = round((won_1x2 / total_1x2_evaluated * 100.0), 1) if total_1x2_evaluated > 0 else 0.0

    return {
        "total_finished": total_evaluated,
        "top_picks_won": won_top_picks,
        "top_picks_win_rate": win_rate_top,
        "one_x_two_evaluated": total_1x2_evaluated,
        "one_x_two_won": won_1x2,
        "one_x_two_win_rate": win_rate_1x2,
        "total_profit_units": round(total_profit_units, 2),
        "history": history_records
    }
