"""MIDI playback manager using QAudioSink for direct PCM playback."""

from __future__ import annotations

import logging
import struct
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QByteArray, QBuffer, QIODevice, QObject, QTimer, pyqtSignal
from PyQt6.QtMultimedia import QAudio, QAudioFormat, QAudioSink, QMediaDevices

from . import meltysynth as ms

LOGGER = logging.getLogger(__name__)


class MidiPlayer(QObject):
    """Manages MIDI playback with OPL3 soundfont synthesis using QAudioSink."""

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

        # Audio format setup (44.1kHz, 16-bit, stereo)
        self.audio_format = QAudioFormat()
        self.audio_format.setSampleRate(44100)
        self.audio_format.setChannelCount(2)
        self.audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        # Audio sink
        self.audio_sink: Optional[QAudioSink] = None
        self.audio_buffer: Optional[QBuffer] = None
        self.audio_data: Optional[QByteArray] = None

        # Playback state
        self.queue: list[Path] = []
        self.current_file: Optional[Path] = None
        self.enabled = True
        self._volume = 0.5

        # Timer to check playback state
        self.state_timer = QTimer(self)
        self.state_timer.timeout.connect(self._check_playback_state)
        self.state_timer.setInterval(100)  # Check every 100ms

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
        if self.audio_sink:
            self.audio_sink.setVolume(self._volume)
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

        if not self._is_playing():
            self._play_next()

    def stop(self) -> None:
        """Stop current playback."""
        if self.audio_sink:
            self.audio_sink.stop()
            self.state_timer.stop()
            LOGGER.debug("Stopped MIDI playback")

    def clear_queue(self) -> None:
        """Clear the playback queue."""
        self.queue.clear()
        self.queue_changed.emit(0)
        LOGGER.debug("Cleared MIDI queue")

    def get_queue_size(self) -> int:
        """Get number of items in queue."""
        return len(self.queue)

    def _is_playing(self) -> bool:
        """Check if currently playing."""
        return self.audio_sink is not None and self.audio_sink.state() != QAudio.State.StoppedState

    def _render_midi_to_pcm(self, midi_path: Path) -> Optional[QByteArray]:
        """Render MIDI file to raw PCM data.

        Args:
            midi_path: Path to MIDI file

        Returns:
            QByteArray containing raw PCM data, or None on error
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

            # Convert to raw PCM (16-bit stereo interleaved)
            pcm_data = self._create_pcm_data(left, right)

            return QByteArray(pcm_data)

        except Exception as e:
            LOGGER.error(f"Failed to render MIDI {midi_path.name}: {e}")
            return None

    def _create_pcm_data(self, left: list[float], right: list[float]) -> bytes:
        """Create raw PCM data from stereo audio buffers.

        Args:
            left: Left channel samples
            right: Right channel samples

        Returns:
            Raw PCM bytes (16-bit signed, interleaved stereo)
        """
        pcm_buffer = bytearray()

        # Interleave samples and convert float to int16
        for l, r in zip(left, right):
            # Clamp and convert to 16-bit signed integer
            l_int = max(-32768, min(32767, int(l * 32767)))
            r_int = max(-32768, min(32767, int(r * 32767)))
            pcm_buffer.extend(struct.pack('<hh', l_int, r_int))

        return bytes(pcm_buffer)

    def _play_next(self) -> None:
        """Play the next file in the queue."""
        if not self.queue:
            self.current_file = None
            return

        next_file = self.queue.pop(0)
        self.current_file = next_file
        self.queue_changed.emit(len(self.queue))

        # Render MIDI to PCM
        pcm_data = self._render_midi_to_pcm(next_file)
        if pcm_data is None:
            # Skip to next on error
            self._play_next()
            return

        # Store data and create buffer
        self.audio_data = pcm_data
        self.audio_buffer = QBuffer(self.audio_data, self)
        self.audio_buffer.open(QIODevice.OpenModeFlag.ReadOnly)

        # Create audio sink
        default_device = QMediaDevices.defaultAudioOutput()
        self.audio_sink = QAudioSink(default_device, self.audio_format, self)
        self.audio_sink.setVolume(self._volume)

        # Start playback
        self.audio_sink.start(self.audio_buffer)

        # Start monitoring playback state
        self.state_timer.start()

        LOGGER.info(f"Playing MIDI: {next_file.name}")
        self.playback_started.emit(next_file)

    def _check_playback_state(self) -> None:
        """Check if playback has finished."""
        if self.audio_sink is None:
            self.state_timer.stop()
            return

        # Check if playback is done
        if self.audio_sink.state() == QAudio.State.IdleState:
            self._on_playback_finished()

    def _on_playback_finished(self) -> None:
        """Handle playback finished."""
        self.state_timer.stop()

        if self.current_file:
            LOGGER.debug(f"Finished playing: {self.current_file.name}")
            self.playback_finished.emit(self.current_file)

        # Cleanup
        if self.audio_sink:
            self.audio_sink.stop()
            self.audio_sink.deleteLater()
            self.audio_sink = None

        if self.audio_buffer:
            self.audio_buffer.close()
            self.audio_buffer.deleteLater()
            self.audio_buffer = None

        self.audio_data = None
        self.current_file = None

        # Play next if available
        if self.queue and self.enabled:
            self._play_next()
