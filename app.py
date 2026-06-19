import streamlit as st

st.set_page_config(
    page_title="Wasylak Golf Pools App",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("⛳ Wasylak Golf Pools App")

st.markdown("---")

st.markdown("""
### Welcome

Navigate using the sidebar:

- **Rules** — How the pool works
- **Make Picks** — Submit your win and short picks
- **Scoreboard** — Live leaderboard and pool standings
""")

st.info("Pool code is required to submit picks. Get it from your pool host!")
