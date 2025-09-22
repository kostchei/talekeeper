-- Migration 011: Add Inspiration columns for Heroic Inspiration feature

-- Add inspiration columns to characters table
ALTER TABLE characters ADD COLUMN inspiration_uses_current INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN inspiration_uses_max INTEGER DEFAULT 0;

-- The migration system will track that this has been applied