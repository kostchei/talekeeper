# core
# category: utility
"""Automatic cleanup of old narration audio files."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

LOGGER = logging.getLogger(__name__)


class NarrationFileCleanup:
    """Manages automatic cleanup of generated narration files."""

    def __init__(
        self,
        output_directory: Path,
        max_age_hours: int = 24,
        max_files: Optional[int] = 500,
    ) -> None:
        self.output_directory = Path(output_directory)
        self.max_age_hours = max_age_hours
        self.max_files = max_files

    def cleanup_old_files(self) -> int:
        """Delete narration files older than max_age_hours."""
        if not self.output_directory.exists():
            return 0

        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        deleted_count = 0

        for audio_file in self.output_directory.glob("*.wav"):
            try:
                file_mtime = datetime.fromtimestamp(audio_file.stat().st_mtime)
                if file_mtime < cutoff_time:
                    audio_file.unlink()
                    deleted_count += 1
                    LOGGER.debug(f"Deleted old narration file: {audio_file.name}")
            except Exception as exc:
                LOGGER.warning(f"Failed to delete {audio_file.name}: {exc}")

        if deleted_count > 0:
            LOGGER.info(f"Cleaned up {deleted_count} old narration files")

        return deleted_count

    def cleanup_excess_files(self) -> int:
        """Delete oldest files if count exceeds max_files."""
        if self.max_files is None or not self.output_directory.exists():
            return 0

        audio_files = list(self.output_directory.glob("*.wav"))
        if len(audio_files) <= self.max_files:
            return 0

        audio_files.sort(key=lambda f: f.stat().st_mtime)
        excess_count = len(audio_files) - self.max_files
        deleted_count = 0

        for audio_file in audio_files[:excess_count]:
            try:
                audio_file.unlink()
                deleted_count += 1
                LOGGER.debug(f"Deleted excess narration file: {audio_file.name}")
            except Exception as exc:
                LOGGER.warning(f"Failed to delete {audio_file.name}: {exc}")

        if deleted_count > 0:
            LOGGER.info(f"Cleaned up {deleted_count} excess narration files")

        return deleted_count

    def run_cleanup(self) -> dict[str, int]:
        """Run both age-based and count-based cleanup."""
        old_files = self.cleanup_old_files()
        excess_files = self.cleanup_excess_files()

        return {
            "old_files_deleted": old_files,
            "excess_files_deleted": excess_files,
            "total_deleted": old_files + excess_files,
        }
