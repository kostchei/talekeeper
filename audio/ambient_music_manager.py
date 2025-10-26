"""Ambient music manager with random bag playlist system."""

from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from .midi_player import MidiPlayer

LOGGER = logging.getLogger(__name__)


class AmbientMusicManager(QObject):
    """Manages ambient music playback using random bag shuffle algorithm.

    The random bag ensures all tracks play once before any track repeats,
    providing variety while avoiding repetition.
    """

    playlist_shuffled = pyqtSignal()
    playlist_empty = pyqtSignal()
    track_changed = pyqtSignal(Path)

    def __init__(
        self,
        midi_player: MidiPlayer,
        campaign_name: str = "golden",
        parent: Optional[QObject] = None,
    ) -> None:
        """Initialize ambient music manager.

        Args:
            midi_player: The MIDI player to use for playback
            campaign_name: Name of campaign folder to load music from
            parent: Parent QObject
        """
        super().__init__(parent)

        self.midi_player = midi_player
        self.campaign_name = campaign_name

        # Random bag state
        self.all_tracks: list[Path] = []
        self.current_bag: list[Path] = []
        self.enabled = False

        # Connect to MIDI player signals
        self.midi_player.playback_finished.connect(self._on_track_finished)

        # Load tracks from campaign folder
        self._load_tracks()

    def _load_tracks(self) -> None:
        """Load all MIDI tracks from campaign ambient folder."""
        # Look for campaign ambient folder
        base_path = Path(__file__).parent / "midi" / "campaigns" / self.campaign_name / "ambient"

        if not base_path.exists():
            LOGGER.warning(f"Campaign ambient folder not found: {base_path}")
            return

        # Load all .mid files
        midi_files = list(base_path.glob("*.mid"))

        if not midi_files:
            LOGGER.warning(f"No MIDI files found in {base_path}")
            return

        self.all_tracks = midi_files
        LOGGER.info(f"Loaded {len(self.all_tracks)} ambient tracks from {self.campaign_name}")

        # Initialize the bag
        self._refill_bag()

    def _refill_bag(self) -> None:
        """Refill and shuffle the random bag with all tracks."""
        if not self.all_tracks:
            LOGGER.warning("No tracks available to refill bag")
            self.playlist_empty.emit()
            return

        self.current_bag = self.all_tracks.copy()
        random.shuffle(self.current_bag)

        LOGGER.info(f"Shuffled {len(self.current_bag)} tracks into playlist")
        self.playlist_shuffled.emit()

    def set_campaign(self, campaign_name: str) -> None:
        """Switch to a different campaign's music.

        Args:
            campaign_name: Name of campaign folder
        """
        was_playing = self.enabled

        # Stop current playback
        if was_playing:
            self.stop()

        self.campaign_name = campaign_name
        self.all_tracks.clear()
        self.current_bag.clear()

        # Load new tracks
        self._load_tracks()

        # Resume playback if it was playing
        if was_playing and self.all_tracks:
            self.start()

    def start(self) -> None:
        """Start ambient music playback."""
        if not self.all_tracks:
            LOGGER.warning("Cannot start ambient music: no tracks loaded")
            return

        self.enabled = True

        # If MIDI player is idle, start playing
        if self.midi_player.get_queue_size() == 0 and self.midi_player.current_file is None:
            self._play_next()

        LOGGER.info("Ambient music started")

    def stop(self) -> None:
        """Stop ambient music playback."""
        self.enabled = False
        self.midi_player.stop()
        self.midi_player.clear_queue()
        LOGGER.info("Ambient music stopped")

    def skip(self) -> None:
        """Skip to next track."""
        if not self.enabled:
            LOGGER.debug("Ambient music not enabled; cannot skip")
            return

        self.midi_player.stop()
        self._play_next()

    def _play_next(self) -> None:
        """Play the next track from the random bag."""
        if not self.enabled:
            return

        # Check if bag is empty
        if not self.current_bag:
            LOGGER.debug("Bag empty, reshuffling...")
            self._refill_bag()

        # Get next track from bag
        if self.current_bag:
            next_track = self.current_bag.pop(0)
            LOGGER.info(f"Playing ambient: {next_track.name} ({len(self.current_bag)} remaining in bag)")

            self.midi_player.enqueue(next_track)
            self.track_changed.emit(next_track)

    def _on_track_finished(self, finished_track: Path) -> None:
        """Handle when a track finishes playing.

        Args:
            finished_track: Path to the track that just finished
        """
        if not self.enabled:
            return

        # Only auto-play next if this was an ambient track
        if finished_track in self.all_tracks:
            LOGGER.debug(f"Ambient track finished: {finished_track.name}")
            self._play_next()

    def get_remaining_count(self) -> int:
        """Get number of tracks remaining in current bag.

        Returns:
            Number of unplayed tracks before reshuffle
        """
        return len(self.current_bag)

    def get_total_count(self) -> int:
        """Get total number of tracks available.

        Returns:
            Total number of ambient tracks
        """
        return len(self.all_tracks)

    def is_playing(self) -> bool:
        """Check if ambient music is currently playing.

        Returns:
            True if enabled and playing
        """
        return self.enabled
