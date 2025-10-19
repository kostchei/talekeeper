# core
# core
import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime


class SorcererKingPatron:
    """Sorcerer-King Patron implementation for Warlock characters."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.patron_name = "Sorcerer-King"

    def get_expanded_spells(self) -> Dict[int, List[str]]:
        """Get the expanded spell list for Sorcerer-King patron."""
        return {
            3: ["command", "compelled_duel", "hold_person", "mind_spike", "wrathful_smite"],
            5: ["fear", "sending"],
            7: ["compulsion", "staggering_smite"],
            9: ["dominate_person", "synaptic_static"]
        }

    def initialize_patron_features(self, character_id: str, level: int):
        """Initialize all Sorcerer-King patron features for the given level."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Level 3: Sorcerer-King Spells and Tyrant's Herald
            if level >= 3:
                # Sorcerer-King Spells with Psionic Casting
                expanded_spells = self.get_expanded_spells()
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'sorcerer_king_spells', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': 'Sorcerer-King Spells',
                    'description': 'The magic of your patron ensures you always have certain spells ready. You can cast these spells without Verbal or Material components (except consumed or costly materials).',
                    'spells': expanded_spells,
                    'psionic_casting': True
                })))

                # Tyrant's Herald - Intimidating Presence
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'intimidating_presence', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': 'Intimidating Presence',
                    'description': 'You gain proficiency in the Intimidation skill. You also have Expertise in Intimidation.',
                    'skill_proficiency': 'Intimidation',
                    'expertise': True
                })))

                # Tyrant's Herald - Voice of Tyranny
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'voice_of_tyranny', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': 'Voice of Tyranny',
                    'description': 'You can cast Command as a Bonus Action without expending a spell slot. You can do so a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.',
                    'usage': 'long_rest',
                    'uses_max': 'charisma_mod',
                    'uses_current': 'charisma_mod',
                    'spell': 'command',
                    'action_type': 'bonus_action'
                })))

            # Level 6: Decisive Edict
            if level >= 6:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'decisive_edict', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': 'Decisive Edict',
                    'description': 'When you cast a spell using a Pact Magic spell slot, you can cause profane power to erupt in a 30-foot Emanation originating from you. For each creature you can see in the Emanation, choose Marshal (Advantage on attack rolls until end of next turn) or Oppress (Frightened condition until end of next turn on failed Wisdom save).',
                    'usage': 'short_rest',
                    'uses_max': 1,
                    'uses_current': 1,
                    'area': '30-foot emanation',
                    'effects': ['marshal', 'oppress']
                })))

            # Level 10: Vindictive Rebuke
            if level >= 10:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'vindictive_rebuke', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': 'Vindictive Rebuke',
                    'description': 'When an enemy hits you with an attack roll, you can take a Reaction to force the enemy to reroll the d20, and the enemy must use the new roll. If this Reaction turns the attack roll into a miss, the triggering creature takes Psychic damage equal to your Warlock level.',
                    'usage': 'long_rest',
                    'uses_max': 'charisma_mod',
                    'uses_current': 'charisma_mod',
                    'damage_type': 'psychic',
                    'action_type': 'reaction'
                })))

            # Level 14: Absolute Tyranny
            if level >= 14:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features (character_id, feature_id, feature_source, feature_data)
                    VALUES (?, 'absolute_tyranny', 'warlock_patron', ?)
                """, (character_id, json.dumps({
                    'name': 'Absolute Tyranny',
                    'description': 'Whenever you cast Command, you can target one additional creature within the spell\'s range. Additionally, a creature Frightened by you automatically fails its save against any Command you cast.',
                    'usage': 'passive',
                    'command_enhancement': True,
                    'additional_targets': 1,
                    'frightened_auto_fail': True
                })))

            conn.commit()

    def use_voice_of_tyranny(self, character_id: str) -> bool:
        """Use Voice of Tyranny to cast Command as bonus action."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get character's Charisma modifier
            cursor.execute("SELECT charisma FROM characters WHERE id = ?", (character_id,))
            result = cursor.fetchone()
            if not result:
                return False

            charisma_mod = max(1, (result[0] - 10) // 2)

            # Check feature availability
            cursor.execute("""
                SELECT feature_data FROM character_features
                WHERE character_id = ? AND feature_id = 'voice_of_tyranny'
            """, (character_id,))

            result = cursor.fetchone()
            if not result:
                return False

            feature_data = json.loads(result[0])
            current_uses = feature_data.get('uses_current', charisma_mod)

            if current_uses <= 0:
                return False

            # Use the feature
            feature_data['uses_current'] = current_uses - 1
            cursor.execute("""
                UPDATE character_features
                SET feature_data = ?
                WHERE character_id = ? AND feature_id = 'voice_of_tyranny'
            """, (json.dumps(feature_data), character_id))

            conn.commit()
            return True

    def use_decisive_edict(self, character_id: str, targets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use Decisive Edict ability when casting a pact magic spell."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if feature is available
            cursor.execute("""
                SELECT feature_data FROM character_features
                WHERE character_id = ? AND feature_id = 'decisive_edict'
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
                WHERE character_id = ? AND feature_id = 'decisive_edict'
            """, (json.dumps(feature_data), character_id))

            conn.commit()

            return {
                'success': True,
                'area': '30-foot emanation',
                'targets_affected': len(targets),
                'effects_available': ['marshal', 'oppress'],
                'description': 'Profane power erupts around you, affecting visible creatures in range'
            }

    def use_vindictive_rebuke(self, character_id: str, attacker_name: str = "attacker") -> Dict[str, Any]:
        """Use Vindictive Rebuke in response to being hit."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get character level and Charisma modifier
            cursor.execute("SELECT level, charisma FROM characters WHERE id = ?", (character_id,))
            result = cursor.fetchone()
            if not result:
                return {'success': False, 'reason': 'Character not found'}

            level, charisma = result
            charisma_mod = max(1, (charisma - 10) // 2)

            # Check feature availability
            cursor.execute("""
                SELECT feature_data FROM character_features
                WHERE character_id = ? AND feature_id = 'vindictive_rebuke'
            """, (character_id,))

            result = cursor.fetchone()
            if not result:
                return {'success': False, 'reason': 'Feature not available'}

            feature_data = json.loads(result[0])
            current_uses = feature_data.get('uses_current', charisma_mod)

            if current_uses <= 0:
                return {'success': False, 'reason': 'No uses remaining'}

            # Use the feature
            feature_data['uses_current'] = current_uses - 1
            cursor.execute("""
                UPDATE character_features
                SET feature_data = ?
                WHERE character_id = ? AND feature_id = 'vindictive_rebuke'
            """, (json.dumps(feature_data), character_id))

            conn.commit()

            return {
                'success': True,
                'attacker': attacker_name,
                'effect': f'Force {attacker_name} to reroll attack',
                'potential_damage': level,
                'damage_type': 'psychic',
                'condition': 'If reroll misses, attacker takes damage'
            }

    def enhance_command_spell(self, character_id: str, base_targets: int = 1) -> Dict[str, Any]:
        """Enhance Command spell with Absolute Tyranny."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if character has Absolute Tyranny
            cursor.execute("""
                SELECT feature_data FROM character_features
                WHERE character_id = ? AND feature_id = 'absolute_tyranny'
            """, (character_id,))

            result = cursor.fetchone()
            if not result:
                return {'enhanced': False, 'additional_targets': 0}

            return {
                'enhanced': True,
                'additional_targets': 1,
                'total_targets': base_targets + 1,
                'frightened_auto_fail': True,
                'description': 'Command can target one additional creature, and frightened creatures automatically fail their saves'
            }

    def short_rest_recovery(self, character_id: str):
        """Recover features that refresh on short rest."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Restore Decisive Edict
            cursor.execute("""
                UPDATE character_features
                SET feature_data = json_set(feature_data, '$.uses_current', json_extract(feature_data, '$.uses_max'))
                WHERE character_id = ? AND feature_id = 'decisive_edict'
            """, (character_id,))

            conn.commit()

    def long_rest_recovery(self, character_id: str):
        """Recover features that refresh on long rest."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get current Charisma modifier for use-based features
            cursor.execute("SELECT charisma FROM characters WHERE id = ?", (character_id,))
            result = cursor.fetchone()
            charisma_mod = max(1, (result[0] - 10) // 2) if result else 1

            # Restore Voice of Tyranny
            cursor.execute("""
                UPDATE character_features
                SET feature_data = json_set(feature_data, '$.uses_current', ?)
                WHERE character_id = ? AND feature_id = 'voice_of_tyranny'
            """, (charisma_mod, character_id))

            # Restore Vindictive Rebuke
            cursor.execute("""
                UPDATE character_features
                SET feature_data = json_set(feature_data, '$.uses_current', ?)
                WHERE character_id = ? AND feature_id = 'vindictive_rebuke'
            """, (charisma_mod, character_id))

            # Also restore short rest features
            self.short_rest_recovery(character_id)

    def apply_intimidation_expertise(self, character_id: str):
        """Apply Intimidation expertise from Tyrant's Herald."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Add or update Intimidation skill with expertise
            cursor.execute("""
                INSERT OR REPLACE INTO character_skills (character_id, skill_name, proficient, expertise)
                VALUES (?, 'Intimidation', 1, 1)
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