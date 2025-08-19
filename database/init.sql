-- D&D 2024 Game Database Schema
-- This schema is designed for extensibility. AI agents should follow these patterns when adding features.

-- Enable UUID extension for better ID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- REFERENCE TABLES (Game Rules Data)
-- =====================================================

-- Character races (Human, Dwarf initially, expandable)
CREATE TABLE races (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    size VARCHAR(20) DEFAULT 'Medium',
    speed INTEGER DEFAULT 30,
    -- D&D 2024: Ability score increases moved to backgrounds, but keeping for compatibility
    ability_score_increase JSONB DEFAULT '{}', -- {"choice": 2, "options": ["str", "dex"]}
    traits JSONB DEFAULT '[]', -- ["Darkvision", "Dwarven Resilience"]
    proficiencies JSONB DEFAULT '{}', -- {"tools": ["Smith's Tools"], "weapons": ["Battleaxe"]}
    -- D&D 2024 race features:
    darkvision_range INTEGER DEFAULT 0, -- Distance in feet (60 for dwarves, 0 for humans)
    special_senses JSONB DEFAULT '[]', -- ["tremorsense 60", "blindsight 30"]
    languages JSONB DEFAULT '[]', -- ["Common", "Dwarvish"] - JSON for SQLAlchemy compatibility
    bonus_languages INTEGER DEFAULT 0, -- Extra language choices
    has_subraces BOOLEAN DEFAULT FALSE, -- Whether race has subraces
    subrace_name VARCHAR(50), -- For subrace entries
    -- Expansion fields for AI agents:
    subraces JSONB DEFAULT '[]', -- For future subrace support
    source_book VARCHAR(100) DEFAULT 'Player''s Handbook 2024',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE races IS 'Playable character races. AI agents: Add new races following D&D 2024 rules';
COMMENT ON COLUMN races.ability_score_increase IS 'JSON format: {"ability": modifier}';

-- Character classes (Fighter, Rogue initially)
CREATE TABLE classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT, -- Class description
    hit_die VARCHAR(10) NOT NULL DEFAULT 'd8', -- "d10" for fighter, "d8" for rogue
    primary_ability JSONB, -- ["strength", "dexterity"] for choice, or single ability
    saving_throw_proficiencies VARCHAR[], -- ["strength", "constitution"]
    armor_proficiencies VARCHAR[], -- ["light", "medium", "heavy", "shields"]
    weapon_proficiencies VARCHAR[], -- ["simple", "martial"]
    tool_proficiencies VARCHAR[], -- ["thieves_tools"]
    skill_proficiencies JSONB, -- {"choose": 2, "from": ["Athletics", "Perception"]}
    starting_equipment JSONB, -- Detailed equipment choices
    starting_gold VARCHAR(20) DEFAULT '2d4 * 10', -- Starting gold dice expression
    features_by_level JSONB, -- Level-based features
    -- Spellcasting properties
    is_spellcaster BOOLEAN DEFAULT FALSE,
    spellcasting_ability VARCHAR(20), -- "intelligence", "wisdom", "charisma" 
    spellcasting_type VARCHAR(20), -- "full", "half", "third", "pact"
    ritual_casting BOOLEAN DEFAULT FALSE,
    spellcasting_focus VARCHAR(50), -- "arcane focus", "holy symbol"
    spell_slots_by_level JSONB, -- For spellcasting classes
    -- Subclass properties
    subclass_level INTEGER DEFAULT 3,
    subclass_name VARCHAR(50) DEFAULT 'Subclass',
    -- Multiclassing
    multiclass_requirements JSONB DEFAULT '{}',
    -- Metadata
    source_book VARCHAR(100) DEFAULT 'Player''s Handbook 2024',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE classes IS 'Character classes with progression. AI agents: Use features_by_level for class abilities';

-- Subclasses (Champion, Battle Master for Fighter; Thief, Assassin for Rogue)
CREATE TABLE subclasses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    choice_level INTEGER DEFAULT 3, -- Level when subclass is chosen
    features JSONB, -- {"3": ["Improved Critical"], "7": ["Remarkable Athlete"]}
    description TEXT,
    UNIQUE(class_id, name)
);
COMMENT ON TABLE subclasses IS 'Class archetypes chosen at level 3. Extend features JSONB for new abilities';

-- Backgrounds (Farmer, Soldier initially)
CREATE TABLE backgrounds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT, -- Background description
    -- D&D 2024: Backgrounds provide ability score increases
    ability_score_increases JSONB NOT NULL, -- {"choice": 2, "any": 1} or {"strength": 2, "wisdom": 1}
    skill_proficiencies VARCHAR[], -- ["Animal Handling", "Survival"]
    tool_proficiencies VARCHAR[], -- ["Herbalism Kit"] 
    language_proficiencies VARCHAR[], -- ["Dwarvish", "Giant"] - languages gained
    languages INTEGER DEFAULT 0, -- Number of bonus languages
    starting_equipment JSONB, -- Starting equipment from background
    starting_gold VARCHAR(20) DEFAULT '2d4 * 10', -- Alternative to equipment
    feature_name VARCHAR(100), -- "Rustic Hospitality"
    feature_description TEXT,
    -- D&D 2024 roleplay elements:
    suggested_personality_traits JSONB DEFAULT '[]', 
    suggested_ideals JSONB DEFAULT '[]',
    suggested_bonds JSONB DEFAULT '[]',
    suggested_flaws JSONB DEFAULT '[]',
    contacts_and_connections JSONB DEFAULT '[]', -- NPCs and organizations
    story_hooks JSONB DEFAULT '[]', -- Adventure hooks tied to background
    variants JSONB DEFAULT '[]', -- Different versions of the background
    customization_options JSONB DEFAULT '{}', -- Player customization choices
    -- Expansion fields (compatibility):
    personality_traits JSONB, -- For roleplay elements
    ideals JSONB,
    bonds JSONB,
    flaws JSONB,
    source_book VARCHAR(100) DEFAULT 'Player''s Handbook 2024',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE backgrounds IS 'Character backgrounds providing skills and story hooks';

-- =====================================================
-- GAME ENTITIES
-- =====================================================

-- Monsters (Cultist, Manes, Slaad Tadpole, etc.)
CREATE TABLE monsters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    challenge_rating DECIMAL(3,2), -- 0.125, 0.25, 0.5, 1, etc.
    size VARCHAR(20),
    type VARCHAR(50), -- "humanoid", "fiend", "aberration"
    alignment VARCHAR(50),
    -- Combat stats
    armor_class INTEGER,
    hit_points INTEGER,
    hit_dice VARCHAR(20), -- "2d8+2"
    speed JSONB, -- {"walk": 30, "swim": 20}
    -- Abilities
    strength INTEGER,
    dexterity INTEGER,
    constitution INTEGER,
    intelligence INTEGER,
    wisdom INTEGER,
    charisma INTEGER,
    -- Defenses
    saving_throws JSONB, -- {"wisdom": 2, "charisma": 1}
    skills JSONB, -- {"perception": 4, "stealth": 3}
    damage_resistances VARCHAR[],
    damage_immunities VARCHAR[],
    condition_immunities VARCHAR[],
    senses JSONB, -- {"darkvision": 60, "passive_perception": 10}
    languages VARCHAR[],
    -- Actions and abilities
    actions JSONB, -- Attack actions, special abilities
    reactions JSONB, -- Reaction abilities if any
    legendary_actions JSONB, -- For future boss monsters
    -- AI behavior
    ai_script VARCHAR(50), -- "basic_melee", "recharge_priority", "control_then_damage"
    -- Loot
    loot_table JSONB, -- {"gold": "2d6", "items": ["potion_healing"], "chance": 0.3}
    xp_value INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE monsters IS 'Monster stat blocks. AI agents: Use ai_script for behavior patterns';
COMMENT ON COLUMN monsters.actions IS 'Format: [{"name": "Claw", "type": "melee", "bonus": 5, "damage": "1d6+3", "damage_type": "slashing"}]';

-- Items and Equipment
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50), -- "weapon", "armor", "potion", "scroll", "misc"
    subtype VARCHAR(50), -- "martial_weapon", "heavy_armor", etc.
    rarity VARCHAR(20) DEFAULT 'common', -- common, uncommon, rare, very_rare, legendary
    -- Physical properties
    weight DECIMAL(6,2) DEFAULT 0,
    cost_gp DECIMAL(10,2) DEFAULT 0,
    -- Combat properties (weapons/armor)
    damage_dice VARCHAR(20), -- "1d8" for longsword
    damage_type VARCHAR(20), -- "slashing", "piercing", "bludgeoning"
    armor_class INTEGER, -- Base AC for armor
    armor_type VARCHAR(20), -- "light", "medium", "heavy"
    properties JSONB, -- ["versatile", "finesse", "two-handed"]
    -- Magic properties
    magic_bonus INTEGER DEFAULT 0, -- +1, +2, etc.
    magic_properties JSONB, -- Special magic effects
    charges INTEGER, -- For items with limited uses
    -- Requirements
    strength_requirement INTEGER, -- Min strength for heavy armor
    attunement BOOLEAN DEFAULT FALSE,
    -- Descriptions
    description TEXT,
    -- Expansion fields:
    consumable BOOLEAN DEFAULT FALSE,
    stackable BOOLEAN DEFAULT FALSE,
    max_stack INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE items IS 'All game items. AI agents: Use type/subtype for categorization, properties for special rules';

-- =====================================================
-- PLAYER DATA TABLES
-- =====================================================

-- Save slots (multiple characters per player)
CREATE TABLE save_slots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slot_number INTEGER NOT NULL CHECK (slot_number BETWEEN 1 AND 10),
    character_name VARCHAR(100),
    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    play_time INTEGER DEFAULT 0, -- Total minutes played
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(slot_number)
);
COMMENT ON TABLE save_slots IS 'Save game slots. AI agents: Expand to 10+ slots if needed';

-- Player Characters
CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    save_slot_id UUID REFERENCES save_slots(id) ON DELETE CASCADE,
    -- Basic info
    name VARCHAR(100) NOT NULL,
    race_id UUID REFERENCES races(id),
    class_id UUID REFERENCES classes(id),
    subclass_id UUID REFERENCES subclasses(id),
    background_id UUID REFERENCES backgrounds(id),
    level INTEGER DEFAULT 1,
    experience_points INTEGER DEFAULT 0,
    -- Abilities (base scores)
    strength INTEGER DEFAULT 10,
    dexterity INTEGER DEFAULT 10,
    constitution INTEGER DEFAULT 10,
    intelligence INTEGER DEFAULT 10,
    wisdom INTEGER DEFAULT 10,
    charisma INTEGER DEFAULT 10,
    -- Combat stats (calculated but stored for performance)
    hit_points_max INTEGER,
    hit_points_current INTEGER,
    hit_points_temporary INTEGER DEFAULT 0,
    armor_class INTEGER DEFAULT 10,
    initiative_bonus INTEGER DEFAULT 0,
    speed INTEGER DEFAULT 30,
    -- Resources
    hit_dice_current INTEGER, -- Current hit dice available
    hit_dice_max INTEGER, -- Maximum hit dice (equal to level)
    -- Proficiencies
    proficiency_bonus INTEGER DEFAULT 2,
    proficiencies JSONB DEFAULT '[]', -- Combined proficiencies for simplified model
    features JSONB DEFAULT '{}', -- Class and racial features
    skill_proficiencies VARCHAR[], -- ["Athletics", "Perception"]
    tool_proficiencies VARCHAR[],
    weapon_proficiencies VARCHAR[], -- ["simple", "martial"]
    armor_proficiencies VARCHAR[], -- ["light", "medium", "shields"]
    saving_throw_proficiencies VARCHAR[], -- ["strength", "constitution"]
    -- Status
    inspiration BOOLEAN DEFAULT FALSE,
    death_saves_successes INTEGER DEFAULT 0,
    death_saves_failures INTEGER DEFAULT 0,
    conditions VARCHAR[], -- ["poisoned", "frightened"]
    -- Currency
    copper INTEGER DEFAULT 0,
    silver INTEGER DEFAULT 0,
    gold INTEGER DEFAULT 0,
    platinum INTEGER DEFAULT 0,
    -- Equipment (for simplified model - separate inventory system also exists)
    equipment_main_hand UUID REFERENCES items(id),
    equipment_off_hand UUID REFERENCES items(id),
    equipment_armor UUID REFERENCES items(id), 
    equipment_shield UUID REFERENCES items(id),
    -- Expansion fields:
    spell_slots_used JSONB, -- {"1": 2, "2": 1} for casters
    prepared_spells INTEGER[], -- References to spell table
    personality JSONB, -- Roleplay characteristics
    notes TEXT, -- Player notes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE characters IS 'Player characters with full D&D stats. AI agents: Calculate derived stats from base abilities';

-- Character Inventory
CREATE TABLE character_inventory (
    id SERIAL PRIMARY KEY,
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    item_id UUID REFERENCES items(id),
    quantity INTEGER DEFAULT 1,
    equipped BOOLEAN DEFAULT FALSE,
    equipped_slot VARCHAR(50), -- "main_hand", "off_hand", "armor", "ring_1", etc.
    identified BOOLEAN DEFAULT TRUE, -- For magic items
    charges_remaining INTEGER, -- For items with charges
    notes TEXT, -- Player notes about item
    UNIQUE(character_id, item_id, equipped_slot)
);
COMMENT ON TABLE character_inventory IS 'Items owned by characters. AI agents: Use equipped_slot for worn/wielded items';

-- =====================================================
-- GAME STATE TABLES
-- =====================================================

-- Current game state (where the character is, what they're doing)
CREATE TABLE game_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    current_location VARCHAR(50) DEFAULT 'town', -- "town", "dungeon", "combat", "rest"
    dungeon_level INTEGER DEFAULT 0,
    rooms_cleared INTEGER DEFAULT 0,
    current_encounter_id INTEGER,
    -- Rest tracking
    short_rests_used INTEGER DEFAULT 0,
    last_long_rest TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Expansion fields:
    quest_flags JSONB, -- {"found_artifact": true, "talked_to_innkeeper": false}
    map_explored JSONB, -- Revealed map sections
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id)
);
COMMENT ON TABLE game_states IS 'Current game progress. AI agents: Add quest_flags for story progression';

-- Encounter history (what fights happened)
CREATE TABLE encounter_history (
    id SERIAL PRIMARY KEY,
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    encounter_number INTEGER,
    monster_ids INTEGER[], -- Array of monster IDs faced
    outcome VARCHAR(20), -- "victory", "flee", "defeat"
    rounds_lasted INTEGER,
    damage_dealt INTEGER,
    damage_taken INTEGER,
    loot_gained JSONB, -- {"gold": 15, "items": [1, 5]}
    experience_gained INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE encounter_history IS 'Combat log for analysis. AI agents: Use for difficulty scaling';

-- Active Effects (buffs, debuffs, ongoing spells)
CREATE TABLE active_effects (
    id SERIAL PRIMARY KEY,
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    effect_name VARCHAR(100),
    effect_type VARCHAR(50), -- "buff", "debuff", "condition"
    source VARCHAR(100), -- What caused this effect
    duration_type VARCHAR(20), -- "rounds", "minutes", "hours", "until_rest"
    duration_remaining INTEGER,
    modifiers JSONB, -- {"ac": 2, "strength": -2}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE active_effects IS 'Temporary effects on characters. Clear on rest or duration expiry';

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_characters_save_slot ON characters(save_slot_id);
CREATE INDEX idx_inventory_character ON character_inventory(character_id);
CREATE INDEX idx_inventory_equipped ON character_inventory(character_id, equipped);
CREATE INDEX idx_game_states_character ON game_states(character_id);
CREATE INDEX idx_encounter_history_character ON encounter_history(character_id);
CREATE INDEX idx_active_effects_character ON active_effects(character_id);
CREATE INDEX idx_monsters_cr ON monsters(challenge_rating);
CREATE INDEX idx_items_type ON items(type, subtype);

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to calculate ability modifier
CREATE OR REPLACE FUNCTION ability_modifier(score INTEGER)
RETURNS INTEGER AS $$
BEGIN
    RETURN FLOOR((score - 10) / 2.0);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
COMMENT ON FUNCTION ability_modifier IS 'Converts ability score to modifier per D&D rules';

-- Function to calculate proficiency bonus by level
CREATE OR REPLACE FUNCTION proficiency_bonus(level INTEGER)
RETURNS INTEGER AS $$
BEGIN
    RETURN CEIL(level / 4.0) + 1;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
COMMENT ON FUNCTION proficiency_bonus IS 'Returns proficiency bonus for character level';

-- Trigger to update character's updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_game_states_updated_at BEFORE UPDATE ON game_states
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();