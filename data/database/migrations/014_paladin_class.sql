-- Migration 014: Paladin Class Implementation
-- Phase 2.3: Paladin Implementation (Half-caster, Divine Smite, Lay on Hands, Oath system)
-- Created: September 2024

-- Paladin-specific features table
CREATE TABLE IF NOT EXISTS paladin_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL,

    -- Spell Slots (Half-caster progression)
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

    -- Paladin-Specific Features
    sacred_oath TEXT, -- 'devotion', 'ancients', 'vengeance', etc.

    -- Lay on Hands pool (5 x paladin level)
    lay_on_hands_pool_current INTEGER DEFAULT 0,
    lay_on_hands_pool_max INTEGER DEFAULT 0,

    -- Channel Divinity (shared resource with oath features)
    channel_divinity_uses_current INTEGER DEFAULT 0,
    channel_divinity_uses_max INTEGER DEFAULT 1, -- Scales with level
    channel_divinity_last_reset TEXT,

    -- Divine Smite tracking (unlimited but consumes spell slots)
    divine_smite_uses_today INTEGER DEFAULT 0, -- For potential limits

    -- Oath spells (always prepared, don't count against limit)
    oath_spells_known TEXT, -- JSON array of oath spells

    -- Spellcasting
    spells_prepared INTEGER DEFAULT 0, -- Number of spells currently prepared
    max_spells_prepared INTEGER DEFAULT 0, -- Charisma modifier + half paladin level

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    PRIMARY KEY (character_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_paladin_features_character_id ON paladin_features(character_id);

-- Insert Paladin class into classes table if not exists
INSERT OR IGNORE INTO classes (
    id, name, description, hit_die, primary_ability, skill_choices,
    starting_equipment, equipment_choices, weapon_proficiencies,
    armor_proficiencies, item_proficiencies
) VALUES (
    'paladin',
    'Paladin',
    'Holy warriors bound by sacred oaths to uphold justice, virtue, and righteousness. They wield divine magic to heal allies and smite enemies.',
    10, -- d10 hit die
    'charisma',
    2, -- 2 skills from: Athletics, Insight, Intimidation, Medicine, Persuasion, Religion
    'chain_mail,shield,javelin_5,holy_symbol,explorers_pack', -- Starting equipment
    'martial_weapons,simple_weapons,all_armor,shields', -- Equipment choices
    'simple_weapons,martial_weapons', -- Weapon proficiencies
    'all_armor,shields', -- Armor proficiencies
    'none' -- No tool proficiencies
);

-- Insert Paladin subclasses (Sacred Oaths)
INSERT OR IGNORE INTO subclasses (
    id, class_id, name, description, selection_level
) VALUES
    ('devotion', 'paladin', 'Oath of Devotion', 'Paladins who commit themselves to the loftiest ideals of justice, virtue, and order', 3),
    ('ancients', 'paladin', 'Oath of the Ancients', 'Paladins who preserve the light against the encroaching darkness', 3),
    ('vengeance', 'paladin', 'Oath of Vengeance', 'Paladins who pursue justice through any means necessary', 3),
    ('crown', 'paladin', 'Oath of the Crown', 'Paladins who swear loyalty to law, civilization, and their sovereign', 3);

-- Add Paladin to class_features_progression table
INSERT OR IGNORE INTO class_features_progression (
    class_id, level, feature_name, feature_type, description
) VALUES
    -- Level 1
    ('paladin', 1, 'Divine Sense', 'passive', 'Detect celestials, fiends, and undead within 60 feet'),
    ('paladin', 1, 'Lay on Hands', 'resource', 'Heal wounds using a pool of healing power'),

    -- Level 2
    ('paladin', 2, 'Fighting Style', 'passive', 'Choose a fighting style specialization'),
    ('paladin', 2, 'Spellcasting', 'passive', 'Cast paladin spells using Charisma as spellcasting ability'),
    ('paladin', 2, 'Divine Smite', 'action', 'Expend spell slots to deal extra radiant damage on weapon hits'),

    -- Level 3
    ('paladin', 3, 'Sacred Oath', 'passive', 'Choose your sacred oath subclass'),
    ('paladin', 3, 'Channel Divinity', 'resource', 'Channel divine energy to fuel magical effects'),
    ('paladin', 3, 'Oath Spells', 'passive', 'Gain oath-specific spells that are always prepared'),

    -- Level 4
    ('paladin', 4, 'Ability Score Improvement', 'passive', 'Increase one ability score by 2, or two ability scores by 1 each'),

    -- Level 5
    ('paladin', 5, 'Extra Attack', 'passive', 'Make two attacks when you take the Attack action'),
    ('paladin', 5, '2nd-level Spells', 'passive', 'You can now learn and cast 2nd-level spells'),

    -- Level 6
    ('paladin', 6, 'Aura of Protection', 'passive', 'You and friendly creatures within 10 feet add your Charisma modifier to saving throws'),

    -- Level 7
    ('paladin', 7, 'Oath Feature', 'passive', 'Your sacred oath grants you additional features'),

    -- Level 8
    ('paladin', 8, 'Ability Score Improvement', 'passive', 'Increase one ability score by 2, or two ability scores by 1 each'),

    -- Level 9
    ('paladin', 9, '3rd-level Spells', 'passive', 'You can now learn and cast 3rd-level spells'),

    -- Level 10
    ('paladin', 10, 'Aura of Courage', 'passive', 'You and friendly creatures within 10 feet cannot be frightened'),

    -- Level 11
    ('paladin', 11, 'Improved Divine Smite', 'passive', 'All weapon attacks deal extra radiant damage'),

    -- Level 12
    ('paladin', 12, 'Ability Score Improvement', 'passive', 'Increase one ability score by 2, or two ability scores by 1 each'),

    -- Level 13
    ('paladin', 13, '4th-level Spells', 'passive', 'You can now learn and cast 4th-level spells'),

    -- Level 14
    ('paladin', 14, 'Cleansing Touch', 'resource', 'End one spell affecting yourself or a willing creature you touch'),

    -- Level 15
    ('paladin', 15, 'Oath Feature', 'passive', 'Your sacred oath grants you additional features'),

    -- Level 16
    ('paladin', 16, 'Ability Score Improvement', 'passive', 'Increase one ability score by 2, or two ability scores by 1 each'),

    -- Level 17
    ('paladin', 17, '5th-level Spells', 'passive', 'You can now learn and cast 5th-level spells'),

    -- Level 18
    ('paladin', 18, 'Aura Improvements', 'passive', 'Your aura range increases to 30 feet'),

    -- Level 19
    ('paladin', 19, 'Ability Score Improvement', 'passive', 'Increase one ability score by 2, or two ability scores by 1 each'),

    -- Level 20
    ('paladin', 20, 'Oath Feature', 'passive', 'Your sacred oath grants you its ultimate feature');

-- Update schema version
UPDATE schema_version SET version = 14, description = 'Paladin class implementation with oath system' WHERE version = (SELECT MAX(version) FROM schema_version);