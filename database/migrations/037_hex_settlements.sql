ALTER TABLE character_hex_map ADD COLUMN settlement_type TEXT;

CREATE INDEX IF NOT EXISTS idx_hex_settlement
ON character_hex_map(character_id, settlement_type);
