-- Migration 046: Enable WAL Mode for Better Concurrency
-- Addresses: Database locking issues during concurrent operations

-- ============================================================================
-- WHAT IS WAL MODE?
-- ============================================================================
-- Write-Ahead Logging (WAL) is an alternative journaling mode for SQLite that
-- provides significant benefits for applications with concurrent access:
--
-- 1. Multiple readers can access the database simultaneously
-- 2. One writer can work concurrently with readers (no blocking)
-- 3. Better performance (up to 2x faster for write operations)
-- 4. More robust handling of concurrent access
--
-- ============================================================================
-- HOW IT WORKS
-- ============================================================================
-- Instead of writing changes directly to the database file, WAL mode writes
-- changes to a separate write-ahead log (WAL) file. This allows:
-- - Readers to continue accessing the main database file
-- - Writers to append changes to the WAL file
-- - Periodic checkpointing to merge WAL changes back to main file
--
-- ============================================================================
-- FILES CREATED
-- ============================================================================
-- When WAL mode is enabled, SQLite creates two additional files:
-- - talekeeper.db-wal  (Write-Ahead Log file)
-- - talekeeper.db-shm  (Shared memory file for coordination)
--
-- These files are automatically managed by SQLite and should NOT be deleted.
--
-- ============================================================================
-- BENEFITS FOR TALEKEEPER
-- ============================================================================
-- - Eliminates "database is locked" errors during level-up operations
-- - Allows UI to read character data while background services write
-- - Faster combat log writes without blocking character sheet updates
-- - Better performance for inventory operations
--
-- ============================================================================

-- Enable Write-Ahead Logging mode
PRAGMA journal_mode=WAL;

-- Set synchronous mode to NORMAL (safe with WAL, faster than FULL)
PRAGMA synchronous=NORMAL;

-- Set busy timeout to 5 seconds (wait for locks instead of failing immediately)
PRAGMA busy_timeout=5000;

-- Optional: Configure WAL auto-checkpoint (checkpoint every 1000 pages)
PRAGMA wal_autocheckpoint=1000;

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- To verify WAL mode is enabled, run:
--   PRAGMA journal_mode;
-- Should return: wal
--
-- ============================================================================
-- REVERTING (NOT RECOMMENDED)
-- ============================================================================
-- To revert to rollback journal mode (not recommended):
--   PRAGMA journal_mode=DELETE;
--
-- ============================================================================
