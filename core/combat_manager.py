"""
D&D 2024 Compliant Combat Manager

Handles initiative, turn order, action economy, and combat resolution
according to official D&D 2024 rules from the SRD.
"""

import random
import sqlite3
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from services.proficiency_system import ProficiencySystem
from services.proficiency_bonus import get_proficiency_bonus
from services.fighting_style_effects import FightingStyleEffects
from services.equipment import EquipmentService

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
    strength: int
    dexterity: int
    
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
    equipped_armor: Optional[str] = None
    extra_attacks: int = 0
    feats: List[str] = field(default_factory=list)
    fighting_styles: List[str] = field(default_factory=list)
    savage_attacker_used_this_turn: bool = False
    light_property_attack_used_this_turn: bool = False

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
        self.fighting_style_service = FightingStyleEffects(db_path)
        self.equipment_service = EquipmentService(db_path)
        
    def add_player_combatant(self, character_data: Dict[str, Any]) -> Combatant:
        """Add player character to combat"""
        character_id = character_data['id']
        
        dex_score = character_data.get('dexterity', 10)
        initiative_bonus = (dex_score - 10) // 2
        
        extra_attacks = self._get_extra_attack_count(
            character_data.get('class_id', ''),
            character_data.get('level', 1)
        )
        
        feats = self._get_character_feats(character_id)
        styles = self.fighting_style_service._get_character_styles(character_id)

        ac = character_data.get('ac', 10)
        if 'Dual Wielder' in feats:
            equipped_weapons = self.equipment_service.get_equipped_weapons(character_id)
            if len(equipped_weapons) >= 2:
                ac += 1

        combatant = Combatant(
            id=character_id,
            name=character_data.get('name', 'Player'),
            type=CombatantType.PLAYER,
            armor_class=ac,
            hit_points=character_data.get('hp', 1),
            max_hit_points=character_data.get('max_hp', 1),
            strength=character_data.get('strength', 10),
            dexterity=character_data.get('dexterity', 10),
            initiative_bonus=initiative_bonus,
            class_name=character_data.get('class_id'),
            level=character_data.get('level', 1),
            extra_attacks=extra_attacks,
            equipped_armor=character_data.get('equipment_armor'),
            feats=feats,
            fighting_styles=styles
        )
        
        self.combatants[character_id] = combatant
        return combatant
    
    def add_monster_combatant(self, monster_id: str, monster_data: Dict[str, Any]) -> Combatant:
        """Add monster to combat"""
        dex_score = monster_data.get('dexterity', 10)
        initiative_bonus = (dex_score - 10) // 2
        
        actions = self._parse_monster_actions(monster_data.get('actions', '[]'))
        multiattack_actions = self._parse_multiattack(actions)
        
        combatant = Combatant(
            id=monster_id,
            name=monster_data.get('name', 'Monster'),
            type=CombatantType.MONSTER,
            armor_class=monster_data.get('armor_class', 10),
            hit_points=monster_data.get('hit_points', 1),
            max_hit_points=monster_data.get('hit_points', 1),
            strength=monster_data.get('strength', 10),
            dexterity=monster_data.get('dexterity', 10),
            initiative_bonus=initiative_bonus,
            actions=actions,
            multiattack_actions=multiattack_actions
        )
        
        self.combatants[monster_id] = combatant
        return combatant
    
    def start_combat(self) -> List[Combatant]:
        """Start combat by rolling initiative for all combatants."""
        if not self.combatants:
            raise ValueError("No combatants added to combat")
        
        self.log("[COMBAT] ==================================================")
        self.log("[COMBAT] [DICE] ROLLING INITIATIVE FOR COMBAT!")
        self.log("[COMBAT] ==================================================")
        
        for combatant in self.combatants.values():
            if combatant.is_alive:
                roll = random.randint(1, 20)
                combatant.initiative_roll = roll + combatant.initiative_bonus
                self.log(f"[COMBAT] {combatant.name} Initiative: d20({roll}) + {combatant.initiative_bonus} = {combatant.initiative_roll}")
        
        initiative_order = sorted([c for c in self.combatants.values() if c.is_alive and c.initiative_roll is not None],
                                  key=lambda c: (c.initiative_roll, random.random()), reverse=True)
        
        self.current_round = CombatRound(number=1, initiative_order=initiative_order)
        self.combat_active = True
        
        self.log("[COMBAT] Initiative Order:")
        for i, combatant in enumerate(initiative_order):
            self.log(f"[COMBAT]   {i+1}. {combatant.name} ({combatant.initiative_roll})")
        
        return initiative_order
    
    def get_current_combatant(self) -> Optional[Combatant]:
        if not self.current_round or self.current_round.completed:
            return None
        if self.current_round.current_turn_index >= len(self.current_round.initiative_order):
            return None
        return self.current_round.initiative_order[self.current_round.current_turn_index]
    
    def is_player_turn(self) -> bool:
        current = self.get_current_combatant()
        return current is not None and current.type == CombatantType.PLAYER
    
    def execute_player_attack(self, character_id: str, weapon_data: Dict[str, Any],
                            target_id: str) -> Dict[str, Any]:
        """Execute player's Attack action, including Extra Attacks and Nick property."""
        if not self.is_player_turn(): return {'error': 'Not player turn'}
        combatant = self.combatants.get(character_id)
        target = self.combatants.get(target_id)
        if not combatant or not target: return {'error': 'Invalid combatant or target'}
        if not target.is_alive: return {'error': 'Cannot target dead creature'}
        if combatant.has_taken_action: return {'error': 'Already took action this turn'}

        combatant.has_taken_action = True
        num_attacks = 1 + combatant.extra_attacks
        
        results = {'attacks': [], 'total_damage': 0, 'targets_hit': [], 'targets_killed': [], 'action_economy_cost': {'action': 1}}
        self.log(f"[COMBAT] {combatant.name} uses Attack Action with {weapon_data.get('name', 'weapon')}")

        for attack_num in range(num_attacks):
            if not target.is_alive: break
            attack_result = self._execute_single_attack(combatant, target, weapon_data, attack_num + 1, num_attacks)
            results['attacks'].append(attack_result)
            if attack_result.get('hit'):
                results['total_damage'] += attack_result.get('damage', 0)
                if target_id not in results['targets_hit']: results['targets_hit'].append(target_id)
                if not target.is_alive:
                    results['targets_killed'].append(target_id)
                    break
        
        # Handle Nick property
        weapon_props = weapon_data.get('weapon_properties', [])
        is_proficient, _ = self.proficiency_system.is_proficient_with_weapon(combatant.id, weapon_data.get('name', ''))
        if 'Nick' in weapon_props and is_proficient and not combatant.light_property_attack_used_this_turn and target.is_alive:
            combatant.light_property_attack_used_this_turn = True
            self.log(f"[COMBAT] {combatant.name} uses Nick property for an extra attack as part of the Attack Action.")

            attack_result = self._execute_single_attack(combatant, target, weapon_data, num_attacks + 1, num_attacks + 1, is_offhand=True)
            results['attacks'].append(attack_result)
            if attack_result.get('hit'):
                results['total_damage'] += attack_result.get('damage', 0)
                if target_id not in results['targets_hit']: results['targets_hit'].append(target_id)
                if not target.is_alive: results['targets_killed'].append(target_id)

        if not target.is_alive and target_id in results['targets_killed']:
            self.log(f"[COMBAT] {target.name} has been defeated!")
        
        return results

    def can_make_offhand_attack(self, character_id: str) -> bool:
        """Check if character can make an off-hand attack."""
        if not self.is_player_turn(): return False
        combatant = self.combatants.get(character_id)
        if not combatant or combatant.has_taken_bonus_action: return False

        equipped_weapons = self.equipment_service.get_equipped_weapons(character_id)
        if len(equipped_weapons) < 2: return False

        main_hand = next((w for w in equipped_weapons if w['slot'] == 'main_hand'), None)
        off_hand = next((w for w in equipped_weapons if w['slot'] == 'off_hand'), None)
        if not main_hand or not off_hand: return False

        has_dual_wielder = 'Dual Wielder' in combatant.feats
        is_light_main = 'Light' in main_hand.get('weapon_properties', [])
        is_light_off = 'Light' in off_hand.get('weapon_properties', [])

        if has_dual_wielder:
            # Feat allows any one-handed melee weapons
            is_one_handed_main = 'two-handed' not in main_hand.get('weapon_properties', [])
            is_one_handed_off = 'two-handed' not in off_hand.get('weapon_properties', [])
            return is_one_handed_main and is_one_handed_off
        else:
            # Without the feat, both weapons must be Light
            return is_light_main and is_light_off

    def execute_offhand_attack(self, character_id: str, target_id: str) -> Dict[str, Any]:
        """Execute an off-hand attack as a bonus action."""
        if not self.is_player_turn(): return {'error': 'Not player turn'}
        combatant = self.combatants.get(character_id)
        target = self.combatants.get(target_id)

        if not combatant or not target: return {'error': 'Invalid combatant or target'}
        if combatant.has_taken_bonus_action: return {'error': 'Bonus action already taken'}
        if combatant.light_property_attack_used_this_turn: return {'error': 'Light property attack already used this turn'}

        if not self.can_make_offhand_attack(character_id):
            return {'error': 'Cannot make off-hand attack'}

        equipped_weapons = self.equipment_service.get_equipped_weapons(character_id)
        off_hand_weapon = next((w for w in equipped_weapons if w['slot'] == 'off_hand'), None)
        if not off_hand_weapon: return {'error': 'No off-hand weapon equipped'}

        combatant.has_taken_bonus_action = True
        combatant.light_property_attack_used_this_turn = True
        self.log(f"[COMBAT] {combatant.name} uses Bonus Action for Two-Weapon Fighting!")
        
        attack_result = self._execute_single_attack(combatant, target, off_hand_weapon, 1, 1, is_offhand=True)
        
        results = {
            'attacks': [attack_result],
            'total_damage': attack_result.get('damage', 0),
            'targets_hit': [target_id] if attack_result.get('hit') else [],
            'targets_killed': [target_id] if not target.is_alive else []
        }

        if not target.is_alive:
            self.log(f"[COMBAT] {target.name} has been defeated!")
            xp = self._calculate_xp_reward(target.id)
            if xp > 0:
                results['xp_gained'] = xp
                self.log(f"[XP] Gained {xp} XP for defeating {target.name}")
        return results

    def execute_monster_turn(self, monster_id: str) -> Dict[str, Any]:
        """Execute monster's turn with proper Multiattack support."""
        if self.is_player_turn(): return {'error': 'Not monster turn'}
        combatant = self.combatants.get(monster_id)
        if not combatant or not combatant.is_alive: return {'error': 'Invalid or dead monster'}
        if combatant.has_taken_action: return {'error': 'Monster already took action'}

        combatant.has_taken_action = True
        results = {'attacks': [], 'total_damage': 0, 'targets_hit': []}
        
        player_target = next((c for c in self.combatants.values() if c.type == CombatantType.PLAYER and c.is_alive), None)
        if not player_target:
            self.log(f"[COMBAT] {combatant.name} has no valid targets")
            return results
        
        if combatant.multiattack_actions:
            self.log(f"[COMBAT] {combatant.name} uses Multiattack on {player_target.name}")
            for action_name in combatant.multiattack_actions:
                action = self._find_monster_action(combatant, action_name)
                if action:
                    attack_result = self._execute_monster_attack(combatant, player_target, action)
                    results['attacks'].append(attack_result)
                    if attack_result.get('hit'):
                        results['total_damage'] += attack_result.get('damage', 0)
                        if player_target.id not in results['targets_hit']: results['targets_hit'].append(player_target.id)
        elif combatant.actions:
            action = combatant.actions[0]
            self.log(f"[COMBAT] {combatant.name} uses {action.name} on {player_target.name}")
            attack_result = self._execute_monster_attack(combatant, player_target, action)
            results['attacks'].append(attack_result)
            if attack_result.get('hit'):
                results['total_damage'] += attack_result.get('damage', 0)
                results['targets_hit'].append(player_target.id)
        return results
    
    def advance_turn(self) -> Optional[Combatant]:
        """Advance to the next combatant's turn."""
        if not self.current_round: return None
        
        current = self.get_current_combatant()
        if current:
            current.has_taken_action = False
            current.has_taken_bonus_action = False
            current.reactions_used = 0
            if current.type == CombatantType.PLAYER:
                current.savage_attacker_used_this_turn = False
                current.light_property_attack_used_this_turn = False
        
        self.current_round.current_turn_index += 1
        
        if self.current_round.current_turn_index >= len(self.current_round.initiative_order):
            self._start_new_round()
        
        next_combatant = self.get_current_combatant()
        if next_combatant:
            self.log(f"[COMBAT] [LIGHTNING] {next_combatant.name}'s turn!")
        return next_combatant
    
    def is_combat_ended(self) -> bool:
        living_players = sum(1 for c in self.combatants.values() if c.type == CombatantType.PLAYER and c.is_alive)
        living_monsters = sum(1 for c in self.combatants.values() if c.type == CombatantType.MONSTER and c.is_alive)
        return living_players == 0 or living_monsters == 0
    
    def end_combat(self) -> Dict[str, Any]:
        """End combat and return summary."""
        self.combat_active = False
        living_players = [c.name for c in self.combatants.values() if c.type == CombatantType.PLAYER and c.is_alive]
        if living_players:
            self.log("[COMBAT] Combat victory! All enemies defeated.")
            result = "victory"
        else:
            self.log("[COMBAT] Combat defeat! Player character defeated.")
            result = "defeat"
        
        return {'result': result, 'rounds': self.current_round.number if self.current_round else 0}
    
    def log(self, message: str):
        self.combat_log.append(message)
        print(message)
    
    def get_combat_log(self) -> List[str]:
        return self.combat_log.copy()
    
    def _get_character_feats(self, character_id: str) -> List[str]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT feat_name FROM character_feats WHERE character_id = ?", (character_id,))
            feats = [row[0] for row in cursor.fetchall()]
            conn.close()
            return feats
        except sqlite3.Error: return []

    def _get_extra_attack_count(self, class_name: str, level: int) -> int:
        class_name = class_name.lower()
        if class_name == 'fighter':
            if level >= 20: return 3
            if level >= 11: return 2
            if level >= 5: return 1
        if class_name in ['barbarian', 'paladin', 'ranger', 'monk'] and level >= 5:
            return 1
        return 0

    def _get_ability_mod(self, combatant: Combatant, weapon_data: Dict[str, Any]) -> int:
        """Determine ability modifier (STR or DEX) for a weapon attack."""
        props = weapon_data.get('weapon_properties', [])
        str_mod = (combatant.strength - 10) // 2
        dex_mod = (combatant.dexterity - 10) // 2
        
        if 'ranged' in props: return dex_mod
        if 'finesse' in props: return max(str_mod, dex_mod)
        return str_mod

    def _calculate_attack_bonus(self, combatant: Combatant, weapon_data: Dict[str, Any]) -> int:
        """Calculate the total attack bonus for a player's weapon attack."""
        if combatant.type != CombatantType.PLAYER: return weapon_data.get('attack_bonus', 0)

        # Ability Modifier
        ability_mod = self._get_ability_mod(combatant, weapon_data)
        
        # Proficiency Bonus
        prof_bonus = 0
        is_proficient, _ = self.proficiency_system.is_proficient_with_weapon(combatant.id, weapon_data.get('name', ''))
        if is_proficient and combatant.level:
            prof_bonus = get_proficiency_bonus(combatant.level)

        # Magic Weapon Bonus
        magic_bonus = weapon_data.get('attack_bonus', 0)

        # Fighting Style Bonus
        style_bonus = self.fighting_style_service.get_attack_bonus(combatant.id, weapon_data)

        total_bonus = ability_mod + prof_bonus + magic_bonus + style_bonus
        
        log_parts = [f"Mod:{ability_mod}", f"Prof:{prof_bonus}", f"Magic:{magic_bonus}", f"Style:{style_bonus}"]
        self.log(f"[COMBAT] [BONUS] Attack Bonus: {total_bonus} ({' + '.join(log_parts)})")
        return total_bonus
        
    def _calculate_damage_bonus(self, combatant: Combatant, weapon_data: Dict[str, Any], is_offhand: bool) -> int:
        """Calculate the total flat damage bonus for a player's weapon attack."""
        if combatant.type != CombatantType.PLAYER: return 0

        # Ability Modifier
        ability_mod = 0
        if not is_offhand:
            ability_mod = self._get_ability_mod(combatant, weapon_data)
        elif self.fighting_style_service.should_add_ability_mod_to_offhand(combatant.id):
            ability_mod = self._get_ability_mod(combatant, weapon_data)

        # Magic Weapon Bonus
        magic_bonus = weapon_data.get('damage_bonus', 0)

        # Fighting Style Bonus (Dueling)
        all_items = self.equipment_service.get_equipped_items(combatant.id)
        style_bonus = self.fighting_style_service.get_damage_bonus(combatant.id, weapon_data, all_items)
        
        # Rage Bonus (Placeholder)
        rage_bonus = 0 # TODO: Add rage bonus check

        total_bonus = ability_mod + magic_bonus + style_bonus + rage_bonus

        log_parts = [f"Mod:{ability_mod}", f"Magic:{magic_bonus}", f"Style:{style_bonus}", f"Rage:{rage_bonus}"]
        self.log(f"[COMBAT] [BONUS] Damage Bonus: {total_bonus} ({' + '.join(log_parts)})")
        return total_bonus

    def _roll_damage_dice(self, combatant: Combatant, weapon_data: Dict[str, Any], is_critical: bool) -> Tuple[int, List[int]]:
        """Roll weapon damage dice, applying critical hits and relevant fighting styles/feats."""
        damage_dice_str = weapon_data.get('damage_dice', '1d4')
        num_dice, die_size = map(int, damage_dice_str.split('d'))
        
        # Roll initial set of dice
        rolls = [random.randint(1, die_size) for _ in range(num_dice)]
        
        # Handle Savage Attacker (once per turn)
        if 'Savage Attacker' in combatant.feats and not combatant.savage_attacker_used_this_turn:
            second_rolls = [random.randint(1, die_size) for _ in range(num_dice)]
            if sum(second_rolls) > sum(rolls):
                self.log(f"[COMBAT] [SAVAGE ATTACKER] Rerolling {rolls} -> {second_rolls}")
                rolls = second_rolls
            combatant.savage_attacker_used_this_turn = True

        # Handle Great Weapon Fighting
        if "great_weapon_fighting" in combatant.fighting_styles:
            rerolled, changed = self.fighting_style_service.apply_great_weapon_fighting(combatant.id, rolls, weapon_data, die_size)
            if changed:
                self.log(f"[COMBAT] [GREAT WEAPON] Rerolling 1s/2s: {rolls} -> {rerolled}")
                rolls = rerolled

        # Handle Critical Hit (roll all dice again)
        if is_critical:
            crit_rolls = [random.randint(1, die_size) for _ in range(num_dice)]
            self.log(f"[COMBAT] [CRITICAL] Additional damage dice: {crit_rolls}")
            rolls.extend(crit_rolls)

        return sum(rolls), rolls

    def _execute_single_attack(self, attacker: Combatant, target: Combatant,
                             weapon_data: Dict[str, Any], attack_num: int, total_attacks: int,
                             is_offhand: bool = False) -> Dict[str, Any]:
        """Execute a single, fully-calculated player attack roll and damage."""
        self.log(f"[COMBAT] [ATTACK {attack_num}/{total_attacks}] {attacker.name} attacks {target.name} with {weapon_data.get('name', 'a weapon')}.")
        
        d20_roll = random.randint(1, 20)
        is_critical = d20_roll == 20
        attack_bonus = self._calculate_attack_bonus(attacker, weapon_data)
        total_attack_roll = d20_roll + attack_bonus
        
        hit = is_critical or total_attack_roll >= target.armor_class
        self.log(f"[COMBAT] [ROLL] Attack: d20({d20_roll}) + {attack_bonus} = {total_attack_roll} vs AC {target.armor_class}")

        if not hit:
            self.log(f"[COMBAT] [RESULT] Miss!")
            return {'hit': False, 'attack_roll': total_attack_roll, 'damage': 0}

        self.log(f"[COMBAT] [RESULT] Hit!")
        if is_critical: self.log("[COMBAT] [CRITICAL] Critical Hit!")

        dice_total, dice_rolls = self._roll_damage_dice(attacker, weapon_data, is_critical)
        self.log(f"[COMBAT] [ROLL] Damage Dice ({weapon_data.get('damage_dice', '1d4')}): {dice_rolls} = {dice_total}")

        damage_bonus = self._calculate_damage_bonus(attacker, weapon_data, is_offhand)
        total_damage = dice_total + damage_bonus

        target.hit_points -= total_damage
        if target.hit_points <= 0:
            target.hit_points = 0
            target.is_alive = False

        self.log(f"[COMBAT] {target.name} takes {total_damage} damage! ({target.hit_points}/{target.max_hit_points} HP)")
        if not target.is_alive:
            self.log(f"[COMBAT] {target.name} has been defeated!")

        return {
            'hit': True, 'attack_roll': total_attack_roll, 'damage': total_damage,
            'is_critical': is_critical, 'target_hp': target.hit_points
        }
    
    def _execute_monster_attack(self, attacker: Combatant, target: Combatant, 
                               action: CombatAction) -> Dict[str, Any]:
        """Execute a monster attack."""
        d20_roll = random.randint(1, 20)
        attack_bonus = action.attack_bonus or 0
        total_attack = d20_roll + attack_bonus
        is_critical = d20_roll == 20
        
        if is_critical and target.type == CombatantType.PLAYER and target.equipped_armor and 'adamantine' in target.equipped_armor.lower():
            self.log(f"[ADAMANTINE] {target.name}'s adamantine armor prevents the critical hit!")
            is_critical = False
        
        hit = is_critical or total_attack >= target.armor_class
        
        if hit:
            damage, _ = self._roll_damage_dice_monster(action.damage_dice or '1d6', is_critical)
            target.hit_points -= damage
            if target.hit_points <= 0:
                target.hit_points = 0
                target.is_alive = False
            
            self.log(f"[COMBAT] [HIT] {attacker.name} {action.name} hits! Attack: d20({d20_roll})+{attack_bonus}={total_attack} vs AC {target.armor_class} for {damage} damage")
            return {'hit': True, 'damage': damage, 'target_hp': target.hit_points}
        else:
            self.log(f"[COMBAT] [MISS] {attacker.name} {action.name} misses! Attack: d20({d20_roll})+{attack_bonus}={total_attack} vs AC {target.armor_class}")
            return {'hit': False, 'damage': 0}

    def _roll_damage_dice_monster(self, damage_dice_str: str, is_critical: bool) -> Tuple[int, List[int]]:
        """Roll damage for monsters, handling crits."""
        try:
            # Handle complex dice strings like '2d6 + 3'
            parts = re.split(r'([+\-])', damage_dice_str.replace(' ', ''))
            total = 0
            rolls = []
            
            # First part is always a dice roll
            num_dice, die_size = map(int, parts[0].split('d'))
            dice_rolls = [random.randint(1, die_size) for _ in range(num_dice)]
            if is_critical:
                dice_rolls.extend([random.randint(1, die_size) for _ in range(num_dice)])
            
            total += sum(dice_rolls)
            rolls.extend(dice_rolls)

            # Add flat bonuses
            if len(parts) > 1:
                for i in range(1, len(parts), 2):
                    op = parts[i]
                    val = int(parts[i+1])
                    if op == '+': total += val
                    else: total -= val
            
            return max(0, total), rolls
        except (ValueError, IndexError):
            return 1, [1]
            
    def _parse_monster_actions(self, actions_json: str) -> List[CombatAction]:
        try:
            actions_data = json.loads(actions_json) if isinstance(actions_json, str) else actions_json
            actions = []
            for action_data in actions_data:
                name = action_data.get('name', 'Unknown')
                entries = action_data.get('entries', [])
                if name.lower() == 'multiattack': continue

                entry_text = entries[0] if entries else ""
                hit_match = re.search(r'\{@hit (\d+)\}', entry_text)
                damage_match = re.search(r'\{@damage ([^}]+)\}', entry_text)

                action = CombatAction(
                    name=name, action_type=ActionType.ACTION, description=entry_text,
                    attack_bonus=int(hit_match.group(1)) if hit_match else None,
                    damage_dice=damage_match.group(1).replace(' ', '') if damage_match else None
                )
                actions.append(action)
            return actions
        except (json.JSONDecodeError, TypeError): return []

    def _parse_multiattack(self, actions: List[CombatAction]) -> Optional[List[str]]: return None
    def _find_monster_action(self, monster: Combatant, action_name: str) -> Optional[CombatAction]:
        return next((a for a in monster.actions if a.name.lower() == action_name.lower()), None)
    def _calculate_xp_reward(self, monster_id: str) -> int: return 0
    
    def _start_new_round(self):
        if not self.current_round: return
        living_combatants = [c for c in self.current_round.initiative_order if c.is_alive]
        round_number = self.current_round.number + 1
        self.current_round = CombatRound(number=round_number, initiative_order=living_combatants)
        self.log(f"[COMBAT] === ROUND {round_number} ===")
        for combatant in living_combatants:
            combatant.has_taken_action = False
            combatant.has_taken_bonus_action = False
            combatant.reactions_used = 0
            if combatant.type == CombatantType.PLAYER:
                combatant.savage_attacker_used_this_turn = False