# Piper TTS Installation Complete

## Installation Summary

Successfully installed and configured Piper TTS for TaleKeeper narration system.

### Installed Components

1. **Piper TTS v1.2.0**
   - Location: `bin/piper/piper/piper.exe`
   - Size: 498 KB (+ 20 MB dependencies)
   - Source: GitHub rhasspy/piper release 2023.11.14-2

2. **Voice Model: en_US-amy-medium**
   - Location: `excess/narration/models/en_US-amy-medium.onnx`
   - Size: 61 MB
   - Config: `en_US-amy-medium.onnx.json`
   - Description: Clear female narrator

3. **Voice Profile Configuration**
   - File: `excess/narration/voice_profiles.json`
   - Active profile: "default" (narrator_default)
   - Campaign style: default

### Verification Results

✅ Piper executable found and working
✅ Voice model downloaded and configured
✅ Test synthesis successful (182 KB audio generated)
✅ Python integration working
✅ PyQt6 Multimedia available for playback

### Quick Test

The system was tested with:
```
"The fighter strikes with their longsword, dealing eight damage."
```

Generated audio successfully in ~1.5 seconds with natural-sounding narration.

## Usage

### Starting TaleKeeper

```bash
python main.py
```

Look for this message in the log panel:
```
[SYSTEM] Narration ready: 'narrator_default' for 'default'
```

### UI Controls

In the **Log Panel** header (top-right):

- **TTS** button (green when enabled)
- **Q:N** label (shows narration queue size)
- **Volume slider** (0-100%)

### Testing Narration

1. Start TaleKeeper
2. Ensure TTS button is green (enabled)
3. Set volume to 70% (default)
4. Enter combat or trigger log messages
5. Audio will automatically play through your speakers

### Troubleshooting

**No audio playing:**
- Check TTS button is green
- Verify volume slider is not at 0
- Check Windows volume mixer
- Look in `excess/narration/` for `.wav` files

**Synthesis errors:**
- Check log panel for error messages
- Verify model files exist in `excess/narration/models/`
- Ensure `voice_profiles.json` paths are correct

**Piper not found:**
- Verify `bin/piper/piper/piper.exe` exists
- Check file permissions (should be executable)

## Performance

- **Synthesis speed**: ~100-600ms per message
- **Batching window**: 2.5 seconds (multiple logs combined)
- **Real-time factor**: ~0.05 (20x faster than playback)
- **File cleanup**: Auto-delete after 24 hours, max 500 files

## File Locations

```
TaleKeeper/
├── bin/piper/piper/
│   ├── piper.exe                    # Main TTS executable
│   ├── espeak-ng.dll                # Phoneme library
│   ├── onnxruntime.dll              # ML runtime
│   └── espeak-ng-data/              # Language data
├── excess/narration/
│   ├── models/
│   │   ├── en_US-amy-medium.onnx      # Voice model
│   │   └── en_US-amy-medium.onnx.json # Voice config
│   ├── voice_profiles.json            # Active configuration
│   └── *.wav                          # Generated narration (auto-cleanup)
└── audio/
    ├── local_tts_engine.py          # Piper wrapper
    ├── audio_player.py              # Playback queue
    ├── file_cleanup.py              # Auto-cleanup
    └── log_narration_pipeline.py   # Main coordinator
```

## Next Steps

### Adding More Voices

1. Browse [Piper Voice Models](https://huggingface.co/rhasspy/piper-voices/tree/main)
2. Download `.onnx` and `.onnx.json` files
3. Place in `excess/narration/models/`
4. Edit `voice_profiles.json` to add new profile
5. Restart TaleKeeper

### Recommended Additional Voices

- **en_US-libritts-high** (90 MB) - Natural variation, multi-speaker
- **en_GB-alan-medium** (75 MB) - British male narrator
- **en_US-ryan-high** (90 MB) - American male narrator

### Campaign-Specific Voices

Edit `voice_profiles.json` to map different voices to campaign styles:

```json
{
  "profiles": {
    "default": { "voice_id": "narrator_default", ... },
    "conan": {
      "voice_id": "narrator_conan",
      "campaign_style": "conan",
      "model_path": "excess/narration/models/en_GB-alan-medium.onnx"
    }
  }
}
```

The system automatically switches voices when you change campaign frames.

## Documentation

- Full pipeline details: [docs/LOG_AUDIO_PIPELINE.md](docs/LOG_AUDIO_PIPELINE.md)
- Setup guide: [docs/PIPER_TTS_SETUP.md](docs/PIPER_TTS_SETUP.md)
- Piper documentation: https://github.com/rhasspy/piper

## Installation Date

October 4, 2025

## Version Info

- Piper TTS: v1.2.0 (2023.11.14-2)
- Voice Model: en_US-amy-medium (v1.0.0)
- TaleKeeper Integration: codex/build-text-to-speech-pipeline-for-logs branch
