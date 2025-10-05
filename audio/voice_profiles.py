"""Voice profile and style configuration objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class VoiceStyleSettings:
    """Fine-tuning controls applied when generating narration."""

    preset: str = "default"
    speaking_rate: float = 1.0
    energy: float = 0.0
    pitch_shift: float = 0.0
    emotion: Optional[str] = None
    additional_params: Dict[str, float] = field(default_factory=dict)

    def build_synthesis_kwargs(self) -> Dict[str, float]:
        """Return keyword arguments understood by the local TTS engine."""
        kwargs: Dict[str, float] = {
            "rate": self.speaking_rate,
            "energy": self.energy,
            "pitch_shift": self.pitch_shift,
        }
        if self.emotion:
            kwargs["emotion"] = self.emotion
        kwargs.update(self.additional_params)
        return kwargs


@dataclass
class CampaignVoiceProfile:
    """Represents a trained voice tied to a specific campaign frame."""

    campaign_style: str
    voice_id: str
    model_path: Path
    style: VoiceStyleSettings = field(default_factory=VoiceStyleSettings)
    sample_library: Optional[Path] = None
    description: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def normalized_style(self) -> str:
        return self.campaign_style.lower().replace(" ", "_")

    def to_dict(self) -> Dict[str, str]:
        """Serialize profile for persistence or debugging."""
        payload = {
            "campaign_style": self.campaign_style,
            "voice_id": self.voice_id,
            "model_path": str(self.model_path),
            "style_preset": self.style.preset,
        }
        if self.sample_library:
            payload["sample_library"] = str(self.sample_library)
        if self.description:
            payload["description"] = self.description
        payload.update(self.metadata)
        return payload
