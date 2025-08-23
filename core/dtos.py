"""
File: core/dtos.py
Path: /core/dtos.py

Data Transfer Objects for TaleKeeper Desktop.
DTOs solve DetachedInstanceError by providing plain data objects
that can be safely passed around without database sessions.

Pseudo Code:
1. Define typed DTOs for all major entities (Character, Monster, etc.)
2. Provide conversion functions from SQLAlchemy models to DTOs
3. Use DTOs in UI and business logic instead of raw models
4. Keep SQLAlchemy models for database operations only

AI Agents: DTOs for clean separation between data layer and business logic.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CharacterDTO:
    """
    Character Data Transfer Object.
    Contains all data typically needed by UI without database dependencies.
    """
    # Core Identity
    id: str
    name: str
    level: int
    experience_points: int
    
    # Character Build
    race_id: str
    race_name: str
    class_id: str
    class_name: str
    subclass_id: Optional[str]
    subclass_name: Optional[str]
    background_id: str
    background_name: str
    
    # Ability Scores (final values with racial bonuses)
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    
    # Ability Modifiers (calculated)
    strength_modifier: int
    dexterity_modifier: int
    constitution_modifier: int
    intelligence_modifier: int
    wisdom_modifier: int
    charisma_modifier: int
    
    # Combat Stats
    armor_class: int
    hit_points_max: int
    hit_points_current: int
    hit_points_temporary: int
    hit_dice_max: int
    hit_dice_current: int
    death_saves_successes: int
    death_saves_failures: int
    conditions: List[str]
    
    # Character Features
    proficiencies: List[str]
    features: Dict[str, Any]
    
    # Equipment (item IDs)
    equipment_main_hand: Optional[str]
    equipment_off_hand: Optional[str]
    equipment_armor: Optional[str]
    equipment_shield: Optional[str]
    
    # Metadata
    created_at: datetime
    updated_at: Optional[datetime]
    notes: str
    
    # Save Slot Info
    save_slot_id: Optional[str]
    save_slot_number: Optional[int]


@dataclass
class MonsterDTO:
    """
    Monster Data Transfer Object.
    Contains all data needed for combat and encounters.
    """
    # Core Identity
    id: str
    name: str
    size: str
    type: str
    alignment: str
    
    # Combat Stats
    armor_class: int
    hit_points: int
    speed: int
    challenge_rating: float
    
    # Ability Scores
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    
    # Skills and Saves
    skills: Dict[str, int]
    saving_throws: Dict[str, int]
    damage_resistances: List[str]
    damage_immunities: List[str]
    condition_immunities: List[str]
    senses: List[str]
    languages: List[str]
    
    # Actions and Abilities
    actions: Dict[str, Any]
    legendary_actions: Dict[str, Any]
    special_abilities: Dict[str, Any]
    
    # AI and Behavior
    ai_script: Optional[str]


@dataclass
class RaceDTO:
    """Race Data Transfer Object for character creation."""
    id: str
    name: str
    description: str
    size: str
    speed: int
    ability_score_increases: Dict[str, int]
    languages: List[str]
    proficiencies: List[str]
    traits: Dict[str, str]


@dataclass
class ClassDTO:
    """Class Data Transfer Object for character creation."""
    id: str
    name: str
    description: str
    hit_die: int
    primary_ability: str
    armor_proficiencies: List[str]
    weapon_proficiencies: List[str]
    saving_throw_proficiencies: List[str]
    skill_proficiencies: List[str]
    subclasses: List[Dict[str, Any]]


@dataclass
class BackgroundDTO:
    """Background Data Transfer Object for character creation."""
    id: str
    name: str
    description: str
    skill_proficiencies: List[str]
    tool_proficiencies: List[str]
    languages: List[str]
    equipment: List[str]
    feature_name: str
    feature_description: str


@dataclass
class SaveSlotDTO:
    """Save Slot Data Transfer Object for save management."""
    id: str
    slot_number: int
    is_occupied: bool
    save_name: Optional[str]
    character_name: Optional[str]
    character_level: Optional[int]
    current_location: Optional[str]
    play_time_hours: int
    last_played: Optional[datetime]
    created_at: datetime