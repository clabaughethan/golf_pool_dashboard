import json
import streamlit as st
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "data" / "tournaments"


def load_tournament_configs():
    """Load all tournament config files from disk."""
    configs = {}
    for path in sorted(CONFIG_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        configs[data["id"]] = data
    return configs


def render_tournament_selector():
    """Render the tournament selector in the sidebar (above page navigation)."""
    configs = load_tournament_configs()

    if not configs:
        st.sidebar.warning("No tournaments found.")
        return None

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
        key="tournament_selector",
    )
    selected_id = tournament_names[selected_name]

    st.session_state.selected_tournament_id = selected_id
    st.session_state.selected_tournament_config = configs[selected_id]

    return configs[selected_id]


def get_current_tournament():
    """Get the currently selected tournament config from session state."""
    return st.session_state.get("selected_tournament_config")


def require_tournament():
    """Stop the page if no tournament is selected."""
    config = get_current_tournament()
    if config is None:
        st.warning("Select a tournament from the sidebar.")
        st.stop()
    return config
