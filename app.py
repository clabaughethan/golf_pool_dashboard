import streamlit as st
from utils.config import load_tournament_configs

st.set_page_config(
    page_title="Wasylak Golf Pools App",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("⛳ Wasylak Golf Pools App")

st.markdown("---")

configs = load_tournament_configs()

if not configs:
    st.warning("No tournament configurations found.")
    st.stop()

tournament_names = {c["name"]: cid for cid, c in configs.items()}
selected_name = st.selectbox("Select Tournament", list(tournament_names.keys()))
selected_id = tournament_names[selected_name]

st.session_state.selected_tournament_id = selected_id
st.session_state.selected_tournament_config = configs[selected_id]

st.markdown(f"### {selected_name}")

st.markdown("""
Navigate using the sidebar:

- **Rules** — How the pool works
- **Make Picks** — Submit your win and short picks
- **Scoreboard** — Live leaderboard and pool standings
""")

st.info("Pool code is required to submit picks. Get it from your pool host!")
