-- Migration 036: Add Bag of Holding system for gold and treasure management

-- Add bag of holding tracking to character_inventory
ALTER TABLE character_inventory ADD COLUMN stored_in_bag INTEGER DEFAULT 0;

-- Add treasure type field to distinguish coins from gems/art
ALTER TABLE character_inventory ADD COLUMN treasure_type TEXT DEFAULT 'standard';

-- Add gem/art object specific properties
ALTER TABLE character_inventory ADD COLUMN unit_value_gp REAL DEFAULT NULL;

-- Create index for bag queries
CREATE INDEX IF NOT EXISTS idx_character_inventory_stored_in_bag
ON character_inventory(character_id, stored_in_bag);
