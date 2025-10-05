-- Subclass Features Migration
-- Core subclass features for D&D 2024 classes

-- FIGHTER SUBCLASSES
-- Champion Fighter
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('champion', 3, 'Improved Critical', 'passive', 'Score critical hits on rolls of 19-20', '{"crit_range": [19, 20]}'),
('champion', 7, 'Remarkable Athlete', 'passive', 'Add half proficiency to Str/Dex/Con checks', '{"half_proficiency": ["strength", "dexterity", "constitution"]}'),
('champion', 10, 'Additional Fighting Style', 'passive', 'Learn another fighting style', '{"additional_fighting_style": true}'),
('champion', 15, 'Superior Critical', 'passive', 'Score critical hits on rolls of 18-20', '{"crit_range": [18, 19, 20]}'),
('champion', 18, 'Survivor', 'passive', 'Regain HP at start of turn if below half', '{"hp_regen": "5_plus_con_mod", "condition": "below_half_hp"}');

-- Battle Master Fighter
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('battle_master', 3, 'Combat Superiority', 'passive', 'Learn maneuvers and gain superiority dice', '{"superiority_dice": 4, "die_type": "d8", "maneuvers_known": 3}'),
('battle_master', 3, 'Student of War', 'passive', 'Proficiency with artisans tools', '{"tool_proficiency": "artisans_tools"}'),
('battle_master', 7, 'Know Your Enemy', 'action', 'Learn information about creatures', '{"study_time": "1_minute", "info_gained": "combat_stats"}'),
('battle_master', 10, 'Improved Combat Superiority', 'passive', 'Superiority dice become d10s', '{"die_type": "d10", "additional_maneuvers": 2}'),
('battle_master', 15, 'Relentless', 'passive', 'Regain one superiority die when you roll initiative', '{"initiative_recovery": 1}'),
('battle_master', 18, 'Improved Combat Superiority', 'passive', 'Superiority dice become d12s', '{"die_type": "d12", "additional_maneuvers": 2}');

-- Eldritch Knight Fighter
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('eldritch_knight', 3, 'Spellcasting', 'passive', 'Cast wizard spells using Intelligence', '{"spell_slots": [2, 0, 0, 0], "spells_known": 2, "cantrips_known": 2}'),
('eldritch_knight', 3, 'Weapon Bond', 'action', 'Bond with weapons for magical connection', '{"bonded_weapons": 2, "summon_range": "1_mile"}'),
('eldritch_knight', 7, 'War Magic', 'bonus_action', 'Cast cantrip then attack as bonus action', '{"cantrip_plus_attack": true}'),
('eldritch_knight', 10, 'Eldritch Strike', 'passive', 'Weapon attacks impose disadvantage on saves', '{"save_disadvantage": "next_spell"}'),
('eldritch_knight', 15, 'Arcane Charge', 'action', 'Teleport when using Action Surge', '{"teleport_range": 30, "requires_action_surge": true}'),
('eldritch_knight', 18, 'Improved War Magic', 'action', 'Cast spell then attack as bonus action', '{"spell_plus_attack": true}');

-- ROGUE SUBCLASSES
-- Thief
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('thief', 3, 'Fast Hands', 'bonus_action', 'Use Cunning Action for object interactions', '{"additional_cunning_actions": ["use_object", "sleight_of_hand", "disarm_trap"]}'),
('thief', 3, 'Second-Story Work', 'passive', 'Climbing and jumping bonuses', '{"climb_speed": "walking_speed", "jump_distance_bonus": "dex_modifier"}'),
('thief', 9, 'Supreme Sneak', 'passive', 'Advantage on Stealth if you move no more than half speed', '{"stealth_advantage": "half_movement"}'),
('thief', 13, 'Use Magic Device', 'passive', 'Ignore class/race/level requirements for magic items', '{"ignore_item_restrictions": true}'),
('thief', 17, 'Thief Reflexes', 'passive', 'Take two turns in first round of combat', '{"first_round_double_turn": true}');

-- Assassin
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('assassin', 3, 'Bonus Proficiencies', 'passive', 'Proficiency with disguise kit and poisoners kit', '{"tool_proficiencies": ["disguise_kit", "poisoners_kit"]}'),
('assassin', 3, 'Assassinate', 'passive', 'Advantage against creatures that havent acted, automatic crit on surprised', '{"advantage_vs_unacted": true, "crit_vs_surprised": true}'),
('assassin', 9, 'Infiltration Expertise', 'passive', 'Create false identities', '{"create_identity": "7_days", "identity_cost": "25gp"}'),
('assassin', 13, 'Impostor', 'action', 'Mimic speech and behavior of others', '{"mimic_person": "3_hours_study", "deception_advantage": true}'),
('assassin', 17, 'Death Strike', 'passive', 'Double damage on surprised creatures that fail Con save', '{"damage_multiplier": 2, "save_type": "constitution", "save_dc": "8_plus_prof_plus_dex"}');

-- Arcane Trickster
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('arcane_trickster', 3, 'Spellcasting', 'passive', 'Cast wizard spells using Intelligence', '{"spell_slots": [2, 0, 0, 0], "spells_known": 2, "cantrips_known": 2, "school_restriction": "enchantment_illusion"}'),
('arcane_trickster', 3, 'Mage Hand Legerdemain', 'bonus_action', 'Enhanced Mage Hand capabilities', '{"invisible_mage_hand": true, "sleight_of_hand_range": 30, "disarm_traps": true}'),
('arcane_trickster', 9, 'Magical Ambush', 'passive', 'Creatures have disadvantage on saves against spells when hidden', '{"spell_save_disadvantage": "when_hidden"}'),
('arcane_trickster', 13, 'Versatile Trickster', 'bonus_action', 'Use Mage Hand to distract for Sneak Attack', '{"mage_hand_sneak_attack": true}'),
('arcane_trickster', 17, 'Spell Thief', 'reaction', 'Steal spells when targeted by them', '{"steal_spell": true, "spell_level_max": 4, "uses_per_long_rest": 1}');

-- BARBARIAN SUBCLASSES
-- Berserker
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('berserker', 3, 'Frenzy', 'bonus_action', 'Make additional attack while raging', '{"bonus_attack_while_raging": true, "exhaustion_cost": 1}'),
('berserker', 6, 'Mindless Rage', 'passive', 'Cannot be charmed or frightened while raging', '{"rage_charm_immunity": true, "rage_fear_immunity": true}'),
('berserker', 10, 'Intimidating Presence', 'action', 'Frighten creatures with your presence', '{"frighten_action": true, "range": 30, "save_type": "wisdom"}'),
('berserker', 14, 'Retaliation', 'reaction', 'Attack when you take damage in melee', '{"reaction_attack_when_damaged": true, "melee_only": true}');

-- Totem Warrior
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('totem_warrior', 3, 'Spirit Seeker', 'passive', 'Ritual casting and animal communication', '{"ritual_spells": ["beast_sense", "speak_with_animals"]}'),
('totem_warrior', 3, 'Totem Spirit', 'passive', 'Choose animal spirit for rage benefits', '{"totem_choice": ["bear", "eagle", "wolf"], "rage_enhancement": true}'),
('totem_warrior', 6, 'Aspect of the Beast', 'passive', 'Gain animal-like abilities', '{"totem_passive_ability": true}'),
('totem_warrior', 10, 'Spirit Walker', 'passive', 'Cast commune with nature as ritual', '{"ritual_spell": "commune_with_nature"}'),
('totem_warrior', 14, 'Totemic Attunement', 'passive', 'Gain powerful totem ability while raging', '{"totem_rage_capstone": true}');

-- WIZARD SUBCLASSES
-- School of Evocation
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('evocation', 2, 'Evocation Savant', 'passive', 'Evocation spells cost half time and gold to copy', '{"spell_copy_discount": 0.5, "school": "evocation"}'),
('evocation', 2, 'Sculpt Spells', 'passive', 'Protect allies from your evocation spells', '{"sculpt_spell_targets": "1_plus_spell_level"}'),
('evocation', 6, 'Potent Cantrip', 'passive', 'Cantrips deal half damage on missed saves', '{"cantrip_half_damage": true}'),
('evocation', 10, 'Empowered Evocation', 'passive', 'Add Intelligence modifier to evocation spell damage', '{"damage_bonus": "intelligence_modifier", "school": "evocation"}'),
('evocation', 14, 'Overchannel', 'action', 'Maximize damage of evocation spells', '{"maximize_damage": "spell_level_1_to_5", "self_damage": true}');

-- School of Abjuration
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('abjuration', 2, 'Abjuration Savant', 'passive', 'Abjuration spells cost half time and gold to copy', '{"spell_copy_discount": 0.5, "school": "abjuration"}'),
('abjuration', 2, 'Arcane Ward', 'passive', 'Create protective ward when casting abjuration spells', '{"ward_hp": "2_times_wizard_level_plus_int", "recharge": "abjuration_spells"}'),
('abjuration', 6, 'Projected Ward', 'reaction', 'Use ward to protect others within 30 feet', '{"ward_range": 30, "protect_others": true}'),
('abjuration', 10, 'Improved Abjuration', 'passive', 'Add proficiency bonus to dispel magic and counterspell', '{"dispel_bonus": "proficiency", "counterspell_bonus": "proficiency"}'),
('abjuration', 14, 'Spell Resistance', 'passive', 'Advantage on spell saves and resistance to spell damage', '{"spell_save_advantage": true, "spell_damage_resistance": true}');

-- CLERIC SUBCLASSES
-- Life Domain
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('life', 1, 'Bonus Proficiency', 'passive', 'Proficiency with heavy armor', '{"armor_proficiency": "heavy"}'),
('life', 1, 'Disciple of Life', 'passive', 'Healing spells restore additional HP', '{"healing_bonus": "2_plus_spell_level"}'),
('life', 2, 'Channel Divinity: Preserve Life', 'action', 'Heal multiple creatures within 30 feet', '{"heal_amount": "cleric_level_times_5", "range": 30, "distribute_healing": true}'),
('life', 6, 'Blessed Healer', 'passive', 'Heal yourself when healing others', '{"self_heal": "2_plus_spell_level"}'),
('life', 8, 'Divine Strike', 'passive', 'Weapon attacks deal extra radiant damage', '{"damage_bonus": "1d8", "damage_type": "radiant"}'),
('life', 17, 'Supreme Healing', 'passive', 'Maximize healing spell results', '{"maximize_healing": true}');

-- War Domain
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('war', 1, 'Bonus Proficiency', 'passive', 'Proficiency with martial weapons and heavy armor', '{"weapon_proficiency": "martial", "armor_proficiency": "heavy"}'),
('war', 1, 'War Priest', 'bonus_action', 'Make weapon attack as bonus action', '{"bonus_weapon_attack": true, "uses_per_long_rest": "wisdom_modifier"}'),
('war', 2, 'Channel Divinity: Guided Strike', 'bonus_action', '+10 bonus to attack roll', '{"attack_bonus": 10}'),
('war', 6, 'Channel Divinity: War God Blessing', 'reaction', 'Grant +10 to ally attack roll', '{"ally_attack_bonus": 10, "range": 30}'),
('war', 8, 'Divine Strike', 'passive', 'Weapon attacks deal extra damage', '{"damage_bonus": "1d8", "damage_type": "weapon"}'),
('war', 17, 'Avatar of Battle', 'passive', 'Resistance to bludgeoning, piercing, slashing from nonmagical weapons', '{"damage_resistance": ["bludgeoning", "piercing", "slashing"], "nonmagical_only": true}');

-- PALADIN SUBCLASSES
-- Oath of Devotion
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('devotion', 3, 'Channel Divinity: Sacred Weapon', 'action', 'Make weapon magical and add Charisma to attack rolls', '{"weapon_magical": true, "attack_bonus": "charisma_modifier", "duration": "1_minute"}'),
('devotion', 3, 'Channel Divinity: Turn the Unholy', 'action', 'Turn fiends and undead', '{"turn_creature_types": ["fiend", "undead"], "range": 30}'),
('devotion', 7, 'Aura of Devotion', 'passive', 'You and allies cannot be charmed', '{"charm_immunity": true, "range": 10}'),
('devotion', 15, 'Purity of Spirit', 'passive', 'Always under protection from evil and good', '{"constant_protection": "evil_and_good"}'),
('devotion', 20, 'Holy Nimbus', 'action', 'Radiate light dealing radiant damage', '{"radiant_damage": "10_to_enemies", "range": 30, "duration": "1_minute"}');

-- Oath of Vengeance
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('vengeance', 3, 'Channel Divinity: Abjure Enemy', 'action', 'Frighten and reduce speed of one creature', '{"frighten_target": true, "speed_reduction": 0.5}'),
('vengeance', 3, 'Channel Divinity: Vow of Enmity', 'bonus_action', 'Gain advantage on attacks against one creature', '{"advantage_vs_target": true, "duration": "1_minute"}'),
('vengeance', 7, 'Relentless Avenger', 'free_action', 'Move after opportunity attack hits', '{"move_after_opportunity_attack": "half_speed"}'),
('vengeance', 15, 'Soul of Vengeance', 'reaction', 'Attack when vowed enemy attacks you', '{"reaction_attack_vs_vowed_enemy": true}'),
('vengeance', 20, 'Avenging Angel', 'action', 'Sprout wings and radiate fear', '{"fly_speed": 60, "frightening_aura": 30, "duration": "1_hour"}');

-- WARLOCK SUBCLASSES
-- Fiend Patron
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('fiend', 1, 'Expanded Spell List', 'passive', 'Additional spells always known', '{"bonus_spells": ["burning_hands", "command", "blindness_deafness", "scorching_ray"]}'),
('fiend', 1, 'Dark Ones Blessing', 'passive', 'Gain temporary HP when you kill a creature', '{"temp_hp": "charisma_modifier_plus_warlock_level", "trigger": "kill_creature"}'),
('fiend', 6, 'Dark Ones Own Luck', 'reaction', 'Add d10 to ability check or saving throw', '{"bonus_die": "d10", "uses_per_short_rest": 1}'),
('fiend', 10, 'Fiendish Resilience', 'action', 'Gain resistance to one damage type', '{"damage_resistance": "choice", "duration": "until_long_rest"}'),
('fiend', 14, 'Hurl Through Hell', 'action', 'Banish creature through lower planes', '{"banish_duration": "1_round", "return_damage": "10d10", "damage_type": "psychic"}');

-- Great Old One Patron
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics) VALUES
('great_old_one', 1, 'Expanded Spell List', 'passive', 'Additional spells always known', '{"bonus_spells": ["dissonant_whispers", "tashas_hideous_laughter", "calm_emotions", "detect_thoughts"]}'),
('great_old_one', 1, 'Telepathic Communication', 'passive', 'Communicate telepathically with creatures', '{"telepathy_range": 30, "language_not_required": true}'),
('great_old_one', 6, 'Entropic Ward', 'reaction', 'Impose disadvantage on attack against you', '{"disadvantage_on_attack": true, "uses_per_short_rest": 1}'),
('great_old_one', 10, 'Thought Shield', 'passive', 'Resistance to psychic damage and reflect damage', '{"psychic_resistance": true, "reflect_damage": true}'),
('great_old_one', 14, 'Create Thrall', 'action', 'Charm humanoid for 24 hours', '{"charm_duration": "24_hours", "creature_type": "humanoid", "uses_per_long_rest": 1}');