import json
import streamlit as st
import requests
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
from supabase import create_client
from utils.scoring import calculate_pool_scores
from utils.config import load_tournament_configs

st.set_page_config(page_title="Wasylak Golf Pools App", page_icon="⛳", layout="wide", initial_sidebar_state="expanded")

configs = load_tournament_configs()
tournament_names = {c["name"]: cid for cid, c in configs.items()}
name_list = list(tournament_names.keys())

current_id = st.session_state.get("selected_tournament_id")
current_index = name_list.index(next((n for n, tid in tournament_names.items() if tid == current_id), name_list[0])) if current_id else 0

active_home = (st.session_state.get("page", "Home") == "Home")
if st.sidebar.button("🏠 Home", key="nav_Home", use_container_width=True, disabled=active_home):
    st.session_state.page = "Home"
    st.rerun()

selected_name = st.sidebar.selectbox("Tournament", name_list, index=current_index)
selected_id = tournament_names[selected_name]
st.session_state.selected_tournament_id = selected_id
st.session_state.selected_tournament_config = configs[selected_id]

st.sidebar.divider()
st.sidebar.markdown("**Pages**")

nav_items = [("📋 Rules", "Rules"), ("🏌️ Make Picks", "Make Picks"), ("🏆 Scoreboard", "Scoreboard")]
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
    st.markdown("""
Navigate using the sidebar:

- **Rules** — How the pool works
- **Make Picks** — Submit your win and short picks
- **Scoreboard** — Live leaderboard and pool standings
""")
    st.info("Pool code is required to submit picks. Get it from your pool host!")

elif page == "Rules":
    st.title("📋 Pool Rules")
    st.header(config["name"])
    st.divider()

    rules = config["rules"]
    groups = config["player_groups"]

    st.subheader("How to Pick")
    st.markdown("""
| Selection | # of Picks | From |
|-----------|------------|------|
| Players to **WIN** | 2 each from Groups 1, 2, and 3 | (6 total) |
| Players to **WIN** | 1 each from Groups 4 and 5 | (2 total) |
| Players to **SHORT** (lose) | 2 | Full field (any group) |
""")

    st.subheader("Scoring (Least Points Wins)")
    st.markdown("""
| Scenario | Points |
|----------|--------|
| **Win pick** finishes in position X | X points (1st = 1 pt, 27th = 27 pts, etc.) |
| **Win pick** misses the cut | 75 points |
| **Short pick** finishes X from last | X points (last = 1 pt, 30th-to-last = 30 pts, etc.) |
| **Short pick** not in bottom 75 after Day 2 | 75 points |
| **WD or DQ** (any pick) | 75 points |
""")

    st.subheader("Key Notes")
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

    def get_sb():
        if "supabase" not in st.session_state:
            st.session_state.supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
        return st.session_state.supabase

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
    all_players = sorted(set(p["name"] for g in groups.values() for p in g))

    win_picks = []
    st.subheader("Win Picks")
    for group_num, count in rules["win_picks_per_group"].items():
        group_names = [p["name"] for p in groups[group_num]]
        defaults = [p for p in existing_win if p in group_names]
        selected = st.multiselect(f"Group {group_num} — Pick {count} to WIN", group_names, default=defaults, key=f"win_{group_num}")
        if len(selected) > count:
            st.error(f"Too many picks for Group {group_num}. You can only pick {count}.")
        elif len(selected) < count:
            st.warning(f"Select {count - len(selected)} more from Group {group_num}.")
        win_picks.extend(selected)

    short_defaults = [p for p in existing_short if p in all_players]
    short_picks = st.multiselect(f"Short Picks — Pick {rules['short_picks']} to LOSE", all_players, default=short_defaults, key="short")
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

elif page == "Scoreboard":
    tournament_id = selected_id

    def get_sb():
        if "supabase" not in st.session_state:
            st.session_state.supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
        return st.session_state.supabase

    st.title("🏆 Live Scoreboard")
    st.divider()
    st_autorefresh(interval=120_000, key="refresh")

    try:
        resp = requests.get("https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        event = data["events"][0]
        competition = event["competitions"][0]
        competitors = competition["competitors"]

        players = {}
        for c in competitors:
            linescores = c.get("linescores", [])
            rounds = sum(1 for r in linescores if r.get("displayValue") and r["displayValue"] != "-")
            players[c["athlete"]["displayName"]] = {"order": c["order"], "score": c["score"], "rounds_completed": rounds}

        leaderboard = {
            "event_name": event["name"],
            "status": competition["status"]["type"]["detail"],
            "total_players": len(competitors),
            "completed": event["status"]["type"].get("completed", False),
            "players": players,
        }
    except Exception as e:
        st.error(f"Could not fetch live scores: {e}")
        st.stop()

    st.subheader(f"{leaderboard['event_name']} — {leaderboard['status']}")

    sb = get_sb()
    picks_list = sb.table("picks").select("*").eq("tournament_id", tournament_id).execute().data
    if not picks_list:
        st.info("No picks submitted yet.")
        st.stop()

    results = calculate_pool_scores(picks_list, leaderboard)
    st.subheader("Pool Standings")

    for r in results:
        with st.expander(f"**#{r['rank']} {r['participant_name']}** — {r['score']} pts", expanded=(r["rank"] <= 3)):
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
    sorted_players = sorted(leaderboard["players"].items(), key=lambda x: x[1]["order"])
    for name, d in sorted_players:
        cols = st.columns([1, 3, 1, 1])
        with cols[0]: st.text(str(d["order"]))
        with cols[1]: st.text(name)
        with cols[2]: st.text(d["score"])
        with cols[3]: st.text(str(d["rounds_completed"]))
    st.caption("Auto-refreshes every 2 minutes.")
