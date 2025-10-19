# core
# category: core
import sqlite3
import random
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod

from talekeeper.services.spell_effects_service import SpellEffectsService
from talekeeper.services.concentration_system import ConcentrationSystem


def roll_dice(num_dice: int, die_size: int) -> int:
    return sum(random.randint(1, die_size) for _ in range(num_dice))


class SpellHandler(ABC):
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.effects = SpellEffectsService(db_path)
        self.concentration = ConcentrationSystem(db_path)

    @abstractmethod
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def can_cast(self, caster_id: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        return True, ""

    def on_turn_start(self, character_id: str) -> Optional[Dict[str, Any]]:
        return None

    def on_turn_end(self, character_id: str) -> Optional[Dict[str, Any]]:
        return None

    def _get_ability_mod(self, character_id: str, ability: str) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(f"""
                    SELECT {ability}
                    FROM characters
                    WHERE id = ?
                """, (character_id,))

                result = cursor.fetchone()
                if result:
                    ability_score = result[0]
                    return (ability_score - 10) // 2

        except Exception as e:
            print(f"Error getting ability mod: {e}")

        return 0

    def _get_spell_save_dc(self, caster_id: str) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT spell_save_dc
                    FROM character_spellcasting
                    WHERE character_id = ?
                """, (caster_id,))

                result = cursor.fetchone()
                if result:
                    return result[0]

        except Exception as e:
            print(f"Error getting spell save DC: {e}")

        return 10

    def _make_save(self, target_id: str, save_ability: str, dc: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(f"""
                    SELECT {save_ability}
                    FROM characters
                    WHERE id = ?
                """, (target_id,))

                result = cursor.fetchone()
                if result:
                    ability_score = result[0]
                    ability_mod = (ability_score - 10) // 2
                    roll = random.randint(1, 20)
                    total = roll + ability_mod

                    return total >= dc

        except Exception as e:
            print(f"Error making save: {e}")

        return False


class SpellHandlerRegistry:
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.handlers: Dict[str, SpellHandler] = {}

    def register(self, spell_id: str, handler: SpellHandler):
        self.handlers[spell_id] = handler

    def get_handler(self, spell_id: str) -> Optional[SpellHandler]:
        return self.handlers.get(spell_id)

    def execute_spell(self, spell_id: str, caster_id: str, targets: List[str],
                      slot_level: int, context: Dict[str, Any]) -> Dict[str, Any]:
        handler = self.get_handler(spell_id)

        if not handler:
            return {
                'success': False,
                'reason': f'No handler registered for spell: {spell_id}'
            }

        can_cast, reason = handler.can_cast(caster_id, context)
        if not can_cast:
            return {
                'success': False,
                'reason': reason
            }

        return handler.execute(caster_id, targets, slot_level, context)

    def process_turn_start_effects(self, character_id: str) -> List[Dict[str, Any]]:
        effects = []

        for spell_id, handler in self.handlers.items():
            result = handler.on_turn_start(character_id)
            if result:
                effects.append({
                    'spell_id': spell_id,
                    **result
                })

        return effects

    def process_turn_end_effects(self, character_id: str) -> List[Dict[str, Any]]:
        effects = []

        for spell_id, handler in self.handlers.items():
            result = handler.on_turn_end(character_id)
            if result:
                effects.append({
                    'spell_id': spell_id,
                    **result
                })

        return effects
