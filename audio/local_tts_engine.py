"""Wrapper around a local open-source TTS model."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Optional

try:
    from TTS.api import TTS  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    TTS = None

from .voice_profiles import CampaignVoiceProfile

LOGGER = logging.getLogger(__name__)


class LocalTTSEngine:
    """Lazily loads a local model and performs synthesis on demand."""

    def __init__(
        self,
        model_path: Path,
        config_path: Optional[Path] = None,
        device: str = "auto",
    ) -> None:
        self.model_path = Path(model_path)
        self.config_path = Path(config_path) if config_path else None
        self.device = device
        if isinstance(device, bool):
            self._use_gpu = device
        else:
            normalized = str(device).lower()
            if normalized in {"cpu", "auto"}:
                self._use_gpu = False if normalized == "cpu" else None
            elif normalized in {"gpu", "cuda", "cuda:0"}:
                self._use_gpu = True
            else:
                self._use_gpu = None
        self._tts = None

    def _ensure_model(self) -> None:
        if self._tts is not None:
            return
        if TTS is None:
            raise RuntimeError(
                "The coqui-TTS package is required for local synthesis but is not installed."
            )
        kwargs = {"model_path": str(self.model_path), "progress_bar": False}
        if self.config_path:
            kwargs["config_path"] = str(self.config_path)
        if self._use_gpu is not None:
            kwargs["gpu"] = self._use_gpu
        self._tts = TTS(**kwargs)

    def synthesize(
        self,
        text: str,
        output_path: Path,
        voice_profile: CampaignVoiceProfile,
        *,
        speaker_wav: Optional[Path] = None,
        style_overrides: Optional[Dict[str, float]] = None,
    ) -> Path:
        """Generate an audio file that narrates ``text``."""
        self._ensure_model()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        synthesis_kwargs: Dict[str, float] = voice_profile.style.build_synthesis_kwargs()
        if style_overrides:
            synthesis_kwargs.update(style_overrides)

        # Coqui TTS expects JSON serializable kwargs
        safe_kwargs = json.loads(json.dumps(synthesis_kwargs))

        LOGGER.debug(
            "Synthesizing narration", extra={
                "voice": voice_profile.voice_id,
                "style": voice_profile.style.preset,
                "output": str(output_path),
                "kwargs": safe_kwargs,
            }
        )

        self._tts.tts_to_file(
            text=text,
            file_path=str(output_path),
            speaker_wav=str(speaker_wav) if speaker_wav else None,
            style_wav=str(voice_profile.sample_library) if voice_profile.sample_library else None,
            preset=voice_profile.style.preset,
            **safe_kwargs,
        )
        return output_path
