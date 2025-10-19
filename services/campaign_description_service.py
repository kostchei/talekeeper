# core
# core
"""Narrative description helper backed by a lightweight Ollama model.

This service builds a rich prompt using campaign frame data and entity context
(monsters, vendors, hazards, traps) and asks a small language model hosted by
Ollama to produce a short descriptive blurb. The service is designed to work in
resource-constrained environments (≤16 GB) by defaulting to a light-weight
model such as ``mistral:7b-instruct``. When Ollama is unavailable the generator
falls back to deterministic text so that the rest of the application continues
functioning.
"""
from __future__ import annotations

import importlib.util
import json
import os
from dataclasses import dataclass
from string import Template
from typing import Any, Dict, Optional, List

from services.tarot_cards import draw_tarot_card, get_tarot_inspiration


def _load_requests_module():
    if importlib.util.find_spec("requests") is None:
        class _RequestsStub:
            class RequestException(RuntimeError):
                """Raised when HTTP requests are unavailable."""

            class Session:  # noqa: D401 - simple stub
                def post(self, *args, **kwargs):  # noqa: D401 - simple stub
                    raise _RequestsStub.RequestException(
                        "The 'requests' package is required for Ollama integration."
                    )

        return _RequestsStub()

    import requests  # type: ignore

    return requests


requests = _load_requests_module()


@dataclass
class DescriptionRequest:
    """Container for the information required to build a prompt."""

    entity_type: str
    entity_data: Dict[str, Any]
    campaign_frame: Any  # Deliberately loose typing to avoid circular imports


class CampaignDescriptionService:
    """Generate campaign-aware descriptions using a local Ollama model."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        request_timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.default_model = default_model or os.getenv("OLLAMA_MODEL", "mistral:7b-instruct")
        self.request_timeout = request_timeout
        self.session = requests.Session()

        # Default prompt uses string.Template placeholders to avoid brace escaping
        self._default_prompt = Template(
            """
You are the narrative voice for the $campaign_name campaign.
Campaign tone: $campaign_style
Campaign summary: $campaign_description

Write 2-3 sentences that vividly describe the $entity_type named $entity_name.
Keep the response under 70 words, focus on mood and stakes, and avoid game
mechanics unless they reinforce the tone. Use the structured reference data
below as inspiration:
$entity_json
"""
        )

        self._combat_event_prompt = Template(
            """
You are narrating a $campaign_style combat encounter.

Combat Event:
$events_json

Write 1-2 vivid sentences describing this action. Keep under 50 words.
Focus on action, atmosphere, and stakes. Avoid repeating mechanical details.
Campaign tone: $campaign_description
"""
        )

        self._round_summary_prompt = Template(
            """
You are narrating a $campaign_style combat round.

Round Events:
$round_events_json

Write 2-3 sentences summarizing this combat round. Keep under 70 words.
Emphasize momentum shifts and dramatic moments.
Campaign tone: $campaign_description
"""
        )

        self._victory_prompt = Template(
            """
You are narrating the aftermath of a $campaign_style combat victory.

Combat Summary:
$combat_summary_json

Write 2-3 sentences describing the aftermath. Keep under 70 words.
Focus on cost of victory and spoils.
Campaign tone: $campaign_description
"""
        )

        self._encounter_prompt = Template(
            """
You are narrating a $campaign_style encounter.

Tarot inspiration: $tarot_inspiration

Monsters in this encounter (appearing together):
$monsters_json

Write your description in this exact structure:

PARAGRAPH 1: Begin with the tarot inspiration, then describe the place and situation where these monsters appear. Write 2-3 sentences that set the scene.

PARAGRAPH 2: For each unique monster type, write a bullet point with the monster name followed by a 1-sentence description of its appearance or behavior.

Example structure (DO NOT use brackets - write actual descriptions):
The tavern reeks of betrayal and false friendship. In this dimly lit corner, suspicious figures gather around crude wooden tables.

- Goblin: Small, green-skinned creatures with yellow eyes that gleam with malice
- Hobgoblin: A battle-scarred warrior towering over the goblins

Keep total under 120 words.
Campaign tone: $campaign_description
"""
        )

    def generate_description(
        self,
        entity_type: str,
        entity_data: Optional[Dict[str, Any]],
        campaign_frame: Any,
    ) -> Optional[str]:
        """Return a short description or ``None`` if generation fails.

        Parameters
        ----------
        entity_type:
            Category of content (``monster``, ``vendor``, ``hazard``, ``trap``).
        entity_data:
            Structured details about the entity. When ``None`` a fallback string
            is returned.
        campaign_frame:
            Campaign metadata used to tailor the tone and LoRA adapter.
        """

        if not entity_data:
            return self._fallback_description(entity_type, {}, campaign_frame)

        request = DescriptionRequest(entity_type=entity_type, entity_data=entity_data, campaign_frame=campaign_frame)

        try:
            prompt = self._build_prompt(request)
        except Exception as exc:  # noqa: BLE001 - defensive conversion to fallback
            print(f"[LLM] Failed to build prompt: {exc}")
            return self._fallback_description(entity_type, entity_data, campaign_frame)

        payload: Dict[str, Any] = {
            "model": getattr(campaign_frame, "llm_model", None) or self.default_model,
            "prompt": prompt,
            "stream": False,
        }

        lora_adapter = getattr(campaign_frame, "lora_adapter", None)
        if lora_adapter:
            payload["options"] = {"lora": lora_adapter}

        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response")
            if isinstance(text, str) and text.strip():
                return text.strip()

            # Some Ollama builds return streaming chunks even with ``stream=False``
            # and aggregate them under ``data``.
            if "data" in data and isinstance(data["data"], list):
                combined = "".join(chunk.get("response", "") for chunk in data["data"] if isinstance(chunk, dict))
                if combined.strip():
                    return combined.strip()

        except requests.RequestException as exc:
            print(f"[LLM] Ollama request failed: {exc}")
        except ValueError as exc:  # JSON decoding errors
            print(f"[LLM] Failed to parse Ollama response: {exc}")

        return self._fallback_description(entity_type, entity_data, campaign_frame)

    def generate_combat_narrative(
        self,
        combat_events: List[Dict[str, Any]],
        campaign_frame: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:

        if not combat_events:
            return None

        events_json = json.dumps(combat_events, indent=2)

        prompt_template_text = getattr(campaign_frame, "narrative_combat_prompt", None) or self._combat_event_prompt.template
        template = Template(prompt_template_text)

        prompt = template.safe_substitute(
            campaign_name=getattr(campaign_frame, "name", "Unnamed Campaign") or "Unnamed Campaign",
            campaign_style=getattr(campaign_frame, "style", "") or "distinctive fantasy",
            campaign_description=getattr(campaign_frame, "description", "") or "",
            events_json=events_json
        )

        return self._generate_from_prompt(prompt.strip(), campaign_frame)

    def generate_round_summary(
        self,
        round_events: List[Dict[str, Any]],
        campaign_frame: Any
    ) -> Optional[str]:

        if not round_events:
            return None

        round_events_json = json.dumps(round_events, indent=2)

        prompt_template_text = getattr(campaign_frame, "narrative_round_summary_prompt", None) or self._round_summary_prompt.template
        template = Template(prompt_template_text)

        prompt = template.safe_substitute(
            campaign_name=getattr(campaign_frame, "name", "Unnamed Campaign") or "Unnamed Campaign",
            campaign_style=getattr(campaign_frame, "style", "") or "distinctive fantasy",
            campaign_description=getattr(campaign_frame, "description", "") or "",
            round_events_json=round_events_json
        )

        return self._generate_from_prompt(prompt.strip(), campaign_frame)

    def generate_victory_narrative(
        self,
        combat_summary: Dict[str, Any],
        campaign_frame: Any
    ) -> Optional[str]:

        if not combat_summary:
            return None

        combat_summary_json = json.dumps(combat_summary, indent=2)

        prompt_template_text = getattr(campaign_frame, "narrative_victory_prompt", None) or self._victory_prompt.template
        template = Template(prompt_template_text)

        prompt = template.safe_substitute(
            campaign_name=getattr(campaign_frame, "name", "Unnamed Campaign") or "Unnamed Campaign",
            campaign_style=getattr(campaign_frame, "style", "") or "distinctive fantasy",
            campaign_description=getattr(campaign_frame, "description", "") or "",
            combat_summary_json=combat_summary_json
        )

        return self._generate_from_prompt(prompt.strip(), campaign_frame)

    def generate_encounter_description(
        self,
        monsters: List[Dict[str, Any]],
        campaign_frame: Any,
        level: int,
        difficulty: str
    ) -> Optional[Dict[str, Any]]:

        if not monsters:
            return None

        tarot_card = draw_tarot_card()
        tarot_inspiration = get_tarot_inspiration(tarot_card)

        monsters_json = json.dumps([{
            "name": m.get("name"),
            "type": m.get("type"),
            "cr": m.get("cr_str", m.get("cr")),
            "alignment": m.get("alignment")
        } for m in monsters], indent=2)

        prompt_template_text = getattr(campaign_frame, "narrative_encounter_prompt", None) or self._encounter_prompt.template
        template = Template(prompt_template_text)

        prompt = template.safe_substitute(
            campaign_name=getattr(campaign_frame, "name", "Unnamed Campaign") or "Unnamed Campaign",
            campaign_style=getattr(campaign_frame, "style", "") or "distinctive fantasy",
            campaign_description=getattr(campaign_frame, "description", "") or "",
            monsters_json=monsters_json,
            tarot_inspiration=tarot_inspiration,
            tarot_card=tarot_card["name"],
            tarot_orientation=tarot_card["orientation"]
        )

        description = self._generate_from_prompt(prompt.strip(), campaign_frame)

        return {
            "description": description,
            "tarot_card": tarot_card["name"],
            "tarot_orientation": tarot_card["orientation"],
            "tarot_aspect": tarot_card["aspect"],
            "tarot_detail": tarot_card["detail"]
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _generate_from_prompt(self, prompt: str, campaign_frame: Any) -> Optional[str]:

        payload: Dict[str, Any] = {
            "model": getattr(campaign_frame, "llm_model", None) or self.default_model,
            "prompt": prompt,
            "stream": False,
        }

        lora_adapter = getattr(campaign_frame, "lora_adapter", None)
        if lora_adapter:
            payload["options"] = {"lora": lora_adapter}

        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response")
            if isinstance(text, str) and text.strip():
                return text.strip()

            if "data" in data and isinstance(data["data"], list):
                combined = "".join(chunk.get("response", "") for chunk in data["data"] if isinstance(chunk, dict))
                if combined.strip():
                    return combined.strip()

        except requests.RequestException as exc:
            print(f"[LLM] Ollama request failed: {exc}")
        except ValueError as exc:
            print(f"[LLM] Failed to parse Ollama response: {exc}")

        return None

    def _build_prompt(self, request: DescriptionRequest) -> str:
        campaign = request.campaign_frame
        entity_data = request.entity_data
        entity_name = entity_data.get("name") or entity_data.get("title") or entity_data.get("id", request.entity_type.title())

        # Create JSON block and escape braces for Template substitution.
        entity_json = json.dumps(entity_data, indent=2, sort_keys=True)

        prompt_template_text = getattr(campaign, "narrative_prompt", None) or self._default_prompt.template
        template = Template(prompt_template_text)

        prompt = template.safe_substitute(
            campaign_name=getattr(campaign, "name", "Unnamed Campaign") or "Unnamed Campaign",
            campaign_style=getattr(campaign, "style", "") or "distinctive fantasy",
            campaign_description=getattr(campaign, "description", "") or "",
            entity_type=request.entity_type,
            entity_name=entity_name,
            entity_json=entity_json,
        )
        return prompt.strip()

    def _fallback_description(
        self,
        entity_type: str,
        entity_data: Dict[str, Any],
        campaign_frame: Any,
    ) -> str:
        """Return a deterministic blurb when Ollama is unavailable."""

        campaign_style = getattr(campaign_frame, "style", "") or getattr(campaign_frame, "name", "the campaign")
        campaign_desc = getattr(campaign_frame, "description", "")
        descriptor = campaign_desc if campaign_desc else f"the {campaign_style} setting"

        name = entity_data.get("name") or entity_data.get("title") or entity_data.get("type", entity_type.title())

        if entity_type == "monster":
            creature_type = entity_data.get("type", "creature")
            return (
                f"{name} embodies the dangers of {descriptor}. Its {creature_type} instincts and presence hint at the "
                "challenges awaiting bold adventurers."
            )
        if entity_type == "vendor":
            size = entity_data.get("shop_size", "travelling")
            stock = entity_data.get("inventory_count") or "an assortment of"
            return (
                f"A {size} merchant tied to {descriptor} lays out {stock} wares, their patter coloured by local legends "
                "and whispered opportunities."
            )
        if entity_type == "hazard":
            hazard_name = name or "hazard"
            effect = entity_data.get("effect") or entity_data.get("failure_effect") or "lingering danger"
            return (
                f"{hazard_name} lurks in {descriptor}, threatening travellers with {effect}. Keen senses and teamwork are "
                "the surest defence."
            )
        if entity_type == "trap":
            trap_type = entity_data.get("type", "hidden device")
            danger = entity_data.get("effects") or entity_data.get("damage") or "harm"
            return (
                f"A {trap_type.lower()} trap crafted in {descriptor} waits patiently to unleash {danger}. Observant "
                "adventurers might still twist fate in their favour."
            )

        return f"The {entity_type} reflects the tone of {descriptor}, adding colour to the adventure."
