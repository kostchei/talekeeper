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
from .action_economy import CombatActionEconomy


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
    
    # Action Economy - NEW: D&D 5e action economy enforcement
    action_economy: Optional[CombatActionEconomy] = None
    
    # Combat log
    actions_log: List[Dict[str, Any]] = field(default_factory=list)  # List of actions taken
    
    # Metadata
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert combat session to dictionary for IndexedDB storage."""
        result = asdict(self)
        # Handle action_economy serialization
        if self.action_economy:
            result["action_economy"] = self.action_economy.to_dict()
        return result
    
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
        
        # Handle action_economy deserialization
        action_economy_data = data.pop("action_economy", None)
        instance = cls(**data)
        
        if action_economy_data:
            instance.action_economy = CombatActionEconomy.from_dict(action_economy_data)
        
        return instance
    
    def start_combat_with_action_economy(self, initiative_order: List[str], combatant_data: List[Dict[str, Any]]):
        """Initialize combat session with action economy tracking."""
        self.turn_order = initiative_order
        self.current_round = 1
        self.current_turn = 0
        
        # Create action economy tracker
        self.action_economy = CombatActionEconomy(
            combat_session_id=self.id,
            current_round=1,
            current_turn=0,
            turn_order=initiative_order
        )
        
        # Add all combatants to action economy
        for combatant in combatant_data:
            self.action_economy.add_combatant(
                combatant_id=combatant.get("id", ""),
                name=combatant.get("name", "Unknown"),
                combatant_type=combatant.get("type", "character"),
                movement_speed=combatant.get("movement_speed", 30),
                has_action_surge=combatant.get("has_action_surge", False)
            )
        
        # Start combat
        self.action_economy.start_combat(initiative_order)
        self.is_active = True
    
    def next_turn(self) -> Optional[str]:
        """Advance to the next turn using action economy."""
        if not self.action_economy:
            # Fallback to basic turn advancement
            self.current_turn += 1
            if self.current_turn >= len(self.turn_order):
                self.current_turn = 0
                self.current_round += 1
            return self.turn_order[self.current_turn] if self.turn_order else None
        
        # Use action economy for turn management
        next_combatant = self.action_economy.next_turn()
        
        # Sync our state with action economy
        self.current_round = self.action_economy.current_round
        self.current_turn = self.action_economy.current_turn
        
        return next_combatant
    
    def can_take_action(self, combatant_id: str, action_type: str) -> bool:
        """Check if a combatant can take a specific type of action."""
        if not self.action_economy:
            return True  # No restrictions if action economy not initialized
        
        from .action_economy import ActionEconomyType
        
        # Map action type strings to ActionEconomyType
        action_type_mapping = {
            "action": ActionEconomyType.ACTION,
            "bonus_action": ActionEconomyType.BONUS_ACTION,
            "reaction": ActionEconomyType.REACTION,
            "movement": ActionEconomyType.MOVEMENT,
            "free_action": ActionEconomyType.FREE_ACTION
        }
        
        economy_type = action_type_mapping.get(action_type.lower())
        if not economy_type:
            return True  # Unknown action types are allowed
        
        state = self.action_economy.get_combatant_state(combatant_id)
        return state.can_take_action(economy_type) if state else False
    
    def use_action(self, combatant_id: str, action_type: str, action_name: str, action_data: Dict = None) -> bool:
        """Attempt to use an action and record it."""
        if not self.action_economy:
            # Just log the action without restrictions
            self.actions_log.append({
                "combatant_id": combatant_id,
                "action_type": action_type,
                "action_name": action_name,
                "action_data": action_data or {},
                "timestamp": datetime.now().isoformat(),
                "round": self.current_round
            })
            return True
        
        from .action_economy import ActionEconomyType
        
        # Map action type strings to ActionEconomyType
        action_type_mapping = {
            "action": ActionEconomyType.ACTION,
            "bonus_action": ActionEconomyType.BONUS_ACTION,
            "reaction": ActionEconomyType.REACTION,
            "movement": ActionEconomyType.MOVEMENT,
            "free_action": ActionEconomyType.FREE_ACTION
        }
        
        economy_type = action_type_mapping.get(action_type.lower())
        if not economy_type:
            economy_type = ActionEconomyType.FREE_ACTION
        
        # Try to use the action
        success = self.action_economy.use_action(combatant_id, economy_type, action_name, action_data or {})
        
        if success:
            # Log the action
            self.actions_log.append({
                "combatant_id": combatant_id,
                "action_type": action_type,
                "action_name": action_name,
                "action_data": action_data or {},
                "timestamp": datetime.now().isoformat(),
                "round": self.current_round,
                "turn": self.current_turn,
                "success": True
            })
        else:
            # Log the failed attempt
            self.actions_log.append({
                "combatant_id": combatant_id,
                "action_type": action_type,
                "action_name": action_name,
                "action_data": action_data or {},
                "timestamp": datetime.now().isoformat(),
                "round": self.current_round,
                "turn": self.current_turn,
                "success": False,
                "reason": f"No {action_type} available"
            })
        
        return success


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