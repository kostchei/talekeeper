-- Migration 012: Add belt equipment slot
-- This migration adds the equipment_belt column to the characters table

ALTER TABLE characters ADD COLUMN equipment_belt TEXT DEFAULT NULL;