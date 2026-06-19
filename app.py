import streamlit as st
from utils.config import load_tournament_configs

st.set_page_config(
    page_title="Wasylak Golf Pools App",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded",
)

configs = load_tournament_configs()
tournament_names = {c["name"]: cid for cid, c in configs.items()}
name_list = list(tournament_names.keys())

current_id = st.session_state.get("selected_tournament_id")
current_index = name_list.index(
    next((n for n, tid in tournament_names.items() if tid == current_id), name_list[0])
) if current_id else 0

selected_name = st.sidebar.selectbox(
    "Tournament",
    name_list,
    index=current_index,
)
selected_id = tournament_names[selected_name]
st.session_state.selected_tournament_id = selected_id
st.session_state.selected_tournament_config = configs[selected_id]

st.sidebar.divider()

home_page = st.Page("pages/0_🏠_Home.py", title="Home", icon="🏠", url_path="home", default=True)
rules_page = st.Page("pages/1_📋_Rules.py", title="Rules", icon="📋", url_path="rules")
picks_page = st.Page("pages/2_🏌️_Make_Picks.py", title="Make Picks", icon="🏌️", url_path="make-picks")
scoreboard_page = st.Page("pages/3_🏆_Scoreboard.py", title="Scoreboard", icon="🏆", url_path="scoreboard")

nav = st.navigation([home_page, rules_page, picks_page, scoreboard_page])
nav.run()
