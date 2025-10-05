-- Migration 015: Warlock Class Implementation
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

-- Warlock spell list would go here but spell_lists table doesn't exist yet
-- This would be added when spell system is fully implemented

-- Insert basic Eldritch Invocations
INSERT OR IGNORE INTO invocations (id, name, description, prerequisites, effect_type, effect_data)
VALUES
    ('agonizing_blast', 'Agonizing Blast', 'When you cast eldritch blast, add your Charisma modifier to the damage', '{"cantrip": "eldritch_blast"}', 'spell_modification', '{"spell": "eldritch_blast", "damage_bonus": "charisma"}'),
    ('armor_of_shadows', 'Armor of Shadows', 'You can cast mage armor on yourself at will', '{}', 'active', '{"spell": "mage_armor", "cost": "none", "target": "self"}'),
    ('beast_speech', 'Beast Speech', 'You can cast speak with animals at will', '{}', 'active', '{"spell": "speak_with_animals", "cost": "none"}'),
    ('beguiling_influence', 'Beguiling Influence', 'You gain proficiency in the Deception and Persuasion skills', '{}', 'passive', '{"skills": ["Deception", "Persuasion"]}'),
    ('book_of_ancient_secrets', 'Book of Ancient Secrets', 'You can now inscribe magical rituals in your Book of Shadows', '{"pact": "tome"}', 'passive', '{"ritual_casting": true}'),
    ('devils_sight', 'Devils Sight', 'You can see normally in darkness, both magical and nonmagical, to a distance of 120 feet', '{}', 'passive', '{"darkvision": 120, "magical_darkness": true}'),
    ('eldritch_sight', 'Eldritch Sight', 'You can cast detect magic at will', '{}', 'active', '{"spell": "detect_magic", "cost": "none"}'),
    ('eldritch_spear', 'Eldritch Spear', 'When you cast eldritch blast, its range is 300 feet', '{"cantrip": "eldritch_blast"}', 'spell_modification', '{"spell": "eldritch_blast", "range": 300}'),
    ('eyes_of_the_rune_keeper', 'Eyes of the Rune Keeper', 'You can read all writing', '{}', 'passive', '{"read_all_writing": true}'),
    ('fiendish_vigor', 'Fiendish Vigor', 'You can cast false life on yourself at will as a 1st-level spell', '{}', 'active', '{"spell": "false_life", "cost": "none", "target": "self", "level": 1}'),
    ('gaze_of_two_minds', 'Gaze of Two Minds', 'You can use your action to touch a willing humanoid and perceive through its senses', '{}', 'active', '{"action": "perceive_through_other"}'),
    ('lifedrinker', 'Lifedrinker', 'When you hit a creature with your pact weapon, deal extra necrotic damage equal to your Charisma modifier', '{"level": 12, "pact": "blade"}', 'passive', '{"pact_weapon_damage": "charisma", "damage_type": "necrotic"}'),
    ('mask_of_many_faces', 'Mask of Many Faces', 'You can cast disguise self at will', '{}', 'active', '{"spell": "disguise_self", "cost": "none"}'),
    ('master_of_myriad_forms', 'Master of Myriad Forms', 'You can cast alter self at will', '{"level": 15}', 'active', '{"spell": "alter_self", "cost": "none"}'),
    ('misty_visions', 'Misty Visions', 'You can cast silent image at will', '{}', 'active', '{"spell": "silent_image", "cost": "none"}'),
    ('one_with_shadows', 'One with Shadows', 'When in darkness, you can use your action to become invisible', '{"level": 5}', 'active', '{"action": "invisibility_in_darkness"}'),
    ('otherworldly_leap', 'Otherworldly Leap', 'You can cast jump on yourself at will', '{"level": 9}', 'active', '{"spell": "jump", "cost": "none", "target": "self"}'),
    ('repelling_blast', 'Repelling Blast', 'When you hit a creature with eldritch blast, push it up to 10 feet away', '{"cantrip": "eldritch_blast"}', 'spell_modification', '{"spell": "eldritch_blast", "push": 10}'),
    ('thirsting_blade', 'Thirsting Blade', 'You can attack twice with your pact weapon', '{"level": 5, "pact": "blade"}', 'passive', '{"extra_attack": 1}'),
    ('voice_of_the_chain_master', 'Voice of the Chain Master', 'You can communicate telepathically with your familiar and perceive through its senses', '{"pact": "chain"}', 'passive', '{"familiar_telepathy": true, "familiar_perception": true}'),
    ('whispers_of_the_grave', 'Whispers of the Grave', 'You can cast speak with dead at will', '{"level": 9}', 'active', '{"spell": "speak_with_dead", "cost": "none"}'),
    ('witch_sight', 'Witch Sight', 'You can see the true form of shapeshifters and creatures concealed by illusion', '{"level": 15}', 'passive', '{"true_sight": 30}');

-- Add Warlock progression data
INSERT OR IGNORE INTO class_features (class_id, level, feature_name, description)
VALUES
    ('warlock', 1, 'Pact Magic', 'You can cast warlock spells using pact magic slots that recover on a short rest'),
    ('warlock', 1, 'Otherworldly Patron', 'You strike a bargain with an otherworldly being'),
    ('warlock', 2, 'Eldritch Invocations', 'You gain 2 invocations of your choice'),
    ('warlock', 3, 'Pact Boon', 'Your patron bestows a gift: Pact of the Blade, Chain, or Tome'),
    ('warlock', 4, 'Ability Score Improvement', 'Increase ability scores or take a feat'),
    ('warlock', 5, 'Invocation Improvement', 'You learn one additional invocation'),
    ('warlock', 6, 'Otherworldly Patron Feature', 'Gain a feature from your patron'),
    ('warlock', 7, 'Invocation Improvement', 'You learn one additional invocation'),
    ('warlock', 8, 'Ability Score Improvement', 'Increase ability scores or take a feat'),
    ('warlock', 9, 'Invocation Improvement', 'You learn one additional invocation'),
    ('warlock', 10, 'Otherworldly Patron Feature', 'Gain a feature from your patron'),
    ('warlock', 11, 'Mystic Arcanum (6th level)', 'You can cast one 6th-level spell once per long rest'),
    ('warlock', 12, 'Ability Score Improvement', 'Increase ability scores or take a feat'),
    ('warlock', 12, 'Invocation Improvement', 'You learn one additional invocation'),
    ('warlock', 13, 'Mystic Arcanum (7th level)', 'You can cast one 7th-level spell once per long rest'),
    ('warlock', 14, 'Otherworldly Patron Feature', 'Gain a feature from your patron'),
    ('warlock', 15, 'Mystic Arcanum (8th level)', 'You can cast one 8th-level spell once per long rest'),
    ('warlock', 15, 'Invocation Improvement', 'You learn one additional invocation'),
    ('warlock', 16, 'Ability Score Improvement', 'Increase ability scores or take a feat'),
    ('warlock', 17, 'Mystic Arcanum (9th level)', 'You can cast one 9th-level spell once per long rest'),
    ('warlock', 18, 'Invocation Improvement', 'You learn one additional invocation'),
    ('warlock', 19, 'Ability Score Improvement', 'Increase ability scores or take a feat'),
    ('warlock', 20, 'Eldritch Master', 'You can regain all expended pact slots once per day with 1 minute of rest');

-- Warlock pact slot progression table
CREATE TABLE IF NOT EXISTS warlock_pact_progression (
    level INTEGER PRIMARY KEY,
    num_slots INTEGER NOT NULL,
    slot_level INTEGER NOT NULL,
    invocations_known INTEGER NOT NULL,
    cantrips_known INTEGER NOT NULL,
    spells_known INTEGER NOT NULL
);

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