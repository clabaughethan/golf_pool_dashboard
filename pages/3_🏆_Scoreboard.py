import json
import streamlit as st
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
from utils.config import render_tournament_selector, require_tournament
from utils.database import get_tournaments, get_picks
from utils.espn_api import fetch_leaderboard
from utils.scoring import calculate_pool_scores

st.set_page_config(page_title="Scoreboard", page_icon="🏆", layout="wide")

render_tournament_selector()

st.title("🏆 Live Scoreboard")
st.divider()

tournament_id = st.session_state.get("selected_tournament_id")
config = require_tournament()

tournaments = get_tournaments()
if not tournaments:
    st.warning("No active tournaments found.")
    st.stop()

tournament = next((t for t in tournaments if t["id"] == tournament_id), None)

st_autorefresh(interval=120_000, key="leaderboard_refresh")

try:
    leaderboard = fetch_leaderboard()
except Exception as e:
    st.error(f"Could not fetch live scores: {e}")
    st.stop()

status = leaderboard["status"]
round_num = leaderboard["round"]
completed = leaderboard["completed"]

st.subheader(f"{leaderboard['event_name']} — {status}")

picks_list = get_picks(tournament_id)
if not picks_list:
    st.info("No picks submitted yet.")
    st.stop()

results = calculate_pool_scores(picks_list, leaderboard)

st.subheader("Pool Standings")

for r in results:
    with st.expander(
        f"**#{r['rank']} {r['participant_name']}** — {r['score']} pts",
        expanded=(r["rank"] <= 3),
    ):
        cols = st.columns(2)

        with cols[0]:
            st.markdown("**Win Picks**")
            for pick in r["picks"]:
                if pick["type"] == "win":
                    st.markdown(
                        f"- {pick['name']}: **{pick['result']}** ({pick['points']} pts)"
                    )

        with cols[1]:
            st.markdown("**Short Picks**")
            for pick in r["picks"]:
                if pick["type"] == "short":
                    st.markdown(
                        f"- {pick['name']}: **{pick['result']}** ({pick['points']} pts)"
                    )

st.divider()
st.subheader("ESPN Leaderboard")

players_sorted = sorted(
    leaderboard["players"].items(), key=lambda x: x[1]["order"]
)

espn_cols = st.columns([1, 3, 1, 1])
with espn_cols[0]:
    st.markdown("**Pos**")
with espn_cols[1]:
    st.markdown("**Player**")
with espn_cols[2]:
    st.markdown("**Score**")
with espn_cols[3]:
    st.markdown("**Rounds**")

for name, data in players_sorted:
    cols = st.columns([1, 3, 1, 1])
    with cols[0]:
        st.text(str(data["order"]))
    with cols[1]:
        st.text(name)
    with cols[2]:
        st.text(data["score"])
    with cols[3]:
        st.text(str(data["rounds_completed"]))

st.caption("Auto-refreshes every 2 minutes during tournament hours.")
