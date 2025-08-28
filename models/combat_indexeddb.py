"""
File: models/combat_indexeddb.py
Path: /models/combat_indexeddb.py

IndexedDB-compatible combat models for TaleKeeper Desktop.
Manages combat sessions, turns, and actions without SQLAlchemy.

Pseudo Code:
1. Define CombatSession dataclass for tracking active encounters
2. Store combatant information and turn order
3. Track combat actions and results
4. Manage initiative and round progression
5. Handle combat state persistence

AI Agents: Combat tracking and turn management.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime


@dataclass
class CombatSession:
    """Active combat encounter session for IndexedDB storage."""
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    character_id: str = ""
    
    # Combat state
    is_active: bool = True
    current_round: int = 1
    current_turn: int = 0
    
    # Participants
    combatants: List[Dict[str, Any]] = field(default_factory=list)  # List of character and monster data
    turn_order: List[str] = field(default_factory=list)  # Initiative order
    
    # Combat log
    actions_log: List[Dict[str, Any]] = field(default_factory=list)  # List of actions taken
    
    # Metadata
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert combat session to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CombatSession':
        """Create combat session from dictionary from IndexedDB."""
        # Handle missing fields gracefully
        defaults = {
            'combatants': [],
            'turn_order': [],
            'actions_log': [],
            'started_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return cls(**data)


@dataclass
class CombatAction:
    """Individual combat action record for IndexedDB storage."""
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    combat_session_id: str = ""
    
    # Action details
    round_number: int = 1
    actor_id: str = ""  # Character or monster ID
    actor_type: str = "character"  # "character" or "monster"
    action_type: str = "attack"  # "attack", "cast_spell", etc.
    
    # Action data
    action_data: Dict[str, Any] = field(default_factory=dict)  # Specific action details
    result_data: Dict[str, Any] = field(default_factory=dict)  # Results (damage, effects, etc.)
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert combat action to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CombatAction':
        """Create combat action from dictionary from IndexedDB."""
        # Handle missing fields gracefully
        defaults = {
            'action_data': {},
            'result_data': {},
            'timestamp': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return cls(**data)