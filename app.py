import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import streamlit as st
import requests
import pandas as pd
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
from supabase import create_client
from utils.scoring import calculate_pool_scores, _compute_made_cut
from utils.espn_api import fetch_leaderboard
from utils.config import load_tournament_configs

st.set_page_config(page_title="Wasylak Golf Pools App", page_icon="⛳", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@media (max-width: 768px) {
    [data-testid="stSidebar"][aria-expanded="true"] {
        width: 280px !important;
        min-width: 280px !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        width: 0px !important;
        min-width: 0px !important;
    }
    [data-testid="stSidebarNav"] {
        padding-top: 0.5rem;
    }
    section[data-testid="stSidebar"] button {
        padding: 0.4rem 0.75rem;
        font-size: 0.85rem;
    }
}
</style>
""", unsafe_allow_html=True)


def get_sb():
    if "supabase" not in st.session_state:
        st.session_state.supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    return st.session_state.supabase

configs = load_tournament_configs()
db_tournaments = get_sb().table("tournaments").select("id, start_time").execute().data
start_times = {t["id"]: t.get("start_time") or "" for t in db_tournaments}
sorted_ids = sorted(configs.keys(), key=lambda cid: start_times.get(cid, ""), reverse=True)
tournament_names = {configs[cid]["name"]: cid for cid in sorted_ids}
name_list = list(tournament_names.keys())

current_id = st.session_state.get("selected_tournament_id")
current_index = name_list.index(next((n for n, tid in tournament_names.items() if tid == current_id), name_list[0])) if current_id else 0

selected_name = st.sidebar.selectbox("Tournament", name_list, index=current_index)
selected_id = tournament_names[selected_name]
st.session_state.selected_tournament_id = selected_id
st.session_state.selected_tournament_config = configs[selected_id]

st.sidebar.divider()

active_home = (st.session_state.get("page", "Home") == "Home")
if st.sidebar.button("🏠 Home", key="nav_Home", use_container_width=True, disabled=active_home):
    st.session_state.page = "Home"
    st.rerun()

nav_items = [("📋 Rules", "Rules"), ("👥 Player Groups", "Groups"), ("🏌️ Make Picks", "Make Picks"), ("🏆 Leaderboard", "Leaderboard")]
for label, key in nav_items:
    active = (st.session_state.get("page", "Home") == key)
    if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True, disabled=active):
        st.session_state.page = key
        st.rerun()

page = st.session_state.get("page", "Home")

config = configs[selected_id]

if page == "Home":
    st.title("⛳ Wasylak Golf Pools App")
    st.markdown("---")
    st.markdown(f"### {config['name']}")

    picks = get_sb().table("picks").select("*", count="exact").eq("tournament_id", selected_id).execute()
    participant_count = picks.count if hasattr(picks, 'count') else len(picks.data)

    start_time = start_times.get(selected_id, "")
    if start_time:
        try:
            t = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) < t:
                status = "Upcoming"
            else:
                snapshot = get_sb().table("leaderboard_snapshots").select("status").eq("tournament_id", selected_id).execute().data
                if snapshot:
                    status = snapshot[0]["status"]
                else:
                    try:
                        lb = fetch_leaderboard()
                        status = "Completed" if lb["completed"] else "In Progress"
                    except Exception:
                        status = "In Progress"
        except Exception:
            status = "Open"
    else:
        status = "Open"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", status)
    with col2:
        st.metric("Participants", participant_count)
    with col3:
        st.metric("Entry Fee", "$20")

    st.markdown("---")
    st.subheader("How It Works")
    total_win = sum(config["rules"].get("win_picks_per_group", {}).values())
    short_n = config["rules"].get("short_picks", 0)
    captain_n = 1 if config["rules"].get("captain_pick") else 0
    parts = [f"Select {total_win} win picks"]
    if captain_n:
        parts.append("1 Captain's Pick")
    if short_n:
        parts.append(f"{short_n} short picks")
    st.markdown(f"**1. Make Your Picks** — {' + '.join(parts)}. Enter the pool code to submit.")
    st.markdown("**2. Tournament Starts** — Picks lock at the first tee time. No changes after that.")
    st.markdown("**3. Live Scoring** — Standings update automatically from ESPN every 2 minutes.")

    st.markdown("---")
    st.subheader("Quick Links")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 View Rules", use_container_width=True):
            st.session_state.page = "Rules"
            st.rerun()
    with col2:
        if st.button("🏌️ Make Picks", use_container_width=True):
            st.session_state.page = "Make Picks"
            st.rerun()
    with col3:
        if st.button("🏆 Leaderboard", use_container_width=True):
            st.session_state.page = "Leaderboard"
            st.rerun()

    st.info("Share the pool code with participants so they can submit their picks!")

elif page == "Rules":
    st.title("📋 Pool Rules")
    st.header(config["name"])
    st.divider()

    rules = config["rules"]
    groups = config["player_groups"]

    st.subheader("How to Pick")

    win_groups = rules.get("win_picks_per_group", {})
    total_win = sum(win_groups.values())
    short_count = rules.get("short_picks", 0)

    has_captain = rules.get("captain_pick", False)

    rows = []
    for g, count in win_groups.items():
        rows.append(f"| Players to **WIN** | {count} from Group {g} |")
    if has_captain:
        rows.append(f"| **Captain's Pick** | 1 | Any group (extra pick, points doubled) |")
    if short_count:
        rows.append(f"| Players to **SHORT** (lose) | {short_count} | Full field (any group) |")
    st.markdown("\n".join([
        "| Selection | # of Picks | From |",
        "|-----------|------------|------|",
    ] + rows))

    st.subheader("Scoring (Least Points Wins)")
    scoring_rows = []
    scoring_rows.append("| **Win pick** finishes in position X | X points (1st = 1 pt, 27th = 27 pts, etc.) |")
    if has_captain:
        multiplier = rules.get("captain_pick_multiplier", 2)
        scoring_rows.append(f"| **Captain's Pick** finishes in position X | **{multiplier}x** points (X × {multiplier}) |")
        scoring_rows.append(f"| **Captain's Pick** misses the cut | {multiplier} × 75 = {multiplier * 75} points |")
    scoring_rows.append("| **Win pick** misses the cut | 75 points |")
    if short_count:
        scoring_rows.append("| **Short pick** finishes X from last | X points (last = 1 pt, 30th-to-last = 30 pts, etc.) |")
        scoring_rows.append("| **Short pick** not in bottom 75 after Day 2 | 75 points |")
    scoring_rows.append("| **WD or DQ** (any pick) | 75 points |")
    st.markdown("\n".join([
        "| Scenario | Points |",
        "|----------|--------|",
    ] + scoring_rows))

    st.subheader("Key Notes")
    if has_captain:
        st.markdown("- Your **Captain's Pick** is an **extra** player (not one of your 10 group picks) whose points are **doubled**.")
    if short_count:
        st.markdown("- Short picks are **not** group-restricted — you can short anyone in the field.")
    st.markdown("- Picks are locked once the tournament begins.")
    st.markdown("- Submit your picks on the **Make Picks** page using your pool code.")

elif page == "Groups":
    st.title("👥 Player Groups")
    st.header(config["name"])
    st.divider()
    rules = config["rules"]
    groups = config["player_groups"]

    total = sum(len(g) for g in groups.values())
    st.markdown(f"**{total} players across {len(groups)} groups**")
    st.divider()

    rows = []
    for group_num in sorted(groups.keys(), key=lambda x: int(x)):
        for p in groups[group_num]:
            rows.append({
                "Group": int(group_num),
                "Player": p["name"],
                "OWGR": p.get("owgr", "N/A"),
                "Odds": p.get("odds", "N/A"),
            })
        if int(group_num) < max(int(g) for g in groups.keys()):
            rows.append({"Group": "", "Player": "", "OWGR": "", "Odds": ""})
    st.dataframe(rows, use_container_width=True, hide_index=True)

elif page == "Make Picks":
    tournament_id = selected_id

    tournaments = get_sb().table("tournaments").select("*").execute().data
    tournament = next((t for t in tournaments if t["id"] == tournament_id), None)

    st.title("🏌️ Make Your Picks")
    st.divider()

    if tournament is None:
        st.error("Tournament not found.")
        st.stop()

    if tournament.get("status") in ("locked", "final"):
        st.warning("This tournament is locked. Picks can no longer be submitted or edited.")
        st.stop()

    start_time = tournament.get("start_time")
    if start_time:
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) >= start_time:
            st.warning("This tournament has started. Picks can no longer be submitted or edited.")
            st.stop()

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.participant_name = ""

    if not st.session_state.authenticated:
        st.subheader("Enter Pool Code")
        col1, col2 = st.columns(2)
        with col1:
            pool_code = st.text_input("Pool Code", type="password")
        with col2:
            st.session_state.participant_name = st.text_input("Your Name")

        if st.button("Enter Pool"):
            if not pool_code:
                st.error("Please enter the pool code.")
            elif not st.session_state.participant_name:
                st.error("Please enter your name.")
            elif pool_code == tournament["pool_code"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid pool code.")
        st.stop()

    participant_name = st.session_state.participant_name
    st.success(f"Welcome, **{participant_name}**!")

    sb = get_sb()
    existing_data = sb.table("picks").select("*").eq("tournament_id", tournament_id).eq("participant_name", participant_name).execute().data
    existing = existing_data[0] if existing_data else None
    existing_win = existing["win_picks"] if existing else []
    existing_short = existing["short_picks"] if existing else []
    existing_captain = existing["captain_pick"] if existing else None

    rules = config["rules"]
    groups = config["player_groups"]

    def parse_odds(s):
        return int(s.replace("+", "").replace(",", "")) if s else 999999

    def player_label(p):
        owgr = f"OWGR: {p['owgr']}" if p.get("owgr") else "No OWGR"
        return f"{p['name']}  ({owgr}, {p['odds']})"

    def sort_key(p):
        return parse_odds(p["odds"])

    all_players_list = sorted(
        [p for g in groups.values() for p in g],
        key=sort_key
    )
    all_player_names = [p["name"] for p in all_players_list]
    all_player_labels = {p["name"]: player_label(p) for p in all_players_list}

    win_picks = []
    st.subheader("Win Picks")
    st.info("Extra picks beyond the allowed count per group are ignored.")
    for group_num, count in rules["win_picks_per_group"].items():
        group_players = sorted(groups[group_num], key=sort_key)
        group_names = [p["name"] for p in group_players]
        defaults = [p for p in existing_win if p in group_names]
        selected = st.multiselect(
            f"Group {group_num} — Pick {count} to WIN",
            group_names,
            default=defaults,
            key=f"win_{group_num}",
            format_func=lambda n: all_player_labels.get(n, n),
        )
        if len(selected) > count:
            selected = selected[:count]
        if len(selected) < count:
            st.warning(f"Select {count - len(selected)} more from Group {group_num}.")
        win_picks.extend(selected)

    captain_pick = None
    has_captain = rules.get("captain_pick", False)
    if has_captain:
        st.subheader("Captain's Pick")
        eligible = [n for n in all_player_names if n not in win_picks]
        captain_default = existing_captain if existing_captain in eligible else None
        captain_pick = st.selectbox(
            "Pick 1 extra player as your CAPTAIN (points doubled!)",
            [""] + eligible,
            index=([""] + eligible).index(captain_default) if captain_default else 0,
            key="captain",
            format_func=lambda n: all_player_labels.get(n, n) if n else "",
        )
        if not captain_pick:
            st.warning("Select your Captain's Pick.")
        else:
            st.success(f"Captain: **{captain_pick}** — all points doubled!")

    short_count = rules["short_picks"]
    short_picks = []
    if short_count > 0:
        short_defaults = [p for p in existing_short if p in all_player_names]
        short_picks = st.multiselect(
            f"Short Picks — Pick {short_count} to LOSE",
            all_player_names,
            default=short_defaults,
            key="short",
            format_func=lambda n: all_player_labels.get(n, n),
        )
        if len(short_picks) > short_count:
            st.error(f"Too many short picks. You can only pick {short_count}.")
        elif len(short_picks) < short_count:
            st.warning(f"Select {short_count - len(short_picks)} more.")

    expected = sum(rules["win_picks_per_group"].values()) + short_count
    captain_extra = 1 if has_captain else 0
    total_expected = expected + captain_extra
    current = len(win_picks) + len(short_picks) + (1 if captain_pick else 0)

    st.divider()
    all_good = current == total_expected and len(set(win_picks)) == len(win_picks)
    if short_count > 0 and set(win_picks) & set(short_picks):
        all_good = False
        st.error("A player cannot be both a win pick and a short pick.")
    if has_captain and not captain_pick:
        all_good = False

    if all_good:
        if st.button("Submit Picks", type="primary"):
            payload = {
                "tournament_id": tournament_id,
                "participant_name": participant_name,
                "win_picks": win_picks,
                "short_picks": short_picks,
            }
            if has_captain:
                payload["captain_pick"] = captain_pick
            sb.table("picks").upsert(payload, on_conflict="tournament_id,participant_name").execute()
            st.success("Picks submitted successfully!")
            st.balloons()
    else:
        st.info(f"Complete all {total_expected} picks to submit.")

elif page == "Leaderboard":
    tournament_id = selected_id

    st.title("🏆 Live Leaderboard")
    st.divider()

    sb = get_sb()

    start_time_str = start_times.get(selected_id, "")
    started = False
    if start_time_str:
        try:
            t = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            started = datetime.now(timezone.utc) >= t
        except Exception:
            started = True
    else:
        started = True

    if not started:
        t_display = t.astimezone(ZoneInfo("America/New_York")).strftime("%A, %B %d at %I:%M %p %Z")
        st.subheader(f"{config['name']} — Starts {t_display}")
        st.info("Picks are hidden until the tournament starts.")
        st.stop()

    snapshot = sb.table("leaderboard_snapshots").select("*").eq("tournament_id", tournament_id).execute().data
    is_snapshot = bool(snapshot)
    if snapshot:
        snap = snapshot[0]
        leaderboard = {
            "event_name": snap["event_name"],
            "status": snap["status"],
            "total_players": len(snap["players"]),
            "completed": True,
            "players": snap["players"],
            "round": 4,
        }
        st.subheader(f"{leaderboard['event_name']} — {leaderboard['status']}")
    else:
        try:
            leaderboard = fetch_leaderboard()
            live = True
        except Exception:
            live = False

        if live:
            if not leaderboard["completed"]:
                st_autorefresh(interval=120_000, key="refresh")
            if leaderboard["completed"]:
                sb.table("leaderboard_snapshots").upsert({
                    "tournament_id": tournament_id,
                    "event_name": leaderboard["event_name"],
                    "status": leaderboard["status"],
                    "players": leaderboard["players"],
                }, on_conflict="tournament_id").execute()
            st.subheader(f"{leaderboard['event_name']} — {leaderboard['status']}")
        else:
            st.subheader(f"{config['name']} — Final Results")
            st.info("No live data available. Paste the final leaderboard below to save results.")

            with st.expander("Manually enter leaderboard", expanded=True):
                st.caption("Paste tab-separated data: one line per player, format: `Player Name\\tScore to Par` (e.g. `-7` or `E`)")
                raw = st.text_area("Leaderboard data", height=300, key="manual_lb")
                if st.button("Save Snapshot", type="primary"):
                    if not raw.strip():
                        st.error("Please paste leaderboard data.")
                    else:
                        players = {}
                        for line in raw.strip().split("\n"):
                            parts = line.split("\t")
                            if len(parts) < 2:
                                continue
                            name = parts[0].strip()
                            score_str = parts[1].strip()
                            if score_str == "E":
                                score_val = 0
                            else:
                                score_val = int(score_str.replace("+", ""))
                            players[name] = {"score": score_val, "score_str": score_str}

                        sorted_players = sorted(players.items(), key=lambda x: x[1]["score"])
                        pos = 1
                        i = 0
                        while i < len(sorted_players):
                            j = i
                            while j < len(sorted_players) and sorted_players[j][1]["score"] == sorted_players[i][1]["score"]:
                                j += 1
                            for k in range(i, j):
                                name, data = sorted_players[k]
                                order = i + 1
                                tied = j - i > 1
                                sorted_players[k] = (name, {
                                    "order": order,
                                    "score": data["score_str"],
                                    "rounds": [],
                                })
                            i = j

                        final_players = {name: data for name, data in sorted_players}

                        sb.table("leaderboard_snapshots").upsert({
                            "tournament_id": tournament_id,
                            "event_name": config["name"],
                            "status": "Final",
                            "players": final_players,
                        }, on_conflict="tournament_id").execute()

                        leaderboard = {
                            "event_name": config["name"],
                            "status": "Final",
                            "total_players": len(final_players),
                            "completed": True,
                            "players": final_players,
                            "round": 4,
                        }
                        st.success("Leaderboard saved!")
                        st.rerun()

            if not snapshot:
                st.stop()

    sb = get_sb()
    picks_list = sb.table("picks").select("*").eq("tournament_id", tournament_id).execute().data
    if not picks_list:
        st.info("No picks submitted yet.")
        st.stop()

    results = calculate_pool_scores(picks_list, leaderboard, config["rules"])
    st.subheader("Pool Standings")

    for r in results:
        with st.expander(f"**#{r['rank']} {r['participant_name']}** — {r['score']} pts", expanded=False):
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**Win Picks**")
                for pick in r["picks"]:
                    if pick["type"] == "win":
                        label = f"- {pick['name']}: **{pick['result']}** ({pick['points']} pts)"
                        if pick.get("captain"):
                            label += " 👑"
                        st.markdown(label)
            with cols[1]:
                st.markdown("**Short Picks**")
                for pick in r["picks"]:
                    if pick["type"] == "short":
                        st.markdown(f"- {pick['name']}: **{pick['result']}** ({pick['points']} pts)")

    st.divider()
    st.subheader("ESPN Leaderboard")

    sorted_items = sorted(leaderboard["players"].items(), key=lambda x: x[1]["order"])
    cur_round = leaderboard["round"]
    cut_line = config["rules"].get("cut_line", 60)
    made_cut = _compute_made_cut(leaderboard["players"], cut_line)
    max_round = max(
        (r["number"] for _, d in sorted_items for r in d.get("rounds", []) if not r["dnp"]),
        default=cur_round,
    )

    positions = {}
    i = 0
    while i < len(sorted_items):
        score = sorted_items[i][1]["score"]
        j = i
        while j < len(sorted_items) and sorted_items[j][1]["score"] == score:
            j += 1
        tied = j - i > 1
        for k in range(i, j):
            positions[k] = f"T{i + 1}" if tied else str(i + 1)
        i = j

    rounds_to_show = [rn for rn in range(1, max_round + 1) if rn != cur_round]

    rows = []
    for idx, (name, d) in enumerate(sorted_items):
        pos = positions[idx]
        if name not in made_cut:
            pos = f"{pos} MC"
        row = {"Pos": pos, "Player": name, "To Par": d["score"]}
        round_map = {r["number"]: r for r in d.get("rounds", [])}
        cur = round_map.get(cur_round)
        if cur is None:
            row[f"R{cur_round}"] = ""
        elif cur["dnp"]:
            row[f"R{cur_round}"] = "—"
        elif cur["complete"]:
            row[f"R{cur_round}"] = str(cur["strokes"])
        else:
            row[f"R{cur_round}"] = f"thru {cur['holes_completed']}"
        for rn in rounds_to_show:
            r = round_map.get(rn)
            if r is None:
                row[f"R{rn}"] = "NA"
            elif r["dnp"]:
                row[f"R{rn}"] = "—"
            elif r["complete"]:
                row[f"R{rn}"] = str(r["strokes"])
            else:
                row[f"R{rn}"] = f"thru {r['holes_completed']}"
        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
