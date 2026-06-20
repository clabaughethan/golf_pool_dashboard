import requests

ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard"


def fetch_leaderboard():
    """Fetch the current PGA leaderboard from ESPN."""
    resp = requests.get(ESPN_SCOREBOARD_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    event = data["events"][0]
    competition = event["competitions"][0]
    competitors = competition["competitors"]
    current_round = competition["status"].get("period", 1)

    players = {}
    for c in competitors:
        name = c["athlete"]["displayName"]
        linescores = c.get("linescores", [])

        rounds = []
        for rs in linescores:
            rnd_num = rs.get("period")
            gross = rs.get("value")
            display = rs.get("displayValue", "")
            holes = len(rs.get("linescores", []))
            dnp = display == "-" or holes == 0
            complete = holes >= 18 if not dnp else False
            rounds.append({
                "number": rnd_num,
                "strokes": int(gross) if gross and gross != "-" and complete else None,
                "holes_completed": holes if not complete and holes > 0 and not dnp else None,
                "complete": complete,
                "dnp": dnp,
            })

        players[name] = {
            "order": c["order"],
            "score": c["score"],
            "rounds": rounds,
        }

    return {
        "event_name": event["name"],
        "status": competition["status"]["type"]["detail"],
        "round": current_round,
        "total_players": len(competitors),
        "completed": event["status"]["type"].get("completed", False),
        "players": players,
    }
