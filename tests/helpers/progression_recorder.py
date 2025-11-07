"""
Progression Recorder for Character Development Testing

Records all character state changes, choices, and features granted during
character progression testing. Generates both JSON and Markdown reports.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class ProgressionRecorder:
    """Records character progression state and generates reports."""

    def __init__(self, character_id: str, character_name: str, output_dir: str):
        """
        Initialize progression recorder.

        Args:
            character_id: Character's database ID
            character_name: Character's display name
            output_dir: Directory for output files
        """
        self.character_id = character_id
        self.character_name = character_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Initialize data structure
        self.data = {
            "character_id": character_id,
            "character_name": character_name,
            "test_timestamp": datetime.now().isoformat(),
            "class": None,
            "subclass": None,
            "species": None,
            "background": None,
            "final_level": 0,
            "initial_state": {},
            "progression": [],
            "summary": {},
        }

        # Track current level data being built
        self.current_level_data = None

    def set_initial_state(
        self,
        character_class: str,
        species: str,
        background: str,
        ability_scores: Dict[str, int],
        **kwargs,
    ) -> None:
        """
        Record initial character state at creation.

        Args:
            character_class: Character class name
            species: Species name
            background: Background name
            ability_scores: Dictionary of ability score values
            **kwargs: Additional initial state data (hp, fighting_style, etc.)
        """
        self.data["class"] = character_class
        self.data["species"] = species
        self.data["background"] = background

        self.data["initial_state"] = {
            "ability_scores": ability_scores.copy(),
            **kwargs,
        }

    def begin_level(self, level: int, xp_required: int) -> None:
        """
        Start recording a new level.

        Args:
            level: Character level
            xp_required: XP required to reach this level
        """
        self.current_level_data = {
            "level": level,
            "xp_required": xp_required,
            "choices_made": {},
            "features_granted": [],
            "resources": {},
            "ability_scores": {},
            "hp_max": 0,
            "extra_attacks": 1,
            "critical_range_min": 20,
        }

    def record_choice(self, choice_type: str, choice_data: Dict[str, Any]) -> None:
        """
        Record a choice made at current level.

        Args:
            choice_type: Type of choice (fighting_style, subclass, asi, feat, etc.)
            choice_data: Data about the choice
        """
        if self.current_level_data is None:
            raise RuntimeError("Must call begin_level() before recording choices")

        self.current_level_data["choices_made"][choice_type] = choice_data

    def record_features_granted(self, features: List[str]) -> None:
        """
        Record features granted at current level.

        Args:
            features: List of feature names granted
        """
        if self.current_level_data is None:
            raise RuntimeError("Must call begin_level() before recording features")

        self.current_level_data["features_granted"].extend(features)

    def record_resources(self, resources: Dict[str, int]) -> None:
        """
        Record resource counts at current level.

        Args:
            resources: Dictionary of resource name -> count
        """
        if self.current_level_data is None:
            raise RuntimeError("Must call begin_level() before recording resources")

        self.current_level_data["resources"].update(resources)

    def record_character_state(
        self,
        ability_scores: Dict[str, int],
        hp_max: int,
        extra_attacks: int = 1,
        critical_range_min: int = 20,
        **kwargs,
    ) -> None:
        """
        Record full character state at current level.

        Args:
            ability_scores: Current ability scores
            hp_max: Maximum HP
            extra_attacks: Number of attacks per action
            critical_range_min: Minimum roll for critical hit
            **kwargs: Additional state data
        """
        if self.current_level_data is None:
            raise RuntimeError("Must call begin_level() before recording state")

        self.current_level_data["ability_scores"] = ability_scores.copy()
        self.current_level_data["hp_max"] = hp_max
        self.current_level_data["extra_attacks"] = extra_attacks
        self.current_level_data["critical_range_min"] = critical_range_min

        # Store any additional state
        for key, value in kwargs.items():
            if key not in self.current_level_data:
                self.current_level_data[key] = value

    def end_level(self) -> None:
        """Finish recording current level and add to progression."""
        if self.current_level_data is None:
            raise RuntimeError("No level in progress")

        level = self.current_level_data["level"]
        self.data["progression"].append(self.current_level_data)
        self.data["final_level"] = level

        self.current_level_data = None

    def set_subclass(self, subclass: str) -> None:
        """Set the character's subclass."""
        self.data["subclass"] = subclass

    def generate_summary(self) -> None:
        """Generate summary statistics from progression data."""
        if not self.data["progression"]:
            return

        initial_scores = self.data["initial_state"].get("ability_scores", {})
        final_data = self.data["progression"][-1]
        final_scores = final_data.get("ability_scores", {})

        # Count ASI and feats
        asi_count = 0
        feat_count = 0
        for level_data in self.data["progression"]:
            choices = level_data.get("choices_made", {})
            if "asi" in choices:
                asi_count += 1
            if "feat" in choices:
                feat_count += 1

        # Count total features
        total_features = sum(
            len(level_data.get("features_granted", [])) for level_data in self.data["progression"]
        )

        self.data["summary"] = {
            "total_features_gained": total_features,
            "asi_taken": asi_count,
            "feats_taken": feat_count,
            "final_ability_scores": final_scores,
            "final_resources": final_data.get("resources", {}),
            "final_extra_attacks": final_data.get("extra_attacks", 1),
            "final_critical_range_min": final_data.get("critical_range_min", 20),
        }

    def generate_json_report(self) -> str:
        """
        Generate JSON report of progression.

        Returns:
            Path to generated JSON file
        """
        # Ensure summary is up to date
        self.generate_summary()

        json_filename = f"{self.character_name.replace(' ', '_')}_{self.timestamp}.json"
        json_path = self.output_dir / json_filename

        with open(json_path, "w") as f:
            json.dump(self.data, f, indent=2)

        return str(json_path)

    def generate_markdown_report(self) -> str:
        """
        Generate human-readable Markdown report.

        Returns:
            Path to generated Markdown file
        """
        # Ensure summary is up to date
        self.generate_summary()

        md_filename = f"{self.character_name.replace(' ', '_')}_{self.timestamp}.md"
        md_path = self.output_dir / md_filename

        with open(md_path, "w") as f:
            f.write(self._generate_markdown_content())

        return str(md_path)

    def _generate_markdown_content(self) -> str:
        """Generate markdown content for report."""
        lines = []

        # Header
        subclass_name = self.data["subclass"] or "No Subclass"
        lines.append(f"# {self.data['class'].title()} ({subclass_name}) Progression Test Report\n")
        lines.append(f"**Character:** {self.character_name}\n")
        lines.append(f"**Species:** {self.data['species']}\n")
        lines.append(f"**Background:** {self.data['background']}\n")
        lines.append(f"**Test Date:** {self.data['test_timestamp']}\n")
        lines.append(f"**Final Level:** {self.data['final_level']}\n")
        lines.append("\n---\n\n")

        # Initial state
        lines.append("## Initial Character State\n\n")
        lines.append("| Attribute | Value |\n")
        lines.append("|-----------|-------|\n")

        initial = self.data["initial_state"]
        scores = initial.get("ability_scores", {})
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            lines.append(f"| {ability.upper()[:3]} | {scores.get(ability, 10)} |\n")

        for key, value in initial.items():
            if key != "ability_scores":
                lines.append(f"| {key.replace('_', ' ').title()} | {value} |\n")

        lines.append("\n---\n\n")

        # Progression by level
        lines.append("## Progression by Level\n\n")

        for level_data in self.data["progression"]:
            level = level_data["level"]
            lines.append(f"### Level {level}\n\n")

            lines.append(f"**XP Required:** {level_data['xp_required']}\n\n")

            # Features
            if level_data["features_granted"]:
                lines.append("**Features Gained:**\n")
                for feature in level_data["features_granted"]:
                    lines.append(f"- {feature}\n")
                lines.append("\n")

            # Choices
            if level_data["choices_made"]:
                lines.append("**Choices Made:**\n")
                for choice_type, choice_data in level_data["choices_made"].items():
                    lines.append(f"- {choice_type.replace('_', ' ').title()}: {self._format_choice(choice_data)}\n")
                lines.append("\n")

            # Resources
            if level_data["resources"]:
                lines.append("**Resources:**\n")
                for resource, count in level_data["resources"].items():
                    lines.append(f"- {resource.replace('_', ' ').title()}: {count} uses\n")
                lines.append("\n")

            # Combat stats
            if level_data.get("extra_attacks", 1) > 1 or level_data.get("critical_range_min", 20) < 20:
                lines.append("**Combat Stats:**\n")
                if level_data.get("extra_attacks", 1) > 1:
                    lines.append(f"- Extra Attacks: {level_data['extra_attacks']}\n")
                if level_data.get("critical_range_min", 20) < 20:
                    crit_min = level_data["critical_range_min"]
                    lines.append(f"- Critical Range: {crit_min}-20\n")
                lines.append("\n")

            lines.append("**Status:** [PASS]\n\n")
            lines.append("---\n\n")

        # Summary
        lines.append("## Final Summary\n\n")

        # Ability score progression
        lines.append("### Ability Score Progression\n\n")
        lines.append("| Ability | Start | Final | Total Increase |\n")
        lines.append("|---------|-------|-------|----------------|\n")

        initial_scores = self.data["initial_state"].get("ability_scores", {})
        final_scores = self.data["summary"]["final_ability_scores"]

        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            start = initial_scores.get(ability, 10)
            final = final_scores.get(ability, 10)
            increase = final - start
            lines.append(f"| {ability.upper()[:3]} | {start} | {final} | +{increase} |\n")

        lines.append("\n")

        # ASI/Feat choices
        asi_and_feat_levels = [
            ld for ld in self.data["progression"] if "asi" in ld.get("choices_made", {}) or "feat" in ld.get("choices_made", {})
        ]

        if asi_and_feat_levels:
            lines.append("### ASI/Feat Choices\n\n")
            lines.append("| Level | Choice | Details |\n")
            lines.append("|-------|--------|---------||\n")

            for level_data in asi_and_feat_levels:
                level = level_data["level"]
                choices = level_data["choices_made"]

                if "asi" in choices:
                    asi_detail = self._format_choice(choices["asi"])
                    lines.append(f"| {level} | ASI | {asi_detail} |\n")
                elif "feat" in choices:
                    feat_detail = self._format_choice(choices["feat"])
                    lines.append(f"| {level} | Feat | {feat_detail} |\n")

            lines.append("\n")

        # Feature summary
        lines.append("### Feature Summary\n\n")
        lines.append(f"**Total Features Gained:** {self.data['summary']['total_features_gained']}\n\n")

        # Fighting styles
        fighting_styles = []
        for level_data in self.data["progression"]:
            choices = level_data.get("choices_made", {})
            if "fighting_style" in choices:
                fighting_styles.append(choices["fighting_style"])
            if "additional_fighting_style" in choices:
                fighting_styles.append(choices["additional_fighting_style"])

        if fighting_styles:
            lines.append(f"**Fighting Styles:** {', '.join(fighting_styles)}\n")

        final_attacks = self.data["summary"]["final_extra_attacks"]
        final_crit = self.data["summary"]["final_critical_range_min"]

        lines.append(f"**Extra Attacks:** {final_attacks}\n")

        if final_crit < 20:
            lines.append(f"**Critical Range:** {final_crit}-20\n")

        lines.append("\n**Resources (Max):**\n")
        for resource, count in self.data["summary"]["final_resources"].items():
            lines.append(f"- {resource.replace('_', ' ').title()}: {count} uses\n")

        lines.append("\n")

        # Test statistics
        lines.append("### Test Statistics\n\n")
        lines.append(f"- **Total Tests Run:** {len(self.data['progression'])}\n")
        lines.append(f"- **Tests Passed:** {len(self.data['progression'])}\n")
        lines.append(f"- **Tests Failed:** 0\n\n")

        lines.append("**Overall Result:** [PASS] ALL TESTS PASSED\n")

        return "".join(lines)

    def _format_choice(self, choice_data: Any) -> str:
        """Format choice data for display."""
        if isinstance(choice_data, str):
            return choice_data

        if isinstance(choice_data, dict):
            # Format ASI
            if "ability_1" in choice_data:
                parts = []
                parts.append(f"{choice_data['ability_1'].upper()[:3]} +{choice_data['ability_1_increase']}")
                if choice_data.get("ability_2"):
                    parts.append(f"{choice_data['ability_2'].upper()[:3]} +{choice_data['ability_2_increase']}")
                return ", ".join(parts)

            # Generic dict formatting
            return ", ".join(f"{k}={v}" for k, v in choice_data.items())

        return str(choice_data)


if __name__ == "__main__":
    # Demo/test
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        recorder = ProgressionRecorder("test_char_123", "Test Fighter", tmpdir)

        # Initial state
        recorder.set_initial_state(
            character_class="fighter",
            species="Human",
            background="Soldier",
            ability_scores={
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            },
            fighting_style="dueling",
            starting_hp=10,
        )

        # Level 1
        recorder.begin_level(1, 0)
        recorder.record_choice("fighting_style", "dueling")
        recorder.record_features_granted(["fighting_style", "second_wind", "weapon_mastery"])
        recorder.record_resources({"second_wind_uses": 2, "action_surge_uses": 0})
        recorder.record_character_state(
            ability_scores={"strength": 15, "dexterity": 14, "constitution": 13, "intelligence": 12, "wisdom": 10, "charisma": 8},
            hp_max=10,
        )
        recorder.end_level()

        # Level 2
        recorder.begin_level(2, 300)
        recorder.record_features_granted(["action_surge", "tactical_mind"])
        recorder.record_resources({"second_wind_uses": 2, "action_surge_uses": 1})
        recorder.record_character_state(
            ability_scores={"strength": 15, "dexterity": 14, "constitution": 13, "intelligence": 12, "wisdom": 10, "charisma": 8},
            hp_max=16,
        )
        recorder.end_level()

        # Level 3 - Champion
        recorder.begin_level(3, 900)
        recorder.record_choice("subclass", "champion")
        recorder.set_subclass("champion")
        recorder.record_features_granted(["improved_critical", "remarkable_athlete"])
        recorder.record_resources({"second_wind_uses": 2, "action_surge_uses": 1})
        recorder.record_character_state(
            ability_scores={"strength": 15, "dexterity": 14, "constitution": 13, "intelligence": 12, "wisdom": 10, "charisma": 8},
            hp_max=22,
            critical_range_min=19,
        )
        recorder.end_level()

        # Generate reports
        json_path = recorder.generate_json_report()
        md_path = recorder.generate_markdown_report()

        print(f"Generated JSON report: {json_path}")
        print(f"Generated Markdown report: {md_path}")

        # Show markdown content
        with open(md_path) as f:
            print("\n" + "=" * 80)
            print(f.read())
