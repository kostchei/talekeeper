# Log Audio Narration Pipeline

This document describes how the log narration system turns TaleKeeper's log panel output into narrated audio using a locally hosted, open-source text-to-speech (TTS) model.

## Overview

1. **Log emission** – `LogPanel.add_log_message()` now emits a `log_message_added` Qt signal with a serializable payload for every entry.
2. **Pipeline coordination** – `audio.log_narration_pipeline.LogNarrationPipeline` listens for these signals, batches nearby events, formats them into narration-friendly text, and calls a local TTS engine.
3. **Voice management** – `audio.campaign_voice_registry.CampaignVoiceRegistry` resolves which trained voice to use for the active campaign frame. Each campaign style can map to a custom model.
4. **Synthesis** – `audio.local_tts_engine.LocalTTSEngine` wraps a Coqui TTS model (or any compatible checkpoint) and writes WAV files to `excess/narration/`.
5. **Training** – `audio.voice_trainer.VoiceTrainer` prepares datasets from provided samples and launches fine-tuning when Coqui's training components are installed.

## Voice profile configuration

Voice metadata lives in `excess/narration/voice_profiles.json`. An example file ships alongside the code as `voice_profiles.example.json` – copy it to `voice_profiles.json` and update the paths to the checkpoints you train.

```json
{
  "default_profile": "default",
  "profiles": {
    "default": {
      "voice_id": "narrator_default",
      "model_path": "excess/narration/models/default_xtts.pth",
      "sample_library": "excess/narration/samples/default/style.wav",
      "style": {
        "preset": "narration",
        "speaking_rate": 0.98,
        "energy": 0.1,
        "emotion": "calm"
      }
    },
    "conan": {
      "voice_id": "narrator_conan",
      "campaign_style": "conan",
      "model_path": "excess/narration/models/conan_xtts.pth",
      "style": {
        "preset": "narration",
        "speaking_rate": 0.94,
        "energy": 0.35,
        "pitch_shift": -0.1
      }
    }
  }
}
```

Each profile supports:

- `voice_id`: Friendly identifier for logging.
- `campaign_style`: Optional override that maps directly to the `campaign_frame.style` string; defaults to the profile key.
- `model_path`: Path to the fine-tuned `.pth` (or equivalent) file.
- `sample_library`: Optional reference audio used for style conditioning.
- `style`: Preset plus modifiers (`speaking_rate`, `energy`, `pitch_shift`, `emotion`). Extra fields are passed through as custom kwargs.
- `metadata`: Additional options for the engine (`device`, `config_path`, etc.).

> **Note** – The narration pipeline is disabled automatically if no profile file is present.

## Campaign-aware delivery

`MainWindow` initializes the narration pipeline after creating the log panel. Whenever a campaign frame is applied, `_sync_narration_campaign()` updates the active voice in the registry using either the frame's `style` or `name`. Combat-focused frames can therefore use more energetic voices than downtime-oriented ones.

## Training workflow

1. Collect clean WAV/FLAC samples plus transcripts for the target performer.
2. Create a list of `VoiceTrainingSample` objects and call `VoiceTrainer.prepare_training_workspace()` to assemble an LJSpeech-style dataset.
3. Supply the samples, output directory, and a `CampaignVoiceProfile` to `VoiceTrainer.train_voice()`. With `TTS[train]` installed, the helper writes metadata, loads the base XTTS config, and invokes Coqui's trainer.
4. Drop the resulting checkpoint path into `voice_profiles.json` and restart TaleKeeper to pick it up.

The training utilities raise a descriptive error when the optional `TTS[train]` extras are missing, so they fail fast instead of silently doing nothing.

## Output files

Synthesized narration is saved inside `excess/narration/` using timestamped filenames. Adjust the output directory by passing a different path to `LogNarrationPipeline`.

## Extensibility

- Extend `NarrationFormatter` to add richer storytelling logic (e.g., combine dice rolls before damage, include actor names, etc.).
- Swap `LocalTTSEngine` for another backend by injecting a different `engine_factory`.
- Hook new analytics or accessibility features to `log_message_added` without touching the log panel implementation again.
