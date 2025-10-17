"""
Template Validator for TaleKeeper Character Templates

Validates JSON/YAML templates against D&D 2024 SRD rules and database constraints.
"""

import sqlite3
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path


class TemplateValidator:
    """
    Validates character templates against D&D 2024 rules.

    Based on SRD 5.2.1 Character Creation steps:
    1. Choose a Class
    2. Determine Origin (Background + Species)
    3. Determine Ability Scores
    4. Choose Alignment (not implemented - flavor only)
    5. Fill in Details (equipment, skills, etc.)
    """

    def __init__(self, db_path='talekeeper.db'):
        self.db_path = db_path
        self.errors = []
        self.warnings = []

    def validate(self, template: dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a template dictionary.

        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        self._validate_required_fields(template)
        self._validate_class(template)
        self._validate_species(template)
        self._validate_background(template)
        self._validate_ability_scores(template)
        self._validate_skills(template)
        self._validate_feats(template)
        self._validate_class_specific_features(template)
        self._validate_equipment(template)

        return (len(self.errors) == 0, self.errors, self.warnings)

    def _validate_required_fields(self, template: dict):
        """Validate required template fields."""
        required = ['class', 'species', 'background']

        for field in required:
            if field not in template:
                self.errors.append(f"Missing required field: '{field}'")

        if 'ability_scores' in template:
            required_abilities = ['strength', 'dexterity', 'constitution',
                                   'intelligence', 'wisdom', 'charisma']
            for ability in required_abilities:
                if ability not in template['ability_scores']:
                    self.errors.append(f"Missing ability score: '{ability}'")

    def _validate_class(self, template: dict):
        """Validate class exists in database."""
        if 'class' not in template:
            return

        class_name = template['class']

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM classes WHERE name = ?", (class_name,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            self.errors.append(f"Invalid class: '{class_name}' not found in database")
            return

        valid_classes = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter',
                         'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer',
                         'Warlock', 'Wizard']

        if class_name not in valid_classes:
            self.warnings.append(f"Class '{class_name}' may not be fully supported")

    def _validate_species(self, template: dict):
        """Validate species exists in database."""
        if 'species' not in template:
            return

        species_name = template['species']

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM races WHERE name = ?", (species_name,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            self.errors.append(f"Invalid species: '{species_name}' not found in database")

    def _validate_background(self, template: dict):
        """Validate background exists in database."""
        if 'background' not in template:
            return

        background_name = template['background']

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM backgrounds WHERE name = ?", (background_name,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            self.errors.append(f"Invalid background: '{background_name}' not found in database")

    def _validate_ability_scores(self, template: dict):
        """
        Validate ability scores.

        D&D 2024 rules:
        - Point buy: 27 points, scores 8-15 before racial bonuses
        - Standard array: 15, 14, 13, 12, 10, 8
        - Rolling: 4d6 drop lowest (unpredictable)
        """
        if 'ability_scores' not in template:
            self.warnings.append("No ability scores specified, will use defaults")
            return

        scores = template['ability_scores']

        for ability, score in scores.items():
            if score < 3 or score > 20:
                self.errors.append(f"Ability score '{ability}' out of range (3-20): {score}")

            if score < 8 or score > 18:
                self.warnings.append(f"Ability score '{ability}' unusual for level 1: {score}")

        score_total = sum(scores.values())
        if score_total < 50 or score_total > 90:
            self.warnings.append(f"Total ability scores unusual: {score_total} (expected ~72)")

    def _validate_skills(self, template: dict):
        """Validate skill selections."""
        valid_skills = [
            'Acrobatics', 'Animal Handling', 'Arcana', 'Athletics',
            'Deception', 'History', 'Insight', 'Intimidation',
            'Investigation', 'Medicine', 'Nature', 'Perception',
            'Performance', 'Persuasion', 'Religion', 'Sleight of Hand',
            'Stealth', 'Survival'
        ]

        if 'class_skills' in template:
            for skill in template['class_skills']:
                if skill not in valid_skills:
                    self.errors.append(f"Invalid skill: '{skill}'")

        if 'species_skills' in template:
            for skill in template['species_skills']:
                if skill not in valid_skills:
                    self.errors.append(f"Invalid species skill: '{skill}'")

    def _validate_feats(self, template: dict):
        """Validate feat selections."""
        if 'feats' not in template:
            return

        feats = template['feats']

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for feat_name in feats:
            cursor.execute("SELECT id, name, category FROM feats WHERE name = ?", (feat_name,))
            row = cursor.fetchone()

            if not row:
                self.errors.append(f"Invalid feat: '{feat_name}' not found in database")

        conn.close()

    def _validate_class_specific_features(self, template: dict):
        """Validate class-specific features."""
        if 'class' not in template:
            return

        class_name = template['class']

        if class_name in ['Fighter', 'Paladin', 'Ranger']:
            self._validate_fighting_style(template)
            self._validate_weapon_masteries(template)

        elif class_name == 'Barbarian':
            self._validate_weapon_masteries(template)

        elif class_name == 'Warlock':
            self._validate_warlock_features(template)

        elif class_name in ['Cleric', 'Wizard', 'Druid', 'Sorcerer', 'Bard']:
            self._validate_spellcaster_features(template)

        elif class_name == 'Rogue':
            self._validate_rogue_features(template)

    def _validate_fighting_style(self, template: dict):
        """Validate fighting style selection."""
        if 'fighting_style' not in template:
            self.warnings.append("No fighting style specified, will use default")
            return

        fighting_style = template['fighting_style']
        valid_styles = ['Archery', 'Defense', 'Dueling', 'Great Weapon Fighting',
                        'Protection', 'Two-Weapon Fighting']

        if fighting_style not in valid_styles:
            self.errors.append(f"Invalid fighting style: '{fighting_style}'")

    def _validate_weapon_masteries(self, template: dict):
        """Validate weapon mastery selections."""
        if 'weapon_masteries' not in template:
            self.warnings.append("No weapon masteries specified, will use defaults")
            return

        masteries = template['weapon_masteries']

        if not isinstance(masteries, list):
            self.errors.append("weapon_masteries must be a list")
            return

        class_name = template.get('class', '')

        if class_name == 'Fighter' and len(masteries) != 3:
            self.warnings.append(f"Fighter gets 3 weapon masteries at level 1, got {len(masteries)}")

    def _validate_warlock_features(self, template: dict):
        """Validate warlock-specific features."""
        if 'patron' not in template:
            self.warnings.append("No patron specified, will use 'fiend'")

        if 'pact_boon' not in template:
            self.warnings.append("No pact boon specified (gets at level 3)")

        if 'invocations' not in template:
            self.warnings.append("No invocations specified, will use defaults")

        if 'cantrips' not in template:
            self.warnings.append("No cantrips specified, will use defaults")

        if 'spells_known' not in template:
            self.warnings.append("No spells specified, will use defaults")

    def _validate_spellcaster_features(self, template: dict):
        """Validate spellcaster features."""
        if 'cantrips' not in template:
            self.warnings.append("No cantrips specified for spellcaster")

        if 'spells_prepared' not in template:
            self.warnings.append("No prepared spells specified for spellcaster")

    def _validate_rogue_features(self, template: dict):
        """Validate rogue-specific features."""
        if 'expertise_skills' not in template:
            self.warnings.append("No expertise skills specified, will use defaults")

    def _validate_equipment(self, template: dict):
        """Validate equipment selections."""
        if 'equipment_choices' not in template:
            self.warnings.append("No equipment choices specified")
            return

        equipment = template['equipment_choices']

        if not isinstance(equipment, dict):
            self.errors.append("equipment_choices must be a dictionary")


def validate_template_file(template_path: str, db_path='talekeeper.db') -> bool:
    """
    Validate a template file and print results.

    Returns:
        True if valid, False otherwise
    """
    import json
    import yaml

    path = Path(template_path)

    if not path.exists():
        print(f"Error: Template not found: {template_path}")
        return False

    with open(path, 'r') as f:
        if path.suffix == '.json':
            template = json.load(f)
        elif path.suffix in ['.yaml', '.yml']:
            template = yaml.safe_load(f)
        else:
            print(f"Error: Unsupported format: {path.suffix}")
            return False

    validator = TemplateValidator(db_path)
    is_valid, errors, warnings = validator.validate(template)

    print(f"\n=== Validating {path.name} ===")

    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for error in errors:
            print(f"    - {error}")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"    - {warning}")

    if is_valid:
        print(f"\n  [OK] Template is valid!")
    else:
        print(f"\n  [ERROR] Template has errors")

    return is_valid


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python template_validator.py <template_file>")
        sys.exit(1)

    template_path = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else 'talekeeper.db'

    is_valid = validate_template_file(template_path, db_path)
    sys.exit(0 if is_valid else 1)
