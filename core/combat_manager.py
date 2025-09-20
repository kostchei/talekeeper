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
from services.proficiency_system import ProficiencySystem
from services.proficiency_bonus import get_proficiency_bonus
from services.advantage_system import advantage_system, RollType
from services.fighter_abilities import FighterAbilitiesService
from services.standardized_attack_processor import StandardizedAttackProcessor

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
    standardized_attack: Optional[Any] = None  # Store full standardized attack for effects

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
    equipped_armor: Optional[str] = None  # Track equipped armor for adamantine check
    extra_attacks: int = 0
    subclass_name: Optional[str] = None
    feature_flags: Dict[str, Any] = field(default_factory=dict)
    character_features: Optional[Any] = None
    initiative_breakdown: Optional[Dict[str, Any]] = None
    has_remarkable_athlete: Optional[bool] = None

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
        self.proficiency_system = ProficiencySystem(db_path)
        self.fighter_service = FighterAbilitiesService(db_path)
        self.attack_processor = StandardizedAttackProcessor()
        
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
        
        raw_feature_flags = character_data.get('feature_flags')
        feature_flags = raw_feature_flags if isinstance(raw_feature_flags, dict) else {}
        character_features = character_data.get('character_features')
        subclass_name = character_data.get('subclass_id') or character_data.get('subclass')
        has_ra_flag = None
        if isinstance(feature_flags, dict) and feature_flags.get('remarkable_athlete'):
            has_ra_flag = True
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
            extra_attacks=extra_attacks,
            equipped_armor=character_data.get('equipment_armor'),
            subclass_name=subclass_name,
            feature_flags=feature_flags,
            character_features=character_features,
            has_remarkable_athlete=has_ra_flag
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
    
    def _build_initiative_context(self, combatant: Combatant) -> Dict[str, Any]:
        """Assemble context data for initiative rolls."""
        context: Dict[str, Any] = {
            'dexterity_modifier': combatant.initiative_bonus
        }
        if combatant.feature_flags:
            context['feature_flags'] = combatant.feature_flags
        if combatant.character_features is not None:
            context['character_features'] = combatant.character_features
        if self._has_remarkable_athlete(combatant):
            context['remarkable_athlete'] = True
        return context

    def _has_remarkable_athlete(self, combatant: Combatant) -> bool:
        """Check and cache whether the combatant benefits from Remarkable Athlete."""
        if combatant.type != CombatantType.PLAYER:
            return False
        if combatant.has_remarkable_athlete is not None:
            return combatant.has_remarkable_athlete
        flags = combatant.feature_flags or {}
        if isinstance(flags, dict) and flags.get('remarkable_athlete'):
            combatant.has_remarkable_athlete = True
            return True
        if (combatant.class_name or '').lower() != 'fighter' or (combatant.level or 0) < 3:
            combatant.has_remarkable_athlete = False
            return False
        subclass = (combatant.subclass_name or '').lower()
        if subclass == 'champion':
            combatant.has_remarkable_athlete = True
            return True
        has_feature = self.fighter_service.has_remarkable_athlete(combatant.id)
        combatant.has_remarkable_athlete = has_feature
        if has_feature and not combatant.subclass_name:
            combatant.subclass_name = 'champion'
        return has_feature

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
                context = self._build_initiative_context(combatant)
                advantage_sources = advantage_system.get_common_advantage_sources(RollType.INITIATIVE, context)
                disadvantage_sources = advantage_system.get_common_disadvantage_sources(RollType.INITIATIVE, context)
                advantage_state = advantage_system.calculate_advantage_state(advantage_sources, disadvantage_sources)
                total, breakdown = advantage_system.roll_d20_with_advantage(advantage_state, combatant.initiative_bonus)
                breakdown['advantage_sources'] = list(advantage_sources)
                breakdown['disadvantage_sources'] = list(disadvantage_sources)
                breakdown['advantage_state'] = advantage_state.value
                combatant.initiative_roll = total
                combatant.initiative_breakdown = breakdown
                description = advantage_system.format_roll_description(breakdown)
                extras = []
                if advantage_sources:
                    adv_text = ', '.join(advantage_sources)
                    extras.append(f"Adv: {adv_text}")
                if disadvantage_sources:
                    dis_text = ', '.join(disadvantage_sources)
                    extras.append(f"Dis: {dis_text}")
                if extras:
                    extras_text = '; '.join(extras)
                    description += f" ({extras_text})"
                self.log(f"[COMBAT] {combatant.name} Initiative: {description}")
        
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
            self._handle_champion_turn_start(next_combatant)

        return next_combatant

    def _handle_champion_turn_start(self, combatant: Optional[Combatant]) -> None:
        """Trigger Champion subclass automation at the start of a player turn."""
        if not combatant or combatant.type != CombatantType.PLAYER:
            return
        if not getattr(self, "fighter_service", None):
            return

        result = self.fighter_service.process_champion_turn_start(combatant.id)
        if not result.get("success"):
            return

        hero_info = result.get("heroic_warrior") or {}
        if hero_info.get("triggered"):
            self.log(f"[COMBAT] [HEROIC WARRIOR] {combatant.name} steels themselves and gains Heroic Inspiration.")

        survivor_info = result.get("survivor") or {}
        if survivor_info.get("healing_triggered") and survivor_info.get("healing"):
            healing_amount = survivor_info.get("healing")
            new_hp = survivor_info.get("new_hp", "?")
            max_hp = survivor_info.get("max_hp", "?")
            self.log(
                f"[COMBAT] [SURVIVOR] {combatant.name} recovers {healing_amount} HP ({new_hp}/{max_hp} HP)."
            )


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
        """Parse monster actions from standardized JSON format"""
        try:
            # Use the standardized attack processor to parse the new format
            standardized_attacks = self.attack_processor.process_monster_attacks(actions_json)
            actions = []

            for attack in standardized_attacks:
                # Convert standardized attack to old CombatAction format for compatibility
                damage_dice = None
                damage_type = None

                if attack.primary_damage:
                    damage_dice = attack.primary_damage.dice
                    damage_type = attack.primary_damage.type

                action = CombatAction(
                    name=attack.name,
                    action_type=ActionType.ACTION,
                    description=attack.description,
                    attack_bonus=attack.attack_bonus,
                    damage_dice=damage_dice,
                    damage_type=damage_type
                )

                # Store the full standardized attack for advanced features
                action.standardized_attack = attack
                actions.append(action)

            return actions

        except Exception as e:
            self.log(f"[ERROR] Failed to parse monster actions: {e}")
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
        
        # Calculate attack bonus with proficiency if applicable
        base_attack_bonus = weapon_data.get('attack_bonus', 0)
        
        # Add proficiency bonus for player attacks
        if attacker.type == CombatantType.PLAYER:
            weapon_name = weapon_data.get('name', '')
            is_proficient, _ = self.proficiency_system.is_proficient_with_weapon(attacker.id, weapon_name)
            
            if is_proficient and attacker.level:
                prof_bonus = get_proficiency_bonus(attacker.level)
                attack_bonus = base_attack_bonus + prof_bonus
            else:
                attack_bonus = base_attack_bonus
        else:
            # Monsters already have proficiency built into their attack bonus
            attack_bonus = base_attack_bonus
        
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
        
        # Check for critical hit (natural 20)
        is_critical = d20_roll == 20
        
        # Check if target is wearing adamantine armor (negates critical hits)
        if is_critical and target.type == CombatantType.PLAYER and target.equipped_armor:
            if 'adamantine' in target.equipped_armor.lower():
                self.log(f"[ADAMANTINE] {target.name}'s adamantine armor prevents the critical hit!")
                is_critical = False
        
        # Check for hit (critical always hits)
        hit = total_attack >= target.armor_class or d20_roll == 20
        
        if hit:
            # Damage roll
            damage = self._roll_damage(action.damage_dice or '1d6')
            
            # Double damage dice on critical hit
            if is_critical:
                crit_damage = self._roll_damage(action.damage_dice or '1d6')
                damage += crit_damage
                self.log(f"[CRITICAL HIT!] {attacker.name} scores a critical hit!")
            
            # Apply damage
            target.hit_points -= damage
            if target.hit_points <= 0:
                target.hit_points = 0
                target.is_alive = False

            # Process standardized attack effects (conditions, saves, etc.)
            effect_results = []
            if hasattr(action, 'standardized_attack') and action.standardized_attack:
                effect_results = self._process_attack_effects(action.standardized_attack, target, attacker)

            if is_critical:
                self.log(f"[COMBAT] [CRITICAL HIT!] {attacker.name} {action.name} critically hits! Attack: {d20_roll} + {attack_bonus} = {total_attack} vs AC {target.armor_class} for {damage} damage")
            else:
                self.log(f"[COMBAT] [HIT] {attacker.name} {action.name} hits! Attack: {d20_roll} + {attack_bonus} = {total_attack} vs AC {target.armor_class} for {damage} damage")

            # Log any effects
            for effect_result in effect_results:
                self.log(f"[EFFECT] {effect_result}")

            return {
                'hit': True,
                'attack_roll': total_attack,
                'damage': damage,
                'target_hp': target.hit_points,
                'is_critical': is_critical,
                'effects': effect_results
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
    
    def _process_attack_effects(self, standardized_attack, target: Combatant, attacker: Combatant) -> List[str]:
        """Process standardized attack effects (saves, conditions, etc.)"""
        effect_results = []

        if not standardized_attack.effects:
            return effect_results

        for effect in standardized_attack.effects:
            try:
                result = self._process_single_effect(effect, target, attacker)
                if result:
                    effect_results.append(result)
            except Exception as e:
                self.log(f"[ERROR] Failed to process effect {effect.type}: {e}")

        return effect_results

    def _process_single_effect(self, effect, target: Combatant, attacker: Combatant) -> Optional[str]:
        """Process a single standardized effect"""
        effect_type = effect.type.value if hasattr(effect.type, 'value') else str(effect.type)

        if effect_type == "save_or_condition":
            return self._handle_save_or_condition(effect, target, attacker)
        elif effect_type == "save_or_damage":
            return self._handle_save_or_damage(effect, target, attacker)
        elif effect_type == "automatic_condition":
            return self._handle_automatic_condition(effect, target, attacker)
        elif effect_type == "size_condition":
            return self._handle_size_condition(effect, target, attacker)
        else:
            return f"Unknown effect type: {effect_type}"

    def _handle_save_or_condition(self, effect, target: Combatant, attacker: Combatant) -> Optional[str]:
        """Handle save-or-condition effects (e.g., paralysis, poisoned)"""
        if target.type != CombatantType.PLAYER:
            return None  # For now, only apply conditions to players

        save_dc = effect.save_dc
        save_ability = effect.save_ability
        condition = effect.condition

        # Roll saving throw
        d20_roll = random.randint(1, 20)
        save_modifier = self._get_saving_throw_modifier(target, save_ability)
        total_save = d20_roll + save_modifier

        if total_save >= save_dc:
            return f"{target.name} saves against {condition}! (rolled {d20_roll}+{save_modifier}={total_save} vs DC {save_dc})"
        else:
            # Apply condition
            if condition not in target.conditions:
                target.conditions.append(condition)
            return f"{target.name} fails save and is {condition}! (rolled {d20_roll}+{save_modifier}={total_save} vs DC {save_dc})"

    def _handle_save_or_damage(self, effect, target: Combatant, attacker: Combatant) -> Optional[str]:
        """Handle save-or-damage effects (e.g., poison damage)"""
        save_dc = effect.save_dc
        save_ability = effect.save_ability

        # Roll saving throw
        d20_roll = random.randint(1, 20)
        save_modifier = self._get_saving_throw_modifier(target, save_ability)
        total_save = d20_roll + save_modifier

        if total_save >= save_dc:
            # Success - half damage or different effect
            if effect.damage_success:
                damage = self._roll_damage(effect.damage_success.dice)
                target.hit_points -= damage
                return f"{target.name} saves! Takes {damage} {effect.damage_success.type} damage (rolled {d20_roll}+{save_modifier}={total_save} vs DC {save_dc})"
            else:
                return f"{target.name} saves! (rolled {d20_roll}+{save_modifier}={total_save} vs DC {save_dc})"
        else:
            # Failure - full damage
            if effect.damage_fail:
                damage = self._roll_damage(effect.damage_fail.dice)
                target.hit_points -= damage
                return f"{target.name} fails save! Takes {damage} {effect.damage_fail.type} damage (rolled {d20_roll}+{save_modifier}={total_save} vs DC {save_dc})"
            else:
                return f"{target.name} fails save! (rolled {d20_roll}+{save_modifier}={total_save} vs DC {save_dc})"

    def _handle_automatic_condition(self, effect, target: Combatant, attacker: Combatant) -> Optional[str]:
        """Handle automatic conditions (e.g., restrained by web)"""
        if target.type != CombatantType.PLAYER:
            return None

        condition = effect.condition
        if condition not in target.conditions:
            target.conditions.append(condition)
        return f"{target.name} is automatically {condition}!"

    def _handle_size_condition(self, effect, target: Combatant, attacker: Combatant) -> Optional[str]:
        """Handle size-based conditions (e.g., grapple large or smaller)"""
        if target.type != CombatantType.PLAYER:
            return None

        # For simplicity, assume players are Medium size
        max_size = effect.max_size
        if max_size in ["huge", "large", "medium"]:  # Player qualifies
            condition = effect.condition
            if condition not in target.conditions:
                target.conditions.append(condition)
            return f"{target.name} is {condition} (size restriction)!"
        else:
            return f"{target.name} is too large to be affected!"

    def _get_saving_throw_modifier(self, combatant: Combatant, ability: str) -> int:
        """Get saving throw modifier for a given ability"""
        # For now, return a basic modifier based on type
        # In a full implementation, this would look up actual ability scores
        if combatant.type == CombatantType.PLAYER:
            # Players get decent saves
            return 2  # Basic proficiency bonus
        else:
            # Monsters get minimal saves
            return 0

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
