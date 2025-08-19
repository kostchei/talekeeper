"""
Character class and subclass models for D&D game.
AI Agents: D&D 2024 classes with features, spellcasting, and progression.
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime

from database import Base

class Class(Base):
    """
    D&D Character Class with 2024 rules.
    AI Agents: Full class progression with features and spellcasting.
    """
    __tablename__ = "classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    
    # Core class properties
    hit_die = Column(String(10), nullable=False, default="d8")  # d6, d8, d10, d12
    primary_ability = Column(JSON, nullable=False)  # ["strength"] or ["dexterity", "strength"]
    
    # Proficiencies granted at level 1
    saving_throw_proficiencies = Column(JSON, nullable=False)  # ["strength", "constitution"]
    armor_proficiencies = Column(JSON, default=list)
    weapon_proficiencies = Column(JSON, default=list)
    tool_proficiencies = Column(JSON, default=list)
    skill_proficiencies = Column(JSON, default=dict)  # {"choose": 2, "from": ["athletics", "intimidation"]}
    
    # Equipment granted at level 1
    starting_equipment = Column(JSON, default=list)
    starting_gold = Column(String(20), default="2d4 * 10")  # Dice expression for starting gold
    
    # Spellcasting
    is_spellcaster = Column(Boolean, default=False)
    spellcasting_ability = Column(String(20), nullable=True)  # "intelligence", "wisdom", "charisma"
    spellcasting_type = Column(String(20), nullable=True)  # "full", "half", "third", "pact"
    ritual_casting = Column(Boolean, default=False)
    spellcasting_focus = Column(String(50), nullable=True)  # "arcane focus", "holy symbol", etc.
    
    # Class features by level (1-20)
    features_by_level = Column(JSON, nullable=False)  # {1: [feature_objects], 2: [feature_objects]}
    spell_slots_by_level = Column(JSON, default=dict)  # {1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}}
    
    # Subclass information
    subclass_level = Column(Integer, default=3)  # Level when subclass is chosen
    subclass_name = Column(String(50), default="Subclass")  # "Archetype", "Patron", "College", etc.
    
    # Multiclassing
    multiclass_requirements = Column(JSON, default=dict)  # {"strength": 13, "charisma": 13}
    
    # Metadata
    source_book = Column(String(100), default="Player's Handbook 2024")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    characters = relationship("Character", back_populates="character_class")
    subclasses = relationship("Subclass", back_populates="parent_class", cascade="all, delete-orphan")

class Subclass(Base):
    """
    Character subclass/archetype.
    AI Agents: Specialized class features and unique abilities.
    """
    __tablename__ = "subclasses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    
    # Subclass features by level
    features_by_level = Column(JSON, nullable=False)  # Additional features beyond base class
    
    # Spellcasting modifications (for subclasses that add spellcasting)
    bonus_spells = Column(JSON, default=dict)  # {1: ["spell_name"], 3: ["spell_name"]} - always prepared
    spell_list_expansion = Column(JSON, default=list)  # Additional spells available to learn
    
    # Special resources
    special_resources = Column(JSON, default=dict)  # Ki points, sorcery points, etc.
    
    # Metadata
    source_book = Column(String(100), default="Player's Handbook 2024")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent_class = relationship("Class", back_populates="subclasses")
    characters = relationship("Character", back_populates="subclass")

# Pydantic Models for API
class ClassFeature(BaseModel):
    """Individual class feature definition."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    feature_type: str = Field(default="passive")  # passive, active, reaction, etc.
    
    # Usage limitations
    uses_per_rest: Optional[str] = None  # "short", "long", or None for unlimited
    uses_per_day: Optional[int] = None
    resource_cost: Optional[str] = None  # For features that cost resources
    
    # Mechanical effects
    stat_bonuses: Dict[str, int] = Field(default_factory=dict)
    proficiency_bonuses: List[str] = Field(default_factory=list)
    special_effects: Dict[str, Any] = Field(default_factory=dict)

class ClassCreate(BaseModel):
    """Data to create a new class."""
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)
    hit_die: str = Field(..., pattern="^d(6|8|10|12)$")
    primary_ability: List[str] = Field(..., min_items=1)
    
    # Proficiencies
    saving_throw_proficiencies: List[str] = Field(..., min_items=2, max_items=2)
    armor_proficiencies: List[str] = Field(default_factory=list)
    weapon_proficiencies: List[str] = Field(default_factory=list)
    tool_proficiencies: List[str] = Field(default_factory=list)
    skill_proficiencies: Dict[str, Any] = Field(default_factory=dict)
    
    # Equipment
    starting_equipment: List[str] = Field(default_factory=list)
    starting_gold: str = Field(default="2d4 * 10")
    
    # Spellcasting
    is_spellcaster: bool = False
    spellcasting_ability: Optional[str] = None
    spellcasting_type: Optional[str] = None
    ritual_casting: bool = False
    spellcasting_focus: Optional[str] = None
    
    # Features and progression
    features_by_level: Dict[int, List[ClassFeature]] = Field(..., min_items=1)
    spell_slots_by_level: Dict[int, Dict[int, int]] = Field(default_factory=dict)
    
    # Subclass
    subclass_level: int = Field(default=3, ge=1, le=20)
    subclass_name: str = Field(default="Subclass", max_length=50)
    
    # Multiclassing
    multiclass_requirements: Dict[str, int] = Field(default_factory=dict)
    
    source_book: str = "Custom"

class ClassResponse(BaseModel):
    """Class data for API responses."""
    id: str
    name: str
    description: str
    hit_die: str
    primary_ability: List[str]
    
    # Proficiencies
    saving_throw_proficiencies: List[str]
    armor_proficiencies: List[str]
    weapon_proficiencies: List[str]
    tool_proficiencies: List[str]
    skill_proficiencies: Dict[str, Any]
    
    # Equipment
    starting_equipment: List[str]
    starting_gold: str
    
    # Spellcasting
    is_spellcaster: bool
    spellcasting_ability: Optional[str]
    spellcasting_type: Optional[str]
    ritual_casting: bool
    spellcasting_focus: Optional[str]
    
    # Progression
    features_by_level: Dict[int, List[Dict[str, Any]]]
    spell_slots_by_level: Dict[int, Dict[int, int]]
    
    # Subclass
    subclass_level: int
    subclass_name: str
    subclasses: List[Dict[str, Any]]  # Available subclasses
    
    # Multiclassing
    multiclass_requirements: Dict[str, int]
    
    source_book: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubclassCreate(BaseModel):
    """Data to create a new subclass."""
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)
    class_id: str
    
    # Features
    features_by_level: Dict[int, List[ClassFeature]] = Field(..., min_items=1)
    
    # Spellcasting additions
    bonus_spells: Dict[int, List[str]] = Field(default_factory=dict)
    spell_list_expansion: List[str] = Field(default_factory=list)
    
    # Resources
    special_resources: Dict[str, Any] = Field(default_factory=dict)
    
    source_book: str = "Custom"

class SubclassResponse(BaseModel):
    """Subclass data for API responses."""
    id: str
    name: str
    description: str
    class_id: str
    class_name: str
    
    features_by_level: Dict[int, List[Dict[str, Any]]]
    bonus_spells: Dict[int, List[str]]
    spell_list_expansion: List[str]
    special_resources: Dict[str, Any]
    
    source_book: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LevelUpResult(BaseModel):
    """Result of character leveling up."""
    character_id: str
    old_level: int
    new_level: int
    
    # Gained features
    new_features: List[Dict[str, Any]]
    new_spell_slots: Dict[int, int]
    
    # Stat increases
    hit_points_gained: int
    ability_score_improvement: bool
    proficiency_bonus_increase: bool
    
    # Choices to make
    pending_choices: List[Dict[str, Any]]  # Subclass selection, spell choices, etc.
    
    class Config:
        from_attributes = True