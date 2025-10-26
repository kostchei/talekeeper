# MIDI Background Music Integration

## Overview

TaleKeeper now includes authentic DOS-era MIDI background music using OPL3 FM synthesis (Sound Blaster 16 emulation). The music automatically plays on launch and dynamically adjusts volume based on game events.

## Components

### 1. MeltyS synth (Pure Python MIDI Synthesizer)
- **Location**: `audio/meltysynth.py` and `src/talekeeper/audio/meltysynth.py`
- **Size**: 117 KB
- **Dependencies**: Zero - uses only Python standard library
- **PyInstaller Ready**: Yes - single file, no external dependencies

### 2. OPL-3 FM Soundfont
- **Location**: `audio/soundfonts/OPL-3_FM_128M.sf2` and `src/talekeeper/audio/soundfonts/OPL-3_FM_128M.sf2`
- **Size**: 129 MB
- **Sound**: Authentic Sound Blaster 16 / Yamaha YMF262 FM synthesis
- **Perfect for**: Conan-style fantasy RPG atmosphere

### 3. MidiPlayer Class
- **Location**: `audio/midi_player.py` and `src/talekeeper/audio/midi_player.py`
- **Purpose**: Qt6-based MIDI playback with on-the-fly synthesis
- **Features**:
  - Queue-based playback
  - Real-time volume control
  - Renders MIDI to raw PCM audio in memory
  - Uses QAudioSink for direct PCM playback (no codec dependencies)
  - Seamless integration with Qt's audio system

### 4. AmbientMusicManager Class
- **Location**: `audio/ambient_music_manager.py` and `src/talekeeper/audio/ambient_music_manager.py`
- **Purpose**: Manages ambient music playback with random bag shuffle algorithm
- **Features**:
  - **Random Bag Algorithm**: Shuffles all tracks and plays through them once before reshuffling
  - **No Repeats**: Ensures every track plays before any track repeats
  - **Auto-play**: Automatically queues next track when one finishes
  - **Campaign Switching**: Dynamically loads music from different campaign folders
  - **Progress Tracking**: Tracks how many tracks remain before reshuffle

### 5. MIDI Music Files (Campaign-Based Organization)

Music is organized by campaign style to match the game's narrative theme:

**Conan Campaign:**
- **Ambient Music** (17 files): `audio/midi/campaigns/conan/ambient/`
  - 6-hour procedurally generated ambient music (12 chapters)
  - 5 original Conan the Barbarian soundtrack themes
  - Plays continuously in background using random bag shuffle
- **Event Soundscapes** (8 files): `audio/midi/campaigns/conan/scape/`
  - `combat.mid` (1.5 min) - Intense combat music
  - `victory.mid` (1.0 min) - Victory fanfare
  - `defeat.mid` (0.5 min) - Death/failure sting
  - `downtime.mid` (3.0 min) - Peaceful rest/campfire
  - `carousing.mid` (2.0 min) - Lively tavern atmosphere
  - `stealth.mid` (3.0 min) - Tense sneaking atmosphere
  - `exploration.mid` (4.0 min) - Atmospheric exploration
  - `tension.mid` (2.5 min) - Building tension/dread

**Golden Age Campaign (Warhammer Fantasy):**
- **Ambient Music** (102 files): `audio/midi/campaigns/golden/ambient/`
  - 12 original Warhammer: The Old World 30-minute ambient chapters
  - 90 Warhammer soundtrack conversions from Yourdio project
  - Total: ~8+ hours of unique ambient music
  - Plays continuously using random bag shuffle (no repeats until all 102 tracks play)
- **Event Soundscapes** (8 files): `audio/midi/campaigns/golden/scape/`
  - Same 8 event soundscapes as Conan (copied from conan/scape/)

The system automatically loads music from the appropriate campaign folder based on the active campaign frame.

## Volume Ducking System

The music automatically adjusts volume based on game state:

| State | Volume | Purpose |
|-------|--------|---------|
| Default | 40% | Light background ambiance |
| Narration Playing | 30% | Music ducks for voice clarity |
| Soundscape Playing | 10% | Music ducks for event soundscapes |

### Implementation

Volume ducking is implemented in `MainWindow`:
- `_duck_music_for_narration()` - Lowers music when narration starts
- `_restore_music_volume()` - Restores music when narration ends
- Signals connect automatically on initialization

## Usage in Code

### Basic MIDI Player Usage

```python
from talekeeper.audio import MidiPlayer

# Create player (auto-loads OPL3 soundfont)
player = MidiPlayer()

# Queue a file (campaign-based path)
player.enqueue(Path("audio/midi/campaigns/conan/ambient/chapter_01.mid"))

# Adjust volume
player.set_volume(0.5)  # 50%
```

### Ambient Music Manager Usage (Recommended)

```python
from talekeeper.audio import MidiPlayer, AmbientMusicManager

# Create MIDI player first
midi_player = MidiPlayer()
midi_player.set_volume(0.4)

# Create ambient music manager
ambient_manager = AmbientMusicManager(
    midi_player=midi_player,
    campaign_name="golden",  # or "conan"
    parent=self
)

# Start ambient music (random bag shuffle)
ambient_manager.start()

# Check status
remaining = ambient_manager.get_remaining_count()  # Tracks left before reshuffle
total = ambient_manager.get_total_count()  # Total tracks available

# Skip to next track
ambient_manager.skip()

# Switch campaigns
ambient_manager.set_campaign("conan")

# Stop playback
ambient_manager.stop()
```

### Integration in MainWindow

The MIDI player is initialized automatically in `MainWindow._initialize_midi_player()`:

```python
def _initialize_midi_player(self) -> None:
    # Creates player
    self.midi_player = MidiPlayer(parent=self)

    # Sets default volume
    self.midi_player.set_volume(0.4)

    # Connects narration ducking signals
    if self.narration_player:
        self.narration_player.playback_started.connect(self._duck_music_for_narration)
        self.narration_player.playback_finished.connect(self._restore_music_volume)

    # Auto-queues ambient music
    self._queue_ambient_music()
```

### Campaign Detection

The system automatically detects the active campaign and loads appropriate music:

```python
def _queue_ambient_music(self) -> None:
    """Queue ambient MIDI files based on active campaign."""
    # Get campaign style from encounter panel's campaign_frame
    campaign_style = self._get_active_campaign_style() or "conan"

    # Build campaign-specific path
    ambient_dir = Path("audio") / "midi" / "campaigns" / campaign_style / "ambient"

    # Load and queue all MIDI files for this campaign
    midi_files = sorted(ambient_dir.glob("*.mid"))
    for midi_file in midi_files:
        self.midi_player.enqueue(midi_file)
```

**Campaign Styles:**
- `"conan"` - Conan campaign (default)
- `"golden"` - Golden Age campaign
- Custom campaigns can be added by creating matching folder structures

## Random Bag Shuffle Algorithm

The `AmbientMusicManager` uses a "random bag" algorithm to ensure variety without repetition:

1. **Initial Shuffle**: All tracks are shuffled into a random order
2. **Sequential Playback**: Tracks play in shuffled order, one at a time
3. **Auto-Reshuffle**: When the bag is empty, it reshuffles all tracks again
4. **No Repeats**: Guarantees every track plays once before any track repeats

This is superior to pure random selection (which can repeat tracks) and sequential playback (which is predictable).

**Example for Golden Campaign (102 tracks):**
- Shuffle creates: `[track_47, track_12, track_89, ... track_3]`
- Plays all 102 tracks in that order
- Reshuffles: `[track_5, track_91, track_34, ... track_67]`
- Repeats indefinitely with new shuffle each cycle

## File Structure

```
TaleKeeper/
├── audio/
│   ├── meltysynth.py              # MIDI synthesizer
│   ├── midi_player.py             # MidiPlayer class (QAudioSink-based)
│   ├── ambient_music_manager.py   # Ambient music with random bag shuffle
│   ├── soundfonts/
│   │   └── OPL-3_FM_128M.sf2     # OPL3 soundfont (129 MB)
│   └── midi/
│       └── campaigns/             # Campaign-specific music
│           ├── conan/
│           │   ├── ambient/       # 17 ambient MIDI files
│           │   └── scape/         # 8 event soundscapes
│           └── golden/
│               ├── ambient/       # 102 Warhammer MIDI files
│               └── scape/         # 8 event soundscapes
│
└── src/talekeeper/               # Mirrored in src for production build
    └── audio/
        ├── meltysynth.py
        ├── midi_player.py
        ├── ambient_music_manager.py
        ├── soundfonts/
        │   └── OPL-3_FM_128M.sf2
        └── midi/
            └── campaigns/
                ├── conan/
                │   ├── ambient/  # 17 files
                │   └── scape/    # 8 soundscapes
                └── golden/
                    ├── ambient/  # 102 files
                    └── scape/    # 8 soundscapes
```

## Future Enhancements

### Soundscape Integration (Planned)
Add specific soundscapes for game events:

```python
def _play_soundscape(self, soundscape_type: str) -> None:
    """Play soundscape and duck music to 10%."""
    # Duck music
    if self.midi_player:
        self.midi_player.set_volume(0.1)

    # Play soundscape (treasure, combat, victory, defeat, etc.)
    soundscape_file = Path(f"audio/soundscapes/{soundscape_type}.ogg")
    # ... play soundscape
```

Event types to implement:
- Treasure/Loot discovery
- Combat initiation
- Victory celebration
- Defeat/death
- Downtime activities
- Town/safe area
- Dungeon exploration

## Technical Details

### QAudioSink vs QMediaPlayer

The `MidiPlayer` uses `QAudioSink` instead of `QMediaPlayer` for several reasons:

1. **No Codec Dependencies**: QMediaPlayer requires multimedia backend plugins that aren't available on all Windows systems
2. **Direct PCM Playback**: QAudioSink consumes raw PCM audio data directly
3. **Guaranteed Availability**: QAudioSink is part of Qt's core multimedia module
4. **Lower Level Control**: More direct control over audio buffer and playback

### Performance

**Rendering Speed:**
- Pure Python implementation is slower than C-based alternatives
- ~10-20 seconds to render 100 seconds of MIDI on typical hardware
- Rendering happens on-demand when tracks are queued
- Does not block UI during rendering

**Memory Usage:**
- ~130 MB for soundfont (loaded once at startup)
- ~1-5 MB per rendered audio buffer (temporary, released after playback)
- Minimal CPU usage during playback (pre-rendered to PCM)

**Random Bag Performance:**
- Negligible overhead (simple list shuffling)
- O(n) shuffle operation when refilling bag
- For 102 tracks: <1ms shuffle time

## PyInstaller Compatibility

✅ **Fully Compatible**
- No compiled dependencies
- Single Python file (meltysynth.py)
- Soundfont is a data file (include via `--add-data`)

Example PyInstaller command:
```bash
pyinstaller --add-data "audio/soundfonts;audio/soundfonts" \
            --add-data "audio/midi;audio/midi" \
            main.py
```

## Testing

A test application is available to verify ambient music functionality:

```bash
python test_ambient_music.py
```

**Features:**
- GUI controls for start/stop/skip
- Campaign switching (Golden/Conan)
- Real-time track counter
- Volume controls
- Playback monitoring

## Credits

- **MeltySynth**: Pure Python MIDI synthesizer by sinshu
  - GitHub: https://github.com/sinshu/py-meltysynth
- **OPL-3 Soundfont**: FM synthesis soundfont by Mindwerks
  - Emulates Yamaha YMF262 (Sound Blaster 16)
- **Conan Music**: Generated from original Basil Poledouris themes
- **Warhammer Music**: Old World soundtrack conversions via Yourdio project
  - 90 converted tracks from Warhammer: The Old World
  - 12 original 30-minute ambient chapters
