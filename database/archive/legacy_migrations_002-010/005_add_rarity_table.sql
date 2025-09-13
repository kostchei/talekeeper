-- Migration: Add item rarity table for treasure hoards and loot generation
-- Based on D&D 5e treasure tables by level range

CREATE TABLE IF NOT EXISTS item_rarity_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level_range TEXT NOT NULL,
    min_level INTEGER NOT NULL,
    max_level INTEGER NOT NULL,
    roll_min INTEGER NOT NULL,
    roll_max INTEGER NOT NULL,
    rarity TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Clear existing data
DELETE FROM item_rarity_table;

-- Levels 1-4 (Early Game)
INSERT INTO item_rarity_table (level_range, min_level, max_level, roll_min, roll_max, rarity) VALUES
('1-4', 1, 4, 1, 54, 'common'),
('1-4', 1, 4, 55, 91, 'uncommon'),
('1-4', 1, 4, 92, 100, 'rare');

-- Levels 5-10 (Mid Game)
INSERT INTO item_rarity_table (level_range, min_level, max_level, roll_min, roll_max, rarity) VALUES
('5-10', 5, 10, 1, 30, 'common'),
('5-10', 5, 10, 31, 81, 'uncommon'),
('5-10', 5, 10, 82, 98, 'rare'),
('5-10', 5, 10, 99, 100, 'very rare');

-- Levels 11-16 (High Game)
INSERT INTO item_rarity_table (level_range, min_level, max_level, roll_min, roll_max, rarity) VALUES
('11-16', 11, 16, 1, 11, 'common'),
('11-16', 11, 16, 12, 34, 'uncommon'),
('11-16', 11, 16, 35, 70, 'rare'),
('11-16', 11, 16, 71, 93, 'very rare'),
('11-16', 11, 16, 94, 100, 'legendary');

-- Levels 17-20 (Epic Game)
INSERT INTO item_rarity_table (level_range, min_level, max_level, roll_min, roll_max, rarity) VALUES
('17-20', 17, 20, 1, 20, 'rare'),
('17-20', 17, 20, 21, 64, 'very rare'),
('17-20', 17, 20, 65, 100, 'legendary');

-- Create index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_rarity_level_range ON item_rarity_table(min_level, max_level);
CREATE INDEX IF NOT EXISTS idx_rarity_roll ON item_rarity_table(roll_min, roll_max);