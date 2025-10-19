# core
# category: core
# === File: campaign_frame.py ===
import json
from typing import Dict, List, Optional

class CampaignFrame:
    def __init__(self, data=None, name: str = None, monster_type_weights: Optional[Dict[str, float]] = None, difficulty_distribution: Dict[str, float] = None, rest_rules: Dict[str, float] = None, style: str = "", available_classes: Optional[List[str]] = None, monster_alignment_rules: Optional[Dict[str, any]] = None, guaranteed_hoards: bool = False, description: str = "", llm_model: Optional[str] = None, lora_adapter: Optional[str] = None, narrative_prompt: Optional[str] = None, tags: Optional[List[str]] = None):
        if isinstance(data, dict):
            # Initialize from dict (JSON loading)
            self.name = data.get('name', '')
            self.campaign_id = data.get('style', '')
            self.monster_type_weights = data.get('monster_type_weights', {})
            self.difficulty_distribution = data.get('difficulty_distribution', {})
            self.rest_rules = data.get('rest_rules', {})
            self.style = data.get('style', '')
            self.available_classes = data.get('available_classes', [])
            self.monster_alignment_rules = data.get('monster_alignment_rules', {})
            self.guaranteed_hoards = data.get('guaranteed_hoards', False)
            self.description = data.get('description', '')
            self.llm_model = data.get('llm_model')
            self.lora_adapter = data.get('lora_adapter')
            self.narrative_prompt = data.get('narrative_prompt')
            self.tags = data.get('tags', [])
        else:
            # Initialize from individual parameters
            self.name = name or data or ''
            self.campaign_id = style
            self.monster_type_weights = monster_type_weights or {}
            self.difficulty_distribution = difficulty_distribution or {}
            self.rest_rules = rest_rules or {}
            self.style = style
            self.available_classes = available_classes or []
            self.monster_alignment_rules = monster_alignment_rules or {}
            self.guaranteed_hoards = guaranteed_hoards
            self.description = description
            self.llm_model = llm_model
            self.lora_adapter = lora_adapter
            self.narrative_prompt = narrative_prompt
            self.tags = tags or []

    def to_dict(self):
        return {
            "name": self.name,
            "campaign_id": self.campaign_id,
            "monster_type_weights": self.monster_type_weights,
            "difficulty_distribution": self.difficulty_distribution,
            "rest_rules": self.rest_rules,
            "style": self.style,
            "available_classes": self.available_classes,
            "monster_alignment_rules": self.monster_alignment_rules,
            "guaranteed_hoards": self.guaranteed_hoards,
            "description": self.description,
            "llm_model": self.llm_model,
            "lora_adapter": self.lora_adapter,
            "narrative_prompt": self.narrative_prompt,
            "tags": self.tags,
        }

    def save_to_file(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load_from_file(path: str):
        with open(path) as f:
            data = json.load(f)
        return CampaignFrame(data)


