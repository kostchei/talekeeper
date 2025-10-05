-- Add Lucky feat usage tracking columns
ALTER TABLE characters ADD COLUMN lucky_uses_current INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN lucky_uses_max INTEGER DEFAULT 0;