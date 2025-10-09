import sqlite3
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class SpellSlotProgression:
    level: int
    slots_1: int = 0
    slots_2: int = 0
    slots_3: int = 0
    slots_4: int = 0
    slots_5: int = 0
    slots_6: int = 0
    slots_7: int = 0
    slots_8: int = 0
    slots_9: int = 0
    cantrips_known: int = 0
    spells_prepared_formula: Optional[str] = None


@dataclass
class PactMagicProgression:
    level: int
    pact_slots: int
    pact_slot_level: int
    cantrips_known: int
    spells_known: int
    invocations_known: int


class SpellcastingProgressionService:

    FULL_CASTER_PROGRESSION = {
        1: SpellSlotProgression(1, 2, 0, 0, 0, 0, 0, 0, 0, 0),
        2: SpellSlotProgression(2, 3, 0, 0, 0, 0, 0, 0, 0, 0),
        3: SpellSlotProgression(3, 4, 2, 0, 0, 0, 0, 0, 0, 0),
        4: SpellSlotProgression(4, 4, 3, 0, 0, 0, 0, 0, 0, 0),
        5: SpellSlotProgression(5, 4, 3, 2, 0, 0, 0, 0, 0, 0),
        6: SpellSlotProgression(6, 4, 3, 3, 0, 0, 0, 0, 0, 0),
        7: SpellSlotProgression(7, 4, 3, 3, 1, 0, 0, 0, 0, 0),
        8: SpellSlotProgression(8, 4, 3, 3, 2, 0, 0, 0, 0, 0),
        9: SpellSlotProgression(9, 4, 3, 3, 3, 1, 0, 0, 0, 0),
        10: SpellSlotProgression(10, 4, 3, 3, 3, 2, 0, 0, 0, 0),
        11: SpellSlotProgression(11, 4, 3, 3, 3, 2, 1, 0, 0, 0),
        12: SpellSlotProgression(12, 4, 3, 3, 3, 2, 1, 0, 0, 0),
        13: SpellSlotProgression(13, 4, 3, 3, 3, 2, 1, 1, 0, 0),
        14: SpellSlotProgression(14, 4, 3, 3, 3, 2, 1, 1, 0, 0),
        15: SpellSlotProgression(15, 4, 3, 3, 3, 2, 1, 1, 1, 0),
        16: SpellSlotProgression(16, 4, 3, 3, 3, 2, 1, 1, 1, 0),
        17: SpellSlotProgression(17, 4, 3, 3, 3, 2, 1, 1, 1, 1),
        18: SpellSlotProgression(18, 4, 3, 3, 3, 3, 1, 1, 1, 1),
        19: SpellSlotProgression(19, 4, 3, 3, 3, 3, 2, 1, 1, 1),
        20: SpellSlotProgression(20, 4, 3, 3, 3, 3, 2, 2, 1, 1),
    }

    HALF_CASTER_PROGRESSION = {
        1: SpellSlotProgression(1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        2: SpellSlotProgression(2, 2, 0, 0, 0, 0, 0, 0, 0, 0),
        3: SpellSlotProgression(3, 3, 0, 0, 0, 0, 0, 0, 0, 0),
        4: SpellSlotProgression(4, 3, 0, 0, 0, 0, 0, 0, 0, 0),
        5: SpellSlotProgression(5, 4, 2, 0, 0, 0, 0, 0, 0, 0),
        6: SpellSlotProgression(6, 4, 2, 0, 0, 0, 0, 0, 0, 0),
        7: SpellSlotProgression(7, 4, 3, 0, 0, 0, 0, 0, 0, 0),
        8: SpellSlotProgression(8, 4, 3, 0, 0, 0, 0, 0, 0, 0),
        9: SpellSlotProgression(9, 4, 3, 2, 0, 0, 0, 0, 0, 0),
        10: SpellSlotProgression(10, 4, 3, 2, 0, 0, 0, 0, 0, 0),
        11: SpellSlotProgression(11, 4, 3, 3, 0, 0, 0, 0, 0, 0),
        12: SpellSlotProgression(12, 4, 3, 3, 0, 0, 0, 0, 0, 0),
        13: SpellSlotProgression(13, 4, 3, 3, 1, 0, 0, 0, 0, 0),
        14: SpellSlotProgression(14, 4, 3, 3, 1, 0, 0, 0, 0, 0),
        15: SpellSlotProgression(15, 4, 3, 3, 2, 0, 0, 0, 0, 0),
        16: SpellSlotProgression(16, 4, 3, 3, 2, 0, 0, 0, 0, 0),
        17: SpellSlotProgression(17, 4, 3, 3, 3, 1, 0, 0, 0, 0),
        18: SpellSlotProgression(18, 4, 3, 3, 3, 1, 0, 0, 0, 0),
        19: SpellSlotProgression(19, 4, 3, 3, 3, 2, 0, 0, 0, 0),
        20: SpellSlotProgression(20, 4, 3, 3, 3, 2, 0, 0, 0, 0),
    }

    PALADIN_PROGRESSION_2024 = {
        1: SpellSlotProgression(1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        2: SpellSlotProgression(2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        3: SpellSlotProgression(3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        4: SpellSlotProgression(4, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        5: SpellSlotProgression(5, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        6: SpellSlotProgression(6, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        7: SpellSlotProgression(7, 4, 3, 0, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        8: SpellSlotProgression(8, 4, 3, 0, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        9: SpellSlotProgression(9, 4, 3, 2, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        10: SpellSlotProgression(10, 4, 3, 2, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        11: SpellSlotProgression(11, 4, 3, 3, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        12: SpellSlotProgression(12, 4, 3, 3, 0, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        13: SpellSlotProgression(13, 4, 3, 3, 1, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        14: SpellSlotProgression(14, 4, 3, 3, 1, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        15: SpellSlotProgression(15, 4, 3, 3, 2, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        16: SpellSlotProgression(16, 4, 3, 3, 2, 0, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        17: SpellSlotProgression(17, 4, 3, 3, 3, 1, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        18: SpellSlotProgression(18, 4, 3, 3, 3, 1, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        19: SpellSlotProgression(19, 4, 3, 3, 3, 2, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
        20: SpellSlotProgression(20, 4, 3, 3, 3, 2, 0, 0, 0, 0, 0, 'charisma_mod + half_level'),
    }

    PACT_MAGIC_PROGRESSION = {
        1: PactMagicProgression(1, 1, 1, 2, 2, 0),
        2: PactMagicProgression(2, 2, 1, 2, 3, 2),
        3: PactMagicProgression(3, 2, 2, 2, 4, 2),
        4: PactMagicProgression(4, 2, 2, 3, 5, 2),
        5: PactMagicProgression(5, 2, 3, 3, 6, 3),
        6: PactMagicProgression(6, 2, 3, 3, 7, 3),
        7: PactMagicProgression(7, 2, 4, 3, 8, 4),
        8: PactMagicProgression(8, 2, 4, 3, 9, 4),
        9: PactMagicProgression(9, 2, 5, 3, 10, 5),
        10: PactMagicProgression(10, 2, 5, 4, 11, 5),
        11: PactMagicProgression(11, 3, 5, 4, 12, 5),
        12: PactMagicProgression(12, 3, 5, 4, 12, 6),
        13: PactMagicProgression(13, 3, 5, 4, 13, 6),
        14: PactMagicProgression(14, 3, 5, 4, 13, 6),
        15: PactMagicProgression(15, 3, 5, 4, 14, 7),
        16: PactMagicProgression(16, 3, 5, 4, 14, 7),
        17: PactMagicProgression(17, 4, 5, 4, 15, 7),
        18: PactMagicProgression(18, 4, 5, 4, 15, 8),
        19: PactMagicProgression(19, 4, 5, 4, 15, 8),
        20: PactMagicProgression(20, 4, 5, 4, 15, 8),
    }

    CANTRIP_PROGRESSION = {
        'wizard': {1: 3, 4: 4, 10: 5},
        'cleric': {1: 3, 4: 4, 10: 5},
        'druid': {1: 2, 4: 3, 10: 4},
        'bard': {1: 2, 4: 3, 10: 4},
        'sorcerer': {1: 4, 4: 5, 10: 6},
        'warlock': {1: 2, 4: 3, 10: 4},
    }

    CLASS_CASTING_TYPE = {
        'wizard': 'full',
        'cleric': 'full',
        'druid': 'full',
        'bard': 'full',
        'sorcerer': 'full',
        'warlock': 'pact',
        'paladin': 'paladin_2024',
        'ranger': 'half',
    }

    PREPARED_SPELLS_BY_LEVEL = {
        'bard': {1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15, 11: 16, 12: 16, 13: 17, 14: 17, 15: 18, 16: 18, 17: 19, 18: 20, 19: 21, 20: 22},
        'cleric': {1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15, 11: 16, 12: 16, 13: 17, 14: 18, 15: 19, 16: 21, 17: 22, 18: 23, 19: 24, 20: 25},
        'druid': {1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15, 11: 16, 12: 16, 13: 17, 14: 18, 15: 19, 16: 21, 17: 22, 18: 23, 19: 24, 20: 25},
        'paladin': {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 6, 7: 7, 8: 7, 9: 9, 10: 9, 11: 10, 12: 10, 13: 11, 14: 11, 15: 12, 16: 12, 17: 14, 18: 14, 19: 15, 20: 15},
        'ranger': {2: 3, 3: 4, 4: 5, 5: 6, 6: 6, 7: 7, 8: 7, 9: 9, 10: 9, 11: 10, 12: 10, 13: 11, 14: 11, 15: 12, 16: 12, 17: 14, 18: 14, 19: 15, 20: 15},
        'sorcerer': {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 12, 12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 17: 15, 18: 15, 19: 15, 20: 15},
        'warlock': {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 12, 12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 17: 15, 18: 15, 19: 15, 20: 15},
        'wizard': {1: 5, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15, 11: 16, 12: 16, 13: 17, 14: 18, 15: 19, 16: 21, 17: 22, 18: 23, 19: 24, 20: 25},
    }

    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path

    def update_spellcasting_on_level_up(self, character_id: str, new_level: int, class_id: str) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT charisma, wisdom, intelligence
                FROM characters WHERE id = ?
            """, (character_id,))

            char_data = cursor.fetchone()
            if not char_data:
                return {'success': False, 'error': 'Character not found'}

            charisma, wisdom, intelligence = char_data

            casting_type = self.CLASS_CASTING_TYPE.get(class_id)
            if not casting_type:
                return {'success': False, 'message': f'{class_id} is not a spellcaster'}

            result = {
                'success': True,
                'spell_slots_updated': False,
                'cantrips_updated': False,
                'pact_slots_updated': False,
                'new_cantrips': 0,
                'prepared_spell_count': 0
            }

            if casting_type == 'pact':
                pact_prog = self.PACT_MAGIC_PROGRESSION.get(new_level)
                if pact_prog:
                    cursor.execute("""
                        UPDATE warlock_features
                        SET pact_slots_max = ?, pact_slots_current = ?, pact_slot_level = ?
                        WHERE character_id = ?
                    """, (pact_prog.pact_slots, pact_prog.pact_slots, pact_prog.pact_slot_level, character_id))

                    cursor.execute("""
                        UPDATE character_spellcasting
                        SET cantrips_known = ?
                        WHERE character_id = ? AND spellcasting_class = 'warlock'
                    """, (pact_prog.cantrips_known, character_id))

                    result['pact_slots_updated'] = True
                    result['new_cantrips'] = pact_prog.cantrips_known

            elif casting_type == 'paladin_2024':
                prog = self.PALADIN_PROGRESSION_2024.get(new_level)
                if prog:
                    self._update_spell_slots(cursor, character_id, 'paladin', prog)
                    result['spell_slots_updated'] = True

                    prepared_count = self.PREPARED_SPELLS_BY_LEVEL.get('paladin', {}).get(new_level, 0)
                    result['prepared_spell_count'] = prepared_count

            elif casting_type in ['full', 'half']:
                progression_table = self.FULL_CASTER_PROGRESSION if casting_type == 'full' else self.HALF_CASTER_PROGRESSION
                prog = progression_table.get(new_level)

                if prog:
                    self._update_spell_slots(cursor, character_id, class_id, prog)
                    result['spell_slots_updated'] = True

            cantrip_prog = self.CANTRIP_PROGRESSION.get(class_id, {})
            if new_level in cantrip_prog:
                new_cantrips = cantrip_prog[new_level]
                cursor.execute("""
                    UPDATE character_spellcasting
                    SET cantrips_known = ?
                    WHERE character_id = ? AND spellcasting_class = ?
                """, (new_cantrips, character_id, class_id))
                result['cantrips_updated'] = True
                result['new_cantrips'] = new_cantrips

            if class_id in self.PREPARED_SPELLS_BY_LEVEL:
                prepared_count = self.PREPARED_SPELLS_BY_LEVEL[class_id].get(new_level, 0)
                result['prepared_spell_count'] = prepared_count

            conn.commit()
            return result

    def _update_spell_slots(self, cursor, character_id: str, class_id: str, prog: SpellSlotProgression):
        cursor.execute("""
            DELETE FROM character_spell_slots WHERE character_id = ?
        """, (character_id,))

        for spell_level in range(1, 10):
            slots = getattr(prog, f'slots_{spell_level}', 0)
            if slots > 0:
                cursor.execute("""
                    INSERT INTO character_spell_slots
                    (character_id, spell_level, max_slots, used_slots, slot_type)
                    VALUES (?, ?, ?, 0, 'normal')
                """, (character_id, spell_level, slots))

    def get_spells_that_can_be_prepared(self, character_id: str, class_id: str, new_level: int) -> int:
        if class_id in self.PREPARED_SPELLS_BY_LEVEL:
            return self.PREPARED_SPELLS_BY_LEVEL[class_id].get(new_level, 0)
        return 0
