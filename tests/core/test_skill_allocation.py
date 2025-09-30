#!/usr/bin/env python3
"""
Regression tests for skill proficiency allocation during character generation.

Tests that skills are properly allocated from:
- Background (fixed skills)
- Class (player-selected skills)
- Species (fixed and choice skills)

Run: python tests/core/test_skill_allocation.py
"""

import sys
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Set

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from services.proficiency_system import ProficiencySystem

class SkillAllocationTester:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
        self.proficiency_system = ProficiencySystem(db_path)
        self.test_results = []
        self.test_character_id = "test_skill_allocation_character"

    def log(self, message: str, status: str = "INFO"):
        """Log test output."""
        prefix = {
            "PASS": "[PASS]",
            "FAIL": "[FAIL]",
            "INFO": "[INFO]",
            "WARN": "[WARN]"
        }.get(status, "[INFO]")
        print(f"{prefix} {message}")

    def setup(self):
        """Setup test environment."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM characters WHERE id = ?", (self.test_character_id,))
            cursor.execute("DELETE FROM character_proficiencies WHERE character_id = ?", (self.test_character_id,))
            conn.commit()
        self.log("Test environment setup complete")

    def teardown(self):
        """Cleanup test data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM characters WHERE id = ?", (self.test_character_id,))
            cursor.execute("DELETE FROM character_proficiencies WHERE character_id = ?", (self.test_character_id,))
            conn.commit()
        self.log("Test cleanup complete")

    def create_test_character(self, class_id: str, background_id: str, race_id: str):
        """Create a minimal test character."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO characters (id, name, class_id, background_id, race_id, level)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (self.test_character_id, "Test Character", class_id, background_id, race_id))
            conn.commit()

    def get_skills_from_db(self, character_id: str) -> Dict[str, List[str]]:
        """Retrieve skill proficiencies grouped by source."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source, proficiency_name
                FROM character_proficiencies
                WHERE character_id = ? AND proficiency_type = 'skill'
                ORDER BY source, proficiency_name
            """, (character_id,))

            skills_by_source = {}
            for source, skill_name in cursor.fetchall():
                if source not in skills_by_source:
                    skills_by_source[source] = []
                skills_by_source[source].append(skill_name)

            return skills_by_source

    def get_expected_background_skills(self, background_id: str) -> Set[str]:
        """Get expected skills from background."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT proficiency_name
                FROM background_proficiencies
                WHERE background_id = ?
                AND proficiency_type = 'skill'
                AND proficiency_name NOT LIKE 'choice_%'
            """, (background_id,))
            return set(row[0] for row in cursor.fetchall())

    def get_expected_species_skills(self, species_id: str) -> Set[str]:
        """Get expected fixed skills from species."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT proficiency_name
                FROM species_proficiencies
                WHERE species_id = ?
                AND proficiency_type = 'skill'
                AND proficiency_name IS NOT NULL
                AND (choice_count IS NULL OR choice_count = 0)
            """, (species_id,))
            return set(row[0] for row in cursor.fetchall())

    def get_class_skill_options(self, class_id: str) -> Dict:
        """Get class skill selection parameters."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT skill_count, available_skills
                FROM class_skill_choices
                WHERE class_id = ?
                LIMIT 1
            """, (class_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'count': row[0],
                    'available': json.loads(row[1])
                }
            return {'count': 0, 'available': []}

    def test_background_skill_allocation(self):
        """Test that background skills are properly allocated."""
        test_name = "Background Skill Allocation"
        self.log(f"Testing: {test_name}")

        backgrounds = ['soldier', 'criminal', 'sage', 'acolyte']
        all_passed = True

        for background_id in backgrounds:
            try:
                self.setup()
                self.create_test_character('fighter', background_id, 'human')

                expected_skills = self.get_expected_background_skills(background_id)

                selected_skills = ['Perception', 'History']

                with sqlite3.connect(self.db_path) as conn:
                    success = self.proficiency_system.initialize_character_proficiencies(
                        self.test_character_id,
                        'fighter',
                        background=background_id,
                        selected_skills=selected_skills,
                        conn=conn
                    )
                    conn.commit()

                if not success:
                    self.log(f"Failed to initialize proficiencies for {background_id}", "FAIL")
                    all_passed = False
                    continue

                skills_by_source = self.get_skills_from_db(self.test_character_id)
                actual_bg_skills = set(skills_by_source.get('background', []))

                all_skills_present = expected_skills.issubset(
                    set(skills_by_source.get('background', [])) | set(skills_by_source.get('class', []))
                )

                if all_skills_present and len(actual_bg_skills) > 0:
                    self.log(f"  {background_id}: Background skills present ({len(expected_skills)} expected, {len(actual_bg_skills)} from background)", "PASS")
                else:
                    self.log(f"  {background_id}: Expected {expected_skills}, got bg={actual_bg_skills}, class={skills_by_source.get('class', [])}", "FAIL")
                    all_passed = False

                self.teardown()

            except Exception as e:
                self.log(f"  {background_id}: Exception - {e}", "FAIL")
                all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_class_skill_allocation(self):
        """Test that class skill selections are properly allocated."""
        test_name = "Class Skill Selection Allocation"
        self.log(f"Testing: {test_name}")

        test_cases = [
            ('fighter', ['Athletics', 'Perception']),
            ('barbarian', ['Athletics', 'Survival']),
            ('rogue', ['Acrobatics', 'Stealth', 'Perception', 'Investigation']),
            ('wizard', ['Arcana', 'History']),
        ]

        all_passed = True

        for class_id, selected_skills in test_cases:
            try:
                self.setup()
                self.create_test_character(class_id, 'soldier', 'human')

                skill_options = self.get_class_skill_options(class_id)
                expected_count = skill_options['count']

                if len(selected_skills) != expected_count:
                    self.log(f"  {class_id}: Test setup error - selected {len(selected_skills)} skills, class allows {expected_count}", "WARN")

                for skill in selected_skills:
                    if skill not in skill_options['available']:
                        self.log(f"  {class_id}: Invalid skill '{skill}' not in available list", "FAIL")
                        all_passed = False
                        continue

                with sqlite3.connect(self.db_path) as conn:
                    success = self.proficiency_system.initialize_character_proficiencies(
                        self.test_character_id,
                        class_id,
                        background='soldier',
                        selected_skills=selected_skills,
                        conn=conn
                    )
                    conn.commit()

                if not success:
                    self.log(f"  {class_id}: Failed to initialize proficiencies", "FAIL")
                    all_passed = False
                    continue

                skills_by_source = self.get_skills_from_db(self.test_character_id)
                actual_class_skills = set(skills_by_source.get('class', []))
                expected_class_skills = set(selected_skills)

                if expected_class_skills == actual_class_skills:
                    self.log(f"  {class_id}: {len(selected_skills)} skills allocated correctly", "PASS")
                else:
                    self.log(f"  {class_id}: Expected {expected_class_skills}, got {actual_class_skills}", "FAIL")
                    all_passed = False

                self.teardown()

            except Exception as e:
                self.log(f"  {class_id}: Exception - {e}", "FAIL")
                all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_species_skill_allocation(self):
        """Test that species skills are properly allocated."""
        test_name = "Species Skill Allocation"
        self.log(f"Testing: {test_name}")

        all_passed = True

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT species_id
                FROM species_proficiencies
                WHERE proficiency_type = 'skill'
                AND proficiency_name IS NOT NULL
            """)
            species_with_skills = [row[0] for row in cursor.fetchall()]

        if not species_with_skills:
            self.log("  No species with fixed skill proficiencies found - test skipped", "WARN")
            self.test_results.append({'test': test_name, 'passed': True})
            return True

        for species_id in species_with_skills:
            try:
                self.setup()
                self.create_test_character('fighter', 'soldier', species_id)

                expected_skills = self.get_expected_species_skills(species_id)

                class_skills = ['History', 'Insight']

                with sqlite3.connect(self.db_path) as conn:
                    success = self.proficiency_system.initialize_character_proficiencies(
                        self.test_character_id,
                        'fighter',
                        background='soldier',
                        race_id=species_id,
                        selected_skills=class_skills,
                        conn=conn
                    )
                    conn.commit()

                if not success:
                    self.log(f"  {species_id}: Failed to initialize proficiencies", "FAIL")
                    all_passed = False
                    continue

                skills_by_source = self.get_skills_from_db(self.test_character_id)
                actual_species_skills = set(skills_by_source.get('species', []))

                if expected_skills == actual_species_skills:
                    self.log(f"  {species_id}: {len(expected_skills)} skills allocated correctly", "PASS")
                else:
                    self.log(f"  {species_id}: Expected {expected_skills}, got {actual_species_skills}", "FAIL")
                    all_passed = False

                self.teardown()

            except Exception as e:
                self.log(f"  {species_id}: Exception - {e}", "FAIL")
                all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_no_duplicate_skills(self):
        """Test that no duplicate skills are allocated across sources."""
        test_name = "No Duplicate Skills Across Sources"
        self.log(f"Testing: {test_name}")

        all_passed = True

        try:
            self.setup()
            self.create_test_character('fighter', 'soldier', 'human')

            with sqlite3.connect(self.db_path) as conn:
                success = self.proficiency_system.initialize_character_proficiencies(
                    self.test_character_id,
                    'fighter',
                    background='soldier',
                    selected_skills=['Athletics', 'Perception'],
                    conn=conn
                )
                conn.commit()

            if not success:
                self.log("  Failed to initialize proficiencies", "FAIL")
                all_passed = False
            else:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT proficiency_name, COUNT(*) as count
                        FROM character_proficiencies
                        WHERE character_id = ? AND proficiency_type = 'skill'
                        GROUP BY proficiency_name
                        HAVING count > 1
                    """, (self.test_character_id,))

                    duplicates = cursor.fetchall()

                    if duplicates:
                        self.log(f"  Found {len(duplicates)} duplicate skills: {duplicates}", "FAIL")
                        all_passed = False
                    else:
                        self.log("  No duplicate skills found", "PASS")

            self.teardown()

        except Exception as e:
            self.log(f"  Exception - {e}", "FAIL")
            all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def test_skill_count_validation(self):
        """Test that characters receive the correct total number of skills."""
        test_name = "Skill Count Validation"
        self.log(f"Testing: {test_name}")

        test_cases = [
            {
                'class_id': 'fighter',
                'background_id': 'soldier',
                'race_id': 'human',
                'selected_skills': ['History', 'Insight'],
                'expected_skills': 4
            },
            {
                'class_id': 'rogue',
                'background_id': 'criminal',
                'race_id': 'human',
                'selected_skills': ['Acrobatics', 'Investigation', 'Perception', 'Sleight of Hand'],
                'expected_skills': 6
            },
            {
                'class_id': 'barbarian',
                'background_id': 'sage',
                'race_id': 'elf',
                'selected_skills': ['Athletics', 'Survival'],
                'expected_skills': 5
            }
        ]

        all_passed = True

        for test_case in test_cases:
            try:
                self.setup()
                self.create_test_character(
                    test_case['class_id'],
                    test_case['background_id'],
                    test_case['race_id']
                )

                with sqlite3.connect(self.db_path) as conn:
                    success = self.proficiency_system.initialize_character_proficiencies(
                        self.test_character_id,
                        test_case['class_id'],
                        background=test_case['background_id'],
                        race_id=test_case['race_id'],
                        selected_skills=test_case['selected_skills'],
                        conn=conn
                    )
                    conn.commit()

                if not success:
                    self.log(f"  {test_case['class_id']}: Failed to initialize", "FAIL")
                    all_passed = False
                    continue

                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(DISTINCT proficiency_name)
                        FROM character_proficiencies
                        WHERE character_id = ? AND proficiency_type = 'skill'
                    """, (self.test_character_id,))

                    total_skills = cursor.fetchone()[0]
                    expected = test_case['expected_skills']

                    if total_skills == expected:
                        self.log(f"  {test_case['class_id']}: {total_skills} skills (expected {expected})", "PASS")
                    else:
                        self.log(f"  {test_case['class_id']}: {total_skills} skills (expected {expected})", "FAIL")
                        all_passed = False

                self.teardown()

            except Exception as e:
                self.log(f"  {test_case['class_id']}: Exception - {e}", "FAIL")
                all_passed = False

        self.test_results.append({'test': test_name, 'passed': all_passed})
        return all_passed

    def run_all_tests(self):
        """Run all skill allocation tests."""
        self.log("=" * 60)
        self.log("SKILL ALLOCATION REGRESSION TESTS")
        self.log("=" * 60)

        tests = [
            self.test_background_skill_allocation,
            self.test_class_skill_allocation,
            self.test_species_skill_allocation,
            self.test_no_duplicate_skills,
            self.test_skill_count_validation,
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
        tester = SkillAllocationTester()
        exit_code = tester.run_all_tests()
        sys.exit(exit_code)
    except Exception as e:
        print(f"[FAIL] Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()