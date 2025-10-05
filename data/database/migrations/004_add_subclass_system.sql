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
    mechanics TEXT,
    action_type TEXT,
    uses_per_rest INTEGER,
    rest_type TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subclass_id) REFERENCES subclasses(id),
    UNIQUE(subclass_id, level, feature_name)
);

-- Insert Fighter subclasses
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, flavor_text) VALUES
('champion', 'fighter', 'Champion', 'A master of physical prowess and martial superiority', 'The archetypal Champion focuses on the development of raw physical power honed to deadly perfection.');

-- Insert Rogue subclasses
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, flavor_text) VALUES
('thief', 'rogue', 'Thief', 'A master of stealth and larceny with fast hands', 'You hone your skills in the larcenous arts, learning tricks to enhance your agility and stealth.'),
('assassin', 'rogue', 'Assassin', 'A deadly killer who strikes from the shadows', 'You focus your training on the grim art of death, becoming a master of poison, disguise, and stealth.');

-- Insert Champion features
INSERT OR IGNORE INTO subclass_features (subclass_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('champion', 3, 'Improved Critical', 'Your weapon attacks score a critical hit on a roll of 19 or 20', '{"critical_range_min": 19}', 'passive', NULL, NULL),
('champion', 7, 'Remarkable Athlete', 'Add half proficiency (round up) to STR, DEX, and CON checks without proficiency', '{"half_prof_physical": true}', 'passive', NULL, NULL),
('champion', 10, 'Additional Fighting Style', 'Choose a second Fighting Style', '{"additional_fighting_style": 1}', 'passive', NULL, NULL),
('champion', 10, 'Heroic Warrior', 'Gain Heroic Inspiration on critical hit or reduce creature to 0 HP', '{"gain_inspiration": ["critical_hit", "reduce_to_zero"]}', 'passive', NULL, NULL),
('champion', 15, 'Superior Critical', 'Your weapon attacks score a critical hit on a roll of 18-20', '{"critical_range_min": 18}', 'passive', NULL, NULL),
('champion', 18, 'Survivor', 'At start of turn, regain 5 + CON mod HP if below half HP and at least 1 HP', '{"regen_hp": "5+con", "condition": "below_half_hp"}', 'passive', NULL, NULL);

-- Insert Thief features (D&D 2024)
INSERT OR IGNORE INTO subclass_features (subclass_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('thief', 3, 'Fast Hands', 'As bonus action: Sleight of Hand check with thieves tools OR take Utilize/Magic action', '{"bonus_action_options": ["sleight_of_hand", "utilize", "magic_action"]}', 'bonus_action', NULL, NULL),
('thief', 3, 'Second-Story Work', 'Climb speed equal to speed, use DEX for jump distance', '{"climb_speed": "base_speed", "jump_ability": "dexterity"}', 'passive', NULL, NULL),
('thief', 9, 'Supreme Sneak', 'Cunning Strike option: Stealth Attack (1d6) - maintain Invisible with cover', '{"cunning_strike": "stealth_attack", "cost": "1d6"}', 'passive', NULL, NULL),
('thief', 13, 'Use Magic Device', 'Attune to 4 items, 1d6 roll 6 saves charges, use any scroll with INT', '{"attunement": 4, "charge_save": "1d6_on_6", "scroll_ability": "intelligence"}', 'passive', NULL, NULL),
('thief', 17, 'Thief''s Reflexes', 'Two turns in first round: at initiative and initiative-10', '{"double_first_turn": true, "second_turn": "initiative-10"}', 'passive', NULL, NULL);

-- Insert Assassin features
INSERT OR IGNORE INTO subclass_features (subclass_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('assassin', 3, 'Assassinate', 'Advantage on attacks vs creatures that haven''t acted; hits on surprised creatures are crits', '{"advantage_vs_slow": true, "auto_crit_surprised": true}', 'passive', NULL, NULL),
('assassin', 3, 'Assassin''s Tools', 'Gain proficiency with poisoner''s kit and disguise kit', '{"tool_proficiencies": ["poisoners_kit", "disguise_kit"]}', 'passive', NULL, NULL),
('assassin', 9, 'Infiltration Expertise', 'Create false identities with 7 days and 25gp', '{"create_identity": true}', 'passive', NULL, NULL),
('assassin', 13, 'Impostor', 'Perfectly mimic speech, writing, and behavior after 3 hours study', '{"perfect_mimicry": true}', 'passive', NULL, NULL),
('assassin', 17, 'Death Strike', 'When you hit a surprised creature, force CON save or double damage', '{"death_strike_dc": "8+prof+dex", "double_damage_on_fail": true}', 'passive', NULL, NULL);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_subclass_features_lookup ON subclass_features(subclass_id, level);
CREATE INDEX IF NOT EXISTS idx_subclasses_class ON subclasses(class_id);
