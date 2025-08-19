"""
File: backend/models/character.py
Path: /backend/models/character.py

Character models for D&D game.
AI Agents: Core character data with D&D 2024 rules integration.

Pseudo Code:
1. Define Character SQLAlchemy model with stats, race, class, equipment
2. Create Pydantic schemas for API requests/responses
3. Include calculated properties (AC, modifiers, spell save DC)
4. Handle character progression (leveling, XP, HP increases)
5. Manage equipment relationships and inventory tracking
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

class Character(Base):
    """
    D&D Character with 2024 rules.
    AI Agents: Extend with class-specific features and spell slots.
    """
    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    
    # Core D&D Stats
    race_id = Column(UUID(as_uuid=True), ForeignKey("races.id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    subclass_id = Column(UUID(as_uuid=True), ForeignKey("subclasses.id"), nullable=True)
    background_id = Column(UUID(as_uuid=True), ForeignKey("backgrounds.id"), nullable=False)
    
    level = Column(Integer, default=1, nullable=False)
    experience_points = Column(Integer, default=0, nullable=False)
    
    # Ability Scores (8-20 range, with racial bonuses)
    strength = Column(Integer, nullable=False, default=10)
    dexterity = Column(Integer, nullable=False, default=10)
    constitution = Column(Integer, nullable=False, default=10)
    intelligence = Column(Integer, nullable=False, default=10)
    wisdom = Column(Integer, nullable=False, default=10)
    charisma = Column(Integer, nullable=False, default=10)
    
    # Calculated Values (updated when stats change)
    armor_class = Column(Integer, nullable=False, default=10)
    hit_points_max = Column(Integer, nullable=False, default=8)
    hit_points_current = Column(Integer, nullable=False, default=8)
    hit_points_temporary = Column(Integer, default=0)
    
    # Proficiencies and Features
    proficiencies = Column(JSON, default=list)  # Skills, tools, languages
    features = Column(JSON, default=dict)  # Class and racial features
    
    # Equipment slots
    equipment_main_hand = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)
    equipment_off_hand = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)
    equipment_armor = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)
    equipment_shield = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    notes = Column(Text, default="")
    
    # Relationships
    race = relationship("Race", back_populates="characters")
    character_class = relationship("Class", back_populates="characters")
    subclass = relationship("Subclass", back_populates="characters")
    background = relationship("Background", back_populates="characters")
    inventory = relationship("CharacterInventory", back_populates="character", cascade="all, delete-orphan")
    game_states = relationship("GameState", back_populates="character", cascade="all, delete-orphan")
    
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
        """Convert character to dictionary for API responses."""
        return {
            "id": str(self.id),
            "name": self.name,
            "level": self.level,
            "experience_points": self.experience_points,
            "race": self.race.name if self.race else None,
            "class": self.character_class.name if self.character_class else None,
            "subclass": self.subclass.name if self.subclass else None,
            "background": self.background.name if self.background else None,
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

# Pydantic Models for API
class CharacterCreate(BaseModel):
    """Data required to create a new character."""
    name: str = Field(..., min_length=1, max_length=100)
    race_id: str
    class_id: str
    background_id: str
    subclass_id: Optional[str] = None  # Optional - chosen at level 3 for most classes
    
    # Starting ability scores (before racial bonuses)
    strength: int = Field(default=10, ge=8, le=15)
    dexterity: int = Field(default=10, ge=8, le=15)
    constitution: int = Field(default=10, ge=8, le=15)
    intelligence: int = Field(default=10, ge=8, le=15)
    wisdom: int = Field(default=10, ge=8, le=15)
    charisma: int = Field(default=10, ge=8, le=15)
    
    # Character creation choices
    ability_scores: Optional[Dict[str, int]] = None  # Override individual scores if provided
    skill_choices: Optional[List[str]] = None  # Chosen skills from class/background
    equipment_choices: Optional[Dict[str, Any]] = None  # Starting equipment selections
    save_slot: Optional[int] = Field(default=1, ge=1, le=10)  # Save slot number
    
    notes: Optional[str] = ""

class CharacterUpdate(BaseModel):
    """Data for updating an existing character."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    notes: Optional[str] = None
    
    # Allow manual stat adjustments (for magic items, etc.)
    strength: Optional[int] = Field(None, ge=1, le=30)
    dexterity: Optional[int] = Field(None, ge=1, le=30)
    constitution: Optional[int] = Field(None, ge=1, le=30)
    intelligence: Optional[int] = Field(None, ge=1, le=30)
    wisdom: Optional[int] = Field(None, ge=1, le=30)
    charisma: Optional[int] = Field(None, ge=1, le=30)

class CharacterResponse(BaseModel):
    """Character data for API responses."""
    id: str
    name: str
    level: int
    experience_points: int
    race: Optional[str]
    character_class: Optional[str]
    subclass: Optional[str]
    background: Optional[str]
    
    ability_scores: Dict[str, int]
    modifiers: Dict[str, int]
    combat_stats: Dict[str, int]
    
    proficiencies: List[str]
    features: Dict[str, Any]
    
    created_at: datetime
    notes: str
    
    class Config:
        from_attributes = True

class HealingRequest(BaseModel):
    """Request to heal a character."""
    character_id: str
    healing_amount: int = Field(..., gt=0)
    healing_type: str = Field(default="magical", description="magical, natural, potion, etc.")
    
class DamageRequest(BaseModel):
    """Request to damage a character."""
    character_id: str
    damage_amount: int = Field(..., gt=0)
    damage_type: str = Field(default="untyped", description="fire, cold, slashing, etc.")
    can_reduce_to_zero: bool = Field(default=True, description="Whether damage can kill character")

class RestRequest(BaseModel):
    """Request for character to rest."""
    character_id: str
    rest_type: str = Field(..., description="short or long")
    hit_dice_used: Optional[int] = Field(default=0, description="Hit dice spent during short rest")