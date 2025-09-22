-- Migration 013: Wizard Class Implementation
-- Phase 2.2: Wizard Implementation (Spellbook system, Arcane Recovery, Evocation School)
-- Created: September 2024

-- Wizard-specific features table
CREATE TABLE IF NOT EXISTS wizard_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL,

    -- Spell Slots (Same as Cleric - Full Caster)
    spell_slots_1_current INTEGER DEFAULT 0,
    spell_slots_1_max INTEGER DEFAULT 0,
    spell_slots_2_current INTEGER DEFAULT 0,
    spell_slots_2_max INTEGER DEFAULT 0,
    spell_slots_3_current INTEGER DEFAULT 0,
    spell_slots_3_max INTEGER DEFAULT 0,
    spell_slots_4_current INTEGER DEFAULT 0,
    spell_slots_4_max INTEGER DEFAULT 0,
    spell_slots_5_current INTEGER DEFAULT 0,
    spell_slots_5_max INTEGER DEFAULT 0,
    spell_slots_6_current INTEGER DEFAULT 0,
    spell_slots_6_max INTEGER DEFAULT 0,
    spell_slots_7_current INTEGER DEFAULT 0,
    spell_slots_7_max INTEGER DEFAULT 0,
    spell_slots_8_current INTEGER DEFAULT 0,
    spell_slots_8_max INTEGER DEFAULT 0,
    spell_slots_9_current INTEGER DEFAULT 0,
    spell_slots_9_max INTEGER DEFAULT 0,

    -- Wizard-Specific Features
    arcane_tradition TEXT, -- 'evocation', 'abjuration', 'conjuration', etc.
    arcane_recovery_used BOOLEAN DEFAULT FALSE,
    arcane_recovery_last_reset TEXT, -- ISO timestamp

    -- Spellbook tracking
    spells_prepared INTEGER DEFAULT 0, -- Number of spells currently prepared
    max_spells_prepared INTEGER DEFAULT 0, -- Intelligence modifier + wizard level

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    PRIMARY KEY (character_id)
);

-- Wizard spellbook - tracks all spells the wizard knows
CREATE TABLE IF NOT EXISTS wizard_spellbook (
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    learned_at_level INTEGER NOT NULL, -- Character level when learned
    source TEXT DEFAULT 'level_up', -- 'level_up', 'copied', 'found', 'starting'
    cost_paid INTEGER DEFAULT 0, -- Gold cost if copied
    time_spent INTEGER DEFAULT 0, -- Hours spent copying if applicable
    notes TEXT, -- Any special notes about this spell

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (spell_id) REFERENCES spells(id),
    PRIMARY KEY (character_id, spell_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_wizard_features_character_id ON wizard_features(character_id);
CREATE INDEX IF NOT EXISTS idx_wizard_spellbook_character_id ON wizard_spellbook(character_id);
CREATE INDEX IF NOT EXISTS idx_wizard_spellbook_spell_level ON wizard_spellbook(spell_level);
CREATE INDEX IF NOT EXISTS idx_wizard_spellbook_source ON wizard_spellbook(source);

-- Insert Wizard class into classes table if not exists
INSERT OR IGNORE INTO classes (
    id, name, description, hit_die, primary_ability, skill_choices,
    starting_equipment, equipment_choices, weapon_proficiencies,
    armor_proficiencies, item_proficiencies
) VALUES (
    'wizard',
    'Wizard',
    'Masters of arcane magic, studying spells from ancient tomes and focusing their minds on understanding the fundamental forces of magic itself.',
    6, -- d6 hit die
    'intelligence',
    2, -- 2 skills from: Arcana, History, Insight, Investigation, Medicine, Religion
    'dagger,component_pouch,scholars_pack', -- Starting equipment
    'simple_weapons,daggers,darts,slings,quarterstaffs,light_crossbows', -- Equipment choices
    'daggers,darts,slings,quarterstaffs,light_crossbows', -- Weapon proficiencies
    'none', -- No armor proficiency
    'none' -- No tool proficiencies
);

-- Insert Wizard subclasses
INSERT OR IGNORE INTO subclasses (
    id, class_id, name, description, selection_level
) VALUES
    ('evocation', 'wizard', 'School of Evocation', 'Masters of elemental magic focused on damage and battlefield control', 2),
    ('abjuration', 'wizard', 'School of Abjuration', 'Specialists in protective magic and nullifying hostile spells', 2),
    ('conjuration', 'wizard', 'School of Conjuration', 'Experts at summoning creatures and objects from other planes', 2),
    ('divination', 'wizard', 'School of Divination', 'Seers who glimpse the future and uncover hidden knowledge', 2),
    ('enchantment', 'wizard', 'School of Enchantment', 'Manipulators of minds and emotions through magical influence', 2),
    ('illusion', 'wizard', 'School of Illusion', 'Masters of deception who blur the line between reality and fantasy', 2),
    ('necromancy', 'wizard', 'School of Necromancy', 'Students of death magic who command undead and manipulate life force', 2),
    ('transmutation', 'wizard', 'School of Transmutation', 'Changers who alter the fundamental properties of creatures and objects', 2);

-- Add Wizard to class_features_progression table
INSERT OR IGNORE INTO class_features_progression (
    class_id, level, feature_name, feature_type, description
) VALUES
    -- Level 1
    ('wizard', 1, 'Spellcasting', 'passive', 'You can cast wizard spells using Intelligence as your spellcasting ability'),
    ('wizard', 1, 'Arcane Recovery', 'resource', 'Once per day when you finish a short rest, you can recover spell slots'),

    -- Level 2
    ('wizard', 2, 'Arcane Tradition', 'passive', 'Choose your school of magic specialization'),

    -- Level 3
    ('wizard', 3, '2nd-level Spells', 'passive', 'You can now learn and cast 2nd-level spells'),

    -- Level 4
    ('wizard', 4, 'Ability Score Improvement', 'passive', 'Increase one ability score by 2, or two ability scores by 1 each'),
    ('wizard', 4, 'Cantrip Versatility', 'passive', 'You can replace one cantrip with another from the wizard spell list'),

    -- Level 5
    ('wizard', 5, '3rd-level Spells', 'passive', 'You can now learn and cast 3rd-level spells'),

    -- Level 6
    ('wizard', 6, 'Arcane Tradition Feature', 'passive', 'Your chosen school grants you additional features'),

    -- Level 7
    ('wizard', 7, '4th-level Spells', 'passive', 'You can now learn and cast 4th-level spells'),

    -- Level 8
    ('wizard', 8, 'Ability Score Improvement', 'passive', 'Increase one ability score by 2, or two ability scores by 1 each'),

    -- Level 9
    ('wizard', 9, '5th-level Spells', 'passive', 'You can now learn and cast 5th-level spells'),

    -- Level 10
    ('wizard', 10, 'Arcane Tradition Feature', 'passive', 'Your chosen school grants you additional features'),

    -- Level 11
    ('wizard', 11, '6th-level Spells', 'passive', 'You can now learn and cast 6th-level spells'),

    -- Level 12
    ('wizard', 12, 'Ability Score Improvement', 'passive', 'Increase one ability score by 2, or two ability scores by 1 each'),

    -- Level 13
    ('wizard', 13, '7th-level Spells', 'passive', 'You can now learn and cast 7th-level spells'),

    -- Level 14
    ('wizard', 14, 'Arcane Tradition Feature', 'passive', 'Your chosen school grants you additional features'),

    -- Level 15
    ('wizard', 15, '8th-level Spells', 'passive', 'You can now learn and cast 8th-level spells'),

    -- Level 16
    ('wizard', 16, 'Ability Score Improvement', 'passive', 'Increase one ability score by 2, or two ability scores by 1 each'),

    -- Level 17
    ('wizard', 17, '9th-level Spells', 'passive', 'You can now learn and cast 9th-level spells'),

    -- Level 18
    ('wizard', 18, 'Spell Mastery', 'passive', 'Choose one 1st-level and one 2nd-level spell to cast at will'),

    -- Level 19
    ('wizard', 19, 'Ability Score Improvement', 'passive', 'Increase one ability score by 2, or two ability scores by 1 each'),

    -- Level 20
    ('wizard', 20, 'Signature Spell', 'passive', 'Choose two 3rd-level spells as signature spells');

-- Update schema version
UPDATE schema_version SET version = 13, description = 'Wizard class implementation with spellbook system' WHERE version = (SELECT MAX(version) FROM schema_version);