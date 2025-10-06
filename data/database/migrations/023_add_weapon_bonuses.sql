-- Add attack_bonus and damage_bonus columns to equipment table for magic weapons
-- Migration 023: Add weapon bonuses

ALTER TABLE equipment ADD COLUMN attack_bonus INTEGER DEFAULT 0;
ALTER TABLE equipment ADD COLUMN damage_bonus INTEGER DEFAULT 0;

-- Update existing magic weapons to have their bonuses
-- +1 weapons
UPDATE equipment SET attack_bonus = 1, damage_bonus = 1 WHERE name LIKE '%+1%' AND item_type = 'weapon';

-- +2 weapons
UPDATE equipment SET attack_bonus = 2, damage_bonus = 2 WHERE name LIKE '%+2%' AND item_type = 'weapon';

-- +3 weapons
UPDATE equipment SET attack_bonus = 3, damage_bonus = 3 WHERE name LIKE '%+3%' AND item_type = 'weapon';
