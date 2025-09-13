-- Migration: Add available classes configuration to campaigns table
-- This allows campaign frames to specify which classes are available for character creation

-- Add available_classes column to campaigns table
ALTER TABLE campaigns ADD COLUMN available_classes TEXT DEFAULT NULL;

-- Update existing campaigns with default available classes (your specified list)
UPDATE campaigns SET available_classes = '["barbarian", "fighter", "rogue", "paladin", "cleric", "warlock", "wizard"]' WHERE available_classes IS NULL;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_campaigns_available_classes ON campaigns(available_classes);