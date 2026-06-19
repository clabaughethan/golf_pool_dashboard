import json
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Rules", page_icon="📋", layout="wide")

st.title("📋 Pool Rules")

CONFIG_DIR = Path(__file__).parent.parent / "data" / "tournaments"
configs = sorted(CONFIG_DIR.glob("*.json"))

if not configs:
    st.warning("No tournament configurations found.")
    st.stop()

tournament_options = {json.loads(c.read_text())["name"]: c.stem for c in configs}
selected_name = st.selectbox("Select Tournament", list(tournament_options.keys()))
config = json.loads((CONFIG_DIR / f"{tournament_options[selected_name]}.json").read_text())

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
