#test
"""
Tests for Tactical Master (Fighter Level 9 Feature)

Tactical Master allows Fighter to replace weapon's mastery property
with Push, Sap, or Slow on a per-attack basis.
"""

import sqlite3
import pytest
from services.weapon_attack_service import WeaponAttackService


class TestTacticalMaster:
    """Test Tactical Master feature"""

    @pytest.fixture
    def db_path(self, tmp_path):
        """Create test database"""
        db = tmp_path / "test_tactical.db"
        conn = sqlite3.connect(str(db))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                name TEXT,
                class_id TEXT,
                level INTEGER,
                strength INTEGER DEFAULT 16,
                dexterity INTEGER DEFAULT 14,
                weapon_mastery_count INTEGER DEFAULT -1
            )
        """)

        conn.commit()
        conn.close()
        return str(db)

    def create_fighter(self, db_path: str, level: int) -> str:
        """Create test fighter"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        char_id = f"fighter_l{level}"
        cursor.execute("""
            INSERT INTO characters (id, name, class_id, level)
            VALUES (?, ?, 'fighter', ?)
        """, (char_id, f"Fighter {level}", level))

        conn.commit()
        conn.close()
        return char_id

    def test_level_8_no_tactical_master(self, db_path):
        """Level 8 Fighter cannot use Tactical Master"""
        char_id = self.create_fighter(db_path, 8)
        service = WeaponAttackService(db_path)

        assert not service.can_use_tactical_master(char_id)

    def test_level_9_has_tactical_master(self, db_path):
        """Level 9 Fighter can use Tactical Master"""
        char_id = self.create_fighter(db_path, 9)
        service = WeaponAttackService(db_path)

        assert service.can_use_tactical_master(char_id)

    def test_level_20_has_tactical_master(self, db_path):
        """Level 20 Fighter can use Tactical Master"""
        char_id = self.create_fighter(db_path, 20)
        service = WeaponAttackService(db_path)

        assert service.can_use_tactical_master(char_id)

    def test_mastery_override_push(self, db_path):
        """Can override mastery with Push"""
        char_id = self.create_fighter(db_path, 9)
        service = WeaponAttackService(db_path)

        weapon = {
            'name': 'Greatsword',
            'mastery_property': 'Graze'
        }

        character = {
            'id': char_id,
            'class_id': 'fighter',
            'level': 9,
            'strength': 16,
            'dexterity': 14
        }

        effects = service.apply_weapon_mastery_effects(
            weapon=weapon,
            character=character,
            target=None,
            hit=True,
            chosen_mastery='push'
        )

        assert 'tactical_master_used' in effects
        assert effects['tactical_master_used']['original'] == 'Graze'
        assert effects['tactical_master_used']['chosen'] == 'Push'
        assert 'push' in effects

    def test_mastery_override_sap(self, db_path):
        """Can override mastery with Sap"""
        char_id = self.create_fighter(db_path, 10)
        service = WeaponAttackService(db_path)

        weapon = {
            'name': 'Greataxe',
            'mastery_property': 'Cleave'
        }

        character = {
            'id': char_id,
            'class_id': 'fighter',
            'level': 10,
            'strength': 18,
            'dexterity': 12
        }

        effects = service.apply_weapon_mastery_effects(
            weapon=weapon,
            character=character,
            target=None,
            hit=True,
            chosen_mastery='sap'
        )

        assert 'tactical_master_used' in effects
        assert effects['tactical_master_used']['original'] == 'Cleave'
        assert effects['tactical_master_used']['chosen'] == 'Sap'
        assert 'sap' in effects

    def test_mastery_override_slow(self, db_path):
        """Can override mastery with Slow"""
        char_id = self.create_fighter(db_path, 15)
        service = WeaponAttackService(db_path)

        weapon = {
            'name': 'Longsword',
            'mastery_property': 'Sap'
        }

        character = {
            'id': char_id,
            'class_id': 'fighter',
            'level': 15,
            'strength': 20,
            'dexterity': 14
        }

        effects = service.apply_weapon_mastery_effects(
            weapon=weapon,
            character=character,
            target=None,
            hit=True,
            chosen_mastery='slow'
        )

        assert 'tactical_master_used' in effects
        assert effects['tactical_master_used']['original'] == 'Sap'
        assert effects['tactical_master_used']['chosen'] == 'Slow'
        assert 'slow' in effects

    def test_mastery_original_choice(self, db_path):
        """Can choose to use original mastery"""
        char_id = self.create_fighter(db_path, 12)
        service = WeaponAttackService(db_path)

        weapon = {
            'name': 'Greatsword',
            'mastery_property': 'Graze'
        }

        character = {
            'id': char_id,
            'class_id': 'fighter',
            'level': 12,
            'strength': 18,
            'dexterity': 14
        }

        effects = service.apply_weapon_mastery_effects(
            weapon=weapon,
            character=character,
            target=None,
            hit=False,
            chosen_mastery='original'
        )

        assert 'tactical_master_used' not in effects
        assert 'graze' in effects

    def test_non_fighter_cannot_use_tactical_master(self, db_path):
        """Non-Fighter cannot use Tactical Master"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO characters (id, name, class_id, level)
            VALUES ('barb1', 'Barbarian', 'barbarian', 12)
        """)
        conn.commit()
        conn.close()

        service = WeaponAttackService(db_path)
        assert not service.can_use_tactical_master('barb1')

    def test_tactical_master_with_already_push_mastery(self, db_path):
        """Can swap even if weapon already has Push"""
        char_id = self.create_fighter(db_path, 9)
        service = WeaponAttackService(db_path)

        weapon = {
            'name': 'Pike',
            'mastery_property': 'Push'
        }

        character = {
            'id': char_id,
            'class_id': 'fighter',
            'level': 9,
            'strength': 16,
            'dexterity': 14
        }

        effects_sap = service.apply_weapon_mastery_effects(
            weapon=weapon,
            character=character,
            target=None,
            hit=True,
            chosen_mastery='sap'
        )

        assert 'tactical_master_used' in effects_sap
        assert effects_sap['tactical_master_used']['original'] == 'Push'
        assert effects_sap['tactical_master_used']['chosen'] == 'Sap'
        assert 'sap' in effects_sap

    def test_tactical_master_per_attack_flexibility(self, db_path):
        """Tactical Master can be different on each attack"""
        char_id = self.create_fighter(db_path, 11)
        service = WeaponAttackService(db_path)

        weapon = {
            'name': 'Greatsword',
            'mastery_property': 'Graze'
        }

        character = {
            'id': char_id,
            'class_id': 'fighter',
            'level': 11,
            'strength': 18,
            'dexterity': 14
        }

        attack1 = service.apply_weapon_mastery_effects(
            weapon=weapon,
            character=character,
            target=None,
            hit=True,
            chosen_mastery='push'
        )

        attack2 = service.apply_weapon_mastery_effects(
            weapon=weapon,
            character=character,
            target=None,
            hit=True,
            chosen_mastery='sap'
        )

        attack3 = service.apply_weapon_mastery_effects(
            weapon=weapon,
            character=character,
            target=None,
            hit=False,
            chosen_mastery='original'
        )

        assert attack1['tactical_master_used']['chosen'] == 'Push'
        assert attack2['tactical_master_used']['chosen'] == 'Sap'
        assert 'tactical_master_used' not in attack3
        assert 'graze' in attack3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])