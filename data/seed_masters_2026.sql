-- =============================================
-- Masters 2026 - Historical Data Seed
-- =============================================

-- Insert leaderboard snapshot
INSERT INTO leaderboard_snapshots (tournament_id, event_name, status, players)
VALUES ('masters-2026', '2026 Masters', 'Final', '{"Rory McIlroy": {"order": 1, "score": "-12", "rounds": [], "made_cut": true}, "Scottie Scheffler": {"order": 2, "score": "-11", "rounds": [], "made_cut": true}, "Tyrrell Hatton": {"order": 3, "score": "-10", "rounds": [], "made_cut": true}, "Russell Henley": {"order": 3, "score": "-10", "rounds": [], "made_cut": true}, "Justin Rose": {"order": 3, "score": "-10", "rounds": [], "made_cut": true}, "Cameron Young": {"order": 3, "score": "-10", "rounds": [], "made_cut": true}, "Collin Morikawa": {"order": 7, "score": "-9", "rounds": [], "made_cut": true}, "Sam Burns": {"order": 7, "score": "-9", "rounds": [], "made_cut": true}, "Max Homa": {"order": 9, "score": "-8", "rounds": [], "made_cut": true}, "Xander Schauffele": {"order": 9, "score": "-8", "rounds": [], "made_cut": true}, "Jake Knapp": {"order": 11, "score": "-7", "rounds": [], "made_cut": true}, "Jordan Spieth": {"order": 12, "score": "-5", "rounds": [], "made_cut": true}, "Hideki Matsuyama": {"order": 12, "score": "-5", "rounds": [], "made_cut": true}, "Brooks Koepka": {"order": 12, "score": "-5", "rounds": [], "made_cut": true}, "Patrick Cantlay": {"order": 12, "score": "-5", "rounds": [], "made_cut": true}, "Patrick Reed": {"order": 12, "score": "-5", "rounds": [], "made_cut": true}, "Jason Day": {"order": 12, "score": "-5", "rounds": [], "made_cut": true}, "Maverick McNealy": {"order": 18, "score": "-4", "rounds": [], "made_cut": true}, "Viktor Hovland": {"order": 18, "score": "-4", "rounds": [], "made_cut": true}, "Matt Fitzpatrick": {"order": 18, "score": "-4", "rounds": [], "made_cut": true}, "Keegan Bradley": {"order": 21, "score": "-3", "rounds": [], "made_cut": true}, "Ludvig Aberg": {"order": 21, "score": "-3", "rounds": [], "made_cut": true}, "Wyndham Clark": {"order": 21, "score": "-3", "rounds": [], "made_cut": true}, "Adam Scott": {"order": 24, "score": "-2", "rounds": [], "made_cut": true}, "Sam Stevens": {"order": 24, "score": "-2", "rounds": [], "made_cut": true}, "Brian Campbell": {"order": 24, "score": "-2", "rounds": [], "made_cut": true}, "Michael Brennan": {"order": 24, "score": "-2", "rounds": [], "made_cut": true}, "Chris Gotterup": {"order": 24, "score": "-2", "rounds": [], "made_cut": true}, "Matt McCarty": {"order": 24, "score": "-2", "rounds": [], "made_cut": true}, "Alex Noren": {"order": 30, "score": "-1", "rounds": [], "made_cut": true}, "Harris English": {"order": 30, "score": "-1", "rounds": [], "made_cut": true}, "Shane Lowry": {"order": 30, "score": "-1", "rounds": [], "made_cut": true}, "Gary Woodland": {"order": 33, "score": "E", "rounds": [], "made_cut": true}, "Dustin Johnson": {"order": 33, "score": "E", "rounds": [], "made_cut": true}, "Brian Harman": {"order": 33, "score": "E", "rounds": [], "made_cut": true}, "Tommy Fleetwood": {"order": 33, "score": "E", "rounds": [], "made_cut": true}, "Ben Griffin": {"order": 33, "score": "E", "rounds": [], "made_cut": true}, "Jon Rahm": {"order": 38, "score": "+1", "rounds": [], "made_cut": true}, "Ryan Gerard": {"order": 38, "score": "+1", "rounds": [], "made_cut": true}, "Haotong Li": {"order": 38, "score": "+1", "rounds": [], "made_cut": true}, "Justin Thomas": {"order": 41, "score": "+2", "rounds": [], "made_cut": true}, "Jacob Bridgeman": {"order": 41, "score": "+2", "rounds": [], "made_cut": true}, "Sepp Straka": {"order": 41, "score": "+2", "rounds": [], "made_cut": true}, "Nick Taylor": {"order": 41, "score": "+2", "rounds": [], "made_cut": true}, "Kristoffer Reitan": {"order": 41, "score": "+2", "rounds": [], "made_cut": true}, "Sungjae Im": {"order": 46, "score": "+3", "rounds": [], "made_cut": true}, "Si Woo Kim": {"order": 47, "score": "+4", "rounds": [], "made_cut": true}, "Aaron Rai": {"order": 48, "score": "+5", "rounds": [], "made_cut": true}, "Corey Conners": {"order": 49, "score": "+6", "rounds": [], "made_cut": true}, "Marco Penge": {"order": 49, "score": "+6", "rounds": [], "made_cut": true}, "Kurt Kitayama": {"order": 51, "score": "+7", "rounds": [], "made_cut": true}, "Sergio Garcia": {"order": 52, "score": "+8", "rounds": [], "made_cut": true}, "Rasmus Hojgaard": {"order": 53, "score": "+10", "rounds": [], "made_cut": true}, "Charl Schwartzel": {"order": 54, "score": "+12", "rounds": [], "made_cut": true}}'::jsonb)
ON CONFLICT (tournament_id) DO UPDATE
SET event_name = EXCLUDED.event_name, status = EXCLUDED.status, players = EXCLUDED.players;

-- Insert participant picks
INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Jen Wasylak', '["Tommy Fleetwood", "Collin Morikawa", "Chris Gotterup", "Russell Henley", "J.J. Spaun", "Shane Lowry", "Ben Griffin", "Keegan Bradley", "Michael Kim", "Dustin Johnson"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Barry, Robin and Maurice', '["Scottie Scheffler", "Xander Schauffele", "Hideki Matsuyama", "Justin Rose", "Corey Conners", "J.J. Spaun", "Harris English", "Sungjae Im", "Michael Kim", "Matt McCarty"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'HappyGilmore16', '["Bryson DeChambeau", "Jon Rahm", "Justin Rose", "Patrick Reed", "Tyrrell Hatton", "Akshay Bhatia", "Harris English", "Daniel Berger", "Michael Kim", "Max Greyserman"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'JR', '["Scottie Scheffler", "Rory McIlroy", "Viktor Hovland", "Patrick Reed", "Shane Lowry", "Akshay Bhatia", "Wyndham Clark", "Cameron Smith", "Max Greyserman", "Michael Kim"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Jon Rheault', '["Jon Rahm", "Bryson DeChambeau", "Hideki Matsuyama", "Patrick Reed", "Akshay Bhatia", "Nicolai Hojgaard", "Harris English", "Daniel Berger", "Dustin Johnson", "Nico Echavarria"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Bacon', '["Scottie Scheffler", "Ludvig Aberg", "Justin Thomas", "Hideki Matsuyama", "Shane Lowry", "Tyrrell Hatton", "Cameron Smith", "Sungjae Im", "Dustin Johnson", "Carlos Ortiz"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Kevin Lobdell', '["Scottie Scheffler", "Ludvig Aberg", "Robert MacIntyre", "Patrick Reed", "Corey Conners", "Jake Knapp", "Harris English", "Gary Woodland", "Matt McCarty", "Andrew Novak"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Alex Lobdell', '["Xander Schauffele", "Tommy Fleetwood", "Patrick Reed", "Russell Henley", "Akshay Bhatia", "Jake Knapp", "Marco Penge", "Daniel Berger", "Andrew Novak", "Mason Howell"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Grant', '["Jon Rahm", "Ludvig Aberg", "Justin Rose", "Si Woo Kim", "Akshay Bhatia", "Jacob Bridgeman", "Ben Griffin", "Keegan Bradley", "Zach Johnson", "Nico Echavarria"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Timothy Paradis', '["Scottie Scheffler", "Collin Morikawa", "Justin Rose", "Hideki Matsuyama", "Patrick Cantlay", "Sepp Straka", "Cameron Smith", "Keegan Bradley", "Dustin Johnson", "Max Greyserman"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Kevin OConnor', '["Tommy Fleetwood", "Ludvig Aberg", "Justin Rose", "Jordan Spieth", "Sam Burns", "Adam Scott", "Daniel Berger", "Wyndham Clark", "Mason Howell", "Bubba Watson"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Grant 2', '["Bryson DeChambeau", "Xander Schauffele", "Robert MacIntyre", "Patrick Reed", "Jacob Bridgeman", "Nicolai Hojgaard", "Gary Woodland", "Ryan Fox", "Kristoffer Reitan", "Zach Johnson"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Drew Hubbard', '["Ludvig Aberg", "Bryson DeChambeau", "Justin Rose", "Russell Henley", "Akshay Bhatia", "Jake Knapp", "Harris English", "Gary Woodland", "Dustin Johnson", "Sami Valimaki"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Rob Malcolm', '["Jon Rahm", "Bryson DeChambeau", "Hideki Matsuyama", "Robert MacIntyre", "Nicolai Hojgaard", "Jacob Bridgeman", "Daniel Berger", "Alex Noren", "Carlos Ortiz", "Haotong Li"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Zac Rheault', '["Bryson DeChambeau", "Ludvig Aberg", "Robert MacIntyre", "Hideki Matsuyama", "Akshay Bhatia", "Nicolai Hojgaard", "Rasmus Hojgaard", "Daniel Berger", "Carlos Ortiz", "Rasmus Neergaard-Petersen"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Ben DiMichele', '["Bryson DeChambeau", "Ludvig Aberg", "Justin Rose", "Brooks Koepka", "Akshay Bhatia", "Adam Scott", "Rasmus Hojgaard", "Keegan Bradley", "Matt McCarty", "Max Greyserman"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Rob Volko', '["Bryson DeChambeau", "Ludvig Aberg", "Viktor Hovland", "Patrick Reed", "Jake Knapp", "Akshay Bhatia", "Ben Griffin", "Gary Woodland", "Nico Echavarria", "Max Greyserman"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Marty', '["Ludvig Aberg", "Bryson DeChambeau", "Justin Thomas", "Brooks Koepka", "Shane Lowry", "Patrick Cantlay", "Wyndham Clark", "Keegan Bradley", "Bubba Watson", "Dustin Johnson"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Dell', '["Scottie Scheffler", "Ludvig Aberg", "Chris Gotterup", "Robert MacIntyre", "Sepp Straka", "Akshay Bhatia", "Brian Harman", "Harris English", "Michael Kim", "Max Greyserman"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Diamond Mike', '["Tommy Fleetwood", "Bryson DeChambeau", "Justin Rose", "Hideki Matsuyama", "Patrick Cantlay", "Akshay Bhatia", "Cameron Smith", "Sungjae Im", "Haotong Li", "Charl Schwartzel"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Brian Burke', '["Jon Rahm", "Matt Fitzpatrick", "Robert MacIntyre", "Patrick Reed", "Akshay Bhatia", "Jacob Bridgeman", "Harry Hall", "Cameron Smith", "Michael Kim", "Davis Riley"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Brady Burke', '["Ludvig Aberg", "Xander Schauffele", "Si Woo Kim", "Russell Henley", "Akshay Bhatia", "Jacob Bridgeman", "Harry Hall", "Daniel Berger", "Nico Echavarria", "Carlos Ortiz"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Cam', '["Ludvig Aberg", "Cameron Young", "Hideki Matsuyama", "Jordan Spieth", "Patrick Cantlay", "Tyrrell Hatton", "Cameron Smith", "Harris English", "Dustin Johnson", "Carlos Ortiz"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Ethan Clawbaugh', '["Ludvig Aberg", "Jon Rahm", "Robert MacIntyre", "Patrick Reed", "Corey Conners", "Nicolai Hojgaard", "Daniel Berger", "Ryan Fox", "Michael Kim", "Davis Riley"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Scott DeLorme', '["Ludvig Aberg", "Cameron Young", "Hideki Matsuyama", "Robert MacIntyre", "Tyrrell Hatton", "Corey Conners", "Cameron Smith", "Sungjae Im", "Michael Kim", "Andrew Novak"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Mark DiMarzio', '["Xander Schauffele", "Jon Rahm", "Jordan Spieth", "Hideki Matsuyama", "Sam Burns", "Sepp Straka", "Marco Penge", "Rasmus Hojgaard", "Nico Echavarria", "Michael Brennan"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

INSERT INTO picks (tournament_id, participant_name, win_picks, short_picks)
VALUES ('masters-2026', 'Bill Stevens', '["Matt Fitzpatrick", "Ludvig Aberg", "Brooks Koepka", "Min Woo Lee", "Tyrrell Hatton", "Sam Burns", "Max Homa", "Cameron Smith", "Dustin Johnson", "Michael Brennan"]'::jsonb, '[]'::jsonb)
ON CONFLICT (tournament_id, participant_name) DO UPDATE
SET win_picks = EXCLUDED.win_picks, short_picks = EXCLUDED.short_picks;

-- Update tournament to final status
UPDATE tournaments SET status = 'final' WHERE id = 'masters-2026';
