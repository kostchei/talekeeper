"""
D&D 2024 Compliant Combat Manager

Handles initiative, turn order, action economy, and combat resolution
according to official D&D 2024 rules from the SRD.
"""

import random
import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class ActionType(Enum):
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    FREE_ACTION = "free_action"
    LEGENDARY_ACTION = "legendary_action"

class CombatantType(Enum):
    PLAYER = "player"
    MONSTER = "monster"

@dataclass
class CombatAction:
    """Represents a single combat action (attack, spell, etc.)"""
    name: str
    action_type: ActionType
    description: str
    attack_bonus: Optional[int] = None
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    target_required: bool = True
    range_feet: Optional[int] = None

@dataclass
class Combatant:
    """Represents a participant in combat"""
    id: str
    name: str
    type: CombatantType
    
    # Core stats
    armor_class: int
    hit_points: int
    max_hit_points: int
    
    # Initiative
    initiative_bonus: int
    initiative_roll: Optional[int] = None
    
    # Status
    is_alive: bool = True
    conditions: List[str] = field(default_factory=list)
    
    # Actions
    has_taken_action: bool = False
    has_taken_bonus_action: bool = False
    reactions_used: int = 0
    
    # For monsters
    actions: List[CombatAction] = field(default_factory=list)
    multiattack_actions: Optional[List[str]] = None
    
    # For players
    class_name: Optional[str] = None
    level: Optional[int] = None
    extra_attacks: int = 0

@dataclass 
class CombatRound:
    """Represents one round of combat"""
    number: int
    initiative_order: List[Combatant]
    current_turn_index: int = 0
    completed: bool = False

class CombatManager:
    """
    Manages D&D 2024 compliant combat including:
    - Initiative rolling and turn order
    - Action economy (Action, Bonus Action, Reaction)
    - Extra Attack and Multiattack features
    - Combat end conditions
    - Dead creature validation
    """
    
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.combatants: Dict[str, Combatant] = {}
        self.current_round: Optional[CombatRound] = None
        self.combat_active: bool = False
        self.combat_log: List[str] = []
        
    def add_player_combatant(self, character_data: Dict[str, Any]) -> Combatant:
        """Add player character to combat"""
        character_id = character_data['id']
        
        # Calculate initiative bonus (DEX modifier)
        dex_score = character_data.get('dexterity', 10)
        initiative_bonus = (dex_score - 10) // 2
        
        # Get Extra Attack count based on class and level
        extra_attacks = self._get_extra_attack_count(
            character_data.get('class_id', ''),
            character_data.get('level', 1)
        )
        
        combatant = Combatant(
            id=character_id,
            name=character_data.get('name', 'Player'),
            type=CombatantType.PLAYER,
            armor_class=character_data.get('ac', 10),
            hit_points=character_data.get('hp', 1),
            max_hit_points=character_data.get('max_hp', 1),
            initiative_bonus=initiative_bonus,
            class_name=character_data.get('class_id'),
            level=character_data.get('level', 1),
            extra_attacks=extra_attacks
        )
        
        self.combatants[character_id] = combatant
        return combatant
    
    def add_monster_combatant(self, monster_id: str, monster_data: Dict[str, Any]) -> Combatant:
        """Add monster to combat"""
        
        # Calculate initiative bonus (DEX modifier)
        dex_score = monster_data.get('dexterity', 10)
        initiative_bonus = (dex_score - 10) // 2
        
        # Parse actions from database format
        actions = self._parse_monster_actions(monster_data.get('actions', '[]'))
        multiattack_actions = self._parse_multiattack(actions)
        
        combatant = Combatant(
            id=monster_id,
            name=monster_data.get('name', 'Monster'),
            type=CombatantType.MONSTER,
            armor_class=monster_data.get('armor_class', 10),
            hit_points=monster_data.get('hit_points', 1),
            max_hit_points=monster_data.get('hit_points', 1),
            initiative_bonus=initiative_bonus,
            actions=actions,
            multiattack_actions=multiattack_actions
        )
        
        self.combatants[monster_id] = combatant
        return combatant
    
    def start_combat(self) -> List[Combatant]:
        """
        Start combat by rolling initiative for all combatants.
        Returns initiative order (highest to lowest).
        """
        if not self.combatants:
            raise ValueError("No combatants added to combat")
        
        self.log("[COMBAT] ==================================================")
        self.log("[COMBAT] [DICE] ROLLING INITIATIVE FOR COMBAT!")
        self.log("[COMBAT] ==================================================")
        
        # Roll initiative for all combatants
        for combatant in self.combatants.values():
            if combatant.is_alive:
                roll = random.randint(1, 20)
                combatant.initiative_roll = roll + combatant.initiative_bonus
                self.log(f"[COMBAT] {combatant.name} Initiative: d20({roll}) + {combatant.initiative_bonus} = {combatant.initiative_roll}")
        
        # Sort by initiative (highest first, with ties resolved randomly)
        initiative_order = []
        for combatant in self.combatants.values():
            if combatant.is_alive and combatant.initiative_roll is not None:
                initiative_order.append(combatant)
        
        # Sort by initiative, randomize ties
        initiative_order.sort(key=lambda c: (c.initiative_roll, random.random()), reverse=True)
        
        # Create first round
        self.current_round = CombatRound(number=1, initiative_order=initiative_order)
        self.combat_active = True
        
        self.log("[COMBAT] Initiative Order:")
        for i, combatant in enumerate(initiative_order):
            self.log(f"[COMBAT]   {i+1}. {combatant.name} ({combatant.initiative_roll})")
        
        return initiative_order
    
    def get_current_combatant(self) -> Optional[Combatant]:
        """Get the combatant whose turn it is"""
        if not self.current_round or self.current_round.completed:
            return None
        
        if self.current_round.current_turn_index >= len(self.current_round.initiative_order):
            return None
            
        return self.current_round.initiative_order[self.current_round.current_turn_index]
    
    def is_player_turn(self) -> bool:
        """Check if it's currently the player's turn"""
        current = self.get_current_combatant()
        return current is not None and current.type == CombatantType.PLAYER
    
    def execute_player_attack(self, character_id: str, weapon_data: Dict[str, Any], 
                            target_id: str) -> Dict[str, Any]:
        """
        Execute player attack with proper Extra Attack support.
        Returns attack results for logging.
        """
        if not self.is_player_turn():
            return {'error': 'Not player turn'}
        
        combatant = self.combatants.get(character_id)
        target = self.combatants.get(target_id)
        
        if not combatant or not target:
            return {'error': 'Invalid combatant or target'}
        
        if not target.is_alive:
            return {'error': 'Cannot target dead creature'}
        
        if combatant.has_taken_action:
            return {'error': 'Already took action this turn'}
        
        # Mark action as taken
        combatant.has_taken_action = True
        
        # Calculate number of attacks (1 + Extra Attack)
        num_attacks = 1 + combatant.extra_attacks
        
        results = {
            'attacks': [],
            'total_damage': 0,
            'targets_hit': [],
            'targets_killed': []
        }
        
        self.log(f"[COMBAT] {combatant.name} Attack Action: Making {num_attacks} attack(s) with {weapon_data.get('name', 'weapon')}")
        
        for attack_num in range(num_attacks):
            if not target.is_alive:
                self.log(f"[COMBAT] [ATTACK {attack_num + 1}/{num_attacks}] Target {target.name} already defeated")
                break
            
            attack_result = self._execute_single_attack(combatant, target, weapon_data, attack_num + 1, num_attacks)
            results['attacks'].append(attack_result)
            
            if attack_result.get('hit'):
                results['total_damage'] += attack_result.get('damage', 0)
                if target_id not in results['targets_hit']:
                    results['targets_hit'].append(target_id)
                
                if not target.is_alive:
                    results['targets_killed'].append(target_id)
                    self.log(f"[COMBAT] {target.name} has been defeated!")
                    
                    # Award XP
                    xp = self._calculate_xp_reward(target_id)
                    if xp > 0:
                        results['xp_gained'] = xp
                        self.log(f"[XP] Gained {xp} XP for defeating {target.name}")
        
        return results
    
    def execute_monster_turn(self, monster_id: str) -> Dict[str, Any]:
        """
        Execute monster's turn with proper Multiattack support.
        Returns turn results for logging.
        """
        if self.is_player_turn():
            return {'error': 'Not monster turn'}
        
        combatant = self.combatants.get(monster_id)
        if not combatant or not combatant.is_alive:
            return {'error': 'Invalid or dead monster'}
        
        if combatant.has_taken_action:
            return {'error': 'Monster already took action this turn'}
        
        # Mark action as taken
        combatant.has_taken_action = True
        
        results = {
            'attacks': [],
            'total_damage': 0,
            'targets_hit': []
        }
        
        # Find player target (for simplicity, target first living player)
        player_target = None
        for c in self.combatants.values():
            if c.type == CombatantType.PLAYER and c.is_alive:
                player_target = c
                break
        
        if not player_target:
            self.log(f"[COMBAT] {combatant.name} has no valid targets")
            return results
        
        # Use Multiattack if available, otherwise single attack
        if combatant.multiattack_actions:
            self.log(f"[COMBAT] {combatant.name} uses Multiattack")
            for action_name in combatant.multiattack_actions:
                action = self._find_monster_action(combatant, action_name)
                if action:
                    attack_result = self._execute_monster_attack(combatant, player_target, action)
                    results['attacks'].append(attack_result)
                    
                    if attack_result.get('hit'):
                        results['total_damage'] += attack_result.get('damage', 0)
                        if player_target.id not in results['targets_hit']:
                            results['targets_hit'].append(player_target.id)
        else:
            # Single attack with first available action
            if combatant.actions:
                action = combatant.actions[0]
                attack_result = self._execute_monster_attack(combatant, player_target, action)
                results['attacks'].append(attack_result)
                
                if attack_result.get('hit'):
                    results['total_damage'] += attack_result.get('damage', 0)
                    results['targets_hit'].append(player_target.id)
        
        return results
    
    def advance_turn(self) -> Optional[Combatant]:
        """
        Advance to the next combatant's turn.
        Returns the new current combatant, or None if round ended.
        """
        if not self.current_round:
            return None
        
        # Reset current combatant's action economy for next round
        current = self.get_current_combatant()
        if current:
            current.has_taken_action = False
            current.has_taken_bonus_action = False
            current.reactions_used = 0
        
        # Advance to next turn
        self.current_round.current_turn_index += 1
        
        # Check if round is complete
        if self.current_round.current_turn_index >= len(self.current_round.initiative_order):
            # Start new round
            self._start_new_round()
        
        next_combatant = self.get_current_combatant()
        
        if next_combatant:
            self.log(f"[COMBAT] [LIGHTNING] {next_combatant.name}'s turn!")
        
        return next_combatant
    
    def is_combat_ended(self) -> bool:
        """Check if combat should end (one side defeated)"""
        living_players = sum(1 for c in self.combatants.values() 
                           if c.type == CombatantType.PLAYER and c.is_alive)
        living_monsters = sum(1 for c in self.combatants.values() 
                            if c.type == CombatantType.MONSTER and c.is_alive)
        
        return living_players == 0 or living_monsters == 0
    
    def end_combat(self) -> Dict[str, Any]:
        """End combat and return summary"""
        self.combat_active = False
        
        living_players = [c for c in self.combatants.values() 
                         if c.type == CombatantType.PLAYER and c.is_alive]
        living_monsters = [c for c in self.combatants.values() 
                          if c.type == CombatantType.MONSTER and c.is_alive]
        
        if living_players and not living_monsters:
            self.log("[COMBAT] Combat victory! All enemies defeated.")
            result = "victory"
        elif living_monsters and not living_players:
            self.log("[COMBAT] Combat defeat! Player character defeated.")
            result = "defeat"
        else:
            self.log("[COMBAT] Combat ended in a draw.")
            result = "draw"
        
        return {
            'result': result,
            'rounds': self.current_round.number if self.current_round else 0,
            'living_players': len(living_players),
            'living_monsters': len(living_monsters)
        }
    
    def log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)
        print(message)  # Also print for debugging
    
    def get_combat_log(self) -> List[str]:
        """Get all combat log messages"""
        return self.combat_log.copy()
    
    # === PRIVATE METHODS ===
    
    def _get_extra_attack_count(self, class_name: str, level: int) -> int:
        """Get number of extra attacks based on D&D 2024 rules"""
        class_name = class_name.lower()
        
        if class_name == 'fighter':
            if level >= 20:
                return 3  # 4 total attacks
            elif level >= 11:
                return 2  # 3 total attacks  
            elif level >= 5:
                return 1  # 2 total attacks
            else:
                return 0  # 1 total attack
        
        elif class_name in ['barbarian', 'paladin', 'ranger', 'monk']:
            if level >= 5:
                return 1  # 2 total attacks
            else:
                return 0  # 1 total attack
        
        else:
            return 0  # 1 total attack
    
    def _parse_monster_actions(self, actions_json: str) -> List[CombatAction]:
        """Parse monster actions from database JSON format"""
        try:
            actions_data = json.loads(actions_json) if isinstance(actions_json, str) else actions_json
            actions = []
            
            for action_data in actions_data:
                name = action_data.get('name', 'Unknown')
                entries = action_data.get('entries', [])
                
                # Skip Multiattack for now (handled separately)
                if name.lower() == 'multiattack':
                    continue
                
                # Parse attack information from entries
                attack_bonus = None
                damage_dice = None
                damage_type = None
                
                if entries:
                    entry_text = entries[0] if entries else ""
                    
                    # Extract attack bonus (e.g., {@hit 5})
                    import re
                    hit_match = re.search(r'\{@hit (\d+)\}', entry_text)
                    if hit_match:
                        attack_bonus = int(hit_match.group(1))
                    
                    # Extract damage (e.g., {@damage 1d8 + 3})
                    damage_match = re.search(r'\{@damage ([^}]+)\}', entry_text)
                    if damage_match:
                        damage_info = damage_match.group(1)
                        # Extract dice and type
                        dice_match = re.search(r'(\d+d\d+(?:\s*[+\-]\s*\d+)?)', damage_info)
                        if dice_match:
                            damage_dice = dice_match.group(1).replace(' ', '')
                        
                        # Extract damage type
                        type_words = ['piercing', 'slashing', 'bludgeoning', 'fire', 'cold', 'lightning', 'thunder', 'acid', 'poison', 'necrotic', 'radiant', 'psychic', 'force']
                        for word in type_words:
                            if word in entry_text.lower():
                                damage_type = word
                                break
                
                action = CombatAction(
                    name=name,
                    action_type=ActionType.ACTION,
                    description=entry_text,
                    attack_bonus=attack_bonus,
                    damage_dice=damage_dice,
                    damage_type=damage_type
                )
                actions.append(action)
            
            return actions
            
        except (json.JSONDecodeError, TypeError):
            return []
    
    def _parse_multiattack(self, actions: List[CombatAction]) -> Optional[List[str]]:
        """Parse Multiattack from monster data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # This would need the monster ID, but for now return None
            # In a full implementation, we'd parse the multiattack description
            return None
            
        except Exception:
            return None
        finally:
            if conn:
                conn.close()
    
    def _execute_single_attack(self, attacker: Combatant, target: Combatant, 
                             weapon_data: Dict[str, Any], attack_num: int, total_attacks: int) -> Dict[str, Any]:
        """Execute a single attack roll and damage"""
        
        # Attack roll
        d20_roll = random.randint(1, 20)
        attack_bonus = weapon_data.get('attack_bonus', 0)
        total_attack = d20_roll + attack_bonus
        
        self.log(f"[COMBAT] [ATTACK {attack_num}/{total_attacks}] {target.name}")
        
        # Check for hit
        hit = total_attack >= target.armor_class
        
        if hit:
            # Damage roll
            damage_dice = weapon_data.get('damage_dice', '1d6')
            damage = self._roll_damage(damage_dice)
            damage_bonus = weapon_data.get('damage_bonus', 0)
            total_damage = damage + damage_bonus
            
            # Apply damage
            target.hit_points -= total_damage
            if target.hit_points <= 0:
                target.hit_points = 0
                target.is_alive = False
            
            self.log(f"[COMBAT] [ATTACK] {weapon_data.get('name', 'Weapon')} hits {target.name}! Attack: d20({d20_roll}) + {attack_bonus} = {total_attack} vs AC {target.armor_class}")
            self.log(f"[COMBAT] [DAMAGE] Damage: {damage_dice} = {damage} + {damage_bonus} = {total_damage} damage")
            self.log(f"[COMBAT] {target.name} takes {total_damage} damage! ({target.hit_points}/{target.max_hit_points} HP)")
            
            return {
                'hit': True,
                'attack_roll': total_attack,
                'damage': total_damage,
                'target_hp': target.hit_points
            }
        else:
            self.log(f"[COMBAT] [ATTACK] {weapon_data.get('name', 'Weapon')} misses {target.name}! Attack: d20({d20_roll}) + {attack_bonus} = {total_attack} vs AC {target.armor_class}")
            
            return {
                'hit': False,
                'attack_roll': total_attack,
                'damage': 0,
                'target_hp': target.hit_points
            }
    
    def _execute_monster_attack(self, attacker: Combatant, target: Combatant, 
                               action: CombatAction) -> Dict[str, Any]:
        """Execute a monster attack"""
        
        # Attack roll  
        d20_roll = random.randint(1, 20)
        attack_bonus = action.attack_bonus or 0
        total_attack = d20_roll + attack_bonus
        
        # Check for hit
        hit = total_attack >= target.armor_class
        
        if hit:
            # Damage roll
            damage = self._roll_damage(action.damage_dice or '1d6')
            
            # Apply damage
            target.hit_points -= damage
            if target.hit_points <= 0:
                target.hit_points = 0
                target.is_alive = False
            
            self.log(f"[COMBAT] [HIT] {attacker.name} {action.name} hits! Attack: {d20_roll} + {attack_bonus} = {total_attack} vs AC {target.armor_class} for {damage} damage")
            
            return {
                'hit': True,
                'attack_roll': total_attack, 
                'damage': damage,
                'target_hp': target.hit_points
            }
        else:
            self.log(f"[COMBAT] [MISS] {attacker.name} {action.name} misses! Attack: {d20_roll} + {attack_bonus} = {total_attack} vs AC {target.armor_class}")
            
            return {
                'hit': False,
                'attack_roll': total_attack,
                'damage': 0,
                'target_hp': target.hit_points
            }
    
    def _roll_damage(self, damage_dice: str) -> int:
        """Roll damage dice (e.g., '1d8+3')"""
        if not damage_dice or 'd' not in damage_dice:
            return 1
        
        try:
            # Parse damage dice (e.g., "1d8+3" or "2d6")
            parts = damage_dice.replace('-', '+-').split('+')
            total = 0
            
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                
                if 'd' in part:
                    # Dice roll (e.g., "1d8" or "2d6")
                    num_dice, die_size = part.split('d')
                    num_dice = int(num_dice)
                    die_size = int(die_size)
                    
                    for _ in range(num_dice):
                        total += random.randint(1, die_size)
                else:
                    # Flat modifier (e.g., "+3" or "-1")
                    total += int(part)
            
            return max(0, total)
            
        except (ValueError, IndexError):
            return 1
    
    def _find_monster_action(self, monster: Combatant, action_name: str) -> Optional[CombatAction]:
        """Find monster action by name"""
        for action in monster.actions:
            if action.name.lower() == action_name.lower():
                return action
        return None
    
    def _calculate_xp_reward(self, monster_id: str) -> int:
        """Calculate XP reward for defeating monster"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT experience_points FROM monsters WHERE id = ?", (monster_id,))
            result = cursor.fetchone()
            
            return result[0] if result else 0
            
        except Exception:
            return 0
        finally:
            if conn:
                conn.close()
    
    def _start_new_round(self):
        """Start a new combat round"""
        if not self.current_round:
            return
        
        # Remove dead combatants from initiative order
        living_combatants = [c for c in self.current_round.initiative_order if c.is_alive]
        
        # Create new round
        round_number = self.current_round.number + 1
        self.current_round = CombatRound(
            number=round_number,
            initiative_order=living_combatants,
            current_turn_index=0
        )
        
        self.log(f"[COMBAT] === ROUND {round_number} ===")
        
        # Reset action economy for all combatants
        for combatant in living_combatants:
            combatant.has_taken_action = False
            combatant.has_taken_bonus_action = False
            combatant.reactions_used = 0