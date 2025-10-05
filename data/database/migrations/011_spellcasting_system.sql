-- Migration 011: Spellcasting System Foundation
-- Phase 1.1: Database Schema Extensions
-- Implementation Plan Reference: Phase 1 > Step 1.1

-- Character spell slots tracking
CREATE TABLE IF NOT EXISTS character_spell_slots (
    character_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    max_slots INTEGER DEFAULT 0,
    used_slots INTEGER DEFAULT 0,
    slot_type TEXT DEFAULT 'standard', -- 'standard', 'pact'
    last_reset TEXT,
    PRIMARY KEY (character_id, spell_level, slot_type),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Character spells known/prepared
CREATE TABLE IF NOT EXISTS character_spells (
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    is_prepared BOOLEAN DEFAULT TRUE,
    source TEXT NOT NULL, -- 'class', 'domain', 'oath', 'patron', 'school'
    source_level INTEGER, -- level when gained
    always_prepared BOOLEAN DEFAULT FALSE, -- domain/oath spells
    ritual_only BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (character_id, spell_id),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (spell_id) REFERENCES spells(id)
);

-- Spell definitions master table
CREATE TABLE IF NOT EXISTS spells (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    level INTEGER NOT NULL,
    school TEXT NOT NULL,
    casting_time TEXT NOT NULL,
    range_value TEXT NOT NULL,
    components TEXT NOT NULL,
    duration TEXT NOT NULL,
    concentration BOOLEAN DEFAULT FALSE,
    ritual BOOLEAN DEFAULT FALSE,
    description TEXT NOT NULL,
    higher_levels TEXT,
    source TEXT DEFAULT 'PHB',
    classes TEXT, -- JSON array of classes that can learn this spell
    created_at TEXT DEFAULT (datetime('now'))
);

-- Spell class lists (for reference and character creation)
CREATE TABLE IF NOT EXISTS spell_class_lists (
    spell_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    is_bonus_spell BOOLEAN DEFAULT FALSE, -- for domain/oath/patron spells
    source_feature TEXT, -- domain name, oath name, etc.
    PRIMARY KEY (spell_id, class_id, source_feature),
    FOREIGN KEY (spell_id) REFERENCES spells(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- Character spellcasting details
CREATE TABLE IF NOT EXISTS character_spellcasting (
    character_id TEXT PRIMARY KEY,
    spellcasting_ability TEXT, -- 'intelligence', 'wisdom', 'charisma'
    spell_attack_bonus INTEGER DEFAULT 0,
    spell_save_dc INTEGER DEFAULT 8,
    ritual_casting BOOLEAN DEFAULT FALSE,
    spellcasting_focus TEXT, -- 'component_pouch', 'arcane_focus', 'holy_symbol', etc.
    spells_known INTEGER DEFAULT 0, -- for classes that know spells vs prepare
    spells_prepared INTEGER DEFAULT 0, -- for classes that prepare spells
    last_preparation_reset TEXT, -- when spells were last prepared
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Concentration tracking during combat
CREATE TABLE IF NOT EXISTS character_concentration (
    character_id TEXT PRIMARY KEY,
    spell_id TEXT,
    spell_level INTEGER,
    start_time TEXT DEFAULT (datetime('now')),
    duration_remaining INTEGER, -- in rounds for combat, minutes otherwise
    concentration_dc INTEGER DEFAULT 10,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (spell_id) REFERENCES spells(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_character_spell_slots_char ON character_spell_slots(character_id);
CREATE INDEX IF NOT EXISTS idx_character_spells_char ON character_spells(character_id);
CREATE INDEX IF NOT EXISTS idx_character_spells_prepared ON character_spells(character_id, is_prepared);
CREATE INDEX IF NOT EXISTS idx_spells_level ON spells(level);
CREATE INDEX IF NOT EXISTS idx_spells_class ON spell_class_lists(class_id);
CREATE INDEX IF NOT EXISTS idx_concentration_char ON character_concentration(character_id);