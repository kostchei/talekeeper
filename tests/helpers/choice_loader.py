"""
Choice Loader for Character Progression Testing

Loads and validates character progression choices from YAML or JSON files.
Choices define all decisions made during character leveling (ASI, feats,
subclass, fighting styles, etc.).
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List


class ChoiceValidationError(Exception):
    """Raised when choice configuration fails validation."""

    pass


class ChoiceLoader:
    """Loads and validates character progression choices from configuration files."""

    # Valid choice types for different decisions
    # Note: These are lowercase for validation, but actual database names are capitalized
    VALID_FIGHTING_STYLES = [
        "archery",
        "defense",
        "dueling",
        "great_weapon_fighting",
        "protection",
        "two_weapon_fighting",
    ]

    VALID_ABILITY_SCORES = [
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma",
    ]

    VALID_CHOICE_TYPES = ["asi", "feat"]

    # Fighter ASI levels (2024 SRD)
    FIGHTER_ASI_LEVELS = [4, 6, 8, 12, 14, 16, 19]

    @classmethod
    def load_from_yaml(cls, file_path: str) -> Dict[str, Any]:
        """
        Load choices from a YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Dictionary containing choices configuration

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If file is not valid YAML
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Choice file not found: {file_path}")

        with open(path, "r") as f:
            try:
                choices = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Invalid YAML in {file_path}: {e}")

        return choices

    @classmethod
    def load_from_json(cls, file_path: str) -> Dict[str, Any]:
        """
        Load choices from a JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Dictionary containing choices configuration

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Choice file not found: {file_path}")

        with open(path, "r") as f:
            try:
                choices = json.load(f)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(f"Invalid JSON in {file_path}: {e}")

        return choices

    @classmethod
    def validate_choices(cls, choices: Dict[str, Any], character_class: str = "fighter") -> bool:
        """
        Validate choices configuration against schema.

        Args:
            choices: Choices dictionary to validate
            character_class: Character class being validated (default: fighter)

        Returns:
            True if valid

        Raises:
            ChoiceValidationError: If validation fails
        """
        # Validate character_template section
        if "character_template" not in choices:
            raise ChoiceValidationError("Missing 'character_template' section")

        template = choices["character_template"]
        cls._validate_character_template(template, character_class)

        # Validate progression_choices section
        if "progression_choices" not in choices:
            raise ChoiceValidationError("Missing 'progression_choices' section")

        progression = choices["progression_choices"]
        cls._validate_progression_choices(progression, character_class)

        return True

    @classmethod
    def _validate_character_template(cls, template: Dict[str, Any], character_class: str) -> None:
        """Validate the character_template section."""
        # Required fields
        required = ["name", "class", "species", "background", "ability_scores"]
        for field in required:
            if field not in template:
                raise ChoiceValidationError(f"Missing required field in character_template: {field}")

        # Validate class matches
        if template["class"].lower() != character_class.lower():
            raise ChoiceValidationError(
                f"Class mismatch: expected '{character_class}', got '{template['class']}'"
            )

        # Validate species and background
        if template["species"] not in ["random", "Random"]:
            if not isinstance(template["species"], str):
                raise ChoiceValidationError("Species must be a string or 'random'")

        if template["background"] not in ["random", "Random"]:
            if not isinstance(template["background"], str):
                raise ChoiceValidationError("Background must be a string or 'random'")

        # Validate ability scores
        cls._validate_ability_scores(template["ability_scores"])

    @classmethod
    def _validate_ability_scores(cls, ability_scores: Dict[str, Any]) -> None:
        """Validate ability scores configuration."""
        if "method" not in ability_scores:
            raise ChoiceValidationError("Missing 'method' in ability_scores")

        method = ability_scores["method"]
        if method not in ["standard_array", "point_buy", "manual"]:
            raise ChoiceValidationError(
                f"Invalid ability score method: {method}. "
                f"Must be 'standard_array', 'point_buy', or 'manual'"
            )

        if "values" not in ability_scores:
            raise ChoiceValidationError("Missing 'values' in ability_scores")

        values = ability_scores["values"]
        for ability in cls.VALID_ABILITY_SCORES:
            if ability not in values:
                raise ChoiceValidationError(f"Missing ability score: {ability}")

            score = values[ability]
            if not isinstance(score, int):
                raise ChoiceValidationError(f"Ability score '{ability}' must be an integer")

            if score < 3 or score > 20:
                raise ChoiceValidationError(
                    f"Ability score '{ability}' out of range (3-20): {score}"
                )

    @classmethod
    def _validate_progression_choices(
        cls, progression: Dict[str, Any], character_class: str
    ) -> None:
        """Validate the progression_choices section."""
        if character_class.lower() == "fighter":
            cls._validate_fighter_progression(progression)
        else:
            raise ChoiceValidationError(f"Unsupported character class: {character_class}")

    @classmethod
    def _validate_fighter_progression(cls, progression: Dict[str, Any]) -> None:
        """Validate Fighter-specific progression choices."""
        # Level 1: Fighting Style required
        if "level_1" not in progression:
            raise ChoiceValidationError("Missing level_1 choices")

        level_1 = progression["level_1"]
        if "fighting_style" not in level_1:
            raise ChoiceValidationError("Missing fighting_style in level_1")

        if level_1["fighting_style"].lower() not in cls.VALID_FIGHTING_STYLES:
            raise ChoiceValidationError(
                f"Invalid fighting style: {level_1['fighting_style']}. "
                f"Must be one of: {', '.join(cls.VALID_FIGHTING_STYLES)}"
            )

        # Level 3: Subclass required
        if "level_3" not in progression:
            raise ChoiceValidationError("Missing level_3 choices")

        level_3 = progression["level_3"]
        if "subclass" not in level_3:
            raise ChoiceValidationError("Missing subclass in level_3")

        # For now, only Champion is supported in tests
        if level_3["subclass"].lower() != "champion":
            raise ChoiceValidationError(
                f"Unsupported Fighter subclass: {level_3['subclass']}. Currently only 'champion' is supported."
            )

        # Champion Level 7: Additional Fighting Style
        if "champion_level_7" in progression:
            champ_7 = progression["champion_level_7"]
            if "additional_fighting_style" not in champ_7:
                raise ChoiceValidationError("Missing additional_fighting_style in champion_level_7")

            style = champ_7["additional_fighting_style"]
            if style.lower() not in cls.VALID_FIGHTING_STYLES:
                raise ChoiceValidationError(f"Invalid additional fighting style: {style}")

            # Cannot duplicate level 1 fighting style (case-insensitive)
            if style.lower() == level_1["fighting_style"].lower():
                raise ChoiceValidationError(
                    "Additional fighting style at level 7 cannot duplicate level 1 choice"
                )

        # ASI Levels: Validate each
        for level in cls.FIGHTER_ASI_LEVELS:
            level_key = f"level_{level}"
            if level_key in progression:
                cls._validate_asi_or_feat_choice(progression[level_key], level)

    @classmethod
    def _validate_asi_or_feat_choice(cls, choice: Dict[str, Any], level: int) -> None:
        """Validate an ASI or Feat choice."""
        if "choice_type" not in choice:
            raise ChoiceValidationError(f"Missing choice_type at level {level}")

        choice_type = choice["choice_type"]
        if choice_type not in cls.VALID_CHOICE_TYPES:
            raise ChoiceValidationError(
                f"Invalid choice_type at level {level}: {choice_type}. Must be 'asi' or 'feat'"
            )

        if choice_type == "asi":
            cls._validate_asi(choice, level)
        elif choice_type == "feat":
            cls._validate_feat(choice, level)

    @classmethod
    def _validate_asi(cls, choice: Dict[str, Any], level: int) -> None:
        """Validate an ASI (Ability Score Increase) choice."""
        if "asi" not in choice:
            raise ChoiceValidationError(f"Missing 'asi' data at level {level}")

        asi = choice["asi"]

        # Must have ability_1
        if "ability_1" not in asi:
            raise ChoiceValidationError(f"Missing ability_1 in ASI at level {level}")

        if asi["ability_1"] not in cls.VALID_ABILITY_SCORES:
            raise ChoiceValidationError(f"Invalid ability_1 in ASI at level {level}")

        if "ability_1_increase" not in asi:
            raise ChoiceValidationError(f"Missing ability_1_increase in ASI at level {level}")

        increase = asi["ability_1_increase"]
        if not isinstance(increase, int) or increase < 1 or increase > 2:
            raise ChoiceValidationError(
                f"ability_1_increase must be 1 or 2 at level {level}, got {increase}"
            )

        # ability_2 is optional
        if "ability_2" in asi and asi["ability_2"] is not None:
            if asi["ability_2"] not in cls.VALID_ABILITY_SCORES:
                raise ChoiceValidationError(f"Invalid ability_2 in ASI at level {level}")

            if "ability_2_increase" not in asi:
                raise ChoiceValidationError(f"Missing ability_2_increase in ASI at level {level}")

            increase2 = asi["ability_2_increase"]
            if not isinstance(increase2, int) or increase2 < 1 or increase2 > 2:
                raise ChoiceValidationError(
                    f"ability_2_increase must be 1 or 2 at level {level}, got {increase2}"
                )

            # Total increase must be exactly 2
            total = asi["ability_1_increase"] + increase2
            if total != 2:
                raise ChoiceValidationError(
                    f"Total ASI increase must be 2 at level {level}, got {total}"
                )

    @classmethod
    def _validate_feat(cls, choice: Dict[str, Any], level: int) -> None:
        """Validate a Feat choice."""
        if "feat" not in choice:
            raise ChoiceValidationError(f"Missing 'feat' data at level {level}")

        feat = choice["feat"]
        if not isinstance(feat, str) or not feat:
            raise ChoiceValidationError(f"Feat name must be a non-empty string at level {level}")

    @classmethod
    def get_choice_for_level(cls, choices: Dict[str, Any], level: int) -> Optional[Dict[str, Any]]:
        """
        Get choices for a specific level.

        Args:
            choices: Full choices configuration
            level: Character level

        Returns:
            Dictionary of choices for that level, or None if no choices at that level
        """
        progression = choices.get("progression_choices", {})

        # Check standard level key
        level_key = f"level_{level}"
        if level_key in progression:
            return progression[level_key]

        # Check for special keys (e.g., champion_level_7)
        for key in progression.keys():
            if key.endswith(f"_level_{level}"):
                return progression[key]

        return None

    @classmethod
    def get_all_choice_levels(cls, choices: Dict[str, Any]) -> List[int]:
        """
        Get all levels that have choices defined.

        Args:
            choices: Full choices configuration

        Returns:
            Sorted list of levels with choices
        """
        progression = choices.get("progression_choices", {})
        levels = []

        for key in progression.keys():
            # Extract level number from key (e.g., "level_4" -> 4, "champion_level_7" -> 7)
            if "level_" in key:
                level_str = key.split("level_")[-1]
                try:
                    levels.append(int(level_str))
                except ValueError:
                    continue

        return sorted(set(levels))

    @classmethod
    def get_character_template(cls, choices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the character template from choices.

        Args:
            choices: Full choices configuration

        Returns:
            Character template dictionary
        """
        return choices.get("character_template", {})

    @classmethod
    def is_random_selection(cls, value: str) -> bool:
        """Check if a value indicates random selection."""
        return value.lower() == "random"


if __name__ == "__main__":
    # Simple validation test
    import sys

    if len(sys.argv) < 2:
        print("Usage: python choice_loader.py <yaml_or_json_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    path = Path(file_path)

    try:
        # Load based on extension
        if path.suffix in [".yaml", ".yml"]:
            choices = ChoiceLoader.load_from_yaml(file_path)
            print(f"✓ Loaded YAML file: {file_path}")
        elif path.suffix == ".json":
            choices = ChoiceLoader.load_from_json(file_path)
            print(f"✓ Loaded JSON file: {file_path}")
        else:
            print(f"Error: Unsupported file type: {path.suffix}")
            sys.exit(1)

        # Validate
        character_class = choices.get("character_template", {}).get("class", "fighter")
        ChoiceLoader.validate_choices(choices, character_class)
        print(f"✓ Validation passed for {character_class} choices")

        # Show summary
        template = ChoiceLoader.get_character_template(choices)
        print(f"\nCharacter: {template.get('name')}")
        print(f"Class: {template.get('class')}")
        print(f"Subclass: {choices['progression_choices'].get('level_3', {}).get('subclass')}")

        choice_levels = ChoiceLoader.get_all_choice_levels(choices)
        print(f"\nChoices defined for {len(choice_levels)} levels: {choice_levels}")

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
