from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from audio.log_narration_pipeline import (
    LogLevel,
    LogNarrationEvent,
    LogNarrationPipeline,
    NarrationFormatter,
)
from audio.voice_profiles import CampaignVoiceProfile, VoiceStyleSettings
from audio.campaign_voice_registry import CampaignVoiceRegistry


class DummyEngine:
    def __init__(self):
        self.calls = []

    def synthesize(self, text, output_path: Path, voice_profile, *, style_overrides=None):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("dummy")
        self.calls.append({
            "text": text,
            "output_path": Path(output_path),
            "voice_id": voice_profile.voice_id,
            "style_overrides": style_overrides or {},
        })
        return output_path


def test_log_narration_event_from_payload():
    payload = {
        "message": "Attack hits",
        "level": "combat",
        "timestamp": "2024-01-01T12:30:00",
        "details": {"damage": 12},
    }
    event = LogNarrationEvent.from_payload(payload)
    assert event.level == LogLevel.COMBAT
    assert event.timestamp.year == 2024
    assert event.details["damage"] == 12


def test_narration_formatter_adds_details():
    formatter = NarrationFormatter()
    events = [
        LogNarrationEvent(
            message="Swing connects",
            level=LogLevel.COMBAT,
            timestamp=datetime.now(timezone.utc),
            details={"damage": 7, "target": "Goblin"},
        ),
        LogNarrationEvent(
            message="Saving throw succeeded",
            level=LogLevel.INFO,
            timestamp=datetime.now(timezone.utc),
            details={}
        ),
    ]
    result = formatter.format_batch(events)
    assert "Battle report" in result
    assert "dealing 7 damage" in result
    assert result.endswith(".")


def test_pipeline_process_entries_sync(tmp_path: Path):
    profile = CampaignVoiceProfile(
        campaign_style="default",
        voice_id="test_voice",
        model_path=tmp_path / "model.pth",
        style=VoiceStyleSettings(preset="narration", speaking_rate=1.0, energy=0.2),
    )
    registry = CampaignVoiceRegistry([profile], default_profile=profile)
    registry.set_active_campaign("default")

    engine = DummyEngine()
    pipeline = LogNarrationPipeline(
        log_panel=None,
        voice_registry=registry,
        engine_factory=lambda _: engine,
        output_directory=tmp_path / "audio",
        auto_start=False,
    )

    events = [
        LogNarrationEvent(
            message="Heavy slash",
            level=LogLevel.COMBAT,
            timestamp=datetime.now(timezone.utc),
            details={"damage": 9},
        )
    ]

    output_path = pipeline.process_entries_sync(events)
    assert output_path is not None
    assert output_path.exists()
    assert engine.calls, "Engine should have been invoked"
    overrides = engine.calls[0]["style_overrides"]
    assert overrides.get("energy", 0) >= profile.style.energy
