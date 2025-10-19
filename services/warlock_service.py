# core
# core
import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from .warlock_patrons import get_patron_manager

class WarlockService:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
        self.pact_magic_service = PactMagicService(db_path)
        self.invocation_service = ElditchInvocationService(db_path)
        self.patron_manager = get_patron_manager(db_path)

    def initialize_warlock_features(self, character_id: str, level: int = 1, patron: str = 'Fiend'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get pact progression for level
            cursor.execute("""
                SELECT num_slots, slot_level, invocations_known, cantrips_known, spells_known
                FROM warlock_pact_progression
                WHERE level = ?
            """, (level,))
            progression = cursor.fetchone()

            if not progression:
                progression = (1, 1, 0, 2, 2)  # Level 1 defaults

            num_slots, slot_level, invocations_known, cantrips_known, spells_known = progression

            # Initialize warlock features
            cursor.execute("""
                INSERT OR REPLACE INTO warlock_features
                (character_id, level, patron, pact_boon, invocations_known, mystic_arcanum_spells,
                 last_pact_reset, pact_slots, pact_slot_level, pact_slots_current, pact_slots_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (character_id, level, patron, None, '[]', '[]',
                  datetime.now().isoformat(), num_slots, slot_level, num_slots, num_slots))

            # Initialize spellcasting if needed
            cursor.execute("""
                INSERT OR IGNORE INTO character_spellcasting
                (character_id, spellcasting_class, spellcasting_ability,
                 spell_save_dc, spell_attack_bonus, prepared_spells, known_spells,
                 cantrips_known, ritual_casting, spellcasting_focus)
                VALUES (?, 'warlock', 'Charisma', 0, 0, '[]', '[]', ?, 0, 'arcane_focus')
            """, (character_id, cantrips_known))

            conn.commit()

    def select_pact_boon(self, character_id: str, pact_boon: str) -> bool:
        valid_pacts = ['blade', 'chain', 'tome']
        if pact_boon.lower() not in valid_pacts:
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE warlock_features
                SET pact_boon = ?
                WHERE character_id = ?
            """, (pact_boon.lower(), character_id))

            # Grant pact-specific benefits
            if pact_boon.lower() == 'blade':
                self._grant_pact_weapon(character_id)
            elif pact_boon.lower() == 'chain':
                self._grant_find_familiar(character_id)
            elif pact_boon.lower() == 'tome':
                self._grant_book_of_shadows(character_id)

            conn.commit()
            return True

    def _grant_pact_weapon(self, character_id: str):
        # Create a pact weapon that can be summoned
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source)
                VALUES (?, 'pact_weapon', 'warlock_pact')
            """, (character_id,))
            conn.commit()

    def _grant_find_familiar(self, character_id: str):
        # Grant enhanced find familiar spell
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source)
                VALUES (?, 'pact_familiar', 'warlock_pact')
            """, (character_id,))
            conn.commit()

    def _grant_book_of_shadows(self, character_id: str):
        # Grant 3 additional cantrips from any class
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_spellcasting
                SET cantrips_known = cantrips_known + 3
                WHERE character_id = ? AND spellcasting_class = 'warlock'
            """, (character_id,))
            conn.commit()

    def get_warlock_features(self, character_id: str) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT patron, pact_boon, invocations_known, mystic_arcanum_spells,
                       last_pact_reset, pact_slots_current, pact_slots_max, pact_slot_level
                FROM warlock_features
                WHERE character_id = ?
            """, (character_id,))

            result = cursor.fetchone()
            if not result:
                return {}

            return {
                'patron': result[0],
                'pact_boon': result[1],
                'invocations': json.loads(result[2]) if result[2] else [],
                'mystic_arcanum': json.loads(result[3]) if result[3] else [],
                'last_pact_reset': result[4],
                'pact_slots_current': result[5],
                'pact_slots_max': result[6],
                'pact_slot_level': result[7]
            }

    def level_up_warlock(self, character_id: str, new_level: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get new progression values
            cursor.execute("""
                SELECT num_slots, slot_level, invocations_known, cantrips_known, spells_known
                FROM warlock_pact_progression
                WHERE level = ?
            """, (new_level,))
            progression = cursor.fetchone()

            if progression:
                num_slots, slot_level, invocations_known, cantrips_known, spells_known = progression

                # Update pact slots
                cursor.execute("""
                    UPDATE warlock_features
                    SET pact_slots_max = ?, pact_slots_current = ?, pact_slot_level = ?
                    WHERE character_id = ?
                """, (num_slots, num_slots, slot_level, character_id))

                # Update cantrips and spells known
                cursor.execute("""
                    UPDATE character_spellcasting
                    SET cantrips_known = ?
                    WHERE character_id = ? AND spellcasting_class = 'warlock'
                """, (cantrips_known, character_id))

                # Check for Mystic Arcanum
                if new_level >= 11:
                    self._grant_mystic_arcanum(character_id, new_level)

                # Check for Eldritch Master at level 20
                if new_level == 20:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source)
                        VALUES (?, 'eldritch_master', 'warlock')
                    """, (character_id,))

                conn.commit()

    def _grant_mystic_arcanum(self, character_id: str, level: int):
        # Grant appropriate level Mystic Arcanum slots
        arcanum_levels = {
            11: 6,  # 6th level spell
            13: 7,  # 7th level spell
            15: 8,  # 8th level spell
            17: 9   # 9th level spell
        }

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for req_level, spell_level in arcanum_levels.items():
                if level >= req_level:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source)
                        VALUES (?, ?, 'warlock')
                    """, (character_id, f'mystic_arcanum_{spell_level}'))
            conn.commit()


class PactMagicService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_pact_slots(self, character_id: str) -> Tuple[int, int]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pact_slots_current, pact_slot_level
                FROM warlock_features
                WHERE character_id = ?
            """, (character_id,))

            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            return 0, 0

    def use_pact_slot(self, character_id: str) -> bool:
        current_slots, slot_level = self.get_pact_slots(character_id)

        if current_slots <= 0:
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE warlock_features
                SET pact_slots_current = pact_slots_current - 1
                WHERE character_id = ?
            """, (character_id,))
            conn.commit()
            return True

    def short_rest_recovery(self, character_id: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get character level
            cursor.execute("""
                SELECT level FROM characters WHERE id = ?
            """, (character_id,))
            level_result = cursor.fetchone()
            level = level_result[0] if level_result else 1

            # Get max slots for level
            cursor.execute("""
                SELECT num_slots FROM warlock_pact_progression WHERE level = ?
            """, (level,))
            max_slots_result = cursor.fetchone()
            max_slots = max_slots_result[0] if max_slots_result else 1

            # Restore all pact slots
            cursor.execute("""
                UPDATE warlock_features
                SET pact_slots_current = ?, pact_slots_max = ?, last_pact_reset = ?
                WHERE character_id = ?
            """, (max_slots, max_slots, datetime.now().isoformat(), character_id))
            conn.commit()

            return max_slots

    def eldritch_master_recovery(self, character_id: str) -> bool:
        # Level 20 feature: Regain all pact slots with 1 minute rest
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Verify character is level 20 warlock
            cursor.execute("""
                SELECT c.level
                FROM characters c
                JOIN warlock_features wf ON c.id = wf.character_id
                WHERE c.id = ? AND c.level >= 20
            """, (character_id,))

            if not cursor.fetchone():
                return False

            # Restore slots
            cursor.execute("""
                UPDATE warlock_features
                SET pact_slots_current = 4, last_pact_reset = ?
                WHERE character_id = ?
            """, (datetime.now().isoformat(), character_id))
            conn.commit()
            return True

    def can_cast_spell_with_pact_slot(self, character_id: str, spell_level: int) -> bool:
        current_slots, slot_level = self.get_pact_slots(character_id)

        # Can upcast spells to pact slot level
        return current_slots > 0 and spell_level <= slot_level


class ElditchInvocationService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_available_invocations(self, character_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get character level and pact
            cursor.execute("""
                SELECT c.level, wf.pact_boon
                FROM characters c
                JOIN warlock_features wf ON c.id = wf.character_id
                WHERE c.id = ?
            """, (character_id,))

            result = cursor.fetchone()
            if not result:
                return []

            level, pact_boon = result

            # Get all invocations
            cursor.execute("""
                SELECT id, name, description, prerequisites
                FROM invocations
            """)

            available = []
            for inv in cursor.fetchall():
                inv_id, name, desc, prereq_str = inv
                prereqs = json.loads(prereq_str) if prereq_str else {}

                # Check prerequisites
                if self._meets_prerequisites(level, pact_boon, prereqs, character_id):
                    available.append({
                        'id': inv_id,
                        'name': name,
                        'description': desc
                    })

            return available

    def _meets_prerequisites(self, level: int, pact_boon: str, prereqs: Dict, character_id: str) -> bool:
        # Check level requirement
        if 'level' in prereqs and level < prereqs['level']:
            return False

        # Check pact requirement
        if 'pact' in prereqs and pact_boon != prereqs['pact']:
            return False

        # Check cantrip requirement
        if 'cantrip' in prereqs:
            if not self._has_cantrip(character_id, prereqs['cantrip']):
                return False

        # Check spell requirement
        if 'spell' in prereqs:
            if not self._knows_spell(character_id, prereqs['spell']):
                return False

        return True

    def _has_cantrip(self, character_id: str, cantrip: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT known_spells FROM character_spellcasting
                WHERE character_id = ? AND spellcasting_class = 'warlock'
            """, (character_id,))

            result = cursor.fetchone()
            if result and result[0]:
                known = json.loads(result[0])
                return cantrip in known.get('0', [])  # Cantrips are level 0
            return False

    def _knows_spell(self, character_id: str, spell_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT known_spells FROM character_spellcasting
                WHERE character_id = ? AND spellcasting_class = 'warlock'
            """, (character_id,))

            result = cursor.fetchone()
            if result and result[0]:
                known = json.loads(result[0])
                for level_spells in known.values():
                    if spell_id in level_spells:
                        return True
            return False

    def learn_invocation(self, character_id: str, invocation_id: str) -> bool:
        available = self.get_available_invocations(character_id)
        if not any(inv['id'] == invocation_id for inv in available):
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get current level
            cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
            level = cursor.fetchone()[0]

            # Add invocation
            cursor.execute("""
                INSERT OR IGNORE INTO warlock_invocations (character_id, invocation_id, learned_at_level)
                VALUES (?, ?, ?)
            """, (character_id, invocation_id, level))

            # Update invocations known list
            cursor.execute("""
                SELECT invocations_known FROM warlock_features WHERE character_id = ?
            """, (character_id,))

            current = cursor.fetchone()[0]
            invocations = json.loads(current) if current else []
            if invocation_id not in invocations:
                invocations.append(invocation_id)

            cursor.execute("""
                UPDATE warlock_features
                SET invocations_known = ?
                WHERE character_id = ?
            """, (json.dumps(invocations), character_id))

            # Apply invocation effects
            self._apply_invocation_effects(character_id, invocation_id)

            conn.commit()
            return True

    def _apply_invocation_effects(self, character_id: str, invocation_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT effect_type, effect_data
                FROM invocations
                WHERE id = ?
            """, (invocation_id,))

            result = cursor.fetchone()
            if not result:
                return

            effect_type, effect_data = result
            effects = json.loads(effect_data) if effect_data else {}

            if effect_type == 'passive':
                # Apply passive bonuses
                if 'skills' in effects:
                    for skill in effects['skills']:
                        cursor.execute("""
                            INSERT OR IGNORE INTO character_skills (character_id, skill_name, proficient, expertise)
                            VALUES (?, ?, 1, 0)
                        """, (character_id, skill))

                if 'darkvision' in effects:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source)
                        VALUES (?, ?, 'invocation')
                    """, (character_id, f'darkvision_{effects["darkvision"]}'))

            elif effect_type == 'active':
                # Record at-will spells
                if 'spell' in effects and effects.get('cost') == 'none':
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source)
                        VALUES (?, ?, 'invocation')
                    """, (character_id, f'at_will_{effects["spell"]}'))

            conn.commit()

    def get_character_invocations(self, character_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.id, i.name, i.description, i.effect_type, i.effect_data, wi.learned_at_level
                FROM warlock_invocations wi
                JOIN invocations i ON wi.invocation_id = i.id
                WHERE wi.character_id = ?
            """, (character_id,))

            invocations = []
            for row in cursor.fetchall():
                invocations.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'effect_type': row[3],
                    'effect_data': json.loads(row[4]) if row[4] else {},
                    'learned_at_level': row[5]
                })

            return invocations


class FiendPatronService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def apply_fiend_features(self, character_id: str, level: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Level 1: Dark One's Blessing
            if level >= 1:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source)
                    VALUES (?, 'dark_ones_blessing', 'warlock_patron')
                """, (character_id,))

                # Add expanded spell list
                self._add_expanded_spells(character_id, 'fiend')

            # Level 6: Dark One's Own Luck
            if level >= 6:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source)
                    VALUES (?, 'dark_ones_own_luck', 'warlock_patron')
                """, (character_id,))

            # Level 10: Fiendish Resilience
            if level >= 10:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source)
                    VALUES (?, 'fiendish_resilience', 'warlock_patron')
                """, (character_id,))

            # Level 14: Hurl Through Hell
            if level >= 14:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source)
                    VALUES (?, 'hurl_through_hell', 'warlock_patron')
                """, (character_id,))

            conn.commit()

    def _add_expanded_spells(self, character_id: str, patron: str):
        # Fiend expanded spell list
        fiend_spells = {
            1: ['burning_hands', 'command'],
            2: ['blindness_deafness', 'scorching_ray'],
            3: ['fireball', 'stinking_cloud'],
            4: ['fire_shield', 'wall_of_fire'],
            5: ['flame_strike', 'hallow']
        }

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Add to available spells (not automatically known)
            cursor.execute("""
                INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                VALUES (?, 'expanded_spell_list', 'warlock_patron', ?)
            """, (character_id, json.dumps(fiend_spells)))

            conn.commit()

    def dark_ones_blessing(self, character_id: str, creature_killed_cr: float) -> int:
        # When you reduce a hostile creature to 0 HP, gain temp HP
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get character level and Charisma modifier
            cursor.execute("""
                SELECT c.level, c.charisma
                FROM characters c
                WHERE c.id = ?
            """, (character_id,))

            result = cursor.fetchone()
            if not result:
                return 0

            level, charisma = result
            cha_mod = (charisma - 10) // 2

            # Temp HP = Charisma modifier + warlock level (minimum 1)
            temp_hp = max(1, cha_mod + level)

            # Apply temporary hit points
            cursor.execute("""
                UPDATE characters
                SET temp_hp = CASE
                    WHEN temp_hp > ? THEN temp_hp
                    ELSE ?
                END
                WHERE id = ?
            """, (temp_hp, temp_hp, character_id))

            conn.commit()
            return temp_hp

    def dark_ones_own_luck(self, character_id: str, roll_type: str) -> bool:
        # Once per short/long rest, add 1d10 to ability check or save
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if already used
            cursor.execute("""
                SELECT feature_data FROM character_features
                WHERE character_id = ? AND feature_id = 'dark_ones_own_luck'
            """, (character_id,))

            result = cursor.fetchone()
            if result and result[0]:
                data = json.loads(result[0])
                if data.get('used', False):
                    return False

            # Mark as used
            cursor.execute("""
                UPDATE character_features
                SET feature_data = ?
                WHERE character_id = ? AND feature_id = 'dark_ones_own_luck'
            """, (json.dumps({'used': True}), character_id))

            conn.commit()
            return True

    def fiendish_resilience(self, character_id: str, damage_type: str) -> bool:
        # Choose resistance to one damage type at end of short/long rest
        valid_types = ['acid', 'cold', 'fire', 'lightning', 'necrotic', 'poison', 'radiant', 'thunder']

        if damage_type not in valid_types:
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_features
                SET feature_data = ?
                WHERE character_id = ? AND feature_id = 'fiendish_resilience'
            """, (json.dumps({'resistance': damage_type}), character_id))

            conn.commit()
            return True

    def hurl_through_hell(self, character_id: str, target_id: str) -> Dict[str, Any]:
        # Once per long rest, when you hit with an attack, send target through hell
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if already used
            cursor.execute("""
                SELECT feature_data FROM character_features
                WHERE character_id = ? AND feature_id = 'hurl_through_hell'
            """, (character_id,))

            result = cursor.fetchone()
            if result and result[0]:
                data = json.loads(result[0])
                if data.get('used', False):
                    return {'success': False, 'reason': 'Already used'}

            # Mark as used
            cursor.execute("""
                UPDATE character_features
                SET feature_data = ?
                WHERE character_id = ? AND feature_id = 'hurl_through_hell'
            """, (json.dumps({'used': True}), character_id))

            conn.commit()

            return {
                'success': True,
                'damage': 10 * 6,  # 10d10 psychic damage
                'damage_type': 'psychic',
                'effect': 'Target disappears and reappears at end of your next turn'
            }