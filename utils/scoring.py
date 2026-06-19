MISSED_CUT_POINTS = 75
WD_DQ_POINTS = 75
SHORT_NOT_BOTTOM_75_POINTS = 75


def calculate_pool_scores(picks_list, leaderboard):
    """
    Calculate pool scores for all participants.

    picks_list: list of dicts with keys: participant_name, win_picks, short_picks
    leaderboard: dict from espn_api.fetch_leaderboard()

    Returns list of dicts sorted by score (least points wins).
    """
    total_players = leaderboard["total_players"]
    players = leaderboard["players"]
    is_final = leaderboard["completed"]

    results = []
    for entry in picks_list:
        score = 0
        pick_details = []

        for player_name in entry["win_picks"]:
            player_data = players.get(player_name)
            detail = {"name": player_name, "type": "win", "points": 0}

            if player_data is None or player_data["score"] in ("WD", "DQ"):
                detail["points"] = WD_DQ_POINTS
                detail["result"] = "WD/DQ"
            elif not is_final and player_data["rounds_completed"] < 2:
                detail["points"] = 0
                detail["result"] = "In progress"
            elif not is_final and _missed_cut(player_data, total_players):
                detail["points"] = MISSED_CUT_POINTS
                detail["result"] = "Missed Cut"
            elif is_final and player_data["score"] in ("WD", "DQ", "MC"):
                detail["points"] = WD_DQ_POINTS
                detail["result"] = player_data["score"]
            else:
                pos = player_data["order"]
                detail["points"] = pos
                detail["result"] = f"T{pos}" if pos else str(pos)

            score += detail["points"]
            pick_details.append(detail)

        for player_name in entry["short_picks"]:
            player_data = players.get(player_name)
            detail = {"name": player_name, "type": "short", "points": 0}

            if player_data is None or player_data["score"] in ("WD", "DQ"):
                detail["points"] = WD_DQ_POINTS
                detail["result"] = "WD/DQ"
            elif not is_final and _not_in_bottom_75_after_day2(player_data, total_players):
                detail["points"] = SHORT_NOT_BOTTOM_75_POINTS
                detail["result"] = "Not in bottom 75"
            elif is_final:
                pos = player_data["order"]
                detail["points"] = total_players - pos + 1
                detail["result"] = f"#{total_players - pos + 1} from last"
            else:
                pos = player_data["order"]
                detail["points"] = total_players - pos + 1
                detail["result"] = f"#{total_players - pos + 1} from last"

            score += detail["points"]
            pick_details.append(detail)

        results.append({
            "participant_name": entry["participant_name"],
            "score": score,
            "picks": pick_details,
        })

    results.sort(key=lambda x: x["score"])
    for i, r in enumerate(results, 1):
        r["rank"] = i

    return results


def _missed_cut(player_data, total_players):
    """Check if a player likely missed the cut (after round 2, not in top ~70 + ties)."""
    if player_data["rounds_completed"] < 2:
        return False
    if player_data["score"] in ("WD", "DQ", "MC"):
        return True
    pos = player_data["order"]
    return pos > 78


def _not_in_bottom_75_after_day2(player_data, total_players):
    """Check if a short pick is NOT in the bottom 75 after Day 2."""
    if player_data["rounds_completed"] < 2:
        return False
    pos = player_data["order"]
    return pos <= (total_players - 75)
