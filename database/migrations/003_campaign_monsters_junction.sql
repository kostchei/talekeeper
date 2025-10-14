-- Campaign-Monster Junction Table
-- Tracks which monsters appear in which campaigns with campaign-specific metadata

CREATE TABLE IF NOT EXISTS campaign_monsters (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    monster_id TEXT NOT NULL,

    -- Encounter generation
    encounter_weight INTEGER DEFAULT 1,
    min_party_level INTEGER DEFAULT 1,
    max_party_level INTEGER DEFAULT 20,

    -- Campaign-specific metadata
    environment_override TEXT,
    notes TEXT,
    variant_rules TEXT,
    is_boss INTEGER DEFAULT 0,

    -- Timestamps
    added_date TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (monster_id) REFERENCES monsters(id) ON DELETE CASCADE,
    UNIQUE(campaign_id, monster_id)
);

CREATE INDEX idx_campaign_monsters_campaign ON campaign_monsters(campaign_id);
CREATE INDEX idx_campaign_monsters_monster ON campaign_monsters(monster_id);
CREATE INDEX idx_campaign_monsters_level ON campaign_monsters(min_party_level, max_party_level);
CREATE INDEX idx_campaign_monsters_boss ON campaign_monsters(is_boss);

-- Example usage:
-- Get all monsters for Conan campaign at level 5:
-- SELECT m.* FROM monsters m
-- JOIN campaign_monsters cm ON m.id = cm.monster_id
-- WHERE cm.campaign_id = 'conan'
--   AND cm.min_party_level <= 5
--   AND cm.max_party_level >= 5
-- ORDER BY RANDOM()
-- LIMIT 1;

-- Get all campaigns using Shadow Demon:
-- SELECT campaign_id FROM campaign_monsters
-- WHERE monster_id = (SELECT id FROM monsters WHERE name = 'Shadow Demon');
