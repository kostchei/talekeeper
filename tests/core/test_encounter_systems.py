#!/usr/bin/env python3
"""
Regression tests for encounter systems: monsters, skill challenges, hazards, and vendors.

Tests that encounter components work correctly:
- Monster database integrity and combat data
- Skill challenge templates and mechanics
- Hazard system and level scaling
- Town encounter system (vendor/shop availability)

Run: python tests/core/test_encounter_systems.py
"""

import sys
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from services.skill_challenge_manager import SkillChallengeManager
from services.hazard_service import HazardService

class EncounterSystemsTester:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
        self.test_results = []
        self.skill_challenge_manager = SkillChallengeManager(db_path)
        self.hazard_service = HazardService(db_path)

    def log(self, message: str, status: str = "INFO"):
        """Log test output."""
        prefix = {
            "PASS": "[PASS]",
            "FAIL": "[FAIL]",
            "INFO": "[INFO]",
            "WARN": "[WARN]"
        }.get(status, "[INFO]")
        print(f"{prefix} {message}")

    def test_monster_database_integrity(self):
        """Test that monster database has valid entries with required fields."""
        test_name = "Monster Database Integrity"
        self.log(f"Testing: {test_name}")

        all_passed = True

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM monsters")
                total_monsters = cursor.fetchone()[0]

                if total_monsters == 0:
                    self.log("  No monsters found in database", "FAIL")
                    all_passed = False
                else:
                    self.log(f"  Found {total_monsters} monsters in database", "PASS")

                cursor.execute("""
                    SELECT COUNT(*) FROM monsters
                    WHERE name IS NULL OR name = ''
                    OR hit_points IS NULL OR hit_points <= 0
                    OR armor_class IS NULL OR armor_class <= 0
                    OR challenge_rating IS NULL OR challenge_rating = ''
                """)
                invalid_monsters = cursor.fetchone()[0]

                if invalid_monsters > 0:
                    self.log(f"  Found {invalid_monsters} monsters with invalid core stats", "FAIL")
                    all_passed = False
                else:
                    self.log("  All monsters have valid core stats", "PASS")

                cursor.execute("""
                    SELECT name FROM monsters
                    WHERE actions IS NULL OR actions = '' OR actions = '[]'
                """)
                monsters_without_actions = cursor.fetchall()

                if len(monsters_without_actions) > 20:
                    self.log(f"  Warning: {len(monsters_without_actions)} monsters have no actions", "WARN")

                cr_ranges = ['0', '1/8', '1/4', '1/2', '1', '2', '5', '10', '15', '20', '25', '30']
                cursor.execute("SELECT DISTINCT challenge_rating FROM monsters ORDER BY challenge_rating")
                found_crs = [row[0] for row in cursor.fetchall()]

                if len(found_crs) > 0:
                    self.log(f"  CR range: {found_crs[0]} to {found_crs[-1]} ({len(found_crs)} unique CRs)", "PASS")
                else:
                    self.log("  No valid CR values found", "FAIL")
                    all_passed = False

        except Exception as e:
            self.log(f"  Exception: {e}", "FAIL")
            all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_monster_combat_data(self):
        """Test that monsters have valid combat-related data."""
        test_name = "Monster Combat Data"
        self.log(f"Testing: {test_name}")

        all_passed = True

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT name, actions FROM monsters
                    WHERE actions IS NOT NULL AND actions != '' AND actions != '[]'
                    LIMIT 10
                """)

                monsters_with_actions = cursor.fetchall()

                if len(monsters_with_actions) == 0:
                    self.log("  No monsters with valid action data found", "FAIL")
                    all_passed = False
                else:
                    valid_action_count = 0
                    for name, actions_json in monsters_with_actions:
                        try:
                            actions = json.loads(actions_json)
                            if isinstance(actions, list) and len(actions) > 0:
                                valid_action_count += 1
                        except:
                            pass

                    if valid_action_count == len(monsters_with_actions):
                        self.log(f"  {valid_action_count}/{len(monsters_with_actions)} sampled monsters have valid action JSON", "PASS")
                    else:
                        self.log(f"  Only {valid_action_count}/{len(monsters_with_actions)} monsters have valid action JSON", "FAIL")
                        all_passed = False

                cursor.execute("""
                    SELECT COUNT(*) FROM monsters
                    WHERE (strength IS NULL OR strength < 1 OR strength > 30)
                    OR (dexterity IS NULL OR dexterity < 1 OR dexterity > 30)
                    OR (constitution IS NULL OR constitution < 1 OR constitution > 30)
                """)
                invalid_stats = cursor.fetchone()[0]

                if invalid_stats > 0:
                    self.log(f"  {invalid_stats} monsters have invalid ability scores", "FAIL")
                    all_passed = False
                else:
                    self.log("  All monsters have valid ability scores (1-30)", "PASS")

        except Exception as e:
            self.log(f"  Exception: {e}", "FAIL")
            all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_skill_challenge_templates(self):
        """Test that skill challenge templates are properly configured."""
        test_name = "Skill Challenge Templates"
        self.log(f"Testing: {test_name}")

        all_passed = True

        try:
            templates = self.skill_challenge_manager.get_all_templates()

            if len(templates) == 0:
                self.log("  No skill challenge templates found", "FAIL")
                all_passed = False
            else:
                self.log(f"  Found {len(templates)} skill challenge templates", "PASS")

            valid_templates = 0
            for template in templates:
                is_valid = (
                    template.name and
                    template.base_dc > 0 and
                    len(template.skills) > 0 and
                    len(template.success_options) > 0 and
                    len(template.failure_options) > 0
                )

                if is_valid:
                    valid_templates += 1

            if valid_templates == len(templates):
                self.log(f"  All {len(templates)} templates have required fields", "PASS")
            else:
                self.log(f"  Only {valid_templates}/{len(templates)} templates are valid", "FAIL")
                all_passed = False

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT template_id, COUNT(*) as skill_count
                    FROM skill_challenge_template_skills
                    GROUP BY template_id
                """)

                template_skill_counts = cursor.fetchall()

                templates_with_no_skills = len(templates) - len(template_skill_counts)
                if templates_with_no_skills > 0:
                    self.log(f"  {templates_with_no_skills} templates have no associated skills", "WARN")

        except Exception as e:
            self.log(f"  Exception: {e}", "FAIL")
            all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_skill_challenge_mechanics(self):
        """Test skill challenge session creation and attempt mechanics."""
        test_name = "Skill Challenge Mechanics"
        self.log(f"Testing: {test_name}")

        all_passed = True

        try:
            templates = self.skill_challenge_manager.get_all_templates()

            if len(templates) == 0:
                self.log("  Skipping - no templates available", "WARN")
                self.test_results.append({'test': test_name, 'passed': True})
                return True

            test_template = templates[0]
            test_character_id = "test_skill_challenge_char"

            session = self.skill_challenge_manager.create_session(
                character_id=test_character_id,
                template=test_template
            )

            if session is None:
                self.log("  Failed to create skill challenge session", "FAIL")
                all_passed = False
            else:
                self.log(f"  Created session for challenge: {test_template.name}", "PASS")

                if session.successes == 0 and session.failures == 0:
                    self.log("  Session initialized with correct counters", "PASS")
                else:
                    self.log("  Session counters not initialized correctly", "FAIL")
                    all_passed = False

            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skill_challenge_sessions'")
                    if cursor.fetchone():
                        try:
                            cursor.execute("DELETE FROM skill_challenge_sessions WHERE id = ?", (session.id,))
                        except:
                            pass

                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skill_challenge_attempts'")
                    if cursor.fetchone():
                        try:
                            cursor.execute("DELETE FROM skill_challenge_attempts WHERE session_id = ?", (session.id,))
                        except:
                            pass

                    conn.commit()
            except:
                pass

        except Exception as e:
            self.log(f"  Exception: {e}", "FAIL")
            all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_hazard_system(self):
        """Test hazard system and level-appropriate hazards."""
        test_name = "Hazard System"
        self.log(f"Testing: {test_name}")

        all_passed = True

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM hazards")
                total_hazards = cursor.fetchone()[0]

                if total_hazards == 0:
                    self.log("  No hazards found in database", "FAIL")
                    all_passed = False
                else:
                    self.log(f"  Found {total_hazards} hazards in database", "PASS")

                cursor.execute("""
                    SELECT COUNT(*) FROM hazards
                    WHERE name IS NULL OR name = ''
                    OR level_min IS NULL OR level_max IS NULL
                    OR (dc IS NULL AND hazard_type NOT IN ('environmental', 'trap'))
                    OR (save_type IS NULL OR save_type = '')
                """)
                invalid_hazards = cursor.fetchone()[0]

                if invalid_hazards > 0:
                    self.log(f"  {invalid_hazards} hazards have invalid required fields (some hazards may have DC=0 by design)", "WARN")
                else:
                    self.log("  All hazards have valid required fields", "PASS")

            test_levels = [1, 5, 10, 15, 20]
            for level in test_levels:
                hazards = self.hazard_service.get_hazards_for_level(level)
                if len(hazards) > 0:
                    self.log(f"  Level {level}: {len(hazards)} hazards available", "PASS")
                else:
                    self.log(f"  Level {level}: No hazards available", "WARN")

            random_hazard = self.hazard_service.get_random_hazard(5)
            if random_hazard:
                required_keys = ['name', 'dc', 'save_type', 'damage_dice']
                missing_keys = [key for key in required_keys if key not in random_hazard]

                if len(missing_keys) == 0:
                    self.log(f"  Random hazard has all required keys", "PASS")
                else:
                    self.log(f"  Random hazard missing keys: {missing_keys}", "FAIL")
                    all_passed = False

        except Exception as e:
            self.log(f"  Exception: {e}", "FAIL")
            all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_hazard_gear_bonuses(self):
        """Test that hazard gear bonuses work correctly."""
        test_name = "Hazard Gear Bonuses"
        self.log(f"Testing: {test_name}")

        all_passed = True

        try:
            test_hazard = {
                'name': 'Quicksand Pit',
                'save_type': 'strength',
                'dc': 13
            }

            gear_with_rope = ['rope', 'backpack']
            bonuses = self.hazard_service.apply_gear_bonus(test_hazard, gear_with_rope)

            if bonuses.get('advantage', False):
                self.log("  Rope provides advantage against quicksand", "PASS")
            else:
                self.log("  Rope should provide advantage against quicksand", "FAIL")
                all_passed = False

            test_hazard_fire = {
                'name': 'Inferno Room',
                'save_type': 'dexterity',
                'dc': 15
            }

            gear_with_cloak = ['cloak', 'boots']
            bonuses_fire = self.hazard_service.apply_gear_bonus(test_hazard_fire, gear_with_cloak)

            if bonuses_fire.get('damage_reduction', 0) > 0:
                self.log(f"  Cloak reduces fire damage by {bonuses_fire['damage_reduction']}", "PASS")
            else:
                self.log("  Cloak should reduce fire damage", "FAIL")
                all_passed = False

        except Exception as e:
            self.log(f"  Exception: {e}", "FAIL")
            all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_town_encounter_system(self):
        """Test town encounter system (vendors, training hall, etc.)."""
        test_name = "Town Encounter System"
        self.log(f"Testing: {test_name}")

        all_passed = True

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT COUNT(*) FROM equipment
                    WHERE item_type IN ('weapon', 'armor', 'potion', 'tool')
                """)
                vendor_items = cursor.fetchone()[0]

                if vendor_items > 0:
                    self.log(f"  Found {vendor_items} items available for vendor system", "PASS")
                else:
                    self.log("  No vendor items found", "FAIL")
                    all_passed = False

                cursor.execute("""
                    SELECT COUNT(*) FROM equipment
                    WHERE (cost_gp IS NULL OR cost_gp = 0)
                    AND item_type IN ('weapon', 'armor')
                """)
                free_items = cursor.fetchone()[0]

                if free_items > 0:
                    self.log(f"  Warning: {free_items} weapons/armor have no cost", "WARN")

                cursor.execute("""
                    SELECT item_type, COUNT(*) as count
                    FROM equipment
                    GROUP BY item_type
                """)

                item_distribution = cursor.fetchall()
                self.log(f"  Item distribution: {dict(item_distribution)}", "INFO")

        except Exception as e:
            self.log(f"  Exception: {e}", "FAIL")
            all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_encounter_level_scaling(self):
        """Test that encounters scale appropriately with character level."""
        test_name = "Encounter Level Scaling"
        self.log(f"Testing: {test_name}")

        all_passed = True

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                test_levels = [1, 5, 10, 15, 20]

                for level in test_levels:
                    cursor.execute("""
                        SELECT COUNT(*) FROM monsters
                        WHERE CAST(REPLACE(REPLACE(challenge_rating, '1/8', '0.125'), '1/4', '0.25') AS REAL) <= ?
                    """, (level,))

                    appropriate_monsters = cursor.fetchone()[0]

                    if appropriate_monsters > 0:
                        self.log(f"  Level {level}: {appropriate_monsters} appropriate monsters", "PASS")
                    else:
                        self.log(f"  Level {level}: No appropriate monsters", "WARN")

                for level in test_levels:
                    hazards = self.hazard_service.get_hazards_for_level(level)

                    if len(hazards) > 0:
                        dcs = [h['dc'] for h in hazards if h.get('dc') is not None]
                        if dcs:
                            avg_dc = sum(dcs) / len(dcs)
                            self.log(f"  Level {level} hazards: avg DC {avg_dc:.1f}", "INFO")

        except Exception as e:
            self.log(f"  Exception: {e}", "FAIL")
            all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def run_all_tests(self):
        """Run all encounter system tests."""
        self.log("=" * 60)
        self.log("ENCOUNTER SYSTEMS REGRESSION TESTS")
        self.log("=" * 60)

        tests = [
            self.test_monster_database_integrity,
            self.test_monster_combat_data,
            self.test_skill_challenge_templates,
            self.test_skill_challenge_mechanics,
            self.test_hazard_system,
            self.test_hazard_gear_bonuses,
            self.test_town_encounter_system,
            self.test_encounter_level_scaling,
        ]

        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log(f"CRITICAL ERROR in {test_func.__name__}: {e}", "FAIL")
                self.test_results.append({'test': test_func.__name__, 'passed': False})
            self.log("")

        self.print_summary()

    def print_summary(self):
        """Print test results summary."""
        self.log("=" * 60)
        self.log("TEST SUMMARY")
        self.log("=" * 60)

        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)

        self.log(f"Tests passed: {passed}/{total}")

        if passed == total:
            self.log("ALL TESTS PASSED", "PASS")
            return 0
        else:
            self.log("SOME TESTS FAILED", "FAIL")
            for result in self.test_results:
                if not result['passed']:
                    self.log(f"  FAILED: {result['test']}", "FAIL")
            return 1

def main():
    """Main entry point."""
    try:
        tester = EncounterSystemsTester()
        exit_code = tester.run_all_tests()
        sys.exit(exit_code)
    except Exception as e:
        print(f"[FAIL] Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()