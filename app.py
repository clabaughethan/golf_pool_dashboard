import json
from datetime import datetime, timezone
import streamlit as st
import requests
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
from supabase import create_client
from utils.scoring import calculate_pool_scores
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
[data-testid="stHorizontalBlock"] {
    overflow-x: auto;
    flex-wrap: nowrap !important;
}
[data-testid="stHorizontalBlock"] > div {
    min-width: 0;
    flex: 1 1 0;
}
[data-testid="stHorizontalBlock"] p,
[data-testid="stHorizontalBlock"] span {
    white-space: nowrap;
    font-size: 0.82rem;
    overflow: hidden;
    text-overflow: ellipsis;
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

nav_items = [("📋 Rules", "Rules"), ("🏌️ Make Picks", "Make Picks"), ("🏆 Leaderboard", "Leaderboard")]
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

    all_tournaments = get_sb().table("tournaments").select("*").execute().data
    tournament = next((t for t in all_tournaments if t["id"] == selected_id), None)
    status = tournament.get("status", "open") if tournament else "open"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", status.capitalize())
    with col2:
        st.metric("Participants", participant_count)
    with col3:
        st.metric("Entry Fee", "$20")

    st.markdown("---")
    st.subheader("How It Works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**1. Make Your Picks**")
        st.markdown("Select 8 win picks and 2 short picks. Enter the pool code to submit.")
    with col2:
        st.markdown("**2. Tournament Starts**")
        st.markdown("Picks lock at the first tee time. No changes after that.")
    with col3:
        st.markdown("**3. Live Scoring**")
        st.markdown("Standings update automatically from ESPN every 2 minutes.")

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

    rows = []
    for g, count in win_groups.items():
        rows.append(f"| Players to **WIN** | {count} from Group {g} |")
    if short_count:
        rows.append(f"| Players to **SHORT** (lose) | {short_count} | Full field (any group) |")
    st.markdown("\n".join([
        "| Selection | # of Picks | From |",
        "|-----------|------------|------|",
    ] + rows))

    st.subheader("Scoring (Least Points Wins)")
    scoring_rows = []
    scoring_rows.append("| **Win pick** finishes in position X | X points (1st = 1 pt, 27th = 27 pts, etc.) |")
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
    if short_count:
        st.markdown("- Short picks are **not** group-restricted — you can short anyone in the field.")
    st.markdown("- Picks are locked once the tournament begins.")
    st.markdown("- Submit your picks on the **Make Picks** page using your pool code.")

    st.divider()
    st.subheader("Player Groups")
    for group_num, players in groups.items():
        with st.expander(f"Group {group_num} ({len(players)} players)"):
            for p in players:
                owgr = str(p.get("owgr")) if p.get("owgr") else "N/A"
                st.text(f"  {p['name']:30s}  OWGR: {owgr:>6s}  Odds: {p['odds']}")

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
            st.error(f"Too many picks for Group {group_num}. You can only pick {count}.")
        elif len(selected) < count:
            st.warning(f"Select {count - len(selected)} more from Group {group_num}.")
        win_picks.extend(selected)

    short_defaults = [p for p in existing_short if p in all_player_names]
    short_picks = st.multiselect(
        f"Short Picks — Pick {rules['short_picks']} to LOSE",
        all_player_names,
        default=short_defaults,
        key="short",
        format_func=lambda n: all_player_labels.get(n, n),
    )
    if len(short_picks) > rules["short_picks"]:
        st.error(f"Too many short picks. You can only pick {rules['short_picks']}.")
    elif len(short_picks) < rules["short_picks"]:
        st.warning(f"Select {rules['short_picks'] - len(short_picks)} more.")

    expected = sum(rules["win_picks_per_group"].values()) + rules["short_picks"]
    current = len(win_picks) + len(short_picks)

    st.divider()
    if current == expected and len(set(win_picks)) == len(win_picks) and len(set(short_picks)) == len(short_picks):
        if not set(win_picks) & set(short_picks):
            if st.button("Submit Picks", type="primary"):
                sb.table("picks").upsert({
                    "tournament_id": tournament_id,
                    "participant_name": participant_name,
                    "win_picks": win_picks,
                    "short_picks": short_picks,
                }, on_conflict="tournament_id,participant_name").execute()
                st.success("Picks submitted successfully!")
                st.balloons()
        else:
            st.error("A player cannot be both a win pick and a short pick.")
    else:
        st.info(f"Complete all {expected} picks to submit.")

elif page == "Leaderboard":
    tournament_id = selected_id

    st.title("🏆 Live Leaderboard")
    st.divider()

    sb = get_sb()

    snapshot = sb.table("leaderboard_snapshots").select("*").eq("tournament_id", tournament_id).execute().data
    if snapshot:
        snap = snapshot[0]
        leaderboard = {
            "event_name": snap["event_name"],
            "status": snap["status"],
            "total_players": len(snap["players"]),
            "completed": True,
            "players": snap["players"],
        }
        st.subheader(f"{leaderboard['event_name']} — {leaderboard['status']}")
    else:
        try:
            leaderboard = fetch_leaderboard()
            live = True
        except Exception:
            live = False

        if live:
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

    results = calculate_pool_scores(picks_list, leaderboard)
    st.subheader("Pool Standings")

    for r in results:
        with st.expander(f"**#{r['rank']} {r['participant_name']}** — {r['score']} pts", expanded=False):
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**Win Picks**")
                for pick in r["picks"]:
                    if pick["type"] == "win":
                        st.markdown(f"- {pick['name']}: **{pick['result']}** ({pick['points']} pts)")
            with cols[1]:
                st.markdown("**Short Picks**")
                for pick in r["picks"]:
                    if pick["type"] == "short":
                        st.markdown(f"- {pick['name']}: **{pick['result']}** ({pick['points']} pts)")

    st.divider()
    st.subheader("ESPN Leaderboard")

    sorted_items = sorted(leaderboard["players"].items(), key=lambda x: x[1]["order"])
    cur_round = leaderboard["round"]
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

    col_w = [1, 2.5, 1, 1.2] + [1.2] * len(rounds_to_show)
    cols = st.columns(col_w)
    with cols[0]: st.text("Pos")
    with cols[1]: st.text("Player")
    with cols[2]: st.text("To Par")
    with cols[3]: st.text(f"R{cur_round}")
    for i, rn in enumerate(rounds_to_show):
        with cols[4 + i]: st.text(f"R{rn}")
    st.divider()

    for idx, (name, d) in enumerate(sorted_items):
        cols = st.columns(col_w)
        with cols[0]: st.text(positions[idx])
        with cols[1]: st.text(name)
        with cols[2]: st.text(d["score"])
        round_map = {r["number"]: r for r in d.get("rounds", [])}
        cur = round_map.get(cur_round)
        with cols[3]:
            if cur is None:
                st.text("")
            elif cur["dnp"]:
                st.text("—")
            elif cur["complete"]:
                st.text(str(cur["strokes"]))
            else:
                st.text(f"thru {cur['holes_completed']}")
        for i, rn in enumerate(rounds_to_show):
            r = round_map.get(rn)
            with cols[4 + i]:
                if r is None:
                    st.text("NA")
                elif r["dnp"]:
                    st.text("—")
                elif r["complete"]:
                    st.text(str(r["strokes"]))
                else:
                    st.text(f"thru {r['holes_completed']}")
