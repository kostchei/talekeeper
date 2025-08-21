-- D&D 2024 Game Seed Data
-- Initial data for MVP: 2 races, 2 classes, 2 backgrounds, 8 monsters, basic equipment

-- =====================================================
-- RACES
-- =====================================================

INSERT INTO races (name, description, size, speed, ability_score_increase, traits, proficiencies, darkvision_range, languages, bonus_languages) VALUES
('Human', 
 'Humans are the most adaptable and ambitious people among the common races. They have widely varying tastes, morals, and customs in the many different lands where they have settled.',
 'Medium', 30, 
 '{}',
 '["Resourceful", "Skillful", "Versatile"]',
 '{"skills": {"choose": 1, "from": ["any"]}}',
 0,
 '["Common"]',
 1),

('Dwarf',
 'Bold and hardy, dwarves are known as skilled warriors, miners, and workers of stone and metal. They stand well under 5 feet tall but are so broad and compact that they can weigh as much as a human.',
 'Medium', 25,
 '{}',
 '["Darkvision", "Dwarven Resilience", "Dwarven Toughness", "Stonecunning"]',
 '{"tools": ["Smith''s Tools", "Brewer''s Supplies", "Mason''s Tools"], "weapons": ["Battleaxe", "Handaxe", "Light Hammer", "Warhammer"]}',
 60,
 '["Common", "Dwarvish"]',
 0);

-- =====================================================
-- CLASSES
-- =====================================================

INSERT INTO classes (name, description, hit_die, primary_ability, saving_throw_proficiencies, armor_proficiencies, weapon_proficiencies, tool_proficiencies, skill_proficiencies, starting_equipment, features_by_level) VALUES
('Fighter', 'Masters of martial combat, skilled with a variety of weapons and armor. Fighters excel at dealing damage and absorbing punishment.', 'd10', '["strength", "dexterity"]', -- D&D 2024: Choice between STR or DEX
 '{"strength", "constitution"}',
 '{"Light armor", "Medium armor", "Heavy armor", "Shields"}',
 '{"Simple weapons", "Martial weapons"}',
 '{}',
 '{"choose": 2, "from": ["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Persuasion", "Perception", "Survival"]}',
 '{
   "armor": ["Chain Mail OR Leather Armor", "Shield OR no shield"],
   "weapons": ["Simple and Martial weapons"],
   "tools": [],
   "other": ["Explorers Pack", "20 arrows if using ranged weapon"]
 }',
 '{
   "1": [
     {
       "name": "Fighting Style",
       "description": "You gain a Fighting Style feat of your choice. Whenever you gain a Fighter level, you can replace this feat with a different Fighting Style feat.",
       "type": "feat_choice",
       "options": ["Archery", "Defense", "Dueling", "Great Weapon Fighting", "Protection", "Two-Weapon Fighting"]
     },
     {
       "name": "Second Wind", 
       "description": "As a Bonus Action, regain Hit Points equal to 1d10 + Fighter level. You can use this feature twice, regaining one use on Short Rest and all uses on Long Rest.",
       "type": "resource",
       "uses": 2,
       "recharge": "short_rest_partial"
     },
     {
       "name": "Weapon Mastery",
       "description": "You can use the mastery properties of 3 kinds of Simple or Martial weapons. You can change one choice when you finish a Long Rest.",
       "type": "weapon_mastery",
       "count": 3
     }
   ],
   "2": [
     {
       "name": "Action Surge",
       "description": "On your turn, you can take one additional action (except Magic action). Once per Short or Long Rest. At level 17, usable twice per rest but only once per turn.",
       "type": "resource", 
       "uses": 1,
       "recharge": "short_rest"
     },
     {
       "name": "Tactical Mind",
       "description": "When you fail an ability check, you can expend a use of Second Wind to roll 1d10 and add it to the check instead of regaining HP.",
       "type": "ability"
     }
   ],
   "3": [
     {
       "name": "Fighter Subclass",
       "description": "Choose a Fighter subclass: Champion, Battle Master, Eldritch Knight, or others.",
       "type": "subclass_choice"
     }
   ]
 }'),

('Rogue', 'Skilled in stealth and precision, rogues excel at striking from the shadows and solving problems with finesse rather than force.', 'd8', '["dexterity"]', -- D&D 2024: DEX is primary
 '{"dexterity", "intelligence"}',
 '{"Light armor"}',
 '{"Simple weapons", "Martial weapons with Finesse or Light property"}',
 '{"Thieves Tools"}',
 '{"choose": 4, "from": ["Acrobatics", "Athletics", "Deception", "Insight", "Intimidation", "Investigation", "Perception", "Persuasion", "Sleight of Hand", "Stealth"]}',
 '{
   "armor": ["Leather Armor"],
   "weapons": ["Simple weapons", "Martial weapons with Finesse or Light property"],
   "tools": ["Thieves Tools"],
   "other": ["Burglars Pack", "Two Daggers"]
 }',
 '{
   "1": [
     {
       "name": "Expertise", 
       "description": "Choose 2 skill proficiencies. Your Proficiency Bonus is doubled for any ability check using those skills.",
       "type": "expertise",
       "count": 2
     },
     {
       "name": "Sneak Attack",
       "description": "Once per turn, deal extra 1d6 damage to a creature you hit with a Finesse or Ranged weapon if you have Advantage or an ally is within 5 feet of the target.",
       "type": "sneak_attack",
       "damage": "1d6"
     },
     {
       "name": "Thieves Cant",
       "description": "You know Thieves Cant, a secret mix of dialect, jargon, and code that allows you to hide messages in seemingly normal conversation.",
       "type": "language"
     },
     {
       "name": "Weapon Mastery",
       "description": "You can use the mastery properties of 2 kinds of Simple or Martial weapons with the Finesse or Light property.",
       "type": "weapon_mastery", 
       "count": 2,
       "restriction": "finesse_or_light"
     }
   ],
   "2": [
     {
       "name": "Cunning Action",
       "description": "You can take a Bonus Action to take the Dash, Disengage, or Hide action.",
       "type": "bonus_action_options",
       "options": ["Dash", "Disengage", "Hide"]
     }
   ],
   "3": [
     {
       "name": "Rogue Subclass", 
       "description": "Choose a Rogue subclass: Thief, Assassin, Arcane Trickster, or others.",
       "type": "subclass_choice"
     }
   ]
 }');

-- =====================================================
-- SUBCLASSES
-- =====================================================

INSERT INTO subclasses (class_id, name, choice_level, features, description) VALUES
-- Fighter subclasses
((SELECT id FROM classes WHERE name = 'Fighter'), 'Champion', 3,
 '{
   "3": ["Improved Critical"],
   "7": ["Remarkable Athlete"],
   "10": ["Additional Fighting Style"],
   "15": ["Superior Critical"],
   "18": ["Survivor"]
 }',
 'The archetypal Champion focuses on the development of raw physical power honed to deadly perfection.'),

((SELECT id FROM classes WHERE name = 'Fighter'), 'Battle Master', 3,
 '{
   "3": ["Combat Superiority", "Student of War"],
   "7": ["Know Your Enemy"],
   "10": ["Improved Combat Superiority"],
   "15": ["Relentless"],
   "18": ["Improved Combat Superiority"]
 }',
 'Those who emulate the archetypal Battle Master employ martial techniques passed down through generations.'),

-- Rogue subclasses
((SELECT id FROM classes WHERE name = 'Rogue'), 'Thief', 3,
 '{
   "3": ["Fast Hands", "Second-Story Work"],
   "9": ["Supreme Sneak"],
   "13": ["Use Magic Device"],
   "17": ["Thiefs Reflexes"]
 }',
 'You hone your skills in the larcenous arts. Burglars, bandits, cutpurses, and other criminals typically follow this archetype.'),

((SELECT id FROM classes WHERE name = 'Rogue'), 'Assassin', 3,
 '{
   "3": ["Assassinate", "Bonus Proficiencies"],
   "9": ["Infiltration Expertise"],
   "13": ["Impostor"],
   "17": ["Death Strike"]
 }',
 'You focus your training on the grim art of death. Those who adhere to this archetype are diverse hired killers, spies, and bounty hunters.');

-- =====================================================
-- BACKGROUNDS
-- =====================================================

INSERT INTO backgrounds (name, description, ability_score_increases, skill_proficiencies, tool_proficiencies, languages, starting_equipment, starting_gold, feature_name, feature_description) VALUES
('Farmer', 
 'You worked the land, understanding the cycles of nature and the value of hard work.',
 '{"choice": 2, "any": 1}',
 '{"Animal Handling", "Nature"}',
 '{"Herbalism Kit"}',
 0,
 '["Herbalism Kit", "Shovel", "Iron Pot", "Set of Common Clothes", "Belt Pouch"]',
 '2d4 * 10',
 'Rustic Hospitality',
 'Since you come from the ranks of the common folk, you fit in among them with ease. You can find a place to hide, rest, or recuperate among other commoners, unless you have shown yourself to be a danger to them.'),

('Soldier',
 'You served in a military organization, trained in tactics and discipline.',
 '{"strength": 2, "constitution": 1}',
 '{"Athletics", "Intimidation"}',
 '{"Gaming Set", "Land Vehicles"}',
 0,
 '["Insignia of Rank", "Trophy from Fallen Enemy", "Deck of Cards", "Set of Common Clothes", "Belt Pouch"]',
 '2d4 * 10',
 'Military Rank',
 'You have a military rank from your career as a soldier. Soldiers loyal to your former military organization still recognize your authority and influence, and they defer to you if they are of a lower rank.');

-- =====================================================
-- MONSTERS (Level 1-3 appropriate)
-- =====================================================

INSERT INTO monsters (name, challenge_rating, size, type, alignment, armor_class, hit_points, hit_dice, speed, 
                     strength, dexterity, constitution, intelligence, wisdom, charisma,
                     saving_throws, skills, senses, languages, actions, ai_script, loot_table, xp_value) VALUES

-- Cultist (CR 1/8)
('Cultist', 0.125, 'Medium', 'humanoid', 'any evil', 12, 9, '2d8',
 '{"walk": 30}',
 11, 12, 10, 10, 11, 10,
 '{}', '{"deception": 2, "religion": 2}',
 '{"passive_perception": 10}', ARRAY['Common'],
 '[{
   "name": "Scimitar",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "1d6+1",
   "damage_type": "slashing"
 }]',
 'basic_melee',
 '{"gold": "2d6", "items": ["cultist_robes"], "chance": 0.3}',
 25),

-- Manes (CR 1/8)
('Manes', 0.125, 'Small', 'fiend', 'chaotic evil', 9, 9, '2d6+2',
 '{"walk": 20}',
 10, 9, 13, 3, 8, 4,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 9}', ARRAY['Abyssal'],
 '[{
   "name": "Claws",
   "type": "melee",
   "bonus": 2,
   "reach": 5,
   "damage": "2d4",
   "damage_type": "slashing"
 }]',
 'basic_melee',
 '{"gold": "1d6", "items": [], "chance": 0.1}',
 25),

-- Slaad Tadpole (CR 1/8)
('Slaad Tadpole', 0.125, 'Tiny', 'aberration', 'chaotic neutral', 12, 10, '4d4',
 '{"walk": 30}',
 7, 15, 10, 3, 5, 3,
 '{}', '{"stealth": 4}',
 '{"darkvision": 60, "passive_perception": 7}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "1d4+2",
   "damage_type": "piercing"
 }]',
 'basic_melee',
 '{"gold": "1d4", "items": [], "chance": 0.05}',
 25),

-- Twig Blight (CR 1/8)
('Twig Blight', 0.125, 'Small', 'plant', 'neutral evil', 13, 4, '1d6+1',
 '{"walk": 20}',
 6, 13, 12, 4, 8, 3,
 '{}', '{"stealth": 3}',
 '{"blindsight": 60, "passive_perception": 9}', ARRAY['Common'],
 '[{
   "name": "Claws",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "1d4+1",
   "damage_type": "slashing"
 }]',
 'basic_melee',
 '{"gold": "1d6", "items": [], "chance": 0.1}',
 25),

-- Troglodyte (CR 1/4)
('Troglodyte', 0.25, 'Medium', 'humanoid', 'chaotic evil', 11, 13, '2d8+4',
 '{"walk": 30}',
 14, 10, 14, 6, 10, 6,
 '{}', '{"stealth": 2}',
 '{"darkvision": 60, "passive_perception": 10}', ARRAY['Troglodyte'],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "1d4+2",
   "damage_type": "piercing"
 },
 {
   "name": "Claw",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "1d4+2",
   "damage_type": "slashing"
 },
 {
   "name": "Stench",
   "type": "special",
   "description": "Any creature within 5 feet must succeed on a DC 12 Constitution saving throw or be poisoned until the start of its next turn.",
   "save_dc": 12,
   "save_type": "constitution",
   "recharge": "passive"
 }]',
 'control_then_damage',
 '{"gold": "2d6", "items": ["crude_spear"], "chance": 0.2}',
 50),

-- Dretch (CR 1/4)
('Dretch', 0.25, 'Small', 'fiend', 'chaotic evil', 11, 18, '4d6+4',
 '{"walk": 20}',
 11, 11, 12, 5, 8, 3,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 9}', ARRAY['Abyssal'],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 2,
   "reach": 5,
   "damage": "1d6",
   "damage_type": "piercing"
 },
 {
   "name": "Claws",
   "type": "melee",
   "bonus": 2,
   "reach": 5,
   "damage": "2d4",
   "damage_type": "slashing"
 },
 {
   "name": "Fetid Cloud",
   "type": "special",
   "description": "10-foot radius cloud. Creatures must succeed on DC 11 Constitution save or be poisoned until the start of the dretches next turn.",
   "save_dc": 11,
   "save_type": "constitution",
   "recharge": "1/day"
 }]',
 'control_first',
 '{"gold": "2d6", "items": [], "chance": 0.15}',
 50),

-- Grimlock (CR 1/4)
('Grimlock', 0.25, 'Medium', 'humanoid', 'neutral evil', 11, 11, '2d8+2',
 '{"walk": 30}',
 16, 12, 12, 9, 8, 6,
 '{}', '{"athletics": 5, "perception": 3, "stealth": 3}',
 '{"blindsight": 30, "passive_perception": 13}', ARRAY['Undercommon'],
 '[{
   "name": "Spiked Club",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d4+3",
   "damage_type": "bludgeoning",
   "extra_damage": "2 piercing"
 }]',
 'basic_melee',
 '{"gold": "2d8", "items": ["spiked_club"], "chance": 0.25}',
 50),

-- Zombie (CR 1/4)
('Zombie', 0.25, 'Medium', 'undead', 'neutral evil', 8, 22, '3d8+9',
 '{"walk": 20}',
 13, 6, 16, 3, 6, 5,
 '{"wisdom": 0}', '{}',
 '{"darkvision": 60, "passive_perception": 8}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Slam",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "1d6+1",
   "damage_type": "bludgeoning"
 },
 {
   "name": "Undead Fortitude",
   "type": "special",
   "description": "If reduced to 0 hit points, make a Constitution save (DC = 5 + damage taken). On success, drop to 1 hit point instead.",
   "recharge": "passive"
 }]',
 'basic_melee',
 '{"gold": "1d8", "items": [], "chance": 0.1}',
 50);

-- =====================================================
-- ITEMS AND EQUIPMENT
-- =====================================================

-- Weapons
INSERT INTO items (name, type, subtype, rarity, weight, cost_gp, damage_dice, damage_type, properties) VALUES
-- Simple Melee
('Club', 'weapon', 'simple_melee', 'common', 2, 0.1, '1d4', 'bludgeoning', '["light"]'),
('Dagger', 'weapon', 'simple_melee', 'common', 1, 2, '1d4', 'piercing', '["finesse", "light", "thrown"]'),
('Handaxe', 'weapon', 'simple_melee', 'common', 2, 5, '1d6', 'slashing', '["light", "thrown"]'),
('Mace', 'weapon', 'simple_melee', 'common', 4, 5, '1d6', 'bludgeoning', '{}'),
('Quarterstaff', 'weapon', 'simple_melee', 'common', 4, 0.2, '1d6', 'bludgeoning', '["versatile"]'),
('Spear', 'weapon', 'simple_melee', 'common', 3, 1, '1d6', 'piercing', '["thrown", "versatile"]'),

-- Simple Ranged
('Shortbow', 'weapon', 'simple_ranged', 'common', 2, 25, '1d6', 'piercing', '["ammunition", "two-handed"]'),

-- Martial Melee
('Battleaxe', 'weapon', 'martial_melee', 'common', 4, 10, '1d8', 'slashing', '["versatile"]'),
('Greatsword', 'weapon', 'martial_melee', 'common', 6, 50, '2d6', 'slashing', '["heavy", "two-handed"]'),
('Longsword', 'weapon', 'martial_melee', 'common', 3, 15, '1d8', 'slashing', '["versatile"]'),
('Rapier', 'weapon', 'martial_melee', 'common', 2, 25, '1d8', 'piercing', '["finesse"]'),
('Scimitar', 'weapon', 'martial_melee', 'common', 3, 25, '1d6', 'slashing', '["finesse", "light"]'),
('Shortsword', 'weapon', 'martial_melee', 'common', 2, 10, '1d6', 'piercing', '["finesse", "light"]'),
('Warhammer', 'weapon', 'martial_melee', 'common', 2, 15, '1d8', 'bludgeoning', '["versatile"]'),

-- Martial Ranged
('Longbow', 'weapon', 'martial_ranged', 'common', 2, 50, '1d8', 'piercing', '["ammunition", "heavy", "two-handed"]'),

-- Armor
('Leather Armor', 'armor', 'light_armor', 'common', 10, 10, NULL, NULL, '{}'),
('Studded Leather', 'armor', 'light_armor', 'common', 13, 45, NULL, NULL, '{}'),
('Hide Armor', 'armor', 'medium_armor', 'common', 12, 10, NULL, NULL, '{}'),
('Chain Shirt', 'armor', 'medium_armor', 'common', 20, 50, NULL, NULL, '{}'),
('Scale Mail', 'armor', 'medium_armor', 'common', 45, 50, NULL, NULL, '["disadvantage_stealth"]'),
('Chain Mail', 'armor', 'heavy_armor', 'common', 55, 75, NULL, NULL, '["disadvantage_stealth"]'),
('Splint Armor', 'armor', 'heavy_armor', 'common', 60, 200, NULL, NULL, '["disadvantage_stealth"]'),
('Plate Armor', 'armor', 'heavy_armor', 'common', 65, 1500, NULL, NULL, '["disadvantage_stealth"]'),
('Shield', 'armor', 'shield', 'common', 6, 10, NULL, NULL, '{}');

-- Set armor class values
UPDATE items SET armor_class = 11 WHERE name = 'Leather Armor';
UPDATE items SET armor_class = 12 WHERE name = 'Studded Leather';
UPDATE items SET armor_class = 12 WHERE name = 'Hide Armor';
UPDATE items SET armor_class = 13 WHERE name = 'Chain Shirt';
UPDATE items SET armor_class = 14 WHERE name = 'Scale Mail';
UPDATE items SET armor_class = 16 WHERE name = 'Chain Mail';
UPDATE items SET armor_class = 17 WHERE name = 'Splint Armor';
UPDATE items SET armor_class = 18 WHERE name = 'Plate Armor';
UPDATE items SET armor_class = 2 WHERE name = 'Shield'; -- Shield adds +2 AC

-- Set strength requirements for heavy armor
UPDATE items SET strength_requirement = 13 WHERE name = 'Chain Mail';
UPDATE items SET strength_requirement = 15 WHERE name IN ('Splint Armor', 'Plate Armor');

-- Set equipment slots for items
UPDATE items SET equipment_slot = 'main_hand' WHERE type = 'weapon' AND subtype LIKE '%melee%';
UPDATE items SET equipment_slot = 'main_hand' WHERE type = 'weapon' AND subtype LIKE '%ranged%';
UPDATE items SET equipment_slot = 'armor' WHERE type = 'armor' AND subtype IN ('light_armor', 'medium_armor', 'heavy_armor');
UPDATE items SET equipment_slot = 'off_hand' WHERE name = 'Shield';

-- Set armor properties
UPDATE items SET max_dex_bonus = NULL WHERE subtype = 'light_armor'; -- No limit for light armor
UPDATE items SET max_dex_bonus = 2 WHERE subtype = 'medium_armor'; -- Max +2 for medium armor  
UPDATE items SET max_dex_bonus = 0 WHERE subtype = 'heavy_armor'; -- No DEX bonus for heavy armor
UPDATE items SET stealth_disadvantage = TRUE WHERE name IN ('Chain Mail', 'Splint Armor', 'Plate Armor', 'Scale Mail');

-- Set weapon range properties
UPDATE items SET range_normal = 150, range_long = 600 WHERE name = 'Longbow';
UPDATE items SET range_normal = 80, range_long = 320 WHERE name = 'Light Crossbow';
UPDATE items SET range_normal = 100, range_long = 400 WHERE name = 'Heavy Crossbow';

-- Set magic item properties
UPDATE items SET is_magical = TRUE, attunement_required = FALSE WHERE name LIKE '%+1%';
UPDATE items SET is_magical = FALSE, attunement_required = FALSE WHERE is_magical IS NULL;

-- Consumables
INSERT INTO items (name, type, subtype, rarity, weight, cost_gp, description, consumable, stackable, max_stack) VALUES
('Potion of Healing', 'potion', 'healing', 'common', 0.5, 50, 'Regain 2d4+2 hit points when consumed.', TRUE, TRUE, 10),
('Potion of Greater Healing', 'potion', 'healing', 'uncommon', 0.5, 150, 'Regain 4d4+4 hit points when consumed.', TRUE, TRUE, 10),
('Antitoxin', 'potion', 'utility', 'common', 0, 50, 'Advantage on Constitution saves against poison for 1 hour.', TRUE, TRUE, 5),
('Alchemists Fire', 'item', 'thrown', 'common', 1, 50, 'Thrown weapon. On hit, target takes 1d4 fire damage at start of each turn. DC 10 Dexterity check to extinguish.', TRUE, TRUE, 5);

-- Magic Items (for level 3 rewards)
INSERT INTO items (name, type, subtype, rarity, weight, cost_gp, damage_dice, damage_type, magic_bonus, description, attunement) VALUES
('Longsword +1', 'weapon', 'martial_melee', 'uncommon', 3, 500, '1d8', 'slashing', 1, 'You have a +1 bonus to attack and damage rolls made with this magic weapon.', FALSE),
('Shortsword +1', 'weapon', 'martial_melee', 'uncommon', 2, 400, '1d6', 'piercing', 1, 'You have a +1 bonus to attack and damage rolls made with this magic weapon.', FALSE),
('Leather Armor +1', 'armor', 'light_armor', 'uncommon', 10, 500, NULL, NULL, 1, 'You have a +1 bonus to AC while wearing this armor.', FALSE);

UPDATE items SET armor_class = 12 WHERE name = 'Leather Armor +1'; -- 11 base + 1 magic

-- Adventuring Gear
INSERT INTO items (name, type, subtype, rarity, weight, cost_gp, description) VALUES
('Rope, Hempen (50 feet)', 'gear', 'utility', 'common', 10, 1, '50 feet of rope. 2 hit points and can be burst with a DC 17 Strength check.'),
('Torch', 'gear', 'light', 'common', 1, 0.01, 'Provides bright light in a 20-foot radius and dim light for an additional 20 feet for 1 hour.'),
('Rations (1 day)', 'gear', 'food', 'common', 2, 0.5, 'Dry foods suitable for extended travel.'),
('Waterskin', 'gear', 'container', 'common', 5, 0.2, 'Holds up to 4 pints of liquid.'),
('Thieves Tools', 'gear', 'tools', 'common', 1, 25, 'Required for picking locks and disarming traps.'),
('Healers Kit', 'gear', 'medical', 'common', 3, 5, 'Ten uses. Stabilize a dying creature without a Medicine check.'),
('Crowbar', 'gear', 'tools', 'common', 5, 2, 'Grants advantage on Strength checks where leverage can be applied.'),
('Grappling Hook', 'gear', 'climbing', 'common', 4, 2, 'Can be attached to rope for climbing.');

-- =====================================================
-- SAMPLE CHARACTER (for testing)
-- =====================================================

-- Create a test save slot
INSERT INTO save_slots (slot_number, character_name) VALUES
(1, 'Test Fighter');

-- Create a test character
INSERT INTO characters (
    save_slot_id,
    name,
    race_id,
    class_id,
    subclass_id,
    background_id,
    level,
    experience_points,
    strength, dexterity, constitution, intelligence, wisdom, charisma,
    hit_points_max, hit_points_current,
    armor_class,
    proficiency_bonus,
    skill_proficiencies,
    weapon_proficiencies,
    armor_proficiencies,
    saving_throw_proficiencies,
    gold
) VALUES (
    (SELECT id FROM save_slots WHERE slot_number = 1),
    'Test Fighter',
    (SELECT id FROM races WHERE name = 'Human'),
    (SELECT id FROM classes WHERE name = 'Fighter'),
    (SELECT id FROM subclasses WHERE name = 'Champion'),
    (SELECT id FROM backgrounds WHERE name = 'Soldier'),
    1,
    0,
    16, 14, 14, 10, 12, 8,
    12, 12, -- HP (10 + CON mod)
    16, -- AC (chain mail)
    2,
    ARRAY['Athletics', 'Intimidation'],
    ARRAY['simple', 'martial'],
    ARRAY['light', 'medium', 'heavy', 'shields'],
    ARRAY['strength', 'constitution'],
    50
);

-- Give the test character some starting equipment
INSERT INTO character_inventory (character_id, item_id, equipped, equipped_slot) VALUES
((SELECT id FROM characters WHERE name = 'Test Fighter'), 
 (SELECT id FROM items WHERE name = 'Longsword'), TRUE, 'main_hand'),
((SELECT id FROM characters WHERE name = 'Test Fighter'), 
 (SELECT id FROM items WHERE name = 'Shield'), TRUE, 'off_hand'),
((SELECT id FROM characters WHERE name = 'Test Fighter'), 
 (SELECT id FROM items WHERE name = 'Chain Mail'), TRUE, 'armor'),
((SELECT id FROM characters WHERE name = 'Test Fighter'), 
 (SELECT id FROM items WHERE name = 'Potion of Healing'), FALSE, NULL);

-- Create a game state for the test character
INSERT INTO game_states (character_id, current_location, inventory_gold) VALUES
((SELECT id FROM characters WHERE name = 'Test Fighter'), 'Starting Town', 50);

-- =====================================================
-- D&D 2024 WEAPON MASTERY PROPERTIES
-- =====================================================

-- Add weapon mastery properties to existing weapons (new D&D 2024 feature)
UPDATE items SET properties = properties || '["mastery_nick"]' WHERE name = 'Scimitar';
UPDATE items SET properties = properties || '["mastery_vex"]' WHERE name = 'Longsword';
UPDATE items SET properties = properties || '["mastery_nick"]' WHERE name = 'Shortsword';
UPDATE items SET properties = properties || '["mastery_vex"]' WHERE name = 'Rapier';
UPDATE items SET properties = properties || '["mastery_cleave"]' WHERE name = 'Greatsword';
UPDATE items SET properties = properties || '["mastery_topple"]' WHERE name = 'Battleaxe';
UPDATE items SET properties = properties || '["mastery_push"]' WHERE name = 'Warhammer';
UPDATE items SET properties = properties || '["mastery_slow"]' WHERE name = 'Club';
UPDATE items SET properties = properties || '["mastery_nick"]' WHERE name = 'Dagger';
UPDATE items SET properties = properties || '["mastery_slow"]' WHERE name = 'Mace';
UPDATE items SET properties = properties || '["mastery_topple"]' WHERE name = 'Quarterstaff';
UPDATE items SET properties = properties || '["mastery_sap"]' WHERE name = 'Spear';

-- Mastery property descriptions for reference:
-- mastery_cleave: Hit another creature within reach if original attack hits
-- mastery_graze: Deal damage equal to ability modifier on missed attack
-- mastery_nick: Make extra light weapon attack as bonus action when dual wielding
-- mastery_push: Push target 10 feet away on hit
-- mastery_sap: Give target disadvantage on next attack if you hit
-- mastery_slow: Reduce target's speed by 10 feet until start of your next turn
-- mastery_topple: Knock target prone if you hit with advantage  
-- mastery_vex: Give yourself advantage on next attack against same target

-- =====================================================
-- NEW MONSTERS - CR 1/2 (XP 100)
-- =====================================================

-- Cockatrice (CR 1/2)
INSERT INTO monsters (name, challenge_rating, size, type, alignment, armor_class, hit_points, hit_dice, speed,
                     strength, dexterity, constitution, intelligence, wisdom, charisma,
                     saving_throws, skills, senses, languages, actions, ai_script, loot_table, xp_value) VALUES
('Cockatrice', 0.5, 'Small', 'monstrosity', 'unaligned', 11, 27, '6d6+6',
 '{"walk": 20, "fly": 40}',
 6, 12, 12, 2, 13, 5,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 11}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "1d4+1",
   "damage_type": "piercing",
   "special": "Target must succeed on DC 11 Constitution save or be restrained for 24 hours unless petrification is ended"
 }]',
 'basic_melee',
 '{"gold": "1d4", "items": [], "chance": 0.1}',
 100),

-- Darkmantle (CR 1/2)
('Darkmantle', 0.5, 'Small', 'monstrosity', 'unaligned', 11, 22, '5d6+5',
 '{"walk": 10, "fly": 30}',
 16, 12, 13, 2, 10, 5,
 '{}', '{"stealth": 3}',
 '{"blindsight": 60, "passive_perception": 10}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Crush",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d6+3",
   "damage_type": "bludgeoning",
   "special": "Target is grappled (escape DC 13) and blinded while grappled"
 }]',
 'ambush_predator',
 '{"gold": "0", "items": [], "chance": 0.05}',
 100),

-- Giant Wasp (CR 1/2)
('Giant Wasp', 0.5, 'Medium', 'beast', 'unaligned', 12, 13, '3d8+3',
 '{"walk": 10, "fly": 50}',
 10, 14, 13, 1, 10, 3,
 '{}', '{}',
 '{"passive_perception": 10}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Sting",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "1d6+2",
   "damage_type": "piercing",
   "special": "Target must make DC 11 Constitution save or take 3d6 poison damage and be poisoned for 1 hour"
 }]',
 'flying_aggressor',
 '{"gold": "0", "items": [], "chance": 0.1}',
 100),

-- Rust Monster (CR 1/2)
('Rust Monster', 0.5, 'Medium', 'monstrosity', 'unaligned', 14, 27, '5d8+5',
 '{"walk": 40}',
 13, 12, 13, 2, 13, 6,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 11}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "1d8+1",
   "damage_type": "piercing"
 }, {
   "name": "Antennae",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "0",
   "damage_type": "special",
   "special": "Corrodes nonmagical metal objects, armor AC reduced by 1"
 }]',
 'equipment_destroyer',
 '{"gold": "0", "items": [], "chance": 0.0}',
 100),

-- Satyr (CR 1/2)
('Satyr', 0.5, 'Medium', 'fey', 'chaotic neutral', 14, 31, '7d8+7',
 '{"walk": 40}',
 12, 16, 13, 12, 10, 14,
 '{}', '{"perception": 2, "performance": 6, "stealth": 5}',
 '{"passive_perception": 12}', ARRAY['Common', 'Elvish', 'Sylvan'],
 '[{
   "name": "Ram",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "2d4+1",
   "damage_type": "bludgeoning"
 }, {
   "name": "Shortsword",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d6+3",
   "damage_type": "piercing"
 }]',
 'forest_trickster',
 '{"gold": "2d6", "items": ["shortsword"], "chance": 0.3}',
 100),

-- Shadow (CR 1/2)
('Shadow', 0.5, 'Medium', 'undead', 'chaotic evil', 12, 16, '3d8+3',
 '{"walk": 40}',
 6, 14, 13, 6, 10, 8,
 '{}', '{"stealth": 4}',
 '{"darkvision": 60, "passive_perception": 10}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Strength Drain",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "2d6+2",
   "damage_type": "necrotic",
   "special": "Target Strength reduced by 1d4, dies if reduced to 0"
 }]',
 'strength_drainer',
 '{"gold": "0", "items": [], "chance": 0.0}',
 100),

-- Skulk (CR 1/2)
('Skulk', 0.5, 'Medium', 'humanoid', 'chaotic evil', 14, 18, '4d8+4',
 '{"walk": 30}',
 6, 16, 12, 10, 7, 1,
 '{}', '{"stealth": 7}',
 '{"darkvision": 120, "passive_perception": 8}', ARRAY['Common'],
 '[{
   "name": "Claws",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d6+3",
   "damage_type": "slashing"
 }]',
 'stealth_ambusher',
 '{"gold": "1d4", "items": [], "chance": 0.2}',
 100),

-- Vine Blight (CR 1/2)
('Vine Blight', 0.5, 'Medium', 'plant', 'neutral evil', 12, 26, '4d8+8',
 '{"walk": 10}',
 15, 8, 14, 5, 10, 3,
 '{}', '{"stealth": 1}',
 '{"blindsight": 60, "passive_perception": 10}', ARRAY['Common'],
 '[{
   "name": "Constrict",
   "type": "melee",
   "bonus": 4,
   "reach": 10,
   "damage": "2d6+2",
   "damage_type": "bludgeoning",
   "special": "Target is grappled (escape DC 12) and restrained while grappled"
 }]',
 'grappling_plant',
 '{"gold": "0", "items": [], "chance": 0.1}',
 100),

-- Warg (CR 1/2)
('Warg', 0.5, 'Large', 'monstrosity', 'neutral evil', 13, 26, '4d10+4',
 '{"walk": 50}',
 16, 13, 13, 7, 11, 8,
 '{}', '{"perception": 4}',
 '{"darkvision": 60, "passive_perception": 14}', ARRAY['Goblin', 'Orcish'],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "2d6+3",
   "damage_type": "piercing",
   "special": "Target must succeed on DC 13 Strength save or be knocked prone"
 }]',
 'pack_hunter',
 '{"gold": "1d6", "items": [], "chance": 0.15}',
 100),

-- =====================================================
-- NEW MONSTERS - CR 1 (XP 200)
-- =====================================================

-- Animated Armor (CR 1)
('Animated Armor', 1, 'Medium', 'construct', 'unaligned', 18, 33, '6d8+6',
 '{"walk": 25}',
 14, 11, 13, 1, 3, 1,
 '{}', '{}',
 '{"blindsight": 60, "passive_perception": 6}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Multiattack",
   "type": "special",
   "description": "Makes two slam attacks"
 }, {
   "name": "Slam",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "1d6+2",
   "damage_type": "bludgeoning"
 }]',
 'construct_guardian',
 '{"gold": "0", "items": [], "chance": 0.0}',
 200),

-- Choker (CR 1)
('Choker', 1, 'Small', 'aberration', 'chaotic evil', 16, 13, '3d6+3',
 '{"walk": 30}',
 16, 14, 13, 4, 12, 7,
 '{}', '{"stealth": 6}',
 '{"darkvision": 60, "passive_perception": 11}', ARRAY['Deep Speech'],
 '[{
   "name": "Tentacle",
   "type": "melee",
   "bonus": 5,
   "reach": 10,
   "damage": "1d4+3",
   "damage_type": "bludgeoning",
   "special": "Target is grappled (escape DC 13) and cannot breathe while grappled"
 }]',
 'grappling_strangler',
 '{"gold": "1d4", "items": [], "chance": 0.1}',
 200),

-- Death Dog (CR 1)
('Death Dog', 1, 'Medium', 'monstrosity', 'neutral evil', 12, 39, '6d8+12',
 '{"walk": 40}',
 15, 14, 14, 3, 13, 6,
 '{}', '{"perception": 5, "stealth": 4}',
 '{"darkvision": 120, "passive_perception": 15}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Multiattack",
   "type": "special",
   "description": "Makes two bite attacks"
 }, {
   "name": "Bite",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "1d6+2",
   "damage_type": "piercing",
   "special": "Target must succeed on DC 12 Constitution save or be poisoned for 1 minute"
 }]',
 'pack_hunter',
 '{"gold": "1d6", "items": [], "chance": 0.1}',
 200),

-- Ghoul (CR 1)
('Ghoul', 1, 'Medium', 'undead', 'chaotic evil', 12, 22, '5d8+5',
 '{"walk": 30}',
 13, 15, 12, 6, 10, 6,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 10}', ARRAY['Common'],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 2,
   "reach": 5,
   "damage": "2d6+2",
   "damage_type": "piercing"
 }, {
   "name": "Claws",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "2d4+2",
   "damage_type": "slashing",
   "special": "Target must succeed on DC 10 Constitution save or be paralyzed for 1 minute"
 }]',
 'undead_paralyzer',
 '{"gold": "1d4", "items": [], "chance": 0.1}',
 200),

-- Harpy (CR 1)
('Harpy', 1, 'Medium', 'monstrosity', 'chaotic evil', 11, 38, '7d8+7',
 '{"walk": 20, "fly": 40}',
 12, 13, 12, 7, 10, 13,
 '{}', '{}',
 '{"passive_perception": 10}', ARRAY['Common'],
 '[{
   "name": "Claws",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "2d4+1",
   "damage_type": "slashing"
 }, {
   "name": "Luring Song",
   "type": "special",
   "description": "Target must succeed on DC 11 Wisdom save or be charmed and move toward harpy"
 }]',
 'flying_charmer',
 '{"gold": "2d6", "items": [], "chance": 0.2}',
 200),

-- Hippogriff (CR 1)
('Hippogriff', 1, 'Large', 'monstrosity', 'unaligned', 11, 19, '3d10+3',
 '{"walk": 40, "fly": 60}',
 17, 13, 13, 2, 12, 8,
 '{}', '{"perception": 5}',
 '{"passive_perception": 15}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Multiattack",
   "type": "special",
   "description": "Makes two attacks: one with beak and one with claws"
 }, {
   "name": "Beak",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d10+3",
   "damage_type": "piercing"
 }, {
   "name": "Claws",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "2d6+3",
   "damage_type": "slashing"
 }]',
 'flying_mount',
 '{"gold": "1d6", "items": [], "chance": 0.1}',
 200),

-- Specter (CR 1)
('Specter', 1, 'Medium', 'undead', 'chaotic evil', 12, 22, '5d8',
 '{"walk": 0, "fly": 50}',
 1, 14, 11, 10, 10, 11,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 10}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Life Drain",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "3d6",
   "damage_type": "necrotic",
   "special": "Target must succeed on DC 10 Constitution save or maximum hit points reduced by damage taken"
 }]',
 'incorporeal_drainer',
 '{"gold": "0", "items": [], "chance": 0.0}',
 200),

-- Bugbear Warrior (CR 1)
('Bugbear Warrior', 1, 'Medium', 'humanoid', 'chaotic evil', 16, 27, '5d8+5',
 '{"walk": 30}',
 15, 14, 13, 8, 11, 9,
 '{}', '{"stealth": 6, "survival": 2}',
 '{"darkvision": 60, "passive_perception": 10}', ARRAY['Common', 'Goblin'],
 '[{
   "name": "Morningstar",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "2d8+2",
   "damage_type": "piercing"
 }, {
   "name": "Javelin",
   "type": "ranged",
   "bonus": 4,
   "range": "30/120",
   "damage": "1d6+2",
   "damage_type": "piercing"
 }]',
 'brutal_ambusher',
 '{"gold": "2d6", "items": ["morningstar", "javelin"], "chance": 0.3}',
 200),

-- Scarecrow (CR 1)
('Scarecrow', 1, 'Medium', 'construct', 'chaotic neutral', 11, 36, '8d8+8',
 '{"walk": 30}',
 11, 13, 12, 10, 10, 13,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 10}', ARRAY['Common'],
 '[{
   "name": "Multiattack",
   "type": "special",
   "description": "Makes two claw attacks"
 }, {
   "name": "Claw",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "1d4+1",
   "damage_type": "slashing"
 }, {
   "name": "Terrifying Glare",
   "type": "special",
   "description": "Target must succeed on DC 11 Wisdom save or be frightened until end of scarecrow''s next turn"
 }]',
 'fear_inducer',
 '{"gold": "1d4", "items": [], "chance": 0.1}',
 200),

-- Giant Spider (CR 1)
('Giant Spider', 1, 'Large', 'beast', 'unaligned', 14, 26, '4d10+4',
 '{"walk": 30, "climb": 30}',
 14, 16, 12, 2, 11, 4,
 '{}', '{"stealth": 7}',
 '{"blindsight": 10, "darkvision": 60, "passive_perception": 10}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d8+3",
   "damage_type": "piercing",
   "special": "Target must succeed on DC 11 Constitution save or take 2d8 poison damage and be poisoned for 1 hour"
 }, {
   "name": "Web",
   "type": "ranged",
   "bonus": 5,
   "range": "30/60",
   "damage": "0",
   "damage_type": "special",
   "special": "Target is restrained by webbing (escape DC 12)"
 }]',
 'web_trapper',
 '{"gold": "0", "items": [], "chance": 0.05}',
 200),

-- Giant Hyena (CR 1)
('Giant Hyena', 1, 'Large', 'beast', 'unaligned', 12, 45, '6d10+12',
 '{"walk": 50}',
 16, 14, 14, 2, 12, 7,
 '{}', '{"perception": 3}',
 '{"passive_perception": 13}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d10+3",
   "damage_type": "piercing"
 }, {
   "name": "Rampage",
   "type": "special",
   "description": "When hyena reduces creature to 0 hit points, it can move up to half speed and make bite attack"
 }]',
 'pack_hunter',
 '{"gold": "0", "items": [], "chance": 0.05}',
 200),

-- Myconid Spore Servant (CR 1)
('Myconid Spore Servant', 1, 'Medium', 'plant', 'unaligned', 10, 22, '4d8+4',
 '{"walk": 20}',
 10, 10, 12, 2, 3, 1,
 '{}', '{}',
 '{"blindsight": 30, "passive_perception": 6}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Fist",
   "type": "melee",
   "bonus": 2,
   "reach": 5,
   "damage": "1d6+2",
   "damage_type": "bludgeoning"
 }]',
 'mindless_servant',
 '{"gold": "0", "items": [], "chance": 0.0}',
 200),

-- =====================================================
-- NEW MONSTERS - CR 2 (XP 450)
-- =====================================================

-- Will-o'-Wisp (CR 2)
('Will-o''-Wisp', 2, 'Tiny', 'undead', 'chaotic evil', 19, 22, '9d4',
 '{"walk": 0, "fly": 50}',
 1, 28, 10, 13, 14, 11,
 '{}', '{}',
 '{"darkvision": 120, "passive_perception": 12}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Shock",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "2d8+4",
   "damage_type": "lightning"
 }, {
   "name": "Invisibility",
   "type": "special",
   "description": "Wisp becomes invisible until it attacks or until concentration ends"
 }]',
 'incorporeal_shock',
 '{"gold": "0", "items": [], "chance": 0.0}',
 450),

-- Ghast (CR 2)
('Ghast', 2, 'Medium', 'undead', 'chaotic evil', 13, 36, '8d8+8',
 '{"walk": 30}',
 16, 17, 12, 11, 10, 8,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 10}', ARRAY['Common'],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "2d8+3",
   "damage_type": "piercing"
 }, {
   "name": "Claws",
   "type": "melee",
   "bonus": 5,
   "reach": 10,
   "damage": "2d6+3",
   "damage_type": "slashing",
   "special": "Target must succeed on DC 10 Constitution save or be paralyzed for 1 minute"
 }]',
 'undead_paralyzer',
 '{"gold": "2d6", "items": [], "chance": 0.15}',
 450),

-- Awakened Tree (CR 2)
('Awakened Tree', 2, 'Huge', 'plant', 'unaligned', 13, 59, '7d12+14',
 '{"walk": 20}',
 19, 6, 15, 10, 10, 7,
 '{}', '{}',
 '{"passive_perception": 10}', ARRAY['Common'],
 '[{
   "name": "Slam",
   "type": "melee",
   "bonus": 6,
   "reach": 10,
   "damage": "3d6+4",
   "damage_type": "bludgeoning"
 }, {
   "name": "Animate Trees",
   "type": "special",
   "description": "Animates 1-2 trees within 60 feet to fight for 1 day"
 }]',
 'forest_guardian',
 '{"gold": "0", "items": [], "chance": 0.05}',
 450),

-- Gelatinous Cube (CR 2)
('Gelatinous Cube', 2, 'Large', 'ooze', 'unaligned', 6, 84, '12d10+24',
 '{"walk": 15}',
 14, 3, 14, 1, 6, 1,
 '{}', '{}',
 '{"blindsight": 60, "passive_perception": 8}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Pseudopod",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "3d6+2",
   "damage_type": "acid"
 }, {
   "name": "Engulf",
   "type": "special",
   "description": "Creatures in cube''s space take acid damage and are restrained"
 }]',
 'dungeon_cleaner',
 '{"gold": "3d6", "items": [], "chance": 0.4}',
 450),

-- Mimic (CR 2)
('Mimic', 2, 'Medium', 'monstrosity', 'neutral', 12, 58, '9d8+18',
 '{"walk": 15}',
 17, 12, 15, 5, 13, 8,
 '{}', '{"stealth": 5}',
 '{"darkvision": 60, "passive_perception": 11}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Pseudopod",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d8+3",
   "damage_type": "bludgeoning",
   "special": "Target is grappled (escape DC 13) and restrained while grappled"
 }, {
   "name": "Bite",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d8+3",
   "damage_type": "piercing",
   "special": "Plus 1d8 acid damage"
 }]',
 'treasure_mimic',
 '{"gold": "5d6", "items": [], "chance": 0.6}',
 450),

-- Carrion Crawler (CR 2)
('Carrion Crawler', 2, 'Large', 'monstrosity', 'unaligned', 13, 51, '6d12+12',
 '{"walk": 30, "climb": 30}',
 14, 13, 15, 1, 12, 5,
 '{}', '{"perception": 3}',
 '{"darkvision": 60, "passive_perception": 13}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Multiattack",
   "type": "special",
   "description": "Makes two attacks: one with tentacles and one with bite"
 }, {
   "name": "Tentacles",
   "type": "melee",
   "bonus": 8,
   "reach": 10,
   "damage": "1d4+2",
   "damage_type": "poison",
   "special": "Target must succeed on DC 13 Constitution save or be poisoned for 1 minute and paralyzed while poisoned"
 }, {
   "name": "Bite",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "2d4+2",
   "damage_type": "piercing"
 }]',
 'paralyzing_scavenger',
 '{"gold": "1d6", "items": [], "chance": 0.1}',
 450),

-- Quaggoth (CR 2)
('Quaggoth', 2, 'Medium', 'humanoid', 'chaotic neutral', 13, 45, '6d8+18',
 '{"walk": 30, "climb": 30}',
 17, 12, 16, 6, 12, 7,
 '{}', '{"athletics": 5}',
 '{"darkvision": 120, "passive_perception": 11}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Multiattack",
   "type": "special",
   "description": "Makes two claw attacks"
 }, {
   "name": "Claw",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d6+3",
   "damage_type": "slashing"
 }]',
 'berserker_climber',
 '{"gold": "2d6", "items": [], "chance": 0.2}',
 450),

-- Berserker (CR 2)
('Berserker', 2, 'Medium', 'humanoid', 'any chaotic', 13, 67, '9d8+27',
 '{"walk": 30}',
 16, 12, 17, 9, 11, 9,
 '{}', '{}',
 '{"passive_perception": 10}', ARRAY['Common'],
 '[{
   "name": "Greataxe",
   "type": "melee",
   "bonus": 5,
   "reach": 5,
   "damage": "1d12+3",
   "damage_type": "slashing"
 }, {
   "name": "Reckless",
   "type": "special",
   "description": "Advantage on melee attacks, but attack rolls against berserker have advantage until next turn"
 }]',
 'reckless_warrior',
 '{"gold": "3d6", "items": ["greataxe"], "chance": 0.4}',
 450),

-- Gargoyle (CR 2)
('Gargoyle', 2, 'Medium', 'elemental', 'chaotic evil', 15, 52, '7d8+21',
 '{"walk": 30, "fly": 60}',
 15, 11, 16, 6, 11, 7,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 10}', ARRAY['Terran'],
 '[{
   "name": "Multiattack",
   "type": "special",
   "description": "Makes two attacks: one with bite and one with claws"
 }, {
   "name": "Bite",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "1d6+2",
   "damage_type": "piercing"
 }, {
   "name": "Claws",
   "type": "melee",
   "bonus": 4,
   "reach": 5,
   "damage": "1d6+2",
   "damage_type": "slashing"
 }]',
 'stone_guardian',
 '{"gold": "1d6", "items": [], "chance": 0.1}',
 450),

-- Glasswork Golem (CR 2)
('Glasswork Golem', 2, 'Medium', 'construct', 'unaligned', 13, 36, '8d8+8',
 '{"walk": 25}',
 10, 14, 12, 3, 8, 1,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 9}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Multiattack",
   "type": "special",
   "description": "Makes two slam attacks"
 }, {
   "name": "Slam",
   "type": "melee",
   "bonus": 3,
   "reach": 5,
   "damage": "1d8+2",
   "damage_type": "bludgeoning"
 }, {
   "name": "Shatter",
   "type": "special",
   "description": "When destroyed, shards deal 2d6 slashing damage to creatures within 5 feet"
 }]',
 'fragile_construct',
 '{"gold": "0", "items": [], "chance": 0.0}',
 450),

-- Giant Constrictor Snake (CR 2)
('Giant Constrictor Snake', 2, 'Huge', 'beast', 'unaligned', 12, 60, '8d12+16',
 '{"walk": 30, "swim": 30}',
 19, 14, 15, 1, 10, 3,
 '{}', '{"perception": 2}',
 '{"blindsight": 10, "passive_perception": 12}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Bite",
   "type": "melee",
   "bonus": 6,
   "reach": 10,
   "damage": "2d6+4",
   "damage_type": "piercing"
 }, {
   "name": "Constrict",
   "type": "melee",
   "bonus": 6,
   "reach": 5,
   "damage": "2d8+4",
   "damage_type": "bludgeoning",
   "special": "Target is grappled (escape DC 16) and restrained while grappled"
 }]',
 'constrictor_predator',
 '{"gold": "0", "items": [], "chance": 0.05}',
 450),

-- Gibbering Mouther (CR 2)
('Gibbering Mouther', 2, 'Medium', 'aberration', 'neutral', 9, 67, '9d8+27',
 '{"walk": 10, "swim": 10}',
 10, 8, 16, 3, 10, 6,
 '{}', '{}',
 '{"darkvision": 60, "passive_perception": 10}', ARRAY[]::VARCHAR[],
 '[{
   "name": "Multiattack",
   "type": "special",
   "description": "Makes one bite attack against each creature within 5 feet"
 }, {
   "name": "Bite",
   "type": "melee",
   "bonus": 2,
   "reach": 5,
   "damage": "1d6+2",
   "damage_type": "piercing"
 }, {
   "name": "Gibbering",
   "type": "special",
   "description": "Creatures within 20 feet must succeed on DC 10 Wisdom save or cannot take reactions and movement is halved"
 }]',
 'madness_inducer',
 '{"gold": "1d4", "items": [], "chance": 0.05}',
 450);