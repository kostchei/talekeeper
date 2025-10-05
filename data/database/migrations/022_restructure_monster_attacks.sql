-- Migration to restructure monster attacks for better combat system integration
-- This adds proper attack tracking columns to monsters table

-- Add new columns for structured attack data
ALTER TABLE monsters ADD COLUMN multiattack_description TEXT;
ALTER TABLE monsters ADD COLUMN primary_attack_name TEXT;
ALTER TABLE monsters ADD COLUMN primary_attack_bonus INTEGER;
ALTER TABLE monsters ADD COLUMN primary_attack_reach TEXT;
ALTER TABLE monsters ADD COLUMN primary_damage_dice TEXT;
ALTER TABLE monsters ADD COLUMN primary_damage_type TEXT;

-- Create index for faster attack lookups
CREATE INDEX IF NOT EXISTS idx_monsters_attacks ON monsters(primary_attack_name, challenge_rating);
