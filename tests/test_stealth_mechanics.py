"""
Test suite for stealth mechanics in TaleKeeper.

Tests the following scenarios:
1. Character with stealth proficiency attempting to hide
2. Character without stealth proficiency (should fail)
3. Stealth with advantage (elven cloak)
4. Stealth with disadvantage (heavy armor)
5. Monster perception checks against stealth DC
6. Hidden attack bonuses (advantage, sneak attack)
7. Assassin features (auto-crit, death strike)
8. Fleeing while hidden
"""

import sys
import os
import pytest
import sqlite3
import json
from typing import Dict, Any
from uuid import uuid4

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.stealth_mechanics import StealthMechanicsService
from services.proficiency_system import ProficiencySystem
from services.weapon_attack_service import WeaponAttackService


class TestStealthMechanics:
    """Test suite for stealth mechanics."""

    @pytest.fixture
    def setup_database(self, tmp_path):
        """Create a test database with necessary schema."""
        db_path = tmp_path / "test_stealth.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create necessary tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id TEXT PRIMARY KEY,
                name TEXT,
                level INTEGER,
                class_id TEXT,
                subclass_id TEXT,
                strength INTEGER,
                dexterity INTEGER,
                constitution INTEGER,
                intelligence INTEGER,
                wisdom INTEGER,
                charisma INTEGER,
                hp INTEGER,
                max_hp INTEGER,
                ac INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_proficiencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT,
                proficiency_type TEXT,
                proficiency_name TEXT,
                source TEXT,
                FOREIGN KEY (character_id) REFERENCES characters(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT,
                item_id TEXT,
                is_equipped INTEGER,
                FOREIGN KEY (character_id) REFERENCES characters(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id TEXT PRIMARY KEY,
                name TEXT,
                equipment_type TEXT,
                armor_type TEXT,
                description TEXT
            )
        """)

        conn.commit()
        conn.close()
        return str(db_path)

    def create_test_character(self, db_path: str, character_data: Dict[str, Any]) -> str:
        """Create a test character in the database."""
        char_id = str(uuid4())
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (id, name, level, class_id, subclass_id,
                                   strength, dexterity, constitution,
                                   intelligence, wisdom, charisma, hp, max_hp, ac)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            char_id,
            character_data.get('name', 'Test Character'),
            character_data.get('level', 1),
            character_data.get('class_id', 'rogue'),
            character_data.get('subclass_id', ''),
            character_data.get('strength', 10),
            character_data.get('dexterity', 16),
            character_data.get('constitution', 12),
            character_data.get('intelligence', 14),
            character_data.get('wisdom', 12),
            character_data.get('charisma', 10),
            character_data.get('hp', 10),
            character_data.get('max_hp', 10),
            character_data.get('ac', 14)
        ))

        # Add proficiencies
        for prof in character_data.get('proficiencies', []):
            cursor.execute("""
                INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
                VALUES (?, ?, ?, ?)
            """, (char_id, prof['type'], prof['name'], prof.get('source', 'class')))

        conn.commit()
        conn.close()
        return char_id

    def add_equipment(self, db_path: str, character_id: str, item_data: Dict[str, Any]):
        """Add equipment to a character."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        item_id = str(uuid4())

        # Add item to equipment table
        cursor.execute("""
            INSERT INTO equipment (id, name, equipment_type, armor_type, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            item_id,
            item_data.get('name'),
            item_data.get('equipment_type', 'armor'),
            item_data.get('armor_type'),
            item_data.get('description', '')
        ))

        # Equip to character
        cursor.execute("""
            INSERT INTO character_equipment (character_id, item_id, is_equipped)
            VALUES (?, ?, ?)
        """, (character_id, item_id, 1))

        conn.commit()
        conn.close()

    def test_stealth_with_proficiency(self, setup_database):
        """Test that character with stealth proficiency can attempt to hide."""
        db_path = setup_database
        stealth_service = StealthMechanicsService(db_path)

        # Create a rogue with stealth proficiency
        char_id = self.create_test_character(db_path, {
            'name': 'Sneaky Rogue',
            'level': 5,
            'class_id': 'rogue',
            'dexterity': 16,
            'proficiencies': [
                {'type': 'skill', 'name': 'Stealth'}
            ]
        })

        # Check proficiency
        assert stealth_service.check_stealth_proficiency(char_id) is True

        # Perform stealth check
        result = stealth_service.perform_stealth_check(char_id, 5)

        # Should have attempted the check
        assert 'success' in result
        assert 'total' in result
        assert 'breakdown' in result

    def test_stealth_without_proficiency(self, setup_database):
        """Test that character without stealth proficiency cannot hide."""
        db_path = setup_database
        stealth_service = StealthMechanicsService(db_path)

        # Create a fighter without stealth proficiency
        char_id = self.create_test_character(db_path, {
            'name': 'Loud Fighter',
            'level': 5,
            'class_id': 'fighter',
            'dexterity': 12,
            'proficiencies': [
                {'type': 'skill', 'name': 'Athletics'}
            ]
        })

        # Check proficiency
        assert stealth_service.check_stealth_proficiency(char_id) is False

        # Perform stealth check
        result = stealth_service.perform_stealth_check(char_id, 5)

        # Should fail due to no proficiency
        assert result['success'] is False
        assert result.get('reason') == 'no_proficiency'

    def test_stealth_with_elven_cloak(self, setup_database):
        """Test stealth with advantage from Elven Cloak."""
        db_path = setup_database
        stealth_service = StealthMechanicsService(db_path)

        # Create a rogue with stealth proficiency
        char_id = self.create_test_character(db_path, {
            'name': 'Elven Rogue',
            'level': 5,
            'class_id': 'rogue',
            'dexterity': 16,
            'proficiencies': [
                {'type': 'skill', 'name': 'Stealth'}
            ]
        })

        # Add Elven Cloak
        self.add_equipment(db_path, char_id, {
            'name': 'Cloak of Elvenkind',
            'equipment_type': 'wondrous',
            'description': 'Grants advantage on Stealth checks'
        })

        # Get modifiers
        modifiers = stealth_service.get_stealth_modifiers(char_id)

        # Should have advantage
        assert modifiers['advantage'] is True
        assert any('Cloak' in s for s in modifiers['sources'])

    def test_stealth_with_heavy_armor(self, setup_database):
        """Test stealth with disadvantage from heavy armor."""
        db_path = setup_database
        stealth_service = StealthMechanicsService(db_path)

        # Create a character with stealth proficiency but wearing heavy armor
        char_id = self.create_test_character(db_path, {
            'name': 'Armored Rogue',
            'level': 5,
            'class_id': 'rogue',
            'dexterity': 16,
            'proficiencies': [
                {'type': 'skill', 'name': 'Stealth'}
            ]
        })

        # Add plate armor
        self.add_equipment(db_path, char_id, {
            'name': 'Plate Armor',
            'equipment_type': 'armor',
            'armor_type': 'heavy'
        })

        # Get modifiers
        modifiers = stealth_service.get_stealth_modifiers(char_id)

        # Should have disadvantage
        assert modifiers['disadvantage'] is True
        assert any('Plate Armor' in s for s in modifiers['sources'])

    def test_monster_perception_check(self, setup_database):
        """Test monster perception checks against stealth DC."""
        db_path = setup_database
        stealth_service = StealthMechanicsService(db_path)

        # Test monster with good perception
        monster = {
            'name': 'Alert Guard',
            'wisdom': 14,
            'skills': {'Perception': 5}
        }

        # Check against DC 15
        result = stealth_service.check_monster_perception(monster, 15)

        assert 'spotted' in result
        assert 'roll' in result
        assert 'total' in result
        assert result['perception_bonus'] == 5

    def test_encounter_stealth_check(self, setup_database):
        """Test full encounter stealth check with multiple monsters."""
        db_path = setup_database
        stealth_service = StealthMechanicsService(db_path)

        # Create a sneaky rogue
        char_id = self.create_test_character(db_path, {
            'name': 'Shadow',
            'level': 5,
            'class_id': 'rogue',
            'dexterity': 18,
            'proficiencies': [
                {'type': 'skill', 'name': 'Stealth'}
            ]
        })

        character_data = {
            'id': char_id,
            'level': 5
        }

        # Create monsters with varying perception
        monsters = [
            {'name': 'Goblin', 'wisdom': 8, 'skills': {}},
            {'name': 'Hobgoblin', 'wisdom': 10, 'skills': {'Perception': 2}},
            {'name': 'Bugbear', 'wisdom': 11, 'skills': {'Perception': 4}}
        ]

        # Check encounter stealth
        result = stealth_service.check_encounter_stealth(char_id, character_data, monsters)

        assert 'hidden' in result
        assert 'stealth_result' in result
        assert 'monster_results' in result
        assert len(result['monster_results']) == 3

    def test_hidden_attack_bonuses(self, setup_database):
        """Test attack bonuses when attacking from hidden."""
        db_path = setup_database
        stealth_service = StealthMechanicsService(db_path)
        weapon_service = WeaponAttackService(db_path)

        # Create attack context
        attack_context = {
            'is_hidden': True,
            'has_advantage': False,
            'sneak_attack_eligible': False,
            'subclass': 'thief',
            'level': 5
        }

        # Apply hidden bonuses
        modified_context = stealth_service.apply_hidden_attack_bonuses(attack_context)

        # Should have advantage and sneak attack
        assert modified_context['has_advantage'] is True
        assert modified_context['sneak_attack_eligible'] is True
        assert modified_context.get('advantage_source') == 'attacking_from_hidden'
        assert modified_context.get('sneak_attack_source') == 'hidden'

    def test_assassin_features(self, setup_database):
        """Test Assassin subclass features when attacking from hidden."""
        db_path = setup_database
        stealth_service = StealthMechanicsService(db_path)

        # Create attack context for level 3 assassin
        attack_context = {
            'is_hidden': True,
            'subclass': 'assassin',
            'level': 3,
            'target_surprised': True
        }

        # Apply hidden bonuses
        modified_context = stealth_service.apply_hidden_attack_bonuses(attack_context)

        # Should have assassinate
        assert modified_context.get('assassinate') is True
        assert modified_context.get('auto_critical') is True
        assert modified_context.get('critical_source') == 'assassinate'

        # Test level 17 Death Strike
        attack_context['level'] = 17
        modified_context = stealth_service.apply_hidden_attack_bonuses(attack_context)

        assert modified_context.get('death_strike') is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])