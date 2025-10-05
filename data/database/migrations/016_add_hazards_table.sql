CREATE TABLE IF NOT EXISTS hazards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level_min INTEGER NOT NULL,
    level_max INTEGER NOT NULL,
    hazard_type TEXT NOT NULL,
    dc INTEGER,
    save_type TEXT,
    damage_dice TEXT,
    damage_avg INTEGER,
    damage_type TEXT,
    failure_effect TEXT NOT NULL,
    success_effect TEXT,
    mechanics TEXT,
    description TEXT,
    category TEXT DEFAULT 'standard',
    frequency TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, level_min, level_max)
);

CREATE INDEX idx_hazards_level ON hazards(level_min, level_max);
CREATE INDEX idx_hazards_type ON hazards(hazard_type);
CREATE INDEX idx_hazards_category ON hazards(category);