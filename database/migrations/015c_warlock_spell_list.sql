-- Migration 015c: Warlock Spell List
-- Adds all Warlock spells to spell_class_lists table

-- Warlock Cantrips (Level 0)
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    ('chill_touch', 'warlock', FALSE, NULL),
    ('eldritch_blast', 'warlock', FALSE, NULL),
    ('mage_hand', 'warlock', FALSE, NULL),
    ('minor_illusion', 'warlock', FALSE, NULL),
    ('poison_spray', 'warlock', FALSE, NULL),
    ('prestidigitation', 'warlock', FALSE, NULL),
    ('true_strike', 'warlock', FALSE, NULL);

-- Level 1 Warlock Spells
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    ('bane', 'warlock', FALSE, NULL),
    ('charm_person', 'warlock', FALSE, NULL),
    ('comprehend_languages', 'warlock', FALSE, NULL),
    ('detect_magic', 'warlock', FALSE, NULL),
    ('expeditious_retreat', 'warlock', FALSE, NULL),
    ('hellish_rebuke', 'warlock', FALSE, NULL),
    ('hex', 'warlock', FALSE, NULL),
    ('hideous_laughter', 'warlock', FALSE, NULL),
    ('illusory_script', 'warlock', FALSE, NULL),
    ('protection_from_evil_and_good', 'warlock', FALSE, NULL),
    ('speak_with_animals', 'warlock', FALSE, NULL),
    ('unseen_servant', 'warlock', FALSE, NULL);

-- Level 2 Warlock Spells
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    ('darkness', 'warlock', FALSE, NULL),
    ('enthrall', 'warlock', FALSE, NULL),
    ('hold_person', 'warlock', FALSE, NULL),
    ('invisibility', 'warlock', FALSE, NULL),
    ('mind_spike', 'warlock', FALSE, NULL),
    ('mirror_image', 'warlock', FALSE, NULL),
    ('misty_step', 'warlock', FALSE, NULL),
    ('ray_of_enfeeblement', 'warlock', FALSE, NULL),
    ('spider_climb', 'warlock', FALSE, NULL),
    ('suggestion', 'warlock', FALSE, NULL);

-- Level 3 Warlock Spells
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    ('counterspell', 'warlock', FALSE, NULL),
    ('dispel_magic', 'warlock', FALSE, NULL),
    ('fear', 'warlock', FALSE, NULL),
    ('fly', 'warlock', FALSE, NULL),
    ('gaseous_form', 'warlock', FALSE, NULL),
    ('hypnotic_pattern', 'warlock', FALSE, NULL),
    ('magic_circle', 'warlock', FALSE, NULL),
    ('major_image', 'warlock', FALSE, NULL),
    ('remove_curse', 'warlock', FALSE, NULL),
    ('tongues', 'warlock', FALSE, NULL),
    ('vampiric_touch', 'warlock', FALSE, NULL);

-- Level 4 Warlock Spells
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    ('banishment', 'warlock', FALSE, NULL),
    ('blight', 'warlock', FALSE, NULL),
    ('charm_monster', 'warlock', FALSE, NULL),
    ('dimension_door', 'warlock', FALSE, NULL),
    ('hallucinatory_terrain', 'warlock', FALSE, NULL);

-- Level 5 Warlock Spells
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    ('contact_other_plane', 'warlock', FALSE, NULL),
    ('dream', 'warlock', FALSE, NULL),
    ('hold_monster', 'warlock', FALSE, NULL),
    ('mislead', 'warlock', FALSE, NULL),
    ('planar_binding', 'warlock', FALSE, NULL),
    ('scrying', 'warlock', FALSE, NULL),
    ('teleportation_circle', 'warlock', FALSE, NULL);

-- Level 6 Warlock Spells (Mystic Arcanum)
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    ('circle_of_death', 'warlock', FALSE, NULL),
    ('create_undead', 'warlock', FALSE, NULL),
    ('eyebite', 'warlock', FALSE, NULL),
    ('true_seeing', 'warlock', FALSE, NULL);

-- Level 7 Warlock Spells (Mystic Arcanum)
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    ('etherealness', 'warlock', FALSE, NULL),
    ('finger_of_death', 'warlock', FALSE, NULL),
    ('forcecage', 'warlock', FALSE, NULL),
    ('plane_shift', 'warlock', FALSE, NULL);

-- Level 8 Warlock Spells (Mystic Arcanum)
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    ('befuddlement', 'warlock', FALSE, NULL),
    ('demiplane', 'warlock', FALSE, NULL),
    ('dominate_monster', 'warlock', FALSE, NULL),
    ('glibness', 'warlock', FALSE, NULL),
    ('power_word_stun', 'warlock', FALSE, NULL);

-- Level 9 Warlock Spells (Mystic Arcanum)
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    ('astral_projection', 'warlock', FALSE, NULL),
    ('foresight', 'warlock', FALSE, NULL),
    ('gate', 'warlock', FALSE, NULL),
    ('imprisonment', 'warlock', FALSE, NULL),
    ('power_word_kill', 'warlock', FALSE, NULL),
    ('true_polymorph', 'warlock', FALSE, NULL),
    ('weird', 'warlock', FALSE, NULL);

-- Fiend Patron Bonus Spells (always prepared at specific levels)
INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id, is_bonus_spell, source_feature)
VALUES
    -- Level 3
    ('burning_hands', 'warlock', TRUE, 'fiend_patron'),
    ('command', 'warlock', TRUE, 'fiend_patron'),
    ('scorching_ray', 'warlock', TRUE, 'fiend_patron'),
    ('suggestion', 'warlock', TRUE, 'fiend_patron'),
    -- Level 5
    ('fireball', 'warlock', TRUE, 'fiend_patron'),
    ('stinking_cloud', 'warlock', TRUE, 'fiend_patron'),
    -- Level 7
    ('fire_shield', 'warlock', TRUE, 'fiend_patron'),
    ('wall_of_fire', 'warlock', TRUE, 'fiend_patron'),
    -- Level 9
    ('geas', 'warlock', TRUE, 'fiend_patron'),
    ('insect_plague', 'warlock', TRUE, 'fiend_patron');
