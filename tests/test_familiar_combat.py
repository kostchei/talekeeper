#test
"""
Test Pact of the Chain familiar combat integration.

Verifies that:
1. Warlock can select a familiar (quasit)
2. Familiar spawns in combat automatically
3. Familiar shares initiative with warlock
4. Familiar HP persists to database when damaged
5. Familiar can be resummoned
"""

import pytest
import sys
import sqlite3
import json
from pathlib import Path

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from talekeeper.services.warlock_service import WarlockService
from talekeeper.core.combat_manager import CombatManager
from tests.fixtures.warlock_test_database import WarlockTestDatabase


class TestFamiliarCombat:
    """Test familiar integration in combat system."""

    def test_familiar_selection_and_retrieval(self):
        """Test that warlocks can select and retrieve a familiar."""
        with WarlockTestDatabase() as db_path:
            warlock_service = WarlockService(db_path)

            # Create a test character
            character_id = "test_warlock_familiar"
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO characters (id, name, class_id, level, save_slot_id)
                    VALUES (?, 'Test Warlock', 'warlock', 3, 'test_slot')
                """, (character_id,))

                cursor.execute("""
                    INSERT INTO save_slots (id, slot_number, save_name)
                    VALUES ('test_slot', 1, 'Test Save')
                """)
                conn.commit()

            # Initialize warlock features and grant Pact of the Chain
            warlock_service.initialize_warlock_features(character_id, 3, 'Fiend')
            success = warlock_service.select_pact_boon(character_id, 'chain')
            assert success, "Failed to select Pact of the Chain"

            # Select a familiar
            success = warlock_service.select_familiar(character_id, 'quasit')
            assert success, "Failed to select quasit familiar"

            # Retrieve active familiar
            familiar = warlock_service.get_active_familiar(character_id)
            assert familiar is not None, "No active familiar found"
            assert familiar['type'] == 'quasit'
            assert familiar['hp'] == 25  # Quasit default HP
            assert familiar['alive'] is True

    def test_familiar_spawns_in_combat(self):
        """Test that familiar automatically spawns when warlock enters combat."""
        with WarlockTestDatabase() as db_path:
            warlock_service = WarlockService(db_path)
            combat_manager = CombatManager(db_path)

            # Create and setup warlock with familiar
            character_id = "test_warlock_combat"
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO characters (id, name, class_id, level, save_slot_id,
                                          dexterity, armor_class, hit_points_current, hit_points_max)
                    VALUES (?, 'Combat Warlock', 'warlock', 3, 'test_slot', 14, 12, 20, 20)
                """, (character_id,))

                cursor.execute("""
                    INSERT INTO save_slots (id, slot_number, save_name)
                    VALUES ('test_slot', 1, 'Test Save')
                """)
                conn.commit()

            warlock_service.initialize_warlock_features(character_id, 3, 'Fiend')
            warlock_service.select_pact_boon(character_id, 'chain')
            warlock_service.select_familiar(character_id, 'quasit')

            # Load character data including features
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM characters WHERE id = ?
                """, (character_id,))
                char_row = cursor.fetchone()

                # Load character features
                cursor.execute("""
                    SELECT feature_name, feature_type, usage_type, level_gained, description, mechanics
                    FROM character_features
                    WHERE character_id = ?
                """, (character_id,))
                feature_rows = cursor.fetchall()
                features = {}
                for row in feature_rows:
                    mechanics = {}
                    if row['mechanics']:
                        try:
                            mechanics = json.loads(row['mechanics'])
                        except json.JSONDecodeError:
                            mechanics = {}

                    features[row['feature_name']] = {
                        'type': row['feature_type'],
                        'usage': row['usage_type'],
                        'level_gained': row['level_gained'],
                        'description': row['description'],
                        'mechanics': mechanics
                    }

                character_data = {
                    'id': char_row['id'],
                    'name': char_row['name'],
                    'class_id': char_row['class_id'],
                    'level': char_row['level'],
                    'dexterity': char_row['dexterity'],
                    'ac': char_row['armor_class'],
                    'hp': char_row['hit_points_current'],
                    'max_hp': char_row['hit_points_max'],
                    'character_features': features
                }

            # Add warlock to combat
            combat_manager.add_player_combatant(character_data)

            # Verify both warlock and familiar are in combat
            assert character_id in combat_manager.combatants, "Warlock not in combat"
            familiar_id = f"{character_id}_familiar"
            assert familiar_id in combat_manager.combatants, "Familiar not spawned in combat"

            # Verify familiar is marked as companion
            familiar = combat_manager.combatants[familiar_id]
            assert familiar.is_companion is True
            assert familiar.companion_of == character_id
            assert familiar.companion_type == "familiar"
            assert familiar.name == "Quasit"
            assert familiar.hit_points == 25

    def test_familiar_shares_initiative(self):
        """Test that familiar shares initiative with owner and goes right after."""
        with WarlockTestDatabase() as db_path:
            warlock_service = WarlockService(db_path)
            combat_manager = CombatManager(db_path)

            # Setup warlock with familiar
            character_id = "test_warlock_init"
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO characters (id, name, class_id, level, save_slot_id,
                                          dexterity, armor_class, hit_points_current, hit_points_max)
                    VALUES (?, 'Init Warlock', 'warlock', 3, 'test_slot', 14, 12, 20, 20)
                """, (character_id,))

                cursor.execute("""
                    INSERT INTO save_slots (id, slot_number, save_name)
                    VALUES ('test_slot', 1, 'Test Save')
                """)
                conn.commit()

            warlock_service.initialize_warlock_features(character_id, 3, 'Fiend')
            warlock_service.select_pact_boon(character_id, 'chain')
            warlock_service.select_familiar(character_id, 'quasit')

            # Load character with features
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
                char_row = cursor.fetchone()
                cursor.execute("""
                    SELECT feature_name, mechanics
                    FROM character_features WHERE character_id = ?
                """, (character_id,))
                feature_rows = cursor.fetchall()
                features = {}
                for row in feature_rows:
                    mechanics = json.loads(row['mechanics']) if row['mechanics'] else {}
                    features[row['feature_name']] = {'mechanics': mechanics}

                character_data = {
                    'id': char_row['id'],
                    'name': char_row['name'],
                    'class_id': 'warlock',
                    'level': 3,
                    'dexterity': char_row['dexterity'],
                    'ac': char_row['armor_class'],
                    'hp': char_row['hit_points_current'],
                    'max_hp': char_row['hit_points_max'],
                    'character_features': features
                }

            # Add warlock and a goblin to combat
            combat_manager.add_player_combatant(character_data)

            # Add a simple goblin
            goblin_data = {
                'name': 'Goblin',
                'armor_class': 13,
                'hit_points': 7,
                'dexterity': 14,
                'actions': []
            }
            combat_manager.add_monster_combatant('goblin1', goblin_data)

            # Start combat and check initiative order
            combat_manager.start_combat()

            initiative_order = combat_manager.current_round.initiative_order
            warlock_index = None
            familiar_index = None

            for i, combatant in enumerate(initiative_order):
                if combatant.id == character_id:
                    warlock_index = i
                elif combatant.id == f"{character_id}_familiar":
                    familiar_index = i

            assert warlock_index is not None, "Warlock not in initiative order"
            assert familiar_index is not None, "Familiar not in initiative order"
            assert familiar_index == warlock_index + 1, "Familiar not immediately after warlock"

            # Verify shared initiative
            warlock = combat_manager.combatants[character_id]
            familiar = combat_manager.combatants[f"{character_id}_familiar"]
            assert warlock.initiative_roll == familiar.initiative_roll, "Familiar doesn't share initiative"

    def test_familiar_hp_persistence(self):
        """Test that familiar HP updates persist to database."""
        with WarlockTestDatabase() as db_path:
            warlock_service = WarlockService(db_path)

            character_id = "test_warlock_hp"
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO characters (id, name, class_id, level, save_slot_id)
                    VALUES (?, 'HP Warlock', 'warlock', 3, 'test_slot')
                """, (character_id,))
                cursor.execute("""
                    INSERT INTO save_slots (id, slot_number, save_name)
                    VALUES ('test_slot', 1, 'Test Save')
                """)
                conn.commit()

            warlock_service.initialize_warlock_features(character_id, 3, 'Fiend')
            warlock_service.select_pact_boon(character_id, 'chain')
            warlock_service.select_familiar(character_id, 'quasit')

            # Damage the familiar
            warlock_service.update_familiar_hp(character_id, 10)

            # Retrieve and verify
            familiar = warlock_service.get_active_familiar(character_id)
            assert familiar['hp'] == 10, "Familiar HP not updated"
            assert familiar['alive'] is True

            # Kill the familiar
            warlock_service.update_familiar_hp(character_id, 0)

            # Verify death
            familiar = warlock_service.get_active_familiar(character_id)
            assert familiar is None, "Dead familiar still active"

            # Resummon
            warlock_service.select_familiar(character_id, 'quasit')
            familiar = warlock_service.get_active_familiar(character_id)
            assert familiar['hp'] == 25, "Resummoned familiar doesn't have full HP"
            assert familiar['alive'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
