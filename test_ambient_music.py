"""Test script for ambient music manager with random bag playlist."""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

from audio.midi_player import MidiPlayer
from audio.ambient_music_manager import AmbientMusicManager


class AmbientMusicTest(QMainWindow):
    """Test window for ambient music playback."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ambient Music Test - Random Bag Playlist")
        self.setGeometry(100, 100, 500, 400)

        # Create MIDI player
        self.midi_player = MidiPlayer(parent=self)
        self.midi_player.set_volume(0.3)

        # Create ambient music manager
        self.ambient_manager = AmbientMusicManager(
            midi_player=self.midi_player,
            campaign_name="golden",
            parent=self
        )

        # Connect signals
        self.ambient_manager.track_changed.connect(self.on_track_changed)
        self.ambient_manager.playlist_shuffled.connect(self.on_playlist_shuffled)
        self.midi_player.playback_started.connect(self.on_playback_started)

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Create the UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Info label
        self.info_label = QLabel("Ambient Music Manager\nRandom Bag Playlist System")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # Track count label
        total = self.ambient_manager.get_total_count()
        self.track_label = QLabel(f"Total tracks: {total}")
        self.track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.track_label)

        # Current track label
        self.current_label = QLabel("No track playing")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.current_label)

        # Remaining label
        self.remaining_label = QLabel("Remaining in bag: 0")
        self.remaining_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.remaining_label)

        # Start button
        self.start_btn = QPushButton("Start Ambient Music")
        self.start_btn.clicked.connect(self.start_ambient)
        layout.addWidget(self.start_btn)

        # Stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_ambient)
        layout.addWidget(self.stop_btn)

        # Skip button
        self.skip_btn = QPushButton("Skip to Next Track")
        self.skip_btn.clicked.connect(self.skip_track)
        layout.addWidget(self.skip_btn)

        # Volume controls
        volume_label = QLabel("Volume: 30%")
        layout.addWidget(volume_label)

        # Campaign switch buttons
        layout.addSpacing(20)
        campaign_label = QLabel("Switch Campaign:")
        layout.addWidget(campaign_label)

        golden_btn = QPushButton("Golden Campaign")
        golden_btn.clicked.connect(lambda: self.switch_campaign("golden"))
        layout.addWidget(golden_btn)

        conan_btn = QPushButton("Conan Campaign")
        conan_btn.clicked.connect(lambda: self.switch_campaign("conan"))
        layout.addWidget(conan_btn)

        layout.addStretch()

        self.update_ui()

    def start_ambient(self):
        """Start ambient music playback."""
        self.ambient_manager.start()
        self.update_ui()

    def stop_ambient(self):
        """Stop ambient music playback."""
        self.ambient_manager.stop()
        self.update_ui()

    def skip_track(self):
        """Skip to next track."""
        self.ambient_manager.skip()

    def switch_campaign(self, campaign_name: str):
        """Switch to different campaign."""
        self.ambient_manager.set_campaign(campaign_name)
        total = self.ambient_manager.get_total_count()
        self.track_label.setText(f"Total tracks: {total} ({campaign_name})")
        self.update_ui()

    def on_track_changed(self, track: Path):
        """Handle track change."""
        self.update_ui()

    def on_playlist_shuffled(self):
        """Handle playlist shuffle."""
        self.info_label.setText("Playlist shuffled!\nRandom bag refilled")
        self.update_ui()

    def on_playback_started(self, track: Path):
        """Handle playback start."""
        self.current_label.setText(f"Now playing:\n{track.name}")
        self.update_ui()

    def update_ui(self):
        """Update UI state."""
        remaining = self.ambient_manager.get_remaining_count()
        total = self.ambient_manager.get_total_count()
        is_playing = self.ambient_manager.is_playing()

        self.remaining_label.setText(f"Remaining in bag: {remaining}/{total}")
        self.start_btn.setEnabled(not is_playing)
        self.stop_btn.setEnabled(is_playing)
        self.skip_btn.setEnabled(is_playing)


def main():
    app = QApplication(sys.argv)
    window = AmbientMusicTest()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
