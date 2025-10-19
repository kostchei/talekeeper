#test
"""
Test Suite for Monster Attack Parser

Tests parsing of monster attacks from database JSON format.
Uses real monster data to ensure accurate parsing of D&D attack formats.
"""

import sys
import os
import unittest
import tempfile
import sqlite3
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.monster_attack_parser import MonsterAttackParser, ParsedAttack, AttackEffect


class TestMonsterAttackParser(unittest.TestCase):
    """Test the monster attack parsing system."""

    def setUp(self):
        """Set up test environment."""
        self.parser = MonsterAttackParser()

    def test_giant_spider_bite(self):
        """Test parsing Giant Spider's bite attack with poison save."""
        # Real data from our database
        actions_json = '''[
            {
                "name": "Bite",
                "entries": [
                    "{@atk mw} {@hit 5} to hit, reach 5 ft., one creature. {@h}7 ({@damage 1d8 + 3}) piercing damage, and the target must make a {@dc 11} Constitution saving throw, taking 9 ({@damage 2d8}) poison damage on a failed save, or half as much damage on a successful one. If the poison damage reduces the target to 0 hit points, the target is stable but {@condition poisoned} for 1 hour, even after regaining hit points, and is {@condition paralyzed} while {@condition poisoned} in this way."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        self.assertEqual(len(attacks), 1)

        bite = attacks[0]
        self.assertEqual(bite.name, "Bite")
        self.assertEqual(bite.attack_type, "melee")
        self.assertEqual(bite.attack_bonus, 5)
        self.assertEqual(bite.reach, 5)
        self.assertEqual(bite.damage_dice, "1d8 + 3")
        self.assertEqual(bite.damage_type, "piercing")

        # Check effects
        self.assertGreaterEqual(len(bite.effects), 1)

        # Should have save-or-damage effect
        save_effect = next((e for e in bite.effects if e.effect_type == "save_damage"), None)
        self.assertIsNotNone(save_effect)
        self.assertEqual(save_effect.save_dc, 11)
        self.assertEqual(save_effect.save_ability, "constitution")

        # Should have conditional poisoned effect
        poison_effect = next((e for e in bite.effects if e.condition == "poisoned"), None)
        self.assertIsNotNone(poison_effect)
        self.assertEqual(poison_effect.trigger, "reduced_to_0_hp_by_poison")

    def test_giant_spider_web(self):
        """Test parsing Giant Spider's web attack with restrained condition."""
        actions_json = '''[
            {
                "name": "Web",
                "entries": [
                    "{@atk rw} {@hit 5} to hit, range 30/60 ft., one creature. {@h}The target is {@condition restrained} by webbing. As an action, the {@condition restrained} target can make a {@dc 12} Strength check, bursting the webbing on a success. The webbing can also be attacked and destroyed (AC 10; hp 5; vulnerability to fire damage; immunity to bludgeoning, poison, and psychic damage)."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        self.assertEqual(len(attacks), 1)

        web = attacks[0]
        self.assertEqual(web.name, "Web")
        self.assertEqual(web.attack_type, "ranged")
        self.assertEqual(web.attack_bonus, 5)
        self.assertEqual(web.range_normal, 30)
        self.assertEqual(web.range_long, 60)

        # Should have automatic restrained effect
        restrained_effect = next((e for e in web.effects if e.condition == "restrained"), None)
        self.assertIsNotNone(restrained_effect)
        self.assertTrue(restrained_effect.automatic)

    def test_ankheg_bite_grapple(self):
        """Test parsing Ankheg's bite with automatic grapple."""
        actions_json = '''[
            {
                "name": "Bite",
                "entries": [
                    "{@atk mw} {@hit 5} to hit, reach 5 ft., one target. {@h}10 ({@damage 2d6 + 3}) slashing damage plus 3 ({@damage 1d6}) acid damage. If the target is a Large or smaller creature, it is {@condition grappled} (escape {@dc 13}). Until this grapple ends, the ankheg can bite only the {@condition grappled} creature and has advantage on attack rolls to do so."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        self.assertEqual(len(attacks), 1)

        bite = attacks[0]
        self.assertEqual(bite.name, "Bite")
        self.assertEqual(bite.damage_dice, "2d6 + 3")
        self.assertEqual(bite.damage_type, "slashing")

        # Check additional acid damage
        self.assertEqual(len(bite.additional_damage), 1)
        self.assertEqual(bite.additional_damage[0], ("1d6", "acid"))

        # Check grapple effect
        grapple_effect = next((e for e in bite.effects if e.condition == "grappled"), None)
        self.assertIsNotNone(grapple_effect)
        self.assertTrue(grapple_effect.automatic)
        self.assertEqual(grapple_effect.save_dc, 13)  # Escape DC

    def test_air_elemental_whirlwind(self):
        """Test parsing Air Elemental's whirlwind with prone effect."""
        actions_json = '''[
            {
                "name": "Whirlwind",
                "entries": [
                    "Each creature in the elemental's space must make a {@dc 13} Strength saving throw. On a failure, a target takes 15 ({@damage 3d8 + 2}) bludgeoning damage and is flung up 20 feet away from the elemental in a random direction and knocked {@condition prone}. If a thrown target strikes an object, such as a wall or floor, the target takes 3 ({@damage 1d6}) bludgeoning damage for every 10 feet it was thrown. If the target is thrown at another creature, that creature must succeed on a {@dc 13} Dexterity saving throw or take the same damage and be knocked {@condition prone}."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        self.assertEqual(len(attacks), 1)

        whirlwind = attacks[0]
        self.assertEqual(whirlwind.name, "Whirlwind")
        self.assertEqual(whirlwind.attack_type, "special")

        # Should have save-or-prone effect
        prone_effect = next((e for e in whirlwind.effects if e.condition == "prone"), None)
        self.assertIsNotNone(prone_effect)

    def test_ghast_claws_paralysis(self):
        """Test parsing Ghast's claws with paralysis save."""
        actions_json = '''[
            {
                "name": "Claws",
                "entries": [
                    "{@atk mw} {@hit 5} to hit, reach 5 ft., one target. {@h}10 ({@damage 2d6 + 3}) slashing damage. If the target is a creature other than an undead, it must succeed on a {@dc 10} Constitution saving throw or be {@condition paralyzed} for 1 minute. The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        self.assertEqual(len(attacks), 1)

        claws = attacks[0]
        self.assertEqual(claws.name, "Claws")
        self.assertEqual(claws.damage_dice, "2d6 + 3")
        self.assertEqual(claws.damage_type, "slashing")

        # Should have paralysis save effect
        paralysis_effect = next((e for e in claws.effects if e.condition == "paralyzed"), None)
        self.assertIsNotNone(paralysis_effect)
        self.assertEqual(paralysis_effect.save_dc, 10)
        self.assertEqual(paralysis_effect.save_ability, "constitution")

    def test_basilisk_bite_simple(self):
        """Test parsing Basilisk's simple bite (no special effects)."""
        actions_json = '''[
            {
                "name": "Bite",
                "entries": [
                    "{@atk mw} {@hit 5} to hit, reach 5 ft., one target. {@h}10 ({@damage 2d6 + 3}) piercing damage plus 7 ({@damage 2d6}) poison damage."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        self.assertEqual(len(attacks), 1)

        bite = attacks[0]
        self.assertEqual(bite.name, "Bite")
        self.assertEqual(bite.damage_dice, "2d6 + 3")
        self.assertEqual(bite.damage_type, "piercing")

        # Should have additional poison damage
        self.assertEqual(len(bite.additional_damage), 1)
        self.assertEqual(bite.additional_damage[0], ("2d6", "poison"))

        # Should have no special effects
        self.assertEqual(len(bite.effects), 0)

    def test_multiattack_parsing(self):
        """Test that multiattack entries are not parsed as attacks."""
        actions_json = '''[
            {
                "name": "Multiattack",
                "entries": [
                    "The creature makes two claw attacks."
                ]
            },
            {
                "name": "Claw",
                "entries": [
                    "{@atk mw} {@hit 6} to hit, reach 5 ft., one target. {@h}8 ({@damage 1d8 + 4}) slashing damage."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        # Should only parse the Claw attack, not Multiattack
        self.assertEqual(len(attacks), 1)
        self.assertEqual(attacks[0].name, "Claw")

    def test_non_attack_actions_ignored(self):
        """Test that non-attack actions are ignored."""
        actions_json = '''[
            {
                "name": "Spider Climb",
                "entries": [
                    "The spider can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check."
                ]
            },
            {
                "name": "Web Walker",
                "entries": [
                    "The spider ignores movement restrictions caused by webs."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        # Should parse no attacks
        self.assertEqual(len(attacks), 0)

    def test_complex_save_patterns(self):
        """Test parsing various save patterns from real monster data."""
        # Test the "Dexterity Saving Throw: DC X" pattern
        actions_json = '''[
            {
                "name": "Web",
                "entries": [
                    "Dexterity Saving Throw: DC 13, one creature the spider can see within 60 feet. Failure: The target has the {@condition restrained} condition until the web is destroyed."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        self.assertEqual(len(attacks), 1)

        web = attacks[0]
        self.assertEqual(web.name, "Web")

        # Should have save-based restrained effect
        restrained_effect = next((e for e in web.effects if e.condition == "restrained"), None)
        self.assertIsNotNone(restrained_effect)
        self.assertEqual(restrained_effect.save_dc, 13)
        self.assertEqual(restrained_effect.save_ability, "dexterity")

    def test_attack_summary(self):
        """Test attack summary generation."""
        actions_json = '''[
            {
                "name": "Longsword",
                "entries": [
                    "{@atk mw} {@hit 7} to hit, reach 5 ft., one target. {@h}11 ({@damage 2d8 + 2}) slashing damage."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)
        attack = attacks[0]

        summary = self.parser.get_attack_summary(attack)

        expected_parts = [
            "Longsword (melee)",
            "+7 to hit",
            "reach 5 ft",
            "2d8 + 2 slashing"
        ]

        for part in expected_parts:
            self.assertIn(part, summary)

    def test_parsing_errors_handled(self):
        """Test that parsing errors are handled gracefully."""
        # Invalid JSON
        invalid_json = "not valid json"
        attacks = self.parser.parse_monster_actions(invalid_json)
        self.assertEqual(len(attacks), 0)

        # Missing entries
        missing_entries = '''[{"name": "Test"}]'''
        attacks = self.parser.parse_monster_actions(missing_entries)
        self.assertEqual(len(attacks), 0)

        # Empty actions
        empty_actions = '''[]'''
        attacks = self.parser.parse_monster_actions(empty_actions)
        self.assertEqual(len(attacks), 0)

    def test_trample_attack_automatic_prone(self):
        """Test parsing trample attacks that automatically knock prone."""
        actions_json = '''[
            {
                "name": "Trample",
                "entries": [
                    "{@atk mw} {@hit 7} to hit, reach 5 ft., one prone creature. {@h}22 ({@damage 4d8 + 4}) bludgeoning damage. Target is knocked {@condition prone}."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        self.assertEqual(len(attacks), 1)

        trample = attacks[0]
        self.assertEqual(trample.name, "Trample")

        # Should have automatic prone effect
        prone_effect = next((e for e in trample.effects if e.condition == "prone"), None)
        self.assertIsNotNone(prone_effect)
        self.assertTrue(prone_effect.automatic)
        self.assertEqual(prone_effect.effect_type, "automatic_condition")

    def test_charge_attack_with_save(self):
        """Test parsing charge attacks that require saves to avoid prone."""
        actions_json = '''[
            {
                "name": "Charge",
                "entries": [
                    "{@atk mw} {@hit 6} to hit, reach 5 ft., one target. {@h}15 ({@damage 3d6 + 5}) bludgeoning damage. If the rhino moved at least 20 feet straight toward the target immediately before the hit, the target must make a {@dc 15} Strength saving throw or be knocked {@condition prone}."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        self.assertEqual(len(attacks), 1)

        charge = attacks[0]
        self.assertEqual(charge.name, "Charge")

        # Should have save-based prone effect
        prone_effect = next((e for e in charge.effects if e.condition == "prone"), None)
        self.assertIsNotNone(prone_effect)
        self.assertEqual(prone_effect.save_dc, 15)
        self.assertEqual(prone_effect.save_ability, "strength")
        self.assertEqual(prone_effect.effect_type, "save_condition")

    def test_size_based_grapple(self):
        """Test parsing size-based automatic grapple effects."""
        actions_json = '''[
            {
                "name": "Constrict",
                "entries": [
                    "{@atk mw} {@hit 6} to hit, reach 5 ft., one Large or smaller creature. {@h}13 ({@damage 2d8 + 4}) bludgeoning damage. If the target is a Large or smaller creature, it has the {@condition grappled} condition (escape {@dc 14})."
                ]
            }
        ]'''

        attacks = self.parser.parse_monster_actions(actions_json)

        self.assertEqual(len(attacks), 1)

        constrict = attacks[0]
        self.assertEqual(constrict.name, "Constrict")

        # Should have conditional automatic grapple
        grapple_effect = next((e for e in constrict.effects if e.condition == "grappled"), None)
        self.assertIsNotNone(grapple_effect)
        self.assertTrue(grapple_effect.automatic)
        self.assertEqual(grapple_effect.effect_type, "conditional_automatic")
        self.assertEqual(grapple_effect.trigger, "target_size_large_or_smaller")

    def test_automatic_vs_save_distinction(self):
        """Test that parser distinguishes automatic effects from save-based effects."""
        # Automatic effect
        auto_json = '''[
            {
                "name": "Slam",
                "entries": [
                    "{@atk mw} {@hit 5} to hit, reach 5 ft., one target. {@h}8 ({@damage 1d8 + 4}) bludgeoning damage. Target is {@condition stunned}."
                ]
            }
        ]'''

        # Save-based effect
        save_json = '''[
            {
                "name": "Sting",
                "entries": [
                    "{@atk mw} {@hit 5} to hit, reach 5 ft., one target. {@h}6 ({@damage 1d6 + 3}) piercing damage. Target must make a {@dc 12} Constitution saving throw or be {@condition stunned} for 1 minute."
                ]
            }
        ]'''

        auto_attacks = self.parser.parse_monster_actions(auto_json)
        save_attacks = self.parser.parse_monster_actions(save_json)

        # Automatic effect
        auto_effect = auto_attacks[0].effects[0]
        self.assertTrue(auto_effect.automatic)
        self.assertEqual(auto_effect.effect_type, "automatic_condition")

        # Save-based effect
        save_effect = save_attacks[0].effects[0]
        self.assertFalse(save_effect.automatic)
        self.assertEqual(save_effect.effect_type, "save_condition")
        self.assertEqual(save_effect.save_dc, 12)
        self.assertEqual(save_effect.save_ability, "constitution")

    def test_condition_mapping(self):
        """Test that condition names are mapped correctly."""
        # Test all standard conditions
        test_conditions = [
            "blinded", "charmed", "deafened", "frightened", "grappled",
            "incapacitated", "invisible", "paralyzed", "petrified",
            "poisoned", "prone", "restrained", "stunned", "unconscious"
        ]

        for condition in test_conditions:
            actions_json = f'''[
                {{
                    "name": "Test Attack",
                    "entries": [
                        "{{@atk mw}} {{@hit 5}} to hit, reach 5 ft., one target. {{@h}}5 ({{@damage 1d6 + 2}}) damage. Target is {{@condition {condition}}}."
                    ]
                }}
            ]'''

            attacks = self.parser.parse_monster_actions(actions_json)
            self.assertEqual(len(attacks), 1)

            effect = next((e for e in attacks[0].effects if e.condition == condition), None)
            self.assertIsNotNone(effect, f"Failed to parse {condition} condition")

    def test_damage_extraction_patterns(self):
        """Test various damage format patterns."""
        test_cases = [
            # Standard format
            ("{@h}7 ({@damage 1d8 + 3}) piercing", "1d8 + 3", "piercing"),
            # Simple format
            ("8 (2d4 + 3) slashing damage", "2d4 + 3", "slashing"),
            # Complex damage types
            ("10 ({@damage 2d6 + 3}) bludgeoning damage", "2d6 + 3", "bludgeoning"),
        ]

        for damage_text, expected_dice, expected_type in test_cases:
            dice, dmg_type = self.parser._extract_primary_damage(damage_text)
            self.assertEqual(dice, expected_dice)
            self.assertEqual(dmg_type, expected_type)


class TestDatabaseIntegration(unittest.TestCase):
    """Test parsing with real database monster data."""

    def setUp(self):
        """Set up database connection."""
        self.parser = MonsterAttackParser()
        self.db_path = "talekeeper.db"

    def test_parse_database_monsters(self):
        """Test parsing attacks from actual database monsters."""
        if not os.path.exists(self.db_path):
            self.skipTest("Database not available for integration testing")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get a few monsters with known interesting attacks
                test_monsters = [
                    "Giant Spider", "Ankheg", "Air Elemental",
                    "Ghast", "Basilisk"
                ]

                for monster_name in test_monsters:
                    cursor.execute(
                        "SELECT actions FROM monsters WHERE name = ? LIMIT 1",
                        (monster_name,)
                    )
                    row = cursor.fetchone()

                    if row and row[0]:
                        attacks = self.parser.parse_monster_actions(row[0])
                        self.assertGreater(len(attacks), 0, f"No attacks parsed for {monster_name}")

                        for attack in attacks:
                            # Basic validation
                            self.assertIsInstance(attack.name, str)
                            self.assertIsInstance(attack.attack_bonus, int)
                            self.assertIn(attack.attack_type, ["melee", "ranged", "special"])

                        print(f"[{monster_name}] Parsed {len(attacks)} attacks:")
                        for attack in attacks:
                            print(f"  - {self.parser.get_attack_summary(attack)}")

        except sqlite3.Error as e:
            self.skipTest(f"Database error: {e}")


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)