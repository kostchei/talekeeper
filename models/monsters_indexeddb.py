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


@dataclass
class EncounterInstance:
    """
    An instance of a monster in a specific encounter with current HP tracking.
    Each monster card in an encounter gets its own instance for damage tracking.
    """
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    encounter_id: str = ""  # Links multiple monster instances together
    
    # Monster reference and current state
    monster_name: str = ""
    monster_cr: str = ""
    monster_type: str = ""
    monster_xp: int = 0
    
    # HP tracking
    max_hit_points: int = 0
    current_hit_points: int = 0
    temporary_hit_points: int = 0
    
    # Combat state
    is_alive: bool = True
    conditions: List[str] = field(default_factory=list)
    initiative: Optional[int] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    @property
    def hp_percentage(self) -> float:
        """Calculate HP as percentage for progress bar display."""
        if self.max_hit_points <= 0:
            return 0.0
        return (self.current_hit_points / self.max_hit_points) * 100.0
    
    @property
    def is_bloodied(self) -> bool:
        """Check if monster is bloodied (below half HP)."""
        return self.current_hit_points <= (self.max_hit_points // 2)
    
    def take_damage(self, damage: int) -> int:
        """Apply damage to the monster instance. Returns actual damage taken."""
        if damage <= 0:
            return 0
        
        # Apply to temporary HP first
        temp_damage = min(damage, self.temporary_hit_points)
        self.temporary_hit_points -= temp_damage
        remaining_damage = damage - temp_damage
        
        # Apply remaining damage to current HP
        actual_damage = min(remaining_damage, self.current_hit_points)
        self.current_hit_points -= actual_damage
        
        # Update alive status
        if self.current_hit_points <= 0:
            self.is_alive = False
            self.current_hit_points = 0
        
        self.updated_at = datetime.now().isoformat()
        return temp_damage + actual_damage
    
    def heal(self, healing: int) -> int:
        """Heal the monster instance. Returns actual healing applied."""
        if healing <= 0 or not self.is_alive:
            return 0
        
        max_healing = self.max_hit_points - self.current_hit_points
        actual_healing = min(healing, max_healing)
        self.current_hit_points += actual_healing
        
        self.updated_at = datetime.now().isoformat()
        return actual_healing
    
    def add_temporary_hp(self, temp_hp: int):
        """Add temporary hit points (doesn't stack, takes higher value)."""
        if temp_hp > self.temporary_hit_points:
            self.temporary_hit_points = temp_hp
            self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncounterInstance':
        """Create instance from dictionary from IndexedDB."""
        defaults = {
            'conditions': [],
            'created_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        # Remove unexpected fields
        expected_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in expected_fields}
        
        return cls(**filtered_data)
    
    @classmethod
    def from_monster_data(cls, monster_data: Dict[str, Any], encounter_id: str, rolled_hp: Optional[int] = None) -> 'EncounterInstance':
        """Create encounter instance from monster generator data."""
        # Calculate HP from SRD data or use provided rolled HP
        if rolled_hp is not None:
            max_hp = rolled_hp
        else:
            # Use average HP from SRD data (we'll implement HP rolling later)
            max_hp = monster_data.get('average_hp', 8)  # Default fallback
        
        return cls(
            encounter_id=encounter_id,
            monster_name=monster_data['name'],
            monster_cr=monster_data['cr_str'],
            monster_type=monster_data['type'],
            monster_xp=monster_data['xp'],
            max_hit_points=max_hp,
            current_hit_points=max_hp,
            temporary_hit_points=0,
            is_alive=True,
            conditions=[],
            initiative=None
        )


@dataclass
class Encounter:
    """
    A complete encounter with multiple monsters and metadata.
    Tracks the encounter as a whole for XP rewards and progression.
    """
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    character_id: str = ""  # Which character is in this encounter
    
    # Encounter metadata
    encounter_level: int = 1  # Character level when encounter was generated
    difficulty: str = "low"  # low, moderate, high
    total_xp_budget: int = 0  # Expected XP for this encounter
    
    # Status tracking
    status: str = "active"  # active, completed, abandoned
    is_combat: bool = False  # Whether combat has started
    rounds_elapsed: int = 0  # Combat rounds if applicable
    
    # XP and rewards
    xp_awarded: int = 0  # XP actually awarded (defeated monsters)
    xp_pending: int = 0  # XP from monsters still alive
    monsters_defeated: int = 0  # Count of defeated monsters
    monsters_total: int = 0  # Total monsters in encounter
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_combat_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def start_combat(self):
        """Mark encounter as entering combat."""
        self.is_combat = True
        self.started_combat_at = datetime.now().isoformat()
    
    def complete_encounter(self):
        """Mark encounter as completed."""
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()
    
    def add_defeated_monster(self, xp_value: int):
        """Add a defeated monster to the encounter."""
        self.monsters_defeated += 1
        self.xp_awarded += xp_value
        self.xp_pending -= xp_value
        
        # Check if encounter is complete
        if self.monsters_defeated >= self.monsters_total:
            self.complete_encounter()
    
    @property
    def completion_percentage(self) -> float:
        """Get encounter completion percentage."""
        if self.monsters_total == 0:
            return 0.0
        return (self.monsters_defeated / self.monsters_total) * 100.0
    
    @property
    def is_complete(self) -> bool:
        """Check if encounter is completed."""
        return self.status == "completed" or self.monsters_defeated >= self.monsters_total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Encounter':
        """Create encounter from dictionary from IndexedDB."""
        defaults = {
            'created_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        # Remove unexpected fields
        expected_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in expected_fields}
        
        return cls(**filtered_data)
    
    @classmethod
    def from_encounter_data(cls, encounter_data: Dict[str, Any], character_id: str) -> 'Encounter':
        """Create encounter from generator encounter data."""
        total_xp = sum(m.get('xp', 0) for m in encounter_data.get('monsters', []))
        monster_count = len(encounter_data.get('monsters', []))
        
        return cls(
            character_id=character_id,
            encounter_level=encounter_data.get('level', 1),
            difficulty=encounter_data.get('difficulty', 'low'),
            total_xp_budget=encounter_data.get('total_xp', total_xp),
            status="active",
            is_combat=False,
            xp_awarded=0,
            xp_pending=total_xp,
            monsters_defeated=0,
            monsters_total=monster_count
        )