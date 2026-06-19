import streamlit as st
from supabase import create_client


def get_client():
    """Get or create a cached Supabase client."""
    if "supabase" not in st.session_state:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        st.session_state.supabase = create_client(url, key)
    return st.session_state.supabase


def get_tournaments():
    """Fetch all tournaments."""
    sb = get_client()
    result = sb.table("tournaments").select("*").execute()
    return result.data


def get_tournament(tournament_id):
    """Fetch a single tournament by ID."""
    sb = get_client()
    result = sb.table("tournaments").select("*").eq("id", tournament_id).execute()
    return result.data[0] if result.data else None


def verify_pool_code(tournament_id, code):
    """Verify a pool code matches the tournament."""
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return False
    return tournament.get("pool_code") == code


def submit_picks(tournament_id, participant_name, win_picks, short_picks):
    """Submit or update picks for a participant."""
    sb = get_client()
    sb.table("picks").upsert({
        "tournament_id": tournament_id,
        "participant_name": participant_name,
        "win_picks": win_picks,
        "short_picks": short_picks,
    }, on_conflict="tournament_id,participant_name").execute()


def get_picks(tournament_id):
    """Fetch all picks for a tournament."""
    sb = get_client()
    result = sb.table("picks").select("*").eq("tournament_id", tournament_id).execute()
    return result.data


def get_pick(tournament_id, participant_name):
    """Fetch a specific participant's picks."""
    sb = get_client()
    result = (
        sb.table("picks")
        .select("*")
        .eq("tournament_id", tournament_id)
        .eq("participant_name", participant_name)
        .execute()
    )
    return result.data[0] if result.data else None
