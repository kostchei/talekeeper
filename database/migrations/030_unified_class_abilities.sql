-- Migration 030: Unified Class Abilities System
-- Replaces per-class ability services with unified database-driven architecture
-- Follows the same pattern as the feats system

-- ============================================================
-- TABLE 1: Class Abilities Definition
-- ============================================================
-- Stores ALL class ability definitions for all 11 D&D classes
-- Similar to how 'feats' table stores all feat definitions

CREATE TABLE IF NOT EXISTS class_abilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ability_id TEXT UNIQUE NOT NULL,
    class_name TEXT NOT NULL,
    ability_name TEXT NOT NULL,
    description TEXT,

    level_gained INTEGER NOT NULL,
    subclass_requirement TEXT,

    feature_type TEXT NOT NULL DEFAULT 'action',
    usage_type TEXT NOT NULL DEFAULT 'unlimited',

    uses_formula TEXT,
    scaling_type TEXT DEFAULT 'fixed',

    mechanics TEXT NOT NULL DEFAULT '{}',

    source TEXT DEFAULT 'SRD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_class_abilities_class ON class_abilities(class_name);
CREATE INDEX IF NOT EXISTS idx_class_abilities_level ON class_abilities(level_gained);
CREATE INDEX IF NOT EXISTS idx_class_abilities_id ON class_abilities(ability_id);

-- ============================================================
-- TABLE 2: Character Ability Usage Tracking
-- ============================================================
-- Tracks per-character resource consumption and state
-- Similar to how 'character_features' tracks character feats

CREATE TABLE IF NOT EXISTS character_ability_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    ability_id TEXT NOT NULL,

    current_uses INTEGER NOT NULL DEFAULT 0,
    max_uses INTEGER NOT NULL DEFAULT 0,

    is_active INTEGER DEFAULT 0,
    turns_remaining INTEGER DEFAULT 0,

    last_used TIMESTAMP,
    last_reset TIMESTAMP,

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (ability_id) REFERENCES class_abilities(ability_id),
    UNIQUE(character_id, ability_id)
);

CREATE INDEX IF NOT EXISTS idx_char_ability_usage_char ON character_ability_usage(character_id);
CREATE INDEX IF NOT EXISTS idx_char_ability_usage_ability ON character_ability_usage(ability_id);

-- ============================================================
-- TABLE 3: Ability Scaling Formulas
-- ============================================================
-- Reusable lookup tables for level-based scaling

CREATE TABLE IF NOT EXISTS ability_scaling_formulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    formula_name TEXT UNIQUE NOT NULL,
    description TEXT,
    formula_type TEXT NOT NULL DEFAULT 'lookup',
    formula_data TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_scaling_formulas_name ON ability_scaling_formulas(formula_name);

-- ============================================================
-- SEED DATA: Scaling Formulas
-- ============================================================

INSERT OR IGNORE INTO ability_scaling_formulas (formula_name, description, formula_type, formula_data) VALUES
('rage_uses_by_level', 'Barbarian rage uses progression', 'lookup', '{"1":2,"2":2,"3":3,"4":3,"5":3,"6":4,"7":4,"8":4,"9":4,"10":4,"11":4,"12":5,"13":5,"14":5,"15":5,"16":5,"17":6,"18":6,"19":6,"20":999}'),
('proficiency_bonus', 'Proficiency bonus by level', 'lookup', '{"1":2,"2":2,"3":2,"4":2,"5":3,"6":3,"7":3,"8":3,"9":4,"10":4,"11":4,"12":4,"13":5,"14":5,"15":5,"16":5,"17":6,"18":6,"19":6,"20":6}'),
('sneak_attack_dice', 'Rogue sneak attack damage dice', 'calculation', '{"formula":"1 + ((level - 1) // 2)"}'),
('rage_damage', 'Barbarian rage damage bonus', 'lookup', '{"1":2,"2":2,"3":2,"4":2,"5":2,"6":2,"7":2,"8":2,"9":3,"10":3,"11":3,"12":3,"13":3,"14":3,"15":3,"16":4,"17":4,"18":4,"19":4,"20":4}');

-- ============================================================
-- SEED DATA: Fighter Abilities
-- ============================================================

INSERT OR IGNORE INTO class_abilities (ability_id, class_name, ability_name, description, level_gained, subclass_requirement, feature_type, usage_type, uses_formula, scaling_type, mechanics) VALUES

('second_wind', 'Fighter', 'Second Wind', 'You have a limited well of stamina. On your turn, you can use a Bonus Action to regain HP equal to 1d10 + your Fighter level.', 1, NULL, 'bonus_action', 'short_rest', '1', 'fixed', '{"heal_formula":"1d10 + level","heal_type":"healing","action_cost":"bonus_action","conditions":[]}'),

('action_surge', 'Fighter', 'Action Surge', 'You can push yourself beyond normal limits. On your turn, you can take one additional action.', 2, NULL, 'special', 'short_rest', '1 + (level >= 17)', 'level_based', '{"effect":"grant_extra_action","action_count":1,"duration":"instant","restrictions":["one_extra_attack_max"]}'),

('indomitable', 'Fighter', 'Indomitable', 'You can reroll a saving throw that you fail. If you do so, you must use the new roll.', 9, NULL, 'reaction', 'long_rest', '1 + (level >= 13) + (level >= 17)', 'level_based', '{"effect":"reroll_save","trigger":"failed_save","must_take_new_roll":true}'),

('tactical_mind', 'Fighter', 'Tactical Mind', 'If you fail an ability check, you can expend a use to add your Intelligence modifier to the check, potentially turning it into a success.', 2, NULL, 'special', 'per_encounter', 'proficiency_bonus', 'proficiency_based', '{"effect":"add_int_to_check","trigger":"failed_check","bonus":"intelligence_modifier"}'),

('tactical_shift', 'Fighter', 'Tactical Shift', 'Whenever you activate Second Wind, you can move up to half your Speed without provoking opportunity attacks.', 10, NULL, 'passive', 'permanent', NULL, 'fixed', '{"trigger":"second_wind_used","effect":"move_half_speed","no_opportunity_attacks":true}'),

('champion_improved_critical', 'Fighter', 'Improved Critical', 'Your weapon attacks score a critical hit on a roll of 19 or 20.', 3, 'Champion', 'passive', 'permanent', NULL, 'fixed', '{"critical_range":19}'),

('champion_remarkable_athlete', 'Fighter', 'Remarkable Athlete', 'You can add half your proficiency bonus (round up) to any Strength, Dexterity, or Constitution check you make that doesn''t already use your proficiency bonus.', 7, 'Champion', 'passive', 'permanent', NULL, 'fixed', '{"bonus":"half_proficiency","ability_checks":["strength","dexterity","constitution"],"only_if_not_proficient":true}'),

('champion_additional_fighting_style', 'Fighter', 'Additional Fighting Style', 'You choose a second option from the Fighting Style feature.', 10, 'Champion', 'passive', 'permanent', NULL, 'fixed', '{"effect":"gain_second_fighting_style"}'),

('champion_superior_critical', 'Fighter', 'Superior Critical', 'Your weapon attacks score a critical hit on a roll of 18-20.', 15, 'Champion', 'passive', 'permanent', NULL, 'fixed', '{"critical_range":18}'),

('champion_survivor', 'Fighter', 'Survivor', 'At the start of each of your turns in combat, you regain HP equal to 5 + your Constitution modifier (minimum 1 HP). You don''t gain this benefit if you have 0 HP or if you have more than half your HP left.', 18, 'Champion', 'passive', 'permanent', NULL, 'fixed', '{"heal_formula":"5 + constitution_modifier","trigger":"turn_start","condition":"hp_below_half"}'),

('champion_heroic_warrior', 'Fighter', 'Heroic Warrior', 'If you have fewer than half your HP at the start of your turn, you gain temporary HP equal to your Fighter level.', 18, 'Champion', 'passive', 'permanent', NULL, 'fixed', '{"temp_hp_formula":"level","trigger":"turn_start","condition":"hp_below_half"}');

-- ============================================================
-- SEED DATA: Barbarian Abilities
-- ============================================================

INSERT OR IGNORE INTO class_abilities (ability_id, class_name, ability_name, description, level_gained, subclass_requirement, feature_type, usage_type, uses_formula, scaling_type, mechanics) VALUES

('rage', 'Barbarian', 'Rage', 'In battle, you fight with primal ferocity. On your turn, you can enter a rage as a Bonus Action. While raging, you gain resistance to physical damage, bonus damage on melee attacks, and advantage on Strength checks and saves.', 1, NULL, 'bonus_action', 'long_rest', 'rage_uses_by_level', 'level_based', '{"damage_bonus_formula":"rage_damage","resistance_types":["bludgeoning","piercing","slashing"],"advantage_on":["strength_checks","strength_saves"],"duration_turns":10,"ends_if":["no_attack_two_turns","unconscious"],"restrictions":["no_heavy_armor"]}'),

('unarmored_defense_barbarian', 'Barbarian', 'Unarmored Defense', 'While not wearing armor, your AC equals 10 + Dexterity modifier + Constitution modifier.', 1, NULL, 'passive', 'permanent', NULL, 'fixed', '{"ac_formula":"10 + dexterity_modifier + constitution_modifier","requires":"no_armor"}'),

('reckless_attack', 'Barbarian', 'Reckless Attack', 'When you make your first attack on your turn using Strength, you can decide to attack recklessly, giving you advantage on melee attack rolls using Strength during this turn, but attack rolls against you have advantage until your next turn.', 2, NULL, 'special', 'unlimited', NULL, 'fixed', '{"trigger":"first_attack","benefit":"advantage_on_attacks","drawback":"enemies_have_advantage","duration":"until_next_turn"}'),

('danger_sense', 'Barbarian', 'Danger Sense', 'You have advantage on Dexterity saving throws against effects you can see while not Blinded, Deafened, or Incapacitated.', 2, NULL, 'passive', 'permanent', NULL, 'fixed', '{"advantage_on":"dexterity_saves","conditions":["can_see","not_blinded","not_deafened","not_incapacitated"]}'),

('primal_path', 'Barbarian', 'Primal Path', 'You choose a path that shapes the nature of your rage.', 3, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"choose_subclass","options":["Berserker","Totem_Warrior","Wild_Soul"]}'),

('fast_movement', 'Barbarian', 'Fast Movement', 'Your speed increases by 10 feet while you aren''t wearing heavy armor.', 5, NULL, 'passive', 'permanent', NULL, 'fixed', '{"speed_bonus":10,"requires":"no_heavy_armor"}'),

('feral_instinct', 'Barbarian', 'Feral Instinct', 'You have advantage on Initiative rolls.', 7, NULL, 'passive', 'permanent', NULL, 'fixed', '{"advantage_on":"initiative"}'),

('instinctive_pounce', 'Barbarian', 'Instinctive Pounce', 'As part of the Bonus Action you take to enter your rage, you can move up to half your speed.', 7, NULL, 'passive', 'permanent', NULL, 'fixed', '{"trigger":"enter_rage","effect":"move_half_speed"}'),

('brutal_strike', 'Barbarian', 'Brutal Strike', 'If you use Reckless Attack, you can forgo advantage on the attack to make it a Brutal Strike. Add one extra damage die to the attack''s damage. You can use this a number of times equal to your proficiency bonus per Long Rest.', 9, NULL, 'special', 'long_rest', 'proficiency_bonus', 'proficiency_based', '{"trigger":"reckless_attack","effect":"extra_damage_die","options":["forceful_blow","hamstring_blow"],"requires":"forgo_advantage"}'),

('relentless_rage', 'Barbarian', 'Relentless Rage', 'If you drop to 0 HP while raging and don''t die outright, you can make a DC 10 Constitution save. If you succeed, you drop to 1 HP instead. Each time you use this after the first, the DC increases by 5, resetting after a Short or Long Rest.', 11, NULL, 'reaction', 'encounter', NULL, 'fixed', '{"trigger":"drop_to_0_hp","save":"constitution","dc_base":10,"dc_increment":5,"result":"stay_at_1_hp"}'),

('persistent_rage', 'Barbarian', 'Persistent Rage', 'Your rage is so fierce that it ends early only if you fall Unconscious or you choose to end it.', 15, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"rage_no_timeout","ends_only_if":["unconscious","voluntary"]}'),

('indomitable_might', 'Barbarian', 'Indomitable Might', 'If your total for a Strength check is less than your Strength score, you can use that score in place of the total.', 18, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"minimum_strength_check","minimum":"strength_score"}'),

('primal_champion', 'Barbarian', 'Primal Champion', 'Your Strength and Constitution scores increase by 4. Your maximum for those scores is now 24.', 20, NULL, 'passive', 'permanent', NULL, 'fixed', '{"ability_increase":{"strength":4,"constitution":4},"new_maximum":24}'),

('frenzy', 'Barbarian', 'Frenzy', 'You can go into a frenzy when you rage. If you do so, for the duration of your rage you can make a single melee weapon attack as a Bonus Action on each of your turns after this one.', 3, 'Berserker', 'bonus_action', 'per_rage', NULL, 'fixed', '{"trigger":"enter_rage","effect":"bonus_action_attack","duration":"rage"}'),

('mindless_rage', 'Barbarian', 'Mindless Rage', 'You can''t be Charmed or Frightened while raging. If you are Charmed or Frightened when you enter your rage, the effect is suspended for the duration of the rage.', 6, 'Berserker', 'passive', 'permanent', NULL, 'fixed', '{"immunity":["charmed","frightened"],"only_while_raging":true}'),

('intimidating_presence', 'Barbarian', 'Intimidating Presence', 'You can use your action to frighten someone with your menacing presence. Target one creature within 30 feet that can see or hear you. Target must succeed Wisdom save (DC 8 + proficiency + Charisma) or be Frightened until end of your next turn.', 10, 'Berserker', 'action', 'short_rest', '1', 'fixed', '{"action_cost":"action","range":30,"save":"wisdom","dc_formula":"8 + proficiency_bonus + charisma_modifier","effect":"frightened","duration":"end_of_next_turn"}'),

('retaliation', 'Barbarian', 'Retaliation', 'When you take damage from a creature that is within 5 feet of you, you can use your reaction to make a melee weapon attack against that creature.', 14, 'Berserker', 'reaction', 'unlimited', NULL, 'fixed', '{"trigger":"take_damage","range":5,"effect":"melee_attack"}');

-- ============================================================
-- SEED DATA: Rogue Abilities
-- ============================================================

INSERT OR IGNORE INTO class_abilities (ability_id, class_name, ability_name, description, level_gained, subclass_requirement, feature_type, usage_type, uses_formula, scaling_type, mechanics) VALUES

('sneak_attack', 'Rogue', 'Sneak Attack', 'You know how to strike subtly and exploit a foe''s distraction. Once per turn, you can deal extra damage to one creature you hit with a finesse or ranged weapon if you have advantage or an ally is within 5 feet of the target.', 1, NULL, 'passive', 'unlimited', NULL, 'fixed', '{"damage_dice":"d6","dice_count_formula":"sneak_attack_dice","damage_type":"weapon","requirements":["finesse_or_ranged","advantage_or_ally_nearby"],"frequency":"once_per_turn"}'),

('thieves_cant', 'Rogue', 'Thieves'' Cant', 'You know thieves'' cant, a secret mix of dialect, jargon, and code.', 1, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"secret_language"}'),

('cunning_action', 'Rogue', 'Cunning Action', 'You can take a Bonus Action to take the Dash, Disengage, or Hide action.', 2, NULL, 'bonus_action', 'unlimited', NULL, 'fixed', '{"options":["dash","disengage","hide"],"action_cost":"bonus_action"}'),

('steady_aim', 'Rogue', 'Steady Aim', 'As a Bonus Action, you give yourself advantage on your next attack roll on the current turn. You can use this only if you haven''t moved during this turn, and after you use it, your speed is 0 until the end of the current turn.', 3, NULL, 'bonus_action', 'unlimited', NULL, 'fixed', '{"effect":"advantage_next_attack","requires":"no_movement","speed_after":0}'),

('uncanny_dodge', 'Rogue', 'Uncanny Dodge', 'When an attacker you can see hits you with an attack, you can use your Reaction to halve the attack''s damage against you.', 5, NULL, 'reaction', 'per_turn', NULL, 'fixed', '{"trigger":"hit_by_attack","effect":"halve_damage","requires":"can_see_attacker"}'),

('evasion', 'Rogue', 'Evasion', 'When you are subjected to an effect that allows a Dexterity save to take only half damage, you instead take no damage on a success and only half damage on a failure.', 7, NULL, 'passive', 'permanent', NULL, 'fixed', '{"trigger":"dexterity_save","success":"no_damage","failure":"half_damage"}'),

('reliable_talent', 'Rogue', 'Reliable Talent', 'Whenever you make an ability check that uses your proficiency bonus, treat a d20 roll of 9 or lower as a 10.', 11, NULL, 'passive', 'permanent', NULL, 'fixed', '{"minimum_roll":10,"only_if_proficient":true}'),

('blindsense', 'Rogue', 'Blindsense', 'If you can hear, you are aware of the location of any hidden or invisible creature within 10 feet of you.', 14, NULL, 'passive', 'permanent', NULL, 'fixed', '{"range":10,"detects":["hidden","invisible"],"requires":"can_hear"}'),

('slippery_mind', 'Rogue', 'Slippery Mind', 'You gain proficiency in Wisdom saving throws.', 15, NULL, 'passive', 'permanent', NULL, 'fixed', '{"proficiency":"wisdom_saves"}'),

('elusive', 'Rogue', 'Elusive', 'No attack roll has advantage against you while you aren''t Incapacitated.', 18, NULL, 'passive', 'permanent', NULL, 'fixed', '{"effect":"no_advantage_against","requires":"not_incapacitated"}'),

('stroke_of_luck', 'Rogue', 'Stroke of Luck', 'If your attack misses a target within range, you can turn the miss into a hit. Alternatively, if you fail an ability check, you can treat the d20 roll as a 20.', 20, NULL, 'special', 'long_rest', '1', 'fixed', '{"effect":"auto_hit_or_auto_succeed","uses":"once_per_long_rest"}');

-- ============================================================
-- Migration Complete
-- ============================================================
