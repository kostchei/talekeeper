-- Migration 020: Add Paladin's Smite Resource Tracking
-- D&D 2024 gives paladins a free Divine Smite once per long rest (Level 2+)

-- Add free Divine Smite tracking to paladin_features
ALTER TABLE paladin_features ADD COLUMN free_divine_smite_used BOOLEAN DEFAULT FALSE;
ALTER TABLE paladin_features ADD COLUMN free_divine_smite_last_reset TEXT;