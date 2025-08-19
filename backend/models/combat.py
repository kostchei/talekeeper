"""
Combat encounter models for D&D game.
AI Agents: Track initiative, actions, and turn-based combat state.
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

class EncounterStatus(str, Enum):
    """Combat encounter states."""
    SETUP = "setup"
    ACTIVE = "active"
    VICTORY = "victory"
    DEFEAT = "defeat"
    FLED = "fled"
    PAUSED = "paused"

class ActionType(str, Enum):
    """Types of combat actions."""
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    MOVEMENT = "movement"
    FREE_ACTION = "free_action"
    LEGENDARY_ACTION = "legendary_action"

class CombatEncounter(Base):
    """
    D&D Combat Encounter with initiative tracking.
    AI Agents: Extend with environment effects and dynamic objectives.
    """
    __tablename__ = "combat_encounters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, default="Combat Encounter")
    description = Column(Text, default="")
    
    # Encounter state
    status = Column(SQLEnum(EncounterStatus), nullable=False, default=EncounterStatus.SETUP)
    current_round = Column(Integer, default=0)
    current_turn = Column(Integer, default=0)  # Index in initiative order
    
    # Participants and initiative
    initiative_order = Column(JSON, default=list)  # Ordered list of participant data
    participants = Column(JSON, default=dict)  # Map of participant_id -> combat data
    
    # Environment
    battlefield_size = Column(String(20), default="medium")  # small, medium, large
    environment_type = Column(String(50), default="dungeon")
    environmental_effects = Column(JSON, default=list)  # Weather, terrain, etc.
    
    # Combat options
    surprise_round = Column(Boolean, default=False)
    legendary_actions_enabled = Column(Boolean, default=True)
    
    # Metadata
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    actions = relationship("CombatAction", back_populates="encounter", cascade="all, delete-orphan")
    logs = relationship("CombatLog", back_populates="encounter", cascade="all, delete-orphan")

class CombatAction(Base):
    """
    Individual actions taken during combat.
    AI Agents: Track detailed action history for AI learning and replay.
    """
    __tablename__ = "combat_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("combat_encounters.id", ondelete="CASCADE"), nullable=False)
    
    # Action details
    round_number = Column(Integer, nullable=False)
    turn_number = Column(Integer, nullable=False)
    actor_id = Column(String(100), nullable=False)  # character_id or monster instance id
    actor_type = Column(String(20), nullable=False)  # "character" or "monster"
    
    # Action data
    action_type = Column(SQLEnum(ActionType), nullable=False)
    action_name = Column(String(100), nullable=False)
    action_description = Column(Text, default="")
    
    # Targets and results
    targets = Column(JSON, default=list)  # List of target data
    dice_rolls = Column(JSON, default=dict)  # All dice rolls made
    damage_dealt = Column(JSON, default=dict)  # Damage by target and type
    healing_done = Column(JSON, default=dict)  # Healing by target
    conditions_applied = Column(JSON, default=list)  # Status effects applied
    
    # Success/failure
    attack_roll = Column(Integer, nullable=True)
    target_ac = Column(Integer, nullable=True)
    hit = Column(Boolean, nullable=True)
    critical = Column(Boolean, default=False)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    encounter = relationship("CombatEncounter", back_populates="actions")

class CombatLog(Base):
    """
    Narrative log of combat events.
    AI Agents: Generate rich descriptions and maintain combat story.
    """
    __tablename__ = "combat_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("combat_encounters.id", ondelete="CASCADE"), nullable=False)
    
    # Log entry data
    round_number = Column(Integer, nullable=False)
    turn_number = Column(Integer, nullable=False)
    log_type = Column(String(20), nullable=False)  # action, damage, heal, effect, system
    
    # Content
    message = Column(Text, nullable=False)
    detailed_message = Column(Text, nullable=True)  # AI-generated rich description
    
    # Context
    actor_name = Column(String(100), nullable=True)
    target_names = Column(JSON, default=list)
    mechanical_data = Column(JSON, default=dict)  # Raw game data for reference
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    encounter = relationship("CombatEncounter", back_populates="logs")

# Pydantic Models for API
class InitiativeEntry(BaseModel):
    """Single initiative entry for combat order."""
    participant_id: str
    participant_name: str
    participant_type: str  # "character" or "monster"
    initiative_roll: int
    dexterity_modifier: int
    initiative_total: int
    
    # Current state
    hit_points_current: int
    hit_points_max: int
    armor_class: int
    conditions: List[str] = Field(default_factory=list)
    
    # Turn tracking
    actions_used: Dict[str, int] = Field(default_factory=dict)  # action_type -> count
    reactions_available: int = 1
    legendary_actions_remaining: int = 0
    
class EncounterSetup(BaseModel):
    """Data to set up a new combat encounter."""
    name: str = Field(default="Combat Encounter")
    description: str = ""
    
    # Participants
    character_ids: List[str] = Field(default_factory=list)
    monsters: List[Dict[str, Any]] = Field(default_factory=list)  # monster_id, quantity, hp_override
    
    # Environment
    battlefield_size: str = "medium"
    environment_type: str = "dungeon"
    environmental_effects: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Options
    surprise_round: bool = False
    auto_roll_initiative: bool = True

class CombatActionRequest(BaseModel):
    """Request to perform a combat action."""
    encounter_id: str
    actor_id: str
    action_type: ActionType
    action_name: str
    
    # Target information
    target_ids: List[str] = Field(default_factory=list)
    target_positions: List[Dict[str, int]] = Field(default_factory=list)  # For area effects
    
    # Action modifiers
    advantage: bool = False
    disadvantage: bool = False
    modifier_bonus: int = 0
    
    # Spell/ability specific
    spell_level: Optional[int] = None
    resource_cost: Dict[str, int] = Field(default_factory=dict)  # spell_slots, ki_points, etc.

class AttackRequest(BaseModel):
    """Specific request for attack actions."""
    encounter_id: str
    attacker_id: str
    target_id: str
    weapon_item_id: Optional[str] = None  # If using specific weapon
    attack_type: str = "melee"  # melee, ranged, spell
    
    # Modifiers
    advantage: bool = False
    disadvantage: bool = False
    bonus_to_hit: int = 0
    bonus_damage: str = ""  # Additional damage dice

class CombatResponse(BaseModel):
    """Combat encounter state for API responses."""
    id: str
    name: str
    description: str
    status: EncounterStatus
    current_round: int
    current_turn: int
    
    # Participants
    initiative_order: List[InitiativeEntry]
    current_participant: Optional[InitiativeEntry]
    
    # Environment
    battlefield_size: str
    environment_type: str
    environmental_effects: List[Dict[str, Any]]
    
    # Options
    surprise_round: bool
    legendary_actions_enabled: bool
    
    # Time tracking
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ActionResult(BaseModel):
    """Result of a combat action."""
    success: bool
    action_id: str
    
    # Action details
    actor_name: str
    action_name: str
    action_description: str
    
    # Results
    targets_hit: List[str]
    damage_dealt: Dict[str, Dict[str, int]]  # target_id -> damage_type -> amount
    healing_done: Dict[str, int]  # target_id -> amount
    conditions_applied: Dict[str, List[str]]  # target_id -> conditions
    
    # Dice rolls
    attack_rolls: List[int]
    damage_rolls: Dict[str, List[int]]  # damage_type -> rolls
    saving_throws: Dict[str, int]  # target_id -> roll
    
    # Critical information
    critical_hits: List[str]  # target_ids that were crit
    
    # Log messages
    summary_message: str
    detailed_message: str
    
    class Config:
        from_attributes = True

class CombatState(Base):
    """
    Current state of combat for quick access.
    AI Agents: Cached combat state for fast queries.
    """
    __tablename__ = "combat_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("combat_encounters.id", ondelete="CASCADE"), nullable=False)
    
    # Current state snapshot
    current_round = Column(Integer, default=0)
    current_turn = Column(Integer, default=0)
    current_participant_id = Column(String(100), nullable=True)
    
    # Fast access data
    participants_data = Column(JSON, default=dict)  # Full participant states
    turn_order = Column(JSON, default=list)  # Initiative order
    
    # Combat flags
    surprise_round = Column(Boolean, default=False)
    combat_started = Column(Boolean, default=False)
    
    # Last update
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CombatParticipant(BaseModel):
    """Participant in combat encounter."""
    participant_id: str
    name: str
    participant_type: str  # "character" or "monster"
    
    # Current stats
    hit_points_current: int
    hit_points_max: int
    armor_class: int
    initiative_total: int
    
    # Turn tracking
    actions_remaining: Dict[str, int] = Field(default_factory=dict)
    conditions: List[str] = Field(default_factory=list)
    position: str = "melee"  # melee, ranged
    
    class Config:
        from_attributes = True

class CombatStateResponse(BaseModel):
    """Combat state for API responses."""
    encounter_id: str
    current_round: int
    current_turn: int
    current_participant: Optional[CombatParticipant]
    
    participants: List[CombatParticipant]
    turn_order: List[str]
    
    combat_started: bool
    surprise_round: bool
    
    class Config:
        from_attributes = True

class CombatActionResponse(BaseModel):
    """Response to combat action."""
    success: bool
    message: str
    action_id: Optional[str]
    
    # Updated state
    updated_participants: List[CombatParticipant] = Field(default_factory=list)
    next_participant: Optional[str] = None
    round_advanced: bool = False
    
    class Config:
        from_attributes = True

class EncounterStartRequest(BaseModel):
    """Request to start a combat encounter."""
    name: str = Field(default="Combat Encounter")
    description: str = ""
    
    # Participants
    character_ids: List[str] = Field(default_factory=list)
    monster_encounters: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Environment
    battlefield_size: str = "medium"
    environment_type: str = "dungeon"
    environmental_effects: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Options
    surprise_round: bool = False
    auto_roll_initiative: bool = True

class EncounterEndResponse(BaseModel):
    """Response when encounter ends."""
    encounter_id: str
    outcome: str  # victory, defeat, fled
    duration_rounds: int
    
    # Rewards
    experience_gained: Dict[str, int] = Field(default_factory=dict)  # character_id -> xp
    loot_generated: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Statistics
    total_damage_dealt: int
    total_healing_done: int
    participants_defeated: List[str]
    
    class Config:
        from_attributes = True