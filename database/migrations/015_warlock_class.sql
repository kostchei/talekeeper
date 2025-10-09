-- Migration 015: Warlock Class Implementation
-- Phase 2.4: Warlock with Pact Magic System

-- Create warlock features table for tracking patron, pact boon, and invocations
CREATE TABLE IF NOT EXISTS warlock_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,

    -- Pact Magic Slots (All same level, recover on short rest)
    pact_slots_current INTEGER DEFAULT 1,
    pact_slots_max INTEGER DEFAULT 1,
    pact_slot_level INTEGER DEFAULT 1,

    -- Warlock-Specific Features
    patron TEXT,
    pact_boon TEXT,
    eldritch_invocations TEXT DEFAULT '[]',

    -- Legacy columns (for backwards compatibility)
    invocations_known TEXT DEFAULT '[]',
    mystic_arcanum_spells TEXT DEFAULT '[]',
    last_pact_reset TEXT,
    pact_slots INTEGER DEFAULT 1,

    -- Magical Cunning (Level 2+)
    magical_cunning_used BOOLEAN DEFAULT 0,
    last_magical_cunning TEXT,

    -- Contact Patron (Level 9+)
    contact_patron_used BOOLEAN DEFAULT 0,
    last_contact_patron TEXT,

    -- Mystic Arcanum Usage (Levels 11, 13, 15, 17)
    arcanum_6_used BOOLEAN DEFAULT 0,
    arcanum_6_spell TEXT,
    arcanum_7_used BOOLEAN DEFAULT 0,
    arcanum_7_spell TEXT,
    arcanum_8_used BOOLEAN DEFAULT 0,
    arcanum_8_spell TEXT,
    arcanum_9_used BOOLEAN DEFAULT 0,
    arcanum_9_spell TEXT,

    -- Fiend Patron Specific
    dark_ones_luck_uses INTEGER DEFAULT 0,
    fiendish_resilience_type TEXT,
    hurl_through_hell_used BOOLEAN DEFAULT 0,

    -- Patron Features (Generic)
    patron_feature_uses_current INTEGER DEFAULT 0,
    patron_feature_uses_max INTEGER DEFAULT 0,

    PRIMARY KEY (character_id),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_warlock_features_character_id ON warlock_features(character_id);

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
    (20, 4, 5, 10, 4, 15);

-- Create warlock_patron_features table for patron-specific features
CREATE TABLE IF NOT EXISTS warlock_patron_features (
    id TEXT PRIMARY KEY,
    patron TEXT NOT NULL,
    level INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    description TEXT,
    effect_type TEXT,
    effect_data TEXT
);

-- Populate Fiend Patron features
INSERT OR IGNORE INTO warlock_patron_features (id, patron, level, feature_name, description, effect_type, effect_data)
VALUES
    ('fiend_dark_ones_blessing', 'Fiend', 3, 'Dark One''s Blessing',
     'When you reduce a hostile creature to 0 hit points, you gain temporary hit points equal to your Charisma modifier + your warlock level (minimum 1). You also gain this benefit if someone else reduces a hostile creature to 0 hit points within 10 feet of you.',
     'passive',
     '{"trigger": "enemy_defeated", "temp_hp_formula": "cha_mod + warlock_level", "range": 10}'),

    ('fiend_patron_spells', 'Fiend', 3, 'Fiend Spells',
     'The magic of your patron ensures you always have certain spells ready.',
     'spell_list',
     '{"3": ["burning_hands", "command", "scorching_ray", "suggestion"], "5": ["fireball", "stinking_cloud"], "7": ["fire_shield", "wall_of_fire"], "9": ["geas", "insect_plague"]}'),

    ('fiend_dark_ones_luck', 'Fiend', 6, 'Dark One''s Own Luck',
     'You can call on your fiendish patron to alter fate in your favor. When you make an ability check or a saving throw, you can use this feature to add 1d10 to your roll. You can do so after seeing the roll but before any of the roll''s effects occur. Once you use this feature, you can''t use it again until you finish a short or long rest.',
     'active',
     '{"bonus_dice": "1d10", "timing": "after_roll", "uses_per_rest": "cha_mod", "rest_type": "long"}'),

    ('fiend_fiendish_resilience', 'Fiend', 10, 'Fiendish Resilience',
     'You can choose one damage type when you finish a short or long rest. You gain resistance to that damage type until you choose a different one with this feature. Damage from magical weapons or silver weapons ignores this resistance.',
     'active',
     '{"resistance_choice": true, "reset_on_rest": true, "exclude": ["force"]}'),

    ('fiend_hurl_through_hell', 'Fiend', 14, 'Hurl Through Hell',
     'When you hit a creature with an attack, you can use this feature to instantly transport the target through the lower planes. The creature disappears and hurtles through a nightmare landscape. At the end of your next turn, the target returns to the space it previously occupied, or the nearest unoccupied space. If the target is not a fiend, it takes 10d10 psychic damage as it reels from its horrific experience. Once you use this feature, you can''t use it again until you finish a long rest.',
     'active',
     '{"trigger": "on_hit", "damage": "10d10", "damage_type": "psychic", "fiend_immune": true, "duration_turns": 1, "uses_per_rest": 1, "rest_type": "long"}');

-- Add missing D&D 2024 invocations
INSERT OR IGNORE INTO invocations (id, name, description, prerequisites, effect_type, effect_data)
VALUES
    ('ascendant_step', 'Ascendant Step', 'You can cast levitate on yourself at will, without expending a spell slot or material components', '{"level": 5}', 'active', '{"spell": "levitate", "cost": "none", "target": "self"}'),

    ('eldritch_mind', 'Eldritch Mind', 'You have advantage on Constitution saving throws that you make to maintain your concentration on a spell', '{"level": 2}', 'passive', '{"concentration_advantage": true}'),

    ('eldritch_smite', 'Eldritch Smite', 'Once per turn when you hit a creature with your pact weapon, you can expend a warlock spell slot to deal an extra 1d8 force damage to the target, plus another 1d8 per level of the spell slot, and you can knock the target prone if it is Huge or smaller', '{"level": 5, "pact": "blade"}', 'active', '{"damage_per_slot_level": "1d8", "damage_type": "force", "base_dice": 1, "can_knock_prone": true, "size_limit": "Huge"}'),

    ('gift_of_the_depths', 'Gift of the Depths', 'You can breathe underwater, and you gain a swimming speed equal to your walking speed. You can also cast water breathing once without expending a spell slot. You regain the ability to do so when you finish a long rest', '{"level": 5}', 'passive', '{"breathe_underwater": true, "swim_speed": "walking", "spell": "water_breathing", "spell_uses": 1}'),

    ('gift_of_the_protectors', 'Gift of the Protectors', 'A new page appears in your Book of Shadows. With your permission, a creature can use its action to write its name on that page, which can contain a number of names equal to your proficiency bonus. When any creature whose name is on the page is reduced to 0 hit points but not killed outright, the creature magically drops to 1 hit point instead. Once this magic is triggered, no creature can benefit from it until you finish a long rest', '{"level": 9, "pact": "tome"}', 'passive', '{"prevent_death": true, "max_creatures": "proficiency_bonus", "uses_per_rest": 1}'),

    ('investment_of_chain_master', 'Investment of the Chain Master', 'When you cast find familiar, you infuse the summoned familiar with a measure of your eldritch power, granting the creature additional benefits', '{"level": 5, "pact": "chain"}', 'passive', '{"familiar_fly_swim": 40, "familiar_bonus_action_attack": true, "familiar_damage_conversion": ["necrotic", "radiant"], "familiar_save_dc": "warlock", "familiar_resistance_reaction": true}'),

    ('lessons_of_the_first_ones', 'Lessons of the First Ones', 'You have received knowledge from an elder entity of the multiverse, allowing you to gain one Origin feat of your choice', '{"level": 2}', 'passive', '{"grant_origin_feat": true, "repeatable": true}'),

    ('devouring_blade', 'Devouring Blade', 'The Extra Attack of your Thirsting Blade invocation confers two extra attacks rather than one', '{"level": 12, "invocation": "thirsting_blade"}', 'passive', '{"extra_attacks": 2}'),

    ('visions_of_distant_realms', 'Visions of Distant Realms', 'You can cast arcane eye at will, without expending a spell slot', '{"level": 9}', 'active', '{"spell": "arcane_eye", "cost": "none"}'),

    ('eldritch_spear', 'Eldritch Spear', 'When you cast eldritch blast, its range is 300 feet', '{"level": 2, "cantrip": "eldritch_blast"}', 'spell_modification', '{"spell": "eldritch_blast", "range": 300}');

-- Update invocations with corrected D&D 2024 prerequisites
UPDATE invocations SET prerequisites = '{"level": 2, "cantrip": "eldritch_blast"}' WHERE id = 'agonizing_blast';
UPDATE invocations SET prerequisites = '{"level": 2}' WHERE id = 'devils_sight';
UPDATE invocations SET prerequisites = '{"level": 5}' WHERE id = 'one_with_shadows';
UPDATE invocations SET prerequisites = '{"level": 2, "cantrip": "eldritch_blast"}' WHERE id = 'repelling_blast';
UPDATE invocations SET prerequisites = '{"level": 7}' WHERE id = 'whispers_of_the_grave';