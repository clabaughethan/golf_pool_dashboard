# Wasylak Golf Pools

A Streamlit-based golf pool dashboard for managing picks, live ESPN scoring, and leaderboard tracking across multiple tournaments.

## Features

- **Pool code authentication** — participants enter a shared code + name to submit picks
- **Manual sidebar navigation** — emoji buttons for Home, Rules, Make Picks, and Leaderboard
- **Live ESPN scoring** — auto-refreshes every 2 minutes during play
- **Multiple tournament support** — different rules and scoring per tournament
- **Tournament lock** — picks auto-lock based on the first tee time
- **Leaderboard snapshots** — saves final results when a tournament completes
- **Mobile-friendly** — responsive sidebar and horizontal-scroll leaderboard

## Tech Stack

- **Frontend:** Streamlit
- **Database:** Supabase (PostgreSQL)
- **Scoring API:** ESPN public leaderboard API
- **Hosting:** Streamlit Cloud

## Project Structure

```
golf_pool_dashboard/
├── app.py                    # Main Streamlit app (all pages + sidebar)
├── utils/
│   ├── config.py             # Tournament config loader + sidebar selector
│   ├── database.py           # Supabase client wrapper
│   ├── espn_api.py           # ESPN leaderboard fetcher
│   └── scoring.py            # Pool scoring engine
├── data/tournaments/
│   ├── us_open_2026.json     # US Open player groups + rules
│   └── masters_2026.json     # Masters player groups + rules
├── .streamlit/
│   ├── config.toml           # Theme + server settings
│   └── secrets_template.toml # Supabase credentials template
├── setup_supabase.sql        # Database schema + RLS policies
└── requirements.txt          # Python dependencies
```

## Setup

1. **Supabase:** Create a free project at [supabase.com](https://supabase.com) and run `setup_supabase.sql` in the SQL Editor
2. **Secrets:** Copy `.streamlit/secrets_template.toml` to `.streamlit/secrets.toml` and fill in your Supabase URL and anon key
3. **Run locally:**
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Tournament Config

Tournament configs are JSON files in `data/tournaments/`. Each contains:

```json
{
  "id": "us-open-2026",
  "name": "2026 US Open",
  "event_id": "401580349",
  "pool_code": "USOPEN2026",
  "player_groups": { ... },
  "rules": {
    "win_picks_per_group": {"1": 2, "2": 2, "3": 2, "4": 1, "5": 1},
    "short_picks": 2,
    "missed_cut_points": 75,
    "wd_dq_points": 75,
    "short_not_bottom_75_points": 75
  }
}
```

## Scoring

Scoring rules vary by tournament and are defined in each tournament's JSON config. Common patterns:

- **Win picks** score their finishing position (1st = 1 pt, 27th = 27 pts)
- **Short picks** score distance from last (last = 1 pt, 30th-to-last = 30 pts)
- **Missed cut, WD, or DQ** = 75 points
- **Short pick not in bottom 75 after Day 2** = 75 points (if applicable)

See each tournament's config in `data/tournaments/` for exact rules. Lowest total score wins.

## Adding a New Tournament

1. Create a new JSON file in `data/tournaments/`
2. Add the tournament to the `tournaments` table in Supabase
3. Import player groups via SQL INSERT
