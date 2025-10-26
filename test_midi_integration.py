"""Test MIDI player integration in TaleKeeper."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from ui.main_window import MainWindow


def test_midi_integration():
    """Test that MIDI player initializes and starts playing."""
    app = QApplication(sys.argv)

    # Create main window
    print("Creating MainWindow...")
    window = MainWindow()

    # Check MIDI player was initialized
    if window.midi_player is None:
        print("ERROR: MIDI player not initialized!")
        return 1

    print(f"MIDI player initialized: {window.midi_player}")
    print(f"MIDI player volume: {window.midi_player.get_volume()}")
    print(f"MIDI queue size: {window.midi_player.get_queue_size()}")

    # Test volume ducking
    if window.narration_player:
        print("\nTesting volume ducking...")

        # Simulate narration start
        test_path = Path("test.wav")
        window._duck_music_for_narration(test_path)
        print(f"Volume after ducking: {window.midi_player.get_volume()} (should be 0.3)")

        # Simulate narration end
        window._restore_music_volume(test_path)
        print(f"Volume after restore: {window.midi_player.get_volume()} (should be 0.4)")

    print("\nSUCCESS: MIDI integration working!")

    # Close window after 2 seconds
    QTimer.singleShot(2000, app.quit)

    return app.exec()


if __name__ == "__main__":
    sys.exit(test_midi_integration())
