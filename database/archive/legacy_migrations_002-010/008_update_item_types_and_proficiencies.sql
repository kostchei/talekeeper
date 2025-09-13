-- Migration 008: Update Item Types and Class Proficiencies
-- Changes magic item types to use proficiency system instead of attunement

-- Update item types for magic items
UPDATE equipment SET item_type = 'wand' WHERE name LIKE '%Wand of the War Mage%';
UPDATE equipment SET item_type = 'rod' WHERE name LIKE '%Rod of the Pact%';
UPDATE equipment SET item_type = 'holy symbol' WHERE name LIKE '%Book of the Devout%';

-- Remove the attunement_requirement column since we're using proficiency now
-- (Keep it for now in case we need it for other items, but we won't use it for these)

-- Add more specific item types for better proficiency checking
UPDATE equipment SET item_type = 'focus' WHERE name IN (
    'Crystal', 'Orb', 'Wand', 'Component Pouch'
);