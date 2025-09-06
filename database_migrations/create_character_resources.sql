-- Unified Character Resource System
-- Scales to all 11 D&D classes and multiclass characters

CREATE TABLE IF NOT EXISTS character_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    resource_name TEXT NOT NULL,        -- "Second Wind", "Action Surge", "Rage", "Spell Slot Level 1"
    current_uses INTEGER NOT NULL DEFAULT 0,
    max_uses INTEGER NOT NULL DEFAULT 0,
    rest_type TEXT NOT NULL,            -- "short_rest", "long_rest", "none"
    source_class TEXT,                  -- "fighter", "barbarian", "wizard", etc.
    source_level INTEGER,               -- Level when gained
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (character_id) REFERENCES characters(id),
    UNIQUE(character_id, resource_name)
);

-- Index for fast rest queries
CREATE INDEX IF NOT EXISTS idx_character_resources_rest 
ON character_resources(character_id, rest_type);

-- Index for fast class queries  
CREATE INDEX IF NOT EXISTS idx_character_resources_class
ON character_resources(character_id, source_class);