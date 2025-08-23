"""
File: models/combat.py
Path: /models/combat.py

Combat models for D&D Desktop game.
Manages combat sessions, turns, and actions.

Pseudo Code:
1. Define CombatSession model for tracking active encounters
2. Store combatant information and turn order
3. Track combat actions and results
4. Manage initiative and round progression
5. Handle combat state persistence

AI Agents: Combat tracking and turn management.
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from core.database import Base


class CombatSession(Base):
    """Active combat encounter session."""
    __tablename__ = "combat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    
    # Combat state
    is_active = Column(Boolean, default=True)
    current_round = Column(Integer, default=1)
    current_turn = Column(Integer, default=0)
    
    # Participants
    combatants = Column(JSON, default=lambda: [])  # List of character and monster data
    turn_order = Column(JSON, default=lambda: [])  # Initiative order
    
    # Combat log
    actions_log = Column(JSON, default=lambda: [])  # List of actions taken
    
    # Metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    character = relationship("Character")


class CombatAction(Base):
    """Individual combat action record."""
    __tablename__ = "combat_actions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    combat_session_id = Column(String, ForeignKey("combat_sessions.id"), nullable=False)
    
    # Action details
    round_number = Column(Integer, nullable=False)
    actor_id = Column(String, nullable=False)  # Character or monster ID
    actor_type = Column(String, nullable=False)  # "character" or "monster"
    action_type = Column(String, nullable=False)  # "attack", "cast_spell", etc.
    
    # Action data
    action_data = Column(JSON, default=lambda: {})  # Specific action details
    result_data = Column(JSON, default=lambda: {})  # Results (damage, effects, etc.)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    combat_session = relationship("CombatSession")