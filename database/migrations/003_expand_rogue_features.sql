-- Expand rogue_features table for comprehensive Rogue class support
-- Migration: 003_expand_rogue_features.sql

-- Add columns for Cunning Strike system (Level 5+)
ALTER TABLE rogue_features ADD COLUMN cunning_strike_available BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN cunning_strike_effects_known TEXT DEFAULT '[]'; -- JSON array of known effects

-- Add columns for Reliable Talent (Level 7+)
ALTER TABLE rogue_features ADD COLUMN reliable_talent_active BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN reliable_talent_minimum INTEGER DEFAULT 10;

-- Add columns for advanced features (Level 11+)
ALTER TABLE rogue_features ADD COLUMN improved_cunning_strike BOOLEAN DEFAULT FALSE; -- Can use 2 effects
ALTER TABLE rogue_features ADD COLUMN devious_strikes_available BOOLEAN DEFAULT FALSE; -- Level 14+

-- Add columns for Devious Strikes (Level 14+)
ALTER TABLE rogue_features ADD COLUMN daze_available BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN knock_out_available BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN obscure_available BOOLEAN DEFAULT FALSE;

-- Add columns for high-level features (Level 15+)
ALTER TABLE rogue_features ADD COLUMN slippery_mind_active BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN elusive_active BOOLEAN DEFAULT FALSE;

-- Add columns for capstone feature (Level 20)
ALTER TABLE rogue_features ADD COLUMN stroke_of_luck_uses_current INTEGER DEFAULT 0;
ALTER TABLE rogue_features ADD COLUMN stroke_of_luck_uses_max INTEGER DEFAULT 0;

-- Add columns for turn-based tracking
ALTER TABLE rogue_features ADD COLUMN sneak_attack_used_this_turn BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN steady_aim_active BOOLEAN DEFAULT FALSE;

-- Add columns for Expertise tracking
ALTER TABLE rogue_features ADD COLUMN expertise_count INTEGER DEFAULT 2; -- 2 at level 1, 4 at level 6

-- Add columns for subclass features (Arcane Trickster, etc.)
ALTER TABLE rogue_features ADD COLUMN subclass_features TEXT DEFAULT '{}'; -- JSON object for subclass-specific data

-- Note: Stroke of Luck will be managed through the character_resources table
-- using the existing resource_name pattern

-- Create index for performance on frequently queried fields
CREATE INDEX IF NOT EXISTS idx_rogue_features_level_cunning_strike ON rogue_features(level, cunning_strike_available);
CREATE INDEX IF NOT EXISTS idx_rogue_features_sneak_attack ON rogue_features(character_id, sneak_attack_used_this_turn);