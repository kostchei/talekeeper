# Piper Voice Training Guide

Train custom voices for TaleKeeper narration from your own audio samples.

## Quick Start

### Requirements

- **Audio samples**: 100-1000+ clean WAV files (or MP3/FLAC to convert)
- **Transcripts**: Text transcription for each audio file
- **Hardware**: GPU recommended (training can take 12-48 hours on CPU)
- **Disk space**: 10-50 GB for checkpoints
- **Software**: Python 3.9+, Git, FFmpeg (for audio conversion)

### Installation

```python
from audio.piper_voice_trainer import PiperVoiceTrainer

trainer = PiperVoiceTrainer()
trainer.setup_training_environment()
```

This downloads the Piper training tools to `bin/piper-training/`.

## Step-by-Step Training

### 1. Prepare Audio Samples

**Requirements:**
- WAV format (or will be auto-converted)
- 22050 Hz sample rate (auto-converted if different)
- Mono audio (single channel)
- Clean recordings (minimal background noise)
- Consistent speaker voice
- 3-10 seconds per sample ideal

**Directory structure:**
```
my_voice_samples/
├── 001_sample.wav
├── 002_sample.wav
├── 003_sample.wav
...
└── transcripts.txt
```

### 2. Create Transcript File

Format: `filename|Transcript text`

```
001_sample.wav|The wizard casts a fireball at the goblin.
002_sample.wav|You find a treasure chest containing gold coins.
003_sample.wav|Roll for initiative!
```

### 3. Run Training

```python
from pathlib import Path
from audio.piper_voice_trainer import (
    PiperVoiceTrainer,
    create_sample_dataset_from_directory,
)

# Setup
trainer = PiperVoiceTrainer(language="en-us")
trainer.setup_training_environment()

# Load samples
audio_dir = Path("my_voice_samples")
transcript_file = audio_dir / "transcripts.txt"
samples = create_sample_dataset_from_directory(audio_dir, transcript_file)

print(f"Loaded {len(samples)} samples")

# Prepare dataset (LJSpeech format)
dataset_dir = Path("training_data/my_voice")
trainer.prepare_dataset(samples, dataset_dir)

# Train model
output_dir = Path("excess/narration/models/my_custom_voice")
model_path = trainer.train_voice(
    dataset_dir=dataset_dir,
    output_dir=output_dir,
    voice_name="my_narrator",
    quality="medium",  # "low", "medium", or "high"
    epochs=200,        # More epochs = better quality (but slower)
    batch_size=32,     # Reduce if GPU runs out of memory
)

print(f"Training complete! Model: {model_path}")
```

### 4. Add to Voice Profiles

Edit `excess/narration/voice_profiles.json`:

```json
{
  "profiles": {
    "my_custom": {
      "voice_id": "my_narrator",
      "campaign_style": "custom",
      "model_path": "excess/narration/models/my_custom_voice/my_narrator.onnx",
      "description": "Custom trained narrator voice",
      "style": {
        "speaking_rate": 1.0
      },
      "metadata": {
        "config_path": "excess/narration/models/my_custom_voice/my_narrator.onnx.json"
      }
    }
  }
}
```

## Quality Levels

- **low**: 10-20 MB model, fast synthesis, basic quality
- **medium**: 40-80 MB model, good balance (recommended)
- **high**: 100-200 MB model, best quality, slower synthesis

## Training Tips

### Audio Quality
- Use a good microphone in a quiet room
- Remove background noise (Audacity noise reduction works well)
- Normalize audio levels (-3 dB peak)
- Trim silence from start/end of clips

### Dataset Size
- **Minimum**: 100 samples (basic voice clone)
- **Recommended**: 500-1000 samples (good quality)
- **Professional**: 5000+ samples (excellent quality)

### Training Duration
- **Low quality + GPU**: 4-8 hours
- **Medium quality + GPU**: 12-24 hours
- **High quality + GPU**: 24-48 hours
- **CPU training**: 5-10x longer

### Transcript Quality
- Must match audio exactly (including punctuation)
- Use consistent spelling and formatting
- Include natural pauses with punctuation
- Avoid typos (they degrade quality)

## Advanced Options

### Multi-speaker Training

```python
# Prepare samples with speaker IDs
samples = [
    VoiceTrainingSample(
        audio_path=Path("narrator1/001.wav"),
        transcript="The dragon roars!",
        speaker="narrator_1",
    ),
    VoiceTrainingSample(
        audio_path=Path("narrator2/001.wav"),
        transcript="The dragon roars!",
        speaker="narrator_2",
    ),
]
```

### Fine-tuning Existing Model

Start from a pre-trained Piper model to reduce training time:

```python
trainer = PiperVoiceTrainer(
    base_model_path=Path("excess/narration/models/en_US-amy-medium.onnx")
)
```

### GPU Training

Ensure PyTorch with CUDA is installed:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Training will automatically use GPU if available.

## Troubleshooting

### "CUDA out of memory"
- Reduce `batch_size` (try 16 or 8)
- Use "low" or "medium" quality
- Close other GPU applications

### Poor voice quality
- Need more training samples (aim for 500+)
- Ensure audio quality is consistent
- Check transcripts match audio exactly
- Train for more epochs (300-500)

### Training very slow
- Use GPU (20-50x faster than CPU)
- Reduce quality level
- Reduce dataset size for testing

### Model doesn't sound like speaker
- Need more diverse samples (different phrases/emotions)
- Train longer (more epochs)
- Verify audio quality is good
- May need 1000+ samples for perfect cloning

## Example: Creating DM Voice Pack

```python
# 1. Record samples of your dungeon master voice
# - Combat narration: "The orc swings its axe!"
# - Exploration: "You enter a dimly lit chamber."
# - NPC dialogue: "Welcome, traveler."
# - Dice results: "Natural twenty!"

# 2. Organize files
# dm_voice/
#   combat/001.wav, 002.wav, ...
#   exploration/001.wav, 002.wav, ...
#   dialogue/001.wav, 002.wav, ...
#   dice/001.wav, 002.wav, ...
#   transcripts.txt

# 3. Train
trainer = PiperVoiceTrainer()
samples = create_sample_dataset_from_directory(
    Path("dm_voice"),
    Path("dm_voice/transcripts.txt")
)

model = trainer.train_voice(
    dataset_dir=Path("training_data/dm_voice"),
    output_dir=Path("excess/narration/models/dm_custom"),
    voice_name="dungeon_master",
    quality="medium",
    epochs=300,
)
```

## Resources

- **Piper Training Docs**: https://github.com/rhasspy/piper/tree/master/notebooks
- **Audio Recording**: Audacity (free, cross-platform)
- **Noise Reduction**: Audacity, Adobe Audition, iZotope RX
- **Dataset Tools**:
  - [Common Voice](https://commonvoice.mozilla.org/) - Free speech datasets
  - [LJSpeech](https://keithito.com/LJ-Speech-Dataset/) - Example dataset format

## Cost vs. Quality Trade-offs

| Samples | Quality | Training Time (GPU) | Use Case |
|---------|---------|---------------------|----------|
| 100     | Basic   | 4-6 hours           | Testing, experimentation |
| 500     | Good    | 12-18 hours         | Campaign narration |
| 1000    | Great   | 24-36 hours         | Professional quality |
| 5000+   | Excellent | 48-72 hours       | Voice acting, production |

Start with 100-200 samples to test the process, then expand to 500+ for production use.
