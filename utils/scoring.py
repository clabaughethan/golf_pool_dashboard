MISSED_CUT_POINTS = 75
WD_DQ_POINTS = 75
SHORT_NOT_BOTTOM_75_POINTS = 75


def calculate_pool_scores(picks_list, leaderboard, rules=None):
    """
    Calculate pool scores for all participants.

    picks_list: list of dicts with keys: participant_name, win_picks, short_picks
    leaderboard: dict from espn_api.fetch_leaderboard()
    rules: tournament rules dict (for cut_line)

    Returns list of dicts sorted by score (least points wins).
    """
    total_players = leaderboard["total_players"]
    players = leaderboard["players"]
    is_final = leaderboard["completed"]
    cut_line = (rules or {}).get("cut_line", 60)

    made_cut = _compute_made_cut(players, cut_line)

    results = []
    for entry in picks_list:
        score = 0
        pick_details = []

        wp = entry["win_picks"]
        all_win = wp.values() if isinstance(wp, dict) else wp
        flat_win = [p for group in all_win for p in (group if isinstance(group, list) else [group])]

        for player_name in flat_win:
            player_data = players.get(player_name)
            detail = {"name": player_name, "type": "win", "points": 0}

            if player_data is None or player_data["score"] in ("WD", "DQ"):
                detail["points"] = WD_DQ_POINTS
                detail["result"] = "WD/DQ"
            elif not is_final and _rounds_completed(player_data) < 2:
                detail["points"] = 0
                detail["result"] = "In progress"
            elif not is_final and _missed_cut(player_name, total_players, made_cut):
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


def _rounds_completed(player_data):
    return sum(1 for r in player_data.get("rounds", []) if r["complete"])


def _compute_made_cut(players, cut_line):
    """Compute which players made the cut based on round 2 scores only."""
    r2_scores = {}
    for name, p in players.items():
        rounds = p.get("rounds", [])
        r2 = [r for r in rounds if r["number"] == 2]
        if r2 and r2[0]["complete"] and r2[0].get("strokes") is not None:
            r1 = [r for r in rounds if r["number"] == 1]
            total = 0
            for r in r1 + r2:
                if r.get("strokes") is not None:
                    total += r["strokes"]
            r2_scores[name] = total

    sorted_players = sorted(r2_scores.items(), key=lambda x: x[1])
    made_cut = set()
    i = 0
    while i < len(sorted_players) and i < cut_line:
        score = sorted_players[i][1]
        j = i
        while j < len(sorted_players) and sorted_players[j][1] == score:
            j += 1
        for k in range(i, j):
            made_cut.add(sorted_players[k][0])
        i = j
    return made_cut


def _missed_cut(player_name, total_players, made_cut):
    """Check if a player missed the cut."""
    return player_name not in made_cut


def _not_in_bottom_75_after_day2(player_data, total_players):
    """Check if a short pick is NOT in the bottom 75 after Day 2."""
    if _rounds_completed(player_data) < 2:
        return False
    pos = player_data["order"]
    return pos <= (total_players - 75)
