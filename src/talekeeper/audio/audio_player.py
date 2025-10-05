"""Audio playback manager for narration files."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

LOGGER = logging.getLogger(__name__)


class NarrationPlayer(QObject):
    """Manages playback queue for narration audio files."""

    playback_started = pyqtSignal(Path)
    playback_finished = pyqtSignal(Path)
    playback_error = pyqtSignal(str)
    queue_changed = pyqtSignal(int)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.errorOccurred.connect(self._on_error)

        self.queue: list[Path] = []
        self.current_file: Optional[Path] = None
        self.enabled = True
        self._volume = 0.7

        self.audio_output.setVolume(self._volume)

    def set_volume(self, volume: float) -> None:
        """Set playback volume (0.0 to 1.0)."""
        self._volume = max(0.0, min(1.0, volume))
        self.audio_output.setVolume(self._volume)
        LOGGER.debug(f"Narration volume set to {self._volume * 100:.0f}%")

    def get_volume(self) -> float:
        """Get current volume (0.0 to 1.0)."""
        return self._volume

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable narration playback."""
        self.enabled = enabled
        if not enabled:
            self.stop()
            self.queue.clear()
            self.queue_changed.emit(0)
        LOGGER.info(f"Narration playback {'enabled' if enabled else 'disabled'}")

    def is_enabled(self) -> bool:
        """Check if narration is enabled."""
        return self.enabled

    def enqueue(self, audio_file: Path) -> None:
        """Add an audio file to the playback queue."""
        if not self.enabled:
            LOGGER.debug(f"Narration disabled; skipping {audio_file.name}")
            return

        if not audio_file.exists():
            LOGGER.warning(f"Audio file does not exist: {audio_file}")
            return

        self.queue.append(audio_file)
        self.queue_changed.emit(len(self.queue))
        LOGGER.debug(f"Queued narration: {audio_file.name} (queue size: {len(self.queue)})")

        if self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            self._play_next()

    def stop(self) -> None:
        """Stop current playback."""
        if self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self.player.stop()
            LOGGER.debug("Stopped narration playback")

    def clear_queue(self) -> None:
        """Clear the playback queue."""
        self.queue.clear()
        self.queue_changed.emit(0)
        LOGGER.debug("Cleared narration queue")

    def get_queue_size(self) -> int:
        """Get number of items in queue."""
        return len(self.queue)

    def _play_next(self) -> None:
        """Play the next file in the queue."""
        if not self.queue:
            self.current_file = None
            return

        next_file = self.queue.pop(0)
        self.current_file = next_file
        self.queue_changed.emit(len(self.queue))

        file_url = QUrl.fromLocalFile(str(next_file.absolute()))
        self.player.setSource(file_url)
        self.player.play()

        LOGGER.info(f"Playing narration: {next_file.name}")
        self.playback_started.emit(next_file)

    def _on_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        """Handle playback state changes."""
        if state == QMediaPlayer.PlaybackState.StoppedState:
            if self.current_file:
                LOGGER.debug(f"Finished playing: {self.current_file.name}")
                self.playback_finished.emit(self.current_file)
                self.current_file = None

            if self.queue and self.enabled:
                self._play_next()

    def _on_error(self, error: QMediaPlayer.Error, error_string: str) -> None:
        """Handle playback errors."""
        LOGGER.error(f"Narration playback error: {error_string}")
        self.playback_error.emit(error_string)
        self.current_file = None
        if self.queue and self.enabled:
            self._play_next()
