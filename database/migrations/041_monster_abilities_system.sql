-- Migration 041: Monster Non-Attack Abilities System
-- Adds support for breath weapons, limited use abilities, and save-based effects

CREATE TABLE IF NOT EXISTS monster_ability_tracker (
    encounter_id TEXT NOT NULL,
    monster_id TEXT NOT NULL,
    ability_name TEXT NOT NULL,
    ability_type TEXT NOT NULL,
    recharge_requirement TEXT,
    max_uses INTEGER DEFAULT -1,
    uses_remaining INTEGER DEFAULT -1,
    is_available BOOLEAN DEFAULT 1,
    last_recharge_roll INTEGER,
    PRIMARY KEY (encounter_id, monster_id, ability_name)
);

CREATE TABLE IF NOT EXISTS monster_ability_effects (
    effect_id TEXT PRIMARY KEY,
    encounter_id TEXT NOT NULL,
    source_monster_id TEXT NOT NULL,
    ability_name TEXT NOT NULL,
    target_id TEXT NOT NULL,
    effect_type TEXT NOT NULL,
    save_dc INTEGER,
    duration_type TEXT,
    duration_remaining INTEGER,
    can_repeat_save BOOLEAN,
    save_ability TEXT,
    created_round INTEGER
);

CREATE INDEX IF NOT EXISTS idx_monster_ability_tracker_encounter
ON monster_ability_tracker(encounter_id);

CREATE INDEX IF NOT EXISTS idx_monster_ability_tracker_monster
ON monster_ability_tracker(encounter_id, monster_id);

CREATE INDEX IF NOT EXISTS idx_monster_ability_effects_encounter
ON monster_ability_effects(encounter_id);

CREATE INDEX IF NOT EXISTS idx_monster_ability_effects_target
ON monster_ability_effects(target_id);
