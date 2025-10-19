# core
# category: utility
"""Convert log panel events into narrated audio."""

from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

try:  # pragma: no cover - optional dependency during headless tests
    from log.log_panel import LogLevel
except Exception:  # pragma: no cover - fallback when PyQt/GL is unavailable
    from enum import Enum

    class LogLevel(Enum):
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
        COMBAT = "combat"
        DICE = "dice"
        SYSTEM = "system"

from .campaign_voice_registry import CampaignVoiceRegistry
from .local_tts_engine import LocalTTSEngine
from .voice_profiles import CampaignVoiceProfile
from .audio_player import NarrationPlayer
from .file_cleanup import NarrationFileCleanup

LOGGER = logging.getLogger(__name__)


@dataclass
class LogNarrationEvent:
    """Normalized representation of a log entry."""

    message: str
    level: LogLevel
    timestamp: datetime
    details: Dict[str, object]

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "LogNarrationEvent":
        raw_level = payload.get("level")
        if isinstance(raw_level, LogLevel):
            level = raw_level
        else:
            try:
                level = LogLevel(raw_level)
            except Exception:  # pragma: no cover - defensive
                level = LogLevel.INFO
        timestamp = payload.get("timestamp")
        if isinstance(timestamp, datetime):
            parsed_ts = timestamp
        elif isinstance(timestamp, str):
            parsed_ts = datetime.fromisoformat(timestamp)
        else:
            parsed_ts = datetime.utcnow()
        return cls(
            message=str(payload.get("message", "")).strip(),
            level=level,
            timestamp=parsed_ts,
            details=dict(payload.get("details") or {}),
        )


class NarrationFormatter:
    """Convert structured log events into narration-friendly sentences."""

    LEVEL_TEMPLATES = {
        LogLevel.INFO: "{message}.",
        LogLevel.WARNING: "Warning: {message}.",
        LogLevel.ERROR: "Error: {message}.",
        LogLevel.COMBAT: "Battle report: {message}.",
        LogLevel.DICE: "Dice result: {message}.",
        LogLevel.SYSTEM: "System note: {message}.",
    }

    def format_batch(self, events: Iterable[LogNarrationEvent]) -> str:
        sentences: List[str] = []
        for event in events:
            template = self.LEVEL_TEMPLATES.get(event.level, "{message}.")
            message = event.message.rstrip(". ")
            if not message:
                continue
            detail_suffix = self._format_details(event)
            sentence = template.format(message=message)
            if detail_suffix:
                sentence = f"{sentence} {detail_suffix}".strip()
            sentences.append(sentence)
        return " ".join(sentences)

    def _format_details(self, event: LogNarrationEvent) -> str:
        details = event.details or {}
        if not details:
            return ""
        fragments = []
        if "roll" in details:
            fragments.append(f"Roll {details['roll']}")
        if "damage" in details:
            fragments.append(f"dealing {details['damage']} damage")
        if "target" in details:
            fragments.append(f"to {details['target']}")
        return " ".join(fragments)


class LogNarrationPipeline:
    """Coordinates log listening, formatting, and synthesis."""

    def __init__(
        self,
        log_panel,
        voice_registry: CampaignVoiceRegistry,
        *,
        engine_factory: Optional[Callable[[CampaignVoiceProfile], LocalTTSEngine]] = None,
        output_directory: Path | str = Path("excess") / "narration",
        batch_window_seconds: float = 2.5,
        auto_start: bool = True,
        audio_player: Optional[NarrationPlayer] = None,
    ) -> None:
        self.log_panel = log_panel
        self.voice_registry = voice_registry
        self.output_directory = Path(output_directory)
        self.batch_window_seconds = batch_window_seconds
        self.formatter = NarrationFormatter()
        self.engine_factory = engine_factory or (lambda profile: LocalTTSEngine(profile.model_path))
        self._queue: "queue.Queue[LogNarrationEvent]" = queue.Queue()
        self._stop_event = threading.Event()
        self._worker: Optional[threading.Thread] = None
        self._engine_cache: Dict[str, LocalTTSEngine] = {}
        self._active_campaign_style: Optional[str] = None
        self.audio_player = audio_player
        self.file_cleanup = NarrationFileCleanup(self.output_directory, max_age_hours=24, max_files=500)
        if auto_start:
            self.start()

    def start(self) -> None:
        if self.log_panel is not None and hasattr(self.log_panel, "log_message_added"):
            try:
                self.log_panel.log_message_added.connect(self.enqueue_payload)
            except Exception:  # pragma: no cover - guard against PyQt runtime issues
                LOGGER.exception("Unable to connect narration pipeline to log panel")
        if self._worker is None or not self._worker.is_alive():
            self._stop_event.clear()
            self._worker = threading.Thread(target=self._process_loop, daemon=True)
            self._worker.start()
        self.file_cleanup.run_cleanup()
        LOGGER.info("Narration pipeline started")

    def stop(self) -> None:
        if self.log_panel is not None and hasattr(self.log_panel, "log_message_added"):
            try:
                self.log_panel.log_message_added.disconnect(self.enqueue_payload)
            except Exception:  # pragma: no cover - guard against PyQt runtime issues
                pass
        self._stop_event.set()
        if self._worker is not None:
            self._worker.join(timeout=1.0)
        self._worker = None

    def enqueue_payload(self, payload: Dict[str, object]) -> None:
        event = LogNarrationEvent.from_payload(payload)
        self.enqueue_event(event)

    def enqueue_event(self, event: LogNarrationEvent) -> None:
        LOGGER.debug("Queued log narration event", extra={"level": event.level.name, "message": event.message})
        self._queue.put(event)

    def update_campaign_voice(self, campaign_style: Optional[str]) -> None:
        self._active_campaign_style = campaign_style
        self.voice_registry.set_active_campaign(campaign_style)

    def process_entries_sync(self, events: Iterable[LogNarrationEvent]) -> Optional[Path]:
        batch = list(events)
        if not batch:
            return None
        try:
            return self._synthesize_batch(batch)
        except Exception:
            LOGGER.exception("Narration synthesis failed during synchronous processing")
            return None

    def _process_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                event = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            batch = [event]
            deadline = time.monotonic() + self.batch_window_seconds
            while time.monotonic() < deadline:
                try:
                    next_event = self._queue.get(timeout=0.1)
                    batch.append(next_event)
                except queue.Empty:
                    break
            try:
                self._synthesize_batch(batch)
            except Exception:
                LOGGER.exception("Narration synthesis failed")

    def _synthesize_batch(self, batch: List[LogNarrationEvent]) -> Optional[Path]:
        profile = self.voice_registry.get_active_profile()
        if not profile:
            LOGGER.debug("No active voice profile; skipping narration batch")
            return None
        text = self.formatter.format_batch(batch)
        if not text.strip():
            return None
        timestamp = batch[-1].timestamp
        output_path = self.output_directory / f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.wav"
        try:
            engine = self._get_engine(profile)
        except Exception as e:
            LOGGER.error(
                f"Unable to initialize TTS engine for voice {profile.voice_id}: {e}\n"
                f"Model path: {profile.model_path}\n"
                f"Campaign style: {self._active_campaign_style}"
            )
            return None
        style_overrides = self._derive_style_overrides(batch, profile)
        LOGGER.info(
            "Rendering narration clip",
            extra={"text": text, "output_path": str(output_path), "campaign_style": self._active_campaign_style},
        )
        try:
            engine.synthesize(text, output_path, profile, style_overrides=style_overrides)
        except Exception as e:
            LOGGER.error(f"TTS synthesis failed: {e}")
            return None

        if self.audio_player and output_path.exists():
            self.audio_player.enqueue(output_path)

        return output_path

    def _derive_style_overrides(
        self, batch: List[LogNarrationEvent], profile: CampaignVoiceProfile
    ) -> Dict[str, float]:
        overrides: Dict[str, float] = {}
        if any(event.level == LogLevel.COMBAT for event in batch):
            overrides.setdefault("energy", max(profile.style.energy, 0.35))
        if any(event.level == LogLevel.DICE for event in batch):
            overrides.setdefault("rate", profile.style.speaking_rate + 0.05)
        if any(event.level == LogLevel.SYSTEM for event in batch):
            overrides.setdefault("rate", profile.style.speaking_rate * 0.95)
        return overrides

    def _get_engine(self, profile: CampaignVoiceProfile) -> LocalTTSEngine:
        engine = self._engine_cache.get(profile.voice_id)
        if engine is None:
            engine = self.engine_factory(profile)
            self._engine_cache[profile.voice_id] = engine
        return engine
