"""
File: services/combat.py
Path: /services/combat.py

Turn-based combat system for D&D Desktop 2024.
Handles initiative, turn order, attacks, damage, and combat resolution.

Pseudo Code:
1. Initialize combat with characters and monsters
2. Roll initiative and establish turn order
3. Process each combatant's turn in initiative order
4. Handle attack rolls, damage calculation, and HP tracking
5. Check win/loss conditions after each action
6. Progress through rounds until combat ends

AI Agents: Core combat mechanics with D&D 2024 rules.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from services.dice import dice, attack_roll
from models.character import Character
from models.monsters import Monster
from models.items import Item
from core.database import DatabaseSession


class CombatState(str, Enum):
    """Combat session states."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    PLAYER_VICTORY = "player_victory"
    PLAYER_DEFEAT = "player_defeat"
    FLED = "fled"


@dataclass
class Combatant:
    """Represents a combatant in combat."""
    id: str
    name: str
    type: str  # "character" or "monster"
    entity: Union[Character, Monster]
    initiative: int = 0
    current_hp: int = 0
    max_hp: int = 0
    armor_class: int = 10
    is_alive: bool = True
    
    def __post_init__(self):
        """Initialize HP and AC from entity."""
        if self.type == "character":
            self.current_hp = self.entity.current_hit_points
            self.max_hp = self.entity.max_hit_points
            self.armor_class = self.entity.armor_class
        elif self.type == "monster":
            self.current_hp = self.entity.hit_points or 1
            self.max_hp = self.entity.hit_points or 1
            self.armor_class = self.entity.armor_class or 10
    
    @property
    def dexterity_modifier(self) -> int:
        """Get dexterity modifier for initiative."""
        return self.entity.dexterity_modifier
    
    def take_damage(self, damage: int) -> int:
        """Apply damage and return actual damage taken."""
        actual_damage = min(damage, self.current_hp)
        self.current_hp = max(0, self.current_hp - damage)
        self.is_alive = self.current_hp > 0
        
        logger.info(f"{self.name} takes {actual_damage} damage ({self.current_hp}/{self.max_hp} HP remaining)")
        
        if not self.is_alive:
            logger.info(f"{self.name} has been defeated!")
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal damage and return actual healing."""
        actual_healing = min(amount, self.max_hp - self.current_hp)
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        
        logger.info(f"{self.name} heals {actual_healing} HP ({self.current_hp}/{self.max_hp} HP)")
        return actual_healing


@dataclass 
class AttackResult:
    """Result of an attack action."""
    attacker_name: str
    target_name: str
    attack_roll: int
    target_ac: int
    hit: bool
    critical: bool
    fumble: bool
    damage: int = 0
    damage_type: str = "unknown"
    # New fields for detailed logging
    attack_dice_roll: int = 0  # The d20 roll without modifiers
    attack_bonus: int = 0  # The total attack bonus
    damage_dice_notation: str = ""  # e.g., "1d8+3"
    damage_dice_roll: int = 0  # The dice roll without modifiers
    damage_bonus: int = 0  # The damage bonus/modifier
    weapon_name: str = ""  # Name of weapon used
    
    def __str__(self) -> str:
        attack_notation = f"1d20+{self.attack_bonus}" if self.attack_bonus >= 0 else f"1d20{self.attack_bonus}"
        
        if self.fumble:
            return f"{self.attacker_name} attacks with {self.weapon_name}: {attack_notation} -> ({self.attack_dice_roll}+{self.attack_bonus}) = {self.attack_roll} - CRITICAL MISS!"
        elif not self.hit:
            return f"{self.attacker_name} attacks {self.target_name} with {self.weapon_name}: {attack_notation} -> ({self.attack_dice_roll}+{self.attack_bonus}) = {self.attack_roll} vs AC {self.target_ac} - MISS"
        elif self.critical:
            if self.damage_bonus > 0:
                return f"{self.attacker_name} attacks {self.target_name} with {self.weapon_name}: {attack_notation} -> ({self.attack_dice_roll}+{self.attack_bonus}) = {self.attack_roll} - CRITICAL HIT! {self.damage_dice_notation} -> ({self.damage_dice_roll}+{self.damage_bonus}) = {self.damage} {self.damage_type} damage"
            else:
                return f"{self.attacker_name} attacks {self.target_name} with {self.weapon_name}: {attack_notation} -> ({self.attack_dice_roll}+{self.attack_bonus}) = {self.attack_roll} - CRITICAL HIT! {self.damage_dice_notation} -> {self.damage_dice_roll} = {self.damage} {self.damage_type} damage"
        else:
            if self.damage_bonus > 0:
                return f"{self.attacker_name} attacks {self.target_name} with {self.weapon_name}: {attack_notation} -> ({self.attack_dice_roll}+{self.attack_bonus}) = {self.attack_roll} vs AC {self.target_ac} - HIT! {self.damage_dice_notation} -> ({self.damage_dice_roll}+{self.damage_bonus}) = {self.damage} {self.damage_type} damage"
            else:
                return f"{self.attacker_name} attacks {self.target_name} with {self.weapon_name}: {attack_notation} -> ({self.attack_dice_roll}+{self.attack_bonus}) = {self.attack_roll} vs AC {self.target_ac} - HIT! {self.damage_dice_notation} -> {self.damage_dice_roll} = {self.damage} {self.damage_type} damage"


class CombatService:
    """
    Manages turn-based D&D combat encounters.
    
    AI Agents: Extend with spell casting, special abilities, and environmental effects.
    """
    
    def __init__(self):
        self.combatants: List[Combatant] = []
        self.turn_order: List[str] = []  # Combatant IDs in initiative order
        self.current_round: int = 1
        self.current_turn: int = 0
        self.state: CombatState = CombatState.NOT_STARTED
        self.combat_log: List[str] = []
        
    def initialize_combat(self, characters: List[Character], monsters: List[Monster]) -> None:
        """
        Initialize a new combat encounter.
        
        Args:
            characters: List of player characters
            monsters: List of enemy monsters
        """
        logger.info("Initializing combat encounter")
        
        self.combatants.clear()
        self.combat_log.clear()
        self.current_round = 1
        self.current_turn = 0
        self.state = CombatState.NOT_STARTED
        
        # Add characters
        for char in characters:
            combatant = Combatant(
                id=str(char.id),
                name=char.name,
                type="character", 
                entity=char
            )
            self.combatants.append(combatant)
            logger.debug(f"Added character: {char.name} (HP: {combatant.current_hp}/{combatant.max_hp}, AC: {combatant.armor_class})")
        
        # Add monsters
        for i, monster in enumerate(monsters):
            combatant = Combatant(
                id=f"monster_{i}",
                name=f"{monster.name} {i+1}" if len(monsters) > 1 else monster.name,
                type="monster",
                entity=monster
            )
            self.combatants.append(combatant)
            logger.debug(f"Added monster: {combatant.name} (HP: {combatant.current_hp}/{combatant.max_hp}, AC: {combatant.armor_class})")
        
        self._roll_initiative()
        self.state = CombatState.IN_PROGRESS
        self._log_action(f"Combat begins! Round {self.current_round}")
        self._log_action(f"Turn order: {', '.join(combatant.name for combatant in self._get_turn_order())}")
    
    def _roll_initiative(self) -> None:
        """Roll initiative for all combatants and establish turn order."""
        logger.info("Rolling initiative...")
        
        initiative_results = []
        
        for combatant in self.combatants:
            # Roll initiative (1d20 + Dex modifier)
            initiative_roll = dice.roll_initiative(combatant.dexterity_modifier)
            combatant.initiative = initiative_roll
            initiative_results.append((combatant.id, combatant.name, initiative_roll))
            
            logger.debug(f"{combatant.name} rolled {initiative_roll} for initiative")
        
        # Sort by initiative (highest first), use dex modifier as tiebreaker
        initiative_results.sort(key=lambda x: (x[2], self._get_combatant_by_id(x[0]).dexterity_modifier), reverse=True)
        
        # Set turn order
        self.turn_order = [result[0] for result in initiative_results]
        
        # Log initiative results
        for _, name, init_roll in initiative_results:
            self._log_action(f"{name}: {init_roll} initiative")
    
    def get_current_combatant(self) -> Optional[Combatant]:
        """Get the combatant whose turn it is."""
        if not self.turn_order or self.current_turn >= len(self.turn_order):
            return None
        
        combatant_id = self.turn_order[self.current_turn]
        return self._get_combatant_by_id(combatant_id)
    
    def _get_combatant_by_id(self, combatant_id: str) -> Optional[Combatant]:
        """Get a combatant by their ID."""
        for combatant in self.combatants:
            if combatant.id == combatant_id:
                return combatant
        return None
    
    def _get_turn_order(self) -> List[Combatant]:
        """Get all combatants in turn order."""
        return [self._get_combatant_by_id(cid) for cid in self.turn_order if self._get_combatant_by_id(cid)]
    
    def attack(self, attacker_id: str, target_id: str, weapon_info: Optional[Dict[str, Any]] = None) -> AttackResult:
        """
        Perform an attack action.
        
        Args:
            attacker_id: ID of attacking combatant
            target_id: ID of target combatant
            
        Returns:
            AttackResult with details of the attack
        """
        attacker = self._get_combatant_by_id(attacker_id)
        target = self._get_combatant_by_id(target_id)
        
        if not attacker or not target:
            raise ValueError("Invalid attacker or target ID")
        
        if not attacker.is_alive:
            raise ValueError(f"{attacker.name} cannot attack - defeated")
        
        if not target.is_alive:
            raise ValueError(f"Cannot target {target.name} - already defeated")
        
        # Get attack bonus and weapon info
        if weapon_info:
            # Use provided weapon info (from player choice)
            attack_bonus = weapon_info.get("attack_bonus", 0)
            weapon_damage = weapon_info.get("damage_dice", "1d4")
            damage_type = weapon_info.get("damage_type", "bludgeoning")
            weapon_name = weapon_info.get("name", "Unknown Weapon")
        else:
            # Use default weapon for monsters or fallback
            attack_bonus = self._get_attack_bonus(attacker)
            weapon_damage, damage_type = self._get_weapon_damage(attacker)
            weapon_name = self._get_weapon_name(attacker)
        
        # Make attack roll and capture detailed results
        import random
        attack_dice_roll = random.randint(1, 20)
        attack_total = attack_dice_roll + attack_bonus
        is_critical = attack_dice_roll == 20
        is_fumble = attack_dice_roll == 1
        
        # Check if attack hits
        hits = is_critical or (not is_fumble and attack_total >= target.armor_class)
        
        # Calculate damage with detailed tracking
        damage_dealt = 0
        damage_dice_roll = 0
        damage_bonus = 0
        damage_dice_notation = weapon_damage
        
        if hits and not is_fumble:
            # Parse damage dice to separate dice and bonus
            import re
            dice_match = re.match(r'(\d+d\d+)([+-]\d+)?', weapon_damage)
            if dice_match:
                base_dice = dice_match.group(1)
                bonus_str = dice_match.group(2) or ""
                damage_bonus = int(bonus_str) if bonus_str else 0
                
                # Double dice on critical hit
                if is_critical:
                    num_dice, die_size = base_dice.split('d')
                    doubled_dice = f"{int(num_dice)*2}d{die_size}"
                    damage_dice_notation = doubled_dice + (bonus_str if bonus_str else "")
                    damage_dice_roll = dice.roll(doubled_dice)
                else:
                    damage_dice_roll = dice.roll(base_dice)
                
                damage_dealt = damage_dice_roll + damage_bonus
            else:
                # Handle simple numeric damage (like "1")
                if weapon_damage.isdigit():
                    damage_dealt = int(weapon_damage)
                    damage_dice_roll = damage_dealt
                    damage_dice_notation = weapon_damage
                else:
                    damage_dealt = dice.roll(weapon_damage)
                    damage_dice_roll = damage_dealt
                    damage_dice_notation = weapon_damage
            
            # Apply damage to target
            actual_damage = target.take_damage(damage_dealt)
            damage_dealt = actual_damage
        
        # Create result with detailed information
        result = AttackResult(
            attacker_name=attacker.name,
            target_name=target.name,
            attack_roll=attack_total,
            target_ac=target.armor_class,
            hit=hits,
            critical=is_critical,
            fumble=is_fumble,
            damage=damage_dealt,
            damage_type=damage_type,
            attack_dice_roll=attack_dice_roll,
            attack_bonus=attack_bonus,
            damage_dice_notation=damage_dice_notation,
            damage_dice_roll=damage_dice_roll,
            damage_bonus=damage_bonus,
            weapon_name=weapon_name
        )
        
        # Log the action
        self._log_action(str(result))
        
        # Check for combat end
        self._check_combat_end()
        
        return result
    
    def _get_attack_bonus(self, combatant: Combatant) -> int:
        """Calculate attack bonus for a combatant."""
        if combatant.type == "character":
            # For characters, use proficiency bonus + ability modifier
            entity = combatant.entity
            return entity.proficiency_bonus + entity.strength_modifier  # Simplified - assume strength weapons
        elif combatant.type == "monster":
            # For monsters, use proficiency bonus + ability modifier  
            entity = combatant.entity
            return entity.proficiency_bonus + entity.strength_modifier
        return 0
    
    def _get_weapon_damage(self, combatant: Combatant) -> Tuple[str, str]:
        """Get weapon damage dice and type for a combatant."""
        if combatant.type == "character":
            # Check equipped weapon, default to unarmed
            # TODO: Get from equipped weapon in character.equipment_main_hand
            return "1d4", "bludgeoning"  # Unarmed strike
        elif combatant.type == "monster":
            # Get first attack from monster actions
            entity = combatant.entity
            if entity.actions and isinstance(entity.actions, list) and len(entity.actions) > 0:
                first_action = entity.actions[0]
                if isinstance(first_action, dict):
                    damage_dice = first_action.get("damage_dice", "1d6")
                    damage_type = first_action.get("damage_type", "bludgeoning")
                    return damage_dice, damage_type
            return "1d6", "bludgeoning"  # Default monster attack
        
        return "1", "bludgeoning"  # Fallback
    
    def _get_weapon_name(self, combatant: Combatant) -> str:
        """Get weapon name for a combatant."""
        if combatant.type == "character":
            # TODO: Get from equipped weapon in character.equipment_main_hand
            return "Unarmed Strike"
        elif combatant.type == "monster":
            # Get first attack from monster actions
            entity = combatant.entity
            if entity.actions and isinstance(entity.actions, list) and len(entity.actions) > 0:
                first_action = entity.actions[0]
                if isinstance(first_action, dict):
                    return first_action.get("name", "Natural Weapon")
            return "Natural Weapon"
        
        return "Unknown Weapon"
    
    def next_turn(self) -> Optional[Combatant]:
        """
        Advance to the next combatant's turn.
        
        Returns:
            Next combatant, or None if combat is over
        """
        if self.state != CombatState.IN_PROGRESS:
            return None
        
        # Skip defeated combatants
        while True:
            self.current_turn = (self.current_turn + 1) % len(self.turn_order)
            
            # Check if we've completed a round
            if self.current_turn == 0:
                self.current_round += 1
                self._log_action(f"--- Round {self.current_round} ---")
            
            current = self.get_current_combatant()
            if not current:
                break
                
            if current.is_alive:
                self._log_action(f"{current.name}'s turn")
                return current
            
            # Remove defeated combatants from turn order
            if not current.is_alive:
                self.turn_order.remove(current.id)
                if self.current_turn >= len(self.turn_order):
                    self.current_turn = 0
                
                # Check if combat ended due to no more combatants
                if self._check_combat_end():
                    return None
        
        return None
    
    def _check_combat_end(self) -> bool:
        """
        Check if combat should end and update state.
        
        Returns:
            True if combat ended, False if continuing
        """
        alive_characters = [c for c in self.combatants if c.type == "character" and c.is_alive]
        alive_monsters = [c for c in self.combatants if c.type == "monster" and c.is_alive]
        
        if not alive_characters:
            self.state = CombatState.PLAYER_DEFEAT
            self._log_action("All player characters have been defeated! GAME OVER")
            return True
        elif not alive_monsters:
            self.state = CombatState.PLAYER_VICTORY
            self._log_action("All monsters defeated! Victory!")
            return True
        
        return False
    
    def get_combat_summary(self) -> Dict[str, Any]:
        """Get current combat state summary."""
        return {
            "state": self.state.value,
            "round": self.current_round,
            "current_turn": self.current_turn,
            "current_combatant": self.get_current_combatant().name if self.get_current_combatant() else None,
            "combatants": [
                {
                    "id": c.id,
                    "name": c.name,
                    "type": c.type,
                    "hp": f"{c.current_hp}/{c.max_hp}",
                    "ac": c.armor_class,
                    "initiative": c.initiative,
                    "alive": c.is_alive
                }
                for c in self.combatants
            ],
            "turn_order": [self._get_combatant_by_id(cid).name for cid in self.turn_order if self._get_combatant_by_id(cid)],
            "log": self.combat_log[-10:]  # Last 10 log entries
        }
    
    def _log_action(self, message: str) -> None:
        """Add an action to the combat log."""
        log_entry = f"[Round {self.current_round}] {message}"
        self.combat_log.append(log_entry)
        logger.info(log_entry)
    
    def get_alive_enemies(self, combatant_type: str) -> List[Combatant]:
        """Get all alive enemies of the specified combatant type."""
        enemy_type = "monster" if combatant_type == "character" else "character"
        return [c for c in self.combatants if c.type == enemy_type and c.is_alive]
    
    def get_alive_allies(self, combatant_type: str) -> List[Combatant]:
        """Get all alive allies of the specified combatant type."""
        return [c for c in self.combatants if c.type == combatant_type and c.is_alive]
    
    def is_player_turn(self) -> bool:
        """Check if it's currently a player character's turn."""
        current = self.get_current_combatant()
        return current and current.type == "character"
    
    def get_available_weapons(self, character_id: str) -> List[Dict[str, Any]]:
        """
        Get available weapons for a character from the database.
        
        Args:
            character_id: ID of the character
            
        Returns:
            List of weapon dictionaries with attack info
        """
        combatant = self._get_combatant_by_id(character_id)
        if not combatant or combatant.type != "character":
            return []

        entity = combatant.entity
        weapons = [
            {
                "name": "Unarmed Strike",
                "attack_bonus": entity.proficiency_bonus + entity.strength_modifier,
                "damage_dice": "1",
                "damage_type": "bludgeoning",
                "description": "Basic unarmed attack"
            }
        ]

        with DatabaseSession() as db:
            # Main hand weapon
            if entity.equipment_main_hand:
                item = db.query(Item).filter_by(id=entity.equipment_main_hand).first()
                if item and item.item_type == 'weapon':
                    # TODO: Handle finesse weapons (dex vs str)
                    attack_bonus = entity.proficiency_bonus + entity.strength_modifier

                    weapons.append({
                        "name": item.name,
                        "attack_bonus": attack_bonus,
                        "damage_dice": f"{item.damage_dice}+{entity.strength_modifier}",
                        "damage_type": item.damage_type,
                        "description": item.description or ""
                    })

                    # Add versatile option
                    if item.weapon_properties and "versatile" in item.weapon_properties:
                         weapons.append({
                            "name": f"{item.name} (Two-Handed)",
                            "attack_bonus": attack_bonus,
                            "damage_dice": f"1d10+{entity.strength_modifier}", # Example for versatile
                            "damage_type": item.damage_type,
                            "description": f"{item.description} (Versatile)"
                        })

        return weapons


# Global combat service instance
combat_service = CombatService()