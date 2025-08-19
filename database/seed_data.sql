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
INSERT INTO game_states (character_id, current_location, dungeon_level, rooms_cleared) VALUES
((SELECT id FROM characters WHERE name = 'Test Fighter'), 'town', 0, 0);

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