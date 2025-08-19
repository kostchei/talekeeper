-- D&D 2024 Game Database Schema - SQLite Version

-- =====================================================
-- REFERENCE TABLES (Game Rules Data)
-- =====================================================

-- Character races
CREATE TABLE races (
    id TEXT PRIMARY KEY DEFAULT (CAST(ABS(RANDOM()) AS TEXT)),
    name VARCHAR(50) UNIQUE NOT NULL,
    size VARCHAR(20) DEFAULT 'Medium',
    speed INTEGER DEFAULT 30,
    ability_score_increase JSON,
    traits JSON,
    description TEXT,
    darkvision_range INTEGER DEFAULT 0,
    special_senses JSON DEFAULT '[]',
    languages JSON DEFAULT '[]',
    bonus_languages INTEGER DEFAULT 0,
    proficiencies JSON DEFAULT '{}',
    has_subraces BOOLEAN DEFAULT FALSE,
    subrace_name VARCHAR(50),
    source_book VARCHAR(100) DEFAULT 'Player''s Handbook 2024',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Character classes
CREATE TABLE classes (
    id TEXT PRIMARY KEY DEFAULT (CAST(ABS(RANDOM()) AS TEXT)),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    hit_die VARCHAR(10) NOT NULL DEFAULT 'd8',
    primary_ability JSON NOT NULL,
    saving_throw_proficiencies JSON NOT NULL,
    armor_proficiencies JSON DEFAULT '[]',
    weapon_proficiencies JSON DEFAULT '[]',
    tool_proficiencies JSON DEFAULT '[]',
    skill_proficiencies JSON DEFAULT '{}',
    starting_equipment JSON DEFAULT '[]',
    starting_gold VARCHAR(20) DEFAULT '2d4 * 10',
    is_spellcaster BOOLEAN DEFAULT FALSE,
    spellcasting_ability VARCHAR(20),
    spellcasting_type VARCHAR(20),
    level_1_features JSON DEFAULT '[]',
    level_2_features JSON DEFAULT '[]',
    level_3_features JSON DEFAULT '[]',
    source_book VARCHAR(100) DEFAULT 'Player''s Handbook 2024',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Character backgrounds
CREATE TABLE backgrounds (
    id TEXT PRIMARY KEY DEFAULT (CAST(ABS(RANDOM()) AS TEXT)),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    skill_proficiencies JSON DEFAULT '[]',
    language_proficiencies JSON DEFAULT '[]',
    tool_proficiencies JSON DEFAULT '[]',
    starting_equipment JSON DEFAULT '[]',
    feature_name VARCHAR(100),
    feature_description TEXT,
    suggested_characteristics JSON DEFAULT '{}',
    source_book VARCHAR(100) DEFAULT 'Player''s Handbook 2024',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Equipment/Items
CREATE TABLE items (
    id TEXT PRIMARY KEY DEFAULT (CAST(ABS(RANDOM()) AS TEXT)),
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    subtype VARCHAR(50),
    rarity VARCHAR(20) DEFAULT 'Common',
    weight DECIMAL(5,2) DEFAULT 0,
    cost_copper INTEGER DEFAULT 0,
    description TEXT,
    properties JSON DEFAULT '{}',
    damage_dice VARCHAR(20),
    damage_type VARCHAR(20),
    armor_class INTEGER,
    strength_requirement INTEGER DEFAULT 0,
    stealth_disadvantage BOOLEAN DEFAULT FALSE,
    is_magical BOOLEAN DEFAULT FALSE,
    requires_attunement BOOLEAN DEFAULT FALSE,
    source_book VARCHAR(100) DEFAULT 'Player''s Handbook 2024'
);

-- Save slots for character management
CREATE TABLE save_slots (
    slot_id INTEGER PRIMARY KEY,
    slot_name VARCHAR(100) NOT NULL,
    is_occupied BOOLEAN DEFAULT FALSE,
    last_saved TIMESTAMP,
    character_name VARCHAR(100),
    character_level INTEGER,
    character_class VARCHAR(50),
    location VARCHAR(100),
    playtime_minutes INTEGER DEFAULT 0
);

-- Characters (player characters)
CREATE TABLE characters (
    id TEXT PRIMARY KEY DEFAULT (CAST(ABS(RANDOM()) AS TEXT)),
    save_slot INTEGER REFERENCES save_slots(slot_id),
    name VARCHAR(100) NOT NULL,
    race_id TEXT REFERENCES races(id),
    class_id TEXT REFERENCES classes(id),
    background_id TEXT REFERENCES backgrounds(id),
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    hit_points INTEGER DEFAULT 8,
    max_hit_points INTEGER DEFAULT 8,
    armor_class INTEGER DEFAULT 10,
    ability_scores JSON NOT NULL,
    proficiency_bonus INTEGER DEFAULT 2,
    proficiencies JSON DEFAULT '{}',
    equipment JSON DEFAULT '[]',
    spells_known JSON DEFAULT '[]',
    spell_slots JSON DEFAULT '{}',
    conditions JSON DEFAULT '[]',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Game state
CREATE TABLE game_states (
    character_id TEXT PRIMARY KEY REFERENCES characters(id),
    current_location VARCHAR(100) DEFAULT 'Starting Town',
    current_hp INTEGER,
    current_spell_slots JSON DEFAULT '{}',
    active_conditions JSON DEFAULT '[]',
    story_flags JSON DEFAULT '{}',
    inventory JSON DEFAULT '[]',
    last_rest_type VARCHAR(20),
    last_rest_time TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);