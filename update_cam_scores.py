import json
import sys
sys.path.insert(0, '.')
from supabase import create_client
from utils.scoring import calculate_pool_scores

url = "https://dfbfajvvlewrwdcmncxd.supabase.co"
key = "sb_publishable_oxbcuTZLm-WSsJzt0wZINg_KmnwzXEP"
sb = create_client(url, key)

picks_result = sb.table('picks').select('*').eq('tournament_id', 'us-open-2026').execute()
picks = [{'participant_name': r['participant_name'], 'win_picks': r['win_picks'], 'short_picks': r['short_picks']} for r in picks_result.data]

snap = sb.table('leaderboard_snapshots').select('*').eq('tournament_id', 'us-open-2026').limit(1).execute()
leaderboard = {"total_players": len(snap.data[0]['players']), "players": snap.data[0]['players'], "completed": True}

results = calculate_pool_scores(picks, leaderboard, {"cut_line": 60})

with open('data/cam_scores.json') as f:
    cam = json.load(f)

output = {}
output['source'] = cam['source']
output['tournament_id'] = cam['tournament_id']
output['official_results'] = cam['official_results']
output['our_results'] = {r['participant_name']: r['score'] for r in results}
output['differences'] = {r['participant_name']: r['score'] - cam['official_results'].get(r['participant_name'], 0) for r in results}

with open('data/cam_scores.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Updated cam_scores.json")
for r in results:
    name = r['participant_name']
    diff = r['score'] - cam['official_results'].get(name, 0)
    flag = " OK" if diff == 0 else f" diff={diff:+d}"
    print(f"  {name:<20} {r['score']:<5} (Cam: {cam['official_results'].get(name, 0)}){flag}")
