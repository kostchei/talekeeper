-- Add character_combat_state table for storing temporary combat selections
-- This includes Cunning Strike selections, Steady Aim status, etc.

CREATE TABLE IF NOT EXISTS character_combat_state (
    character_id TEXT PRIMARY KEY,
    cunning_strike_selection TEXT,  -- JSON array of effect IDs
    steady_aim_active BOOLEAN DEFAULT 0,
    movement_used INTEGER DEFAULT 0,
    bonus_action_used BOOLEAN DEFAULT 0,
    reaction_used BOOLEAN DEFAULT 0,
    sneak_attack_used_this_turn BOOLEAN DEFAULT 0,
    last_updated TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_combat_state_character
ON character_combat_state(character_id);
