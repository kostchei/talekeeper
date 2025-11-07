"""
Database Archiver for TaleKeeper Testing

Provides safe backup and restore functionality for the production database
during testing. Ensures tests can run against the real database while
maintaining the ability to restore to the original state.

Usage:
    # Archive before tests
    archive_path = DatabaseArchiver.archive("talekeeper.db")

    # Run tests...

    # Restore after tests
    DatabaseArchiver.unarchive(archive_path, "talekeeper.db")
"""

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json


class DatabaseArchiver:
    """Handles archiving and restoration of TaleKeeper database for testing."""

    ARCHIVE_DIR = Path(__file__).parent.parent / "archives"
    ARCHIVE_PREFIX = "talekeeper.db.archive"

    @classmethod
    def _ensure_archive_dir(cls) -> None:
        """Ensure the archive directory exists."""
        cls.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _get_timestamp(cls) -> str:
        """Get formatted timestamp for archive naming."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @classmethod
    def _verify_database_integrity(cls, db_path: str) -> bool:
        """
        Verify database integrity using SQLite's PRAGMA integrity_check.

        Args:
            db_path: Path to database file

        Returns:
            True if database is intact, False otherwise
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                return result[0] == "ok"
        except Exception as e:
            print(f"[ERROR] Database integrity check failed: {e}")
            return False

    @classmethod
    def _get_database_stats(cls, db_path: str) -> dict:
        """
        Get basic statistics about the database.

        Args:
            db_path: Path to database file

        Returns:
            Dictionary with table counts and other stats
        """
        stats = {
            "file_size_bytes": Path(db_path).stat().st_size,
            "tables": {},
        }

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Get all table names
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                tables = [row[0] for row in cursor.fetchall()]

                # Get row count for each table
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats["tables"][table] = count

        except Exception as e:
            print(f"[WARNING] Could not gather database stats: {e}")

        return stats

    @classmethod
    def archive(cls, db_path: str, description: Optional[str] = None) -> str:
        """
        Create an archived backup of the database.

        Args:
            db_path: Path to database to archive
            description: Optional description of this archive

        Returns:
            Path to the created archive file

        Raises:
            FileNotFoundError: If database file doesn't exist
            RuntimeError: If database fails integrity check
        """
        db_path_obj = Path(db_path)

        # Verify database exists
        if not db_path_obj.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        # Verify database integrity before archiving
        print(f"[INFO] Verifying database integrity: {db_path}")
        if not cls._verify_database_integrity(db_path):
            raise RuntimeError(f"Database failed integrity check: {db_path}")

        # Ensure archive directory exists
        cls._ensure_archive_dir()

        # Create archive filename with timestamp
        timestamp = cls._get_timestamp()
        archive_name = f"{cls.ARCHIVE_PREFIX}.{timestamp}"
        archive_path = cls.ARCHIVE_DIR / archive_name

        # Get database stats before archiving
        stats = cls._get_database_stats(db_path)

        # Copy database file
        print(f"[INFO] Creating archive: {archive_path}")
        shutil.copy2(db_path, archive_path)

        # Create metadata file
        metadata = {
            "timestamp": timestamp,
            "original_path": str(db_path_obj.absolute()),
            "archive_path": str(archive_path.absolute()),
            "description": description or "Test archive",
            "database_stats": stats,
        }

        metadata_path = archive_path.with_suffix(".json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"[SUCCESS] Archive created: {archive_path}")
        print(f"[INFO] Database size: {stats['file_size_bytes']:,} bytes")
        print(f"[INFO] Total tables: {len(stats['tables'])}")

        return str(archive_path)

    @classmethod
    def unarchive(cls, archive_path: str, target_db_path: str, force: bool = False) -> None:
        """
        Restore database from an archived backup.

        Args:
            archive_path: Path to archive file
            target_db_path: Path where database should be restored
            force: If True, overwrite existing database without confirmation

        Raises:
            FileNotFoundError: If archive doesn't exist
            RuntimeError: If archive fails integrity check or target exists and force=False
        """
        archive_path_obj = Path(archive_path)
        target_path_obj = Path(target_db_path)

        # Verify archive exists
        if not archive_path_obj.exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")

        # Verify archive integrity
        print(f"[INFO] Verifying archive integrity: {archive_path}")
        if not cls._verify_database_integrity(archive_path):
            raise RuntimeError(f"Archive failed integrity check: {archive_path}")

        # Check if target already exists
        if target_path_obj.exists() and not force:
            raise RuntimeError(
                f"Target database already exists: {target_db_path}. "
                f"Use force=True to overwrite."
            )

        # Load metadata if available
        metadata_path = archive_path_obj.with_suffix(".json")
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                print(f"[INFO] Archive metadata:")
                print(f"  Created: {metadata['timestamp']}")
                print(f"  Description: {metadata['description']}")

        # Copy archive to target location
        print(f"[INFO] Restoring database: {target_db_path}")
        shutil.copy2(archive_path, target_db_path)

        # Verify restored database
        if not cls._verify_database_integrity(target_db_path):
            raise RuntimeError(f"Restored database failed integrity check: {target_db_path}")

        print(f"[SUCCESS] Database restored: {target_db_path}")

    @classmethod
    def list_archives(cls) -> List[dict]:
        """
        List all available archives with their metadata.

        Returns:
            List of dictionaries containing archive information
        """
        cls._ensure_archive_dir()

        archives = []
        for archive_file in sorted(cls.ARCHIVE_DIR.glob(f"{cls.ARCHIVE_PREFIX}.*")):
            if archive_file.suffix != ".json":
                metadata_path = archive_file.with_suffix(".json")

                metadata = {"archive_path": str(archive_file)}
                if metadata_path.exists():
                    with open(metadata_path, "r") as f:
                        metadata.update(json.load(f))
                else:
                    # Basic info if metadata doesn't exist
                    metadata["timestamp"] = archive_file.stem.split(".")[-1]
                    metadata["file_size_bytes"] = archive_file.stat().st_size

                archives.append(metadata)

        return archives

    @classmethod
    def cleanup_old_archives(cls, keep_count: int = 10) -> int:
        """
        Remove old archives, keeping only the most recent ones.

        Args:
            keep_count: Number of recent archives to keep

        Returns:
            Number of archives deleted
        """
        archives = cls.list_archives()

        if len(archives) <= keep_count:
            return 0

        # Sort by timestamp (oldest first)
        archives.sort(key=lambda x: x.get("timestamp", ""))

        # Delete oldest archives
        to_delete = archives[: len(archives) - keep_count]
        deleted_count = 0

        for archive in to_delete:
            archive_path = Path(archive["archive_path"])
            metadata_path = archive_path.with_suffix(".json")

            try:
                archive_path.unlink()
                if metadata_path.exists():
                    metadata_path.unlink()
                deleted_count += 1
                print(f"[INFO] Deleted old archive: {archive_path.name}")
            except Exception as e:
                print(f"[WARNING] Could not delete archive: {e}")

        return deleted_count

    @classmethod
    def get_latest_archive(cls) -> Optional[str]:
        """
        Get the path to the most recent archive.

        Returns:
            Path to latest archive, or None if no archives exist
        """
        archives = cls.list_archives()
        if not archives:
            return None

        # Sort by timestamp (newest first)
        archives.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return archives[0]["archive_path"]


# Convenience context manager for testing
class TemporaryDatabaseRestore:
    """
    Context manager that archives the database, runs code, then restores it.

    Usage:
        with TemporaryDatabaseRestore("talekeeper.db") as db_path:
            # Make changes to database during testing
            pass
        # Database is automatically restored after exiting the context
    """

    def __init__(self, db_path: str, description: Optional[str] = None):
        self.db_path = db_path
        self.description = description or "Temporary test archive"
        self.archive_path = None

    def __enter__(self) -> str:
        """Create archive and return database path."""
        self.archive_path = DatabaseArchiver.archive(self.db_path, self.description)
        return self.db_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore database from archive."""
        if self.archive_path:
            try:
                DatabaseArchiver.unarchive(self.archive_path, self.db_path, force=True)
                # Optionally clean up the temporary archive
                archive_path_obj = Path(self.archive_path)
                metadata_path = archive_path_obj.with_suffix(".json")
                archive_path_obj.unlink()
                if metadata_path.exists():
                    metadata_path.unlink()
                print(f"[INFO] Cleaned up temporary archive: {archive_path_obj.name}")
            except Exception as e:
                print(f"[ERROR] Failed to restore database: {e}")
                raise


if __name__ == "__main__":
    # Simple test/demo
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python database_archiver.py archive <db_path>")
        print("  python database_archiver.py unarchive <archive_path> <target_db_path>")
        print("  python database_archiver.py list")
        print("  python database_archiver.py cleanup [keep_count]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "archive":
        if len(sys.argv) < 3:
            print("Error: Missing database path")
            sys.exit(1)
        archive_path = DatabaseArchiver.archive(sys.argv[2])
        print(f"\nArchive created: {archive_path}")

    elif command == "unarchive":
        if len(sys.argv) < 4:
            print("Error: Missing archive_path or target_db_path")
            sys.exit(1)
        DatabaseArchiver.unarchive(sys.argv[2], sys.argv[3], force=True)

    elif command == "list":
        archives = DatabaseArchiver.list_archives()
        if not archives:
            print("No archives found.")
        else:
            print(f"\nFound {len(archives)} archive(s):\n")
            for i, archive in enumerate(archives, 1):
                print(f"{i}. {Path(archive['archive_path']).name}")
                print(f"   Timestamp: {archive.get('timestamp', 'unknown')}")
                print(f"   Description: {archive.get('description', 'N/A')}")
                print(f"   Size: {archive.get('file_size_bytes', 0):,} bytes")
                print()

    elif command == "cleanup":
        keep_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        deleted = DatabaseArchiver.cleanup_old_archives(keep_count)
        print(f"\nDeleted {deleted} old archive(s), kept {keep_count} most recent.")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
