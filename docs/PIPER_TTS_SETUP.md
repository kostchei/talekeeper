# Piper TTS Setup Guide

Quick setup guide for enabling narration in TaleKeeper using Piper TTS.

## Prerequisites

- Windows 10/11, Linux, or macOS
- TaleKeeper installed and working
- ~100-200MB free space for voice models

## Installation Steps

### 1. Install Piper TTS

#### Windows
```bash
# Download from GitHub releases
https://github.com/rhasspy/piper/releases

# Download piper_windows_amd64.zip
# Extract to TaleKeeper/bin/piper/ or add to PATH
```

#### Linux
```bash
wget https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz
tar -xzf piper_linux_x86_64.tar.gz
sudo mv piper /usr/local/bin/
```

#### macOS
```bash
wget https://github.com/rhasspy/piper/releases/latest/download/piper_macos_x64.tar.gz
tar -xzf piper_macos_x64.tar.gz
sudo mv piper /usr/local/bin/
```

### 2. Download Voice Models

Visit [Piper Voice Models](https://huggingface.co/rhasspy/piper-voices/tree/main) and download:

**Recommended for narration:**
- `en_US-amy-medium` (Clear female, 63MB)
- `en_US-libritts-high` (Natural variation, 90MB)
- `en_GB-alan-medium` (British male, 75MB)

**Download both files for each voice:**
- `en_US-amy-medium.onnx`
- `en_US-amy-medium.onnx.json`

### 3. Setup TaleKeeper Directory

```bash
cd TaleKeeper
mkdir -p excess/narration/models
```

Move downloaded `.onnx` and `.onnx.json` files to:
```
TaleKeeper/excess/narration/models/
```

### 4. Configure Voice Profiles

Copy the example config:
```bash
cp excess/narration/voice_profiles.example.json excess/narration/voice_profiles.json
```

Edit `voice_profiles.json` to match your downloaded models:

```json
{
  "default_profile": "default",
  "profiles": {
    "default": {
      "voice_id": "narrator_default",
      "model_path": "excess/narration/models/en_US-amy-medium.onnx",
      "description": "Clear female narrator",
      "style": {
        "speaking_rate": 1.0
      },
      "metadata": {
        "config_path": "excess/narration/models/en_US-amy-medium.onnx.json"
      }
    }
  }
}
```

### 5. Verify Installation

```bash
# Test Piper
piper --version

# Should output: piper v1.2.0 (or similar)
```

### 6. Launch TaleKeeper

```bash
python main.py
```

Check the log panel for:
```
[SYSTEM] Narration ready: 'narrator_default' for 'default'
```

## UI Controls

In the log panel header:

- **TTS button**: Toggle narration (green = on, red = off)
- **Q:N**: Queue size (number of pending narration clips)
- **Slider**: Volume control (0-100%)

## Troubleshooting

### "Piper TTS not found"
- Ensure `piper` is in your PATH
- Or place in `TaleKeeper/bin/piper/piper.exe` (Windows) or `TaleKeeper/bin/piper/piper` (Linux/Mac)

### "Model file not found"
- Check `model_path` in `voice_profiles.json` matches actual file location
- Verify both `.onnx` and `.onnx.json` files exist

### No audio playback
- Check volume slider is not at 0
- Verify TTS button is green (enabled)
- Check `excess/narration/` for generated `.wav` files

### Slow synthesis
- Try smaller models (low/medium quality instead of high)
- Reduce `speaking_rate` to generate faster

## Advanced Configuration

### Multi-speaker voices

For voices like `libritts`, specify speaker ID:

```json
"metadata": {
  "speaker": "1"
}
```

### Adjust speaking rate

```json
"style": {
  "speaking_rate": 1.2
}
```

Values: `0.5` (slow) to `2.0` (fast), default `1.0`

### Campaign-specific voices

Map different voices to campaign styles:

```json
{
  "profiles": {
    "default": { ... },
    "conan": {
      "voice_id": "conan_narrator",
      "campaign_style": "conan",
      "model_path": "excess/narration/models/en_GB-alan-medium.onnx",
      "style": {
        "speaking_rate": 0.9
      }
    }
  }
}
```

The system automatically switches voices when campaign frames change.

## File Management

Narration files are auto-deleted:
- Files older than 24 hours (on startup)
- When total exceeds 500 files (oldest first)

Audio files stored in: `excess/narration/*.wav`

## Performance

Typical synthesis times:
- Short log (5-10 words): 100-300ms
- Medium log (20-30 words): 300-600ms
- Long log (50+ words): 600-1200ms

Batching reduces overhead - logs within 2.5s are combined into one narration.
