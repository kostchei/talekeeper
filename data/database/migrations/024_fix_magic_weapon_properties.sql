-- Fix magic weapons to have proper weapon properties
-- Migration 024: Copy weapon properties from base weapons to magic variants

-- Longsword variants
UPDATE equipment SET
    weapon_category = 'martial_melee',
    damage_dice = '1d8',
    damage_type = 'slashing',
    weapon_properties = '["versatile"]',
    weapon_mastery = 'Sap',
    versatile_damage = '1d10'
WHERE name LIKE 'Longsword +%';

-- Rapier variants
UPDATE equipment SET
    weapon_category = 'martial_melee',
    damage_dice = '1d8',
    damage_type = 'piercing',
    weapon_properties = '["finesse"]',
    weapon_mastery = 'Vex'
WHERE name LIKE 'Rapier +%';

-- Greatsword variants
UPDATE equipment SET
    weapon_category = 'martial_melee',
    damage_dice = '2d6',
    damage_type = 'slashing',
    weapon_properties = '["heavy", "two-handed", "graze"]',
    weapon_mastery = 'Graze'
WHERE name LIKE 'Greatsword +%';

-- Greataxe variants
UPDATE equipment SET
    weapon_category = 'martial_melee',
    damage_dice = '1d12',
    damage_type = 'slashing',
    weapon_properties = '["heavy", "two-handed"]',
    weapon_mastery = 'Cleave'
WHERE name LIKE 'Greataxe +%';

-- Scimitar variants
UPDATE equipment SET
    weapon_category = 'martial_melee',
    damage_dice = '1d6',
    damage_type = 'slashing',
    weapon_properties = '["finesse", "light"]',
    weapon_mastery = 'Nick'
WHERE name LIKE 'Scimitar +%';

-- Spear variants
UPDATE equipment SET
    weapon_category = 'simple_melee',
    damage_dice = '1d6',
    damage_type = 'piercing',
    weapon_properties = '["thrown", "versatile"]',
    weapon_mastery = 'Sap',
    range_normal = 20,
    range_long = 60,
    versatile_damage = '1d8'
WHERE name LIKE 'Spear +%';

-- Staff/Quarterstaff variants
UPDATE equipment SET
    weapon_category = 'simple_melee',
    damage_dice = '1d6',
    damage_type = 'bludgeoning',
    weapon_properties = '["versatile"]',
    weapon_mastery = 'Topple',
    versatile_damage = '1d8'
WHERE name LIKE 'Staff +%';
