"""Test MIDI player with Conan soundtracks."""

import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

from audio.midi_player import MidiPlayer


def test_midi_playback():
    """Test MIDI playback with Conan files."""
    app = QApplication(sys.argv)

    # Create MIDI player
    player = MidiPlayer()

    # Find some Conan MIDI files
    source_dir = Path("audio/midi/conan_source")
    ambient_dir = Path("audio/midi/conan_ambient")

    # Test with one source file and one ambient file
    test_files = []

    if source_dir.exists():
        midi_files = list(source_dir.glob("*.mid"))
        if midi_files:
            test_files.append(midi_files[0])
            print(f"Found source file: {midi_files[0].name}")

    if ambient_dir.exists():
        midi_files = list(ambient_dir.glob("*.mid"))
        if midi_files:
            test_files.append(midi_files[0])
            print(f"Found ambient file: {midi_files[0].name}")

    if not test_files:
        print("No MIDI files found!")
        return

    # Connect signals
    player.playback_started.connect(
        lambda p: print(f"\n▶️  Playing: {p.name}")
    )
    player.playback_finished.connect(
        lambda p: print(f"✅ Finished: {p.name}")
    )
    player.playback_error.connect(
        lambda e: print(f"❌ Error: {e}")
    )

    # Queue files
    print(f"\nQueuing {len(test_files)} MIDI files...")
    for midi_file in test_files:
        player.enqueue(midi_file)

    # Run event loop
    print("\nStarting playback...")
    print("Press Ctrl+C to stop\n")

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n\nStopped by user")
        player.stop()


if __name__ == "__main__":
    test_midi_playback()
