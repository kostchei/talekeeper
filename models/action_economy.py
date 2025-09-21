"""
Action Economy System for D&D 5e Combat

Enforces the core D&D 5e rule: On each turn, a creature can take:
- ONE Action (Attack, Cast a Spell, Dash, Disengage, Dodge, Help, Hide, Ready, Search, Use an Object)
- ONE Bonus Action (if available from class features, spells, or abilities) 
- ONE Reaction per round (not per turn - persists until start of next turn)
- Any amount of Free Actions/Object Interactions

This system tracks action usage per turn and resets appropriately.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Set, List, Any
from enum import Enum
from datetime import datetime


class ActionEconomyType(Enum):
    """Types of actions in D&D 5e action economy."""
    ACTION = "action"
    BONUS_ACTION = "bonus_action" 
    REACTION = "reaction"
    FREE_ACTION = "free_action"
    MOVEMENT = "movement"


class ActionStatus(Enum):
    """Status of an action type for the current turn/round."""
    AVAILABLE = "available"
    USED = "used"
    UNAVAILABLE = "unavailable"  # Not available due to conditions, features, etc.


@dataclass
class ActionEconomyState:
    """
    Tracks action economy for a single combatant during combat.
    
    Key Rules:
    - Action & Bonus Action: Reset at start of each turn
    - Reaction: Resets at start of creature's next turn (not each turn in initiative)
    - Movement: Has a pool that resets each turn
    - Free Actions: Unlimited (but DM discretion)
    """
    
    # Combatant identification
    combatant_id: str = ""
    combatant_name: str = ""
    combatant_type: str = "character"  # "character" or "monster"
    
    # Current combat state
    current_round: int = 1
    current_turn_in_initiative: int = 0  # Position in initiative order
    is_active_turn: bool = False
    
    # Action availability (resets each turn)
    action_available: bool = True
    bonus_action_available: bool = True
    
    # Reaction availability (resets at start of this creature's next turn)
    reaction_available: bool = True
    last_reaction_round: int = 0  # Track when reaction was used
    
    # Movement (speed pool)
    movement_speed: int = 30  # Base movement in feet
    movement_used: int = 0    # Movement used this turn
    
    # Action history for this combat
    actions_taken_this_turn: List[Dict[str, Any]] = field(default_factory=list)
    actions_taken_this_round: List[Dict[str, Any]] = field(default_factory=list)
    
    # Special states
    has_action_surge: bool = False  # Fighter feature
    action_surge_used: bool = False

    # Class Action Tracking (Stage 3.2 Enhancement)
    class_actions_used: Dict[str, int] = field(default_factory=dict)  # action_id -> uses_this_combat
    resource_usage: Dict[str, int] = field(default_factory=dict)  # resource_name -> amount_used
    active_effects: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # effect_id -> effect_data

    # Duration tracking for ongoing effects
    ongoing_durations: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # effect_id -> duration_info

    # Metadata
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def start_new_turn(self, round_number: int, turn_position: int):
        """Start a new turn - reset action economy."""
        self.current_round = round_number
        self.current_turn_in_initiative = turn_position
        self.is_active_turn = True

        # Reset per-turn resources
        self.action_available = True
        self.bonus_action_available = True
        self.movement_used = 0
        self.actions_taken_this_turn = []

        # Reset reaction if it's this creature's turn
        self.reaction_available = True

        # Reset Action Surge if it's a new combat day (would be handled elsewhere)

        # Update effect durations (Stage 3.2 Enhancement)
        self.update_effect_durations()

        self.last_updated = datetime.now().isoformat()
    
    def end_turn(self):
        """End the current turn."""
        self.is_active_turn = False
        # Move current turn actions to round history
        self.actions_taken_this_round.extend(self.actions_taken_this_turn)
        self.last_updated = datetime.now().isoformat()
    
    def start_new_round(self, round_number: int):
        """Start a new round - minimal resets (reactions stay consumed until owner's turn)."""
        self.current_round = round_number
        self.actions_taken_this_round = []
        self.last_updated = datetime.now().isoformat()
    
    def use_action(self, action_type: ActionEconomyType, action_name: str, action_data: Dict = None) -> bool:
        """
        Attempt to use an action. Returns True if successful, False if not available.
        """
        if action_data is None:
            action_data = {}
            
        action_record = {
            "type": action_type.value,
            "name": action_name,
            "data": action_data,
            "timestamp": datetime.now().isoformat(),
            "round": self.current_round,
            "turn_position": self.current_turn_in_initiative
        }
        
        # Check availability and consume resource
        if action_type == ActionEconomyType.ACTION:
            if not self.action_available:
                return False
            self.action_available = False
            
        elif action_type == ActionEconomyType.BONUS_ACTION:
            if not self.bonus_action_available:
                return False
            self.bonus_action_available = False
            
        elif action_type == ActionEconomyType.REACTION:
            if not self.reaction_available:
                return False
            self.reaction_available = False
            self.last_reaction_round = self.current_round
            
        elif action_type == ActionEconomyType.MOVEMENT:
            movement_cost = action_data.get("movement_cost", 0)
            if self.movement_used + movement_cost > self.movement_speed:
                return False
            self.movement_used += movement_cost
            
        elif action_type == ActionEconomyType.FREE_ACTION:
            # Free actions are generally unlimited, but track them
            pass
        
        # Record the action
        self.actions_taken_this_turn.append(action_record)
        self.last_updated = datetime.now().isoformat()
        return True
    
    def use_action_surge(self) -> bool:
        """Use Fighter Action Surge to gain an additional action."""
        if not self.has_action_surge or self.action_surge_used:
            return False
            
        self.action_surge_used = True
        self.action_available = True  # Gain another action
        
        # Record the action surge use
        action_record = {
            "type": "special",
            "name": "Action Surge",
            "data": {"grants_extra_action": True},
            "timestamp": datetime.now().isoformat(),
            "round": self.current_round,
            "turn_position": self.current_turn_in_initiative
        }
        self.actions_taken_this_turn.append(action_record)
        self.last_updated = datetime.now().isoformat()
        return True

    def track_class_action(self, action_id: str, action_name: str, resource_cost: Dict[str, int] = None,
                          effect_duration: Optional[Dict[str, Any]] = None) -> bool:
        """Track usage of a class-specific action (Stage 3.2 Enhancement)."""

        # Track action usage count
        self.class_actions_used[action_id] = self.class_actions_used.get(action_id, 0) + 1

        # Track resource consumption
        if resource_cost:
            for resource_name, amount in resource_cost.items():
                self.resource_usage[resource_name] = self.resource_usage.get(resource_name, 0) + amount

        # Track ongoing effects with duration
        if effect_duration:
            effect_id = f"{action_id}_{len(self.ongoing_durations)}"
            self.ongoing_durations[effect_id] = {
                "action_id": action_id,
                "action_name": action_name,
                "start_round": self.current_round,
                "start_turn": self.current_turn_in_initiative,
                "duration_type": effect_duration.get("type", "rounds"),  # rounds, turns, until_end_of_combat
                "duration_value": effect_duration.get("value", 1),
                "effect_data": effect_duration.get("data", {}),
                "timestamp": datetime.now().isoformat()
            }

        # Log the action
        action_record = {
            "type": "class_action",
            "action_id": action_id,
            "name": action_name,
            "resource_cost": resource_cost or {},
            "effect_duration": effect_duration,
            "timestamp": datetime.now().isoformat(),
            "round": self.current_round,
            "turn_position": self.current_turn_in_initiative
        }
        self.actions_taken_this_turn.append(action_record)
        self.last_updated = datetime.now().isoformat()
        return True

    def update_effect_durations(self):
        """Update durations for ongoing effects - called at start of turn/round."""
        to_remove = []

        for effect_id, effect_data in self.ongoing_durations.items():
            duration_type = effect_data["duration_type"]
            duration_value = effect_data["duration_value"]
            start_round = effect_data["start_round"]
            start_turn = effect_data["start_turn"]

            should_expire = False

            if duration_type == "rounds":
                # Effect expires after X rounds from start
                if self.current_round >= start_round + duration_value:
                    should_expire = True
            elif duration_type == "turns":
                # Effect expires after X turns (more complex tracking needed)
                turn_count = (self.current_round - start_round) * 10 + (self.current_turn_in_initiative - start_turn)
                if turn_count >= duration_value:
                    should_expire = True
            elif duration_type == "end_of_turn":
                # Effect expires at end of this creature's turn
                if self.current_round > start_round or (self.current_round == start_round and not self.is_active_turn):
                    should_expire = True

            if should_expire:
                to_remove.append(effect_id)

        # Remove expired effects
        for effect_id in to_remove:
            del self.ongoing_durations[effect_id]

        self.last_updated = datetime.now().isoformat()

    def get_resource_usage(self, resource_name: str) -> int:
        """Get total usage of a specific resource this combat."""
        return self.resource_usage.get(resource_name, 0)

    def get_action_usage_count(self, action_id: str) -> int:
        """Get number of times a specific action has been used this combat."""
        return self.class_actions_used.get(action_id, 0)

    def get_active_effects(self) -> Dict[str, Dict[str, Any]]:
        """Get all currently active effects."""
        return self.ongoing_durations.copy()

    def has_active_effect(self, action_id: str) -> bool:
        """Check if a specific action has an active ongoing effect."""
        for effect_data in self.ongoing_durations.values():
            if effect_data["action_id"] == action_id:
                return True
        return False

    def get_action_status(self, action_type: ActionEconomyType) -> ActionStatus:
        """Get current availability status of an action type."""
        if action_type == ActionEconomyType.ACTION:
            return ActionStatus.AVAILABLE if self.action_available else ActionStatus.USED
        elif action_type == ActionEconomyType.BONUS_ACTION:
            return ActionStatus.AVAILABLE if self.bonus_action_available else ActionStatus.USED
        elif action_type == ActionEconomyType.REACTION:
            return ActionStatus.AVAILABLE if self.reaction_available else ActionStatus.USED
        elif action_type == ActionEconomyType.MOVEMENT:
            return ActionStatus.AVAILABLE if self.movement_used < self.movement_speed else ActionStatus.USED
        else:
            return ActionStatus.AVAILABLE
    
    def get_remaining_movement(self) -> int:
        """Get remaining movement for this turn."""
        return max(0, self.movement_speed - self.movement_used)
    
    def can_take_action(self, action_type: ActionEconomyType) -> bool:
        """Check if an action type can currently be taken."""
        return self.get_action_status(action_type) == ActionStatus.AVAILABLE
    
    def get_turn_summary(self) -> Dict[str, Any]:
        """Get a summary of this turn's action economy state."""
        return {
            "combatant": self.combatant_name,
            "round": self.current_round,
            "turn_position": self.current_turn_in_initiative,
            "action_available": self.action_available,
            "bonus_action_available": self.bonus_action_available,
            "reaction_available": self.reaction_available,
            "movement_remaining": self.get_remaining_movement(),
            "actions_taken": len(self.actions_taken_this_turn),
            "is_active": self.is_active_turn
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        from dataclasses import asdict
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionEconomyState':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class CombatActionEconomy:
    """
    Manages action economy for an entire combat encounter.
    
    Tracks all combatants and enforces D&D 5e action economy rules.
    """
    
    # Combat identification
    combat_session_id: str = ""
    
    # Combat state
    current_round: int = 1
    current_turn: int = 0  # Index in turn_order
    turn_order: List[str] = field(default_factory=list)  # List of combatant IDs in initiative order
    
    # Action economy states for each combatant
    combatant_states: Dict[str, ActionEconomyState] = field(default_factory=dict)
    
    # Combat metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_combatant(self, combatant_id: str, name: str, combatant_type: str = "character", 
                      movement_speed: int = 30, has_action_surge: bool = False):
        """Add a combatant to the action economy tracking."""
        state = ActionEconomyState(
            combatant_id=combatant_id,
            combatant_name=name,
            combatant_type=combatant_type,
            current_round=self.current_round,
            movement_speed=movement_speed,
            has_action_surge=has_action_surge
        )
        self.combatant_states[combatant_id] = state
        self.last_updated = datetime.now().isoformat()
    
    def start_combat(self, initiative_order: List[str]):
        """Start combat with the given initiative order."""
        self.turn_order = initiative_order
        self.current_round = 1
        self.current_turn = 0
        
        # Initialize all combatants for first round
        for combatant_id in self.combatant_states:
            self.combatant_states[combatant_id].start_new_round(1)
            
        # Start first combatant's turn
        if self.turn_order:
            self._start_combatant_turn(self.turn_order[0])
        
        self.last_updated = datetime.now().isoformat()
    
    def next_turn(self) -> Optional[str]:
        """Advance to the next turn. Returns the ID of the next active combatant."""
        # End current combatant's turn
        if self.turn_order and self.current_turn < len(self.turn_order):
            current_combatant = self.turn_order[self.current_turn]
            if current_combatant in self.combatant_states:
                self.combatant_states[current_combatant].end_turn()
        
        # Advance turn
        self.current_turn += 1
        
        # Check if we need to start a new round
        if self.current_turn >= len(self.turn_order):
            self.current_turn = 0
            self.current_round += 1
            
            # Start new round for all combatants
            for combatant_id in self.combatant_states:
                self.combatant_states[combatant_id].start_new_round(self.current_round)
        
        # Start next combatant's turn
        if self.turn_order:
            next_combatant = self.turn_order[self.current_turn]
            self._start_combatant_turn(next_combatant)
            self.last_updated = datetime.now().isoformat()
            return next_combatant
        
        return None
    
    def _start_combatant_turn(self, combatant_id: str):
        """Start a combatant's turn."""
        if combatant_id in self.combatant_states:
            self.combatant_states[combatant_id].start_new_turn(
                self.current_round, 
                self.current_turn
            )
    
    def get_active_combatant(self) -> Optional[str]:
        """Get the ID of the currently active combatant."""
        if self.turn_order and self.current_turn < len(self.turn_order):
            return self.turn_order[self.current_turn]
        return None
    
    def use_action(self, combatant_id: str, action_type: ActionEconomyType, 
                   action_name: str, action_data: Dict = None) -> bool:
        """Attempt to use an action for a combatant."""
        if combatant_id not in self.combatant_states:
            return False
            
        success = self.combatant_states[combatant_id].use_action(
            action_type, action_name, action_data or {}
        )
        
        if success:
            self.last_updated = datetime.now().isoformat()
            
        return success

    def track_class_action(self, combatant_id: str, action_id: str, action_name: str,
                          resource_cost: Dict[str, int] = None,
                          effect_duration: Optional[Dict[str, Any]] = None) -> bool:
        """Track a class-specific action for a combatant (Stage 3.2 Enhancement)."""
        if combatant_id not in self.combatant_states:
            return False

        success = self.combatant_states[combatant_id].track_class_action(
            action_id, action_name, resource_cost, effect_duration
        )

        if success:
            self.last_updated = datetime.now().isoformat()

        return success

    def get_combatant_resource_usage(self, combatant_id: str, resource_name: str) -> int:
        """Get resource usage for a specific combatant."""
        if combatant_id not in self.combatant_states:
            return 0
        return self.combatant_states[combatant_id].get_resource_usage(resource_name)

    def get_combatant_action_count(self, combatant_id: str, action_id: str) -> int:
        """Get action usage count for a specific combatant."""
        if combatant_id not in self.combatant_states:
            return 0
        return self.combatant_states[combatant_id].get_action_usage_count(action_id)

    def get_combatant_active_effects(self, combatant_id: str) -> Dict[str, Dict[str, Any]]:
        """Get active effects for a specific combatant."""
        if combatant_id not in self.combatant_states:
            return {}
        return self.combatant_states[combatant_id].get_active_effects()

    def get_combatant_state(self, combatant_id: str) -> Optional[ActionEconomyState]:
        """Get the action economy state for a specific combatant."""
        return self.combatant_states.get(combatant_id)
    
    def get_combat_summary(self) -> Dict[str, Any]:
        """Get a summary of the current combat state."""
        active_combatant = self.get_active_combatant()
        
        return {
            "combat_session_id": self.combat_session_id,
            "current_round": self.current_round,
            "current_turn": self.current_turn,
            "active_combatant": active_combatant,
            "turn_order": self.turn_order,
            "combatant_summaries": {
                cid: state.get_turn_summary() 
                for cid, state in self.combatant_states.items()
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        from dataclasses import asdict
        result = asdict(self)
        # Convert combatant_states to serializable format
        result["combatant_states"] = {
            cid: state.to_dict() for cid, state in self.combatant_states.items()
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CombatActionEconomy':
        """Create from dictionary."""
        # Handle combatant_states separately
        combatant_states_data = data.pop("combatant_states", {})
        
        instance = cls(**data)
        
        # Reconstruct combatant states
        for cid, state_data in combatant_states_data.items():
            instance.combatant_states[cid] = ActionEconomyState.from_dict(state_data)
        
        return instance