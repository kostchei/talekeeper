-- Fix skill proficiency system to support proper selection
-- Replace the incorrect auto-assignment system with proper choice-based system

-- Create table for class skill choices (how many to pick from which list)
CREATE TABLE IF NOT EXISTS class_skill_choices (
    class_id TEXT NOT NULL,
    skill_count INTEGER NOT NULL, -- How many skills to choose
    available_skills TEXT NOT NULL, -- JSON array of available skills
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- Create table for background proficiencies  
CREATE TABLE IF NOT EXISTS background_proficiencies (
    background_id TEXT NOT NULL,
    proficiency_type TEXT NOT NULL, -- 'skill', 'tool', 'language'
    proficiency_name TEXT NOT NULL,
    FOREIGN KEY (background_id) REFERENCES backgrounds(id)
);

-- Create table for species proficiencies
CREATE TABLE IF NOT EXISTS species_proficiencies (
    species_id TEXT NOT NULL, 
    proficiency_type TEXT NOT NULL, -- 'skill', 'tool', 'language', 'weapon'
    proficiency_name TEXT, -- NULL for choices
    choice_count INTEGER DEFAULT 0, -- For species that get to choose (e.g., Human gets 1 skill choice)
    available_options TEXT, -- JSON array for choices
    FOREIGN KEY (species_id) REFERENCES races(id)
);

-- Populate class skill choices with correct D&D 2024 values
INSERT OR REPLACE INTO class_skill_choices VALUES 
('fighter', 2, '["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Perception", "Survival"]'),
('barbarian', 2, '["Animal Handling", "Athletics", "Intimidation", "Nature", "Perception", "Survival"]'),
('cleric', 2, '["History", "Insight", "Medicine", "Persuasion", "Religion"]'),
('rogue', 4, '["Acrobatics", "Athletics", "Deception", "Insight", "Intimidation", "Investigation", "Perception", "Performance", "Persuasion", "Sleight of Hand", "Stealth"]'),
('wizard', 2, '["Arcana", "History", "Insight", "Investigation", "Medicine", "Religion"]'),
('paladin', 2, '["Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"]');

-- Populate background proficiencies (common D&D backgrounds)
INSERT OR REPLACE INTO background_proficiencies VALUES 
-- Acolyte
('acolyte', 'skill', 'Insight'),
('acolyte', 'skill', 'Religion'),
('acolyte', 'language', 'choice_2'), -- Choose 2 languages

-- Criminal  
('criminal', 'skill', 'Deception'),
('criminal', 'skill', 'Stealth'),
('criminal', 'tool', 'thieves_tools'),
('criminal', 'tool', 'gaming_set'),

-- Folk Hero
('folk_hero', 'skill', 'Animal Handling'),
('folk_hero', 'skill', 'Survival'), 
('folk_hero', 'tool', 'artisan_tools'),
('folk_hero', 'tool', 'vehicles_land'),

-- Noble
('noble', 'skill', 'History'),
('noble', 'skill', 'Persuasion'),
('noble', 'tool', 'gaming_set'),
('noble', 'language', 'choice_1'), -- Choose 1 language

-- Sage
('sage', 'skill', 'Arcana'),
('sage', 'skill', 'History'),
('sage', 'language', 'choice_2'), -- Choose 2 languages

-- Soldier
('soldier', 'skill', 'Athletics'), 
('soldier', 'skill', 'Intimidation'),
('soldier', 'tool', 'gaming_set'),
('soldier', 'tool', 'vehicles_land');

-- Populate species proficiencies  
INSERT OR REPLACE INTO species_proficiencies VALUES
-- Human (gets to choose 1 skill)
('human', 'skill', NULL, 1, '["any"]'),

-- Dwarf
('dwarf', 'tool', 'smith_tools', 0, NULL),

-- Elf  
('elf', 'skill', 'Perception', 0, NULL),
('elf', 'weapon', 'longsword', 0, NULL),
('elf', 'weapon', 'shortbow', 0, NULL),

-- Halfling
('halfling', 'skill', 'Stealth', 0, NULL);

-- Clear the incorrect auto-assigned skills from existing characters
-- (We'll need to let players re-choose their skills properly)
DELETE FROM character_proficiencies WHERE proficiency_type = 'skill' AND source = 'class';