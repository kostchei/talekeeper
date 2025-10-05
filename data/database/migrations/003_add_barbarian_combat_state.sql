-- Add Barbarian-specific columns to character_combat_state table
-- Migration: 003_add_barbarian_combat_state.sql

ALTER TABLE character_combat_state ADD COLUMN raging BOOLEAN DEFAULT FALSE;
ALTER TABLE character_combat_state ADD COLUMN rage_damage_bonus INTEGER DEFAULT 0;
ALTER TABLE character_combat_state ADD COLUMN reckless_attack_active BOOLEAN DEFAULT FALSE;
ALTER TABLE character_combat_state ADD COLUMN frenzy_active BOOLEAN DEFAULT FALSE;