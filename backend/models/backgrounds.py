"""
Character background models for D&D game.
AI Agents: D&D 2024 backgrounds with skills, features, and equipment.
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

class Background(Base):
    """
    D&D Character Background with 2024 rules.
    AI Agents: Rich backgrounds with features, contacts, and story hooks.
    """
    __tablename__ = "backgrounds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    
    # Core background elements
    skill_proficiencies = Column(JSON, nullable=False)  # ["insight", "medicine"] or choice structure
    tool_proficiencies = Column(JSON, default=list)  # Specific tools gained
    language_proficiencies = Column(JSON, default=list)  # Languages gained
    
    # Equipment and starting gear
    starting_equipment = Column(JSON, default=list)  # Items gained from background
    starting_gold = Column(Integer, default=0)  # Additional starting gold
    
    # Background feature
    feature_name = Column(String(100), nullable=False)
    feature_description = Column(Text, nullable=False)
    
    # Personality elements (for AI generation)
    suggested_personality_traits = Column(JSON, default=list)
    suggested_ideals = Column(JSON, default=list)
    suggested_bonds = Column(JSON, default=list)
    suggested_flaws = Column(JSON, default=list)
    
    # Story connections
    contacts_and_connections = Column(JSON, default=list)  # NPCs and organizations
    story_hooks = Column(JSON, default=list)  # Adventure hooks tied to background
    
    # Variant options
    variants = Column(JSON, default=list)  # Different versions of the background
    customization_options = Column(JSON, default=dict)  # Player customization choices
    
    # Metadata
    source_book = Column(String(100), default="Player's Handbook 2024")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    characters = relationship("Character", back_populates="background")

# Pydantic Models for API
class PersonalityElement(BaseModel):
    """Individual personality trait, ideal, bond, or flaw."""
    text: str = Field(..., min_length=1, max_length=500)
    category: str = Field(..., pattern="^(trait|ideal|bond|flaw)$")
    alignment_tendency: Optional[str] = None  # For ideals

class BackgroundContact(BaseModel):
    """NPC contact or connection from background."""
    name: str = Field(..., min_length=1, max_length=100)
    relationship: str = Field(..., min_length=1, max_length=100)  # "mentor", "rival", "ally"
    location: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    influence_level: str = Field(default="local")  # local, regional, national

class BackgroundCreate(BaseModel):
    """Data to create a new background."""
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)
    
    # Proficiencies
    skill_proficiencies: List[str] = Field(..., min_items=1, max_items=4)
    tool_proficiencies: List[str] = Field(default_factory=list)
    language_proficiencies: List[str] = Field(default_factory=list)
    
    # Equipment
    starting_equipment: List[str] = Field(default_factory=list)
    starting_gold: int = Field(default=0, ge=0, le=1000)
    
    # Feature
    feature_name: str = Field(..., min_length=1, max_length=100)
    feature_description: str = Field(..., min_length=1)
    
    # Personality suggestions
    suggested_personality_traits: List[PersonalityElement] = Field(default_factory=list)
    suggested_ideals: List[PersonalityElement] = Field(default_factory=list)
    suggested_bonds: List[PersonalityElement] = Field(default_factory=list)
    suggested_flaws: List[PersonalityElement] = Field(default_factory=list)
    
    # Story elements
    contacts_and_connections: List[BackgroundContact] = Field(default_factory=list)
    story_hooks: List[str] = Field(default_factory=list)
    
    # Customization
    variants: List[Dict[str, Any]] = Field(default_factory=list)
    customization_options: Dict[str, Any] = Field(default_factory=dict)
    
    source_book: str = "Custom"

class BackgroundResponse(BaseModel):
    """Background data for API responses."""
    id: str
    name: str
    description: str
    
    # Proficiencies
    skill_proficiencies: List[str]
    tool_proficiencies: List[str]
    language_proficiencies: List[str]
    
    # Equipment
    starting_equipment: List[str]
    starting_gold: int
    
    # Feature
    feature_name: str
    feature_description: str
    
    # Personality suggestions
    suggested_personality_traits: List[Dict[str, Any]]
    suggested_ideals: List[Dict[str, Any]]
    suggested_bonds: List[Dict[str, Any]]
    suggested_flaws: List[Dict[str, Any]]
    
    # Story elements
    contacts_and_connections: List[Dict[str, Any]]
    story_hooks: List[str]
    
    # Customization
    variants: List[Dict[str, Any]]
    customization_options: Dict[str, Any]
    
    source_book: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class BackgroundSelection(BaseModel):
    """Character's selected background details."""
    background_id: str
    
    # Customized personality (player choices)
    selected_personality_traits: List[str] = Field(default_factory=list, max_items=2)
    selected_ideals: List[str] = Field(default_factory=list, max_items=1)
    selected_bonds: List[str] = Field(default_factory=list, max_items=1)
    selected_flaws: List[str] = Field(default_factory=list, max_items=1)
    
    # Custom entries (if player writes their own)
    custom_personality_traits: List[str] = Field(default_factory=list)
    custom_ideals: List[str] = Field(default_factory=list)
    custom_bonds: List[str] = Field(default_factory=list)
    custom_flaws: List[str] = Field(default_factory=list)
    
    # Background story customization
    selected_contacts: List[str] = Field(default_factory=list)  # Contact IDs or names
    custom_contacts: List[BackgroundContact] = Field(default_factory=list)
    background_story: str = Field(default="", max_length=2000)  # Player's background story
    
    # Variant selection
    selected_variant: Optional[str] = None
    customization_choices: Dict[str, Any] = Field(default_factory=dict)