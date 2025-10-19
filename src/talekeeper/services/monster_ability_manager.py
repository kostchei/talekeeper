# core
# category: core
"""
Monster Non-Attack Ability Manager

Handles monster abilities that don't use standard attack rolls:
- Breath weapons (recharge mechanics)
- Limited use abilities (X/Day)
- Save-based effects (charm, fear, paralysis, etc.)
- Ongoing condition application

Integrates with existing condition_manager and save systems.
"""

import sqlite3
import json
import random
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from loguru import logger

from talekeeper.services.condition_manager import ConditionManager, ConditionType, ActiveCondition
from talekeeper.services.dice import DiceRoller


class RechargeType(Enum):
    """Types of recharge mechanics."""
    RECHARGE_5_6 = "5-6"
    RECHARGE_4_6 = "4-6"
    RECHARGE_6 = "6"
    NONE = "none"


class AbilityType(Enum):
    """Types of monster abilities."""
    RECHARGE = "recharge"
    LIMITED_USE = "limited_use"
    AT_WILL = "at_will"
    LEGENDARY = "legendary"


@dataclass
class MonsterAbility:
    """Represents a monster ability."""
    name: str
    ability_type: AbilityType
    save_type: Optional[str] = None
    save_dc: Optional[int] = None
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    condition_on_fail: Optional[str] = None
    recharge_type: RechargeType = RechargeType.NONE
    max_uses: int = -1
    area_type: Optional[str] = None
    area_size: Optional[int] = None
    description: str = ""
    half_damage_on_save: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'ability_type': self.ability_type.value,
            'save_type': self.save_type,
            'save_dc': self.save_dc,
            'damage_dice': self.damage_dice,
            'damage_type': self.damage_type,
            'condition_on_fail': self.condition_on_fail,
            'recharge_type': self.recharge_type.value,
            'max_uses': self.max_uses,
            'area_type': self.area_type,
            'area_size': self.area_size,
            'description': self.description,
            'half_damage_on_save': self.half_damage_on_save
        }


@dataclass
class AbilityState:
    """Tracks the current state of an ability."""
    ability_name: str
    is_available: bool = True
    uses_remaining: int = -1
    last_recharge_roll: Optional[int] = None


class MonsterAbilityManager:
    """
    Manages monster non-attack abilities.

    Responsibilities:
    - Track recharge abilities (breath weapons)
    - Track limited use abilities (X/Day)
    - Handle save-based effects
    - Apply conditions on failed saves
    - Integrate with existing condition system
    """

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.dice_roller = DiceRoller()
        self.condition_manager = ConditionManager(db_path)
        self._ensure_tables()

    def _ensure_tables(self):
        """Create ability tracking tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monster_ability_tracker (
                    encounter_id TEXT NOT NULL,
                    monster_id TEXT NOT NULL,
                    ability_name TEXT NOT NULL,
                    ability_type TEXT NOT NULL,
                    recharge_requirement TEXT,
                    max_uses INTEGER DEFAULT -1,
                    uses_remaining INTEGER DEFAULT -1,
                    is_available BOOLEAN DEFAULT 1,
                    last_recharge_roll INTEGER,
                    PRIMARY KEY (encounter_id, monster_id, ability_name)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monster_ability_effects (
                    effect_id TEXT PRIMARY KEY,
                    encounter_id TEXT NOT NULL,
                    source_monster_id TEXT NOT NULL,
                    ability_name TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    effect_type TEXT NOT NULL,
                    save_dc INTEGER,
                    duration_type TEXT,
                    duration_remaining INTEGER,
                    can_repeat_save BOOLEAN,
                    save_ability TEXT,
                    created_round INTEGER
                )
            """)

            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_ability(self, encounter_id: str, monster_id: str, ability: MonsterAbility):
        """Initialize an ability for tracking in an encounter."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO monster_ability_tracker
                (encounter_id, monster_id, ability_name, ability_type,
                 recharge_requirement, max_uses, uses_remaining, is_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                encounter_id,
                monster_id,
                ability.name,
                ability.ability_type.value,
                ability.recharge_type.value,
                ability.max_uses,
                ability.max_uses,
                True
            ))

            conn.commit()

        logger.info(f"Initialized ability {ability.name} for monster {monster_id}")

    def attempt_recharge(self, encounter_id: str, monster_id: str, ability_name: str) -> Tuple[bool, int]:
        """
        Attempt to recharge an ability at the start of the monster's turn.

        Returns:
            (success, roll) - Whether recharge succeeded and the d6 roll
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT recharge_requirement, is_available
                FROM monster_ability_tracker
                WHERE encounter_id = ? AND monster_id = ? AND ability_name = ?
            """, (encounter_id, monster_id, ability_name))

            row = cursor.fetchone()
            if not row:
                return (False, 0)

            recharge_req = row['recharge_requirement']

            if recharge_req == RechargeType.NONE.value:
                return (True, 0)

            roll = random.randint(1, 6)
            success = False

            if recharge_req == RechargeType.RECHARGE_5_6.value:
                success = roll >= 5
            elif recharge_req == RechargeType.RECHARGE_4_6.value:
                success = roll >= 4
            elif recharge_req == RechargeType.RECHARGE_6.value:
                success = roll == 6

            cursor.execute("""
                UPDATE monster_ability_tracker
                SET is_available = ?, last_recharge_roll = ?
                WHERE encounter_id = ? AND monster_id = ? AND ability_name = ?
            """, (success, roll, encounter_id, monster_id, ability_name))

            conn.commit()

        return (success, roll)

    def use_ability(self, encounter_id: str, monster_id: str, ability_name: str) -> bool:
        """
        Mark an ability as used.

        Returns:
            Whether the ability was available to use
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT is_available, uses_remaining, ability_type
                FROM monster_ability_tracker
                WHERE encounter_id = ? AND monster_id = ? AND ability_name = ?
            """, (encounter_id, monster_id, ability_name))

            row = cursor.fetchone()
            if not row or not row['is_available']:
                return False

            ability_type = row['ability_type']
            uses_remaining = row['uses_remaining']

            if ability_type == AbilityType.LIMITED_USE.value:
                if uses_remaining <= 0:
                    return False

                uses_remaining -= 1
                is_available = uses_remaining > 0

                cursor.execute("""
                    UPDATE monster_ability_tracker
                    SET uses_remaining = ?, is_available = ?
                    WHERE encounter_id = ? AND monster_id = ? AND ability_name = ?
                """, (uses_remaining, is_available, encounter_id, monster_id, ability_name))

            elif ability_type == AbilityType.RECHARGE.value:
                cursor.execute("""
                    UPDATE monster_ability_tracker
                    SET is_available = 0
                    WHERE encounter_id = ? AND monster_id = ? AND ability_name = ?
                """, (encounter_id, monster_id, ability_name))

            conn.commit()

        return True

    def execute_ability(self, encounter_id: str, monster_id: str, monster_name: str,
                       ability: MonsterAbility, target_id: str,
                       target_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a monster ability against a target.

        Returns:
            Dictionary with execution results including save roll, damage, etc.
        """
        if not self.use_ability(encounter_id, monster_id, ability.name):
            return {
                'success': False,
                'error': 'Ability not available'
            }

        result = {
            'success': True,
            'ability_name': ability.name,
            'monster_name': monster_name,
            'messages': []
        }

        result['messages'].append(f"{monster_name} uses {ability.name}!")

        if ability.save_type and ability.save_dc:
            save_result = self._roll_saving_throw(
                target_data,
                ability.save_type,
                ability.save_dc
            )

            result['save_roll'] = save_result['roll']
            result['save_total'] = save_result['total']
            result['save_success'] = save_result['success']
            result['save_dc'] = ability.save_dc

            if save_result['success']:
                result['messages'].append(
                    f"Save successful! (rolled {save_result['total']} vs DC {ability.save_dc})"
                )
            else:
                result['messages'].append(
                    f"Save failed! (rolled {save_result['total']} vs DC {ability.save_dc})"
                )

        if ability.damage_dice:
            damage_roll = self.dice_roller.roll(ability.damage_dice)

            if ability.save_type and ability.half_damage_on_save and save_result.get('success'):
                damage_roll = damage_roll // 2
                result['messages'].append(
                    f"Half damage on successful save: {damage_roll} {ability.damage_type}"
                )
            else:
                result['messages'].append(
                    f"Damage: {damage_roll} {ability.damage_type}"
                )

            result['damage'] = damage_roll
            result['damage_type'] = ability.damage_type

        if ability.condition_on_fail and ability.save_type:
            if not save_result.get('success'):
                condition_applied = self._apply_condition(
                    target_id,
                    ability.condition_on_fail,
                    source=f"{monster_name}'s {ability.name}",
                    save_dc=ability.save_dc,
                    save_ability=ability.save_type
                )

                if condition_applied:
                    result['messages'].append(
                        f"Applied {ability.condition_on_fail} condition!"
                    )
                    result['condition_applied'] = ability.condition_on_fail

        return result

    def _roll_saving_throw(self, target: Dict[str, Any], ability: str, dc: int) -> Dict[str, Any]:
        """Roll a saving throw for a target."""
        ability_score = target.get(ability, 10)
        ability_mod = (ability_score - 10) // 2

        proficiency_bonus = target.get('proficiency_bonus', 0)

        save_proficiencies = target.get('save_proficiencies', [])
        if ability in save_proficiencies:
            ability_mod += proficiency_bonus

        roll = random.randint(1, 20)
        total = roll + ability_mod

        return {
            'roll': roll,
            'modifier': ability_mod,
            'total': total,
            'success': total >= dc,
            'dc': dc
        }

    def _apply_condition(self, character_id: str, condition_name: str,
                        source: str, save_dc: Optional[int] = None,
                        save_ability: Optional[str] = None) -> bool:
        """Apply a condition to a character."""
        try:
            condition_type = ConditionType(condition_name.lower())
        except ValueError:
            logger.error(f"Unknown condition type: {condition_name}")
            return False

        condition = ActiveCondition(
            condition_type=condition_type,
            source=source,
            duration_type="save_ends" if save_dc else "permanent",
            save_dc=save_dc,
            save_ability=save_ability,
            save_frequency="end_of_turn"
        )

        try:
            return self.condition_manager.add_condition(character_id, condition)
        except Exception as e:
            logger.warning(f"Could not apply condition (schema mismatch or missing table): {e}")
            return False

    def get_ability_state(self, encounter_id: str, monster_id: str,
                         ability_name: str) -> Optional[AbilityState]:
        """Get the current state of an ability."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ability_name, is_available, uses_remaining, last_recharge_roll
                FROM monster_ability_tracker
                WHERE encounter_id = ? AND monster_id = ? AND ability_name = ?
            """, (encounter_id, monster_id, ability_name))

            row = cursor.fetchone()
            if not row:
                return None

            return AbilityState(
                ability_name=row['ability_name'],
                is_available=bool(row['is_available']),
                uses_remaining=row['uses_remaining'],
                last_recharge_roll=row['last_recharge_roll']
            )

    def get_all_monster_abilities(self, encounter_id: str,
                                 monster_id: str) -> List[AbilityState]:
        """Get all abilities for a monster in an encounter."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ability_name, is_available, uses_remaining, last_recharge_roll
                FROM monster_ability_tracker
                WHERE encounter_id = ? AND monster_id = ?
            """, (encounter_id, monster_id))

            rows = cursor.fetchall()

            return [
                AbilityState(
                    ability_name=row['ability_name'],
                    is_available=bool(row['is_available']),
                    uses_remaining=row['uses_remaining'],
                    last_recharge_roll=row['last_recharge_roll']
                )
                for row in rows
            ]

    def reset_daily_abilities(self, encounter_id: str, monster_id: str):
        """Reset all daily abilities (called on long rest)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE monster_ability_tracker
                SET uses_remaining = max_uses, is_available = 1
                WHERE encounter_id = ? AND monster_id = ?
                AND ability_type = ?
            """, (encounter_id, monster_id, AbilityType.LIMITED_USE.value))

            conn.commit()


PREDEFINED_ABILITIES = {
    'fire_breath': MonsterAbility(
        name="Fire Breath",
        ability_type=AbilityType.RECHARGE,
        recharge_type=RechargeType.RECHARGE_5_6,
        save_type="dexterity",
        save_dc=19,
        damage_dice="18d6",
        damage_type="fire",
        area_type="cone",
        area_size=60,
        half_damage_on_save=True,
        description="90 ft. cone, DC 19 Dex save, 63 (18d6) fire damage, half on save"
    ),

    'lightning_breath': MonsterAbility(
        name="Lightning Breath",
        ability_type=AbilityType.RECHARGE,
        recharge_type=RechargeType.RECHARGE_5_6,
        save_type="dexterity",
        save_dc=19,
        damage_dice="12d10",
        damage_type="lightning",
        area_type="line",
        area_size=90,
        half_damage_on_save=True,
        description="90 ft. line, DC 19 Dex save, 66 (12d10) lightning damage, half on save"
    ),

    'acid_breath': MonsterAbility(
        name="Acid Breath",
        ability_type=AbilityType.RECHARGE,
        recharge_type=RechargeType.RECHARGE_5_6,
        save_type="dexterity",
        save_dc=18,
        damage_dice="12d8",
        damage_type="acid",
        area_type="line",
        area_size=60,
        half_damage_on_save=True,
        description="60 ft. line, DC 18 Dex save, 54 (12d8) acid damage, half on save"
    ),

    'sleep_breath': MonsterAbility(
        name="Sleep Breath",
        ability_type=AbilityType.RECHARGE,
        recharge_type=RechargeType.RECHARGE_5_6,
        save_type="constitution",
        save_dc=18,
        condition_on_fail="unconscious",
        area_type="cone",
        area_size=60,
        description="60 ft. cone, DC 18 Con save or fall unconscious for 10 minutes"
    ),

    'frightful_presence': MonsterAbility(
        name="Frightful Presence",
        ability_type=AbilityType.AT_WILL,
        save_type="wisdom",
        save_dc=19,
        condition_on_fail="frightened",
        area_type="radius",
        area_size=120,
        description="120 ft. radius, DC 19 Wis save or frightened for 1 minute"
    ),

    'dominate_mind': MonsterAbility(
        name="Dominate Mind",
        ability_type=AbilityType.LIMITED_USE,
        max_uses=2,
        save_type="wisdom",
        save_dc=16,
        condition_on_fail="charmed",
        description="2/Day, DC 16 Wis save or charmed (aboleth control)"
    ),

    'petrifying_gaze': MonsterAbility(
        name="Petrifying Gaze",
        ability_type=AbilityType.AT_WILL,
        save_type="constitution",
        save_dc=14,
        condition_on_fail="restrained",
        description="DC 14 Con save or begin turning to stone (second fail: petrified)"
    ),

    'paralyzing_touch': MonsterAbility(
        name="Paralyzing Touch",
        ability_type=AbilityType.AT_WILL,
        save_type="constitution",
        save_dc=13,
        condition_on_fail="paralyzed",
        description="DC 13 Con save or paralyzed for 1 minute"
    )
}
