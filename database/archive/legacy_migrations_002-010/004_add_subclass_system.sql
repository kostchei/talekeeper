-- Migration: Add comprehensive subclass system
-- This migration adds tables and data for D&D 2024 subclasses

-- Create subclasses table
CREATE TABLE IF NOT EXISTS subclasses (
    id TEXT PRIMARY KEY,
    class_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    flavor_text TEXT,
    selection_level INTEGER DEFAULT 3,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- Create subclass_features table
CREATE TABLE IF NOT EXISTS subclass_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subclass_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    description TEXT,
    mechanics TEXT, -- JSON string describing mechanical effects
    action_type TEXT, -- 'passive', 'action', 'bonus_action', 'reaction', 'resource'
    uses_per_rest INTEGER,
    rest_type TEXT, -- 'short', 'long', 'none'
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subclass_id) REFERENCES subclasses(id),
    UNIQUE(subclass_id, level, feature_name)
);

-- Insert Fighter subclasses
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, flavor_text) VALUES
('champion', 'fighter', 'Champion', 'A master of physical prowess and martial superiority', 'The archetypal Champion focuses on the development of raw physical power honed to deadly perfection.'),
('gladiator', 'fighter', 'Gladiator', 'A crowd-pleasing arena warrior who thrives on spectacle', 'Gladiators are showmen as much as warriors, turning combat into performance art.');

-- Insert Rogue subclasses
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, flavor_text) VALUES
('thief', 'rogue', 'Thief', 'A master of stealth and larceny with fast hands', 'You hone your skills in the larcenous arts, learning tricks to enhance your agility and stealth.'),
('assassin', 'rogue', 'Assassin', 'A deadly killer who strikes from the shadows', 'You focus your training on the grim art of death, becoming a master of poison, disguise, and stealth.');

-- Insert Champion features
INSERT OR IGNORE INTO subclass_features (subclass_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('champion', 3, 'Improved Critical', 'Your weapon attacks score a critical hit on a roll of 19 or 20', '{"critical_range_min": 19}', 'passive', NULL, NULL),
('champion', 7, 'Remarkable Athlete', 'Add half proficiency (round up) to STR, DEX, and CON checks without proficiency', '{"half_prof_physical": true}', 'passive', NULL, NULL),
('champion', 10, 'Additional Fighting Style', 'Choose a second Fighting Style', '{"additional_fighting_style": 1}', 'passive', NULL, NULL),
('champion', 10, 'Heroic Warrior', 'At start of turn, regain 5 + CON mod HP if below half HP', '{"regen_hp": "5+con"}', 'passive', NULL, NULL),
('champion', 15, 'Superior Critical', 'Your weapon attacks score a critical hit on a roll of 18-20', '{"critical_range_min": 18}', 'passive', NULL, NULL),
('champion', 18, 'Survivor', 'At start of turn, regain 10 + CON mod HP if below half HP', '{"regen_hp": "10+con"}', 'passive', NULL, NULL);

-- Insert Gladiator features
INSERT OR IGNORE INTO subclass_features (subclass_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('gladiator', 3, 'Crowd Pleaser', 'When you score a critical hit, gain temp HP equal to your fighter level', '{"on_crit": "temp_hp_level"}', 'passive', NULL, NULL),
('gladiator', 3, 'Performance Fighter', 'Gain proficiency in Performance and Intimidation', '{"skills": ["performance", "intimidation"]}', 'passive', NULL, NULL),
('gladiator', 7, 'Arena Reflexes', 'You have advantage on initiative rolls and can draw/stow two weapons as part of your movement', '{"initiative_advantage": true, "quick_draw": true}', 'passive', NULL, NULL),
('gladiator', 10, 'Signature Move', 'Once per short rest, make a special attack that deals extra damage and can frighten', '{"damage_bonus": "2d6", "save_dc": "8+prof+str", "effect": "frightened"}', 'action', 1, 'short'),
('gladiator', 15, 'Crowd Favorite', 'When below half HP, gain resistance to all damage except psychic', '{"bloodied_resistance": true}', 'passive', NULL, NULL),
('gladiator', 18, 'Champion of the Arena', 'Your Signature Move recharges on a 5-6 on d6 at start of turn', '{"signature_recharge": "5-6"}', 'passive', NULL, NULL);

-- Insert Thief features
INSERT OR IGNORE INTO subclass_features (subclass_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('thief', 3, 'Fast Hands', 'Use thieves tools, Use Object action, or Sleight of Hand as bonus action', '{"bonus_action_options": ["thieves_tools", "use_object", "sleight_of_hand"]}', 'bonus_action', NULL, NULL),
('thief', 3, 'Second-Story Work', 'Climb at normal speed, running jump bonus equals DEX mod', '{"climb_speed": "normal", "jump_bonus": "dex"}', 'passive', NULL, NULL),
('thief', 9, 'Supreme Sneak', 'Advantage on Stealth checks if you move no more than half speed', '{"stealth_advantage_half_speed": true}', 'passive', NULL, NULL),
('thief', 13, 'Use Magic Device', 'Ignore class, race, and level requirements on magic items', '{"ignore_magic_requirements": true}', 'passive', NULL, NULL),
('thief', 17, 'Thief''s Reflexes', 'Take two turns in first round of combat (at initiative and initiative-10)', '{"double_first_turn": true}', 'passive', NULL, NULL);

-- Insert Assassin features
INSERT OR IGNORE INTO subclass_features (subclass_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('assassin', 3, 'Assassinate', 'Advantage on attacks vs creatures that haven''t acted; hits on surprised creatures are crits', '{"advantage_vs_slow": true, "auto_crit_surprised": true}', 'passive', NULL, NULL),
('assassin', 3, 'Assassin''s Tools', 'Gain proficiency with poisoner''s kit and disguise kit', '{"tool_proficiencies": ["poisoners_kit", "disguise_kit"]}', 'passive', NULL, NULL),
('assassin', 9, 'Infiltration Expertise', 'Create false identities with 7 days and 25gp', '{"create_identity": true}', 'passive', NULL, NULL),
('assassin', 13, 'Impostor', 'Perfectly mimic speech, writing, and behavior after 3 hours study', '{"perfect_mimicry": true}', 'passive', NULL, NULL),
('assassin', 17, 'Death Strike', 'When you hit a surprised creature, force CON save or double damage', '{"death_strike_dc": "8+prof+dex", "double_damage_on_fail": true}', 'passive', NULL, NULL);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_subclass_features_lookup ON subclass_features(subclass_id, level);
CREATE INDEX IF NOT EXISTS idx_subclasses_class ON subclasses(class_id);