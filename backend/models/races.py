"""
Character race models for D&D game.
AI Agents: D&D 2024 races with traits and ability bonuses.
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime

from database import Base

class Race(Base):
    """
    D&D Character Race with 2024 rules.
    AI Agents: Extend with custom races and variant traits.
    """
    __tablename__ = "races"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    
    # Physical characteristics
    size = Column(String(20), default="Medium")  # Tiny, Small, Medium, Large, etc.
    speed = Column(Integer, default=30)  # Base walking speed in feet
    
    # Ability score increases (D&D 2024 style - more flexible)
    ability_score_increase = Column(JSON, default=dict)  # {"choice": 2, "options": ["str", "dex", "con"]}
    
    # Racial traits
    traits = Column(JSON, default=list)  # List of trait objects
    proficiencies = Column(JSON, default=dict)  # Skills, tools, languages, weapons
    
    # Senses and special abilities
    darkvision_range = Column(Integer, default=0)  # 0 if no darkvision
    special_senses = Column(JSON, default=list)  # Other special senses
    
    # Languages
    languages = Column(JSON, default=list)  # Known languages
    bonus_languages = Column(Integer, default=0)  # Number of additional language choices
    
    # Subraces
    has_subraces = Column(Boolean, default=False)
    subrace_name = Column(String(50), nullable=True)  # e.g., "Lineage" for new races
    
    # Metadata
    source_book = Column(String(100), default="Player's Handbook 2024")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    characters = relationship("Character", back_populates="race")

# Pydantic Models for API
class RaceCreate(BaseModel):
    """Data to create a new race."""
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)
    size: str = Field(default="Medium")
    speed: int = Field(default=30, ge=0, le=120)
    
    # Ability bonuses
    ability_score_increase: Dict[str, Any] = Field(default_factory=dict)
    
    # Traits and abilities
    traits: List[Dict[str, Any]] = Field(default_factory=list)
    proficiencies: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Senses
    darkvision_range: int = Field(default=0, ge=0, le=120)
    special_senses: List[str] = Field(default_factory=list)
    
    # Languages
    languages: List[str] = Field(default_factory=list)
    bonus_languages: int = Field(default=0, ge=0, le=10)
    
    # Subraces
    has_subraces: bool = False
    subrace_name: Optional[str] = None
    
    source_book: str = "Custom"

class RaceResponse(BaseModel):
    """Race data for API responses."""
    id: str
    name: str
    description: str
    size: str
    speed: int
    
    ability_score_increase: Dict[str, Any]
    traits: List[Dict[str, Any]]
    proficiencies: Dict[str, List[str]]
    
    darkvision_range: int
    special_senses: List[str]
    languages: List[str]
    bonus_languages: int
    
    has_subraces: bool
    subrace_name: Optional[str]
    source_book: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class RacialTrait(BaseModel):
    """Individual racial trait definition."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    trait_type: str = Field(default="passive")  # passive, active, reaction, etc.
    uses_per_rest: Optional[str] = None  # "short", "long", or None for unlimited
    resource_cost: Optional[str] = None  # For traits that cost resources