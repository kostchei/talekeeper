#test
#!/usr/bin/env python3
"""
Comprehensive test for Rogue level progression (1-20)
Tests all features are properly granted and stored in both tables
"""

import sys
import os
import sqlite3
import json
import uuid
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.level_up import LevelUpService
from services.subclass_manager import SubclassManager

class RogueLevelProgressionTest:
    """Test rogue leveling from 1-20 with all features."""

    def __init__(self):
        self.db_path = "test_rogue_progression.db"
        self.level_up_service = None
        self.test_character_id = None
        self.test_results = []

    def setup(self):
        """Create test database and character."""
        # Remove existing test database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        # Copy from main database structure
        import shutil
        shutil.copy("talekeeper.db", self.db_path)

        # Apply the rogue features migration to ensure proper schema
        with sqlite3.connect(self.db_path) as conn:
            with open("../database/migrations/005_fix_rogue_features_table.sql", 'r') as f:
                conn.executescript(f.read())
            conn.commit()

        # Clear any existing data
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM characters")
            cursor.execute("DELETE FROM character_features")
            cursor.execute("DELETE FROM rogue_features")
            cursor.execute("DELETE FROM character_subclasses")
            conn.commit()

        # Create level up service with test database
        self.level_up_service = LevelUpService(self.db_path)

        # Create a test rogue character
        self.test_character_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO characters
                (id, name, level, class_id, race_id, hit_points_max, hit_points_current,
                 strength, dexterity, constitution, intelligence, wisdom, charisma)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.test_character_id, "Test Rogue", 1, "rogue", "human", 8, 8,
                  10, 16, 12, 14, 13, 15))
            conn.commit()

        print(f"[OK] Test setup complete - Character ID: {self.test_character_id}")

    def test_level(self, level: int) -> Dict[str, Any]:
        """Test a specific level progression."""
        result = {
            "level": level,
            "success": False,
            "features_granted": [],
            "errors": [],
            "rogue_features": {},
            "character_features": []
        }

        try:
            # Level up the character
            success = self.level_up_service.level_up_character(
                self.test_character_id,
                "rogue",
                "thief" if level == 3 else None  # Select thief at level 3
            )

            if not success:
                result["errors"].append(f"Failed to level up to level {level}")
                return result

            # Check character_features table
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get all features for this character
                cursor.execute("""
                    SELECT feature_name, feature_type, level_gained, description, mechanics
                    FROM character_features
                    WHERE character_id = ?
                    ORDER BY level_gained, feature_name
                """, (self.test_character_id,))

                features = cursor.fetchall()
                result["character_features"] = [
                    {
                        "name": f[0],
                        "type": f[1],
                        "level": f[2],
                        "description": f[3],
                        "mechanics": f[4]
                    }
                    for f in features
                ]

                # Get rogue_features data
                cursor.execute("""
                    SELECT level, sneak_attack_dice, cunning_action_available,
                           uncanny_dodge_available, evasion_available,
                           cunning_strike_available, reliable_talent_active,
                           expertise_count, improved_cunning_strike,
                           slippery_mind_active, elusive_active,
                           stroke_of_luck_uses_max
                    FROM rogue_features
                    WHERE character_id = ?
                """, (self.test_character_id,))

                rogue_data = cursor.fetchone()
                if rogue_data:
                    result["rogue_features"] = {
                        "level": rogue_data[0],
                        "sneak_attack_dice": rogue_data[1],
                        "cunning_action": bool(rogue_data[2]),
                        "uncanny_dodge": bool(rogue_data[3]),
                        "evasion": bool(rogue_data[4]),
                        "cunning_strike": bool(rogue_data[5]),
                        "reliable_talent": bool(rogue_data[6]),
                        "expertise_count": rogue_data[7],
                        "improved_cunning_strike": bool(rogue_data[8]),
                        "slippery_mind": bool(rogue_data[9]),
                        "elusive": bool(rogue_data[10]),
                        "stroke_of_luck": rogue_data[11] or 0
                    }

            result["success"] = True

        except Exception as e:
            result["errors"].append(str(e))

        return result

    def verify_level_features(self, level: int, result: Dict[str, Any]) -> List[str]:
        """Verify expected features for a given level."""
        errors = []
        rogue_features = result.get("rogue_features", {})
        char_features = {f["name"]: f for f in result.get("character_features", [])}

        # Expected sneak attack dice
        expected_sneak_dice = (level + 1) // 2
        if rogue_features.get("sneak_attack_dice") != expected_sneak_dice:
            errors.append(f"Level {level}: Expected {expected_sneak_dice}d6 sneak attack, got {rogue_features.get('sneak_attack_dice')}d6")

        # Level-specific features
        if level >= 1:
            if "Sneak Attack" not in char_features:
                errors.append(f"Level {level}: Missing Sneak Attack in character_features")
            if "Thieves' Cant" not in char_features:
                errors.append(f"Level {level}: Missing Thieves' Cant")
            if "Expertise" not in char_features:
                errors.append(f"Level {level}: Missing Expertise")

        if level >= 2:
            if not rogue_features.get("cunning_action"):
                errors.append(f"Level {level}: Cunning Action not enabled in rogue_features")
            if "Cunning Action" not in char_features:
                errors.append(f"Level {level}: Missing Cunning Action in character_features")

        if level >= 3:
            # Should have subclass features (Fast Hands for thief)
            if "Fast Hands" not in char_features:
                errors.append(f"Level {level}: Missing Fast Hands (Thief subclass feature)")

        if level >= 5:
            if not rogue_features.get("uncanny_dodge"):
                errors.append(f"Level {level}: Uncanny Dodge not enabled")
            if not rogue_features.get("cunning_strike"):
                errors.append(f"Level {level}: Cunning Strike not enabled")
            if "Uncanny Dodge" not in char_features:
                errors.append(f"Level {level}: Missing Uncanny Dodge in character_features")
            if "Cunning Strike" not in char_features:
                errors.append(f"Level {level}: Missing Cunning Strike in character_features")

        if level >= 6:
            if rogue_features.get("expertise_count") != 4:
                errors.append(f"Level {level}: Expected 4 expertise, got {rogue_features.get('expertise_count')}")

        if level >= 7:
            if not rogue_features.get("evasion"):
                errors.append(f"Level {level}: Evasion not enabled")
            if "Evasion" not in char_features:
                errors.append(f"Level {level}: Missing Evasion in character_features")

        if level >= 11:
            if not rogue_features.get("reliable_talent"):
                errors.append(f"Level {level}: Reliable Talent not enabled")
            if "Reliable Talent" not in char_features:
                errors.append(f"Level {level}: Missing Reliable Talent in character_features")

        if level >= 14:
            if not rogue_features.get("improved_cunning_strike"):
                errors.append(f"Level {level}: Improved Cunning Strike not enabled")

        if level >= 15:
            if not rogue_features.get("slippery_mind"):
                errors.append(f"Level {level}: Slippery Mind not enabled")
            if "Slippery Mind" not in char_features:
                errors.append(f"Level {level}: Missing Slippery Mind in character_features")

        if level >= 18:
            if not rogue_features.get("elusive"):
                errors.append(f"Level {level}: Elusive not enabled")
            if "Elusive" not in char_features:
                errors.append(f"Level {level}: Missing Elusive in character_features")

        if level >= 20:
            if rogue_features.get("stroke_of_luck") != 1:
                errors.append(f"Level {level}: Expected Stroke of Luck uses = 1, got {rogue_features.get('stroke_of_luck')}")
            if "Stroke of Luck" not in char_features:
                errors.append(f"Level {level}: Missing Stroke of Luck in character_features")

        return errors

    def run_full_test(self):
        """Run complete level progression test."""
        print("\n" + "="*60)
        print("ROGUE LEVEL PROGRESSION TEST (1-20)")
        print("="*60)

        self.setup()

        all_errors = []

        # Test each level from 1 to 20
        for level in range(1, 21):
            print(f"\n[TEST] Testing Level {level}...")

            result = self.test_level(level)
            errors = self.verify_level_features(level, result)

            if errors:
                all_errors.extend(errors)
                print(f"[FAIL] Level {level} FAILED:")
                for error in errors:
                    print(f"   - {error}")
            else:
                print(f"[PASS] Level {level} PASSED")

            # Show key features
            rf = result["rogue_features"]
            print(f"   Sneak Attack: {rf.get('sneak_attack_dice')}d6")
            if rf.get("cunning_action"):
                print(f"   + Cunning Action")
            if rf.get("uncanny_dodge"):
                print(f"   + Uncanny Dodge")
            if rf.get("cunning_strike"):
                print(f"   + Cunning Strike")
            if rf.get("evasion"):
                print(f"   + Evasion")
            if rf.get("reliable_talent"):
                print(f"   + Reliable Talent")
            if rf.get("elusive"):
                print(f"   + Elusive")
            if rf.get("stroke_of_luck"):
                print(f"   + Stroke of Luck")

        # Final summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        if not all_errors:
            print("[SUCCESS] ALL TESTS PASSED! Rogue progression 1-20 working correctly!")
        else:
            print(f"[FAIL] {len(all_errors)} ERRORS FOUND:")
            for error in all_errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(all_errors) > 10:
                print(f"   ... and {len(all_errors) - 10} more errors")

        # Cleanup
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        return len(all_errors) == 0

if __name__ == "__main__":
    tester = RogueLevelProgressionTest()
    success = tester.run_full_test()
    sys.exit(0 if success else 1)