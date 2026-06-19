import streamlit as st
from utils.config import render_tournament_selector

st.set_page_config(
    page_title="Wasylak Golf Pools App",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded",
)

config = render_tournament_selector()

st.title("⛳ Wasylak Golf Pools App")

st.markdown("---")

if config:
    st.markdown(f"### {config['name']}")

st.markdown("""
Navigate using the sidebar:

- **Rules** — How the pool works
- **Make Picks** — Submit your win and short picks
- **Scoreboard** — Live leaderboard and pool standings
""")

st.info("Pool code is required to submit picks. Get it from your pool host!")
