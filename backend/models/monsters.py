"""
File: backend/models/monsters.py
Path: /backend/models/monsters.py

Monster models for D&D game.
AI Agents: Combat encounters with full stat blocks and AI behavior patterns.

Pseudo Code:
1. Define Monster model with complete D&D stat block (HP, AC, stats, saves)
2. Store AI behavior scripts for different monster types
3. Handle special abilities, attacks, and spellcasting
4. Manage encounter difficulty and challenge rating
5. Process monster actions during combat turns
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from enum import Enum

from database import Base

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

class Monster(Base):
    """
    D&D Monster with complete stat block.
    AI Agents: Extend with tactical AI behaviors and environmental effects.
    """
    __tablename__ = "monsters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    
    # Basic properties
    size = Column(String(20), nullable=False, default=MonsterSize.MEDIUM)
    type = Column(String(20), nullable=False, default=MonsterType.HUMANOID)
    subtype = Column(String(50), nullable=True)  # e.g., "goblinoid", "shapechanger"
    alignment = Column(String(50), default="neutral")
    
    # Challenge and XP
    challenge_rating = Column(Numeric(4, 2), nullable=False, default=0.25)
    experience_value = Column(Integer, nullable=False, default=50)
    
    # Ability Scores
    strength = Column(Integer, nullable=False, default=10)
    dexterity = Column(Integer, nullable=False, default=10)
    constitution = Column(Integer, nullable=False, default=10)
    intelligence = Column(Integer, nullable=False, default=10)
    wisdom = Column(Integer, nullable=False, default=10)
    charisma = Column(Integer, nullable=False, default=10)
    
    # Combat Stats
    armor_class = Column(Integer, nullable=False, default=10)
    hit_points_max = Column(Integer, nullable=False, default=1)
    hit_dice = Column(String(20), nullable=False, default="1d4")  # e.g., "2d8+2"
    speed = Column(JSON, default=dict)  # {"walk": 30, "fly": 60, "swim": 30}
    
    # Defenses
    damage_resistances = Column(JSON, default=list)  # ["fire", "cold"]
    damage_immunities = Column(JSON, default=list)
    condition_immunities = Column(JSON, default=list)
    damage_vulnerabilities = Column(JSON, default=list)
    
    # Senses and Languages
    senses = Column(JSON, default=dict)  # {"darkvision": 60, "passive_perception": 12}
    languages = Column(JSON, default=list)  # ["Common", "Goblin"]
    
    # Skills and Saves
    saving_throws = Column(JSON, default=dict)  # {"dexterity": 4, "wisdom": 2}
    skills = Column(JSON, default=dict)  # {"stealth": 6, "perception": 3}
    
    # Abilities
    special_abilities = Column(JSON, default=list)  # Passive abilities
    actions = Column(JSON, default=list)  # Standard actions
    bonus_actions = Column(JSON, default=list)  # Bonus actions
    reactions = Column(JSON, default=list)  # Reaction abilities
    legendary_actions = Column(JSON, default=list)  # Legendary actions (if any)
    lair_actions = Column(JSON, default=list)  # Lair actions (if any)
    
    # Loot and Environment
    loot_table_id = Column(UUID(as_uuid=True), ForeignKey("loot_tables.id"), nullable=True)
    environment_tags = Column(JSON, default=list)  # ["dungeon", "forest", "urban"]
    
    # AI Behavior
    ai_behavior = Column(JSON, default=dict)  # Combat tactics and preferences
    
    # Metadata
    source_book = Column(String(100), default="Custom")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    loot_table = relationship("LootTable", backref="monsters")
    
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
        """Calculate proficiency bonus from CR."""
        cr = float(self.challenge_rating)
        if cr < 5:
            return 2
        elif cr < 9:
            return 3
        elif cr < 13:
            return 4
        elif cr < 17:
            return 5
        elif cr < 21:
            return 6
        elif cr < 25:
            return 7
        elif cr < 29:
            return 8
        else:
            return 9
    
    def to_stat_block(self) -> Dict[str, Any]:
        """Generate complete D&D stat block."""
        return {
            "name": self.name,
            "size": self.size,
            "type": self.type,
            "subtype": self.subtype,
            "alignment": self.alignment,
            "challenge_rating": str(self.challenge_rating),
            "experience_value": self.experience_value,
            "armor_class": self.armor_class,
            "hit_points": self.hit_points_max,
            "hit_dice": self.hit_dice,
            "speed": self.speed,
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
            "proficiency_bonus": self.proficiency_bonus,
            "saving_throws": self.saving_throws,
            "skills": self.skills,
            "damage_resistances": self.damage_resistances,
            "damage_immunities": self.damage_immunities,
            "damage_vulnerabilities": self.damage_vulnerabilities,
            "condition_immunities": self.condition_immunities,
            "senses": self.senses,
            "languages": self.languages,
            "special_abilities": self.special_abilities,
            "actions": self.actions,
            "bonus_actions": self.bonus_actions,
            "reactions": self.reactions,
            "legendary_actions": self.legendary_actions,
            "lair_actions": self.lair_actions
        }

# Pydantic Models for API
class MonsterCreate(BaseModel):
    """Data to create a new monster."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    size: MonsterSize = MonsterSize.MEDIUM
    type: MonsterType = MonsterType.HUMANOID
    subtype: Optional[str] = None
    alignment: str = "neutral"
    challenge_rating: float = Field(default=0.25, ge=0, le=30)
    
    # Ability scores
    strength: int = Field(default=10, ge=1, le=30)
    dexterity: int = Field(default=10, ge=1, le=30)
    constitution: int = Field(default=10, ge=1, le=30)
    intelligence: int = Field(default=10, ge=1, le=30)
    wisdom: int = Field(default=10, ge=1, le=30)
    charisma: int = Field(default=10, ge=1, le=30)
    
    # Combat stats
    armor_class: int = Field(default=10, ge=1, le=25)
    hit_points_max: int = Field(default=1, ge=1)
    hit_dice: str = Field(default="1d4")
    speed: Dict[str, int] = Field(default_factory=lambda: {"walk": 30})
    
    # Optional complex data
    damage_resistances: List[str] = Field(default_factory=list)
    damage_immunities: List[str] = Field(default_factory=list)
    condition_immunities: List[str] = Field(default_factory=list)
    damage_vulnerabilities: List[str] = Field(default_factory=list)
    senses: Dict[str, int] = Field(default_factory=dict)
    languages: List[str] = Field(default_factory=list)
    saving_throws: Dict[str, int] = Field(default_factory=dict)
    skills: Dict[str, int] = Field(default_factory=dict)
    
    # Abilities
    special_abilities: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    bonus_actions: List[Dict[str, Any]] = Field(default_factory=list)
    reactions: List[Dict[str, Any]] = Field(default_factory=list)
    legendary_actions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    source_book: str = "Custom"
    environment_tags: List[str] = Field(default_factory=list)
    ai_behavior: Dict[str, Any] = Field(default_factory=dict)

class MonsterResponse(BaseModel):
    """Monster data for API responses."""
    id: str
    name: str
    description: str
    size: str
    type: str
    subtype: Optional[str]
    alignment: str
    challenge_rating: float
    experience_value: int
    
    # Combat stats
    armor_class: int
    hit_points_max: int
    hit_dice: str
    speed: Dict[str, int]
    
    # Ability scores and modifiers
    ability_scores: Dict[str, int]
    modifiers: Dict[str, int]
    proficiency_bonus: int
    
    # Defenses
    damage_resistances: List[str]
    damage_immunities: List[str]
    condition_immunities: List[str]
    damage_vulnerabilities: List[str]
    
    # Senses and skills
    senses: Dict[str, int]
    languages: List[str]
    saving_throws: Dict[str, int]
    skills: Dict[str, int]
    
    # Abilities
    special_abilities: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    bonus_actions: List[Dict[str, Any]]
    reactions: List[Dict[str, Any]]
    legendary_actions: List[Dict[str, Any]]
    
    # Environment and AI
    environment_tags: List[str]
    ai_behavior: Dict[str, Any]
    
    source_book: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MonsterEncounterData(BaseModel):
    """Monster data for combat encounters."""
    monster_id: str
    quantity: int = Field(default=1, ge=1, le=20)
    hp_override: Optional[int] = None  # Override HP for this encounter
    initiative_modifier: Optional[int] = None  # Modify initiative roll
    special_conditions: List[str] = Field(default_factory=list)  # Starting conditions