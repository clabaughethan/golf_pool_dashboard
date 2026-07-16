SHORT_NOT_BOTTOM_75_POINTS = 75


def _get_r2_total(player_data):
    """Compute R1+R2 total strokes for a player."""
    rounds = player_data.get("rounds", [])
    return sum(
        r.get("strokes", 0) for r in rounds
        if r.get("strokes") is not None and r["number"] <= 2
    )


def _build_mc_from_last(players, made_cut):
    """Build a dict mapping MC player name -> position from last among MC.

    Position from last = number of MC players with a higher (worse) R1+R2 total, + 1.
    Players tied at the same R1+R2 get the same value.
    Excludes WD/DQ players from the MC count.
    """
    has_made_cut_field = any(
        isinstance(p.get("made_cut"), bool) for p in players.values()
    )
    mc_players = {}
    for name, p in players.items():
        is_mc = not p.get("made_cut") if has_made_cut_field else name not in made_cut
        if is_mc and p.get("score", "") not in ("WD", "DQ"):
            r2 = _get_r2_total(p)
            if r2 > 0:
                mc_players[name] = r2

    if not mc_players:
        return {}

    r2_values = sorted(set(mc_players.values()))
    worse_counts = {}
    for i, score in enumerate(r2_values):
        worse_counts[score] = sum(1 for s in mc_players.values() if s > score)

    return {name: worse_counts[r2] + 1 for name, r2 in mc_players.items()}


def _rounds_completed(player_data):
    return sum(1 for r in player_data.get("rounds", []) if r["complete"])


def _resolve_made_cut(players, cut_line):
    """Determine which players made the cut.

    If any player has a 'made_cut' boolean in their snapshot data,
    use those directly (snapshot is source of truth for past tournaments).
    Otherwise fall back to computing from R2 totals (for live ESPN data).
    """
    has_made_cut_field = any(
        isinstance(p.get("made_cut"), bool) for p in players.values()
    )
    if has_made_cut_field:
        return {name for name, p in players.items() if p.get("made_cut")}
    return _compute_made_cut(players, cut_line)


def _compute_made_cut(players, cut_line):
    """Compute which players made the cut based on round 2 scores only."""
    r2_scores = {}
    for name, p in players.items():
        r2_total = _get_r2_total(p)
        rounds = p.get("rounds", [])
        r2_complete = any(r["number"] == 2 and r.get("complete") for r in rounds)
        if r2_complete and r2_total > 0:
            r2_scores[name] = r2_total

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


def _not_in_bottom_75_after_day2(player_data, total_players):
    """Check if a short pick is NOT in the bottom 75 after Day 2."""
    if _rounds_completed(player_data) < 2:
        return False
    pos = player_data["order"]
    return pos <= (total_players - 75)


def calculate_pool_scores(picks_list, leaderboard, rules=None):
    """Calculate pool scores for all participants.

    Returns list of dicts sorted by score (least points wins).
    """
    total_players = leaderboard["total_players"]
    players = leaderboard["players"]
    is_final = leaderboard["completed"]
    cut_line = (rules or {}).get("cut_line", 60)
    has_captain = (rules or {}).get("captain_pick", False)
    captain_mul = (rules or {}).get("captain_pick_multiplier", 2)

    made_cut = _resolve_made_cut(players, cut_line)
    mc_from_last = _build_mc_from_last(players, made_cut)
    mc_points = max(75, len(made_cut) + 1)
    print(f"[SCORING DEBUG] made_cut={len(made_cut)}, mc_points={mc_points}, cut_line={cut_line}, is_final={is_final}, total_players={total_players}")

    results = []
    for entry in picks_list:
        score = 0
        pick_details = []
        captain_name = entry.get("captain_pick") if has_captain else None

        wp = entry["win_picks"]
        all_win = wp.values() if isinstance(wp, dict) else wp
        flat_win = [p for group in all_win for p in (group if isinstance(group, list) else [group])]

        cut_determined = len(made_cut) > 0

        for player_name in flat_win:
            player_data = players.get(player_name)
            is_captain = player_name == captain_name
            detail = {"name": player_name, "type": "win", "points": 0, "captain": is_captain}

            if player_data is None or player_data["score"] in ("WD", "DQ"):
                detail["points"] = mc_points
                detail["result"] = "WD/DQ"
            elif not is_final and not cut_determined:
                pos = player_data.get("order", mc_points)
                detail["points"] = pos
                detail["result"] = f"T{pos}" if pos else str(pos)
            elif player_name not in made_cut:
                detail["points"] = mc_points
                detail["result"] = "Missed Cut"
            else:
                pos = player_data["order"]
                detail["points"] = pos
                detail["result"] = f"T{pos}" if pos else str(pos)

            if is_captain:
                detail["points"] *= captain_mul
                detail["captain_mul"] = captain_mul

            score += detail["points"]
            pick_details.append(detail)

        for player_name in entry["short_picks"]:
            player_data = players.get(player_name)
            detail = {"name": player_name, "type": "short", "points": 0}

            if player_data is None or player_data["score"] in ("WD", "DQ"):
                detail["points"] = mc_points
                detail["result"] = "WD/DQ"
            elif player_name in made_cut:
                detail["points"] = SHORT_NOT_BOTTOM_75_POINTS
                detail["result"] = "Made Cut"
            elif not is_final and _not_in_bottom_75_after_day2(player_data, total_players):
                detail["points"] = SHORT_NOT_BOTTOM_75_POINTS
                detail["result"] = "Not in bottom 75"
            else:
                fl = mc_from_last.get(player_name)
                if fl:
                    detail["points"] = fl
                    detail["result"] = f"#{fl} from last"
                else:
                    detail["points"] = mc_points
                    detail["result"] = "Missed Cut"

            score += detail["points"]
            pick_details.append(detail)

        # If captain pick is NOT in win_picks (stored separately), score it too
        if captain_name and captain_name not in flat_win:
            player_data = players.get(captain_name)
            detail = {"name": captain_name, "type": "win", "points": 0, "captain": True, "captain_mul": captain_mul}

            if player_data is None or player_data["score"] in ("WD", "DQ"):
                detail["points"] = mc_points
                detail["result"] = "WD/DQ"
            elif not is_final and not cut_determined:
                pos = player_data.get("order", mc_points)
                detail["points"] = pos
                detail["result"] = f"T{pos}" if pos else str(pos)
            elif captain_name not in made_cut:
                detail["points"] = mc_points
                detail["result"] = "Missed Cut"
            else:
                pos = player_data["order"]
                detail["points"] = pos
                detail["result"] = f"T{pos}" if pos else str(pos)

            detail["points"] *= captain_mul
            score += detail["points"]
            pick_details.append(detail)

        if len(results) == 0:
            print(f"[SCORING DEBUG] First entry: {entry['participant_name']}, score={score}, cut_determined={cut_determined}")
            for d in pick_details[:3]:
                print(f"  {d['name']}: pts={d['points']} result={d['result']}")

        results.append({
            "participant_name": entry["participant_name"],
            "score": score,
            "picks": pick_details,
        })

    results.sort(key=lambda x: x["score"])
    for i, r in enumerate(results, 1):
        r["rank"] = i

    return results
