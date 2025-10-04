# Log Audio Narration Pipeline

This document describes how the log narration system turns TaleKeeper's log panel output into narrated audio using Piper TTS, a fast local text-to-speech engine.

## Overview

1. **Log emission** – `LogPanel.add_log_message()` emits a `log_message_added` Qt signal with a serializable payload for every entry.
2. **Pipeline coordination** – `audio.log_narration_pipeline.LogNarrationPipeline` listens for these signals, batches nearby events, formats them into narration-friendly text, and calls Piper TTS.
3. **Voice management** – `audio.campaign_voice_registry.CampaignVoiceRegistry` resolves which voice to use for the active campaign frame. Each campaign style can map to a different Piper voice model.
4. **Synthesis** – `audio.local_tts_engine.LocalTTSEngine` wraps Piper TTS CLI and generates WAV files in `excess/narration/`.
5. **Audio playback** – `audio.audio_player.NarrationPlayer` manages a playback queue using PyQt6's QMediaPlayer, automatically playing synthesized narration.
6. **File cleanup** – `audio.file_cleanup.NarrationFileCleanup` automatically removes old narration files (default: 24 hours old).

## Voice profile configuration

Voice metadata lives in `excess/narration/voice_profiles.json`. An example file ships alongside the code as `voice_profiles.example.json` – copy it to `voice_profiles.json` and update the paths to the checkpoints you train.

```json
{
  "default_profile": "default",
  "profiles": {
    "default": {
      "voice_id": "narrator_default",
      "model_path": "excess/narration/models/en_US-amy-medium.onnx",
      "description": "Baseline narrator using Piper TTS",
      "style": {
        "preset": "narration",
        "speaking_rate": 0.98
      },
      "metadata": {
        "device": "cpu",
        "config_path": "excess/narration/models/en_US-amy-medium.onnx.json"
      }
    },
    "conan": {
      "voice_id": "narrator_conan",
      "campaign_style": "conan",
      "model_path": "excess/narration/models/en_US-libritts-high.onnx",
      "description": "Deeper voice for Conan campaign",
      "style": {
        "speaking_rate": 0.94
      },
      "metadata": {
        "speaker": "1"
      }
    }
  }
}
```

Each profile supports:

- `voice_id`: Friendly identifier for logging.
- `campaign_style`: Optional override that maps directly to the `campaign_frame.style` string; defaults to the profile key.
- `model_path`: Path to the Piper `.onnx` model file.
- `style`: Modifiers like `speaking_rate` (affects Piper's `--length_scale` parameter).
- `metadata`: Additional options like `device`, `config_path`, and `speaker` (for multi-speaker models).

> **Note** – The narration pipeline is disabled automatically if no profile file is present.

## Installing Piper TTS

Download Piper from [rhasspy/piper releases](https://github.com/rhasspy/piper/releases).

1. Download the appropriate binary for your platform (Windows, Linux, macOS)
2. Extract and add to PATH or place in `TaleKeeper/bin/piper`
3. Download voice models from [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices/tree/main)
4. Place `.onnx` and `.onnx.json` files in `excess/narration/models/`

Recommended voices:
- `en_US-amy-medium` - Clear female narrator
- `en_US-libritts-high` - Multi-speaker with natural variation
- `en_GB-alan-medium` - British male narrator

## UI Controls

The log panel header includes narration controls:

- **TTS button**: Toggle narration on/off (green = on, red = off)
- **Q:N label**: Shows current queue size
- **Volume slider**: Adjust playback volume (0-100%)

## Campaign-aware delivery

`MainWindow` initializes the narration pipeline after creating the log panel. Whenever a campaign frame is applied, `_sync_narration_campaign()` updates the active voice in the registry using either the frame's `style` or `name`. Combat-focused frames can use different voices than exploration scenes.

## File cleanup

The pipeline automatically:
- Deletes narration files older than 24 hours on startup
- Limits total narration files to 500 (oldest deleted first)
- Runs cleanup when pipeline starts

Configure in `LogNarrationPipeline` initialization:
```python
self.file_cleanup = NarrationFileCleanup(
    self.output_directory,
    max_age_hours=24,
    max_files=500
)
```

## Audio playback

`NarrationPlayer` manages the playback queue:
- Automatically plays synthesized audio in order
- Stops playback when narration is disabled
- Emits signals for queue updates and errors
- Uses PyQt6's QMediaPlayer for cross-platform compatibility

## Extensibility

- Extend `NarrationFormatter` to add richer storytelling logic (e.g., combine dice rolls with damage).
- Swap `LocalTTSEngine` for another backend by injecting a different `engine_factory`.
- Hook new analytics or accessibility features to `log_message_added` without touching the log panel implementation.
