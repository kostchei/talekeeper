-- Migration 015: Warlock Class Implementation (Simplified for existing schema)
-- Phase 2.4: Warlock with Pact Magic System

-- Create warlock features table for tracking patron, pact boon, and invocations
CREATE TABLE IF NOT EXISTS warlock_features (
    character_id TEXT PRIMARY KEY,
    patron TEXT,
    pact_boon TEXT,
    invocations_known TEXT, -- JSON array of invocation IDs
    mystic_arcanum_spells TEXT, -- JSON array of spell IDs for 6th-9th level spells
    last_pact_reset TEXT,
    pact_slots INTEGER DEFAULT 1,
    pact_slot_level INTEGER DEFAULT 1,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- Create warlock invocations table for tracking learned invocations
CREATE TABLE IF NOT EXISTS warlock_invocations (
    character_id TEXT NOT NULL,
    invocation_id TEXT NOT NULL,
    learned_at_level INTEGER,
    PRIMARY KEY (character_id, invocation_id),
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- Create invocations reference table
CREATE TABLE IF NOT EXISTS invocations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    prerequisites TEXT, -- JSON object with level, pact, spell requirements
    effect_type TEXT, -- passive, active, spell_modification
    effect_data TEXT -- JSON data for the effect
);

-- Insert Warlock class if not exists
INSERT OR IGNORE INTO classes (id, name, description, hit_die, primary_ability, skill_choices, starting_equipment)
VALUES (
    'warlock',
    'Warlock',
    'A wielder of magic that is derived from a bargain with an extraplanar entity',
    8,
    'Charisma',
    2,
    'leather armor, simple weapon, component pouch or arcane focus, scholar pack or dungeoneer pack, dagger x2'
);

-- Insert Warlock subclasses
INSERT OR IGNORE INTO subclasses (id, class_id, name, description)
VALUES
    ('warlock_fiend', 'warlock', 'Fiend', 'You have made a pact with a fiend from the lower planes of existence'),
    ('warlock_archfey', 'warlock', 'Archfey', 'Your patron is a lord or lady of the fey, a creature of legend'),
    ('warlock_great_old_one', 'warlock', 'Great Old One', 'Your patron is a mysterious entity whose nature is utterly foreign');

-- Insert basic Eldritch Invocations (simplified for testing)
INSERT OR IGNORE INTO invocations (id, name, description, prerequisites, effect_type, effect_data)
VALUES
    ('agonizing_blast', 'Agonizing Blast', 'Add Charisma modifier to eldritch blast damage', '{"cantrip": "eldritch_blast"}', 'spell_modification', '{"spell": "eldritch_blast", "damage_bonus": "charisma"}'),
    ('armor_of_shadows', 'Armor of Shadows', 'Cast mage armor at will', '{}', 'active', '{"spell": "mage_armor", "cost": "none", "target": "self"}'),
    ('devils_sight', 'Devils Sight', 'See in magical darkness', '{}', 'passive', '{"darkvision": 120, "magical_darkness": true}'),
    ('fiendish_vigor', 'Fiendish Vigor', 'Cast false life at will', '{}', 'active', '{"spell": "false_life", "cost": "none", "target": "self", "level": 1}'),
    ('thirsting_blade', 'Thirsting Blade', 'Extra attack with pact weapon', '{"level": 5, "pact": "blade"}', 'passive', '{"extra_attack": 1}');

-- Warlock pact slot progression table
CREATE TABLE IF NOT EXISTS warlock_pact_progression (
    level INTEGER PRIMARY KEY,
    num_slots INTEGER NOT NULL,
    slot_level INTEGER NOT NULL,
    invocations_known INTEGER NOT NULL,
    cantrips_known INTEGER NOT NULL,
    spells_known INTEGER NOT NULL
);

-- Insert pact progression data
INSERT OR IGNORE INTO warlock_pact_progression (level, num_slots, slot_level, invocations_known, cantrips_known, spells_known)
VALUES
    (1, 1, 1, 0, 2, 2),
    (2, 2, 1, 2, 2, 3),
    (3, 2, 2, 2, 2, 4),
    (4, 2, 2, 2, 3, 5),
    (5, 2, 3, 3, 3, 6),
    (6, 2, 3, 3, 3, 7),
    (7, 2, 4, 4, 3, 8),
    (8, 2, 4, 4, 3, 9),
    (9, 2, 5, 5, 3, 10),
    (10, 2, 5, 5, 4, 10),
    (11, 3, 5, 5, 4, 11),
    (12, 3, 5, 6, 4, 11),
    (13, 3, 5, 6, 4, 12),
    (14, 3, 5, 6, 4, 12),
    (15, 3, 5, 7, 4, 13),
    (16, 3, 5, 7, 4, 13),
    (17, 4, 5, 7, 4, 14),
    (18, 4, 5, 8, 4, 14),
    (19, 4, 5, 8, 4, 15),
    (20, 4, 5, 8, 4, 15);

-- Create a simple spellcasting tracking table if it doesn't exist
CREATE TABLE IF NOT EXISTS character_spellcasting (
    character_id TEXT NOT NULL,
    spellcasting_class TEXT NOT NULL,
    spellcasting_ability TEXT,
    spell_save_dc INTEGER,
    spell_attack_bonus INTEGER,
    prepared_spells TEXT, -- JSON array
    known_spells TEXT, -- JSON array
    cantrips_known INTEGER,
    ritual_casting INTEGER DEFAULT 0,
    spellcasting_focus TEXT,
    PRIMARY KEY (character_id, spellcasting_class),
    FOREIGN KEY (character_id) REFERENCES characters(id)
);