-- Add fighter-specific resource tracking columns
-- This migration adds support for Fighter class features

-- Add fighter resource columns to characters table
-- Note: SQLite doesn't support IF NOT EXISTS for ALTER TABLE
-- These will fail silently if columns already exist
ALTER TABLE characters ADD COLUMN second_wind_uses_current INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN second_wind_uses_max INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN action_surge_uses_current INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN action_surge_uses_max INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN indomitable_uses_current INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN indomitable_uses_max INTEGER DEFAULT 0;

-- Create fighter features table if it doesn't exist
CREATE TABLE IF NOT EXISTS fighter_features (
    level INTEGER PRIMARY KEY,
    feature_name TEXT NOT NULL,
    description TEXT,
    action_type TEXT,
    uses_per_rest TEXT,
    rest_type TEXT
);

-- Insert fighter feature data if not already present
INSERT OR IGNORE INTO fighter_features VALUES
    (1, 'Second Wind', 'Regain 1d10 + fighter level HP', 'bonus_action', '1', 'short'),
    (1, 'Fighting Style', 'Choose a fighting style', 'passive', NULL, NULL),
    (1, 'Weapon Mastery', 'Master weapon properties', 'passive', NULL, NULL),
    (2, 'Action Surge', 'Take an additional action', 'free', '1', 'short'),
    (2, 'Tactical Mind', 'Add 1d10 to ability checks', 'reaction', 'uses_second_wind', 'short'),
    (5, 'Extra Attack', 'Attack twice when taking Attack action', 'passive', NULL, NULL),
    (5, 'Tactical Shift', 'Move half speed after Second Wind', 'passive', NULL, NULL),
    (9, 'Indomitable', 'Reroll a failed save', 'reaction', '1', 'long'),
    (11, 'Extra Attack (2)', 'Attack three times', 'passive', NULL, NULL),
    (13, 'Studied Attacks', 'Advantage after missing', 'passive', NULL, NULL),
    (20, 'Extra Attack (3)', 'Attack four times', 'passive', NULL, NULL);