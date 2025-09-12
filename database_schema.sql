-- TaleKeeper SQLite Database Schema
-- Migration from IndexedDB to SQLite for better data integrity and debugging

PRAGMA foreign_keys = ON;

-- ================================================
-- CHARACTERS TABLE
-- ================================================
CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    save_slot_id TEXT,
    name TEXT NOT NULL,
    
    -- Core D&D Stats
    race_id TEXT NOT NULL DEFAULT '',
    class_id TEXT NOT NULL DEFAULT '',
    subclass_id TEXT,
    background_id TEXT NOT NULL DEFAULT '',
    
    level INTEGER NOT NULL DEFAULT 1,
    experience_points INTEGER NOT NULL DEFAULT 0,
    
    -- Ability Scores (1-20 range)
    strength INTEGER NOT NULL DEFAULT 10,
    dexterity INTEGER NOT NULL DEFAULT 10,
    constitution INTEGER NOT NULL DEFAULT 10,
    intelligence INTEGER NOT NULL DEFAULT 10,
    wisdom INTEGER NOT NULL DEFAULT 10,
    charisma INTEGER NOT NULL DEFAULT 10,
    
    -- Calculated Combat Stats
    armor_class INTEGER NOT NULL DEFAULT 10,
    hit_points_max INTEGER NOT NULL DEFAULT 8,
    hit_points_current INTEGER NOT NULL DEFAULT 8,
    hit_points_temporary INTEGER NOT NULL DEFAULT 0,
    max_hit_points INTEGER NOT NULL DEFAULT 8,
    current_hit_points INTEGER NOT NULL DEFAULT 8,
    hit_dice_max INTEGER NOT NULL DEFAULT 1,
    hit_dice_current INTEGER NOT NULL DEFAULT 1,
    death_saves_successes INTEGER NOT NULL DEFAULT 0,
    death_saves_failures INTEGER NOT NULL DEFAULT 0,
    
    -- Equipment Slots
    equipment_main_hand TEXT,
    equipment_off_hand TEXT,
    equipment_armor TEXT,
    equipment_shield TEXT,
    
    -- Rest Tracking
    last_short_rest TEXT,  -- ISO timestamp
    last_long_rest TEXT,   -- ISO timestamp
    
    -- Metadata
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT,
    notes TEXT DEFAULT '',
    
    -- Foreign Key Constraints
    FOREIGN KEY (save_slot_id) REFERENCES save_slots(id) ON DELETE SET NULL
);

-- ================================================
-- CHARACTER FEATS (Many-to-Many with order)
-- ================================================
CREATE TABLE character_feats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    feat_name TEXT NOT NULL,
    feat_source TEXT NOT NULL DEFAULT 'unknown', -- 'background', 'species', 'class', 'level_up'
    level_acquired INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    UNIQUE(character_id, feat_name)
);

-- ================================================
-- CHARACTER PROFICIENCIES
-- ================================================
CREATE TABLE character_proficiencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    proficiency_type TEXT NOT NULL, -- 'skill', 'tool', 'language', 'weapon', 'armor'
    proficiency_name TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'unknown', -- 'background', 'class', 'race'
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    UNIQUE(character_id, proficiency_name)
);

-- ================================================
-- CHARACTER FEATURES (Class/Racial Features)
-- ================================================
CREATE TABLE character_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    feature_type TEXT NOT NULL DEFAULT 'passive', -- 'action', 'bonus_action', 'reaction', 'passive'
    usage_type TEXT NOT NULL DEFAULT 'permanent', -- 'permanent', 'short_rest', 'long_rest', 'daily'
    level_gained INTEGER NOT NULL DEFAULT 1,
    description TEXT NOT NULL DEFAULT '',
    mechanics TEXT, -- JSON string for complex mechanics
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- ================================================
-- CHARACTER WEAPON MASTERIES
-- ================================================
CREATE TABLE character_weapon_masteries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    weapon_name TEXT NOT NULL,
    mastery_type TEXT NOT NULL, -- 'cleave', 'graze', 'nick', etc.
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    UNIQUE(character_id, weapon_name)
);

-- ================================================
-- CHARACTER CONDITIONS
-- ================================================
CREATE TABLE character_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    condition_name TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    duration TEXT, -- 'permanent', 'end_of_turn', 'end_of_encounter', etc.
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- ================================================
-- CHARACTER RESOURCES (Spell Slots, Class Resources)
-- ================================================
CREATE TABLE character_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    resource_type TEXT NOT NULL, -- 'spell_slot', 'class_resource', 'ability_use'
    resource_name TEXT NOT NULL, -- 'level_1', 'ki_points', 'second_wind'
    current_value INTEGER NOT NULL DEFAULT 0,
    max_value INTEGER NOT NULL DEFAULT 0,
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    UNIQUE(character_id, resource_type, resource_name)
);

-- ================================================
-- CHARACTER INVENTORY
-- ================================================
CREATE TABLE character_inventory (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    item_type TEXT NOT NULL,  -- 'weapon', 'armor', 'shield', 'gear', 'treasure', etc.
    quantity INTEGER NOT NULL DEFAULT 1,
    weight_lb REAL NOT NULL DEFAULT 0.0,
    description TEXT,
    value_gp REAL NOT NULL DEFAULT 0,
    equipped INTEGER NOT NULL DEFAULT 0,  -- 0 = not equipped, 1 = equipped
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- ================================================
-- SAVE SLOTS
-- ================================================
CREATE TABLE save_slots (
    id TEXT PRIMARY KEY,
    slot_number INTEGER NOT NULL UNIQUE,
    is_occupied BOOLEAN NOT NULL DEFAULT FALSE,
    save_name TEXT,
    last_played TEXT, -- ISO timestamp
    play_time_minutes INTEGER NOT NULL DEFAULT 0,
    character_name TEXT,
    character_level INTEGER,
    current_location TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT
);

-- ================================================
-- COMBAT SESSIONS
-- ================================================
CREATE TABLE combat_sessions (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    encounter_name TEXT NOT NULL DEFAULT 'Combat',
    current_round INTEGER NOT NULL DEFAULT 1,
    current_turn INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at TEXT,
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- ================================================
-- GAME STATES
-- ================================================
CREATE TABLE game_states (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    current_location TEXT NOT NULL DEFAULT 'Starting Town',
    game_time TEXT NOT NULL DEFAULT (datetime('now')),
    weather TEXT DEFAULT 'clear',
    notes TEXT DEFAULT '',
    state_data TEXT, -- JSON string for complex state
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT,
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- ================================================
-- EQUIPMENT DATABASE
-- ================================================
CREATE TABLE equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    item_type TEXT NOT NULL,  -- 'weapon', 'armor', 'shield', 'gear', etc.
    rarity TEXT,
    cost_gp REAL NOT NULL DEFAULT 0,
    weight_lb REAL NOT NULL DEFAULT 0.0,
    
    -- Weapon properties (nullable for non-weapons)
    weapon_category TEXT,  -- 'simple_melee', 'martial_melee', 'simple_ranged', 'martial_ranged'
    damage_dice TEXT,
    damage_type TEXT,
    weapon_properties TEXT,  -- JSON array: ["finesse", "light", "thrown"]
    weapon_mastery TEXT,
    range_normal INTEGER,
    range_long INTEGER,
    versatile_damage TEXT,
    ammunition TEXT,
    
    -- Armor properties (nullable for non-armor)
    armor_class INTEGER,
    armor_type TEXT,  -- 'light', 'medium', 'heavy'
    dex_bonus_max INTEGER,  -- NULL means unlimited
    strength_requirement INTEGER,
    stealth_disadvantage BOOLEAN,
    
    -- General properties
    is_magical BOOLEAN DEFAULT FALSE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- CLASS EQUIPMENT CHOICES TABLE
-- ================================================
CREATE TABLE class_equipment_choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id TEXT NOT NULL,
    choice_group TEXT NOT NULL,  -- e.g., 'weapon_choice_1', 'armor_choice'
    choice_name TEXT NOT NULL,   -- Display name like 'Primary Weapon'
    options TEXT NOT NULL,        -- JSON array of options
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(class_id, choice_group)
);

-- ================================================
-- INDEXES FOR PERFORMANCE
-- ================================================
CREATE INDEX idx_characters_save_slot ON characters(save_slot_id);
CREATE INDEX idx_characters_name ON characters(name);
CREATE INDEX idx_character_feats_character_id ON character_feats(character_id);
CREATE INDEX idx_character_features_character_id ON character_features(character_id);
CREATE INDEX idx_character_proficiencies_character_id ON character_proficiencies(character_id);
CREATE INDEX idx_character_resources_character_id ON character_resources(character_id);
CREATE INDEX idx_character_inventory_character_id ON character_inventory(character_id);
CREATE INDEX idx_equipment_name ON equipment(name);
CREATE INDEX idx_equipment_item_type ON equipment(item_type);
CREATE INDEX idx_save_slots_slot_number ON save_slots(slot_number);
CREATE INDEX idx_combat_sessions_character_id ON combat_sessions(character_id);
CREATE INDEX idx_game_states_character_id ON game_states(character_id);
CREATE INDEX idx_class_equipment_choices_class_id ON class_equipment_choices(class_id);

-- ================================================
-- VIEWS FOR COMMON QUERIES
-- ================================================

-- Complete character view with all feats and features
CREATE VIEW character_full AS
SELECT 
    c.*,
    GROUP_CONCAT(cf.feat_name, '|') as feats,
    GROUP_CONCAT(cp.proficiency_name, '|') as proficiencies,
    GROUP_CONCAT(cwm.weapon_name || ':' || cwm.mastery_type, '|') as weapon_masteries
FROM characters c
LEFT JOIN character_feats cf ON c.id = cf.character_id
LEFT JOIN character_proficiencies cp ON c.id = cp.character_id  
LEFT JOIN character_weapon_masteries cwm ON c.id = cwm.character_id
GROUP BY c.id;

-- Character summary for save slots
CREATE VIEW character_summary AS
SELECT 
    c.id,
    c.name,
    c.level,
    c.race_id,
    c.class_id,
    c.hit_points_current,
    c.hit_points_max,
    s.slot_number,
    s.last_played
FROM characters c
JOIN save_slots s ON c.save_slot_id = s.id
WHERE s.is_occupied = TRUE;

-- ================================================
-- LEVEL PROGRESSION TABLE (from level_ch.json)
-- ================================================
CREATE TABLE level_progression (
    level INTEGER PRIMARY KEY,
    experience_points INTEGER NOT NULL,
    proficiency_bonus INTEGER NOT NULL
);

-- ================================================
-- LEVEL UP COSTS TABLE (from levelup_cost.json)
-- ================================================
CREATE TABLE levelup_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level_range_start INTEGER NOT NULL,
    level_range_end INTEGER NOT NULL,
    training_days INTEGER NOT NULL,
    training_cost_gp INTEGER NOT NULL
);

-- ================================================
-- CLASS-SPECIFIC FEATURE TABLES
-- ================================================

-- FIGHTER FEATURES
CREATE TABLE fighter_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    
    -- Core Fighter Features
    fighting_style TEXT, -- 'archery', 'defense', 'dueling', etc.
    action_surge_uses_current INTEGER DEFAULT 0,
    action_surge_uses_max INTEGER DEFAULT 0,
    second_wind_used BOOLEAN DEFAULT FALSE,
    indomitable_uses_current INTEGER DEFAULT 0,
    indomitable_uses_max INTEGER DEFAULT 0,
    extra_attacks INTEGER DEFAULT 1, -- 1 base, +1 at levels 5, 11, 20
    
    -- Weapon Mastery
    weapon_masteries_known INTEGER DEFAULT 3, -- Scales with level
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    PRIMARY KEY (character_id)
);

-- BARBARIAN FEATURES  
CREATE TABLE barbarian_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    
    -- Rage System
    rage_uses_current INTEGER DEFAULT 0,
    rage_uses_max INTEGER DEFAULT 2, -- Scales with level
    rage_damage_bonus INTEGER DEFAULT 2, -- +2 at level 1, scales up
    is_raging BOOLEAN DEFAULT FALSE,
    rage_turns_remaining INTEGER DEFAULT 0,
    
    -- Unarmored Defense (AC = 10 + Dex + Con)
    unarmored_defense_active BOOLEAN DEFAULT TRUE,
    
    -- Other Features
    reckless_attack_available BOOLEAN DEFAULT FALSE, -- Level 2+
    danger_sense_active BOOLEAN DEFAULT FALSE, -- Level 2+
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    PRIMARY KEY (character_id)
);

-- WIZARD FEATURES (Full Spellcaster)
CREATE TABLE wizard_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    
    -- Spell Slots (Full Caster Progression)
    spell_slots_1_current INTEGER DEFAULT 0,
    spell_slots_1_max INTEGER DEFAULT 0,
    spell_slots_2_current INTEGER DEFAULT 0,
    spell_slots_2_max INTEGER DEFAULT 0,
    spell_slots_3_current INTEGER DEFAULT 0,
    spell_slots_3_max INTEGER DEFAULT 0,
    spell_slots_4_current INTEGER DEFAULT 0,
    spell_slots_4_max INTEGER DEFAULT 0,
    spell_slots_5_current INTEGER DEFAULT 0,
    spell_slots_5_max INTEGER DEFAULT 0,
    spell_slots_6_current INTEGER DEFAULT 0,
    spell_slots_6_max INTEGER DEFAULT 0,
    spell_slots_7_current INTEGER DEFAULT 0,
    spell_slots_7_max INTEGER DEFAULT 0,
    spell_slots_8_current INTEGER DEFAULT 0,
    spell_slots_8_max INTEGER DEFAULT 0,
    spell_slots_9_current INTEGER DEFAULT 0,
    spell_slots_9_max INTEGER DEFAULT 0,
    
    -- Wizard-Specific Features
    arcane_school TEXT, -- 'abjuration', 'evocation', etc.
    arcane_recovery_used BOOLEAN DEFAULT FALSE, -- Short rest feature
    spellbook_spells_known INTEGER DEFAULT 6, -- Starts with 6, +2 per level
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    PRIMARY KEY (character_id)
);

-- WARLOCK FEATURES (Pact Magic - Different Slot System)
CREATE TABLE warlock_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    
    -- Pact Magic Slots (All same level, recover on short rest)
    pact_slots_current INTEGER DEFAULT 0,
    pact_slots_max INTEGER DEFAULT 1, -- 1 at level 1, max 4 at level 17+
    pact_slot_level INTEGER DEFAULT 1, -- Level of pact slots (1-5)
    
    -- Warlock-Specific Features
    patron TEXT, -- 'fiend', 'archfey', 'great_old_one', etc.
    pact_boon TEXT, -- 'chain', 'blade', 'tome', null until level 3
    eldritch_invocations TEXT, -- JSON array of known invocations
    
    -- Patron Features
    patron_feature_uses_current INTEGER DEFAULT 0,
    patron_feature_uses_max INTEGER DEFAULT 0,
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    PRIMARY KEY (character_id)
);

-- CLERIC FEATURES (Full Spellcaster + Domain Powers)
CREATE TABLE cleric_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    
    -- Spell Slots (Same as Wizard - Full Caster)
    spell_slots_1_current INTEGER DEFAULT 0,
    spell_slots_1_max INTEGER DEFAULT 0,
    spell_slots_2_current INTEGER DEFAULT 0,
    spell_slots_2_max INTEGER DEFAULT 0,
    spell_slots_3_current INTEGER DEFAULT 0,
    spell_slots_3_max INTEGER DEFAULT 0,
    spell_slots_4_current INTEGER DEFAULT 0,
    spell_slots_4_max INTEGER DEFAULT 0,
    spell_slots_5_current INTEGER DEFAULT 0,
    spell_slots_5_max INTEGER DEFAULT 0,
    spell_slots_6_current INTEGER DEFAULT 0,
    spell_slots_6_max INTEGER DEFAULT 0,
    spell_slots_7_current INTEGER DEFAULT 0,
    spell_slots_7_max INTEGER DEFAULT 0,
    spell_slots_8_current INTEGER DEFAULT 0,
    spell_slots_8_max INTEGER DEFAULT 0,
    spell_slots_9_current INTEGER DEFAULT 0,
    spell_slots_9_max INTEGER DEFAULT 0,
    
    -- Cleric-Specific Features
    divine_domain TEXT, -- 'life', 'light', 'war', etc.
    channel_divinity_uses_current INTEGER DEFAULT 0,
    channel_divinity_uses_max INTEGER DEFAULT 1, -- Scales with level
    
    -- Domain Spells (always prepared, don't count against limit)
    domain_spells_known TEXT, -- JSON array of domain spells
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    PRIMARY KEY (character_id)
);

-- ROGUE FEATURES
CREATE TABLE rogue_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    
    -- Sneak Attack (scales with level)
    sneak_attack_dice INTEGER DEFAULT 1, -- 1d6 at level 1, +1d6 every 2 levels
    
    -- Expertise (double proficiency bonus)
    expertise_skills TEXT, -- JSON array of skills with expertise
    
    -- Cunning Action (level 2+)
    cunning_action_available BOOLEAN DEFAULT FALSE,
    
    -- Uncanny Dodge (level 5+)
    uncanny_dodge_available BOOLEAN DEFAULT FALSE,
    uncanny_dodge_used BOOLEAN DEFAULT FALSE, -- Once per turn
    
    -- Evasion (level 7+)
    evasion_available BOOLEAN DEFAULT FALSE,
    
    -- Archetype
    archetype TEXT, -- 'thief', 'assassin', 'arcane_trickster', etc.
    
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    PRIMARY KEY (character_id)
);

CREATE TABLE campaigns (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    monster_type_weights TEXT,
    difficulty_distribution TEXT,
    rest_rules TEXT,
    style TEXT,
    available_classes TEXT
);

-- ================================================
-- INDEXES FOR CLASS-SPECIFIC TABLES
-- ================================================
CREATE INDEX idx_fighter_features_character_id ON fighter_features(character_id);
CREATE INDEX idx_barbarian_features_character_id ON barbarian_features(character_id);
CREATE INDEX idx_wizard_features_character_id ON wizard_features(character_id);
CREATE INDEX idx_warlock_features_character_id ON warlock_features(character_id);
CREATE INDEX idx_cleric_features_character_id ON cleric_features(character_id);
CREATE INDEX idx_rogue_features_character_id ON rogue_features(character_id);