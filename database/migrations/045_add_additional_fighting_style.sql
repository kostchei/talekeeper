-- Migration 045: Add additional_fighting_style column to fighter_features
-- Addresses: Champion's level 7 additional fighting style not being stored in DB

PRAGMA foreign_keys = OFF;

-- Add additional_fighting_style column to fighter_features table
ALTER TABLE fighter_features ADD COLUMN additional_fighting_style TEXT DEFAULT NULL;

-- Add comment for documentation
-- This column stores the Champion's additional fighting style selected at level 7
-- Examples: 'defense', 'dueling', 'archery', 'great_weapon_fighting', etc.

PRAGMA foreign_keys = ON;
