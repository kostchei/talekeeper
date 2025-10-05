-- Migration 012: Cleric Class Implementation
-- Phase 2.1: Cleric Base Class Implementation
-- Implementation Plan Reference: Phase 2 > Phase 2.1 > Step 2.1.1

-- Cleric-specific features table
CREATE TABLE IF NOT EXISTS cleric_features (
    character_id TEXT PRIMARY KEY,
    domain TEXT,
    channel_divinity_uses INTEGER DEFAULT 0,
    max_channel_divinity INTEGER DEFAULT 1,
    last_cd_reset TEXT,
    divine_intervention_used BOOLEAN DEFAULT FALSE,
    last_divine_intervention TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Divine domains definitions
CREATE TABLE IF NOT EXISTS divine_domains (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    domain_spells TEXT, -- JSON array of spell lists by level
    features TEXT, -- JSON array of domain features
    source TEXT DEFAULT 'PHB'
);

-- Channel Divinity options
CREATE TABLE IF NOT EXISTS channel_divinity_options (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT, -- NULL for universal options like Turn Undead
    description TEXT NOT NULL,
    action_cost TEXT DEFAULT 'action',
    range_value TEXT,
    area_effect TEXT,
    save_type TEXT, -- wisdom, charisma, etc.
    damage_type TEXT,
    uses_per_rest INTEGER DEFAULT 1,
    level_requirement INTEGER DEFAULT 2,
    source TEXT DEFAULT 'PHB'
);

-- Character Channel Divinity tracking
CREATE TABLE IF NOT EXISTS character_channel_divinity (
    character_id TEXT NOT NULL,
    option_id TEXT NOT NULL,
    uses_remaining INTEGER DEFAULT 0,
    last_used TEXT,
    PRIMARY KEY (character_id, option_id),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (option_id) REFERENCES channel_divinity_options(id)
);

-- Insert Cleric class if not exists
INSERT OR IGNORE INTO classes (id, name, description, hit_die, primary_ability, skill_choices, weapon_proficiencies, armor_proficiencies, item_proficiencies)
VALUES (
    'cleric',
    'Cleric',
    'Divine spellcasters who serve gods and channel divine magic through prayer and faith.',
    8,
    'wisdom',
    2,
    'simple_weapons',
    'light_armor,medium_armor,shields',
    'none'
);

-- Insert core Channel Divinity options
INSERT OR IGNORE INTO channel_divinity_options (id, name, domain, description, action_cost, range_value, save_type, level_requirement)
VALUES
    ('turn_undead', 'Turn Undead', NULL,
     'Each undead within 30 feet must make a Wisdom save or be turned for 1 minute.',
     'action', '30 feet', 'wisdom', 2),
    ('destroy_undead', 'Destroy Undead', NULL,
     'Turned undead of CR 1/2 or lower are destroyed instead of turned. Increases with level.',
     'none', 'self', NULL, 5);

-- Insert Life Domain
INSERT OR IGNORE INTO divine_domains (id, name, description, domain_spells, features)
VALUES (
    'life',
    'Life Domain',
    'Gods of life promote vitality and health through healing the sick and wounded, caring for those in need, and driving away the forces of death and undeath.',
    '{"1": ["bless", "cure_wounds"], "3": ["lesser_restoration", "spiritual_weapon"], "5": ["beacon_of_hope", "revivify"], "7": ["death_ward", "guardian_of_faith"], "9": ["mass_cure_wounds", "raise_dead"]}',
    '[
        {
            "name": "Bonus Proficiency",
            "level": 1,
            "description": "You gain proficiency with heavy armor.",
            "type": "proficiency",
            "grants": ["heavy_armor"]
        },
        {
            "name": "Disciple of Life",
            "level": 1,
            "description": "When you cast a healing spell of 1st level or higher, the creature regains additional hit points equal to 2 + the spell level.",
            "type": "passive",
            "mechanics": {
                "healing_bonus": "2 + spell_level",
                "applies_to": "healing_spells_1st_or_higher"
            }
        },
        {
            "name": "Preserve Life",
            "level": 2,
            "description": "Channel Divinity to heal living creatures within 30 feet. Distribute hit points equal to 5 × your cleric level.",
            "type": "channel_divinity",
            "action_cost": "action",
            "range": "30 feet",
            "mechanics": {
                "healing_pool": "5 * cleric_level",
                "max_per_creature": "half_max_hp"
            }
        },
        {
            "name": "Blessed Healer",
            "level": 6,
            "description": "When you cast a healing spell on another creature, you regain 2 + spell level hit points.",
            "type": "passive",
            "mechanics": {
                "self_healing": "2 + spell_level",
                "triggers_on": "healing_other_creatures"
            }
        },
        {
            "name": "Divine Strike",
            "level": 8,
            "description": "Once per turn, when you hit with a weapon attack, deal an extra 1d8 radiant damage. At 14th level, increases to 2d8.",
            "type": "passive",
            "mechanics": {
                "damage_bonus": "1d8_radiant",
                "frequency": "once_per_turn",
                "damage_14": "2d8_radiant"
            }
        },
        {
            "name": "Supreme Healing",
            "level": 17,
            "description": "When you roll dice to restore hit points with a spell, use the maximum number on the dice instead of rolling.",
            "type": "passive",
            "mechanics": {
                "maximize_healing": true
            }
        }
    ]'
);

-- Insert Life Domain Channel Divinity
INSERT OR IGNORE INTO channel_divinity_options (id, name, domain, description, action_cost, range_value, level_requirement)
VALUES (
    'preserve_life', 'Preserve Life', 'life',
    'You present your holy symbol and evoke healing energy that restores hit points equal to 5 × your cleric level. Choose creatures within 30 feet, distributing points as you choose. Cannot heal above half maximum hit points.',
    'action', '30 feet', 2
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_cleric_features_char ON cleric_features(character_id);
CREATE INDEX IF NOT EXISTS idx_channel_divinity_char ON character_channel_divinity(character_id);
CREATE INDEX IF NOT EXISTS idx_channel_divinity_domain ON channel_divinity_options(domain);