import streamlit as st

st.set_page_config(
    page_title="Golf Pool Dashboard",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("⛳ Golf Pool Dashboard")

st.markdown("---")

st.markdown("""
### Welcome

Navigate using the sidebar:

- **Rules** — How the pool works
- **Make Picks** — Submit your win and short picks
- **Scoreboard** — Live leaderboard and pool standings
""")

st.info("Pool code is required to submit picks. Get it from your pool host!")
