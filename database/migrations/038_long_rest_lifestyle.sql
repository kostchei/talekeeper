CREATE TABLE IF NOT EXISTS character_long_rests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    hex_q INTEGER NOT NULL,
    hex_r INTEGER NOT NULL,
    rest_date TEXT NOT NULL,
    lifestyle_type TEXT NOT NULL,
    lifestyle_cost_gp REAL NOT NULL,
    settlement_name TEXT,
    accommodation_name TEXT,
    hazard_triggered INTEGER DEFAULT 0,
    hazard_type TEXT,
    hazard_result TEXT,
    rest_completed INTEGER DEFAULT 0,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

CREATE INDEX IF NOT EXISTS idx_character_rests
ON character_long_rests(character_id, rest_date);

CREATE INDEX IF NOT EXISTS idx_hex_rests
ON character_long_rests(character_id, hex_q, hex_r);

ALTER TABLE character_hex_map ADD COLUMN settlement_name TEXT;
ALTER TABLE character_hex_map ADD COLUMN accommodation_name TEXT;
