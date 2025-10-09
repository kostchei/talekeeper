-- Migration 015b: Warlock Class Enhancements
-- DEPRECATED: This migration is no longer needed
-- All enhancements have been merged into migration 015_warlock_class.sql
-- This file is kept for historical reference only

-- If you need to apply warlock enhancements:
-- 1. Use migration 015_warlock_class.sql (complete version)
-- 2. Use migration 015c_warlock_spell_list.sql (spell list only)

-- Note: This migration was created when migration 015 was incomplete
-- Migration 015 has now been updated to include all necessary columns and tables
-- Applying this migration on a fresh database is not needed

-- Original content was:
-- - warlock_patron_features table
-- - Fiend patron features
-- - Additional invocations
-- - Prerequisite corrections

-- All of the above are now in migration 015
