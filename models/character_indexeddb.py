"""
Character Data Models for TaleKeeper Desktop

Dataclass-based character models for IndexedDB storage.
Implements D&D 2024 character rules and statistics.

Models:
- Character: Player character with stats, equipment, and progression
- Race: Character species with traits and bonuses
- Class: Character class with features and progression
- Subclass: Specialized class variants
- Background: Character background with proficiencies

Features:
- Computed ability modifiers
- JSON serialization/deserialization
- D&D 2024 rule compliance
- Equipment slot management
- Character progression tracking
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
import json


@dataclass
class Character:
    """
    D&D Character with 2024 rules for IndexedDB storage.
    AI Agents: Extend with class-specific features and spell slots.
    """
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    save_slot_id: Optional[str] = None
    name: str = ""
    
    # Core D&D Stats
    race_id: str = ""
    class_id: str = ""
    subclass_id: Optional[str] = None
    background_id: str = ""
    
    level: int = 1
    experience_points: int = 0
    
    # Ability Scores (1-20 range, with racial bonuses)
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    # Calculated Values (updated when stats change)
    armor_class: int = 10
    hit_points_max: int = 8
    hit_points_current: int = 8
    hit_points_temporary: int = 0
    
    # Alternative field names used by combat system
    max_hit_points: int = 8
    current_hit_points: int = 8
    hit_dice_max: int = 1
    hit_dice_current: int = 1
    death_saves_successes: int = 0
    death_saves_failures: int = 0
    conditions: List[str] = field(default_factory=list)
    
    # Proficiencies and Features
    proficiencies: List[str] = field(default_factory=list)  # Skills, tools, languages
    features: Dict[str, Any] = field(default_factory=dict)  # Class and racial features
    feats: List[str] = field(default_factory=list)  # Character feats by name
    weapon_masteries: List[str] = field(default_factory=list)  # Weapon mastery selections
    
    # Equipment slots
    equipment_main_hand: Optional[str] = None
    equipment_off_hand: Optional[str] = None
    equipment_armor: Optional[str] = None
    equipment_shield: Optional[str] = None
    
    # Metadata
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    notes: str = ""

    @property
    def strength_modifier(self) -> int:
        return (self.strength - 10) // 2
    
    @property
    def dexterity_modifier(self) -> int:
        return (self.dexterity - 10) // 2
    
    @property
    def constitution_modifier(self) -> int:
        return (self.constitution - 10) // 2
    
    @property
    def intelligence_modifier(self) -> int:
        return (self.intelligence - 10) // 2
    
    @property
    def wisdom_modifier(self) -> int:
        return (self.wisdom - 10) // 2
    
    @property
    def charisma_modifier(self) -> int:
        return (self.charisma - 10) // 2
    
    @property
    def proficiency_bonus(self) -> int:
        return (self.level - 1) // 4 + 2
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Create character from dictionary from IndexedDB."""
        # Handle missing fields gracefully
        defaults = {
            'id': str(uuid4()),
            'conditions': [],
            'proficiencies': [],
            'features': {},
            'created_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return cls(**data)
    
    def to_display_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary for display in UI."""
        return {
            "id": str(self.id),
            "name": self.name,
            "level": self.level,
            "experience_points": self.experience_points,
            "race_id": self.race_id,
            "class_id": self.class_id,
            "subclass_id": self.subclass_id,
            "background_id": self.background_id,
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
            "combat_stats": {
                "armor_class": self.armor_class,
                "hit_points_max": self.hit_points_max,
                "hit_points_current": self.hit_points_current,
                "hit_points_temporary": self.hit_points_temporary,
                "proficiency_bonus": self.proficiency_bonus
            },
            "proficiencies": self.proficiencies or [],
            "features": self.features or {},
            "created_at": self.created_at,
            "notes": self.notes
        }


@dataclass
class Race:
    """Character races with D&D 2024 rules for IndexedDB storage."""
    # Primary key (use name as ID)
    name: str = ""
    description: str = ""
    
    # Ability Score Increases
    ability_score_increases: Dict[str, int] = field(default_factory=dict)  # e.g., {"strength": 2, "constitution": 1}
    
    # Racial features
    size: str = "Medium"
    speed: int = 30
    languages: List[str] = field(default_factory=list)  # e.g., ["Common", "Dwarvish"]
    proficiencies: List[str] = field(default_factory=list)  # Skills, tools, weapons
    traits: Dict[str, Any] = field(default_factory=dict)  # Special racial traits
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert race to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Race':
        """Create race from dictionary from IndexedDB."""
        # Remove unexpected fields that might come from IndexedDB
        expected_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in expected_fields}
        return cls(**filtered_data)


@dataclass
class Class:
    """Character classes with D&D 2024 rules for IndexedDB storage."""
    # Primary key (use name as ID)
    name: str = ""
    description: str = ""
    
    # Core class mechanics
    hit_die: int = 8  # d8, d10, etc.
    primary_ability: str = ""  # "Strength" or "Dexterity"
    saving_throw_proficiencies: List[str] = field(default_factory=list)  # e.g., ["strength", "constitution"]
    
    # Proficiencies granted
    armor_proficiencies: List[str] = field(default_factory=list)
    weapon_proficiencies: List[str] = field(default_factory=list)
    skill_proficiencies: List[str] = field(default_factory=list)  # Available skills to choose from
    skill_choices: int = 2  # Number of skills player can choose
    
    # Equipment and features
    starting_equipment: Dict[str, Any] = field(default_factory=dict)
    equipment_choices: List[Dict[str, Any]] = field(default_factory=list)  # Equipment choice options
    class_features: Dict[str, Any] = field(default_factory=dict)  # Features by level
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert class to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Class':
        """Create class from dictionary from IndexedDB."""
        # Remove unexpected fields that might come from IndexedDB
        expected_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in expected_fields}
        return cls(**filtered_data)


@dataclass
class Subclass:
    """Character subclasses (archetypes) for IndexedDB storage."""
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    class_id: str = ""
    name: str = ""
    description: str = ""
    
    # Subclass features by level
    features: Dict[str, Any] = field(default_factory=dict)
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subclass to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subclass':
        """Create subclass from dictionary from IndexedDB."""
        # Remove unexpected fields that might come from IndexedDB
        expected_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in expected_fields}
        return cls(**filtered_data)


@dataclass
class Background:
    """Character backgrounds with D&D 2024 rules for IndexedDB storage."""
    # Primary key (use name as ID)
    name: str = ""
    description: str = ""
    
    # Background features
    skill_proficiencies: List[str] = field(default_factory=list)  # Granted skills
    language_proficiencies: List[str] = field(default_factory=list)  # Languages or number of languages
    tool_proficiencies: List[str] = field(default_factory=list)  # Tools
    
    # Equipment and features
    starting_equipment: Dict[str, Any] = field(default_factory=dict)
    feature_name: str = ""  # Name of background feature
    feature_description: str = ""  # Background feature description
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert background to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Background':
        """Create background from dictionary from IndexedDB."""
        # Remove unexpected fields that might come from IndexedDB
        expected_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in expected_fields}
        return cls(**filtered_data)