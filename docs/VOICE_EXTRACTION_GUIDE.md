# Voice Extraction & Transcription Guide

Extract voice samples from existing audio and prepare them for training.

## Quick Answer

**Minimum samples needed:**
- **Testing**: 50-100 samples (basic quality)
- **Good quality**: 300-500 samples (recommended)
- **Professional**: 1000+ samples (excellent quality)

**Can you use existing audio?**
- ✅ **YES** - if you have permission
- ❌ **NO** - copyrighted content without permission

## Legal Sources for Audio

### ✅ You CAN Use

1. **Your Own Recordings**
   - Read narration yourself
   - Record your voice for 30-60 minutes
   - Best option - you own the rights

2. **Hired Voice Actors**
   - Contract specifically allows voice cloning
   - Get written permission
   - Sites: Fiverr, Upwork, Voice123

3. **Public Domain Audio**
   - Recordings from 1920s or earlier
   - LibriVox audiobooks (public domain books)
   - Archive.org public domain collections

4. **Creative Commons Licensed**
   - Check license allows derivative works
   - Common Voice dataset (Mozilla)
   - Some podcasters allow it

5. **Personal Use Audio**
   - Friends/family who give permission
   - Get written consent

### ❌ You CANNOT Use (Without Permission)

- Audiobooks (copyrighted)
- Podcasts (copyrighted)
- Movies/TV dialogue
- Commercial voice actors
- YouTube videos (most are copyrighted)
- Music with vocals

## Workflow: Extract Voice from Existing Audio

### Option 1: Automatic (Recommended)

Use the provided tool that handles everything:

```bash
python examples/prepare_voice_from_audio.py
```

This will:
1. Split long audio into segments (3-10 seconds)
2. Auto-transcribe using Whisper or Vosk
3. Create training dataset
4. Generate transcripts.txt

### Option 2: Manual Steps

#### Step 1: Install Dependencies

```bash
# For audio transcription (choose one):
pip install openai-whisper  # OpenAI Whisper (high quality, GPU recommended)
# OR
pip install vosk            # Vosk (fast, CPU-friendly)

# For audio splitting:
pip install pydub

# Also need FFmpeg:
# Windows: Download from https://ffmpeg.org/
# Linux: sudo apt-get install ffmpeg
# Mac: brew install ffmpeg
```

#### Step 2: Prepare Your Audio

If you have long audio (podcast, audiobook), split it:

```python
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Load audio
audio = AudioSegment.from_file("my_audiobook.mp3")

# Split on silence
chunks = split_on_silence(
    audio,
    min_silence_len=500,    # 500ms of silence
    silence_thresh=-40,      # -40 dBFS
    keep_silence=100,        # Keep 100ms at edges
)

# Save segments
for i, chunk in enumerate(chunks, 1):
    if 2000 < len(chunk) < 10000:  # 2-10 seconds
        chunk.export(f"segments/segment_{i:04d}.wav", format="wav")
```

#### Step 3: Transcribe Audio

**Option A: Using Whisper (Best Quality)**

```python
import whisper

model = whisper.load_model("base")  # or "small", "medium", "large"

# Transcribe single file
result = model.transcribe("segment_0001.wav")
print(result["text"])

# Batch process
import os
for filename in sorted(os.listdir("segments")):
    if filename.endswith(".wav"):
        result = model.transcribe(f"segments/{filename}")
        print(f"{filename}|{result['text']}")
```

**Option B: Using Vosk (Faster, Offline)**

```python
import vosk
import wave
import json

# Download model from: https://alphacephei.com/vosk/models
model = vosk.Model("vosk-model-small-en-us-0.15")

wf = wave.open("segment_0001.wav", "rb")
rec = vosk.KaldiRecognizer(model, wf.getframerate())

transcript = []
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        transcript.append(result["text"])

final = json.loads(rec.FinalResult())
transcript.append(final["text"])
print(" ".join(transcript))
```

#### Step 4: Create Transcripts File

Save as `transcripts.txt`:

```
segment_0001.wav|The wizard casts a powerful fireball spell.
segment_0002.wav|You find a treasure chest containing gold.
segment_0003.wav|The dragon roars and spreads its wings.
```

#### Step 5: Train Model

```bash
python examples/train_custom_voice.py
```

Point it to your directory with audio + transcripts.txt.

## Real-World Examples

### Example 1: Your Own Voice (Easiest)

**Time**: 1-2 hours recording + 12-18 hours training

1. Record yourself reading D&D narration:
   ```
   - 300 different sentences
   - 3-8 seconds each
   - Use a good USB mic
   - Quiet room
   ```

2. Create transcripts.txt (you know what you said!)

3. Train model

**Result**: Your voice narrating your own games!

### Example 2: Hired Voice Actor

**Cost**: $50-200 | **Time**: 18-24 hours training

1. Hire voice actor on Fiverr/Upwork
2. Contract: "500 narration samples, 3-5 sec each, for voice cloning"
3. They provide: WAV files + transcripts.txt
4. Train model

**Result**: Professional narrator for campaigns

### Example 3: Public Domain Audiobook

**Cost**: Free | **Time**: 2-3 hours prep + 20-30 hours training

1. Download LibriVox audiobook (public domain)
2. Run extraction script:
   ```bash
   python examples/prepare_voice_from_audio.py
   ```
3. Review and fix transcripts (auto-transcription ~95% accurate)
4. Train model

**Result**: Classic narrator voice (1920s style)

### Example 4: Friend's Voice (With Permission)

**Time**: 1 hour recording + 12-18 hours training

1. Get written permission
2. Record friend reading narration samples
3. Use Whisper to auto-transcribe
4. Train model

**Result**: Friend narrates your games!

## Sample Count vs. Quality

### 100 Samples
- **Recording time**: 20-30 minutes
- **Training time**: 4-6 hours
- **Quality**: Basic, robotic at times
- **Use for**: Testing, experimentation
- **Example**: Can narrate simple combat

### 300 Samples
- **Recording time**: 1-1.5 hours
- **Training time**: 12-15 hours
- **Quality**: Good, natural sounding
- **Use for**: Personal campaigns
- **Example**: Smooth narration with some emotion

### 500 Samples
- **Recording time**: 2-2.5 hours
- **Training time**: 18-24 hours
- **Quality**: Very good, natural prosody
- **Use for**: Regular use, streaming
- **Example**: Professional-sounding narration

### 1000 Samples
- **Recording time**: 4-5 hours
- **Training time**: 30-40 hours
- **Quality**: Excellent, captures nuances
- **Use for**: Production quality
- **Example**: Indistinguishable from source

### 3000+ Samples
- **Recording time**: 12+ hours
- **Training time**: 50+ hours
- **Quality**: Studio quality
- **Use for**: Commercial applications
- **Example**: Perfect voice clone

## Transcription Accuracy

| Method | Accuracy | Speed | Cost | GPU Needed |
|--------|----------|-------|------|------------|
| Whisper Large | 98-99% | Slow | Free | Yes (recommended) |
| Whisper Medium | 96-98% | Medium | Free | Yes (recommended) |
| Whisper Base | 93-95% | Fast | Free | No |
| Vosk | 90-93% | Very Fast | Free | No |
| Manual | 100% | Very Slow | Time | No |

**Recommendation**: Use Whisper Medium, then manually review and fix errors.

## Common Transcription Errors to Fix

Auto-transcription mistakes to watch for:

```
# Numbers
Audio: "twenty damage"
Transcript: "20 damage" → Fix to: "twenty damage"

# Homophones
Audio: "you're hit"
Transcript: "your hit" → Fix to: "you're hit"

# D&D Terms
Audio: "roll initiative"
Transcript: "roll an initiative" → Fix to: "roll initiative"

# Punctuation
Audio: "The goblin attacks, but misses"
Transcript: "The goblin attacks but misses" → Add comma

# Contractions
Audio: "you've been hit"
Transcript: "you have been hit" → Fix to: "you've been hit"
```

## Optimization Tips

### For Best Audio Extraction

1. **Use Mono Audio**: Stereo doesn't help, wastes space
2. **22050 Hz Sample Rate**: Piper's native rate
3. **Remove Music**: Voice-only segments train better
4. **Consistent Volume**: Normalize all clips to same level
5. **Clean Silence**: Trim silence from start/end

### For Best Transcriptions

1. **Review First 50**: Check accuracy before doing all
2. **Fix Consistently**: Same words should be same spelling
3. **Match Exactly**: Transcript must match audio perfectly
4. **Include Punctuation**: Helps with natural pauses
5. **Check Numbers**: Write out numbers as words

### For Faster Training

1. **Start Small**: Test with 100 samples first
2. **Use GPU**: 20-50x faster than CPU
3. **Lower Quality**: "low" or "medium" trains faster
4. **Batch Processing**: Process all transcripts at once

## Ethical Guidelines

### Do:
- ✅ Get explicit written permission
- ✅ Use public domain sources
- ✅ Hire voice actors with proper contracts
- ✅ Credit the source voice
- ✅ Use for personal, non-commercial purposes

### Don't:
- ❌ Clone celebrities without permission
- ❌ Use copyrighted audiobooks
- ❌ Impersonate real people maliciously
- ❌ Use for commercial purposes without rights
- ❌ Clone someone without their knowledge

## Troubleshooting

### "Not enough diversity in samples"
**Problem**: Model sounds robotic or monotone
**Solution**: Need more varied sentences (questions, emotions, different structures)

### "Transcription accuracy too low"
**Problem**: Lots of errors in auto-transcription
**Solution**: Use larger Whisper model or manually review/fix

### "Training quality poor despite many samples"
**Problem**: Model doesn't sound like source
**Solution**: Check audio quality, normalize volumes, remove background noise

### "Segments too short or too long"
**Problem**: Segments are 1 second or 30 seconds
**Solution**: Adjust silence detection parameters in splitting

## Next Steps

1. **Choose your audio source** (your voice recommended)
2. **Record or extract 300-500 samples**
3. **Transcribe using Whisper**
4. **Review and fix transcripts**
5. **Run training script**
6. **Test in TaleKeeper**

See also:
- [PIPER_VOICE_TRAINING.md](PIPER_VOICE_TRAINING.md) - Full training guide
- [examples/prepare_voice_from_audio.py](../examples/prepare_voice_from_audio.py) - Extraction tool
- [training_samples/README.md](../training_samples/README.md) - Sample organization
