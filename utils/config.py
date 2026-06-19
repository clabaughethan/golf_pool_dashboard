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


def get_current_tournament():
    """Get the currently selected tournament config from session state."""
    return st.session_state.get("selected_tournament_config")


def require_tournament():
    """Stop the page if no tournament is selected."""
    config = get_current_tournament()
    if config is None:
        st.warning("Select a tournament on the home page first.")
        st.stop()
    return config
