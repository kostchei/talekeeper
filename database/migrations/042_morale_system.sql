-- Migration 042: Morale System
-- Adds morale mechanics for enemies in combat
-- Enemies flee when reduced below 50% strength (HP or count)

-- Add morale configuration to monsters table
ALTER TABLE monsters ADD COLUMN morale_threshold REAL DEFAULT 0.5;
ALTER TABLE monsters ADD COLUMN morale_dc INTEGER DEFAULT 15;

-- Track morale status during active combat encounters
CREATE TABLE IF NOT EXISTS combat_morale_status (
    encounter_id TEXT NOT NULL,
    monster_id TEXT NOT NULL,
    monster_name TEXT NOT NULL,
    initial_count INTEGER NOT NULL,
    initial_hp INTEGER NOT NULL,
    current_count INTEGER NOT NULL,
    morale_broken INTEGER DEFAULT 0,
    morale_check_passed INTEGER,
    morale_roll INTEGER,
    morale_modifier INTEGER,
    check_timestamp TEXT,
    PRIMARY KEY (encounter_id, monster_id)
);
