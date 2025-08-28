"""
File: models/monsters_indexeddb.py
Path: /models/monsters_indexeddb.py

IndexedDB-compatible monster models for TaleKeeper Desktop.
Replaces SQLAlchemy Monster model with plain Python dataclass.

Pseudo Code:
1. Define Monster dataclass with complete D&D stat block
2. Store AI behavior scripts for different monster types
3. Handle special abilities, attacks, and spellcasting
4. Manage encounter difficulty and challenge rating
5. Process monster actions during combat turns

AI Agents: Combat encounters with full stat blocks and AI behavior patterns.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from enum import Enum


class MonsterType(str, Enum):
    """D&D monster types."""
    ABERRATION = "aberration"
    BEAST = "beast"
    CELESTIAL = "celestial"
    CONSTRUCT = "construct"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    FEY = "fey"
    FIEND = "fiend"
    GIANT = "giant"
    HUMANOID = "humanoid"
    MONSTROSITY = "monstrosity"
    OOZE = "ooze"
    PLANT = "plant"
    UNDEAD = "undead"


class MonsterSize(str, Enum):
    """D&D monster sizes."""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"


@dataclass
class Monster:
    """
    D&D Monster with complete stat block for IndexedDB storage.
    AI Agents: Extend with new monster abilities and AI behaviors.
    """
    # Primary key
    name: str = ""
    challenge_rating: float = 0.0
    size: str = "Medium"
    type: str = "humanoid"
    alignment: str = "neutral"
    armor_class: int = 10
    hit_points: int = 8
    hit_dice: str = "1d8"
    speed: Dict[str, int] = field(default_factory=lambda: {"walk": 30})
    
    # Ability scores
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    # Proficiencies and resistances
    saving_throws: Dict[str, int] = field(default_factory=dict)
    skills: Dict[str, int] = field(default_factory=dict)
    damage_vulnerabilities: List[str] = field(default_factory=list)
    damage_resistances: List[str] = field(default_factory=list)
    damage_immunities: List[str] = field(default_factory=list)
    condition_immunities: List[str] = field(default_factory=list)
    senses: Dict[str, int] = field(default_factory=dict)
    languages: List[str] = field(default_factory=list)
    
    # Combat abilities
    actions: List[Dict[str, Any]] = field(default_factory=list)
    reactions: List[Dict[str, Any]] = field(default_factory=list)
    legendary_actions: List[Dict[str, Any]] = field(default_factory=list)
    special_abilities: List[Dict[str, Any]] = field(default_factory=list)
    
    # AI and rewards
    ai_script: Optional[str] = None
    loot_table: Dict[str, Any] = field(default_factory=dict)
    xp_value: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def strength_modifier(self) -> int:
        return (self.strength - 10) // 2 if self.strength else 0
    
    @property
    def dexterity_modifier(self) -> int:
        return (self.dexterity - 10) // 2 if self.dexterity else 0
    
    @property
    def constitution_modifier(self) -> int:
        return (self.constitution - 10) // 2 if self.constitution else 0
    
    @property
    def intelligence_modifier(self) -> int:
        return (self.intelligence - 10) // 2 if self.intelligence else 0
    
    @property
    def wisdom_modifier(self) -> int:
        return (self.wisdom - 10) // 2 if self.wisdom else 0
    
    @property
    def charisma_modifier(self) -> int:
        return (self.charisma - 10) // 2 if self.charisma else 0
    
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on CR."""
        if not self.challenge_rating:
            return 2
        cr = float(self.challenge_rating)
        if cr <= 4:
            return 2
        elif cr <= 8:
            return 3
        elif cr <= 12:
            return 4
        elif cr <= 16:
            return 5
        else:
            return 6
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert monster to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Monster':
        """Create monster from dictionary from IndexedDB."""
        # Handle missing fields gracefully
        defaults = {
            'speed': {"walk": 30},
            'saving_throws': {},
            'skills': {},
            'damage_vulnerabilities': [],
            'damage_resistances': [],
            'damage_immunities': [],
            'condition_immunities': [],
            'senses': {},
            'languages': [],
            'actions': [],
            'reactions': [],
            'legendary_actions': [],
            'special_abilities': [],
            'loot_table': {},
            'created_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        # Remove unexpected fields that might come from IndexedDB
        expected_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in expected_fields}
        
        return cls(**filtered_data)
    
    def to_display_dict(self) -> Dict[str, Any]:
        """Convert monster to dictionary for display in UI."""
        return {
            "name": self.name,
            "challenge_rating": self.challenge_rating,
            "size": self.size,
            "type": self.type,
            "alignment": self.alignment,
            "armor_class": self.armor_class,
            "hit_points": self.hit_points,
            "hit_dice": self.hit_dice,
            "speed": self.speed or {},
            "ability_scores": {
                "strength": self.strength,
                "dexterity": self.dexterity,
                "constitution": self.constitution,
                "intelligence": self.intelligence,
                "wisdom": self.wisdom,
                "charisma": self.charisma
            },
            "modifiers": {
                "strength": self.strength_modifier,
                "dexterity": self.dexterity_modifier,
                "constitution": self.constitution_modifier,
                "intelligence": self.intelligence_modifier,
                "wisdom": self.wisdom_modifier,
                "charisma": self.charisma_modifier
            },
            "saving_throws": self.saving_throws or {},
            "skills": self.skills or {},
            "damage_vulnerabilities": self.damage_vulnerabilities or [],
            "damage_resistances": self.damage_resistances or [],
            "damage_immunities": self.damage_immunities or [],
            "condition_immunities": self.condition_immunities or [],
            "senses": self.senses or {},
            "languages": self.languages or [],
            "actions": self.actions or [],
            "reactions": self.reactions or [],
            "legendary_actions": self.legendary_actions or [],
            "special_abilities": self.special_abilities or [],
            "ai_script": self.ai_script,
            "loot_table": self.loot_table or {},
            "xp_value": self.xp_value,
            "proficiency_bonus": self.proficiency_bonus
        }