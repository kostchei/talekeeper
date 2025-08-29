"""
File: models/game.py
Path: /models/game.py

Game state models for D&D Desktop game.
Manages save slots and persistent game state.

Pseudo Code:
1. Define SaveSlot model for managing multiple character saves
2. Store GameState for character progression and world state
3. Handle location tracking and exploration progress
4. Manage encounter history and random bag state
5. Support save/load functionality

AI Agents: Game state persistence and save management.
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from core.database import Base


class SaveSlot(Base):
    """Character save slots (1-10)."""
    __tablename__ = "save_slots"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    slot_number = Column(Integer, nullable=False, unique=True)  # 1-10
    is_occupied = Column(Boolean, default=False)
    
    # Save metadata
    save_name = Column(String(100), nullable=True)  # Optional name for save
    last_played = Column(DateTime(timezone=True), nullable=True)
    play_time_minutes = Column(Integer, default=0)
    
    # Quick save info
    character_name = Column(String(100), nullable=True)
    character_level = Column(Integer, nullable=True)
    current_location = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    characters = relationship("Character", back_populates="save_slot")


class GameState(Base):
    """Persistent game state for a character."""
    __tablename__ = "game_states"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    character_id = Column(String, ForeignKey("characters.id"), nullable=False, unique=True)
    
    # Current game state
    current_location = Column(String(100), default="Starting Town")
    location_type = Column(String(50), default="town")  # town, dungeon, wilderness
    
    # World state
    discovered_locations = Column(JSON, default=lambda: [])
    completed_quests = Column(JSON, default=lambda: [])
    quest_flags = Column(JSON, default=lambda: {})
    world_events = Column(JSON, default=lambda: {})
    
    # Random bag system for encounters
    encounter_bag_remaining = Column(JSON, default=lambda: {})  # location_type -> [monster_ids]
    encounter_bag_history = Column(JSON, default=lambda: {})    # location_type -> [used_monster_ids]
    
    # Game statistics
    total_play_time_minutes = Column(Integer, default=0)
    encounters_won = Column(Integer, default=0)
    encounters_fled = Column(Integer, default=0)
    total_damage_dealt = Column(Integer, default=0)
    total_damage_taken = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    character = relationship("Character", back_populates="game_states")