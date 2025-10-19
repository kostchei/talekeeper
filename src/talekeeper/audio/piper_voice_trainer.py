# core
# category: utility
"""Train custom Piper TTS voices from audio samples."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

PIPER_TRAINING_REPO = "https://github.com/rhasspy/piper.git"


@dataclass
class VoiceTrainingSample:
    """Audio sample with transcript for voice training."""

    audio_path: Path
    transcript: str
    speaker: str = "narrator"
    language: str = "en"

    def sanitized_transcript(self) -> str:
        return " ".join(self.transcript.strip().split())


class PiperVoiceTrainer:
    """Train custom Piper voices from audio samples."""

    def __init__(
        self,
        piper_training_dir: Optional[Path] = None,
        language: str = "en-us",
    ) -> None:
        self.piper_training_dir = (
            Path(piper_training_dir) if piper_training_dir else Path("bin/piper-training")
        )
        self.language = language

    def verify_training_environment(self) -> bool:
        """Check if Piper training environment is set up."""
        required_files = [
            self.piper_training_dir / "src" / "python" / "piper_train",
            self.piper_training_dir / "src" / "python" / "requirements.txt",
        ]
        return all(f.exists() for f in required_files)

    def setup_training_environment(self) -> None:
        """Clone and set up Piper training repository."""
        if self.verify_training_environment():
            print("Piper training environment already set up")
            return

        print(f"Cloning Piper training repository to {self.piper_training_dir}...")
        self.piper_training_dir.parent.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            ["git", "clone", PIPER_TRAINING_REPO, str(self.piper_training_dir)],
            check=True,
        )

        print("Installing training dependencies...")
        requirements = self.piper_training_dir / "src" / "python" / "requirements.txt"
        subprocess.run(
            ["pip", "install", "-r", str(requirements)],
            check=True,
        )

    def prepare_dataset(
        self,
        samples: Iterable[VoiceTrainingSample],
        output_dir: Path,
        *,
        sample_rate: int = 22050,
        copy_audio: bool = True,
    ) -> Path:
        """
        Prepare LJSpeech-format dataset for Piper training.

        Creates:
        - output_dir/wavs/*.wav (audio files)
        - output_dir/metadata.csv (filename|transcript pairs)
        """
        output_dir = Path(output_dir)
        wav_dir = output_dir / "wavs"
        wav_dir.mkdir(parents=True, exist_ok=True)

        sample_list = list(samples)
        if not sample_list:
            raise ValueError("No training samples provided")

        metadata_lines: List[str] = []

        for idx, sample in enumerate(sample_list, start=1):
            source = Path(sample.audio_path)
            if not source.exists():
                raise FileNotFoundError(f"Audio file not found: {source}")

            target = wav_dir / f"{idx:04d}.wav"

            if source.suffix.lower() == ".wav":
                if copy_audio:
                    shutil.copyfile(source, target)
                else:
                    target.symlink_to(source.absolute())
            else:
                print(f"Converting {source.name} to WAV at {sample_rate} Hz...")
                subprocess.run(
                    [
                        "ffmpeg",
                        "-i", str(source),
                        "-ar", str(sample_rate),
                        "-ac", "1",
                        "-y",
                        str(target),
                    ],
                    check=True,
                    capture_output=True,
                )

            metadata_lines.append(f"{target.stem}|{sample.sanitized_transcript()}")

        metadata_path = output_dir / "metadata.csv"
        metadata_path.write_text("\n".join(metadata_lines))

        print(f"Prepared {len(sample_list)} samples in {output_dir}")
        return metadata_path

    def train_voice(
        self,
        dataset_dir: Path,
        output_dir: Path,
        voice_name: str,
        *,
        quality: str = "medium",
        epochs: Optional[int] = None,
        batch_size: int = 32,
        validation_split: float = 0.1,
    ) -> Path:
        """
        Train a Piper voice model.

        Args:
            dataset_dir: Directory with wavs/ and metadata.csv
            output_dir: Where to save trained model
            voice_name: Name for the voice
            quality: "low", "medium", or "high" (affects model size/quality)
            epochs: Number of training epochs (None = auto)
            batch_size: Training batch size
            validation_split: Fraction of data for validation

        Returns:
            Path to trained .onnx model
        """
        if not self.verify_training_environment():
            raise RuntimeError(
                "Piper training environment not set up. Run setup_training_environment() first."
            )

        dataset_dir = Path(dataset_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        training_script = self.piper_training_dir / "src" / "python" / "piper_train"

        config = {
            "dataset_dir": str(dataset_dir.absolute()),
            "output_dir": str(output_dir.absolute()),
            "language": self.language,
            "voice_name": voice_name,
            "quality": quality,
            "batch_size": batch_size,
            "validation_split": validation_split,
        }

        if epochs:
            config["max_epochs"] = epochs

        config_path = output_dir / "training_config.json"
        config_path.write_text(json.dumps(config, indent=2))

        print(f"Starting training for '{voice_name}'...")
        print(f"Quality: {quality}")
        print(f"Output: {output_dir}")

        cmd = [
            "python",
            "-m",
            "piper_train",
            "--dataset-dir", str(dataset_dir.absolute()),
            "--output-dir", str(output_dir.absolute()),
            "--language", self.language,
        ]

        if quality:
            cmd.extend(["--quality", quality])
        if epochs:
            cmd.extend(["--max-epochs", str(epochs)])

        print(f"Running: {' '.join(cmd)}")

        subprocess.run(cmd, check=True, cwd=self.piper_training_dir / "src" / "python")

        model_path = output_dir / f"{voice_name}.onnx"
        if not model_path.exists():
            raise RuntimeError(f"Training completed but model not found at {model_path}")

        print(f"Training complete! Model saved to: {model_path}")
        return model_path


def create_sample_dataset_from_directory(
    audio_dir: Path,
    transcript_file: Optional[Path] = None,
) -> List[VoiceTrainingSample]:
    """
    Helper: Create training samples from a directory of audio files.

    If transcript_file is provided, expects format:
    filename.wav|This is the transcript text
    filename2.wav|Another transcript

    Otherwise, uses filename as transcript (not recommended for training).
    """
    audio_dir = Path(audio_dir)
    samples = []

    transcripts = {}
    if transcript_file and transcript_file.exists():
        for line in transcript_file.read_text().splitlines():
            if "|" in line:
                filename, transcript = line.split("|", 1)
                transcripts[filename.strip()] = transcript.strip()

    for audio_file in sorted(audio_dir.glob("*.wav")):
        transcript = transcripts.get(
            audio_file.name,
            audio_file.stem.replace("_", " ").replace("-", " ")
        )
        samples.append(
            VoiceTrainingSample(
                audio_path=audio_file,
                transcript=transcript,
            )
        )

    return samples
