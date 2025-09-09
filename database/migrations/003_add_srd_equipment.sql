-- Migration: Add missing SRD equipment items
-- This adds weapons and armor from the D&D SRD that aren't already in the database

-- First, let's add any missing weapons from the SRD

-- Musket (Martial Ranged)
INSERT OR IGNORE INTO equipment (
    name, description, item_type, weapon_category, rarity, cost_gp, weight_lb,
    damage_dice, damage_type, weapon_properties, weapon_mastery, range_normal, range_long
) VALUES (
    'Musket', 'A firearm that uses gunpowder to propel a bullet.', 'weapon', 'martial_ranged', 
    'uncommon', 500, 10.0, '1d12', 'piercing', 
    '["ammunition", "loading", "two-handed"]', 'Slow', 40, 120
);

-- Pistol (Martial Ranged)
INSERT OR IGNORE INTO equipment (
    name, description, item_type, weapon_category, rarity, cost_gp, weight_lb,
    damage_dice, damage_type, weapon_properties, weapon_mastery, range_normal, range_long
) VALUES (
    'Pistol', 'A one-handed firearm.', 'weapon', 'martial_ranged', 
    'uncommon', 250, 3.0, '1d10', 'piercing', 
    '["ammunition", "loading"]', 'Vex', 30, 90
);

-- War Pick (Martial Melee)
INSERT OR IGNORE INTO equipment (
    name, description, item_type, weapon_category, rarity, cost_gp, weight_lb,
    damage_dice, damage_type, weapon_properties, weapon_mastery, versatile_damage
) VALUES (
    'War Pick', 'A military pick designed for piercing armor.', 'weapon', 'martial_melee', 
    'common', 5, 2.0, '1d8', 'piercing', 
    '["versatile"]', 'Sap', '1d10'
);

-- Now let's ensure all armor is in the database with correct stats from SRD

-- Light Armor
INSERT OR IGNORE INTO equipment (
    name, description, item_type, armor_type, rarity, cost_gp, weight_lb,
    armor_class, stealth_disadvantage
) VALUES 
    ('Padded Armor', 'Quilted layers of cloth and batting.', 'armor', 'light', 
     'common', 5, 8.0, 11, 1),
    ('Leather Armor', 'Made from stiffened leather.', 'armor', 'light', 
     'common', 10, 10.0, 11, 0),
    ('Studded Leather Armor', 'Leather reinforced with rivets or spikes.', 'armor', 'light', 
     'common', 45, 13.0, 12, 0);

-- Medium Armor
INSERT OR IGNORE INTO equipment (
    name, description, item_type, armor_type, rarity, cost_gp, weight_lb,
    armor_class, dex_bonus_max, stealth_disadvantage
) VALUES 
    ('Hide Armor', 'Crude armor of thick furs and pelts.', 'armor', 'medium', 
     'common', 10, 12.0, 12, 2, 0),
    ('Chain Shirt', 'Made of interlocking metal rings.', 'armor', 'medium', 
     'common', 50, 20.0, 13, 2, 0),
    ('Scale Mail', 'Leather with overlapping metal plates.', 'armor', 'medium', 
     'common', 50, 45.0, 14, 2, 1),
    ('Breastplate', 'A fitted metal chest piece with flexible leather.', 'armor', 'medium', 
     'common', 400, 20.0, 14, 2, 0),
    ('Half Plate Armor', 'Shaped metal plates covering vital areas.', 'armor', 'medium', 
     'common', 750, 40.0, 15, 2, 1);

-- Heavy Armor
INSERT OR IGNORE INTO equipment (
    name, description, item_type, armor_type, rarity, cost_gp, weight_lb,
    armor_class, strength_requirement, stealth_disadvantage
) VALUES 
    ('Ring Mail', 'Leather armor with heavy rings sewn into it.', 'armor', 'heavy', 
     'common', 30, 40.0, 14, NULL, 1),
    ('Chain Mail', 'Made of interlocking metal rings.', 'armor', 'heavy', 
     'common', 75, 55.0, 16, 13, 1),
    ('Splint Armor', 'Strips of metal riveted to leather backing.', 'armor', 'heavy', 
     'common', 200, 60.0, 17, 15, 1),
    ('Plate Armor', 'Shaped, interlocking metal plates.', 'armor', 'heavy', 
     'common', 1500, 65.0, 18, 15, 1);

-- Shield (already exists but let's ensure it has correct stats)
UPDATE equipment 
SET cost_gp = 10, weight_lb = 6.0, armor_class = 2
WHERE name = 'Shield' AND item_type = 'armor';

-- Add missing ammunition types
INSERT OR IGNORE INTO equipment (
    name, description, item_type, rarity, cost_gp, weight_lb
) VALUES 
    ('Arrow', 'Ammunition for bows.', 'ammunition', 'common', 0.05, 0.05),
    ('Bolt', 'Ammunition for crossbows.', 'ammunition', 'common', 0.05, 0.075),
    ('Bullet', 'Ammunition for slings and firearms.', 'ammunition', 'common', 0.02, 0.075),
    ('Needle', 'Ammunition for blowguns.', 'ammunition', 'common', 0.02, 0.02);

-- Add some basic adventuring gear from SRD
INSERT OR IGNORE INTO equipment (
    name, description, item_type, rarity, cost_gp, weight_lb
) VALUES 
    ('Backpack', 'Holds up to 30 pounds of gear.', 'gear', 'common', 2, 5.0),
    ('Bedroll', 'Sleeping bag for resting.', 'gear', 'common', 1, 7.0),
    ('Rope (50 feet)', 'Hemp rope, 50 feet long.', 'gear', 'common', 1, 10.0),
    ('Torch', 'Burns for 1 hour, provides bright light.', 'gear', 'common', 0.01, 1.0),
    ('Waterskin', 'Holds up to 4 pints of liquid.', 'gear', 'common', 0.2, 5.0),
    ('Rations (1 day)', 'Dried foods suitable for travel.', 'gear', 'common', 0.5, 2.0),
    ('Potion of Healing', 'Restores 2d4+2 hit points.', 'consumable', 'common', 50, 0.5),
    ('Crowbar', 'Grants advantage on Strength checks to pry.', 'gear', 'common', 2, 5.0),
    ('Grappling Hook', 'Used for climbing.', 'gear', 'common', 2, 4.0),
    ('Lantern', 'Provides bright light in 15-foot radius.', 'gear', 'common', 5, 2.0),
    ('Oil (flask)', 'Can be used as fuel or weapon.', 'gear', 'common', 0.1, 1.0),
    ('Tinderbox', 'Used to light fires.', 'gear', 'common', 0.5, 1.0);

-- Update weapon properties to ensure consistency with SRD
UPDATE equipment SET weapon_properties = '["finesse", "reach"]' WHERE name = 'Whip';
UPDATE equipment SET damage_dice = '1' WHERE name = 'Blowgun';  -- Blowgun does 1 damage, not 1d4