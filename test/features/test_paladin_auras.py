# test
"""
Regression Test: Paladin Aura System

Tests the aura system for paladins including Protection, Courage, and oath-specific auras.
"""

import sys
import os
import sqlite3
import tempfile

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from services.aura_manager import AuraManager, AuraType, get_aura_manager


class PaladinAuraTestFramework:
    """Test framework for paladin aura system."""

    def __init__(self):
        self.aura_manager = None
        self.db_path = None
        self.test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": []
        }

    def setup(self):
        """Set up test environment."""
        try:
            # Use existing database
            self.db_path = os.path.join(os.path.dirname(__file__), "..", "..", "talekeeper.db")
            self.aura_manager = AuraManager(self.db_path)

            print("Paladin aura test environment ready")
            return True

        except Exception as e:
            print(f"Setup failed: {e}")
            return False

    def run_test(self, test_name: str, test_function):
        """Run a single test and record results."""
        self.test_results["tests_run"] += 1
        print(f"\n--- Testing: {test_name} ---")

        try:
            result = test_function()
            if result:
                self.test_results["tests_passed"] += 1
                print(f"PASS: {test_name}")
            else:
                self.test_results["tests_failed"] += 1
                self.test_results["failures"].append(test_name)
                print(f"FAIL: {test_name}")
            return result
        except Exception as e:
            self.test_results["tests_failed"] += 1
            self.test_results["failures"].append(f"{test_name}: {str(e)}")
            print(f"ERROR: {test_name} - {e}")
            return False

    def create_test_paladin(self, character_id: str, level: int, charisma: int, subclass: str = "devotion"):
        """Create a test paladin character in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Insert or update test character
                cursor.execute("""
                    INSERT OR REPLACE INTO characters
                    (id, name, class_id, level, charisma, subclass_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (character_id, f"Test Paladin {level}", "paladin", level, charisma, subclass))

                conn.commit()
                return True

        except Exception as e:
            print(f"Error creating test paladin: {e}")
            return False

    def test_aura_manager_creation(self):
        """Test that aura manager can be created."""
        try:
            manager = AuraManager(self.db_path)
            if manager:
                print("Aura manager created successfully")
                return True
            else:
                print("Failed to create aura manager")
                return False
        except Exception as e:
            print(f"Aura manager creation error: {e}")
            return False

    def test_aura_range_calculation(self):
        """Test aura range calculation by level."""
        try:
            # Test normal range (levels 6-17)
            range_normal = self.aura_manager.get_aura_range(10)
            if range_normal == 10:
                print(f"Normal aura range correct: {range_normal} feet")
            else:
                print(f"Normal aura range incorrect: {range_normal}, expected 10")
                return False

            # Test expanded range (level 18+)
            range_expanded = self.aura_manager.get_aura_range(18)
            if range_expanded == 30:
                print(f"Expanded aura range correct: {range_expanded} feet")
            else:
                print(f"Expanded aura range incorrect: {range_expanded}, expected 30")
                return False

            return True

        except Exception as e:
            print(f"Aura range test error: {e}")
            return False

    def test_aura_of_protection(self):
        """Test Aura of Protection (level 6, +Cha mod to saves)."""
        try:
            # Create level 6 paladin with 16 Charisma (+3 modifier)
            character_id = "test_paladin_protection"
            if not self.create_test_paladin(character_id, 6, 16, "devotion"):
                return False

            # Get auras
            auras = self.aura_manager.get_character_auras(character_id)
            protection_auras = [a for a in auras if a.aura_type == AuraType.PROTECTION]

            if not protection_auras:
                print("Aura of Protection not found")
                return False

            protection_aura = protection_auras[0]
            expected_bonus = 3  # +3 Charisma modifier

            if protection_aura.save_bonus == expected_bonus:
                print(f"Aura of Protection bonus correct: +{protection_aura.save_bonus}")
            else:
                print(f"Aura of Protection bonus incorrect: +{protection_aura.save_bonus}, expected +{expected_bonus}")
                return False

            # Test save bonus calculation
            save_bonus = self.aura_manager.calculate_save_bonus(character_id, "wisdom")
            if save_bonus == expected_bonus:
                print(f"Save bonus calculation correct: +{save_bonus}")
            else:
                print(f"Save bonus calculation incorrect: +{save_bonus}, expected +{expected_bonus}")
                return False

            return True

        except Exception as e:
            print(f"Aura of Protection test error: {e}")
            return False

    def test_aura_of_courage(self):
        """Test Aura of Courage (level 10, fear immunity)."""
        try:
            # Create level 10 paladin
            character_id = "test_paladin_courage"
            if not self.create_test_paladin(character_id, 10, 16, "devotion"):
                return False

            # Check fear immunity
            has_fear_immunity = self.aura_manager.has_condition_immunity(character_id, "frightened")

            if has_fear_immunity:
                print("Fear immunity from Aura of Courage correct")
            else:
                print("Fear immunity from Aura of Courage not found")
                return False

            # Test specific condition check
            is_immune, aura_desc = self.aura_manager.check_aura_condition_immunity(character_id, "frightened")

            if is_immune and "Courage" in aura_desc:
                print(f"Condition immunity check correct: {aura_desc}")
            else:
                print(f"Condition immunity check failed: immune={is_immune}, desc={aura_desc}")
                return False

            return True

        except Exception as e:
            print(f"Aura of Courage test error: {e}")
            return False

    def test_aura_of_devotion(self):
        """Test Aura of Devotion (level 7 Devotion oath, charm immunity)."""
        try:
            # Create level 7 Devotion paladin
            character_id = "test_paladin_devotion_aura"
            if not self.create_test_paladin(character_id, 7, 16, "devotion"):
                return False

            # Check charm immunity
            has_charm_immunity = self.aura_manager.has_condition_immunity(character_id, "charmed")

            if has_charm_immunity:
                print("Charm immunity from Aura of Devotion correct")
            else:
                print("Charm immunity from Aura of Devotion not found")
                return False

            # Get auras to verify
            auras = self.aura_manager.get_character_auras(character_id)
            devotion_auras = [a for a in auras if a.aura_type == AuraType.DEVOTION]

            if devotion_auras:
                print(f"Aura of Devotion found: {devotion_auras[0].description}")
            else:
                print("Aura of Devotion not found in aura list")
                return False

            return True

        except Exception as e:
            print(f"Aura of Devotion test error: {e}")
            return False

    def test_multiple_auras(self):
        """Test character with multiple auras (high level)."""
        try:
            # Create level 15 Devotion paladin (has Protection, Courage, and Devotion auras)
            character_id = "test_paladin_multiple"
            if not self.create_test_paladin(character_id, 15, 18, "devotion"):  # 18 Cha = +4 mod
                return False

            # Get all auras
            auras = self.aura_manager.get_character_auras(character_id)
            aura_types = [a.aura_type for a in auras]

            expected_auras = [AuraType.PROTECTION, AuraType.COURAGE, AuraType.DEVOTION]
            for expected in expected_auras:
                if expected not in aura_types:
                    print(f"Missing expected aura: {expected}")
                    return False

            print(f"Multiple auras correct: {len(auras)} auras found")

            # Test summary
            summary = self.aura_manager.get_active_aura_summary(character_id)

            if summary["total_auras"] == 3:
                print(f"Aura summary correct: {summary['total_auras']} total auras")
            else:
                print(f"Aura summary incorrect: {summary['total_auras']} auras, expected 3")
                return False

            if summary["save_bonus"] == 4:  # +4 Charisma modifier
                print(f"Save bonus summary correct: +{summary['save_bonus']}")
            else:
                print(f"Save bonus summary incorrect: +{summary['save_bonus']}, expected +4")
                return False

            return True

        except Exception as e:
            print(f"Multiple auras test error: {e}")
            return False

    def test_different_oath_auras(self):
        """Test auras from different oaths."""
        try:
            # Test Ancients oath
            character_id_ancients = "test_paladin_ancients"
            if not self.create_test_paladin(character_id_ancients, 7, 16, "ancients"):
                return False

            ancients_auras = self.aura_manager.get_character_auras(character_id_ancients)
            ancients_types = [a.aura_type for a in ancients_auras]

            if AuraType.ANCIENTS in ancients_types:
                print("Ancients aura found")
            else:
                print("Ancients aura not found")
                return False

            # Test Vengeance oath
            character_id_vengeance = "test_paladin_vengeance"
            if not self.create_test_paladin(character_id_vengeance, 7, 16, "vengeance"):
                return False

            vengeance_auras = self.aura_manager.get_character_auras(character_id_vengeance)
            vengeance_types = [a.aura_type for a in vengeance_auras]

            if AuraType.VENGEANCE in vengeance_types:
                print("Vengeance aura found")
            else:
                print("Vengeance aura not found")
                return False

            return True

        except Exception as e:
            print(f"Different oath auras test error: {e}")
            return False

    def test_low_charisma_protection(self):
        """Test Aura of Protection with low Charisma (minimum +1 bonus)."""
        try:
            # Create level 6 paladin with 8 Charisma (-1 modifier, but minimum +1)
            character_id = "test_paladin_low_cha"
            if not self.create_test_paladin(character_id, 6, 8, "devotion"):
                return False

            # Test save bonus (should be +1 minimum)
            save_bonus = self.aura_manager.calculate_save_bonus(character_id, "constitution")
            if save_bonus == 1:
                print(f"Low Charisma protection bonus correct: +{save_bonus} (minimum)")
            else:
                print(f"Low Charisma protection bonus incorrect: +{save_bonus}, expected +1")
                return False

            return True

        except Exception as e:
            print(f"Low Charisma test error: {e}")
            return False

    def test_aura_expansion_level_18(self):
        """Test aura expansion at level 18."""
        try:
            # Create level 18 paladin
            character_id = "test_paladin_expansion"
            if not self.create_test_paladin(character_id, 18, 16, "devotion"):
                return False

            # Get auras and check range
            auras = self.aura_manager.get_character_auras(character_id)

            all_expanded = True
            for aura in auras:
                if aura.range_feet != 30:
                    print(f"Aura range not expanded: {aura.range_feet}, expected 30")
                    all_expanded = False

            if all_expanded and auras:
                print(f"All auras expanded to 30 feet at level 18")
            else:
                print("Aura expansion failed")
                return False

            return True

        except Exception as e:
            print(f"Aura expansion test error: {e}")
            return False

    def test_non_paladin_no_auras(self):
        """Test that non-paladins don't get auras."""
        try:
            # Create a non-paladin character
            character_id = "test_fighter"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO characters
                    (id, name, class_id, level, charisma)
                    VALUES (?, ?, ?, ?, ?)
                """, (character_id, "Test Fighter", "fighter", 10, 16))
                conn.commit()

            # Check for auras
            auras = self.aura_manager.get_character_auras(character_id)

            if not auras:
                print("Non-paladin correctly has no auras")
                return True
            else:
                print(f"Non-paladin incorrectly has auras: {len(auras)}")
                return False

        except Exception as e:
            print(f"Non-paladin test error: {e}")
            return False

    def run_all_tests(self):
        """Run all paladin aura tests."""
        print("=== PALADIN AURA REGRESSION TEST SUITE ===\n")

        if not self.setup():
            print("Failed to set up test environment")
            return False

        # Run all tests
        self.run_test("Aura Manager Creation", self.test_aura_manager_creation)
        self.run_test("Aura Range Calculation", self.test_aura_range_calculation)
        self.run_test("Aura of Protection", self.test_aura_of_protection)
        self.run_test("Aura of Courage", self.test_aura_of_courage)
        self.run_test("Aura of Devotion", self.test_aura_of_devotion)
        self.run_test("Multiple Auras", self.test_multiple_auras)
        self.run_test("Different Oath Auras", self.test_different_oath_auras)
        self.run_test("Low Charisma Protection", self.test_low_charisma_protection)
        self.run_test("Aura Expansion Level 18", self.test_aura_expansion_level_18)
        self.run_test("Non-Paladin No Auras", self.test_non_paladin_no_auras)

        # Print summary
        self.print_summary()

        return self.test_results["tests_failed"] == 0

    def print_summary(self):
        """Print test results summary."""
        print(f"\n=== PALADIN AURA TEST RESULTS ===")
        print(f"Tests Run: {self.test_results['tests_run']}")
        print(f"Tests Passed: {self.test_results['tests_passed']}")
        print(f"Tests Failed: {self.test_results['tests_failed']}")

        if self.test_results["failures"]:
            print(f"\nFAILED TESTS:")
            for failure in self.test_results["failures"]:
                print(f"  - {failure}")

        success_rate = (self.test_results["tests_passed"] / self.test_results["tests_run"]) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")


def main():
    """Run the paladin aura test suite."""
    tester = PaladinAuraTestFramework()
    success = tester.run_all_tests()

    if success:
        print("\nALL PALADIN AURA TESTS PASSED!")
        return 0
    else:
        print("\nSOME PALADIN AURA TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())