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

page = st.sidebar.radio(
    "Go to",
    ["Home", "Rules", "Make Picks", "Scoreboard"],
    label_visibility="collapsed",
)

if page == "Home":
    st.title("⛳ Wasylak Golf Pools App")
    st.markdown("---")
    st.markdown(f"### {configs[selected_id]['name']}")
    st.markdown("""
Navigate using the sidebar:

- **Rules** — How the pool works
- **Make Picks** — Submit your win and short picks
- **Scoreboard** — Live leaderboard and pool standings
""")
    st.info("Pool code is required to submit picks. Get it from your pool host!")

elif page == "Rules":
    from views.rules import render
    render()

elif page == "Make Picks":
    from views.picks import render
    render()

elif page == "Scoreboard":
    from views.scoreboard import render
    render()
