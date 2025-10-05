"""Registry that maps campaign frames to trained voice profiles."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional

from .voice_profiles import CampaignVoiceProfile


class CampaignVoiceRegistry:
    """Stores campaign voice profiles and tracks the active selection."""

    def __init__(
        self,
        profiles: Optional[Iterable[CampaignVoiceProfile]] = None,
        default_profile: Optional[CampaignVoiceProfile] = None,
    ) -> None:
        self._profiles: Dict[str, CampaignVoiceProfile] = {}
        if profiles:
            for profile in profiles:
                self.register_profile(profile)
        self._default_profile = default_profile
        if default_profile and default_profile.campaign_style not in self._profiles:
            self.register_profile(default_profile)
        self._active_style: Optional[str] = (
            default_profile.campaign_style if default_profile else None
        )

    def register_profile(self, profile: CampaignVoiceProfile) -> None:
        """Add or replace a campaign voice profile."""
        style_key = profile.normalized_style()
        self._profiles[style_key] = profile

    def set_active_campaign(self, campaign_style: Optional[str]) -> None:
        """Update the active campaign style, falling back to the default."""
        if campaign_style is None:
            self._active_style = (
                self._default_profile.normalized_style() if self._default_profile else None
            )
            return
        normalized = campaign_style.lower().replace(" ", "_")
        if normalized in self._profiles:
            self._active_style = normalized
        elif self._default_profile:
            self._active_style = self._default_profile.normalized_style()
        else:
            self._active_style = None

    def get_active_profile(self) -> Optional[CampaignVoiceProfile]:
        """Return the profile that should be used for narration."""
        if self._active_style and self._active_style in self._profiles:
            return self._profiles[self._active_style]
        return self._default_profile

    def ensure_profile(
        self,
        campaign_style: str,
        voice_id: str,
        model_path: Path,
    ) -> CampaignVoiceProfile:
        """Create a placeholder profile if one does not exist."""
        normalized = campaign_style.lower().replace(" ", "_")
        profile = self._profiles.get(normalized)
        if profile:
            return profile
        profile = CampaignVoiceProfile(
            campaign_style=campaign_style,
            voice_id=voice_id,
            model_path=model_path,
        )
        self._profiles[normalized] = profile
        return profile

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """Return a serializable snapshot useful for debugging."""
        return {key: profile.to_dict() for key, profile in self._profiles.items()}
