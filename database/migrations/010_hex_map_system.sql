CREATE TABLE IF NOT EXISTS character_hex_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    q INTEGER NOT NULL,
    r INTEGER NOT NULL,
    terrain_type TEXT NOT NULL,
    biome TEXT NOT NULL,
    encounter_seed INTEGER,
    settlement_type TEXT,
    revealed INTEGER DEFAULT 0,
    visited INTEGER DEFAULT 0,
    first_visited_date TEXT,
    last_visited_date TEXT,
    visit_count INTEGER DEFAULT 0,
    cleared INTEGER DEFAULT 0,
    cleared_date TEXT,
    UNIQUE(character_id, q, r),
    FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hex_map_character ON character_hex_map(character_id);
CREATE INDEX IF NOT EXISTS idx_hex_map_coords ON character_hex_map(character_id, q, r);

CREATE TABLE IF NOT EXISTS character_hex_position (
    character_id TEXT PRIMARY KEY,
    current_q INTEGER NOT NULL DEFAULT 0,
    current_r INTEGER NOT NULL DEFAULT 0,
    facing_direction INTEGER DEFAULT 0,
    FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hex_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    hex_q INTEGER NOT NULL,
    hex_r INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    event_date TEXT NOT NULL,
    character_level INTEGER,
    narrative TEXT,
    outcome TEXT,
    FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hex_events_character ON hex_events(character_id);
CREATE INDEX IF NOT EXISTS idx_hex_events_hex ON hex_events(character_id, hex_q, hex_r);

CREATE TABLE IF NOT EXISTS hex_combat_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hex_event_id INTEGER NOT NULL,
    monster_name TEXT NOT NULL,
    monster_cr INTEGER,
    quantity INTEGER DEFAULT 1,
    killed INTEGER DEFAULT 0,
    fled INTEGER DEFAULT 0,
    combat_rounds INTEGER,
    damage_dealt INTEGER,
    damage_taken INTEGER,
    FOREIGN KEY(hex_event_id) REFERENCES hex_events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hex_loot_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hex_event_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    item_type TEXT,
    quantity INTEGER DEFAULT 1,
    value_gp INTEGER,
    equipped INTEGER DEFAULT 0,
    sold INTEGER DEFAULT 0,
    FOREIGN KEY(hex_event_id) REFERENCES hex_events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hex_narrative_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hex_event_id INTEGER NOT NULL,
    narrative_text TEXT NOT NULL,
    narrative_type TEXT,
    timestamp TEXT,
    FOREIGN KEY(hex_event_id) REFERENCES hex_events(id) ON DELETE CASCADE
);
