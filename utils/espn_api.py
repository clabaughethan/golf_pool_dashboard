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

    players = {}
    for c in competitors:
        name = c["athlete"]["displayName"]
        linescores = c.get("linescores", [])
        rounds_completed = sum(
            1 for r in linescores
            if r.get("displayValue") and r["displayValue"] != "-"
        )

        players[name] = {
            "order": c["order"],
            "score": c["score"],
            "rounds_completed": rounds_completed,
        }

    return {
        "event_name": event["name"],
        "status": competition["status"]["type"]["detail"],
        "round": competition["status"].get("period", 0),
        "total_players": len(competitors),
        "completed": event["status"]["type"].get("completed", False),
        "players": players,
    }
