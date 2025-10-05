-- Barbarian Class Features Seed Data
-- Insert all Barbarian class features into class_features table

-- Level 1 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 1, 'Rage', 'Enter a battle rage for damage resistance and bonuses. +2 damage on Strength attacks, resistance to bludgeoning/piercing/slashing, advantage on Strength checks/saves.', '{"damage_bonus": 2, "resistance": ["bludgeoning", "piercing", "slashing"], "advantage": ["strength_checks", "strength_saves"], "duration": "10_minutes"}', 'bonus_action', 2, 'long'),
('barbarian', 1, 'Unarmored Defense', 'While not wearing armor, AC equals 10 + Dex modifier + Con modifier (can use shield)', '{"ac_formula": "10+dex+con", "requires_no_armor": true, "allows_shield": true}', 'passive', NULL, NULL),
('barbarian', 1, 'Weapon Mastery', 'Gain mastery with 2 weapons of your choice. You can use the mastery property of weapons you have mastery with.', '{"mastery_count": 2, "unlimited_uses": true}', 'passive', NULL, NULL);

-- Level 2 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 2, 'Danger Sense', 'You have advantage on Dexterity saving throws while not incapacitated.', '{"advantage_on": "dex_saves", "condition": "not_incapacitated"}', 'passive', NULL, NULL),
('barbarian', 2, 'Reckless Attack', 'On your first attack of the turn, gain advantage on Strength attack rolls, but enemies have advantage on attacks against you until your next turn.', '{"player_advantage": "strength_attacks", "enemy_advantage": "all_attacks", "duration": "until_next_turn"}', 'free', NULL, NULL);

-- Level 3 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 3, 'Primal Knowledge', 'Choose one skill: Animal Handling, Athletics, Intimidation, Nature, Perception, or Survival. While raging, you can use Strength for Acrobatics, Intimidation, Perception, Stealth, and Survival checks.', '{"bonus_skill": 1, "skill_choices": ["animal_handling", "athletics", "intimidation", "nature", "perception", "survival"], "rage_str_skills": ["acrobatics", "intimidation", "perception", "stealth", "survival"]}', 'passive', NULL, NULL);

-- Level 4 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 4, 'Ability Score Improvement', 'Increase one ability score by 2, or two ability scores by 1 each. You can choose a feat instead.', '{"asi_points": 2, "feat_option": true}', 'passive', NULL, NULL);

-- Level 5 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 5, 'Extra Attack', 'You can attack twice when you take the Attack action on your turn.', '{"attacks": 2}', 'passive', NULL, NULL),
('barbarian', 5, 'Fast Movement', 'Your speed increases by 10 feet while you are not wearing Heavy armor.', '{"speed_bonus": 10, "requires": "no_heavy_armor"}', 'passive', NULL, NULL);

-- Level 6 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 6, 'Subclass Feature', 'Gain a feature from your Primal Path (subclass).', '{"subclass_feature": true}', 'passive', NULL, NULL);

-- Level 7 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 7, 'Feral Instinct', 'You have advantage on Initiative rolls.', '{"advantage_on": "initiative"}', 'passive', NULL, NULL),
('barbarian', 7, 'Instinctive Pounce', 'When you enter a rage, you can move up to half your speed without provoking opportunity attacks.', '{"trigger": "enter_rage", "movement": "half_speed_no_aoo"}', 'passive', NULL, NULL);

-- Level 8 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 8, 'Ability Score Improvement', 'Increase one ability score by 2, or two ability scores by 1 each. You can choose a feat instead.', '{"asi_points": 2, "feat_option": true}', 'passive', NULL, NULL);

-- Level 9 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 9, 'Brutal Strike', 'If you use Reckless Attack, you can forgo advantage on one attack to add +1d10 damage and apply an effect: Forceful Blow (push 15 ft, move toward target) or Hamstring Blow (reduce speed 15 ft until next turn).', '{"requires": "reckless_attack", "damage_bonus": "1d10", "effects": ["forceful", "hamstring"]}', 'special', NULL, NULL);

-- Level 10 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 10, 'Subclass Feature', 'Gain a feature from your Primal Path (subclass).', '{"subclass_feature": true}', 'passive', NULL, NULL);

-- Level 11 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 11, 'Relentless Rage', 'If you drop to 0 hit points while raging, make a DC 10 Constitution saving throw. On success, drop to hit points equal to twice your Barbarian level instead. DC increases by 5 each time until you finish a long rest.', '{"trigger": "drop_to_0_hp", "save": "constitution", "base_dc": 10, "dc_increase": 5, "hp_recovery": "2*level"}', 'triggered', NULL, NULL);

-- Level 12 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 12, 'Ability Score Improvement', 'Increase one ability score by 2, or two ability scores by 1 each. You can choose a feat instead.', '{"asi_points": 2, "feat_option": true}', 'passive', NULL, NULL);

-- Level 13 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 13, 'Improved Brutal Strike', 'Add two new Brutal Strike options: Staggering Blow (target has disadvantage on next save and cannot make opportunity attacks) and Sundering Blow (next attack roll against target gains +5 bonus).', '{"brutal_strike_upgrade": true, "new_effects": ["staggering", "sundering"]}', 'passive', NULL, NULL);

-- Level 14 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 14, 'Subclass Feature', 'Gain a feature from your Primal Path (subclass).', '{"subclass_feature": true}', 'passive', NULL, NULL);

-- Level 15 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 15, 'Persistent Rage', 'When you roll Initiative and have no uses of Rage left, you regain all uses (once per long rest). Rage now lasts for 10 minutes and only ends if you fall unconscious or don heavy armor.', '{"rage_persistent": true, "initiative_recovery": true, "duration": "10_minutes"}', 'passive', NULL, NULL);

-- Level 16 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 16, 'Ability Score Improvement', 'Increase one ability score by 2, or two ability scores by 1 each. You can choose a feat instead.', '{"asi_points": 2, "feat_option": true}', 'passive', NULL, NULL);

-- Level 17 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 17, 'Improved Brutal Strike', 'Brutal Strike damage increases to 2d10, and you can apply two different effects when you use it.', '{"brutal_strike_damage": "2d10", "dual_effects": true}', 'passive', NULL, NULL);

-- Level 18 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 18, 'Indomitable Might', 'If your total for a Strength check or Strength saving throw is less than your Strength score, you can use your Strength score in place of the total.', '{"str_minimum": "ability_score", "applies_to": ["strength_checks", "strength_saves"]}', 'passive', NULL, NULL);

-- Level 19 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 19, 'Epic Boon', 'You gain an Epic Boon feat or another feat of your choice.', '{"feat_choice": "epic_boon", "alternative": "any_feat"}', 'passive', NULL, NULL);

-- Level 20 Features
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 20, 'Primal Champion', 'Your Strength and Constitution scores increase by 4, to a maximum of 25.', '{"ability_increase": {"strength": 4, "constitution": 4}, "new_maximum": 25}', 'passive', NULL, NULL);