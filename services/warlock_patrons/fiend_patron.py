# core
# core
import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime


class FiendPatron:
    """Fiend Patron implementation for Warlock characters."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.patron_name = "Fiend"

    def get_expanded_spells(self) -> Dict[int, List[str]]:
        """Get the expanded spell list for Fiend patron."""
        return {
            1: ["burning_hands", "command"],
            2: ["blindness_deafness", "scorching_ray"],
            3: ["fireball", "stinking_cloud"],
            4: ["fire_shield", "wall_of_fire"],
            5: ["flame_strike", "hallow"]
        }

    def initialize_patron_features(self, character_id: str, level: int):
        """Initialize all Fiend patron features for the given level."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Level 1: Dark One's Blessing
            if level >= 1:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'dark_ones_blessing', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': "Dark One's Blessing",
                    'description': "When you reduce a hostile creature to 0 hit points, you gain temporary hit points equal to your Charisma modifier + your warlock level (minimum of 1).",
                    'usage': 'passive'
                })))

                # Add expanded spells
                expanded_spells = self.get_expanded_spells()
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'fiend_expanded_spells', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': 'Fiend Expanded Spells',
                    'description': 'The Fiend lets you choose from an expanded list of spells when you learn a warlock spell.',
                    'spells': expanded_spells
                })))

            # Level 6: Dark One's Own Luck
            if level >= 6:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'dark_ones_own_luck', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': "Dark One's Own Luck",
                    'description': "You can call on your patron to alter fate in your favor. When you make an ability check or a saving throw, you can use this feature to add a d10 to your roll. You can do so after seeing the initial roll but before any of the roll's effects occur.",
                    'usage': 'short_rest',
                    'uses_max': 1,
                    'uses_current': 1
                })))

            # Level 10: Fiendish Resilience
            if level >= 10:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'fiendish_resilience', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': 'Fiendish Resilience',
                    'description': 'You can choose one damage type when you finish a short or long rest. You gain resistance to that damage type until you choose a different one with this feature.',
                    'usage': 'rest_choice',
                    'current_resistance': None,
                    'available_types': ['acid', 'cold', 'fire', 'lightning', 'necrotic', 'poison', 'radiant', 'thunder']
                })))

            # Level 14: Hurl Through Hell
            if level >= 14:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'hurl_through_hell', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': 'Hurl Through Hell',
                    'description': 'When you hit a creature with an attack, you can use this feature to instantly transport the target through the lower planes. The creature disappears and hurtles through a nightmare landscape.',
                    'usage': 'long_rest',
                    'uses_max': 1,
                    'uses_current': 1,
                    'damage': '10d10',
                    'damage_type': 'psychic'
                })))

            conn.commit()

    def dark_ones_blessing(self, character_id: str, target_cr: float = 1.0) -> int:
        """Apply Dark One's Blessing when a creature is reduced to 0 HP."""
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
            cha_mod = max(0, (charisma - 10) // 2)

            # Calculate temporary HP
            temp_hp = max(1, cha_mod + level)

            # Update character's temporary HP (take the higher value)
            cursor.execute("""
                UPDATE characters
                SET temp_hp = CASE
                    WHEN COALESCE(temp_hp, 0) > ? THEN temp_hp
                    ELSE ?
                END
                WHERE id = ?
            """, (temp_hp, temp_hp, character_id))

            conn.commit()
            return temp_hp

    def use_dark_ones_own_luck(self, character_id: str) -> bool:
        """Use Dark One's Own Luck ability."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if feature is available
            cursor.execute("""
                SELECT feature_data FROM character_features
                WHERE character_id = ? AND feature_id = 'dark_ones_own_luck'
            """, (character_id,))

            result = cursor.fetchone()
            if not result:
                return False

            feature_data = json.loads(result[0])
            if feature_data.get('uses_current', 0) <= 0:
                return False

            # Use the feature
            feature_data['uses_current'] = feature_data.get('uses_current', 1) - 1
            cursor.execute("""
                UPDATE character_features
                SET feature_data = ?
                WHERE character_id = ? AND feature_id = 'dark_ones_own_luck'
            """, (json.dumps(feature_data), character_id))

            conn.commit()
            return True

    def set_fiendish_resilience(self, character_id: str, damage_type: str) -> bool:
        """Set the damage type for Fiendish Resilience."""
        valid_types = ['acid', 'cold', 'fire', 'lightning', 'necrotic', 'poison', 'radiant', 'thunder']

        if damage_type not in valid_types:
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Update the resistance choice
            cursor.execute("""
                UPDATE character_features
                SET feature_data = json_set(feature_data, '$.current_resistance', ?)
                WHERE character_id = ? AND feature_id = 'fiendish_resilience'
            """, (damage_type, character_id))

            # Also update character resistances
            cursor.execute("""
                SELECT resistances FROM characters WHERE id = ?
            """, (character_id,))

            result = cursor.fetchone()
            current_resistances = json.loads(result[0]) if result and result[0] else []

            # Remove any previous fiendish resilience
            current_resistances = [r for r in current_resistances if not r.startswith('fiendish_')]

            # Add new resistance
            current_resistances.append(f'fiendish_{damage_type}')

            cursor.execute("""
                UPDATE characters
                SET resistances = ?
                WHERE id = ?
            """, (json.dumps(current_resistances), character_id))

            conn.commit()
            return True

    def use_hurl_through_hell(self, character_id: str, target_name: str = "target") -> Dict[str, Any]:
        """Use Hurl Through Hell ability."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if feature is available
            cursor.execute("""
                SELECT feature_data FROM character_features
                WHERE character_id = ? AND feature_id = 'hurl_through_hell'
            """, (character_id,))

            result = cursor.fetchone()
            if not result:
                return {'success': False, 'reason': 'Feature not available'}

            feature_data = json.loads(result[0])
            if feature_data.get('uses_current', 0) <= 0:
                return {'success': False, 'reason': 'No uses remaining'}

            # Use the feature
            feature_data['uses_current'] = feature_data.get('uses_current', 1) - 1
            cursor.execute("""
                UPDATE character_features
                SET feature_data = ?
                WHERE character_id = ? AND feature_id = 'hurl_through_hell'
            """, (json.dumps(feature_data), character_id))

            conn.commit()

            # Calculate damage (10d10 = average 55, but we'll use dice notation)
            return {
                'success': True,
                'target': target_name,
                'damage_dice': '10d10',
                'damage_type': 'psychic',
                'effect': f'{target_name} disappears and reappears at the end of your next turn',
                'description': f'{target_name} hurtles through a nightmare landscape of the lower planes'
            }

    def short_rest_recovery(self, character_id: str):
        """Recover features that refresh on short rest."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Restore Dark One's Own Luck
            cursor.execute("""
                UPDATE character_features
                SET feature_data = json_set(feature_data, '$.uses_current', json_extract(feature_data, '$.uses_max'))
                WHERE character_id = ? AND feature_id = 'dark_ones_own_luck'
                AND json_extract(feature_data, '$.usage') = 'short_rest'
            """, (character_id,))

            conn.commit()

    def long_rest_recovery(self, character_id: str):
        """Recover features that refresh on long rest."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Restore all long rest features
            cursor.execute("""
                UPDATE character_features
                SET feature_data = json_set(feature_data, '$.uses_current', json_extract(feature_data, '$.uses_max'))
                WHERE character_id = ? AND feature_source = 'warlock_patron'
                AND json_extract(feature_data, '$.usage') IN ('long_rest', 'short_rest')
            """, (character_id,))

            conn.commit()

    def get_patron_features(self, character_id: str) -> List[Dict[str, Any]]:
        """Get all patron features for this character."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT feature_id, feature_data FROM character_features
                WHERE character_id = ? AND feature_source = 'warlock_patron'
            """, (character_id,))

            features = []
            for row in cursor.fetchall():
                feature_id, feature_data = row
                data = json.loads(feature_data) if feature_data else {}
                features.append({
                    'id': feature_id,
                    'name': data.get('name', feature_id),
                    'description': data.get('description', ''),
                    'usage': data.get('usage', 'passive'),
                    'uses_current': data.get('uses_current'),
                    'uses_max': data.get('uses_max'),
                    'data': data
                })

            return features