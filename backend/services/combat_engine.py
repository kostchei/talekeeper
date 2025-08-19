"""
File: backend/services/combat_engine.py
Path: /backend/services/combat_engine.py

D&D 2024 Combat Engine
Handles all combat mechanics including initiative, actions, damage, and conditions.

Pseudo Code:
1. Initialize combat encounter with initiative rolls and turn order
2. Process player and monster actions (attacks, spells, movement)
3. Calculate damage, apply resistance/immunity, update HP
4. Handle status conditions (poisoned, stunned, etc.)
5. Check for combat end conditions (victory/defeat)
6. Manage turn progression and action economy

AI Agents: This is the core combat system. Key methods:
- start_combat(): Initialize encounter
- process_action(): Handle player/monster actions
- check_reactions(): Opportunity attacks, etc.
- end_turn(): Clean up and advance
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

from services.dice import DiceRoller

# Combat action types
class ActionType(Enum):
    """Types of actions in D&D combat"""
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    MOVEMENT = "movement"
    FREE = "free"  # Free actions like dropping items

class CombatPosition(Enum):
    """Simplified positioning system"""
    MELEE = "melee"  # In melee range (within 5 feet)
    RANGED = "ranged"  # Not in melee range

@dataclass
class Combatant:
    """
    Represents a creature in combat.
    AI Agents: Extend this for new creature abilities.
    """
    id: str
    name: str
    type: str  # "player" or "monster"
    # Stats
    max_hp: int
    current_hp: int
    ac: int
    initiative_bonus: int
    speed: int = 30
    # Abilities
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    # Combat state
    position: CombatPosition = CombatPosition.RANGED
    initiative: int = 0
    has_taken_action: bool = False
    has_taken_bonus: bool = False
    has_taken_reaction: bool = False
    movement_remaining: int = 30
    # Conditions and effects
    conditions: List[str] = field(default_factory=list)
    temp_hp: int = 0
    death_saves_success: int = 0
    death_saves_failure: int = 0
    # Actions available
    actions: List[Dict] = field(default_factory=list)
    bonus_actions: List[Dict] = field(default_factory=list)
    reactions: List[Dict] = field(default_factory=list)
    # AI behavior
    ai_script: Optional[str] = None
    
    def ability_modifier(self, ability: str) -> int:
        """Calculate ability modifier"""
        score = getattr(self, ability, 10)
        return (score - 10) // 2
    
    def is_alive(self) -> bool:
        """Check if combatant is still in the fight"""
        return self.current_hp > 0
    
    def take_damage(self, damage: int) -> int:
        """
        Apply damage to combatant.
        Returns actual damage taken after temp HP.
        """
        actual_damage = damage
        
        # Apply to temp HP first
        if self.temp_hp > 0:
            if damage <= self.temp_hp:
                self.temp_hp -= damage
                return 0
            else:
                damage -= self.temp_hp
                self.temp_hp = 0
        
        # Apply to regular HP
        self.current_hp = max(0, self.current_hp - damage)
        
        # Check for instant death (damage >= max HP while at 0)
        if self.current_hp == 0 and damage >= self.max_hp:
            logger.warning(f"{self.name} suffers instant death from massive damage!")
            self.death_saves_failure = 3
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal the combatant. Returns actual healing done."""
        if self.current_hp == 0:
            # Healing from 0 HP resets death saves
            self.death_saves_success = 0
            self.death_saves_failure = 0
        
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp

class CombatEngine:
    """
    Main combat engine implementing D&D 2024 rules.
    
    AI Agents: Key extension points:
    - Add new action types in process_action()
    - Add new conditions in apply_condition()
    - Add new AI behaviors in get_monster_action()
    """
    
    def __init__(self):
        self.dice = DiceRoller()
        self.combatants: Dict[str, Combatant] = {}
        self.turn_order: List[str] = []
        self.current_turn: int = 0
        self.round_number: int = 0
        self.combat_log: List[str] = []
        self.is_active: bool = False
        
    def start_combat(self, player: Combatant, monsters: List[Combatant]) -> Dict:
        """
        Initialize combat encounter.
        
        Args:
            player: The player character
            monsters: List of monsters in the encounter
            
        Returns:
            Combat state including turn order
        """
        self.combat_log = []
        self.round_number = 1
        self.current_turn = 0
        self.is_active = True
        
        # Add all combatants
        self.combatants = {player.id: player}
        for monster in monsters:
            self.combatants[monster.id] = monster
        
        # Roll initiative
        for combatant in self.combatants.values():
            roll = self.dice.roll("1d20")
            combatant.initiative = roll + combatant.initiative_bonus
            self.log(f"{combatant.name} rolls initiative: {roll} + {combatant.initiative_bonus} = {combatant.initiative}")
        
        # Sort by initiative (highest first)
        self.turn_order = sorted(
            self.combatants.keys(),
            key=lambda x: (self.combatants[x].initiative, self.combatants[x].dexterity),
            reverse=True
        )
        
        self.log(f"=== COMBAT BEGINS ===")
        self.log(f"Round {self.round_number}")
        
        return self.get_combat_state()
    
    def process_action(self, combatant_id: str, action: Dict, target_id: Optional[str] = None) -> Dict:
        """
        Process a combat action.
        
        Args:
            combatant_id: ID of acting combatant
            action: Action details (name, type, damage, etc.)
            target_id: Target combatant ID if applicable
            
        Returns:
            Result of the action
        """
        combatant = self.combatants.get(combatant_id)
        if not combatant:
            return {"error": "Invalid combatant"}
        
        target = self.combatants.get(target_id) if target_id else None
        
        # Check action availability
        action_type = ActionType(action.get("type", "action"))
        if not self._can_take_action(combatant, action_type):
            return {"error": f"Cannot take {action_type.value} - already used"}
        
        result = {"success": False, "description": ""}
        
        # Process based on action type
        if action.get("attack"):
            result = self._process_attack(combatant, target, action)
        elif action.get("heal"):
            result = self._process_healing(combatant, action)
        elif action.get("special"):
            result = self._process_special_ability(combatant, target, action)
        elif action_type == ActionType.MOVEMENT:
            result = self._process_movement(combatant, action)
        else:
            result = {"success": False, "description": "Unknown action type"}
        
        # Mark action as used
        self._mark_action_used(combatant, action_type)
        
        # Check for defeated enemies
        self._check_defeats()
        
        return result
    
    def _process_attack(self, attacker: Combatant, target: Combatant, action: Dict) -> Dict:
        """Process an attack action"""
        if not target or not target.is_alive():
            return {"success": False, "description": "Invalid target"}
        
        # Check range
        is_melee = action.get("range", "melee") == "melee"
        if is_melee and attacker.position != CombatPosition.MELEE:
            return {"success": False, "description": "Not in melee range"}
        
        # Roll to hit
        attack_bonus = action.get("bonus", 0)
        attack_roll = self.dice.roll("1d20")
        total_attack = attack_roll + attack_bonus
        
        # Check for critical
        is_crit = attack_roll == 20
        is_fumble = attack_roll == 1
        
        self.log(f"{attacker.name} attacks {target.name}: {attack_roll} + {attack_bonus} = {total_attack} vs AC {target.ac}")
        
        if is_fumble:
            self.log("Critical miss!")
            return {"success": False, "description": "Critical miss!", "roll": attack_roll}
        
        if is_crit or (not is_fumble and total_attack >= target.ac):
            # Roll damage
            damage_dice = action.get("damage", "1d6")
            damage_mod = action.get("damage_bonus", 0)
            
            if is_crit:
                # Double dice on crit
                parts = damage_dice.split('d')
                if len(parts) == 2:
                    num_dice = int(parts[0]) * 2
                    damage_dice = f"{num_dice}d{parts[1]}"
                self.log("Critical hit!")
            
            damage_roll = self.dice.roll(damage_dice)
            total_damage = damage_roll + damage_mod
            
            # Apply damage
            actual_damage = target.take_damage(total_damage)
            
            self.log(f"Hit! {damage_roll} + {damage_mod} = {total_damage} {action.get('damage_type', 'damage')}")
            self.log(f"{target.name} takes {actual_damage} damage ({target.current_hp}/{target.max_hp} HP)")
            
            return {
                "success": True,
                "description": f"Hit for {total_damage} damage",
                "attack_roll": attack_roll,
                "damage": total_damage,
                "is_crit": is_crit
            }
        else:
            self.log("Miss!")
            return {
                "success": False,
                "description": "Attack missed",
                "attack_roll": attack_roll
            }
    
    def _process_movement(self, combatant: Combatant, action: Dict) -> Dict:
        """Process movement action"""
        new_position = CombatPosition(action.get("position", "ranged"))
        old_position = combatant.position
        
        # Check if entering melee with enemies
        if new_position == CombatPosition.MELEE:
            # Check for opportunity attacks when leaving melee
            if old_position == CombatPosition.MELEE:
                # Leaving melee might provoke opportunity attacks
                # AI Agents: Implement opportunity attack logic here
                pass
        
        combatant.position = new_position
        movement_used = 15 if new_position != old_position else 0
        combatant.movement_remaining = max(0, combatant.movement_remaining - movement_used)
        
        self.log(f"{combatant.name} moves to {new_position.value} position")
        
        return {
            "success": True,
            "description": f"Moved to {new_position.value}",
            "movement_remaining": combatant.movement_remaining
        }
    
    def _process_healing(self, combatant: Combatant, action: Dict) -> Dict:
        """Process healing action"""
        heal_dice = action.get("heal", "2d4+2")
        heal_amount = self.dice.roll(heal_dice)
        actual_heal = combatant.heal(heal_amount)
        
        self.log(f"{combatant.name} heals for {heal_amount} ({actual_heal} actual)")
        self.log(f"{combatant.name} HP: {combatant.current_hp}/{combatant.max_hp}")
        
        return {
            "success": True,
            "description": f"Healed for {actual_heal} HP",
            "healing": actual_heal
        }
    
    def _process_special_ability(self, combatant: Combatant, target: Optional[Combatant], action: Dict) -> Dict:
        """
        Process special abilities like Second Wind, Action Surge, etc.
        AI Agents: Add new special abilities here.
        """
        ability_name = action.get("name", "Special Ability")
        
        # Fighter - Second Wind
        if "Second Wind" in ability_name:
            heal_dice = f"1d10+{combatant.level}"
            heal_amount = self.dice.roll(heal_dice)
            actual_heal = combatant.heal(heal_amount)
            
            self.log(f"{combatant.name} uses Second Wind: heals {actual_heal} HP")
            return {
                "success": True,
                "description": f"Second Wind: Recovered {actual_heal} HP",
                "healing": actual_heal
            }
        
        # Fighter - Action Surge
        if "Action Surge" in ability_name:
            combatant.has_taken_action = False  # Reset action
            self.log(f"{combatant.name} uses Action Surge - gains extra action!")
            return {
                "success": True,
                "description": "Action Surge: Gained additional action",
                "extra_action": True
            }
        
        # Rogue - Cunning Action
        if "Cunning Action" in ability_name:
            # Dash, Disengage, or Hide as bonus action
            sub_action = action.get("sub_action", "dash")
            if sub_action == "dash":
                combatant.movement_remaining += combatant.speed
                return {"success": True, "description": "Cunning Action: Dash"}
            elif sub_action == "disengage":
                combatant.conditions.append("disengaging")
                return {"success": True, "description": "Cunning Action: Disengage"}
            elif sub_action == "hide":
                # Simplified hide mechanic
                stealth_roll = self.dice.roll("1d20") + combatant.ability_modifier("dexterity")
                return {"success": True, "description": f"Cunning Action: Hide (Stealth: {stealth_roll})"}
        
        # Rogue - Sneak Attack
        if "Sneak Attack" in ability_name and target:
            # Check conditions for sneak attack
            can_sneak = (
                target.position == CombatPosition.MELEE or  # Advantage in melee
                any(c.position == CombatPosition.MELEE and c.type == "player" 
                    for c in self.combatants.values() if c.id != combatant.id)  # Ally in melee
            )
            
            if can_sneak:
                sneak_dice = f"{(combatant.level + 1) // 2}d6"  # 1d6 at level 1-2, 2d6 at 3-4, etc.
                sneak_damage = self.dice.roll(sneak_dice)
                target.take_damage(sneak_damage)
                self.log(f"Sneak Attack! Additional {sneak_damage} damage")
                return {"success": True, "description": f"Sneak Attack: {sneak_damage} extra damage"}
        
        return {"success": False, "description": f"Unknown ability: {ability_name}"}
    
    def _can_take_action(self, combatant: Combatant, action_type: ActionType) -> bool:
        """Check if combatant can take the specified action type"""
        if action_type == ActionType.ACTION:
            return not combatant.has_taken_action
        elif action_type == ActionType.BONUS_ACTION:
            return not combatant.has_taken_bonus
        elif action_type == ActionType.REACTION:
            return not combatant.has_taken_reaction
        elif action_type == ActionType.MOVEMENT:
            return combatant.movement_remaining > 0
        return True  # Free actions always available
    
    def _mark_action_used(self, combatant: Combatant, action_type: ActionType):
        """Mark an action type as used"""
        if action_type == ActionType.ACTION:
            combatant.has_taken_action = True
        elif action_type == ActionType.BONUS_ACTION:
            combatant.has_taken_bonus = True
        elif action_type == ActionType.REACTION:
            combatant.has_taken_reaction = True
    
    def end_turn(self) -> Dict:
        """
        End current turn and advance to next.
        AI Agents: Add end-of-turn effects here (damage over time, etc.)
        """
        current_combatant = self.combatants[self.turn_order[self.current_turn]]
        
        # Process end-of-turn effects
        self._process_end_of_turn_effects(current_combatant)
        
        # Advance turn
        self.current_turn += 1
        
        # Check for round end
        if self.current_turn >= len(self.turn_order):
            self.current_turn = 0
            self.round_number += 1
            self.log(f"=== Round {self.round_number} ===")
            
            # Reset actions for all combatants
            for combatant in self.combatants.values():
                combatant.has_taken_action = False
                combatant.has_taken_bonus = False
                combatant.has_taken_reaction = False
                combatant.movement_remaining = combatant.speed
        
        # Skip dead combatants
        while self.current_turn < len(self.turn_order):
            next_combatant = self.combatants[self.turn_order[self.current_turn]]
            if next_combatant.is_alive():
                break
            self.current_turn += 1
        
        return self.get_combat_state()
    
    def _process_end_of_turn_effects(self, combatant: Combatant):
        """Process effects that trigger at end of turn"""
        # Remove temporary conditions
        if "disengaging" in combatant.conditions:
            combatant.conditions.remove("disengaging")
        
        # Process damage over time effects
        # AI Agents: Add poison, burning, etc. here
        
        # Death saves for unconscious characters
        if combatant.current_hp == 0 and combatant.type == "player":
            self._process_death_save(combatant)
    
    def _process_death_save(self, combatant: Combatant):
        """Process death saving throws for dying characters"""
        if combatant.death_saves_failure >= 3:
            self.log(f"{combatant.name} has died!")
            return
        
        roll = self.dice.roll("1d20")
        
        if roll == 20:
            # Natural 20: regain 1 HP
            combatant.heal(1)
            combatant.death_saves_success = 0
            combatant.death_saves_failure = 0
            self.log(f"{combatant.name} rolls 20 on death save - regains consciousness with 1 HP!")
        elif roll == 1:
            # Natural 1: two failures
            combatant.death_saves_failure += 2
            self.log(f"{combatant.name} rolls 1 on death save - two failures! ({combatant.death_saves_failure}/3)")
        elif roll >= 10:
            # Success
            combatant.death_saves_success += 1
            self.log(f"{combatant.name} succeeds death save ({combatant.death_saves_success}/3)")
            if combatant.death_saves_success >= 3:
                self.log(f"{combatant.name} is stabilized!")
        else:
            # Failure
            combatant.death_saves_failure += 1
            self.log(f"{combatant.name} fails death save ({combatant.death_saves_failure}/3)")
    
    def _check_defeats(self):
        """Check for defeated combatants and handle appropriately"""
        for combatant in self.combatants.values():
            if not combatant.is_alive() and combatant.id in self.turn_order:
                if combatant.type == "monster":
                    self.log(f"{combatant.name} is defeated!")
                    # Monster is simply dead
                    combatant.death_saves_failure = 3
    
    def get_monster_action(self, monster_id: str) -> Dict:
        """
        AI decision making for monsters.
        AI Agents: Extend with new AI behaviors and tactics.
        """
        monster = self.combatants.get(monster_id)
        if not monster or not monster.is_alive():
            return {"action": None}
        
        # Find player target
        player = next((c for c in self.combatants.values() if c.type == "player" and c.is_alive()), None)
        if not player:
            return {"action": None}
        
        # Execute AI script
        ai_script = monster.ai_script or "basic_melee"
        
        if ai_script == "basic_melee":
            # Simple melee attacker
            if monster.position != CombatPosition.MELEE:
                # Move to melee
                return {
                    "action": {"type": "movement", "position": "melee"},
                    "target": None
                }
            else:
                # Attack with first available action
                if monster.actions:
                    return {
                        "action": monster.actions[0],
                        "target": player.id
                    }
        
        elif ai_script == "control_first":
            # Use control abilities first, then damage
            for action in monster.actions:
                if action.get("special") and not action.get("used"):
                    return {
                        "action": action,
                        "target": player.id if action.get("requires_target") else None
                    }
            # Fall back to basic attack
            return self._get_basic_attack(monster, player)
        
        elif ai_script == "control_then_damage":
            # Similar to control_first but more strategic
            # AI Agents: Implement smarter control usage
            pass
        
        # Default: basic attack
        return self._get_basic_attack(monster, player)
    
    def _get_basic_attack(self, monster: Combatant, target: Combatant) -> Dict:
        """Get a basic attack action for a monster"""
        if monster.position != CombatPosition.MELEE:
            return {"action": {"type": "movement", "position": "melee"}, "target": None}
        
        if monster.actions:
            return {"action": monster.actions[0], "target": target.id}
        
        return {"action": None}
    
    def check_combat_end(self) -> Optional[str]:
        """
        Check if combat has ended.
        Returns: "victory", "defeat", or None if ongoing
        """
        players_alive = any(c.is_alive() for c in self.combatants.values() if c.type == "player")
        monsters_alive = any(c.is_alive() for c in self.combatants.values() if c.type == "monster")
        
        if not players_alive:
            self.is_active = False
            return "defeat"
        elif not monsters_alive:
            self.is_active = False
            return "victory"
        
        return None
    
    def get_combat_state(self) -> Dict:
        """Get current combat state for frontend"""
        return {
            "round": self.round_number,
            "current_turn": self.turn_order[self.current_turn] if self.turn_order else None,
            "turn_order": self.turn_order,
            "combatants": {
                id: {
                    "id": c.id,
                    "name": c.name,
                    "type": c.type,
                    "hp": c.current_hp,
                    "max_hp": c.max_hp,
                    "ac": c.ac,
                    "position": c.position.value,
                    "conditions": c.conditions,
                    "has_action": not c.has_taken_action,
                    "has_bonus": not c.has_taken_bonus,
                    "has_reaction": not c.has_taken_reaction,
                    "movement": c.movement_remaining,
                    "is_alive": c.is_alive()
                }
                for id, c in self.combatants.items()
            },
            "log": self.combat_log[-10:],  # Last 10 log entries
            "is_active": self.is_active,
            "outcome": self.check_combat_end()
        }
    
    def log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)
        logger.info(f"[Combat] {message}")

# Singleton instance for the game
combat_engine = CombatEngine()

__all__ = ['CombatEngine', 'Combatant', 'ActionType', 'CombatPosition', 'combat_engine']