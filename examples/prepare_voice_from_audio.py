"""Extract voice samples from existing audio files with auto-transcription."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def transcribe_audio_whisper(audio_path: Path) -> str:
    """
    Transcribe audio using OpenAI Whisper (local, free).

    Install: pip install openai-whisper
    """
    try:
        import whisper
    except ImportError:
        raise RuntimeError(
            "Whisper not installed. Install with: pip install openai-whisper"
        )

    print(f"Transcribing {audio_path.name}...")
    model = whisper.load_model("base")  # or "small", "medium", "large"
    result = model.transcribe(str(audio_path))
    return result["text"].strip()


def transcribe_audio_vosk(audio_path: Path, model_path: Optional[Path] = None) -> str:
    """
    Transcribe audio using Vosk (offline, fast, free).

    Install: pip install vosk
    Download model from: https://alphacephei.com/vosk/models
    """
    try:
        import vosk
        import wave
        import json
    except ImportError:
        raise RuntimeError(
            "Vosk not installed. Install with: pip install vosk"
        )

    if model_path is None:
        model_path = Path("models/vosk-model-small-en-us-0.15")

    if not model_path.exists():
        raise FileNotFoundError(
            f"Vosk model not found at {model_path}\n"
            "Download from: https://alphacephei.com/vosk/models"
        )

    model = vosk.Model(str(model_path))

    wf = wave.open(str(audio_path), "rb")
    rec = vosk.KaldiRecognizer(model, wf.getframerate())

    transcript_parts = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            transcript_parts.append(result.get("text", ""))

    final_result = json.loads(rec.FinalResult())
    transcript_parts.append(final_result.get("text", ""))

    return " ".join(transcript_parts).strip()


def split_audio_by_silence(
    audio_path: Path,
    output_dir: Path,
    min_silence_len: int = 500,
    silence_thresh: int = -40,
    min_segment_len: int = 1000,
    max_segment_len: int = 10000,
) -> list[Path]:
    """
    Split long audio into segments based on silence detection.

    Install: pip install pydub

    Args:
        audio_path: Input audio file
        output_dir: Where to save segments
        min_silence_len: Minimum silence length in ms to split on
        silence_thresh: Silence threshold in dBFS (lower = more sensitive)
        min_segment_len: Minimum segment length in ms
        max_segment_len: Maximum segment length in ms

    Returns:
        List of paths to generated segments
    """
    try:
        from pydub import AudioSegment
        from pydub.silence import split_on_silence
    except ImportError:
        raise RuntimeError(
            "pydub not installed. Install with: pip install pydub\n"
            "Also need ffmpeg: https://ffmpeg.org/download.html"
        )

    print(f"Loading audio: {audio_path.name}")
    audio = AudioSegment.from_file(audio_path)

    print("Splitting on silence...")
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=100,  # Keep 100ms of silence at edges
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_files = []

    for i, chunk in enumerate(chunks, 1):
        duration = len(chunk)

        # Skip too short or too long segments
        if duration < min_segment_len:
            continue
        if duration > max_segment_len:
            # Split long segments into smaller pieces
            num_parts = (duration // max_segment_len) + 1
            part_len = duration // num_parts
            for j in range(num_parts):
                start = j * part_len
                end = start + part_len
                part = chunk[start:end]
                output_file = output_dir / f"segment_{i:04d}_{j:02d}.wav"
                part.export(output_file, format="wav")
                output_files.append(output_file)
        else:
            output_file = output_dir / f"segment_{i:04d}.wav"
            chunk.export(output_file, format="wav")
            output_files.append(output_file)

    print(f"Created {len(output_files)} segments")
    return output_files


def main():
    from audio.piper_voice_trainer import VoiceTrainingSample

    print("=" * 60)
    print("Voice Sample Preparation from Existing Audio")
    print("=" * 60)

    print("\nThis tool will:")
    print("1. Split long audio into segments (optional)")
    print("2. Auto-transcribe each segment")
    print("3. Create training dataset")

    print("\n" + "=" * 60)
    print("IMPORTANT: Legal Notice")
    print("=" * 60)
    print("Only use audio you have permission to use:")
    print("  - Your own voice recordings")
    print("  - Voice actors you've hired")
    print("  - Public domain recordings")
    print("  - Audio with explicit permission")
    print("\nDo NOT use copyrighted material without permission!")

    response = input("\nI confirm I have permission to use this audio (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return

    print("\n" + "=" * 60)
    print("Step 1: Audio Input")
    print("=" * 60)

    audio_file = input("Path to audio file (or directory of files): ").strip()
    audio_path = Path(audio_file)

    if not audio_path.exists():
        print(f"Error: File not found: {audio_path}")
        return

    output_base = Path("training_samples/extracted_voice")

    # Process single file or directory
    if audio_path.is_file():
        audio_files = [audio_path]
    else:
        audio_files = list(audio_path.glob("*.wav")) + \
                     list(audio_path.glob("*.mp3")) + \
                     list(audio_path.glob("*.flac"))
        if not audio_files:
            print("Error: No audio files found in directory")
            return

    # Ask about splitting
    print("\n" + "=" * 60)
    print("Step 2: Audio Splitting")
    print("=" * 60)
    print("Do you need to split long audio into segments?")
    print("  - Choose 'yes' for podcasts, audiobooks, long recordings")
    print("  - Choose 'no' if you already have short clips (3-10 sec)")

    split_audio = input("\nSplit audio? (yes/no): ").lower() in ['yes', 'y']

    segments_to_process = []

    if split_audio:
        print("\nSplitting audio files...")
        segments_dir = output_base / "segments"
        for audio_file in audio_files:
            try:
                segments = split_audio_by_silence(
                    audio_file,
                    segments_dir,
                    min_silence_len=500,
                    silence_thresh=-40,
                    min_segment_len=2000,   # 2 seconds minimum
                    max_segment_len=10000,  # 10 seconds maximum
                )
                segments_to_process.extend(segments)
            except Exception as e:
                print(f"Error splitting {audio_file.name}: {e}")
    else:
        segments_to_process = audio_files

    print(f"\nTotal segments to transcribe: {len(segments_to_process)}")

    # Choose transcription method
    print("\n" + "=" * 60)
    print("Step 3: Transcription")
    print("=" * 60)
    print("Choose transcription method:")
    print("  1. Whisper (OpenAI, high quality, slower, GPU recommended)")
    print("  2. Vosk (offline, fast, good quality)")
    print("  3. Manual (create transcripts.txt yourself)")

    method = input("\nChoice (1/2/3): ").strip()

    samples = []

    if method == "1":
        # Whisper transcription
        for segment in segments_to_process:
            try:
                transcript = transcribe_audio_whisper(segment)
                samples.append(VoiceTrainingSample(
                    audio_path=segment,
                    transcript=transcript
                ))
                print(f"  {segment.name}: {transcript[:60]}...")
            except Exception as e:
                print(f"  Error: {e}")

    elif method == "2":
        # Vosk transcription
        model_path = input("Path to Vosk model (or press Enter for default): ").strip()
        vosk_model = Path(model_path) if model_path else None

        for segment in segments_to_process:
            try:
                transcript = transcribe_audio_vosk(segment, vosk_model)
                samples.append(VoiceTrainingSample(
                    audio_path=segment,
                    transcript=transcript
                ))
                print(f"  {segment.name}: {transcript[:60]}...")
            except Exception as e:
                print(f"  Error: {e}")

    elif method == "3":
        # Manual transcription
        print("\nSegments saved. Create transcripts.txt manually:")
        for segment in segments_to_process:
            print(f"  {segment.name}")

        transcript_file = output_base / "transcripts.txt"
        print(f"\nCreate: {transcript_file}")
        print("Format: filename.wav|Transcript text here")
        return

    else:
        print("Invalid choice.")
        return

    # Save transcripts
    print("\n" + "=" * 60)
    print("Step 4: Saving Results")
    print("=" * 60)

    output_base.mkdir(parents=True, exist_ok=True)
    transcript_file = output_base / "transcripts.txt"

    lines = []
    for sample in samples:
        lines.append(f"{sample.audio_path.name}|{sample.transcript}")

    transcript_file.write_text("\n".join(lines))

    print(f"\nSaved {len(samples)} transcripts to: {transcript_file}")
    print(f"Audio files in: {output_base / 'segments' if split_audio else audio_path.parent}")

    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    print("1. Review transcripts.txt and fix any errors")
    print("2. Run: python examples/train_custom_voice.py")
    print("3. Point it to:", output_base)

    print(f"\nDataset ready with {len(samples)} samples!")


if __name__ == "__main__":
    from typing import Optional
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
