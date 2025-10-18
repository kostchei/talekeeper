-- Migration 035: Add gold column to characters table

ALTER TABLE characters ADD COLUMN gold INTEGER DEFAULT 0;
