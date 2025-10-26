"""MIDI playback manager using meltysynth for authentic DOS-era sound."""

from __future__ import annotations

import io
import logging
import struct
import wave
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, QObject, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

from . import meltysynth as ms

LOGGER = logging.getLogger(__name__)


class MidiPlayer(QObject):
    """Manages MIDI playback with OPL3 soundfont synthesis."""

    playback_started = pyqtSignal(Path)
    playback_finished = pyqtSignal(Path)
    playback_error = pyqtSignal(str)
    queue_changed = pyqtSignal(int)

    def __init__(
        self,
        soundfont_path: Optional[Path] = None,
        parent: Optional[QObject] = None,
    ) -> None:
        """Initialize MIDI player with soundfont.

        Args:
            soundfont_path: Path to .sf2 soundfont file.
                          Defaults to audio/soundfonts/OPL-3_FM_128M.sf2
            parent: Parent QObject
        """
        super().__init__(parent)

        # Set default soundfont path
        if soundfont_path is None:
            soundfont_path = Path(__file__).parent / "soundfonts" / "OPL-3_FM_128M.sf2"

        self.soundfont_path = soundfont_path
        self.sound_font: Optional[ms.SoundFont] = None

        # Qt audio player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.errorOccurred.connect(self._on_error)

        self.queue: list[Path] = []
        self.current_file: Optional[Path] = None
        self.enabled = True
        self._volume = 0.5

        self.audio_output.setVolume(self._volume)

        # Load soundfont
        self._load_soundfont()

    def _load_soundfont(self) -> None:
        """Load the soundfont file."""
        try:
            if not self.soundfont_path.exists():
                LOGGER.error(f"Soundfont not found: {self.soundfont_path}")
                return

            LOGGER.info(f"Loading soundfont: {self.soundfont_path.name}")
            self.sound_font = ms.SoundFont.from_file(str(self.soundfont_path))
            LOGGER.info("Soundfont loaded successfully")

        except Exception as e:
            LOGGER.error(f"Failed to load soundfont: {e}")
            self.sound_font = None

    def set_volume(self, volume: float) -> None:
        """Set playback volume (0.0 to 1.0)."""
        self._volume = max(0.0, min(1.0, volume))
        self.audio_output.setVolume(self._volume)
        LOGGER.debug(f"MIDI volume set to {self._volume * 100:.0f}%")

    def get_volume(self) -> float:
        """Get current volume (0.0 to 1.0)."""
        return self._volume

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable MIDI playback."""
        self.enabled = enabled
        if not enabled:
            self.stop()
            self.queue.clear()
            self.queue_changed.emit(0)
        LOGGER.info(f"MIDI playback {'enabled' if enabled else 'disabled'}")

    def is_enabled(self) -> bool:
        """Check if MIDI playback is enabled."""
        return self.enabled

    def enqueue(self, midi_file: Path) -> None:
        """Add a MIDI file to the playback queue."""
        if not self.enabled:
            LOGGER.debug(f"MIDI playback disabled; skipping {midi_file.name}")
            return

        if not midi_file.exists():
            LOGGER.warning(f"MIDI file does not exist: {midi_file}")
            return

        if self.sound_font is None:
            LOGGER.error("Cannot play MIDI: soundfont not loaded")
            return

        self.queue.append(midi_file)
        self.queue_changed.emit(len(self.queue))
        LOGGER.debug(f"Queued MIDI: {midi_file.name} (queue size: {len(self.queue)})")

        if self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            self._play_next()

    def stop(self) -> None:
        """Stop current playback."""
        if self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self.player.stop()
            LOGGER.debug("Stopped MIDI playback")

    def clear_queue(self) -> None:
        """Clear the playback queue."""
        self.queue.clear()
        self.queue_changed.emit(0)
        LOGGER.debug("Cleared MIDI queue")

    def get_queue_size(self) -> int:
        """Get number of items in queue."""
        return len(self.queue)

    def _render_midi_to_wav(self, midi_path: Path) -> Optional[QByteArray]:
        """Render MIDI file to WAV data in memory.

        Args:
            midi_path: Path to MIDI file

        Returns:
            QByteArray containing WAV data, or None on error
        """
        try:
            # Load the MIDI file
            midi_file = ms.MidiFile.from_file(str(midi_path))

            # Create synthesizer
            settings = ms.SynthesizerSettings(44100)
            synthesizer = ms.Synthesizer(self.sound_font, settings)

            # Create sequencer
            sequencer = ms.MidiFileSequencer(synthesizer)
            sequencer.play(midi_file, False)

            # Calculate buffer size
            sample_count = int(settings.sample_rate * midi_file.length)

            # Create output buffers
            left = ms.create_buffer(sample_count)
            right = ms.create_buffer(sample_count)

            # Render audio
            LOGGER.debug(f"Rendering {midi_file.length:.1f}s of MIDI audio...")
            sequencer.render(left, right)

            # Convert to WAV format
            wav_data = self._create_wav_data(left, right, settings.sample_rate)

            return QByteArray(wav_data)

        except Exception as e:
            LOGGER.error(f"Failed to render MIDI {midi_path.name}: {e}")
            return None

    def _create_wav_data(
        self,
        left: list[float],
        right: list[float],
        sample_rate: int
    ) -> bytes:
        """Create WAV file data from stereo audio buffers.

        Args:
            left: Left channel samples
            right: Right channel samples
            sample_rate: Sample rate in Hz

        Returns:
            WAV file bytes
        """
        # Create in-memory WAV file
        wav_buffer = io.BytesIO()

        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            # Interleave samples and convert float to int16
            for l, r in zip(left, right):
                # Clamp and convert to 16-bit signed integer
                l_int = max(-32768, min(32767, int(l * 32767)))
                r_int = max(-32768, min(32767, int(r * 32767)))
                wav_file.writeframes(struct.pack('<hh', l_int, r_int))

        return wav_buffer.getvalue()

    def _play_next(self) -> None:
        """Play the next file in the queue."""
        if not self.queue:
            self.current_file = None
            return

        next_file = self.queue.pop(0)
        self.current_file = next_file
        self.queue_changed.emit(len(self.queue))

        # Render MIDI to WAV
        wav_data = self._render_midi_to_wav(next_file)
        if wav_data is None:
            # Skip to next on error
            self._play_next()
            return

        # Create QBuffer to hold WAV data
        buffer = QBuffer()
        buffer.setData(wav_data)
        buffer.open(QIODevice.OpenModeFlag.ReadOnly)

        # Set the buffer as the media source
        self.player.setSourceDevice(buffer, QUrl())
        self.player.play()

        LOGGER.info(f"Playing MIDI: {next_file.name}")
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
        LOGGER.error(f"MIDI playback error: {error_string}")
        self.playback_error.emit(error_string)
        self.current_file = None
        if self.queue and self.enabled:
            self._play_next()
