import streamlit as st

config = st.session_state.get("selected_tournament_config")

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
