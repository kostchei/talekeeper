"""Wrapper around Piper TTS for local narration synthesis."""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Optional
import os

from .voice_profiles import CampaignVoiceProfile

LOGGER = logging.getLogger(__name__)


class LocalTTSEngine:
    """Uses Piper TTS for fast, local synthesis."""

    def __init__(
        self,
        model_path: Path,
        config_path: Optional[Path] = None,
        device: str = "auto",
    ) -> None:
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise RuntimeError(
                f"TTS model not found at {self.model_path}\n"
                f"Absolute path: {self.model_path.absolute()}\n"
                f"Please ensure the model file exists."
            )
        self.config_path = Path(config_path) if config_path else None
        if self.config_path and not self.config_path.exists():
            LOGGER.warning(f"TTS config not found at {self.config_path}, proceeding without it")
            self.config_path = None
        self.device = device
        self.piper_executable = self._find_piper()
        self._verify_piper()

    def _find_piper(self) -> str:
        local_piper = Path("bin/piper/piper/piper.exe")
        if local_piper.exists():
            return str(local_piper.absolute())
        return "piper"

    def _verify_piper(self) -> None:
        try:
            result = subprocess.run(
                [self.piper_executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise RuntimeError("Piper TTS not found or not executable")
            LOGGER.info(f"Piper TTS available: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError(
                "Piper TTS is required but not found. Install from https://github.com/rhasspy/piper"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Piper TTS verification timed out")

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
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        clean_text = ''.join(char for char in text if ord(char) < 128)

        speaking_rate = voice_profile.style.speaking_rate
        if style_overrides and "rate" in style_overrides:
            speaking_rate = style_overrides["rate"]

        cmd = [
            self.piper_executable,
            "--model", str(self.model_path),
            "--output_file", str(output_path),
        ]

        if self.config_path and self.config_path.exists():
            cmd.extend(["--config", str(self.config_path)])

        if speaking_rate != 1.0:
            cmd.extend(["--length_scale", str(1.0 / speaking_rate)])

        if voice_profile.metadata.get("speaker"):
            cmd.extend(["--speaker", voice_profile.metadata["speaker"]])

        LOGGER.debug(
            "Synthesizing narration with Piper",
            extra={
                "voice": voice_profile.voice_id,
                "model": str(self.model_path),
                "output": str(output_path),
                "rate": speaking_rate,
            }
        )

        try:
            result = subprocess.run(
                cmd,
                input=clean_text,
                text=True,
                capture_output=True,
                timeout=30,
            )
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "No error output"
                stdout_msg = result.stdout.strip() if result.stdout else "No stdout"
                raise RuntimeError(
                    f"Piper synthesis failed (exit code {result.returncode})\n"
                    f"Command: {' '.join(cmd)}\n"
                    f"Stderr: {error_msg}\n"
                    f"Stdout: {stdout_msg}\n"
                    f"Text: {clean_text[:100]}..."
                )

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise RuntimeError(f"Piper did not generate audio at {output_path}")

            LOGGER.info(f"Generated narration: {output_path.name}")
            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Piper synthesis timed out for text: {text[:50]}...")
