-- Migration to fix rogue_features table schema
-- Adds missing columns for rogue progression features

-- Check if columns exist and add them if missing
-- SQLite doesn't support IF NOT EXISTS for ALTER TABLE, so we need to handle this carefully

-- First, create a temporary table with the complete schema
CREATE TABLE IF NOT EXISTS rogue_features_new (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,

    -- Sneak Attack (scales with level)
    sneak_attack_dice INTEGER DEFAULT 1,

    -- Expertise (double proficiency bonus)
    expertise_skills TEXT,
    expertise_count INTEGER DEFAULT 2,

    -- Cunning Action (level 2+)
    cunning_action_available BOOLEAN DEFAULT FALSE,

    -- Uncanny Dodge (level 5+)
    uncanny_dodge_available BOOLEAN DEFAULT FALSE,
    uncanny_dodge_used BOOLEAN DEFAULT FALSE,

    -- Evasion (level 7+)
    evasion_available BOOLEAN DEFAULT FALSE,

    -- Cunning Strike (level 5+)
    cunning_strike_available BOOLEAN DEFAULT FALSE,
    cunning_strike_effects_known TEXT DEFAULT '[]',
    improved_cunning_strike BOOLEAN DEFAULT FALSE,

    -- Devious Strikes (level 14+)
    devious_strikes_available BOOLEAN DEFAULT FALSE,
    daze_available BOOLEAN DEFAULT FALSE,
    knock_out_available BOOLEAN DEFAULT FALSE,
    obscure_available BOOLEAN DEFAULT FALSE,

    -- Reliable Talent (level 11+)
    reliable_talent_active BOOLEAN DEFAULT FALSE,
    reliable_talent_minimum INTEGER DEFAULT 10,

    -- Slippery Mind (level 15+)
    slippery_mind_active BOOLEAN DEFAULT FALSE,

    -- Elusive (level 18+)
    elusive_active BOOLEAN DEFAULT FALSE,

    -- Stroke of Luck (level 20)
    stroke_of_luck_uses_current INTEGER DEFAULT 0,
    stroke_of_luck_uses_max INTEGER DEFAULT 0,

    -- Combat tracking
    sneak_attack_used_this_turn BOOLEAN DEFAULT FALSE,
    steady_aim_active BOOLEAN DEFAULT FALSE,

    -- Subclass features
    archetype TEXT,
    subclass_features TEXT DEFAULT '{}',

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    PRIMARY KEY (character_id)
);

-- Copy existing data if table exists (only copy columns that exist)
INSERT OR IGNORE INTO rogue_features_new (character_id, level, sneak_attack_dice)
SELECT
    character_id,
    COALESCE(level, 1),
    COALESCE(sneak_attack_dice, 1)
FROM rogue_features
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='rogue_features');

-- Drop old table and rename new one
DROP TABLE IF EXISTS rogue_features;
ALTER TABLE rogue_features_new RENAME TO rogue_features;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_rogue_features_character_id ON rogue_features(character_id);
CREATE INDEX IF NOT EXISTS idx_rogue_features_level_cunning_strike ON rogue_features(level, cunning_strike_available);
CREATE INDEX IF NOT EXISTS idx_rogue_features_sneak_attack ON rogue_features(character_id, sneak_attack_used_this_turn);