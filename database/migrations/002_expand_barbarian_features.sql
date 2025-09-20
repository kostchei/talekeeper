-- Expand barbarian_features table for all Barbarian features levels 1-20
-- Migration: 002_expand_barbarian_features.sql

-- Add columns for core Barbarian features
ALTER TABLE barbarian_features ADD COLUMN fast_movement_active BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN feral_instinct_active BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN brutal_strike_uses_current INTEGER DEFAULT 0;
ALTER TABLE barbarian_features ADD COLUMN brutal_strike_uses_max INTEGER DEFAULT 0;
ALTER TABLE barbarian_features ADD COLUMN relentless_rage_uses_current INTEGER DEFAULT 0;
ALTER TABLE barbarian_features ADD COLUMN relentless_rage_uses_max INTEGER DEFAULT 0;
ALTER TABLE barbarian_features ADD COLUMN persistent_rage_recharge_used BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN primal_knowledge_skills TEXT; -- JSON array of selected skills
ALTER TABLE barbarian_features ADD COLUMN instinctive_pounce_available BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN indomitable_might_active BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN primal_champion_applied BOOLEAN DEFAULT FALSE;

-- Path of the Berserker subclass features
ALTER TABLE barbarian_features ADD COLUMN frenzy_active BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN mindless_rage_active BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN retaliation_available BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN intimidating_presence_uses_current INTEGER DEFAULT 0;
ALTER TABLE barbarian_features ADD COLUMN intimidating_presence_uses_max INTEGER DEFAULT 0;

-- Track which Brutal Strike effects are available by level
ALTER TABLE barbarian_features ADD COLUMN brutal_strike_effects TEXT; -- JSON array: ["forceful", "hamstring", "staggering", "sundering"]

-- Additional tracking for advanced features
ALTER TABLE barbarian_features ADD COLUMN weapon_mastery_count INTEGER DEFAULT 2; -- Scales with level
ALTER TABLE barbarian_features ADD COLUMN extra_attacks INTEGER DEFAULT 1; -- Base 1, becomes 2 at level 5

-- Ensure proper indexing
CREATE INDEX IF NOT EXISTS idx_barbarian_features_level ON barbarian_features(level);
CREATE INDEX IF NOT EXISTS idx_barbarian_features_raging ON barbarian_features(is_raging);