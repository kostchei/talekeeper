-- TaleKeeper Test Characters
-- Generated: 2025-09-13
-- Seven test characters with various builds for testing combat and features

-- Create save slots for test characters
INSERT INTO save_slots (id, slot_number, character_name, character_level, last_played, is_occupied)
VALUES 
    ('1', 1, 'Valerius', 1, datetime('now'), 1),
    ('2', 2, 'Achelos', 1, datetime('now'), 1),
    ('3', 3, 'Roland', 1, datetime('now'), 1),
    ('4', 4, 'Ragnar', 1, datetime('now'), 1),
    ('5', 5, 'Thrud', 1, datetime('now'), 1),
    ('6', 6, 'Gath', 1, datetime('now'), 1),
    ('7', 7, 'Gurnison', 1, datetime('now'), 1);

-- Valerius: Dexterity-based Fighter with Alert, Lucky, and Dueling
INSERT INTO characters (
    id, save_slot_id, name, race_id, class_id, background_id, level, experience_points,
    strength, dexterity, constitution, intelligence, wisdom, charisma,
    armor_class, hit_points_max, hit_points_current, max_hit_points, current_hit_points,
    hit_dice_max, hit_dice_current, equipment_main_hand, equipment_armor,
    created_at, notes
)
VALUES (
    'test_valerius',
    '1',
    'Valerius',
    'human',
    'fighter',
    'soldier',
    1,
    0,
    10, 20, 16, 12, 8, 12,  -- Stats
    15,  -- AC (Studded leather 12 + 5 Dex)
    13, 13, 13, 13,  -- HP (10 + 3 Con)
    1, 1,  -- Hit dice
    'Rapier', 'Studded Leather', 
    datetime('now'),
    'Dex-based duelist with Alert and Lucky feats'
);

-- Achelos: Defensive Fighter with Defense fighting style
INSERT INTO characters (
    id, save_slot_id, name, race_id, class_id, background_id, level, experience_points,
    strength, dexterity, constitution, intelligence, wisdom, charisma,
    armor_class, hit_points_max, hit_points_current, max_hit_points, current_hit_points,
    hit_dice_max, hit_dice_current, equipment_main_hand, equipment_armor, equipment_shield,
    created_at, notes
)
VALUES (
    'test_achelos',
    '2',
    'Achelos',
    'human',
    'fighter',
    'farmer',
    1,
    0,
    16, 15, 17, 15, 15, 15,  -- Stats
    19,  -- AC (Scale Mail 14 + 2 Dex + Defense +1 = 17, plus shield would be 19)
    15, 15, 15, 15,  -- HP (10 + 3 Con)
    1, 1,  -- Hit dice
    'Longsword', 'Scale Mail', '',
    datetime('now'),
    'Well-rounded fighter with Defense fighting style'
);

-- Roland: Heavy armor tank with Tough, Defense, and Savage Attacker
INSERT INTO characters (
    id, save_slot_id, name, race_id, class_id, background_id, level, experience_points,
    strength, dexterity, constitution, intelligence, wisdom, charisma,
    armor_class, hit_points_max, hit_points_current, max_hit_points, current_hit_points,
    hit_dice_max, hit_dice_current, equipment_main_hand, equipment_armor, equipment_shield,
    created_at, notes
)
VALUES (
    'test_roland',
    '3',
    'Roland',
    'human',
    'fighter',
    'noble',
    1,
    0,
    18, 10, 18, 10, 12, 10,  -- Stats
    20,  -- AC (Plate 18 + Shield 2)
    14, 14, 14, 14,  -- HP (10 + 4 Con)
    1, 1,  -- Hit dice
    'Longsword', 'Plate Armor', 'Shield',
    datetime('now'),
    'Heavy armor tank with Savage Attacker'
);

-- Ragnar: Barbarian with Tough and Lucky
INSERT INTO characters (
    id, save_slot_id, name, race_id, class_id, background_id, level, experience_points,
    strength, dexterity, constitution, intelligence, wisdom, charisma,
    armor_class, hit_points_max, hit_points_current, max_hit_points, current_hit_points,
    hit_dice_max, hit_dice_current, equipment_main_hand, equipment_shield,
    created_at, notes
)
VALUES (
    'test_ragnar',
    '4',
    'Ragnar',
    'human',
    'barbarian',
    'outlander',
    1,
    0,
    18, 16, 18, 4, 12, 10,  -- Stats
    15,  -- AC (10 + 3 Dex + 4 Con unarmored defense - using shield)
    16, 16, 16, 16,  -- HP (12 + 4 Con)
    1, 1,  -- Hit dice (d12)
    'Longsword', 'Shield',
    datetime('now'),
    'Barbarian with sword and board, Tough and Lucky feats'
);

-- Thrud: Glass cannon Barbarian with maxed physical stats
INSERT INTO characters (
    id, save_slot_id, name, race_id, class_id, background_id, level, experience_points,
    strength, dexterity, constitution, intelligence, wisdom, charisma,
    armor_class, hit_points_max, hit_points_current, max_hit_points, current_hit_points,
    hit_dice_max, hit_dice_current, equipment_main_hand,
    created_at, notes
)
VALUES (
    'test_thrud',
    '5',
    'Thrud',
    'human',
    'barbarian',
    'outlander',
    1,
    0,
    20, 20, 20, 3, 6, 9,  -- Stats
    15,  -- AC (10 + 5 Dex unarmored)
    17, 17, 17, 17,  -- HP (12 + 5 Con)
    1, 1,  -- Hit dice (d12)
    'Greataxe',
    datetime('now'),
    'Max physical stats barbarian with Greataxe'
);

-- Gath: Versatile Barbarian with dual wielding setup
INSERT INTO characters (
    id, save_slot_id, name, race_id, class_id, background_id, level, experience_points,
    strength, dexterity, constitution, intelligence, wisdom, charisma,
    armor_class, hit_points_max, hit_points_current, max_hit_points, current_hit_points,
    hit_dice_max, hit_dice_current, equipment_main_hand, equipment_off_hand, equipment_armor, equipment_shield,
    created_at, notes
)
VALUES (
    'test_gath',
    '6',
    'Gath',
    'human',
    'barbarian',
    'soldier',
    1,
    0,
    20, 14, 18, 4, 12, 10,  -- Stats
    14,  -- AC (Scale Mail 14 + 2 Dex max)
    16, 16, 16, 16,  -- HP (12 + 4 Con)
    1, 1,  -- Hit dice (d12)
    'Battleaxe', 'Handaxe', 'Scale Mail', '',
    datetime('now'),
    'Armored barbarian with dual wielding axes'
);

-- Gurnison: Dwarf Barbarian with Greataxe
INSERT INTO characters (
    id, save_slot_id, name, race_id, class_id, background_id, level, experience_points,
    strength, dexterity, constitution, intelligence, wisdom, charisma,
    armor_class, hit_points_max, hit_points_current, max_hit_points, current_hit_points,
    hit_dice_max, hit_dice_current, equipment_main_hand,
    created_at, notes
)
VALUES (
    'test_gurnison',
    '7',
    'Gurnison',
    'dwarf',
    'barbarian',
    'folk_hero',
    1,
    0,
    18, 20, 20, 8, 8, 4,  -- Stats
    15,  -- AC (10 + 5 Dex unarmored)
    17, 17, 17, 17,  -- HP (12 + 5 Con)
    1, 1,  -- Hit dice (d12)
    'Greataxe',
    datetime('now'),
    'Dwarf barbarian with max Con and Dex'
);

-- Add inventory for all characters
-- Valerius inventory
INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped, created_at)
VALUES 
    ('inv_val_rapier', 'test_valerius', 'Rapier', 'weapon', 1, 2.0, 'Finesse weapon', 25.0, 1, datetime('now')),
    ('inv_val_studded', 'test_valerius', 'Studded Leather', 'armor', 1, 13.0, 'Light armor, AC 12 + Dex', 45.0, 1, datetime('now')),
    ('inv_val_rations', 'test_valerius', 'Rations', 'consumable', 5, 2.0, 'One day of food', 0.5, 0, datetime('now')),
    ('inv_val_sack', 'test_valerius', 'Sack', 'gear', 1, 0.5, 'Holds 30 pounds', 0.01, 0, datetime('now')),
    ('inv_val_potion', 'test_valerius', 'Potion of Healing', 'consumable', 1, 0.5, 'Heals 2d4+2 HP', 50.0, 0, datetime('now'));

-- Achelos inventory
INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped, created_at)
VALUES
    ('inv_ach_longsword', 'test_achelos', 'Longsword', 'weapon', 1, 3.0, 'Versatile martial weapon', 15.0, 1, datetime('now')),
    ('inv_ach_scale', 'test_achelos', 'Scale Mail', 'armor', 1, 45.0, 'Medium armor, AC 14 + Dex (max 2)', 50.0, 1, datetime('now')),
    ('inv_ach_rations', 'test_achelos', 'Rations', 'consumable', 5, 2.0, 'One day of food', 0.5, 0, datetime('now')),
    ('inv_ach_sack', 'test_achelos', 'Sack', 'gear', 1, 0.5, 'Holds 30 pounds', 0.01, 0, datetime('now')),
    ('inv_ach_potion', 'test_achelos', 'Potion of Healing', 'consumable', 1, 0.5, 'Heals 2d4+2 HP', 50.0, 0, datetime('now'));

-- Roland inventory
INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped, created_at)
VALUES 
    ('inv_rol_sword', 'test_roland', 'Longsword', 'weapon', 1, 3.0, 'Versatile martial weapon', 15.0, 1, datetime('now')),
    ('inv_rol_plate', 'test_roland', 'Plate Armor', 'armor', 1, 65.0, 'Heavy armor, AC 18', 1500.0, 1, datetime('now')),
    ('inv_rol_shield', 'test_roland', 'Shield', 'shield', 1, 6.0, '+2 AC bonus', 10.0, 1, datetime('now')),
    ('inv_rol_rations', 'test_roland', 'Rations', 'consumable', 5, 2.0, 'One day of food', 0.5, 0, datetime('now')),
    ('inv_rol_backpack', 'test_roland', 'Backpack', 'gear', 1, 5.0, 'Holds 30 pounds', 2.0, 0, datetime('now')),
    ('inv_rol_potion', 'test_roland', 'Potion of Healing', 'consumable', 1, 0.5, 'Heals 2d4+2 HP', 50.0, 0, datetime('now')),
    ('inv_rol_healkit', 'test_roland', 'Healers Kit', 'gear', 1, 3.0, '10 uses, stabilize dying', 5.0, 0, datetime('now'));

-- Ragnar inventory
INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped, created_at)
VALUES 
    ('inv_rag_sword', 'test_ragnar', 'Longsword', 'weapon', 1, 3.0, 'Versatile martial weapon', 15.0, 1, datetime('now')),
    ('inv_rag_shield', 'test_ragnar', 'Shield', 'shield', 1, 6.0, '+2 AC bonus', 10.0, 1, datetime('now')),
    ('inv_rag_rations', 'test_ragnar', 'Rations', 'consumable', 5, 2.0, 'One day of food', 0.5, 0, datetime('now')),
    ('inv_rag_sack', 'test_ragnar', 'Sack', 'gear', 1, 0.5, 'Holds 30 pounds', 0.01, 0, datetime('now'));

-- Thrud inventory
INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped, created_at)
VALUES 
    ('inv_thr_greataxe', 'test_thrud', 'Greataxe', 'weapon', 1, 7.0, 'Heavy two-handed weapon', 30.0, 1, datetime('now')),
    ('inv_thr_rations', 'test_thrud', 'Rations', 'consumable', 5, 2.0, 'One day of food', 0.5, 0, datetime('now')),
    ('inv_thr_sack', 'test_thrud', 'Sack', 'gear', 1, 0.5, 'Holds 30 pounds', 0.01, 0, datetime('now'));

-- Gath inventory
INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped, created_at)
VALUES 
    ('inv_gat_battleaxe', 'test_gath', 'Battleaxe', 'weapon', 1, 4.0, 'Versatile martial weapon', 10.0, 1, datetime('now')),
    ('inv_gat_handaxe1', 'test_gath', 'Handaxe', 'weapon', 1, 2.0, 'Light thrown weapon', 5.0, 1, datetime('now')),
    ('inv_gat_handaxe2', 'test_gath', 'Handaxe', 'weapon', 1, 2.0, 'Light thrown weapon', 5.0, 0, datetime('now')),
    ('inv_gat_scale', 'test_gath', 'Scale Mail', 'armor', 1, 45.0, 'Medium armor, AC 14 + Dex (max 2)', 50.0, 1, datetime('now')),
    ('inv_gat_rations', 'test_gath', 'Rations', 'consumable', 5, 2.0, 'One day of food', 0.5, 0, datetime('now')),
    ('inv_gat_sack', 'test_gath', 'Sack', 'gear', 1, 0.5, 'Holds 30 pounds', 0.01, 0, datetime('now')),
    ('inv_gat_potion', 'test_gath', 'Potion of Healing', 'consumable', 1, 0.5, 'Heals 2d4+2 HP', 50.0, 0, datetime('now'));

-- Gurnison inventory
INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped, created_at)
VALUES 
    ('inv_gur_greataxe', 'test_gurnison', 'Greataxe', 'weapon', 1, 7.0, 'Heavy two-handed weapon', 30.0, 1, datetime('now')),
    ('inv_gur_handaxe1', 'test_gurnison', 'Handaxe', 'weapon', 1, 2.0, 'Light thrown weapon', 5.0, 0, datetime('now')),
    ('inv_gur_handaxe2', 'test_gurnison', 'Handaxe', 'weapon', 1, 2.0, 'Light thrown weapon', 5.0, 0, datetime('now')),
    ('inv_gur_rations', 'test_gurnison', 'Rations', 'consumable', 5, 2.0, 'One day of food', 0.5, 0, datetime('now')),
    ('inv_gur_sack', 'test_gurnison', 'Sack', 'gear', 1, 0.5, 'Holds 30 pounds', 0.01, 0, datetime('now')),
    ('inv_gur_potion', 'test_gurnison', 'Potion of Healing', 'consumable', 1, 0.5, 'Heals 2d4+2 HP', 50.0, 0, datetime('now'));

-- Add character features (feats and fighting styles)
-- Valerius features
INSERT INTO character_features (character_id, feature_name, feature_type, usage_type, level_gained, description)
VALUES 
    ('test_valerius', 'Alert', 'feat', 'permanent', 1, 'Add proficiency bonus to initiative, advantage on initiative rolls (solo play adaptation)'),
    ('test_valerius', 'Lucky', 'feat', 'permanent', 1, '3 luck points per long rest'),
    ('test_valerius', 'Fighting Style: Dueling', 'passive', 'permanent', 1, '+2 damage with one-handed weapon'),
    ('test_valerius', 'Second Wind', 'bonus_action', 'short_rest', 1, 'Regain 1d10+1 hit points');

-- Achelos features
INSERT INTO character_features (character_id, feature_name, feature_type, usage_type, level_gained, description)
VALUES
    ('test_achelos', 'Fighting Style: Defense', 'passive', 'permanent', 1, '+1 to AC while wearing armor'),
    ('test_achelos', 'Second Wind', 'bonus_action', 'short_rest', 1, 'Regain 1d10+1 hit points');

-- Roland features
INSERT INTO character_features (character_id, feature_name, feature_type, usage_type, level_gained, description)
VALUES 
    ('test_roland', 'Tough', 'feat', 'permanent', 1, '+2 HP per level'),
    ('test_roland', 'Fighting Style: Defense', 'passive', 'permanent', 1, '+1 to AC while wearing armor'),
    ('test_roland', 'Savage Attacker', 'feat', 'permanent', 1, 'Reroll damage dice once per turn'),
    ('test_roland', 'Second Wind', 'bonus_action', 'short_rest', 1, 'Regain 1d10+1 hit points');

-- Ragnar features
INSERT INTO character_features (character_id, feature_name, feature_type, usage_type, level_gained, description)
VALUES 
    ('test_ragnar', 'Tough', 'feat', 'permanent', 1, '+2 HP per level'),
    ('test_ragnar', 'Lucky', 'feat', 'permanent', 1, '3 luck points per long rest'),
    ('test_ragnar', 'Rage', 'bonus_action', 'long_rest', 1, 'Advantage on Strength checks, resistance to physical damage'),
    ('test_ragnar', 'Unarmored Defense', 'passive', 'permanent', 1, 'AC = 10 + Dex + Con when not wearing armor');

-- Thrud features
INSERT INTO character_features (character_id, feature_name, feature_type, usage_type, level_gained, description)
VALUES 
    ('test_thrud', 'Tough', 'feat', 'permanent', 1, '+2 HP per level'),
    ('test_thrud', 'Savage Attacker', 'feat', 'permanent', 1, 'Reroll damage dice once per turn'),
    ('test_thrud', 'Rage', 'bonus_action', 'long_rest', 1, 'Advantage on Strength checks, resistance to physical damage'),
    ('test_thrud', 'Unarmored Defense', 'passive', 'permanent', 1, 'AC = 10 + Dex + Con when not wearing armor');

-- Gath features
INSERT INTO character_features (character_id, feature_name, feature_type, usage_type, level_gained, description)
VALUES 
    ('test_gath', 'Tough', 'feat', 'permanent', 1, '+2 HP per level'),
    ('test_gath', 'Savage Attacker', 'feat', 'permanent', 1, 'Reroll damage dice once per turn'),
    ('test_gath', 'Rage', 'bonus_action', 'long_rest', 1, 'Advantage on Strength checks, resistance to physical damage');

-- Gurnison features
INSERT INTO character_features (character_id, feature_name, feature_type, usage_type, level_gained, description)
VALUES
    ('test_gurnison', 'Tough', 'feat', 'permanent', 1, '+2 HP per level'),
    ('test_gurnison', 'Rage', 'bonus_action', 'long_rest', 1, 'Advantage on Strength checks, resistance to physical damage'),
    ('test_gurnison', 'Unarmored Defense', 'passive', 'permanent', 1, 'AC = 10 + Dex + Con when not wearing armor');

-- Add proficiencies for all characters
-- Valerius proficiencies (Fighter + Soldier background)
INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
VALUES
    ('test_valerius', 'weapon', 'simple', 'class'),
    ('test_valerius', 'weapon', 'martial', 'class'),
    ('test_valerius', 'armor', 'light', 'class'),
    ('test_valerius', 'armor', 'medium', 'class'),
    ('test_valerius', 'armor', 'heavy', 'class'),
    ('test_valerius', 'armor', 'shields', 'class'),
    ('test_valerius', 'saving_throw', 'strength', 'class'),
    ('test_valerius', 'saving_throw', 'constitution', 'class'),
    ('test_valerius', 'skill', 'Acrobatics', 'class'),
    ('test_valerius', 'skill', 'Athletics', 'class'),
    ('test_valerius', 'skill', 'Intimidation', 'background'),
    ('test_valerius', 'skill', 'Perception', 'background'),
    ('test_valerius', 'tool', 'Gaming Set', 'background'),
    ('test_valerius', 'tool', 'Vehicles (Land)', 'background');

-- Achelos proficiencies (Fighter + Farmer background)
INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
VALUES
    ('test_achelos', 'weapon', 'simple', 'class'),
    ('test_achelos', 'weapon', 'martial', 'class'),
    ('test_achelos', 'armor', 'light', 'class'),
    ('test_achelos', 'armor', 'medium', 'class'),
    ('test_achelos', 'armor', 'heavy', 'class'),
    ('test_achelos', 'armor', 'shields', 'class'),
    ('test_achelos', 'saving_throw', 'strength', 'class'),
    ('test_achelos', 'saving_throw', 'constitution', 'class'),
    ('test_achelos', 'skill', 'Athletics', 'class'),
    ('test_achelos', 'skill', 'Perception', 'class'),
    ('test_achelos', 'skill', 'Animal Handling', 'background'),
    ('test_achelos', 'skill', 'Nature', 'background'),
    ('test_achelos', 'tool', 'Carpenter\'s Tools', 'background');

-- Roland proficiencies (Fighter + Noble background)
INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
VALUES
    ('test_roland', 'weapon', 'simple', 'class'),
    ('test_roland', 'weapon', 'martial', 'class'),
    ('test_roland', 'armor', 'light', 'class'),
    ('test_roland', 'armor', 'medium', 'class'),
    ('test_roland', 'armor', 'heavy', 'class'),
    ('test_roland', 'armor', 'shields', 'class'),
    ('test_roland', 'saving_throw', 'strength', 'class'),
    ('test_roland', 'saving_throw', 'constitution', 'class'),
    ('test_roland', 'skill', 'Athletics', 'class'),
    ('test_roland', 'skill', 'Intimidation', 'class'),
    ('test_roland', 'skill', 'History', 'background'),
    ('test_roland', 'skill', 'Persuasion', 'background'),
    ('test_roland', 'tool', 'Gaming Set', 'background');

-- Ragnar proficiencies (Barbarian + Outlander background)
INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
VALUES
    ('test_ragnar', 'weapon', 'simple', 'class'),
    ('test_ragnar', 'weapon', 'martial', 'class'),
    ('test_ragnar', 'armor', 'light', 'class'),
    ('test_ragnar', 'armor', 'medium', 'class'),
    ('test_ragnar', 'armor', 'shields', 'class'),
    ('test_ragnar', 'saving_throw', 'strength', 'class'),
    ('test_ragnar', 'saving_throw', 'constitution', 'class'),
    ('test_ragnar', 'skill', 'Athletics', 'class'),
    ('test_ragnar', 'skill', 'Intimidation', 'class'),
    ('test_ragnar', 'skill', 'Survival', 'background'),
    ('test_ragnar', 'skill', 'Nature', 'background'),
    ('test_ragnar', 'tool', 'Herbalism Kit', 'background');

-- Thrud proficiencies (Barbarian + Outlander background)
INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
VALUES
    ('test_thrud', 'weapon', 'simple', 'class'),
    ('test_thrud', 'weapon', 'martial', 'class'),
    ('test_thrud', 'armor', 'light', 'class'),
    ('test_thrud', 'armor', 'medium', 'class'),
    ('test_thrud', 'armor', 'shields', 'class'),
    ('test_thrud', 'saving_throw', 'strength', 'class'),
    ('test_thrud', 'saving_throw', 'constitution', 'class'),
    ('test_thrud', 'skill', 'Athletics', 'class'),
    ('test_thrud', 'skill', 'Perception', 'class'),
    ('test_thrud', 'skill', 'Survival', 'background'),
    ('test_thrud', 'skill', 'Nature', 'background'),
    ('test_thrud', 'tool', 'Herbalism Kit', 'background');

-- Gath proficiencies (Barbarian + Soldier background)
INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
VALUES
    ('test_gath', 'weapon', 'simple', 'class'),
    ('test_gath', 'weapon', 'martial', 'class'),
    ('test_gath', 'armor', 'light', 'class'),
    ('test_gath', 'armor', 'medium', 'class'),
    ('test_gath', 'armor', 'shields', 'class'),
    ('test_gath', 'saving_throw', 'strength', 'class'),
    ('test_gath', 'saving_throw', 'constitution', 'class'),
    ('test_gath', 'skill', 'Animal Handling', 'class'),
    ('test_gath', 'skill', 'Survival', 'class'),
    ('test_gath', 'skill', 'Intimidation', 'background'),
    ('test_gath', 'skill', 'Perception', 'background'),
    ('test_gath', 'tool', 'Gaming Set', 'background'),
    ('test_gath', 'tool', 'Vehicles (Land)', 'background');

-- Gurnison proficiencies (Barbarian + Folk Hero background)
INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
VALUES
    ('test_gurnison', 'weapon', 'simple', 'class'),
    ('test_gurnison', 'weapon', 'martial', 'class'),
    ('test_gurnison', 'armor', 'light', 'class'),
    ('test_gurnison', 'armor', 'medium', 'class'),
    ('test_gurnison', 'armor', 'shields', 'class'),
    ('test_gurnison', 'saving_throw', 'strength', 'class'),
    ('test_gurnison', 'saving_throw', 'constitution', 'class'),
    ('test_gurnison', 'skill', 'Athletics', 'class'),
    ('test_gurnison', 'skill', 'Intimidation', 'class'),
    ('test_gurnison', 'skill', 'Animal Handling', 'background'),
    ('test_gurnison', 'skill', 'Survival', 'background'),
    ('test_gurnison', 'tool', 'Smith\'s Tools', 'background'),
    ('test_gurnison', 'tool', 'Vehicles (Land)', 'background');