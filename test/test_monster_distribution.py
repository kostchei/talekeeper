#!/usr/bin/env python3
# test
"""
Comprehensive Monster Distribution System Tests

Tests the monster distribution functionality including:
- Campaign frame monster type weights
- Difficulty distribution
- Monster alignment filtering
- CR-based filtering
- XP budget calculations
- Encounter generation mechanics
"""

import sys
import os
import unittest
import random
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from encounter_pane.encounter_generator import EncounterGenerator, load_monsters, MONSTER_DB, XP_BUDGETS, CR_TO_XP
from encounter_pane.campaign_frame import CampaignFrame


class TestMonsterDistribution(unittest.TestCase):
    """Test suite for monster distribution system"""

    def setUp(self):
        """Set up test fixtures"""
        random.seed(42)  # For reproducible tests

        # Create test campaign frames
        self.balanced_frame = CampaignFrame({
            'monster_type_weights': {
                'humanoid': 0.3,
                'beast': 0.2,
                'monstrosity': 0.2,
                'undead': 0.15,
                'fiend': 0.15
            },
            'difficulty_distribution': {
                'low': 0.3,
                'moderate': 0.5,
                'high': 0.2
            },
            'monster_alignment_rules': {
                'allow_evil': True,
                'allow_humanoid_not_good': True
            }
        })

        self.good_only_frame = CampaignFrame({
            'monster_type_weights': {
                'humanoid': 0.4,
                'beast': 0.6
            },
            'difficulty_distribution': {
                'low': 0.4,
                'moderate': 0.6,
                'high': 0.0
            },
            'monster_alignment_rules': {
                'allow_evil': False,
                'allow_humanoid_not_good': False
            }
        })

        self.high_difficulty_frame = CampaignFrame({
            'monster_type_weights': {
                'dragon': 0.4,
                'fiend': 0.3,
                'undead': 0.3
            },
            'difficulty_distribution': {
                'low': 0.1,
                'moderate': 0.2,
                'high': 0.7
            },
            'monster_alignment_rules': {
                'allow_evil': True,
                'allow_humanoid_not_good': True
            }
        })

    def test_monster_database_loading(self):
        """Test that monsters are loaded correctly from database"""
        monsters = load_monsters()

        self.assertGreater(len(monsters), 0, "Should load monsters from database")

        # Verify monster structure
        monster = monsters[0]
        required_fields = ['name', 'cr', 'cr_str', 'xp', 'type', 'alignment', 'average_hp', 'hp_formula']
        for field in required_fields:
            self.assertIn(field, monster, f"Monster should have {field} field")

        # Verify CR to XP mapping works
        self.assertIsInstance(monster['xp'], int, "XP should be integer")
        self.assertGreaterEqual(monster['xp'], 0, "XP should be non-negative")

    def test_xp_budget_calculation(self):
        """Test XP budget calculations for different levels and difficulties"""
        generator = EncounterGenerator(self.balanced_frame)

        # Test level 1 budgets
        self.assertEqual(generator.get_budget(1, "low"), 50)
        self.assertEqual(generator.get_budget(1, "moderate"), 75)
        self.assertEqual(generator.get_budget(1, "high"), 100)

        # Test level 5 budgets
        self.assertEqual(generator.get_budget(5, "low"), 500)
        self.assertEqual(generator.get_budget(5, "moderate"), 750)
        self.assertEqual(generator.get_budget(5, "high"), 1100)

        # Test invalid level
        with self.assertRaises(ValueError):
            generator.get_budget(99, "low")

    def test_cr_filtering(self):
        """Test that monsters are filtered correctly by CR relative to party level"""
        generator = EncounterGenerator(self.balanced_frame)

        # Generate encounters for level 1 (CR cap = 0.25)
        encounters = [generator.generate_encounter(1) for _ in range(50)]

        for encounter in encounters:
            for monster in encounter['monsters']:
                self.assertLessEqual(monster['cr'], 0.25,
                    f"Level 1 encounter should not include CR {monster['cr']} monsters")

        # Generate encounters for level 10 (CR cap = 5.0)
        encounters = [generator.generate_encounter(10) for _ in range(50)]

        for encounter in encounters:
            for monster in encounter['monsters']:
                self.assertLessEqual(monster['cr'], 5.0,
                    f"Level 10 encounter should not include CR {monster['cr']} monsters")

    def test_alignment_filtering(self):
        """Test monster alignment filtering based on campaign frame rules"""
        # Test good-only campaign
        generator = EncounterGenerator(self.good_only_frame)
        encounters = [generator.generate_encounter(3) for _ in range(30)]

        for encounter in encounters:
            for monster in encounter['monsters']:
                alignment = monster.get('alignment', 'N').upper()
                self.assertNotIn('E', alignment,
                    f"Good-only campaign should not include evil monster: {monster['name']} ({alignment})")

                # If humanoid, should be good or neutral
                if monster['type'] == 'humanoid':
                    self.assertTrue('G' in alignment or alignment == 'N',
                        f"Humanoid in good campaign should be good/neutral: {monster['name']} ({alignment})")

    def test_difficulty_distribution(self):
        """Test that encounters are generated according to difficulty distribution"""
        generator = EncounterGenerator(self.high_difficulty_frame)

        # Generate many encounters to test distribution
        encounters = [generator.generate_encounter(5) for _ in range(200)]
        difficulty_counts = Counter(enc['difficulty'] for enc in encounters)

        total = len(encounters)
        low_ratio = difficulty_counts['low'] / total
        moderate_ratio = difficulty_counts['moderate'] / total
        high_ratio = difficulty_counts['high'] / total

        # Should roughly match the distribution (with some tolerance)
        self.assertLess(low_ratio, 0.25, "Should have few low difficulty encounters")
        self.assertLess(moderate_ratio, 0.4, "Should have some moderate encounters")
        self.assertGreater(high_ratio, 0.5, "Should have many high difficulty encounters")

    def test_high_difficulty_encounter_structure(self):
        """Test that high difficulty encounters follow single strong monster pattern"""
        generator = EncounterGenerator(self.balanced_frame)

        # Force high difficulty encounters
        original_weights = generator.frame.difficulty_distribution
        generator.frame.difficulty_distribution = {'low': 0, 'moderate': 0, 'high': 1.0}

        encounters = [generator.generate_encounter(5) for _ in range(50)]

        for encounter in encounters:
            if encounter['difficulty'] == 'high':
                self.assertEqual(len(encounter['monsters']), 1,
                    "High difficulty encounters should have exactly 1 monster")

                monster = encounter['monsters'][0]
                budget = generator.get_budget(5, "high")
                self.assertGreaterEqual(monster['xp'], budget * 0.8,
                    "High difficulty monster should use most of XP budget")

        # Restore original weights
        generator.frame.difficulty_distribution = original_weights

    def test_low_moderate_encounter_structure(self):
        """Test that low/moderate encounters can have multiple monsters"""
        generator = EncounterGenerator(self.balanced_frame)

        # Force low/moderate encounters
        generator.frame.difficulty_distribution = {'low': 0.5, 'moderate': 0.5, 'high': 0}

        encounters = [generator.generate_encounter(3) for _ in range(100)]

        multi_monster_count = 0
        for encounter in encounters:
            if len(encounter['monsters']) > 1:
                multi_monster_count += 1

                # Verify total XP doesn't exceed budget
                budget = generator.get_budget(3, encounter['difficulty'])
                self.assertLessEqual(encounter['total_xp'], budget,
                    "Total XP should not exceed budget")

                # Verify max 4 monsters
                self.assertLessEqual(len(encounter['monsters']), 4,
                    "Should not have more than 4 monsters")

        self.assertGreater(multi_monster_count, 0,
            "Should generate some multi-monster encounters")

    def test_monster_type_distribution(self):
        """Test that monster types follow campaign frame weights over many encounters"""
        # Create frame with specific type weights
        frame = CampaignFrame({
            'monster_type_weights': {
                'humanoid': 0.5,
                'beast': 0.3,
                'undead': 0.2
            },
            'difficulty_distribution': {'low': 0.3, 'moderate': 0.5, 'high': 0.2},
            'monster_alignment_rules': {'allow_evil': True, 'allow_humanoid_not_good': True}
        })

        generator = EncounterGenerator(frame)

        # Generate many encounters
        type_counts = defaultdict(int)
        total_monsters = 0

        for _ in range(200):
            encounter = generator.generate_encounter(4)
            for monster in encounter['monsters']:
                type_counts[monster['type']] += 1
                total_monsters += 1

        # Check that distribution roughly matches weights
        humanoid_ratio = type_counts['humanoid'] / total_monsters if total_monsters > 0 else 0
        beast_ratio = type_counts['beast'] / total_monsters if total_monsters > 0 else 0
        undead_ratio = type_counts['undead'] / total_monsters if total_monsters > 0 else 0

        # Allow some variance (±15%)
        self.assertGreater(humanoid_ratio, 0.35, "Should have significant humanoid presence")
        self.assertGreater(beast_ratio, 0.15, "Should have some beasts")
        self.assertGreater(undead_ratio, 0.05, "Should have some undead")

    def test_random_bag_system(self):
        """Test that RandomBag ensures variety in monster selection"""
        generator = EncounterGenerator(self.balanced_frame)

        # Generate encounters for the same level repeatedly
        monsters_seen = set()
        for _ in range(20):
            encounter = generator.generate_encounter(3)
            for monster in encounter['monsters']:
                monsters_seen.add(monster['name'])

        # Should see variety of monsters, not just the same ones
        self.assertGreater(len(monsters_seen), 5,
            "Should see variety of monsters due to RandomBag system")

    def test_encounter_xp_accuracy(self):
        """Test that encounter XP calculations are accurate"""
        generator = EncounterGenerator(self.balanced_frame)

        encounters = [generator.generate_encounter(2) for _ in range(50)]

        for encounter in encounters:
            # Calculate XP manually
            calculated_xp = sum(monster['xp'] for monster in encounter['monsters'])

            self.assertEqual(encounter['total_xp'], calculated_xp,
                "Encounter total_xp should match sum of monster XP")

            # Verify budget constraint
            budget = generator.get_budget(2, encounter['difficulty'])
            self.assertLessEqual(encounter['total_xp'], budget,
                "Encounter XP should not exceed budget")

    def test_monster_hp_calculation(self):
        """Test monster HP rolling and average HP usage"""
        from encounter_pane.encounter_generator import roll_monster_hp

        # Test dice formula parsing
        hp = roll_monster_hp("3d8")
        self.assertGreaterEqual(hp, 3, "3d8 should roll at least 3")
        self.assertLessEqual(hp, 24, "3d8 should roll at most 24")

        # Test with modifier
        hp = roll_monster_hp("2d6 + 3")
        self.assertGreaterEqual(hp, 5, "2d6+3 should roll at least 5")
        self.assertLessEqual(hp, 15, "2d6+3 should roll at most 15")

        # Test invalid formula
        hp = roll_monster_hp("invalid")
        self.assertEqual(hp, 8, "Invalid formula should return default HP")

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        generator = EncounterGenerator(self.balanced_frame)

        # Test with empty monster list (should handle gracefully)
        original_monster_db = generator.bags
        generator.bags = {}  # Clear bags to force regeneration

        # Temporarily reduce MONSTER_DB to test empty scenario
        import encounter_pane.encounter_generator as gen_module
        original_db = gen_module.MONSTER_DB
        gen_module.MONSTER_DB = []

        try:
            encounter = generator.generate_encounter(1)
            # Should handle empty monster list gracefully
            self.assertIsInstance(encounter, dict)
            self.assertIn('monsters', encounter)
        except Exception as e:
            # If it fails, that's also acceptable behavior
            self.assertIsInstance(e, (ValueError, IndexError))
        finally:
            # Restore original database
            gen_module.MONSTER_DB = original_db
            generator.bags = original_monster_db

    def test_campaign_frame_serialization(self):
        """Test that campaign frames can be serialized to/from JSON"""
        frame_data = self.balanced_frame.to_dict()

        # Verify all expected fields are present
        expected_fields = ['monster_type_weights', 'difficulty_distribution',
                          'monster_alignment_rules', 'name', 'rest_rules',
                          'style', 'available_classes', 'guaranteed_hoards']

        for field in expected_fields:
            self.assertIn(field, frame_data, f"Should include {field} in serialization")

        # Test round-trip serialization
        new_frame = CampaignFrame(frame_data)
        self.assertEqual(new_frame.monster_type_weights, self.balanced_frame.monster_type_weights)
        self.assertEqual(new_frame.difficulty_distribution, self.balanced_frame.difficulty_distribution)
        self.assertEqual(new_frame.monster_alignment_rules, self.balanced_frame.monster_alignment_rules)


class TestMonsterDistributionIntegration(unittest.TestCase):
    """Integration tests for the complete monster distribution system"""

    def setUp(self):
        """Set up integration test fixtures"""
        random.seed(12345)  # Different seed for integration tests

    def test_full_campaign_simulation(self):
        """Simulate a full campaign to test monster distribution over time"""
        # Create a realistic campaign frame
        campaign = CampaignFrame({
            'monster_type_weights': {
                'humanoid': 0.25,
                'beast': 0.20,
                'monstrosity': 0.15,
                'undead': 0.15,
                'fiend': 0.10,
                'dragon': 0.05,
                'aberration': 0.10
            },
            'difficulty_distribution': {
                'low': 0.25,
                'moderate': 0.50,
                'high': 0.25
            },
            'monster_alignment_rules': {
                'allow_evil': True,
                'allow_humanoid_not_good': True
            }
        })

        generator = EncounterGenerator(campaign)

        # Simulate encounters from level 1 to 10
        campaign_stats = {
            'total_encounters': 0,
            'total_monsters': 0,
            'difficulty_breakdown': defaultdict(int),
            'type_breakdown': defaultdict(int),
            'cr_breakdown': defaultdict(int)
        }

        for level in range(1, 11):
            # Generate 10 encounters per level
            for _ in range(10):
                encounter = generator.generate_encounter(level)

                campaign_stats['total_encounters'] += 1
                campaign_stats['total_monsters'] += len(encounter['monsters'])
                campaign_stats['difficulty_breakdown'][encounter['difficulty']] += 1

                for monster in encounter['monsters']:
                    campaign_stats['type_breakdown'][monster['type']] += 1
                    campaign_stats['cr_breakdown'][monster['cr']] += 1

        # Verify campaign-wide statistics
        self.assertEqual(campaign_stats['total_encounters'], 100)
        self.assertGreater(campaign_stats['total_monsters'], 100)

        # Verify difficulty distribution is reasonable
        total_enc = campaign_stats['total_encounters']
        low_pct = campaign_stats['difficulty_breakdown']['low'] / total_enc
        mod_pct = campaign_stats['difficulty_breakdown']['moderate'] / total_enc
        high_pct = campaign_stats['difficulty_breakdown']['high'] / total_enc

        self.assertGreater(low_pct, 0.15, "Should have some low difficulty encounters")
        self.assertGreater(mod_pct, 0.35, "Should have many moderate encounters")
        self.assertGreater(high_pct, 0.15, "Should have some high difficulty encounters")

        print(f"\nCampaign Simulation Results:")
        print(f"Total Encounters: {campaign_stats['total_encounters']}")
        print(f"Total Monsters: {campaign_stats['total_monsters']}")
        print(f"Difficulty Distribution: Low {low_pct:.2%}, Moderate {mod_pct:.2%}, High {high_pct:.2%}")
        print(f"Most Common Types: {dict(sorted(campaign_stats['type_breakdown'].items(), key=lambda x: x[1], reverse=True)[:5])}")


def run_monster_distribution_tests():
    """Run all monster distribution tests"""
    print("=" * 60)
    print("MONSTER DISTRIBUTION SYSTEM TESTS")
    print("=" * 60)

    # Change to project root
    os.chdir(Path(__file__).parent.parent)

    # Create test suite
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTest(unittest.makeSuite(TestMonsterDistribution))
    suite.addTest(unittest.makeSuite(TestMonsterDistributionIntegration))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall Result: {'PASS' if success else 'FAIL'}")

    return success


if __name__ == "__main__":
    success = run_monster_distribution_tests()
    sys.exit(0 if success else 1)