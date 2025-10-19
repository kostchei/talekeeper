# core
# category: utility
"""Utilities to fine-tune a narration voice from campaign samples."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from .voice_profiles import CampaignVoiceProfile


@dataclass
class VoiceTrainingSample:
    """Represents a single utterance used for voice training."""

    audio_path: Path
    transcript: str
    speaker: str = "narrator"
    language: str = "en"

    def sanitized_transcript(self) -> str:
        return " ".join(self.transcript.strip().split())


class VoiceTrainer:
    """Prepare datasets and launch local fine-tuning runs."""

    def __init__(
        self,
        base_model_path: Optional[Path] = None,
        base_config_path: Optional[Path] = None,
        language: str = "en",
    ) -> None:
        self.base_model_path = Path(base_model_path) if base_model_path else None
        self.base_config_path = Path(base_config_path) if base_config_path else None
        self.language = language

    def prepare_training_workspace(
        self,
        samples: Iterable[VoiceTrainingSample],
        workspace: Path,
        *,
        copy_audio: bool = True,
    ) -> tuple[Path, List[VoiceTrainingSample]]:
        """Create an LJSpeech-style dataset from the provided samples."""
        workspace = Path(workspace)
        wav_dir = workspace / "wavs"
        wav_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = workspace / "metadata.csv"

        sample_list = list(samples)
        lines: List[str] = []
        for idx, sample in enumerate(sample_list, start=1):
            source = Path(sample.audio_path)
            if not source.exists():
                raise FileNotFoundError(f"Training sample {source} was not found")
            target = wav_dir / f"{idx:04d}{source.suffix}"
            if copy_audio:
                shutil.copyfile(source, target)
            else:
                if target.exists():
                    target.unlink()
                target.symlink_to(source)
            lines.append(f"{target.stem}|{sample.sanitized_transcript()}")

        metadata_path.write_text("\n".join(lines))
        return metadata_path, sample_list

    def train_voice(
        self,
        samples: Iterable[VoiceTrainingSample],
        output_directory: Path,
        voice_profile: CampaignVoiceProfile,
        *,
        epochs: int = 150,
        copy_audio: bool = True,
    ) -> Path:
        """Fine-tune a base model on the provided samples."""
        workspace = Path(output_directory) / "training_workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        metadata_path, sample_list = self.prepare_training_workspace(
            samples, workspace, copy_audio=copy_audio
        )
        if not sample_list:
            raise ValueError("No training samples provided")

        try:
            from TTS.trainer import Trainer, TrainerArgs  # type: ignore
            from TTS.tts.configs.xtts_config import XttsConfig  # type: ignore
            from TTS.tts.datasets.dataset_config import DatasetConfig  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Training requires the coqui-TTS extras. Install with `pip install TTS[train]`."
            ) from exc

        config = XttsConfig()
        if self.base_config_path and self.base_config_path.exists():
            config.load_json(str(self.base_config_path))
        config.output_path = str(output_directory)
        config.run_name = voice_profile.voice_id
        max_len = max((len(sample.sanitized_transcript()) for sample in sample_list), default=0)
        config.max_text_len = max_len or 200
        dataset = DatasetConfig(
            formatter="ljspeech",
            meta_file_train=str(metadata_path),
            path=str(workspace),
            language=self.language,
        )
        config.datasets = [dataset]
        if self.base_model_path:
            model_args = getattr(config, "model_args", {}) or {}
            model_args["checkpoint_path"] = str(self.base_model_path)
            config.model_args = model_args
        trainer_args = getattr(config, "trainer_args", None)
        if trainer_args is not None:
            trainer_args.num_epochs = epochs

        trainer = Trainer(TrainerArgs(), config)
        trainer.fit()
        # Coqui saves checkpoints under output_path/run_name
        run_dir = Path(config.output_path) / config.run_name
        return run_dir
