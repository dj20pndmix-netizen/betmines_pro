import json
from analyzer import analyze_fixture, get_golden_picks

with open(r'C:\Users\user\.gemini\antigravity\brain\cf4ed9c5-d20d-4b14-b5a7-c1fa9393b83b\scratch\sample_fixtures.json', 'r', encoding='utf-8') as f:
    fixtures = json.load(f)

print('Testing analyze_fixture...')
for fix in fixtures:
    res = analyze_fixture(fix)
    print(f"Match: {res['match']} ({res['league']})")
    print(f"  Top Pick: {res['top_pick']['name']} | Prob: {res['top_pick']['prob']}% | Odds: {res['top_pick']['odds']}")
    if res['best_banker']:
        print(f"  Banker: {res['best_banker']['name']} ({res['best_banker']['prob']}%)")
    if res['best_value']:
        ev_pct = int(res['best_value']['ev'] * 100)
        print(f"  Value: {res['best_value']['name']} (EV: +{ev_pct}%)")

print('\nTesting get_golden_picks...')
golden = get_golden_picks(fixtures)
print(f"Bankers: {len(golden['bankers'])}, Values: {len(golden['values'])}, BTTS: {len(golden['btts'])}, Goals: {len(golden['goals'])}")
