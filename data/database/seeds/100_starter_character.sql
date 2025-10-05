-- TaleKeeper Starter Character
-- Generated: 2025-09-13T13:48:22.578262
-- This provides a basic Level 1 Fighter for new users


-- Starter Character: Sir Galahad (Level 1 Fighter)
INSERT INTO characters (
    id, name, race_id, class_id, background_id, level, experience_points, 
    strength, dexterity, constitution, intelligence, wisdom, charisma, 
    armor_class, hit_points_max, hit_points_current, max_hit_points, current_hit_points,
    hit_dice_max, hit_dice_current, equipment_main_hand, equipment_armor, equipment_shield,
    created_at, notes
) 
VALUES (
    'starter_galahad',
    'Sir Galahad',
    'human',
    'fighter',
    'soldier',
    1,
    0,
    16, 14, 14, 10, 12, 13,  -- Ability scores
    16,  -- AC (Chain mail + shield)
    12, 12, 12, 12,  -- HP values
    1, 1,  -- Hit dice
    'Longsword', 'Chain Mail', 'Shield',  -- Equipped items
    datetime('now'),
    'Starter character for new players'
);

-- Add starting inventory
INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight, description, value, is_equipped, created_at)
VALUES 
    ('inv_starter_longsword', 'starter_galahad', 'Longsword', 'weapon', 1, 3.0, 'Versatile martial weapon', 15.0, 1, datetime('now')),
    ('inv_starter_chainmail', 'starter_galahad', 'Chain Mail', 'armor', 1, 55.0, 'Medium armor, AC 13 + Dex mod (max 2)', 75.0, 1, datetime('now')),
    ('inv_starter_shield', 'starter_galahad', 'Shield', 'shield', 1, 6.0, '+2 AC bonus', 10.0, 1, datetime('now')),
    ('inv_starter_javelin', 'starter_galahad', 'Javelin', 'weapon', 5, 2.0, 'Thrown weapon, range 30/120', 0.5, 0, datetime('now')),
    ('inv_starter_gold', 'starter_galahad', 'Gold Pieces', 'treasure', 150, 0.02, 'Starting money', 1.0, 0, datetime('now'));

-- Add Fighter features
INSERT INTO character_features (character_id, feature_name, feature_type, usage_type, level_gained, description)
VALUES 
    ('starter_galahad', 'Second Wind', 'bonus_action', 'short_rest', 1, 'Regain 1d10+1 hit points as a bonus action'),
    ('starter_galahad', 'Fighting Style: Defense', 'passive', 'permanent', 1, '+1 to AC while wearing armor');
