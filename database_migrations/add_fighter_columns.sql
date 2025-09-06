-- Add Fighter-specific resource columns to characters table
ALTER TABLE characters ADD COLUMN second_wind_uses_current INTEGER DEFAULT 2;
ALTER TABLE characters ADD COLUMN second_wind_uses_max INTEGER DEFAULT 2;
ALTER TABLE characters ADD COLUMN action_surge_uses_current INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN action_surge_uses_max INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN indomitable_uses_current INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN indomitable_uses_max INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN weapon_mastery_count INTEGER DEFAULT 3;
ALTER TABLE characters ADD COLUMN weapon_mastery_selections TEXT DEFAULT '[]';  -- JSON array

-- Create weapon masteries table
CREATE TABLE IF NOT EXISTS character_weapon_masteries (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    weapon_type TEXT NOT NULL,
    mastery_property TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Create combat state table
CREATE TABLE IF NOT EXISTS character_combat_state (
    character_id TEXT PRIMARY KEY,
    studied_target_id TEXT,
    last_miss_turn INTEGER DEFAULT 0,
    heroic_warrior_active INTEGER DEFAULT 0,  -- BOOL
    survivor_active INTEGER DEFAULT 0,  -- BOOL
    last_attack_missed INTEGER DEFAULT 0,  -- BOOL
    critical_range_min INTEGER DEFAULT 20,  -- For improved/superior critical
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_weapon_masteries_character ON character_weapon_masteries(character_id);
CREATE INDEX IF NOT EXISTS idx_combat_state_character ON character_combat_state(character_id);