import json
import streamlit as st
from pathlib import Path
from utils.config import render_tournament_selector, require_tournament
from utils.database import get_tournaments, verify_pool_code, submit_picks, get_pick

st.set_page_config(page_title="Make Picks", page_icon="🏌️", layout="wide")

render_tournament_selector()

st.title("🏌️ Make Your Picks")
st.divider()

tournament_id = st.session_state.get("selected_tournament_id")
config = require_tournament()

tournaments = get_tournaments()
if not tournaments:
    st.warning("No active tournaments found. Contact your pool host.")
    st.stop()

tournament = next((t for t in tournaments if t["id"] == tournament_id), None)
if tournament is None:
    st.warning("Tournament not found in database.")
    st.stop()

if tournament.get("status") in ("locked", "final"):
    st.warning("This tournament is locked. Picks can no longer be submitted or edited.")
    st.stop()

CONFIG_DIR = Path(__file__).parent.parent / "data" / "tournaments"
config_path = CONFIG_DIR / f"{tournament_id}.json"
if not config_path.exists():
    st.error("Tournament configuration not found.")
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
        elif verify_pool_code(tournament_id, pool_code):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid pool code.")
    st.stop()

participant_name = st.session_state.participant_name
st.success(f"Welcome, **{participant_name}**!")

existing = get_pick(tournament_id, participant_name)
existing_win = existing["win_picks"] if existing else []
existing_short = existing["short_picks"] if existing else []

rules = config["rules"]
groups = config["player_groups"]
all_players = []
for g_players in groups.values():
    for p in g_players:
        if p["name"] not in all_players:
            all_players.append(p["name"])
all_players.sort()

win_picks = []
st.subheader("Win Picks")

for group_num, count in rules["win_picks_per_group"].items():
    group_player_names = [p["name"] for p in groups[group_num]]
    defaults = [p for p in existing_win if p in group_player_names]

    selected = st.multiselect(
        f"Group {group_num} — Pick {count} to WIN",
        group_player_names,
        default=defaults,
        key=f"win_group_{group_num}",
    )

    if len(selected) > count:
        st.error(f"Too many picks for Group {group_num}. You can only pick {count}.")
    elif len(selected) < count:
        st.warning(f"Select {count - len(selected)} more from Group {group_num}.")

    win_picks.extend(selected)

short_defaults = [p for p in existing_short if p in all_players]
short_picks = st.multiselect(
    f"Short Picks — Pick {rules['short_picks']} to LOSE (any player from full field)",
    all_players,
    default=short_defaults,
    key="short_picks",
)

if len(short_picks) > rules["short_picks"]:
    st.error(f"Too many short picks. You can only pick {rules['short_picks']}.")
elif len(short_picks) < rules["short_picks"]:
    st.warning(f"Select {rules['short_picks'] - len(short_picks)} more short pick(s).")

expected_total = sum(rules["win_picks_per_group"].values()) + rules["short_picks"]
current_total = len(win_picks) + len(short_picks)

st.divider()

if current_total == expected_total and len(set(win_picks)) == len(win_picks) and len(set(short_picks)) == len(short_picks):
    if not set(win_picks) & set(short_picks):
        if st.button("Submit Picks", type="primary"):
            submit_picks(tournament_id, participant_name, win_picks, short_picks)
            st.success("Picks submitted successfully!")
            st.balloons()
    else:
        st.error("A player cannot be both a win pick and a short pick.")
else:
    st.info(f"Complete all {expected_total} picks to submit.")
