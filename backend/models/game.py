"""
Game state and save system models.
AI Agents: Track progression, quests, and persistent world state.
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from enum import Enum

from database import Base

class GameStatus(str, Enum):
    """Current state of the game."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class LocationType(str, Enum):
    """Types of game locations."""
    TOWN = "town"
    DUNGEON = "dungeon"
    WILDERNESS = "wilderness"
    SHOP = "shop"
    TAVERN = "tavern"
    TEMPLE = "temple"

class QuestStatus(str, Enum):
    """Quest progression states."""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"

class GameState(Base):
    """
    Character's current game state and progress.
    AI Agents: Central hub for character progression and world interaction.
    """
    __tablename__ = "game_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    
    # Game progress
    status = Column(String(20), nullable=False, default="ACTIVE")
    total_playtime_minutes = Column(Integer, default=0)
    last_played = Column(DateTime(timezone=True), server_default=func.now())
    
    # Location and exploration
    current_location = Column(String(100), default="Starting Town")
    location_type = Column(String(20), default="TOWN")
    discovered_locations = Column(JSON, default=list)  # List of discovered location names
    
    # Resources
    inventory_gold = Column(Integer, default=50)  # Starting gold
    inventory_weight = Column(Integer, default=0)  # Current carry weight
    
    # Rest and recovery
    last_short_rest = Column(DateTime(timezone=True), nullable=True)
    last_long_rest = Column(DateTime(timezone=True), nullable=True)
    short_rests_today = Column(Integer, default=0)
    hit_dice_remaining = Column(JSON, default=dict)  # class -> remaining dice
    
    # Spell casting (if applicable)
    spell_slots_remaining = Column(JSON, default=dict)  # level -> remaining slots
    spell_slots_max = Column(JSON, default=dict)  # level -> max slots
    
    # Experience and progression
    experience_gained_session = Column(Integer, default=0)
    levels_gained_session = Column(Integer, default=0)
    milestone_progress = Column(JSON, default=dict)  # Custom milestone tracking
    
    # Quests and story
    active_quests = Column(JSON, default=list)  # List of active quest data
    completed_quests = Column(JSON, default=list)  # List of completed quest data
    story_flags = Column(JSON, default=dict)  # Custom story progression flags
    
    # Exploration and encounters
    encounters_faced = Column(Integer, default=0)
    monsters_defeated = Column(JSON, default=dict)  # monster_name -> count
    dungeons_completed = Column(JSON, default=list)  # List of dungeon names
    
    # Achievements and statistics
    total_damage_dealt = Column(Integer, default=0)
    total_damage_taken = Column(Integer, default=0)
    total_healing_done = Column(Integer, default=0)
    critical_hits_landed = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    
    # Social interactions
    npc_relationships = Column(JSON, default=dict)  # npc_name -> relationship_value
    faction_standings = Column(JSON, default=dict)  # faction_name -> standing_value
    
    # Settings and preferences
    difficulty_level = Column(String(20), default="normal")  # easy, normal, hard, nightmare
    auto_rest = Column(Boolean, default=False)
    combat_speed = Column(String(20), default="normal")  # slow, normal, fast
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    notes = Column(Text, default="")  # Player notes
    
    # Relationships
    character = relationship("Character", back_populates="game_states")
    save_slots = relationship("SaveSlot", back_populates="game_state", cascade="all, delete-orphan")

class SaveSlot(Base):
    """
    Save game snapshots for multiple save slots.
    AI Agents: Implement auto-save and manual save functionality.
    """
    __tablename__ = "save_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_state_id = Column(UUID(as_uuid=True), ForeignKey("game_states.id", ondelete="CASCADE"), nullable=False)
    
    # Save slot info
    slot_number = Column(Integer, nullable=False)  # 1-10 for manual saves, 0 for auto-saves
    save_name = Column(String(100), default="Quick Save")
    description = Column(Text, default="")
    
    # Snapshot data
    character_snapshot = Column(JSON, nullable=False)  # Complete character state
    game_state_snapshot = Column(JSON, nullable=False)  # Complete game state
    inventory_snapshot = Column(JSON, nullable=False)  # Complete inventory
    
    # Save metadata
    location_saved = Column(String(100), nullable=False)
    playtime_at_save = Column(Integer, nullable=False)
    character_level_at_save = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_auto_save = Column(Boolean, default=False)
    
    # Relationships
    game_state = relationship("GameState", back_populates="save_slots")

class Quest(Base):
    """
    Quest definitions and templates.
    AI Agents: Create dynamic quests with branching narratives.
    """
    __tablename__ = "quests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    
    # Quest properties
    quest_type = Column(String(50), default="main")  # main, side, daily, random
    difficulty = Column(String(20), default="normal")
    estimated_duration = Column(Integer, default=30)  # Minutes
    
    # Requirements
    level_requirement = Column(Integer, default=1)
    prerequisite_quests = Column(JSON, default=list)  # Quest IDs required
    location_requirement = Column(String(100), nullable=True)
    
    # Objectives and rewards
    objectives = Column(JSON, nullable=False)  # List of objective data
    rewards = Column(JSON, default=dict)  # XP, gold, items, story flags
    
    # Quest flow
    is_repeatable = Column(Boolean, default=False)
    auto_complete = Column(Boolean, default=False)
    time_limit_hours = Column(Integer, nullable=True)
    
    # Narrative
    start_text = Column(Text, default="")
    completion_text = Column(Text, default="")
    failure_text = Column(Text, default="")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(50), default="custom")

# Pydantic Models for API
class GameStateResponse(BaseModel):
    """Game state data for API responses."""
    id: str
    character_id: str
    status: GameStatus
    total_playtime_minutes: int
    last_played: datetime
    
    # Location
    current_location: str
    location_type: LocationType
    discovered_locations: List[str]
    
    # Resources
    inventory_gold: int
    inventory_weight: int
    
    # Rest state
    last_short_rest: Optional[datetime]
    last_long_rest: Optional[datetime]
    short_rests_today: int
    hit_dice_remaining: Dict[str, int]
    
    # Spells
    spell_slots_remaining: Dict[str, int]
    spell_slots_max: Dict[str, int]
    
    # Progress
    experience_gained_session: int
    levels_gained_session: int
    active_quests: List[Dict[str, Any]]
    completed_quests: List[Dict[str, Any]]
    
    # Statistics
    encounters_faced: int
    monsters_defeated: Dict[str, int]
    dungeons_completed: List[str]
    total_damage_dealt: int
    total_damage_taken: int
    critical_hits_landed: int
    deaths: int
    
    # Social
    npc_relationships: Dict[str, int]
    faction_standings: Dict[str, int]
    
    # Settings
    difficulty_level: str
    auto_rest: bool
    combat_speed: str
    
    notes: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SaveSlotResponse(BaseModel):
    """Save slot data for API responses."""
    id: str
    slot_number: int
    save_name: str
    description: str
    location_saved: str
    playtime_at_save: int
    character_level_at_save: int
    created_at: datetime
    is_auto_save: bool
    
    class Config:
        from_attributes = True

class QuestResponse(BaseModel):
    """Quest data for API responses."""
    id: str
    name: str
    description: str
    quest_type: str
    difficulty: str
    estimated_duration: int
    level_requirement: int
    objectives: List[Dict[str, Any]]
    rewards: Dict[str, Any]
    is_repeatable: bool
    time_limit_hours: Optional[int]
    
    class Config:
        from_attributes = True

class RestRequest(BaseModel):
    """Request to rest."""
    character_id: str
    rest_type: str = Field(..., pattern="^(short|long)$")
    hit_dice_to_spend: Dict[str, int] = Field(default_factory=dict)  # class -> dice count
    force_rest: bool = False  # Override rest limitations

class LocationChangeRequest(BaseModel):
    """Request to change location."""
    character_id: str
    new_location: str
    location_type: LocationType = LocationType.TOWN
    travel_time_minutes: int = 0

class QuestActionRequest(BaseModel):
    """Request to interact with quests."""
    character_id: str
    quest_id: str
    action: str = Field(..., pattern="^(start|complete|abandon|progress)$")
    objective_index: Optional[int] = None  # For progressing specific objectives
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class SaveGameRequest(BaseModel):
    """Request to save game."""
    character_id: str
    slot_number: int = Field(..., ge=0, le=10)  # 0 for auto-save
    save_name: str = Field(default="Quick Save", max_length=100)
    description: str = Field(default="", max_length=500)

class GameSave(Base):
    """
    Game save data (alias for SaveSlot for router compatibility).
    AI Agents: Alternative interface to save slot system.
    """
    __tablename__ = "game_saves"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    
    # Save information
    slot_number = Column(Integer, nullable=False)
    save_name = Column(String(100), default="Quick Save")
    description = Column(Text, default="")
    
    # Save data
    game_data = Column(JSON, nullable=False)  # Complete game state
    character_data = Column(JSON, nullable=False)  # Character snapshot
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Game state at time of save
    character_level = Column(Integer, nullable=False)
    location = Column(String(100), nullable=False)
    playtime_minutes = Column(Integer, default=0)

class DungeonRoom(Base):
    """
    Individual rooms in dungeons.
    AI Agents: Procedural dungeon generation and exploration tracking.
    """
    __tablename__ = "dungeon_rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    dungeon_name = Column(String(100), nullable=False)
    room_number = Column(Integer, nullable=False)
    
    # Room properties
    name = Column(String(100), default="Room")
    description = Column(Text, default="")
    room_type = Column(String(50), default="standard")  # standard, treasure, boss, trap
    
    # Layout
    connections = Column(JSON, default=dict)  # {"north": "room_2", "east": "room_3"}
    size = Column(String(20), default="medium")  # small, medium, large, huge
    
    # Contents
    monsters = Column(JSON, default=list)  # Monster encounter data
    treasures = Column(JSON, default=list)  # Treasure data
    traps = Column(JSON, default=list)  # Trap data
    environmental_features = Column(JSON, default=list)  # Special features
    
    # State tracking
    explored = Column(Boolean, default=False)
    cleared = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GameEvent(Base):
    """
    Game events and story progression tracking.
    AI Agents: Dynamic story events and narrative branching.
    """
    __tablename__ = "game_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    
    # Event information
    event_type = Column(String(50), nullable=False)  # story, combat, interaction, etc.
    event_name = Column(String(100), nullable=False)
    event_description = Column(Text, default="")
    
    # Context
    location = Column(String(100), nullable=False)
    character_level = Column(Integer, nullable=False)
    session_time = Column(Integer, default=0)  # Minutes into session
    
    # Event data
    event_data = Column(JSON, default=dict)  # Flexible event details
    outcomes = Column(JSON, default=list)  # Possible or chosen outcomes
    
    # Flags
    is_major_event = Column(Boolean, default=False)
    affects_story = Column(Boolean, default=False)
    repeatable = Column(Boolean, default=False)
    
    # Timestamp
    occurred_at = Column(DateTime(timezone=True), server_default=func.now())

# Additional Pydantic models for API
class GameSaveRequest(BaseModel):
    """Request to save game."""
    character_id: str
    slot_number: int = Field(..., ge=1, le=10)
    save_name: str = Field(default="Quick Save", max_length=100)
    description: str = Field(default="", max_length=500)

class GameSaveResponse(BaseModel):
    """Response to save game request."""
    success: bool
    save_id: str
    slot_number: int
    save_name: str
    message: str
    
    class Config:
        from_attributes = True

class DungeonRoomResponse(BaseModel):
    """Dungeon room data for API responses."""
    id: str
    dungeon_name: str
    room_number: int
    name: str
    description: str
    room_type: str
    
    connections: Dict[str, str]
    size: str
    
    monsters: List[Dict[str, Any]]
    treasures: List[Dict[str, Any]]
    traps: List[Dict[str, Any]]
    environmental_features: List[Dict[str, Any]]
    
    explored: bool
    cleared: bool
    
    class Config:
        from_attributes = True

class GameEventResponse(BaseModel):
    """Game event data for API responses."""
    id: str
    character_id: str
    event_type: str
    event_name: str
    event_description: str
    
    location: str
    character_level: int
    session_time: int
    
    event_data: Dict[str, Any]
    outcomes: List[Dict[str, Any]]
    
    is_major_event: bool
    affects_story: bool
    repeatable: bool
    
    occurred_at: datetime
    
    class Config:
        from_attributes = True

class DungeonEnterRequest(BaseModel):
    """Request to enter a dungeon."""
    character_id: str
    dungeon_name: str = "Random Dungeon"
    difficulty: str = Field(default="normal", pattern="^(easy|normal|hard|nightmare)$")
    party_size: int = Field(default=1, ge=1, le=6)

class EncounterResult(BaseModel):
    """Result of a random encounter."""
    encounter_type: str  # combat, trap, treasure, event
    encounter_name: str
    description: str
    
    # Combat data (if applicable)
    monsters: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Rewards
    experience_reward: int = 0
    gold_reward: int = 0
    items_reward: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Story data
    story_impact: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True

class TownActionRequest(BaseModel):
    """Request for town actions."""
    character_id: str
    action_type: str = Field(..., pattern="^(rest|shop|train|quest|inn)$")
    action_data: Dict[str, Any] = Field(default_factory=dict)  # Additional action parameters