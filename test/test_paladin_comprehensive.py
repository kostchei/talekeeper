# test
"""
Comprehensive Paladin Implementation Test

Tests the current paladin implementation to identify what works and what needs fixing.
Covers character creation, spellcasting, Divine Smite, and basic functionality.
"""

import sys
import os
import sqlite3
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.paladin_abilities import PaladinAbilitiesService, get_paladin_service
from core.game_engine_sqlite import GameEngineSQLite


class PaladinTestFramework:
    """Test framework for paladin functionality."""

    def __init__(self):
        self.db_path = None
        self.game_engine = None
        self.paladin_service = None
        self.test_character_id = None
        self.results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "successes": []
        }

    def setup(self):
        """Set up test environment with temporary database."""
        print("Setting up paladin test environment...")

        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = temp_db.name
        temp_db.close()

        try:
            # Use the existing database instead of creating a new one
            self.db_path = "talekeeper.db"
            print(f"Using existing database: {self.db_path}")

            # Initialize services
            self.game_engine = GameEngineSQLite(self.db_path)
            self.paladin_service = PaladinAbilitiesService(self.db_path)

            print(f"Test database created: {self.db_path}")
            return True

        except Exception as e:
            print(f"Setup failed: {e}")
            return False

    def create_test_character(self, level=1):
        """Create a test paladin character."""
        try:
            # Create character in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                character_data = {
                    'id': 'test_paladin_001',
                    'name': 'Test Paladin',
                    'class': 'paladin',
                    'level': level,
                    'strength': 16,
                    'dexterity': 12,
                    'constitution': 14,
                    'intelligence': 10,
                    'wisdom': 12,
                    'charisma': 15,  # 15 Charisma = +2 modifier
                    'max_hp': 10 + (level - 1) * 6,
                    'current_hp': 10 + (level - 1) * 6,
                    'armor_class': 16,
                    'proficiency_bonus': 2 if level < 5 else 3
                }

                cursor.execute("""
                    INSERT OR REPLACE INTO characters
                    (id, name, class, level, strength, dexterity, constitution,
                     intelligence, wisdom, charisma, max_hp, current_hp, armor_class, proficiency_bonus)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    character_data['id'], character_data['name'], character_data['class'],
                    character_data['level'], character_data['strength'], character_data['dexterity'],
                    character_data['constitution'], character_data['intelligence'], character_data['wisdom'],
                    character_data['charisma'], character_data['max_hp'], character_data['current_hp'],
                    character_data['armor_class'], character_data['proficiency_bonus']
                ))

                conn.commit()
                self.test_character_id = character_data['id']
                print(f"Created test character: {character_data['name']} (Level {level} Paladin)")
                return character_data

        except Exception as e:
            print(f"Failed to create test character: {e}")
            return None

    def run_test(self, test_name, test_function):
        """Run a single test and record results."""
        self.results["tests_run"] += 1
        print(f"\n--- Testing: {test_name} ---")

        try:
            result = test_function()
            if result:
                self.results["tests_passed"] += 1
                self.results["successes"].append(test_name)
                print(f"PASS: {test_name}")
            else:
                self.results["tests_failed"] += 1
                self.results["failures"].append(test_name)
                print(f"FAIL: {test_name}")
            return result
        except Exception as e:
            self.results["tests_failed"] += 1
            self.results["failures"].append(f"{test_name}: {str(e)}")
            print(f"ERROR: {test_name} - {e}")
            return False

    def test_paladin_class_exists(self):
        """Test if paladin class is defined in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM classes WHERE name = 'paladin'")
                paladin_class = cursor.fetchone()

                if paladin_class:
                    print(f"Found paladin class definition: {paladin_class}")
                    return True
                else:
                    print("Paladin class not found in database")
                    return False

        except Exception as e:
            print(f"Database error checking paladin class: {e}")
            return False

    def test_paladin_service_creation(self):
        """Test paladin service can be created."""
        try:
            service = get_paladin_service(self.db_path)
            if service and isinstance(service, PaladinAbilitiesService):
                print("Paladin service created successfully")
                return True
            else:
                print("Failed to create paladin service")
                return False
        except Exception as e:
            print(f"Error creating paladin service: {e}")
            return False

    def test_paladin_character_creation(self):
        """Test creating a paladin character."""
        character = self.create_test_character(level=1)
        if character and character['class'] == 'paladin':
            print(f"Paladin character created: {character['name']}")
            return True
        else:
            print("Failed to create paladin character")
            return False

    def test_paladin_initialization(self):
        """Test paladin character initialization."""
        try:
            if not self.test_character_id:
                self.create_test_character(level=3)  # Level 3 for oath features

            result = self.paladin_service.initialize_paladin_character(
                self.test_character_id,
                oath="devotion"
            )

            if result.get("success"):
                print(f"Paladin initialization successful: {result}")
                return True
            else:
                print(f"Paladin initialization failed: {result.get('reason', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"Error in paladin initialization: {e}")
            return False

    def test_lay_on_hands_calculation(self):
        """Test Lay on Hands pool calculation."""
        try:
            if not self.test_character_id:
                self.create_test_character(level=5)

            # Initialize paladin
            init_result = self.paladin_service.initialize_paladin_character(self.test_character_id)

            if init_result.get("success"):
                expected_pool = 5 * 5  # 5 points per level at level 5
                actual_pool = init_result.get("lay_on_hands_pool", 0)

                if actual_pool == expected_pool:
                    print(f"Lay on Hands pool correct: {actual_pool}/{expected_pool}")
                    return True
                else:
                    print(f"Lay on Hands pool incorrect: {actual_pool}, expected {expected_pool}")
                    return False
            else:
                print("Could not initialize paladin for Lay on Hands test")
                return False

        except Exception as e:
            print(f"Error testing Lay on Hands: {e}")
            return False

    def test_divine_smite_calculation(self):
        """Test Divine Smite damage calculation."""
        try:
            # Test basic Divine Smite with 1st level slot
            result = self.paladin_service.divine_smite(
                character_id=self.test_character_id or "test",
                spell_slot_level=1,
                target_is_undead_or_fiend=False
            )

            if result.get("success"):
                expected_dice = 2  # 2d8 for 1st level slot
                actual_dice = result.get("damage_dice", 0)

                if actual_dice == expected_dice:
                    print(f"Divine Smite calculation correct: {actual_dice}d8")
                    return True
                else:
                    print(f"Divine Smite incorrect: {actual_dice}d8, expected {expected_dice}d8")
                    return False
            else:
                print(f"Divine Smite calculation failed: {result}")
                return False

        except Exception as e:
            print(f"Error testing Divine Smite: {e}")
            return False

    def test_divine_smite_vs_undead(self):
        """Test Divine Smite bonus damage vs undead/fiends."""
        try:
            result = self.paladin_service.divine_smite(
                character_id=self.test_character_id or "test",
                spell_slot_level=1,
                target_is_undead_or_fiend=True
            )

            if result.get("success"):
                expected_dice = 3  # 2d8 + 1d8 bonus vs undead/fiends
                actual_dice = result.get("damage_dice", 0)

                if actual_dice == expected_dice:
                    print(f"Divine Smite vs undead correct: {actual_dice}d8")
                    return True
                else:
                    print(f"Divine Smite vs undead incorrect: {actual_dice}d8, expected {expected_dice}d8")
                    return False
            else:
                print(f"Divine Smite vs undead failed: {result}")
                return False

        except Exception as e:
            print(f"Error testing Divine Smite vs undead: {e}")
            return False

    def test_channel_divinity_uses(self):
        """Test Channel Divinity use calculation."""
        try:
            if not self.test_character_id:
                self.create_test_character(level=3)

            # Initialize paladin
            init_result = self.paladin_service.initialize_paladin_character(self.test_character_id)

            if init_result.get("success"):
                expected_uses = 2  # Level 3-6 gets 2 uses
                actual_uses = init_result.get("channel_divinity_uses", 0)

                if actual_uses == expected_uses:
                    print(f"Channel Divinity uses correct: {actual_uses}")
                    return True
                else:
                    print(f"Channel Divinity uses incorrect: {actual_uses}, expected {expected_uses}")
                    return False
            else:
                print("Could not initialize paladin for Channel Divinity test")
                return False

        except Exception as e:
            print(f"Error testing Channel Divinity: {e}")
            return False

    def test_paladin_spell_preparation(self):
        """Test paladin spell preparation calculation."""
        try:
            if not self.test_character_id:
                self.create_test_character(level=5)  # Level 5 for decent spell access

            # Initialize paladin
            init_result = self.paladin_service.initialize_paladin_character(self.test_character_id)

            if init_result.get("success"):
                # Level 5 paladin with 15 Charisma (+2) should prepare: 2 + (5//2) = 4 spells
                expected_prepared = 4
                actual_prepared = init_result.get("max_prepared_spells", 0)

                if actual_prepared == expected_prepared:
                    print(f"Spell preparation calculation correct: {actual_prepared}")
                    return True
                else:
                    print(f"Spell preparation incorrect: {actual_prepared}, expected {expected_prepared}")
                    return False
            else:
                print("Could not initialize paladin for spell preparation test")
                return False

        except Exception as e:
            print(f"Error testing spell preparation: {e}")
            return False

    def test_oath_spells_added(self):
        """Test that oath spells are properly added."""
        try:
            if not self.test_character_id:
                self.create_test_character(level=5)  # Level 5 for multiple oath spell levels

            # Initialize paladin with Devotion oath
            init_result = self.paladin_service.initialize_paladin_character(
                self.test_character_id,
                oath="devotion"
            )

            if init_result.get("success"):
                oath_spells = init_result.get("spells_added", [])

                # Level 5 Devotion should have spells from levels 3 and 5
                expected_spells = [
                    "protection_from_evil_and_good", "sanctuary",  # Level 3
                    "lesser_restoration", "zone_of_truth"          # Level 5
                ]

                found_spells = [spell for spell in expected_spells if spell in oath_spells]

                if len(found_spells) >= 2:  # At least some oath spells should be added
                    print(f"Oath spells added: {oath_spells}")
                    return True
                else:
                    print(f"Insufficient oath spells added: {oath_spells}")
                    return False
            else:
                print("Could not initialize paladin for oath spells test")
                return False

        except Exception as e:
            print(f"Error testing oath spells: {e}")
            return False

    def test_paladin_info_retrieval(self):
        """Test getting comprehensive paladin information."""
        try:
            if not self.test_character_id:
                self.create_test_character(level=3)
                self.paladin_service.initialize_paladin_character(self.test_character_id)

            paladin_info = self.paladin_service.get_paladin_info(self.test_character_id)

            if paladin_info and not paladin_info.get("error"):
                print(f"Paladin info retrieved successfully")
                if "paladin_features" in paladin_info:
                    print(f"Paladin features found: {paladin_info['paladin_features']}")
                return True
            else:
                print(f"Failed to retrieve paladin info: {paladin_info}")
                return False

        except Exception as e:
            print(f"Error retrieving paladin info: {e}")
            return False

    def test_database_tables_exist(self):
        """Test that required database tables exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check for paladin_features table
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='paladin_features'
                """)

                paladin_table = cursor.fetchone()

                if paladin_table:
                    print("paladin_features table exists")
                    return True
                else:
                    print("paladin_features table missing - this is expected and needs to be created")
                    return False

        except Exception as e:
            print(f"Error checking database tables: {e}")
            return False

    def run_all_tests(self):
        """Run all paladin tests."""
        print("=== PALADIN COMPREHENSIVE TEST SUITE ===\n")

        if not self.setup():
            print("Failed to set up test environment")
            return False

        # Run all tests
        self.run_test("Paladin Class Definition", self.test_paladin_class_exists)
        self.run_test("Paladin Service Creation", self.test_paladin_service_creation)
        self.run_test("Database Tables", self.test_database_tables_exist)
        self.run_test("Character Creation", self.test_paladin_character_creation)
        self.run_test("Paladin Initialization", self.test_paladin_initialization)
        self.run_test("Lay on Hands Calculation", self.test_lay_on_hands_calculation)
        self.run_test("Divine Smite Basic", self.test_divine_smite_calculation)
        self.run_test("Divine Smite vs Undead", self.test_divine_smite_vs_undead)
        self.run_test("Channel Divinity Uses", self.test_channel_divinity_uses)
        self.run_test("Spell Preparation", self.test_paladin_spell_preparation)
        self.run_test("Oath Spells", self.test_oath_spells_added)
        self.run_test("Paladin Info Retrieval", self.test_paladin_info_retrieval)

        # Print summary
        self.print_summary()

        # Clean up
        self.cleanup()

        return self.results["tests_failed"] == 0

    def print_summary(self):
        """Print test results summary."""
        print(f"\n=== TEST RESULTS SUMMARY ===")
        print(f"Tests Run: {self.results['tests_run']}")
        print(f"Tests Passed: {self.results['tests_passed']}")
        print(f"Tests Failed: {self.results['tests_failed']}")

        if self.results["failures"]:
            print(f"\nFAILED TESTS:")
            for failure in self.results["failures"]:
                print(f"  - {failure}")

        if self.results["successes"]:
            print(f"\nPASSED TESTS:")
            for success in self.results["successes"]:
                print(f"  - {success}")

        success_rate = (self.results["tests_passed"] / self.results["tests_run"]) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")

    def cleanup(self):
        """Clean up test environment."""
        if self.db_path and os.path.exists(self.db_path):
            try:
                os.unlink(self.db_path)
                print(f"\nCleaned up test database: {self.db_path}")
            except Exception as e:
                print(f"Failed to clean up test database: {e}")


def main():
    """Run the paladin test suite."""
    tester = PaladinTestFramework()
    success = tester.run_all_tests()

    if success:
        print("\nALL TESTS PASSED - Paladin implementation is working!")
        return 0
    else:
        print("\nSOME TESTS FAILED - Paladin implementation needs fixes")
        return 1


if __name__ == "__main__":
    exit(main())