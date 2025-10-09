-- Migration 032: Add Warlock Invocation-based Abilities to Unified System
-- This migration adds invocations that grant at-will spellcasting or active abilities

INSERT OR IGNORE INTO class_abilities (ability_id, class_name, ability_name, description, level_gained, subclass_requirement, feature_type, usage_type, uses_formula, scaling_type, mechanics) VALUES

('invocation_armor_of_shadows', 'Warlock', 'Armor of Shadows (Invocation)', 'You can cast mage armor on yourself at will, without expending a spell slot or material components.', 1, NULL, 'action', 'unlimited', NULL, 'fixed', '{"invocation_id":"armor_of_shadows","spell":"mage_armor","cost":"none","target":"self","requires_invocation":true}'),

('invocation_fiendish_vigor', 'Warlock', 'Fiendish Vigor (Invocation)', 'You can cast false life on yourself at will as a 1st-level spell, without expending a spell slot or material components.', 1, NULL, 'action', 'unlimited', NULL, 'fixed', '{"invocation_id":"fiendish_vigor","spell":"false_life","cost":"none","target":"self","spell_level":1,"requires_invocation":true}'),

('invocation_ascendant_step', 'Warlock', 'Ascendant Step (Invocation)', 'You can cast levitate on yourself at will, without expending a spell slot or material components.', 1, NULL, 'action', 'unlimited', NULL, 'fixed', '{"invocation_id":"ascendant_step","spell":"levitate","cost":"none","target":"self","requires_invocation":true}'),

('invocation_visions_of_distant_realms', 'Warlock', 'Visions of Distant Realms (Invocation)', 'You can cast arcane eye at will, without expending a spell slot.', 1, NULL, 'action', 'unlimited', NULL, 'fixed', '{"invocation_id":"visions_of_distant_realms","spell":"arcane_eye","cost":"none","requires_invocation":true}'),

('invocation_eldritch_smite', 'Warlock', 'Eldritch Smite (Invocation)', 'Once per turn when you hit with your pact weapon, you can expend a spell slot to deal extra 1d8 force damage per slot level and knock the target prone.', 1, NULL, 'special', 'unlimited', NULL, 'fixed', '{"invocation_id":"eldritch_smite","trigger":"pact_weapon_hit","damage":"1d8_per_slot","damage_type":"force","effect":"prone","requires":"pact_blade","requires_invocation":true}'),

('invocation_agonizing_blast', 'Warlock', 'Agonizing Blast (Invocation)', 'When you cast eldritch blast, add your Charisma modifier to the damage it deals on a hit.', 1, NULL, 'passive', 'permanent', NULL, 'fixed', '{"invocation_id":"agonizing_blast","modifies":"eldritch_blast","bonus_damage":"charisma_modifier","requires_invocation":true}'),

('invocation_devils_sight', 'Warlock', 'Devils Sight (Invocation)', 'You can see normally in darkness, both magical and nonmagical, to a distance of 120 feet.', 1, NULL, 'passive', 'permanent', NULL, 'fixed', '{"invocation_id":"devils_sight","darkvision":120,"magical_darkness":true,"requires_invocation":true}'),

('invocation_eldritch_mind', 'Warlock', 'Eldritch Mind (Invocation)', 'You have advantage on Constitution saving throws that you make to maintain concentration on a spell.', 1, NULL, 'passive', 'permanent', NULL, 'fixed', '{"invocation_id":"eldritch_mind","advantage":"concentration_saves","requires_invocation":true}'),

('invocation_thirsting_blade', 'Warlock', 'Thirsting Blade (Invocation)', 'You can attack with your pact weapon twice, instead of once, whenever you take the Attack action on your turn.', 1, NULL, 'passive', 'permanent', NULL, 'fixed', '{"invocation_id":"thirsting_blade","extra_attacks":1,"requires":"pact_blade","requires_invocation":true}'),

('invocation_gift_of_the_depths', 'Warlock', 'Gift of the Depths (Invocation)', 'You can breathe underwater, and you gain a swimming speed equal to your walking speed.', 1, NULL, 'passive', 'permanent', NULL, 'fixed', '{"invocation_id":"gift_of_the_depths","underwater_breathing":true,"swim_speed":"equal_to_walking","requires_invocation":true}');
