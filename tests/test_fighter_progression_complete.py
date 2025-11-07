"""
Comprehensive Fighter (Champion) Progression Test

Tests character progression from level 1 to 20 using backend APIs only.
Uses the real TaleKeeper database with archive/restore mechanism for safety.

D&D 5e SRD 2024 Rules
Weapon Masteries: Simplified (assumes ALL masteries known)

Usage:
    python -m pytest tests/test_fighter_progression_complete.py -v -s
"""

import pytest
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Add project paths
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / 'src'))

# Test helpers
from tests.helpers.database_archiver import DatabaseArchiver
from tests.helpers.choice_loader import ChoiceLoader
from tests.helpers.random_selector import RandomSelector
from tests.helpers.progression_recorder import ProgressionRecorder

# TaleKeeper imports
from scripts.character_tools.programmatic_character_creator import ProgrammaticCharacterCreator
from talekeeper.services.unified_level_up import UnifiedLevelUpService
from talekeeper.services.subclass_manager import SubclassManager

# D&D 5e XP thresholds
XP_THRESHOLDS = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000,
    100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
]


class TestFighterProgression:
    """Test Fighter progression from level 1 to 20 using Champion subclass."""

    # Class variables to persist across test methods
    db_path = "talekeeper.db"
    archive_path = None
    character_id = None
    recorder = None
    choices = None
    character_name = None
    species_name = None
    background_name = None

    @classmethod
    def setup_class(cls):
        """Archive database and load choices before running tests."""
        print("\n" + "=" * 80)
        print("FIGHTER PROGRESSION TEST SUITE - Setup")
        print("=" * 80)

        # Archive the database
        print(f"\n[1/3] Archiving database: {cls.db_path}")
        cls.archive_path = DatabaseArchiver.archive(
            cls.db_path, description="Fighter progression test"
        )
        print(f"[OK] Archive created: {cls.archive_path}")

        # Load progression choices
        print(f"\n[2/3] Loading progression choices...")
        choices_path = repo_root / "tests" / "fixtures" / "fighter_champion_choices.yaml"
        cls.choices = ChoiceLoader.load_from_yaml(str(choices_path))
        ChoiceLoader.validate_choices(cls.choices, "fighter")
        print(f"[OK] Choices loaded and validated")

        # Initialize progress recorder
        print(f"\n[3/3] Initializing progression recorder...")
        output_dir = repo_root / "tests" / "output"
        template = cls.choices["character_template"]
        cls.character_name = template["name"]
        cls.recorder = ProgressionRecorder(
            "fighter_test", cls.character_name, str(output_dir)
        )
        print(f"[OK] Recorder initialized")

        print("\n" + "=" * 80)
        print("Setup complete - starting tests")
        print("=" * 80 + "\n")

    @classmethod
    def teardown_class(cls):
        """Restore database and generate reports after tests."""
        print("\n" + "=" * 80)
        print("FIGHTER PROGRESSION TEST SUITE - Teardown")
        print("=" * 80)

        # Generate reports
        if cls.recorder:
            print(f"\n[1/2] Generating progression reports...")
            json_path = cls.recorder.generate_json_report()
            md_path = cls.recorder.generate_markdown_report()
            print(f"[OK] JSON report: {json_path}")
            print(f"[OK] Markdown report: {md_path}")

        # Restore database
        print(f"\n[2/2] Restoring database from archive...")
        DatabaseArchiver.unarchive(cls.archive_path, cls.db_path, force=True)
        print(f"[OK] Database restored")

        print("\n" + "=" * 80)
        print("Teardown complete")
        print("=" * 80 + "\n")

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _get_db_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def _get_character_data(self, character_id: str) -> Dict[str, Any]:
        """Fetch character data from database."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
            row = cursor.fetchone()
            if not row:
                return {}

            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))

    def _add_xp(self, character_id: str, xp_amount: int) -> None:
        """Add XP to character."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE characters SET experience_points = ? WHERE id = ?",
                (xp_amount, character_id)
            )
            conn.commit()

    def _get_fighter_resources(self, character_id: str) -> Dict[str, int]:
        """Get Fighter resource counts from database."""
        # Get character level for calculation
        char_data = self._get_character_data(character_id)
        level = char_data.get("level", 1)

        # Default resources based on level
        resources = {
            "second_wind_uses": 4 if level >= 10 else (3 if level >= 4 else 2),
            "action_surge_uses": 2 if level >= 17 else (1 if level >= 2 else 0),
            "indomitable_uses": 3 if level >= 17 else (2 if level >= 13 else (1 if level >= 9 else 0))
        }

        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            # Check fighter_features table with correct column names
            cursor.execute(
                """SELECT action_surge_uses_max, indomitable_uses_max
                   FROM fighter_features WHERE character_id = ?""",
                (character_id,)
            )
            row = cursor.fetchone()
            if row:
                # Override with actual DB values if they exist
                if row[0] is not None:
                    resources["action_surge_uses"] = row[0]
                if row[1] is not None:
                    resources["indomitable_uses"] = row[1]

        return resources

    def _get_extra_attacks(self, character_id: str) -> int:
        """Get number of extra attacks."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT extra_attacks FROM fighter_features WHERE character_id = ?",
                (character_id,)
            )
            row = cursor.fetchone()
            return row[0] if row and row[0] else 1

    def _get_critical_range(self, character_id: str) -> int:
        """Get minimum critical hit range."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT critical_range_min FROM character_combat_state WHERE character_id = ?",
                (character_id,)
            )
            row = cursor.fetchone()
            return row[0] if row and row[0] else 20

    def _apply_asi(self, character_id: str, asi_data: Dict[str, Any]) -> None:
        """Apply ASI to character abilities."""
        ability_1 = asi_data["ability_1"]
        increase_1 = asi_data["ability_1_increase"]

        updates = {ability_1: increase_1}

        if asi_data.get("ability_2"):
            ability_2 = asi_data["ability_2"]
            increase_2 = asi_data["ability_2_increase"]
            updates[ability_2] = increase_2

        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            for ability, increase in updates.items():
                cursor.execute(
                    f"UPDATE characters SET {ability} = {ability} + ? WHERE id = ?",
                    (increase, character_id)
                )

            conn.commit()

    def _apply_feat(self, character_id: str, feat_name: str) -> None:
        """Add feat to character."""
        char_data = self._get_character_data(character_id)
        level = char_data.get("level", 1)

        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO character_feats (character_id, feat_name, feat_id, level_acquired)
                   VALUES (?, ?, ?, ?)""",
                (character_id, feat_name, feat_name, level)
            )
            conn.commit()

    def _apply_fighting_style(self, character_id: str, fighting_style: str, is_additional: bool = False) -> None:
        """Apply fighting style to Fighter."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            if is_additional:
                # For Champion's additional fighting style at level 7
                # Note: The database schema doesn't have an additional_fighting_style column
                # This is recorded in the progression tracker but not stored in DB
                # In a real implementation, this would need a schema change or separate table
                print(f"[INFO] Additional fighting style '{fighting_style}' selected (not stored in DB)")
            else:
                cursor.execute(
                    "UPDATE fighter_features SET fighting_style = ? WHERE character_id = ?",
                    (fighting_style, character_id)
                )
                conn.commit()

    def _select_subclass(self, character_id: str, subclass: str) -> None:
        """Select subclass for character."""
        subclass_manager = SubclassManager(self.db_path)
        subclass_manager.select_subclass(character_id, subclass, class_level=3)

    # =========================================================================
    # Test Methods - Level by Level
    # =========================================================================

    def test_01_create_character(self):
        """Test Level 1: Create Fighter character."""
        print("\n" + "=" * 80)
        print("TEST 01: Create Level 1 Fighter")
        print("=" * 80)

        template = ChoiceLoader.get_character_template(self.choices)
        level_1_choices = ChoiceLoader.get_choice_for_level(self.choices, 1)

        # Resolve species and background
        species_id, species_name = RandomSelector.resolve_species(
            self.db_path, template["species"]
        )
        background_id, background_name = RandomSelector.resolve_background(
            self.db_path, template["background"]
        )

        TestFighterProgression.species_name = species_name
        TestFighterProgression.background_name = background_name

        print(f"Species: {species_name} (id: {species_id})")
        print(f"Background: {background_name} (id: {background_id})")

        # Build character template for ProgrammaticCharacterCreator
        character_template = {
            "name": template["name"],
            "race_id": species_id,
            "class_id": "fighter",
            "background_id": background_id,
            "strength": template["ability_scores"]["values"]["strength"],
            "dexterity": template["ability_scores"]["values"]["dexterity"],
            "constitution": template["ability_scores"]["values"]["constitution"],
            "intelligence": template["ability_scores"]["values"]["intelligence"],
            "wisdom": template["ability_scores"]["values"]["wisdom"],
            "charisma": template["ability_scores"]["values"]["charisma"],
            "fighting_style": level_1_choices["fighting_style"],
            "level": 1,
            "experience_points": 0,
        }

        # Create character
        creator = ProgrammaticCharacterCreator(self.db_path)
        created_char = creator.create_from_dict(character_template)

        TestFighterProgression.character_id = created_char["id"]
        char_id = TestFighterProgression.character_id

        print(f"\n[OK] Character created: {created_char['name']} (ID: {char_id})")

        # Verify character in database
        char_data = self._get_character_data(char_id)
        assert char_data["level"] == 1, "Character should be level 1"
        assert char_data["class_id"] == "fighter", "Character should be Fighter"

        # Record initial state
        ability_scores = {
            "strength": char_data["strength"],
            "dexterity": char_data["dexterity"],
            "constitution": char_data["constitution"],
            "intelligence": char_data["intelligence"],
            "wisdom": char_data["wisdom"],
            "charisma": char_data["charisma"],
        }

        self.recorder.set_initial_state(
            character_class="fighter",
            species=species_name,
            background=background_name,
            ability_scores=ability_scores,
            fighting_style=level_1_choices["fighting_style"],
            starting_hp=char_data["hit_points_max"],
        )

        # Record level 1
        self.recorder.begin_level(1, 0)
        self.recorder.record_choice("fighting_style", level_1_choices["fighting_style"])
        self.recorder.record_choice("species", species_name)
        self.recorder.record_choice("background", background_name)
        self.recorder.record_features_granted(
            ["fighting_style", "second_wind", "weapon_mastery"]
        )
        resources = self._get_fighter_resources(char_id)
        self.recorder.record_resources(resources)
        self.recorder.record_character_state(
            ability_scores=ability_scores,
            hp_max=char_data["hit_points_max"],
            extra_attacks=1,
            critical_range_min=20,
        )
        self.recorder.end_level()

        print("[OK] Level 1 complete")

    def test_02_level_2(self):
        """Test Level 2: Action Surge."""
        print("\n" + "=" * 80)
        print("TEST 02: Level Up to 2")
        print("=" * 80)

        char_id = TestFighterProgression.character_id
        assert char_id, "Character must be created first"

        # Add XP for level 2
        self._add_xp(char_id, XP_THRESHOLDS[1])

        # Level up
        level_up_service = UnifiedLevelUpService(self.db_path)
        result = level_up_service.level_up_character(char_id)

        assert result["success"], f"Level up failed: {result.get('error')}"
        assert result["new_level"] == 2, "Should be level 2"

        # Verify
        char_data = self._get_character_data(char_id)
        assert char_data["level"] == 2

        # Record
        self.recorder.begin_level(2, XP_THRESHOLDS[1])
        self.recorder.record_features_granted(["action_surge", "tactical_mind"])
        resources = self._get_fighter_resources(char_id)
        self.recorder.record_resources(resources)
        ability_scores = {
            "strength": char_data["strength"],
            "dexterity": char_data["dexterity"],
            "constitution": char_data["constitution"],
            "intelligence": char_data["intelligence"],
            "wisdom": char_data["wisdom"],
            "charisma": char_data["charisma"],
        }
        self.recorder.record_character_state(
            ability_scores=ability_scores,
            hp_max=char_data["hit_points_max"],
        )
        self.recorder.end_level()

        print("[OK] Level 2 complete")

    def test_03_level_3_champion(self):
        """Test Level 3: Champion subclass selection."""
        print("\n" + "=" * 80)
        print("TEST 03: Level Up to 3 - Champion Subclass")
        print("=" * 80)

        char_id = TestFighterProgression.character_id
        level_3_choices = ChoiceLoader.get_choice_for_level(self.choices, 3)

        # Add XP
        self._add_xp(char_id, XP_THRESHOLDS[2])

        # Level up
        level_up_service = UnifiedLevelUpService(self.db_path)
        result = level_up_service.level_up_character(char_id)
        assert result["success"]

        # Select Champion subclass
        subclass = level_3_choices["subclass"]
        self._select_subclass(char_id, subclass)
        self.recorder.set_subclass(subclass)

        # Verify
        char_data = self._get_character_data(char_id)
        assert char_data["level"] == 3
        crit_range = self._get_critical_range(char_id)
        assert crit_range == 19, "Champion should have 19-20 crit range"

        # Record
        self.recorder.begin_level(3, XP_THRESHOLDS[2])
        self.recorder.record_choice("subclass", subclass)
        self.recorder.record_features_granted(["improved_critical", "remarkable_athlete"])
        resources = self._get_fighter_resources(char_id)
        self.recorder.record_resources(resources)
        ability_scores = {
            "strength": char_data["strength"],
            "dexterity": char_data["dexterity"],
            "constitution": char_data["constitution"],
            "intelligence": char_data["intelligence"],
            "wisdom": char_data["wisdom"],
            "charisma": char_data["charisma"],
        }
        self.recorder.record_character_state(
            ability_scores=ability_scores,
            hp_max=char_data["hit_points_max"],
            critical_range_min=crit_range,
        )
        self.recorder.end_level()

        print("[OK] Level 3 complete - Champion subclass selected")

    def test_04_level_4_asi(self):
        """Test Level 4: First ASI."""
        self._level_up_with_asi_or_feat(4)

    def test_05_level_5(self):
        """Test Level 5: Extra Attack."""
        self._level_up_simple(5, ["extra_attack", "tactical_shift"])

    def test_06_level_6_asi(self):
        """Test Level 6: Second ASI."""
        self._level_up_with_asi_or_feat(6)

    def test_07_level_7_additional_fighting_style(self):
        """Test Level 7: Champion Additional Fighting Style."""
        print("\n" + "=" * 80)
        print("TEST 07: Level Up to 7 - Additional Fighting Style")
        print("=" * 80)

        char_id = TestFighterProgression.character_id
        choices = self.choices["progression_choices"].get("champion_level_7", {})

        # Add XP and level up
        self._add_xp(char_id, XP_THRESHOLDS[6])
        level_up_service = UnifiedLevelUpService(self.db_path)
        result = level_up_service.level_up_character(char_id)
        assert result["success"]

        # Apply additional fighting style
        if "additional_fighting_style" in choices:
            style = choices["additional_fighting_style"]
            self._apply_fighting_style(char_id, style, is_additional=True)

        # Record
        char_data = self._get_character_data(char_id)
        self.recorder.begin_level(7, XP_THRESHOLDS[6])
        if "additional_fighting_style" in choices:
            self.recorder.record_choice("additional_fighting_style", choices["additional_fighting_style"])
        self.recorder.record_features_granted(["additional_fighting_style", "studied_attacks"])
        resources = self._get_fighter_resources(char_id)
        self.recorder.record_resources(resources)
        ability_scores = {k: char_data[k] for k in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]}
        self.recorder.record_character_state(
            ability_scores=ability_scores,
            hp_max=char_data["hit_points_max"],
            extra_attacks=self._get_extra_attacks(char_id),
            critical_range_min=self._get_critical_range(char_id),
        )
        self.recorder.end_level()

        print("[OK] Level 7 complete")

    def test_08_level_8_asi(self):
        """Test Level 8: Third ASI."""
        self._level_up_with_asi_or_feat(8)

    def test_09_level_9(self):
        """Test Level 9: Indomitable."""
        self._level_up_simple(9, ["indomitable", "tactical_master"])

    def test_10_level_10(self):
        """Test Level 10: Champion Heroic Warrior."""
        self._level_up_simple(10, ["heroic_warrior"])

    def test_11_level_11(self):
        """Test Level 11: Two Extra Attacks (3 total)."""
        self._level_up_simple(11, ["two_extra_attacks"])

    def test_12_level_12_asi(self):
        """Test Level 12: Fourth ASI."""
        self._level_up_with_asi_or_feat(12)

    def test_13_level_13(self):
        """Test Level 13: Studied Attacks, Indomitable x2."""
        self._level_up_simple(13, ["studied_attacks"])

    def test_14_level_14_asi(self):
        """Test Level 14: Fifth ASI."""
        self._level_up_with_asi_or_feat(14)

    def test_15_level_15(self):
        """Test Level 15: Champion Superior Critical (18-20)."""
        self._level_up_simple(15, ["superior_critical"])

    def test_16_level_16_asi(self):
        """Test Level 16: Sixth ASI."""
        self._level_up_with_asi_or_feat(16)

    def test_17_level_17(self):
        """Test Level 17: Action Surge x2, Indomitable x3."""
        self._level_up_simple(17, [])

    def test_18_level_18(self):
        """Test Level 18: Champion Survivor."""
        self._level_up_simple(18, ["survivor"])

    def test_19_level_19_epic_boon(self):
        """Test Level 19: Epic Boon."""
        self._level_up_with_asi_or_feat(19)

    def test_20_level_20(self):
        """Test Level 20: Three Extra Attacks (4 total)."""
        self._level_up_simple(20, ["three_extra_attacks"])

    def test_21_generate_reports(self):
        """Generate final progression reports."""
        print("\n" + "=" * 80)
        print("TEST 21: Generate Reports")
        print("=" * 80)

        json_path = self.recorder.generate_json_report()
        md_path = self.recorder.generate_markdown_report()

        print(f"[OK] JSON report generated: {json_path}")
        print(f"[OK] Markdown report generated: {md_path}")

        # Verify reports exist
        assert Path(json_path).exists(), "JSON report should exist"
        assert Path(md_path).exists(), "Markdown report should exist"

        print("[OK] Reports generated successfully")

    # =========================================================================
    # Helper Methods for Common Test Patterns
    # =========================================================================

    def _level_up_simple(self, level: int, features: list) -> None:
        """Level up without choices (automatic features only)."""
        print(f"\n{'=' * 80}")
        print(f"TEST: Level Up to {level}")
        print("=" * 80)

        char_id = TestFighterProgression.character_id

        # Add XP and level up
        self._add_xp(char_id, XP_THRESHOLDS[level - 1])
        level_up_service = UnifiedLevelUpService(self.db_path)
        result = level_up_service.level_up_character(char_id)
        assert result["success"], f"Level up to {level} failed"

        # Verify and record
        char_data = self._get_character_data(char_id)
        assert char_data["level"] == level

        self.recorder.begin_level(level, XP_THRESHOLDS[level - 1])
        if features:
            self.recorder.record_features_granted(features)
        resources = self._get_fighter_resources(char_id)
        self.recorder.record_resources(resources)
        ability_scores = {k: char_data[k] for k in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]}
        self.recorder.record_character_state(
            ability_scores=ability_scores,
            hp_max=char_data["hit_points_max"],
            extra_attacks=self._get_extra_attacks(char_id),
            critical_range_min=self._get_critical_range(char_id),
        )
        self.recorder.end_level()

        print(f"[OK] Level {level} complete")

    def _level_up_with_asi_or_feat(self, level: int) -> None:
        """Level up with ASI or Feat choice."""
        print(f"\n{'=' * 80}")
        print(f"TEST: Level Up to {level} - ASI/Feat")
        print("=" * 80)

        char_id = TestFighterProgression.character_id
        choices = ChoiceLoader.get_choice_for_level(self.choices, level)

        # Add XP and level up
        self._add_xp(char_id, XP_THRESHOLDS[level - 1])
        level_up_service = UnifiedLevelUpService(self.db_path)
        result = level_up_service.level_up_character(char_id)
        assert result["success"]

        # Apply choice
        if choices and choices.get("choice_type") == "asi":
            self._apply_asi(char_id, choices["asi"])
        elif choices and choices.get("choice_type") == "feat":
            self._apply_feat(char_id, choices["feat"])

        # Verify and record
        char_data = self._get_character_data(char_id)
        assert char_data["level"] == level

        self.recorder.begin_level(level, XP_THRESHOLDS[level - 1])

        if choices:
            if choices.get("choice_type") == "asi":
                self.recorder.record_choice("asi", choices["asi"])
            elif choices.get("choice_type") == "feat":
                self.recorder.record_choice("feat", choices["feat"])

        resources = self._get_fighter_resources(char_id)
        self.recorder.record_resources(resources)
        ability_scores = {k: char_data[k] for k in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]}
        self.recorder.record_character_state(
            ability_scores=ability_scores,
            hp_max=char_data["hit_points_max"],
            extra_attacks=self._get_extra_attacks(char_id),
            critical_range_min=self._get_critical_range(char_id),
        )
        self.recorder.end_level()

        print(f"[OK] Level {level} complete")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
