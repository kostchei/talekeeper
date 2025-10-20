-- Migration 044: Remove duplicate HP columns from characters table
-- Standardizes on hit_points_current and hit_points_max naming convention
-- Removes: current_hit_points and max_hit_points (duplicates)

-- First, copy any data from the old columns to the new ones (safety measure)
-- In case any code was only updating the old columns
UPDATE characters
SET hit_points_current = COALESCE(current_hit_points, hit_points_current),
    hit_points_max = COALESCE(max_hit_points, hit_points_max)
WHERE current_hit_points IS NOT NULL OR max_hit_points IS NOT NULL;

-- SQLite doesn't support DROP COLUMN directly
-- We need to create a new table and copy data

-- Create temporary table with corrected schema
CREATE TABLE characters_new (
    id TEXT PRIMARY KEY,
    save_slot_id TEXT,
    name TEXT NOT NULL,

    -- Core D&D Stats
    race_id TEXT NOT NULL DEFAULT '',
    class_id TEXT NOT NULL DEFAULT '',
    subclass_id TEXT,
    background_id TEXT NOT NULL DEFAULT '',

    level INTEGER NOT NULL DEFAULT 1,
    experience_points INTEGER NOT NULL DEFAULT 0,

    -- Ability Scores (1-20 range)
    strength INTEGER NOT NULL DEFAULT 10,
    dexterity INTEGER NOT NULL DEFAULT 10,
    constitution INTEGER NOT NULL DEFAULT 10,
    intelligence INTEGER NOT NULL DEFAULT 10,
    wisdom INTEGER NOT NULL DEFAULT 10,
    charisma INTEGER NOT NULL DEFAULT 10,

    -- Calculated Combat Stats (STANDARDIZED COLUMNS ONLY)
    armor_class INTEGER NOT NULL DEFAULT 10,
    hit_points_max INTEGER NOT NULL DEFAULT 8,
    hit_points_current INTEGER NOT NULL DEFAULT 8,
    hit_points_temporary INTEGER NOT NULL DEFAULT 0,
    hit_dice_max INTEGER NOT NULL DEFAULT 1,
    hit_dice_current INTEGER NOT NULL DEFAULT 1,
    death_saves_successes INTEGER NOT NULL DEFAULT 0,
    death_saves_failures INTEGER NOT NULL DEFAULT 0,

    -- Equipment Slots
    equipment_main_hand TEXT,
    equipment_off_hand TEXT,
    equipment_armor TEXT,
    equipment_shield TEXT,
    equipment_helmet TEXT,
    equipment_gloves TEXT,
    equipment_boots TEXT,
    equipment_cloak TEXT,
    equipment_ring_1 TEXT,
    equipment_ring_2 TEXT,
    equipment_amulet TEXT,
    equipment_belt TEXT,

    -- Rest Tracking
    last_short_rest TEXT,
    last_long_rest TEXT,

    -- Metadata
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT,
    notes TEXT DEFAULT '',

    -- Fighter Features
    second_wind_uses_current INTEGER DEFAULT 2,
    second_wind_uses_max INTEGER DEFAULT 2,
    action_surge_uses_current INTEGER DEFAULT 0,
    action_surge_uses_max INTEGER DEFAULT 0,
    indomitable_uses_current INTEGER DEFAULT 0,
    indomitable_uses_max INTEGER DEFAULT 0,
    weapon_mastery_count INTEGER DEFAULT 3,
    weapon_mastery_selections TEXT DEFAULT '[]',

    -- Inspiration System
    inspiration_uses_current INTEGER DEFAULT 0,
    inspiration_uses_max INTEGER DEFAULT 0,

    -- Foreign Key Constraints
    FOREIGN KEY (save_slot_id) REFERENCES save_slots(id) ON DELETE SET NULL
);

-- Copy all data from old table to new table
INSERT INTO characters_new
SELECT
    id, save_slot_id, name,
    race_id, class_id, subclass_id, background_id,
    level, experience_points,
    strength, dexterity, constitution, intelligence, wisdom, charisma,
    armor_class,
    hit_points_max,
    hit_points_current,
    hit_points_temporary,
    hit_dice_max,
    hit_dice_current,
    death_saves_successes,
    death_saves_failures,
    equipment_main_hand, equipment_off_hand, equipment_armor, equipment_shield,
    equipment_helmet, equipment_gloves, equipment_boots, equipment_cloak,
    equipment_ring_1, equipment_ring_2, equipment_amulet, equipment_belt,
    last_short_rest, last_long_rest,
    created_at, updated_at, notes,
    second_wind_uses_current, second_wind_uses_max,
    action_surge_uses_current, action_surge_uses_max,
    indomitable_uses_current, indomitable_uses_max,
    weapon_mastery_count, weapon_mastery_selections,
    COALESCE(inspiration_uses_current, 0), COALESCE(inspiration_uses_max, 0)
FROM characters;

-- Drop views that reference the characters table BEFORE modifying it
DROP VIEW IF EXISTS character_summary;
DROP VIEW IF EXISTS character_full;

-- Drop old table
DROP TABLE characters;

-- Rename new table to original name
ALTER TABLE characters_new RENAME TO characters;

-- Recreate indexes
CREATE INDEX idx_characters_save_slot ON characters(save_slot_id);
CREATE INDEX idx_characters_name ON characters(name);

-- Recreate views that reference the characters table
CREATE VIEW character_summary AS
SELECT
    c.id,
    c.name,
    c.level,
    c.race_id,
    c.class_id,
    c.hit_points_current,
    c.hit_points_max,
    s.slot_number,
    s.last_played
FROM characters c
JOIN save_slots s ON c.save_slot_id = s.id
WHERE s.is_occupied = TRUE;

CREATE VIEW character_full AS
SELECT
    c.*,
    GROUP_CONCAT(cf.feat_name, '|') as feats,
    GROUP_CONCAT(cp.proficiency_name, '|') as proficiencies,
    GROUP_CONCAT(cwm.weapon_name || ':' || cwm.mastery_type, '|') as weapon_masteries
FROM characters c
LEFT JOIN character_feats cf ON c.id = cf.character_id
LEFT JOIN character_proficiencies cp ON c.id = cp.character_id
LEFT JOIN character_weapon_masteries cwm ON c.id = cwm.character_id
GROUP BY c.id;
