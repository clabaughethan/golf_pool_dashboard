-- Supabase SQL Setup Script
-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard)
-- Safe to re-run (idempotent)

-- Tournaments table
CREATE TABLE IF NOT EXISTS tournaments (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  pool_code TEXT NOT NULL,
  status TEXT DEFAULT 'open',
  player_groups JSONB NOT NULL,
  rules JSONB NOT NULL,
  event_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Leaderboard snapshots table
CREATE TABLE IF NOT EXISTS leaderboard_snapshots (
  tournament_id TEXT PRIMARY KEY,
  event_name TEXT NOT NULL,
  status TEXT NOT NULL,
  players JSONB NOT NULL
);

-- Picks table
CREATE TABLE IF NOT EXISTS picks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tournament_id TEXT REFERENCES tournaments(id),
  participant_name TEXT NOT NULL,
  win_picks JSONB NOT NULL,
  short_picks JSONB NOT NULL,
  captain_pick TEXT,
  submitted_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(tournament_id, participant_name)
);

-- Enable Row Level Security (RLS)
ALTER TABLE tournaments ENABLE ROW LEVEL SECURITY;
ALTER TABLE picks ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist, then recreate
DROP POLICY IF EXISTS "Allow public read access on tournaments" ON tournaments;
DROP POLICY IF EXISTS "Allow public read access on picks" ON picks;
DROP POLICY IF EXISTS "Allow authenticated insert on picks" ON picks;
DROP POLICY IF EXISTS "Allow authenticated update on picks" ON picks;
DROP POLICY IF EXISTS "Allow public delete on picks" ON picks;

-- Policies: allow anonymous read access, authenticated write
CREATE POLICY "Allow public read access on tournaments"
  ON tournaments FOR SELECT
  USING (true);

CREATE POLICY "Allow public read access on picks"
  ON picks FOR SELECT
  USING (true);

CREATE POLICY "Allow authenticated insert on picks"
  ON picks FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow authenticated update on picks"
  ON picks FOR UPDATE
  USING (true);

CREATE POLICY "Allow public delete on picks"
  ON picks FOR DELETE
  USING (true);

-- RLS for leaderboard_snapshots
ALTER TABLE leaderboard_snapshots ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read access on leaderboard_snapshots" ON leaderboard_snapshots;
DROP POLICY IF EXISTS "Allow public upsert on leaderboard_snapshots" ON leaderboard_snapshots;
CREATE POLICY "Allow public read access on leaderboard_snapshots"
  ON leaderboard_snapshots FOR SELECT USING (true);
CREATE POLICY "Allow public upsert on leaderboard_snapshots"
  ON leaderboard_snapshots FOR INSERT WITH CHECK (true);

-- Insert the US Open 2026 tournament
INSERT INTO tournaments (id, name, pool_code, status, player_groups, rules)
VALUES (
  'us-open-2026',
  '2026 US Open',
  'USOPEN2026',
  'open',
  '[]'::jsonb,
  '{
    "win_picks_per_group": {"1": 2, "2": 2, "3": 2, "4": 1, "5": 1},
    "short_picks": 2,
    "missed_cut_points": 75,
    "wd_dq_points": 75,
    "short_not_bottom_75_points": 75
  }'::jsonb
)
ON CONFLICT (id) DO NOTHING;

-- Insert The Open Championship 2026 tournament
INSERT INTO tournaments (id, name, pool_code, status, player_groups, rules)
VALUES (
  'the-open-2026',
  '2026 The Open Championship',
  'OPEN2026',
  'open',
  '[]'::jsonb,
  '{
    "win_picks_per_group": {"1": 2, "2": 2, "3": 2, "4": 2, "5": 2},
    "short_picks": 0,
    "captain_pick": true,
    "captain_pick_multiplier": 2,
    "missed_cut_points": 75,
    "wd_dq_points": 75,
    "short_not_bottom_75_points": 75,
    "cut_line": 60
  }'::jsonb
)
ON CONFLICT (id) DO NOTHING;
