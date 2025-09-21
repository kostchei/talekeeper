-- Comprehensive Class Feature System Migration
-- Supports all 11 D&D classes and their subclasses with scalable architecture

-- Main class features progression table
CREATE TABLE IF NOT EXISTS class_features_progression (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    feature_type TEXT NOT NULL, -- 'passive', 'action', 'bonus_action', 'reaction', 'resource'
    description TEXT,
    mechanics JSON, -- JSON object with mechanical effects
    prerequisites JSON, -- JSON object with prerequisites
    UNIQUE(class_id, level, feature_name),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- Subclass features progression table
CREATE TABLE IF NOT EXISTS subclass_features_progression (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subclass_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    feature_type TEXT NOT NULL,
    description TEXT,
    mechanics JSON,
    prerequisites JSON,
    UNIQUE(subclass_id, level, feature_name),
    FOREIGN KEY (subclass_id) REFERENCES subclasses(id)
);

-- Character feature instances (tracks what features a character has)
CREATE TABLE IF NOT EXISTS character_feature_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    feature_source TEXT NOT NULL, -- 'class', 'subclass', 'feat', 'item', 'other'
    feature_id INTEGER, -- References class_features_progression or subclass_features_progression
    feature_name TEXT NOT NULL,
    level_gained INTEGER NOT NULL,
    current_uses INTEGER DEFAULT 0,
    max_uses INTEGER DEFAULT 0,
    recharge_type TEXT, -- 'short_rest', 'long_rest', 'dawn', 'permanent'
    configuration JSON, -- Character-specific configuration (e.g., chosen fighting style, expertise skills)
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Insert D&D 2024 class features for all classes
-- BARBARIAN
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('barbarian', 1, 'Rage', 'bonus_action', 'Enter a battle fury for combat bonuses', '{"damage_bonus": 2, "uses_per_long_rest": 2, "duration_rounds": 10, "resistance": ["bludgeoning", "piercing", "slashing"]}'),
('barbarian', 1, 'Unarmored Defense', 'passive', 'AC = 10 + Dex + Con when not wearing armor', '{"ac_calculation": "10_plus_dex_plus_con"}'),
('barbarian', 2, 'Reckless Attack', 'free_action', 'Gain advantage on attacks but enemies have advantage against you', '{"grants_advantage": true, "grants_advantage_to_enemies": true}'),
('barbarian', 2, 'Danger Sense', 'passive', 'Advantage on Dex saves against effects you can see', '{"dex_save_advantage": true}'),
('barbarian', 3, 'Primal Path', 'passive', 'Choose your barbarian subclass', '{"subclass_selection": true}'),
('barbarian', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('barbarian', 5, 'Extra Attack', 'passive', 'Attack twice when you take the Attack action', '{"extra_attacks": 1}'),
('barbarian', 5, 'Fast Movement', 'passive', 'Speed increases by 10 feet while not wearing heavy armor', '{"speed_bonus": 10}'),
('barbarian', 7, 'Feral Instinct', 'passive', 'Advantage on initiative rolls', '{"initiative_advantage": true}'),
('barbarian', 9, 'Brutal Critical', 'passive', 'Roll one additional damage die on critical hits', '{"crit_extra_dice": 1}'),
('barbarian', 11, 'Relentless Rage', 'passive', 'Keep fighting when reduced to 0 HP while raging', '{"death_save_dc": 10}'),
('barbarian', 13, 'Brutal Critical', 'passive', 'Roll two additional damage dice on critical hits', '{"crit_extra_dice": 2}'),
('barbarian', 15, 'Persistent Rage', 'passive', 'Rage only ends early if you fall unconscious', '{"rage_persistent": true}'),
('barbarian', 17, 'Brutal Critical', 'passive', 'Roll three additional damage dice on critical hits', '{"crit_extra_dice": 3}'),
('barbarian', 18, 'Indomitable Might', 'passive', 'Minimum result on Strength checks equals Strength score', '{"str_check_minimum": "strength_score"}'),
('barbarian', 20, 'Primal Champion', 'passive', '+4 to Strength and Constitution (max 24)', '{"str_bonus": 4, "con_bonus": 4, "ability_max": 24}');

-- FIGHTER
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('fighter', 1, 'Fighting Style', 'passive', 'Choose a combat specialization', '{"choice": ["defense", "dueling", "great_weapon_fighting", "archery", "protection", "two_weapon_fighting"]}'),
('fighter', 1, 'Second Wind', 'bonus_action', 'Regain 1d10 + level HP', '{"healing": "1d10+level", "uses_per_short_rest": 1}'),
('fighter', 2, 'Action Surge', 'free_action', 'Take an additional action on your turn', '{"uses_per_short_rest": 1, "extra_actions": 1}'),
('fighter', 3, 'Martial Archetype', 'passive', 'Choose your fighter subclass', '{"subclass_selection": true}'),
('fighter', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('fighter', 5, 'Extra Attack', 'passive', 'Attack twice when you take the Attack action', '{"extra_attacks": 1}'),
('fighter', 6, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('fighter', 8, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('fighter', 9, 'Indomitable', 'reaction', 'Reroll a failed saving throw', '{"uses_per_long_rest": 1}'),
('fighter', 11, 'Extra Attack', 'passive', 'Attack three times when you take the Attack action', '{"extra_attacks": 2}'),
('fighter', 12, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('fighter', 13, 'Indomitable', 'reaction', 'Reroll a failed saving throw', '{"uses_per_long_rest": 2}'),
('fighter', 14, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('fighter', 16, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('fighter', 17, 'Action Surge', 'free_action', 'Take an additional action on your turn', '{"uses_per_short_rest": 2, "extra_actions": 1}'),
('fighter', 17, 'Indomitable', 'reaction', 'Reroll a failed saving throw', '{"uses_per_long_rest": 3}'),
('fighter', 19, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('fighter', 20, 'Extra Attack', 'passive', 'Attack four times when you take the Attack action', '{"extra_attacks": 3}');

-- ROGUE
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('rogue', 1, 'Expertise', 'passive', 'Double proficiency bonus on two skills', '{"expertise_count": 2}'),
('rogue', 1, 'Sneak Attack', 'passive', 'Deal extra damage when you have advantage', '{"damage_dice": 1, "damage_type": "d6"}'),
('rogue', 1, 'Thieves Cant', 'passive', 'Secret language of rogues and thieves', '{"language": "thieves_cant"}'),
('rogue', 2, 'Cunning Action', 'bonus_action', 'Dash, Disengage, or Hide as a bonus action', '{"bonus_actions": ["dash", "disengage", "hide"]}'),
('rogue', 3, 'Roguish Archetype', 'passive', 'Choose your rogue subclass', '{"subclass_selection": true}'),
('rogue', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('rogue', 5, 'Uncanny Dodge', 'reaction', 'Half damage from one attack you can see', '{"damage_reduction": 0.5}'),
('rogue', 6, 'Expertise', 'passive', 'Double proficiency bonus on two more skills', '{"expertise_count": 4}'),
('rogue', 7, 'Evasion', 'passive', 'Take no damage on successful Dex saves', '{"dex_save_success_no_damage": true}'),
('rogue', 8, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('rogue', 10, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('rogue', 11, 'Reliable Talent', 'passive', 'Minimum of 10 on ability checks you are proficient in', '{"ability_check_minimum": 10}'),
('rogue', 12, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('rogue', 14, 'Blindsense', 'passive', 'Detect hidden creatures within 10 feet', '{"blindsense_range": 10}'),
('rogue', 15, 'Slippery Mind', 'passive', 'Proficiency in Wisdom saving throws', '{"save_proficiency": "wisdom"}'),
('rogue', 16, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('rogue', 18, 'Elusive', 'passive', 'No attack has advantage against you unless incapacitated', '{"no_advantage": true}'),
('rogue', 19, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('rogue', 20, 'Stroke of Luck', 'free_action', 'Turn a miss into a hit or make an attack a critical hit', '{"uses_per_short_rest": 1}');

-- WIZARD
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('wizard', 1, 'Spellcasting', 'passive', 'Cast wizard spells using Intelligence', '{"spell_slots": [2, 0, 0, 0, 0, 0, 0, 0, 0], "cantrips_known": 3}'),
('wizard', 1, 'Arcane Recovery', 'short_rest', 'Recover spell slots on a short rest', '{"slot_levels_recovered": "wizard_level/2"}'),
('wizard', 2, 'Arcane Tradition', 'passive', 'Choose your wizard subclass', '{"subclass_selection": true}'),
('wizard', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('wizard', 8, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('wizard', 12, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('wizard', 16, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('wizard', 18, 'Spell Mastery', 'passive', 'Cast certain spells without using spell slots', '{"free_spells": 2}'),
('wizard', 19, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('wizard', 20, 'Signature Spells', 'passive', 'Cast two 3rd-level spells without using slots', '{"signature_spells": 2}');

-- CLERIC
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('cleric', 1, 'Spellcasting', 'passive', 'Cast cleric spells using Wisdom', '{"spell_slots": [2, 0, 0, 0, 0, 0, 0, 0, 0], "cantrips_known": 3}'),
('cleric', 1, 'Divine Domain', 'passive', 'Choose your cleric subclass', '{"subclass_selection": true}'),
('cleric', 2, 'Channel Divinity', 'action', 'Channel divine energy for powerful effects', '{"uses_per_short_rest": 1}'),
('cleric', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('cleric', 5, 'Destroy Undead', 'passive', 'Destroy undead with Turn Undead', '{"destroy_undead_cr": 0.5}'),
('cleric', 6, 'Channel Divinity', 'action', 'Channel divine energy for powerful effects', '{"uses_per_short_rest": 2}'),
('cleric', 8, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('cleric', 8, 'Destroy Undead', 'passive', 'Destroy undead with Turn Undead', '{"destroy_undead_cr": 1}'),
('cleric', 10, 'Divine Intervention', 'action', 'Request aid from your deity', '{"success_chance": "level_percent"}'),
('cleric', 11, 'Destroy Undead', 'passive', 'Destroy undead with Turn Undead', '{"destroy_undead_cr": 2}'),
('cleric', 12, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('cleric', 14, 'Destroy Undead', 'passive', 'Destroy undead with Turn Undead', '{"destroy_undead_cr": 3}'),
('cleric', 16, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('cleric', 17, 'Destroy Undead', 'passive', 'Destroy undead with Turn Undead', '{"destroy_undead_cr": 4}'),
('cleric', 18, 'Channel Divinity', 'action', 'Channel divine energy for powerful effects', '{"uses_per_short_rest": 3}'),
('cleric', 19, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('cleric', 20, 'Divine Intervention', 'action', 'Request aid from your deity', '{"success_chance": "automatic"}');

-- RANGER
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('ranger', 1, 'Favored Enemy', 'passive', 'Choose a creature type to specialize against', '{"choice": ["aberrations", "beasts", "celestials", "constructs", "dragons", "elementals", "fey", "fiends", "giants", "monstrosities", "oozes", "plants", "undead"]}'),
('ranger', 1, 'Natural Explorer', 'passive', 'Choose a favored terrain', '{"choice": ["arctic", "coast", "desert", "forest", "grassland", "mountain", "swamp", "underdark"]}'),
('ranger', 2, 'Fighting Style', 'passive', 'Choose a combat specialization', '{"choice": ["archery", "defense", "dueling", "two_weapon_fighting"]}'),
('ranger', 2, 'Spellcasting', 'passive', 'Cast ranger spells using Wisdom', '{"spell_slots": [2, 0, 0, 0, 0], "spells_known": 2}'),
('ranger', 3, 'Ranger Archetype', 'passive', 'Choose your ranger subclass', '{"subclass_selection": true}'),
('ranger', 3, 'Primeval Awareness', 'action', 'Sense certain creature types within 1 mile', '{"uses_per_long_rest": 1}'),
('ranger', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('ranger', 5, 'Extra Attack', 'passive', 'Attack twice when you take the Attack action', '{"extra_attacks": 1}'),
('ranger', 6, 'Favored Enemy', 'passive', 'Choose an additional creature type', '{"additional_favored_enemy": true}'),
('ranger', 6, 'Natural Explorer', 'passive', 'Choose an additional favored terrain', '{"additional_favored_terrain": true}'),
('ranger', 8, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('ranger', 8, 'Land Stride', 'passive', 'Move through difficult terrain without penalty', '{"difficult_terrain_ignore": true}'),
('ranger', 10, 'Natural Explorer', 'passive', 'Choose an additional favored terrain', '{"additional_favored_terrain": true}'),
('ranger', 10, 'Hide in Plain Sight', 'action', 'Become invisible when hiding', '{"invisibility_when_hiding": true}'),
('ranger', 12, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('ranger', 14, 'Favored Enemy', 'passive', 'Choose an additional creature type', '{"additional_favored_enemy": true}'),
('ranger', 14, 'Vanish', 'action', 'Hide as a bonus action', '{"hide_bonus_action": true}'),
('ranger', 16, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('ranger', 18, 'Feral Senses', 'passive', 'Detect invisible creatures within 30 feet', '{"detect_invisible": 30}'),
('ranger', 19, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('ranger', 20, 'Foe Slayer', 'passive', 'Add Wisdom modifier to damage against favored enemies', '{"favored_enemy_damage_bonus": "wisdom_mod"}');

-- PALADIN
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('paladin', 1, 'Divine Sense', 'action', 'Detect celestials, fiends, and undead', '{"uses_per_long_rest": "1+cha_mod", "range": 60}'),
('paladin', 1, 'Lay on Hands', 'action', 'Heal with divine power', '{"healing_pool": "level*5", "disease_cure": true}'),
('paladin', 2, 'Fighting Style', 'passive', 'Choose a combat specialization', '{"choice": ["defense", "dueling", "great_weapon_fighting", "protection"]}'),
('paladin', 2, 'Spellcasting', 'passive', 'Cast paladin spells using Charisma', '{"spell_slots": [2, 0, 0, 0, 0], "spells_known": 2}'),
('paladin', 2, 'Divine Smite', 'special', 'Expend spell slots for extra damage', '{"damage_per_slot": "2d8", "extra_vs_undead_fiend": "1d8"}'),
('paladin', 3, 'Divine Health', 'passive', 'Immunity to disease', '{"disease_immunity": true}'),
('paladin', 3, 'Sacred Oath', 'passive', 'Choose your paladin subclass', '{"subclass_selection": true}'),
('paladin', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('paladin', 5, 'Extra Attack', 'passive', 'Attack twice when you take the Attack action', '{"extra_attacks": 1}'),
('paladin', 6, 'Aura of Protection', 'passive', 'Add Charisma modifier to saving throws within 10 feet', '{"save_bonus": "cha_mod", "range": 10}'),
('paladin', 8, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('paladin', 10, 'Aura of Courage', 'passive', 'Immunity to fear and allies cannot be frightened', '{"fear_immunity": true, "ally_fear_immunity": true, "range": 10}'),
('paladin', 11, 'Improved Divine Smite', 'passive', 'All weapon attacks deal extra radiant damage', '{"radiant_damage": "1d8"}'),
('paladin', 12, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('paladin', 14, 'Cleansing Touch', 'action', 'End spells on yourself or others', '{"uses_per_long_rest": "cha_mod"}'),
('paladin', 16, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('paladin', 18, 'Aura Improvements', 'passive', 'Aura range increases to 30 feet', '{"aura_range": 30}'),
('paladin', 19, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('paladin', 20, 'Sacred Oath Feature', 'passive', 'Capstone ability from your Sacred Oath', '{"subclass_capstone": true}');

-- SORCERER
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('sorcerer', 1, 'Spellcasting', 'passive', 'Cast sorcerer spells using Charisma', '{"spell_slots": [2, 0, 0, 0, 0, 0, 0, 0, 0], "cantrips_known": 4, "spells_known": 2}'),
('sorcerer', 1, 'Sorcerous Origin', 'passive', 'Choose your sorcerer subclass', '{"subclass_selection": true}'),
('sorcerer', 2, 'Font of Magic', 'passive', 'Gain sorcery points equal to sorcerer level', '{"sorcery_points": "level"}'),
('sorcerer', 3, 'Metamagic', 'passive', 'Learn to alter spells with sorcery points', '{"metamagic_options": 2, "choice": ["careful", "distant", "empowered", "extended", "heightened", "quickened", "subtle", "twinned"]}'),
('sorcerer', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('sorcerer', 8, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('sorcerer', 10, 'Metamagic', 'passive', 'Learn an additional metamagic option', '{"metamagic_options": 3}'),
('sorcerer', 12, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('sorcerer', 16, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('sorcerer', 17, 'Metamagic', 'passive', 'Learn an additional metamagic option', '{"metamagic_options": 4}'),
('sorcerer', 19, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('sorcerer', 20, 'Sorcerous Restoration', 'short_rest', 'Regain 4 sorcery points on short rest', '{"sorcery_point_recovery": 4}');

-- WARLOCK
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('warlock', 1, 'Otherworldly Patron', 'passive', 'Choose your warlock subclass', '{"subclass_selection": true}'),
('warlock', 1, 'Pact Magic', 'passive', 'Cast warlock spells using Charisma', '{"spell_slots": 1, "slot_level": 1, "cantrips_known": 2, "spells_known": 2}'),
('warlock', 2, 'Eldritch Invocations', 'passive', 'Learn magical invocations', '{"invocations_known": 2}'),
('warlock', 3, 'Pact Boon', 'passive', 'Choose a supernatural gift from your patron', '{"choice": ["pact_of_the_blade", "pact_of_the_chain", "pact_of_the_tome"]}'),
('warlock', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('warlock', 5, 'Eldritch Invocations', 'passive', 'Learn an additional invocation', '{"invocations_known": 3}'),
('warlock', 6, 'Otherworldly Patron Feature', 'passive', 'Gain a feature from your patron', '{"subclass_feature": true}'),
('warlock', 7, 'Eldritch Invocations', 'passive', 'Learn an additional invocation', '{"invocations_known": 4}'),
('warlock', 8, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('warlock', 9, 'Eldritch Invocations', 'passive', 'Learn an additional invocation', '{"invocations_known": 5}'),
('warlock', 10, 'Otherworldly Patron Feature', 'passive', 'Gain a feature from your patron', '{"subclass_feature": true}'),
('warlock', 11, 'Mystic Arcanum', 'passive', 'Learn a 6th-level spell', '{"mystic_arcanum_6": true}'),
('warlock', 12, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('warlock', 12, 'Eldritch Invocations', 'passive', 'Learn an additional invocation', '{"invocations_known": 6}'),
('warlock', 13, 'Mystic Arcanum', 'passive', 'Learn a 7th-level spell', '{"mystic_arcanum_7": true}'),
('warlock', 14, 'Otherworldly Patron Feature', 'passive', 'Gain a feature from your patron', '{"subclass_feature": true}'),
('warlock', 15, 'Mystic Arcanum', 'passive', 'Learn an 8th-level spell', '{"mystic_arcanum_8": true}'),
('warlock', 15, 'Eldritch Invocations', 'passive', 'Learn an additional invocation', '{"invocations_known": 7}'),
('warlock', 16, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('warlock', 17, 'Mystic Arcanum', 'passive', 'Learn a 9th-level spell', '{"mystic_arcanum_9": true}'),
('warlock', 18, 'Eldritch Invocations', 'passive', 'Learn an additional invocation', '{"invocations_known": 8}'),
('warlock', 19, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('warlock', 20, 'Eldritch Master', 'long_rest', 'Regain all expended spell slots once per long rest', '{"spell_slot_recovery": "all"}');

-- BARD
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('bard', 1, 'Spellcasting', 'passive', 'Cast bard spells using Charisma', '{"spell_slots": [2, 0, 0, 0, 0, 0, 0, 0, 0], "cantrips_known": 2, "spells_known": 4}'),
('bard', 1, 'Bardic Inspiration', 'bonus_action', 'Inspire allies with bonus dice', '{"uses_per_short_rest": "cha_mod", "die_type": "d6"}'),
('bard', 2, 'Jack of All Trades', 'passive', 'Add half proficiency to non-proficient checks', '{"half_proficiency": true}'),
('bard', 2, 'Song of Rest', 'passive', 'Allies regain extra HP during short rests', '{"short_rest_bonus": "d6"}'),
('bard', 3, 'Bard College', 'passive', 'Choose your bard subclass', '{"subclass_selection": true}'),
('bard', 3, 'Expertise', 'passive', 'Double proficiency bonus on two skills', '{"expertise_count": 2}'),
('bard', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('bard', 5, 'Bardic Inspiration', 'bonus_action', 'Inspiration die becomes d8', '{"die_type": "d8"}'),
('bard', 5, 'Font of Inspiration', 'short_rest', 'Regain Bardic Inspiration on short rest', '{"short_rest_recovery": true}'),
('bard', 6, 'Countercharm', 'action', 'Grant advantage against charm and fear', '{"charm_fear_advantage": true}'),
('bard', 6, 'Bard College Feature', 'passive', 'Gain a feature from your college', '{"subclass_feature": true}'),
('bard', 8, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('bard', 10, 'Bardic Inspiration', 'bonus_action', 'Inspiration die becomes d10', '{"die_type": "d10"}'),
('bard', 10, 'Magical Secrets', 'passive', 'Learn spells from any class', '{"additional_spells": 2}'),
('bard', 10, 'Expertise', 'passive', 'Double proficiency bonus on two more skills', '{"expertise_count": 4}'),
('bard', 12, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('bard', 14, 'Bard College Feature', 'passive', 'Gain a feature from your college', '{"subclass_feature": true}'),
('bard', 14, 'Magical Secrets', 'passive', 'Learn additional spells from any class', '{"additional_spells": 2}'),
('bard', 15, 'Bardic Inspiration', 'bonus_action', 'Inspiration die becomes d12', '{"die_type": "d12"}'),
('bard', 16, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('bard', 18, 'Magical Secrets', 'passive', 'Learn additional spells from any class', '{"additional_spells": 2}'),
('bard', 19, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('bard', 20, 'Superior Inspiration', 'passive', 'Regain Bardic Inspiration when you roll initiative', '{"initiative_recovery": true}');

-- DRUID
INSERT OR REPLACE INTO class_features_progression (class_id, level, feature_name, feature_type, description, mechanics) VALUES
('druid', 1, 'Druidcraft', 'cantrip', 'Know the Druidcraft cantrip', '{"cantrip": "druidcraft"}'),
('druid', 1, 'Spellcasting', 'passive', 'Cast druid spells using Wisdom', '{"spell_slots": [2, 0, 0, 0, 0, 0, 0, 0, 0], "cantrips_known": 2}'),
('druid', 2, 'Wild Shape', 'action', 'Transform into a beast', '{"uses_per_short_rest": 2, "max_cr": 0.25, "restrictions": ["no_flying", "no_swimming"]}'),
('druid', 2, 'Druid Circle', 'passive', 'Choose your druid subclass', '{"subclass_selection": true}'),
('druid', 4, 'Wild Shape Improvement', 'passive', 'Can swim and transform into CR 1/2 beasts', '{"max_cr": 0.5, "swimming_allowed": true}'),
('druid', 4, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('druid', 8, 'Wild Shape Improvement', 'passive', 'Can fly and transform into CR 1 beasts', '{"max_cr": 1, "flying_allowed": true}'),
('druid', 8, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('druid', 12, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('druid', 16, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('druid', 18, 'Timeless Body', 'passive', 'Age at 1/10th normal rate', '{"aging_resistance": true}'),
('druid', 18, 'Beast Spells', 'passive', 'Cast spells while in Wild Shape', '{"wildshape_spellcasting": true}'),
('druid', 19, 'Ability Score Improvement', 'passive', 'Increase ability scores or take a feat', '{"asi_or_feat": true}'),
('druid', 20, 'Archdruid', 'passive', 'Unlimited Wild Shape uses', '{"unlimited_wildshape": true, "ignore_verbal_somatic": true}');


-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_class_features_class_level ON class_features_progression(class_id, level);
CREATE INDEX IF NOT EXISTS idx_subclass_features_subclass_level ON subclass_features_progression(subclass_id, level);
CREATE INDEX IF NOT EXISTS idx_character_features_character ON character_feature_instances(character_id);
CREATE INDEX IF NOT EXISTS idx_character_features_active ON character_feature_instances(character_id, active);