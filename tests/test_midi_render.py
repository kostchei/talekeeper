"""Simple test of MIDI rendering without Qt."""

import sys
from pathlib import Path

# Add audio directory to path
sys.path.insert(0, 'audio')

import meltysynth as ms


def test_render():
    """Test rendering a MIDI file to audio."""
    print("Loading soundfont...")
    soundfont_path = Path("audio/soundfonts/OPL-3_FM_128M.sf2")
    sound_font = ms.SoundFont.from_file(str(soundfont_path))
    print(f"  Loaded: {soundfont_path.name}")

    # Find a small MIDI file
    midi_path = Path("audio/midi/conan_source/Conan the Barbarian - Basil Poledouris.mid")
    if not midi_path.exists():
        print(f"MIDI file not found: {midi_path}")
        return

    print(f"\nLoading MIDI: {midi_path.name}")
    midi_file = ms.MidiFile.from_file(str(midi_path))
    print(f"  Duration: {midi_file.length:.1f} seconds")

    # Create synthesizer
    print("\nCreating synthesizer...")
    settings = ms.SynthesizerSettings(44100)
    synthesizer = ms.Synthesizer(sound_font, settings)

    # Create sequencer
    print("Creating sequencer...")
    sequencer = ms.MidiFileSequencer(synthesizer)
    sequencer.play(midi_file, False)

    # Calculate buffer size
    sample_count = int(settings.sample_rate * midi_file.length)
    print(f"  Buffer size: {sample_count:,} samples")

    # Create output buffers
    print("\nCreating audio buffers...")
    left = ms.create_buffer(sample_count)
    right = ms.create_buffer(sample_count)

    # Render audio
    print("Rendering MIDI to audio...")
    sequencer.render(left, right)
    print("  Done!")

    # Check output
    max_left = max(abs(s) for s in left)
    max_right = max(abs(s) for s in right)
    print(f"\nAudio stats:")
    print(f"  Max left:  {max_left:.3f}")
    print(f"  Max right: {max_right:.3f}")

    if max_left > 0.01 and max_right > 0.01:
        print("\n✓ SUCCESS: MIDI rendered with audio output!")
    else:
        print("\n✗ WARNING: Audio levels very low")


if __name__ == "__main__":
    try:
        test_render()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
