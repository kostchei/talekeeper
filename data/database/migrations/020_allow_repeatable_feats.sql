-- Allow repeatable feats (like Skilled) to be taken multiple times
-- Add repeatable flag to feats table and remove UNIQUE constraint from character_feats

-- Add repeatable column to feats table
ALTER TABLE feats ADD COLUMN repeatable INTEGER DEFAULT 0;

-- Mark Skilled as repeatable
UPDATE feats SET repeatable = 1 WHERE name = 'Skilled';

-- Rebuild character_feats without UNIQUE constraint
DROP VIEW IF EXISTS character_full;

CREATE TABLE character_feats_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    feat_name TEXT NOT NULL,
    feat_id TEXT,
    feat_source TEXT NOT NULL DEFAULT 'unknown',
    level_acquired INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

INSERT INTO character_feats_new (id, character_id, feat_name, feat_id, feat_source, level_acquired, created_at)
SELECT id, character_id, feat_name, feat_id, feat_source, level_acquired, created_at
FROM character_feats;

DROP TABLE character_feats;

ALTER TABLE character_feats_new RENAME TO character_feats;

CREATE INDEX idx_character_feats_character_id ON character_feats(character_id);

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