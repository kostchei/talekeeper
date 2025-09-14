-- Migration 013: Add accessory equipment slots
-- Adds additional equipment columns for accessories
ALTER TABLE characters ADD COLUMN equipment_helmet TEXT DEFAULT NULL;
ALTER TABLE characters ADD COLUMN equipment_gloves TEXT DEFAULT NULL;
ALTER TABLE characters ADD COLUMN equipment_boots TEXT DEFAULT NULL;
ALTER TABLE characters ADD COLUMN equipment_cloak TEXT DEFAULT NULL;
ALTER TABLE characters ADD COLUMN equipment_ring_1 TEXT DEFAULT NULL;
ALTER TABLE characters ADD COLUMN equipment_ring_2 TEXT DEFAULT NULL;
ALTER TABLE characters ADD COLUMN equipment_amulet TEXT DEFAULT NULL;
