-- Add captain_pick column to picks table for The Open Championship
ALTER TABLE picks ADD COLUMN IF NOT EXISTS captain_pick TEXT;

-- Verify it was added
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'picks' AND column_name = 'captain_pick';
