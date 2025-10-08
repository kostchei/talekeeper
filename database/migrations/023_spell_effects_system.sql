-- Migration 023: Spell Effects System Foundation
-- Phase 0.1: Database Schema for Spell Effect Tracking
-- Implementation Plan Reference: SPELL_EFFECTS_IMPLEMENTATION_ANALYSIS.md > Phase 0.1

-- Active spell effects tracking (buffs, debuffs, ongoing spell effects)
CREATE TABLE IF NOT EXISTS active_spell_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    spell_name TEXT NOT NULL,
    spell_level_cast INTEGER NOT NULL,
    effect_type TEXT NOT NULL,
    effect_data TEXT,
    duration_type TEXT NOT NULL,
    duration_remaining INTEGER,
    rounds_remaining INTEGER,
    concentration BOOLEAN DEFAULT FALSE,
    caster_id TEXT,
    target_id TEXT,
    applied_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT,

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (spell_id) REFERENCES spells(id),
    FOREIGN KEY (caster_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Enhance character_conditions table for spell source tracking
ALTER TABLE character_conditions ADD COLUMN source_spell_id TEXT;
ALTER TABLE character_conditions ADD COLUMN duration_rounds INTEGER;
ALTER TABLE character_conditions ADD COLUMN save_dc INTEGER;
ALTER TABLE character_conditions ADD COLUMN save_ability TEXT;

-- Spell summons tracking (Find Steed, future summon spells)
CREATE TABLE IF NOT EXISTS spell_summons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    summon_name TEXT NOT NULL,
    summon_type TEXT NOT NULL,
    stat_block TEXT NOT NULL,
    current_hp INTEGER NOT NULL,
    max_hp INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    summoned_at TEXT DEFAULT (datetime('now')),
    dismissed_at TEXT,

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (spell_id) REFERENCES spells(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_active_effects_character ON active_spell_effects(character_id);
CREATE INDEX IF NOT EXISTS idx_active_effects_spell ON active_spell_effects(spell_id);
CREATE INDEX IF NOT EXISTS idx_active_effects_caster ON active_spell_effects(caster_id);
CREATE INDEX IF NOT EXISTS idx_active_effects_expiration ON active_spell_effects(expires_at);
CREATE INDEX IF NOT EXISTS idx_conditions_spell ON character_conditions(source_spell_id);
CREATE INDEX IF NOT EXISTS idx_summons_character ON spell_summons(character_id);
CREATE INDEX IF NOT EXISTS idx_summons_active ON spell_summons(character_id, is_active);
