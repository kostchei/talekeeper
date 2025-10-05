-- Migration: Fix Thieves Tools duplicate and make equipable to belt slot
-- Created: 2025-09-24

-- Remove duplicate Thieves' Tools entry if it exists
DELETE FROM equipment WHERE id = 165;

-- Ensure the main Thieves Tools entry has consistent naming and enhanced description
UPDATE equipment
SET name = 'Thieves Tools',
    description = 'Lock picks and small tools for disarming traps and opening locks. Can be equipped to belt slot. When equipped and you are proficient with Thieves Tools and either Investigation or Sleight of Hand, you gain advantage on checks to detect and disarm traps.'
WHERE id = 93;

-- Update any character inventories that have the old name
UPDATE character_inventory
SET item_name = 'Thieves Tools'
WHERE item_name = 'Thieves'' Tools';

-- Update any character equipment slots that have the old name
UPDATE characters
SET equipment_belt = 'Thieves Tools'
WHERE equipment_belt = 'Thieves'' Tools';

-- Update background proficiencies to use consistent name
UPDATE background_proficiencies
SET proficiency_name = 'Thieves Tools'
WHERE proficiency_name = 'Thieves'' Tools';