-- Migration 007: Add Attunement Requirements
-- Adds attunement_requirement column to equipment table for magic item restrictions

-- Add attunement_requirement column
ALTER TABLE equipment ADD COLUMN attunement_requirement TEXT DEFAULT NULL;

-- Update existing magic items with attunement requirements
UPDATE equipment SET attunement_requirement = 'spellcaster' WHERE name = 'Wand of the War Mage +1';
UPDATE equipment SET attunement_requirement = 'warlock' WHERE name = 'Rod of the Pact Keeper +1';
UPDATE equipment SET attunement_requirement = 'cleric,paladin' WHERE name LIKE '%Book of the Devout%';

-- Update other items that require attunement
UPDATE equipment SET attunement_requirement = 'any' WHERE name IN (
    'Cloak of Protection',
    'Ring of Protection', 
    'Ring of Spell Storing',
    'Belt of Hill Giant Strength',
    'Belt of Stone Giant Strength', 
    'Belt of Cloud Giant Strength',
    'Cloak of Displacement',
    'Ring of Resistance',
    'Bracers of Defense',
    'Staff of Power',
    'Staff of the Magi',
    'Holy Avenger',
    'Vorpal Sword', 
    'Sword of Answering',
    'Defender',
    'Robe of the Archmagi',
    'Illusionist''s Bracers'
);

-- Items that require attunement by spellcasters
UPDATE equipment SET attunement_requirement = 'spellcaster' WHERE name IN (
    'Staff of Power',
    'Staff of the Magi',
    'Robe of the Archmagi',
    'Illusionist''s Bracers'
);

-- Items that require attunement by specific classes
UPDATE equipment SET attunement_requirement = 'paladin' WHERE name = 'Holy Avenger';