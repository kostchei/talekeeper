-- Migration 031: Add Paladin and Warlock to Unified Class Abilities System
-- Extends the unified system to include Paladin and Warlock classes

-- ============================================================
-- PALADIN ABILITIES
-- ============================================================

INSERT OR IGNORE INTO class_abilities (ability_id, class_name, ability_name, description, level_gained, subclass_requirement, feature_type, usage_type, uses_formula, scaling_type, mechanics) VALUES

('lay_on_hands', 'Paladin', 'Lay on Hands', 'You have a pool of healing power that can restore 5 HP per Paladin level. As an action, you can touch a creature to restore HP from your pool (up to the maximum remaining). You can also expend 5 HP from your pool to cure one disease or neutralize one poison.', 1, NULL, 'action', 'long_rest', '5 * level', 'level_based', '{"heal_type":"pool","pool_formula":"5 * level","action_cost":"action","can_cure":"disease_or_poison","cure_cost":5}'),

('divine_sense', 'Paladin', 'Divine Sense', 'You can use a Bonus Action to detect celestials, fiends, and undead within 60 feet until the end of your next turn. You know the location of any such creature but not its identity. You can use this a number of times equal to your proficiency bonus.', 1, NULL, 'bonus_action', 'long_rest', 'proficiency_bonus', 'proficiency_based', '{"range":60,"detects":["celestial","fiend","undead"],"duration":"end_of_next_turn","reveals":"location_only"}'),

('fighting_style_paladin', 'Paladin', 'Fighting Style', 'You adopt a Fighting Style as a specialty.', 2, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"choose_fighting_style","options":["defense","dueling","great_weapon_fighting","protection"]}'),

('paladin_spellcasting', 'Paladin', 'Spellcasting', 'You have the ability to cast Paladin spells using Charisma as your spellcasting ability.', 1, NULL, 'passive', 'permanent', NULL, 'fixed', '{"spellcasting_class":"paladin","spellcasting_ability":"charisma","spell_slots":"half_caster","prepared_spells_formula":"charisma_modifier + (level // 2)"}'),

('divine_smite', 'Paladin', 'Divine Smite', 'When you hit with a melee weapon attack, you can expend a spell slot to deal extra radiant damage. The damage is 2d8 for a 1st-level slot, plus 1d8 for each slot level above 1st (max 5d8). Add 1d8 if the target is undead or fiend (max 6d8).', 2, NULL, 'special', 'unlimited', NULL, 'fixed', '{"trigger":"melee_hit","damage_base":"2d8","damage_per_level":"1d8","max_dice":5,"bonus_vs":["undead","fiend"],"bonus_damage":"1d8","requires":"spell_slot"}'),

('channel_divinity_paladin', 'Paladin', 'Channel Divinity', 'You can channel divine energy to fuel magical effects. You start with one effect based on your Sacred Oath. You can use Channel Divinity once, regaining use on a short rest. At 7th level you can use it twice between rests, and at 15th level three times.', 3, NULL, 'special', 'short_rest', '1 + (level >= 7) + (level >= 15)', 'level_based', '{"uses_base":1,"increases":[{"level":7,"uses":2},{"level":15,"uses":3}],"oath_specific":true}'),

('sacred_oath', 'Paladin', 'Sacred Oath', 'You swear an oath that binds you to the cause of righteousness.', 3, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"choose_subclass","options":["devotion","ancients","vengeance"]}'),

('extra_attack_paladin', 'Paladin', 'Extra Attack', 'You can attack twice instead of once whenever you take the Attack action.', 5, NULL, 'passive', 'permanent', NULL, 'fixed', '{"extra_attacks":1}'),

('aura_of_protection', 'Paladin', 'Aura of Protection', 'Whenever you or a friendly creature within 10 feet must make a saving throw, they gain a bonus equal to your Charisma modifier. At 18th level, the range increases to 30 feet.', 6, NULL, 'passive', 'permanent', NULL, 'fixed', '{"aura_range":10,"aura_range_18":30,"bonus":"charisma_modifier","applies_to":"all_saves","affects":"self_and_allies"}'),

('aura_of_courage', 'Paladin', 'Aura of Courage', 'You and friendly creatures within 10 feet can''t be Frightened. At 18th level, the range increases to 30 feet.', 10, NULL, 'passive', 'permanent', NULL, 'fixed', '{"aura_range":10,"aura_range_18":30,"immunity":"frightened","affects":"self_and_allies"}'),

('improved_divine_smite', 'Paladin', 'Improved Divine Smite', 'You are so suffused with righteous might that all your melee weapon attacks carry divine power with them. Whenever you hit with a melee weapon, the creature takes an extra 1d8 radiant damage.', 11, NULL, 'passive', 'permanent', NULL, 'fixed', '{"trigger":"all_melee_hits","damage":"1d8","damage_type":"radiant"}'),

('cleansing_touch', 'Paladin', 'Cleansing Touch', 'You can use your action to end one spell on yourself or one willing creature you touch. You can use this a number of times equal to your Charisma modifier (minimum 1).', 14, NULL, 'action', 'long_rest', 'max(1, charisma_modifier)', 'ability_based', '{"action_cost":"action","effect":"end_spell","target":"self_or_willing","range":"touch"}'),

('divine_health', 'Paladin', 'Divine Health', 'You are immune to disease.', 3, NULL, 'passive', 'permanent', NULL, 'fixed', '{"immunity":"disease"}'),

('devotion_sacred_weapon', 'Paladin', 'Sacred Weapon', 'As an action, you imbue one weapon with positive energy. For 1 minute, you add your Charisma modifier to attack rolls with that weapon (min +1), and it emits bright light in a 20-foot radius. You can use this once per rest.', 3, 'Devotion', 'action', 'short_rest', '1', 'fixed', '{"action_cost":"action","duration_minutes":1,"attack_bonus":"charisma_modifier","min_bonus":1,"light_radius":20,"channel_divinity":true}'),

('devotion_turn_unholy', 'Paladin', 'Turn the Unholy', 'As an action, you present your holy symbol and each fiend or undead within 30 feet must make a Wisdom save (DC = spell save DC) or be turned for 1 minute.', 3, 'Devotion', 'action', 'short_rest', '1', 'fixed', '{"action_cost":"action","range":30,"targets":["fiend","undead"],"save":"wisdom","duration_minutes":1,"channel_divinity":true}'),

('devotion_aura_of_devotion', 'Paladin', 'Aura of Devotion', 'You and friendly creatures within 10 feet can''t be Charmed. At 18th level, the range increases to 30 feet.', 7, 'Devotion', 'passive', 'permanent', NULL, 'fixed', '{"aura_range":10,"aura_range_18":30,"immunity":"charmed","affects":"self_and_allies"}'),

('devotion_purity_of_spirit', 'Paladin', 'Purity of Spirit', 'You are always under the effects of a Protection from Evil and Good spell.', 15, 'Devotion', 'passive', 'permanent', NULL, 'fixed', '{"effect":"protection_from_evil_and_good_permanent"}'),

('devotion_holy_nimbus', 'Paladin', 'Holy Nimbus', 'As an action, you emanate sunlight in a 30-foot radius for 1 minute. Bright light fills the area, enemies take 10 radiant damage at the start of their turns, and you have advantage on saves vs spells cast by fiends and undead. Once used, you can''t use this again until you finish a Long Rest.', 20, 'Devotion', 'action', 'long_rest', '1', 'fixed', '{"action_cost":"action","duration_minutes":1,"radius":30,"damage":"10","damage_type":"radiant","trigger":"enemy_turn_start","advantage_vs":["fiend_spells","undead_spells"]}');

-- ============================================================
-- WARLOCK ABILITIES
-- ============================================================

INSERT OR IGNORE INTO class_abilities (ability_id, class_name, ability_name, description, level_gained, subclass_requirement, feature_type, usage_type, uses_formula, scaling_type, mechanics) VALUES

('pact_magic', 'Warlock', 'Pact Magic', 'You can cast Warlock spells using Charisma. Your spell slots are all the same level and you regain all expended slots on a Short or Long Rest. Pact Magic slots automatically upcast spells to their slot level.', 1, NULL, 'passive', 'permanent', NULL, 'fixed', '{"spellcasting_class":"warlock","spellcasting_ability":"charisma","slot_recovery":"short_rest","auto_upcast":true,"slot_progression":"pact_magic"}'),

('eldritch_invocations', 'Warlock', 'Eldritch Invocations', 'You learn mystic invocations that grant you magical abilities. You learn 1 invocation at 1st level, and more as you gain levels.', 1, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"choose_invocations","invocations_known_formula":"invocations_by_level","can_replace_on_level_up":true}'),

('magical_cunning', 'Warlock', 'Magical Cunning', 'When you finish a Short Rest, you can recover expended Pact Magic spell slots. Once you use this, you can''t do so again until you finish a Long Rest. The number of slots you regain is up to half your max slots (rounded up).', 2, NULL, 'special', 'long_rest', '1', 'fixed', '{"trigger":"short_rest","slots_recovered":"ceiling(max_slots / 2)","uses_per_long_rest":1}'),

('warlock_subclass', 'Warlock', 'Warlock Subclass', 'You make a pact with an otherworldly patron who grants you power.', 3, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"choose_subclass","options":["fiend","archfey","great_old_one"]}'),

('pact_boon', 'Warlock', 'Pact Boon', 'Your patron bestows a gift upon you. Choose one of Pact of the Blade, Pact of the Chain, or Pact of the Tome.', 3, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"choose_pact_boon","options":["blade","chain","tome"]}'),

('ability_score_improvement_warlock', 'Warlock', 'Ability Score Improvement', 'You can increase one ability score by 2, or two ability scores by 1 each, or take a feat.', 4, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"asi_or_feat","repeats_at":[8,12,16,19]}'),

('contact_patron', 'Warlock', 'Contact Patron', 'You always have the Contact Other Plane spell prepared, and it doesn''t count against your number of prepared spells.', 9, NULL, 'passive', 'permanent', NULL, 'fixed', '{"spell_always_prepared":"contact_other_plane","doesnt_count_against_limit":true}'),

('mystic_arcanum_6', 'Warlock', 'Mystic Arcanum (6th level)', 'Choose one 6th-level Warlock spell. You can cast it once without expending a spell slot. You regain the ability to do so when you finish a Long Rest.', 11, NULL, 'special', 'long_rest', '1', 'fixed', '{"spell_level":6,"choose_one_spell":true,"free_cast":true}'),

('mystic_arcanum_7', 'Warlock', 'Mystic Arcanum (7th level)', 'Choose one 7th-level Warlock spell. You can cast it once without expending a spell slot. You regain the ability to do so when you finish a Long Rest.', 13, NULL, 'special', 'long_rest', '1', 'fixed', '{"spell_level":7,"choose_one_spell":true,"free_cast":true}'),

('mystic_arcanum_8', 'Warlock', 'Mystic Arcanum (8th level)', 'Choose one 8th-level Warlock spell. You can cast it once without expending a spell slot. You regain the ability to do so when you finish a Long Rest.', 15, NULL, 'special', 'long_rest', '1', 'fixed', '{"spell_level":8,"choose_one_spell":true,"free_cast":true}'),

('mystic_arcanum_9', 'Warlock', 'Mystic Arcanum (9th level)', 'Choose one 9th-level Warlock spell. You can cast it once without expending a spell slot. You regain the ability to do so when you finish a Long Rest.', 17, NULL, 'special', 'long_rest', '1', 'fixed', '{"spell_level":9,"choose_one_spell":true,"free_cast":true}'),

('eldritch_master', 'Warlock', 'Eldritch Master', 'When you use your Magical Cunning feature, you regain all your expended Pact Magic spell slots instead of only half.', 20, NULL, 'passive', 'permanent', NULL, 'fixed', '{"modifies":"magical_cunning","slots_recovered":"all"}'),

('fiend_dark_ones_blessing', 'Warlock', 'Dark One''s Blessing', 'When you reduce a hostile creature to 0 HP, you gain temporary HP equal to your Charisma modifier + Warlock level (min 1).', 1, 'Fiend', 'passive', 'unlimited', NULL, 'fixed', '{"trigger":"enemy_to_0_hp","temp_hp_formula":"charisma_modifier + level","min_temp_hp":1}'),

('fiend_dark_ones_own_luck', 'Warlock', 'Dark One''s Own Luck', 'When you make an ability check or saving throw, you can add a d10 to your roll. You can use this after seeing the roll but before knowing if it succeeds or fails. Once used, you can''t use it again until you finish a Short or Long Rest.', 6, 'Fiend', 'special', 'short_rest', '1', 'fixed', '{"trigger":"check_or_save","bonus":"1d10","timing":"after_roll_before_result"}'),

('fiend_fiendish_resilience', 'Warlock', 'Fiendish Resilience', 'When you finish a Short or Long Rest, choose one damage type. You gain resistance to that damage type until you choose a different one with this feature. Damage from magical weapons or silver weapons ignores this resistance.', 10, 'Fiend', 'special', 'short_rest', NULL, 'fixed', '{"effect":"choose_resistance","excludes":["magical_weapons","silver_weapons"],"duration":"until_changed"}'),

('fiend_hurl_through_hell', 'Warlock', 'Hurl Through Hell', 'When you hit a creature with an attack, you can banish it to the lower planes until the end of your next turn. When it returns, it takes 10d10 psychic damage. Once used, you can''t use this again until you finish a Long Rest.', 14, 'Fiend', 'special', 'long_rest', '1', 'fixed', '{"trigger":"hit_with_attack","effect":"banish","duration":"end_of_next_turn","return_damage":"10d10","damage_type":"psychic"}');

-- ============================================================
-- Additional Scaling Formula
-- ============================================================

INSERT OR IGNORE INTO ability_scaling_formulas (formula_name, description, formula_type, formula_data) VALUES
('invocations_by_level', 'Warlock Eldritch Invocations known', 'lookup', '{"1":0,"2":2,"3":2,"4":2,"5":3,"6":3,"7":4,"8":4,"9":5,"10":5,"11":5,"12":6,"13":6,"14":6,"15":7,"16":7,"17":7,"18":8,"19":8,"20":8}');

-- ============================================================
-- Migration Complete
-- ============================================================
