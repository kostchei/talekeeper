-- Migration 009: Add Class Proficiencies
-- Adds proficiency columns to classes table for weapons, armor, and items

-- Add proficiency columns
ALTER TABLE classes ADD COLUMN weapon_proficiencies TEXT DEFAULT NULL;
ALTER TABLE classes ADD COLUMN armor_proficiencies TEXT DEFAULT NULL;
ALTER TABLE classes ADD COLUMN item_proficiencies TEXT DEFAULT NULL;

-- Update Fighter proficiencies
UPDATE classes SET 
    weapon_proficiencies = 'simple weapons,martial weapons',
    armor_proficiencies = 'light armor,medium armor,heavy armor,shields',
    item_proficiencies = ''
WHERE name = 'Fighter';

-- Update Barbarian proficiencies
UPDATE classes SET 
    weapon_proficiencies = 'simple weapons,martial weapons',
    armor_proficiencies = 'light armor,medium armor,shields',
    item_proficiencies = ''
WHERE name = 'Barbarian';

-- Update Cleric proficiencies
UPDATE classes SET 
    weapon_proficiencies = 'simple weapons',
    armor_proficiencies = 'light armor,medium armor,shields',
    item_proficiencies = 'holy symbol,focus'
WHERE name = 'Cleric';

-- Update Paladin proficiencies
UPDATE classes SET 
    weapon_proficiencies = 'simple weapons,martial weapons',
    armor_proficiencies = 'light armor,medium armor,heavy armor,shields',
    item_proficiencies = 'holy symbol'
WHERE name = 'Paladin';

-- Update Rogue proficiencies
UPDATE classes SET 
    weapon_proficiencies = 'simple weapons,hand crossbow,longsword,rapier,shortsword',
    armor_proficiencies = 'light armor',
    item_proficiencies = ''
WHERE name = 'Rogue';

-- Update Warlock proficiencies
UPDATE classes SET 
    weapon_proficiencies = 'simple weapons',
    armor_proficiencies = 'light armor',
    item_proficiencies = 'rod,focus'
WHERE name = 'Warlock';

-- Update Wizard proficiencies
UPDATE classes SET 
    weapon_proficiencies = 'dagger,dart,sling,quarterstaff,light crossbow',
    armor_proficiencies = '',
    item_proficiencies = 'wand,focus'
WHERE name = 'Wizard';

-- Add other missing classes if they exist
INSERT OR IGNORE INTO classes (id, name, weapon_proficiencies, armor_proficiencies, item_proficiencies) VALUES
('sorcerer', 'Sorcerer', 'dagger,dart,sling,quarterstaff,light crossbow', '', 'focus'),
('ranger', 'Ranger', 'simple weapons,martial weapons', 'light armor,medium armor,shields', ''),
('druid', 'Druid', 'simple weapons', 'light armor,medium armor,shields', 'focus'),
('bard', 'Bard', 'simple weapons', 'light armor', 'focus');