"""
File: models/character.py
Path: /models/character.py

Character models for D&D Desktop game.
Ported from web version with SQLite compatibility.

Pseudo Code:
1. Define Character SQLAlchemy model with stats, race, class, equipment
2. Include calculated properties (AC, modifiers, spell save DC)
3. Handle character progression (leveling, XP, HP increases)
4. Manage equipment relationships and inventory tracking
5. Provide convenience methods for character operations

AI Agents: Core character data with D&D 2024 rules integration.
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from core.database import Base


class Character(Base):
    """
    D&D Character with 2024 rules.
    AI Agents: Extend with class-specific features and spell slots.
    """
    __tablename__ = "characters"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    save_slot_id = Column(String, ForeignKey("save_slots.id"), nullable=True)
    name = Column(String(100), nullable=False)
    
    # Core D&D Stats
    race_id = Column(String, ForeignKey("races.id"), nullable=False)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    subclass_id = Column(String, ForeignKey("subclasses.id"), nullable=True)
    background_id = Column(String, ForeignKey("backgrounds.id"), nullable=False)
    
    level = Column(Integer, default=1, nullable=False)
    experience_points = Column(Integer, default=0, nullable=False)
    
    # Ability Scores (1-20 range, with racial bonuses)
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
    
    # Alternative field names used by combat system
    max_hit_points = Column(Integer, nullable=False, default=8)
    current_hit_points = Column(Integer, nullable=False, default=8)
    hit_dice_max = Column(Integer, nullable=False, default=1)
    hit_dice_current = Column(Integer, nullable=False, default=1)
    death_saves_successes = Column(Integer, default=0)
    death_saves_failures = Column(Integer, default=0)
    conditions = Column(JSON, default=lambda: [])
    
    # Proficiencies and Features
    proficiencies = Column(JSON, default=lambda: [])  # Skills, tools, languages
    features = Column(JSON, default=lambda: {})  # Class and racial features
    
    # Equipment slots
    equipment_main_hand = Column(String, ForeignKey("items.id"), nullable=True)
    equipment_off_hand = Column(String, ForeignKey("items.id"), nullable=True)
    equipment_armor = Column(String, ForeignKey("items.id"), nullable=True)
    equipment_shield = Column(String, ForeignKey("items.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    notes = Column(Text, default="")
    
    # Relationships
    race = relationship("Race", back_populates="characters")
    character_class = relationship("Class", back_populates="characters")
    subclass = relationship("Subclass", back_populates="characters")
    background = relationship("Background", back_populates="characters")
    save_slot = relationship("SaveSlot", back_populates="characters")
    # inventory = relationship("CharacterInventory", back_populates="character", cascade="all, delete-orphan")  # TODO: Implement CharacterInventory model
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
        """Convert character to dictionary for display."""
        return {
            "id": str(self.id),
            "name": self.name,
            "level": self.level,
            "experience_points": self.experience_points,
            "race": self.race.name if self.race else None,
            "character_class": self.character_class.name if self.character_class else None,
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


class Race(Base):
    """Character races with D&D 2024 rules."""
    __tablename__ = "races"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    
    # Ability Score Increases
    ability_score_increases = Column(JSON, default=lambda: {})  # e.g., {"strength": 2, "constitution": 1}
    
    # Racial features
    size = Column(String(20), default="Medium")
    speed = Column(Integer, default=30)
    languages = Column(JSON, default=lambda: [])  # e.g., ["Common", "Dwarvish"]
    proficiencies = Column(JSON, default=lambda: [])  # Skills, tools, weapons
    traits = Column(JSON, default=lambda: {})  # Special racial traits
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    characters = relationship("Character", back_populates="race")


class Class(Base):
    """Character classes with D&D 2024 rules."""
    __tablename__ = "classes"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    
    # Core class mechanics
    hit_die = Column(Integer, nullable=False, default=8)  # d8, d10, etc.
    primary_ability = Column(String(50))  # "Strength" or "Dexterity"
    saving_throw_proficiencies = Column(JSON, default=lambda: [])  # e.g., ["strength", "constitution"]
    
    # Proficiencies granted
    armor_proficiencies = Column(JSON, default=lambda: [])
    weapon_proficiencies = Column(JSON, default=lambda: [])
    skill_proficiencies = Column(JSON, default=lambda: [])  # Available skills to choose from
    skill_choices = Column(Integer, default=2)  # Number of skills player can choose
    
    # Equipment and features
    starting_equipment = Column(JSON, default=lambda: {})
    class_features = Column(JSON, default=lambda: {})  # Features by level
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    characters = relationship("Character", back_populates="character_class")
    subclasses = relationship("Subclass", back_populates="parent_class", cascade="all, delete-orphan")


class Subclass(Base):
    """Character subclasses (archetypes).""" 
    __tablename__ = "subclasses"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Subclass features by level
    features = Column(JSON, default=lambda: {})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent_class = relationship("Class", back_populates="subclasses")
    characters = relationship("Character", back_populates="subclass")


class Background(Base):
    """Character backgrounds with D&D 2024 rules."""
    __tablename__ = "backgrounds"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    
    # Background features
    skill_proficiencies = Column(JSON, default=lambda: [])  # Granted skills
    language_proficiencies = Column(JSON, default=lambda: [])  # Languages or number of languages
    tool_proficiencies = Column(JSON, default=lambda: [])  # Tools
    
    # Equipment and features
    starting_equipment = Column(JSON, default=lambda: {})
    feature_name = Column(String(100))  # Name of background feature
    feature_description = Column(Text)  # Background feature description
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    characters = relationship("Character", back_populates="background")