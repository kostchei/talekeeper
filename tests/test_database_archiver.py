"""
Tests for Database Archiver

Tests the archive/unarchive functionality to ensure safe backup
and restoration of the TaleKeeper database.
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from tests.helpers.database_archiver import DatabaseArchiver, TemporaryDatabaseRestore


@pytest.fixture
def temp_db():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Create a simple schema
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE test_characters (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                level INTEGER DEFAULT 1
            )
        """)
        cursor.execute(
            "INSERT INTO test_characters (name, level) VALUES (?, ?)", ("TestChar", 5)
        )
        conn.commit()

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def cleanup_archives():
    """Cleanup any test archives after tests."""
    yield
    # Clean up any archives created during testing
    archive_dir = DatabaseArchiver.ARCHIVE_DIR
    if archive_dir.exists():
        for archive in archive_dir.glob("talekeeper.db.archive.*"):
            try:
                archive.unlink()
            except:
                pass


def test_archive_creates_backup(temp_db, cleanup_archives):
    """Test that archive creates a valid backup file."""
    archive_path = DatabaseArchiver.archive(temp_db, description="Test backup")

    # Verify archive exists
    assert Path(archive_path).exists(), "Archive file should exist"

    # Verify metadata exists
    metadata_path = Path(archive_path).with_suffix(".json")
    assert metadata_path.exists(), "Metadata file should exist"

    # Verify archive has same data
    with sqlite3.connect(archive_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, level FROM test_characters")
        result = cursor.fetchone()
        assert result == ("TestChar", 5), "Archive should contain original data"


def test_archive_verifies_integrity(temp_db, cleanup_archives):
    """Test that archive verifies database integrity."""
    # This should succeed with a valid database
    archive_path = DatabaseArchiver.archive(temp_db)
    assert Path(archive_path).exists()


def test_archive_fails_on_missing_file(cleanup_archives):
    """Test that archive raises error for non-existent database."""
    with pytest.raises(FileNotFoundError):
        DatabaseArchiver.archive("nonexistent.db")


def test_unarchive_restores_database(temp_db, cleanup_archives):
    """Test that unarchive correctly restores database."""
    # Create archive
    archive_path = DatabaseArchiver.archive(temp_db, description="Test restore")

    # Modify original database
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE test_characters SET level = 10")
        conn.commit()

    # Verify modification
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM test_characters")
        assert cursor.fetchone()[0] == 10, "Database should be modified"

    # Restore from archive
    DatabaseArchiver.unarchive(archive_path, temp_db, force=True)

    # Verify restoration
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM test_characters")
        assert cursor.fetchone()[0] == 5, "Database should be restored to original state"


def test_unarchive_fails_on_missing_archive(temp_db, cleanup_archives):
    """Test that unarchive raises error for non-existent archive."""
    with pytest.raises(FileNotFoundError):
        DatabaseArchiver.unarchive("nonexistent_archive.db", temp_db)


def test_unarchive_requires_force_for_existing_db(temp_db, cleanup_archives):
    """Test that unarchive requires force flag to overwrite existing database."""
    archive_path = DatabaseArchiver.archive(temp_db)

    # Should fail without force flag
    with pytest.raises(RuntimeError, match="already exists"):
        DatabaseArchiver.unarchive(archive_path, temp_db, force=False)

    # Should succeed with force flag
    DatabaseArchiver.unarchive(archive_path, temp_db, force=True)


def test_list_archives(temp_db, cleanup_archives):
    """Test that list_archives returns all archives with metadata."""
    # Create multiple archives
    archive1 = DatabaseArchiver.archive(temp_db, description="First archive")
    archive2 = DatabaseArchiver.archive(temp_db, description="Second archive")

    # List archives
    archives = DatabaseArchiver.list_archives()

    assert len(archives) >= 2, "Should find at least 2 archives"

    # Verify archives have metadata
    for archive in archives:
        assert "archive_path" in archive
        assert "timestamp" in archive


def test_get_latest_archive(temp_db, cleanup_archives):
    """Test that get_latest_archive returns the most recent archive."""
    # Create multiple archives
    archive1 = DatabaseArchiver.archive(temp_db, description="First")
    archive2 = DatabaseArchiver.archive(temp_db, description="Second (latest)")

    latest = DatabaseArchiver.get_latest_archive()

    assert latest == archive2, "Should return the most recent archive"


def test_cleanup_old_archives(temp_db, cleanup_archives):
    """Test that cleanup removes old archives while keeping recent ones."""
    # Create several archives
    archives = []
    for i in range(5):
        archive = DatabaseArchiver.archive(temp_db, description=f"Archive {i}")
        archives.append(archive)

    # Keep only 3 most recent
    deleted = DatabaseArchiver.cleanup_old_archives(keep_count=3)

    assert deleted == 2, "Should delete 2 old archives"

    remaining = DatabaseArchiver.list_archives()
    assert len(remaining) == 3, "Should have 3 archives remaining"


def test_temporary_restore_context_manager(temp_db, cleanup_archives):
    """Test the TemporaryDatabaseRestore context manager."""
    # Get original data
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM test_characters")
        original_level = cursor.fetchone()[0]

    # Use context manager to modify database
    with TemporaryDatabaseRestore(temp_db, description="Temporary test change"):
        # Modify database
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE test_characters SET level = 99")
            conn.commit()

        # Verify modification
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level FROM test_characters")
            assert cursor.fetchone()[0] == 99, "Database should be modified inside context"

    # After context exits, database should be restored
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM test_characters")
        restored_level = cursor.fetchone()[0]

    assert (
        restored_level == original_level
    ), "Database should be restored to original state after context exit"


def test_database_stats_collection(temp_db, cleanup_archives):
    """Test that database stats are collected correctly."""
    archive_path = DatabaseArchiver.archive(temp_db)

    # Load metadata
    metadata_path = Path(archive_path).with_suffix(".json")
    import json

    with open(metadata_path) as f:
        metadata = json.load(f)

    stats = metadata["database_stats"]

    assert "file_size_bytes" in stats, "Should include file size"
    assert "tables" in stats, "Should include table information"
    assert "test_characters" in stats["tables"], "Should list test_characters table"
    assert stats["tables"]["test_characters"] == 1, "Should count 1 row in test_characters"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
