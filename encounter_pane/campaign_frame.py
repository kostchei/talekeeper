# === File: campaign_frame.py ===
import json
from typing import Dict, List

class CampaignFrame:
    def __init__(self, name: str, monster_type_weights: Dict[str, float], difficulty_distribution: Dict[str, float], rest_rules: Dict[str, float], style: str, available_classes: List[str] | None = None):
        self.name = name
        self.monster_type_weights = monster_type_weights
        self.difficulty_distribution = difficulty_distribution
        self.rest_rules = rest_rules
        self.style = style
        self.available_classes = available_classes or []

    def to_dict(self):
        return {
            "name": self.name,
            "monster_type_weights": self.monster_type_weights,
            "difficulty_distribution": self.difficulty_distribution,
            "rest_rules": self.rest_rules,
            "style": self.style,
            "available_classes": self.available_classes
        }

    def save_to_file(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load_from_file(path: str):
        with open(path) as f:
            data = json.load(f)
        return CampaignFrame(**data)


