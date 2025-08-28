"""
File: models/game_indexeddb.py
Path: /models/game_indexeddb.py

IndexedDB-compatible game state models for TaleKeeper Desktop.
Manages save slots and persistent game state without SQLAlchemy.

Pseudo Code:
1. Define SaveSlot dataclass for managing multiple character saves
2. Store GameState for character progression and world state
3. Handle location tracking and exploration progress
4. Manage encounter history and random bag state
5. Support save/load functionality

AI Agents: Game state persistence and save management.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime


@dataclass
class SaveSlot:
    """Character save slots (1-10) for IndexedDB storage."""
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    slot_number: int = 1  # 1-10
    is_occupied: bool = False
    
    # Save metadata
    save_name: Optional[str] = None  # Optional name for save
    last_played: Optional[str] = None  # ISO datetime string
    play_time_minutes: int = 0
    
    # Quick save info
    character_name: Optional[str] = None
    character_level: Optional[int] = None
    current_location: Optional[str] = None
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert save slot to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaveSlot':
        """Create save slot from dictionary from IndexedDB."""
        return cls(**data)


@dataclass
class GameState:
    """Persistent game state for a character for IndexedDB storage."""
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    character_id: str = ""
    
    # Current game state
    current_location: str = "Starting Town"
    location_type: str = "town"  # town, dungeon, wilderness
    
    # World state
    discovered_locations: List[str] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)
    quest_flags: Dict[str, Any] = field(default_factory=dict)
    world_events: Dict[str, Any] = field(default_factory=dict)
    
    # Random bag system for encounters
    encounter_bag_remaining: Dict[str, List[str]] = field(default_factory=dict)  # location_type -> [monster_ids]
    encounter_bag_history: Dict[str, List[str]] = field(default_factory=dict)    # location_type -> [used_monster_ids]
    
    # Game statistics
    total_play_time_minutes: int = 0
    encounters_won: int = 0
    encounters_fled: int = 0
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Create game state from dictionary from IndexedDB."""
        # Handle missing fields gracefully
        defaults = {
            'discovered_locations': [],
            'completed_quests': [],
            'quest_flags': {},
            'world_events': {},
            'encounter_bag_remaining': {},
            'encounter_bag_history': {},
            'created_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return cls(**data)