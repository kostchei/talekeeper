-- Add ability check bonus column for luckstone and similar items
ALTER TABLE character_magical_bonuses ADD COLUMN ability_check_bonus INTEGER DEFAULT 0;