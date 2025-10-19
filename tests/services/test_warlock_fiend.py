#test
import pytest
import sqlite3
import json
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.warlock_service import (
    WarlockService, PactMagicService, ElditchInvocationService, FiendPatronService
)
from core.game_engine_sqlite import GameEngineSQLite
from database.database_init import DatabaseInitializer


class TestWarlockImplementation:
    @classmethod
    def setup_class(cls):
        """Set up test database once for all tests."""
        cls.db_path = 'test_warlock.db'

        # Remove existing test database
        if Path(cls.db_path).exists():
            Path(cls.db_path).unlink()

        cls.db_init = DatabaseInitializer(cls.db_path)
        cls.db_init.initialize(force=True)

        # Apply warlock migration manually
        with sqlite3.connect(cls.db_path) as conn:
            migration_path = Path(__file__).parent.parent.parent / 'database' / 'migrations' / '015_warlock_class_simple.sql'
            if migration_path.exists():
                with open(migration_path, 'r') as f:
                    migration_sql = f.read()
                    conn.executescript(migration_sql)
                    conn.commit()
            else:
                print(f"Migration not found at {migration_path}")

        cls.engine = GameEngineSQLite(cls.db_path)
        cls.warlock_service = WarlockService(cls.db_path)
        cls.pact_service = PactMagicService(cls.db_path)
        cls.invocation_service = ElditchInvocationService(cls.db_path)
        cls.fiend_service = FiendPatronService(cls.db_path)

    @classmethod
    def teardown_class(cls):
        """Clean up test database."""
        try:
            if Path(cls.db_path).exists():
                import time
                time.sleep(0.1)  # Give time for connections to close
                Path(cls.db_path).unlink()
        except:
            pass  # Ignore cleanup errors

    def setup_method(self):
        """Clear character data before each test."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM characters")
            cursor.execute("DELETE FROM warlock_features")
            cursor.execute("DELETE FROM warlock_invocations")
            cursor.execute("DELETE FROM character_spellcasting")
            conn.commit()

    def create_test_warlock(self, level=1, patron='Fiend'):
        """Helper to create a test warlock character."""
        character_data = {
            'name': 'Test Warlock',
            'race_id': 'human',
            'class_id': 'warlock',
            'subclass': patron,
            'level': level,
            'strength': 10,
            'dexterity': 14,
            'constitution': 12,
            'intelligence': 12,
            'wisdom': 13,
            'charisma': 16,
            'hit_points_current': 8 + ((level - 1) * 5),
            'hit_points_max': 8 + ((level - 1) * 5),
            'ac': 12,
            'background_id': 'sage',
            'save_slot': 1
        }

        # Create character in database
        result = self.engine.create_new_character_sync(character_data, 1)
        return result['id'] if result else None

    def test_warlock_initialization(self):
        """Test basic Warlock initialization."""
        char_id = self.create_test_warlock(level=1)

        features = self.warlock_service.get_warlock_features(char_id)

        assert features['patron'] == 'Fiend'
        assert features['pact_slots'] == 1
        assert features['pact_slot_level'] == 1
        assert features['pact_boon'] is None  # Not chosen until level 3
        assert features['invocations'] == []

    def test_pact_magic_slots(self):
        """Test pact magic slot progression."""
        test_levels = [
            (1, 1, 1),   # Level 1: 1 slot, level 1
            (2, 2, 1),   # Level 2: 2 slots, level 1
            (3, 2, 2),   # Level 3: 2 slots, level 2
            (5, 2, 3),   # Level 5: 2 slots, level 3
            (7, 2, 4),   # Level 7: 2 slots, level 4
            (9, 2, 5),   # Level 9: 2 slots, level 5
            (11, 3, 5),  # Level 11: 3 slots, level 5
            (17, 4, 5),  # Level 17: 4 slots, level 5
            (20, 4, 5),  # Level 20: 4 slots, level 5
        ]

        for level, expected_slots, expected_level in test_levels:
            char_id = self.create_test_warlock(level=level)
            slots, slot_level = self.pact_service.get_pact_slots(char_id)
            assert slots == expected_slots, f"Level {level}: Expected {expected_slots} slots, got {slots}"
            assert slot_level == expected_level, f"Level {level}: Expected slot level {expected_level}, got {slot_level}"

    def test_pact_slot_usage_and_recovery(self):
        """Test using and recovering pact slots."""
        char_id = self.create_test_warlock(level=3)

        # Start with 2 slots
        slots, _ = self.pact_service.get_pact_slots(char_id)
        assert slots == 2

        # Use a slot
        success = self.pact_service.use_pact_slot(char_id)
        assert success
        slots, _ = self.pact_service.get_pact_slots(char_id)
        assert slots == 1

        # Use another slot
        success = self.pact_service.use_pact_slot(char_id)
        assert success
        slots, _ = self.pact_service.get_pact_slots(char_id)
        assert slots == 0

        # Can't use when empty
        success = self.pact_service.use_pact_slot(char_id)
        assert not success

        # Short rest recovery
        recovered = self.pact_service.short_rest_recovery(char_id)
        assert recovered == 2
        slots, _ = self.pact_service.get_pact_slots(char_id)
        assert slots == 2

    def test_pact_boon_selection(self):
        """Test selecting pact boons at level 3."""
        char_id = self.create_test_warlock(level=3)

        # Test Pact of the Blade
        success = self.warlock_service.select_pact_boon(char_id, 'blade')
        assert success
        features = self.warlock_service.get_warlock_features(char_id)
        assert features['pact_boon'] == 'blade'

        # Check that pact weapon feature was added
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM character_features
                WHERE character_id = ? AND feature_id = 'pact_weapon'
            """, (char_id,))
            assert cursor.fetchone() is not None

    def test_eldritch_invocations(self):
        """Test learning and applying eldritch invocations."""
        char_id = self.create_test_warlock(level=2)

        # Add eldritch blast cantrip first (required for Agonizing Blast)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_spellcasting
                SET known_spells = ?
                WHERE character_id = ? AND spellcasting_class = 'warlock'
            """, (json.dumps({'0': ['eldritch_blast']}), char_id))
            conn.commit()

        # Get available invocations
        available = self.invocation_service.get_available_invocations(char_id)
        assert len(available) > 0

        # Learn Agonizing Blast
        success = self.invocation_service.learn_invocation(char_id, 'agonizing_blast')
        assert success

        # Check it was learned
        invocations = self.invocation_service.get_character_invocations(char_id)
        assert any(inv['id'] == 'agonizing_blast' for inv in invocations)

        # Learn Armor of Shadows
        success = self.invocation_service.learn_invocation(char_id, 'armor_of_shadows')
        assert success

    def test_invocation_prerequisites(self):
        """Test that invocations with prerequisites are properly filtered."""
        # Level 5 character with Pact of the Blade
        char_id = self.create_test_warlock(level=5)
        self.warlock_service.select_pact_boon(char_id, 'blade')

        available = self.invocation_service.get_available_invocations(char_id)

        # Thirsting Blade requires level 5 and Pact of the Blade - should be available
        thirsting_blade_available = any(inv['id'] == 'thirsting_blade' for inv in available)
        assert thirsting_blade_available

        # Lifedrinker requires level 12 - should NOT be available
        lifedrinker_available = any(inv['id'] == 'lifedrinker' for inv in available)
        assert not lifedrinker_available

        # Book of Ancient Secrets requires Pact of the Tome - should NOT be available
        book_available = any(inv['id'] == 'book_of_ancient_secrets' for inv in available)
        assert not book_available

    def test_fiend_patron_features(self):
        """Test Fiend patron specific features."""
        char_id = self.create_test_warlock(level=1, patron='Fiend')

        # Check Dark One's Blessing
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM character_features
                WHERE character_id = ? AND feature_id = 'dark_ones_blessing'
            """, (char_id,))
            assert cursor.fetchone() is not None

        # Test Dark One's Blessing temp HP grant
        temp_hp = self.fiend_service.dark_ones_blessing(char_id, 1.0)
        assert temp_hp == 4  # Level 1 + 3 Cha modifier

    def test_fiend_level_progression(self):
        """Test Fiend patron features at different levels."""
        test_levels = [
            (1, ['dark_ones_blessing']),
            (6, ['dark_ones_blessing', 'dark_ones_own_luck']),
            (10, ['dark_ones_blessing', 'dark_ones_own_luck', 'fiendish_resilience']),
            (14, ['dark_ones_blessing', 'dark_ones_own_luck', 'fiendish_resilience', 'hurl_through_hell'])
        ]

        for level, expected_features in test_levels:
            char_id = self.create_test_warlock(level=level, patron='Fiend')

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for feature in expected_features:
                    cursor.execute("""
                        SELECT * FROM character_features
                        WHERE character_id = ? AND feature_id = ?
                    """, (char_id, feature))
                    assert cursor.fetchone() is not None, f"Missing {feature} at level {level}"

    def test_dark_ones_own_luck(self):
        """Test Dark One's Own Luck usage."""
        char_id = self.create_test_warlock(level=6, patron='Fiend')

        # First use should succeed
        success = self.fiend_service.dark_ones_own_luck(char_id, 'ability_check')
        assert success

        # Second use should fail (once per rest)
        success = self.fiend_service.dark_ones_own_luck(char_id, 'ability_check')
        assert not success

    def test_fiendish_resilience(self):
        """Test Fiendish Resilience damage type selection."""
        char_id = self.create_test_warlock(level=10, patron='Fiend')

        # Select fire resistance
        success = self.fiend_service.fiendish_resilience(char_id, 'fire')
        assert success

        # Invalid damage type
        success = self.fiend_service.fiendish_resilience(char_id, 'force')
        assert not success

    def test_hurl_through_hell(self):
        """Test Hurl Through Hell ability."""
        char_id = self.create_test_warlock(level=14, patron='Fiend')

        # First use should succeed
        result = self.fiend_service.hurl_through_hell(char_id, 'target_123')
        assert result['success']
        assert result['damage'] == 60  # 10d10 average
        assert result['damage_type'] == 'psychic'

        # Second use should fail (once per long rest)
        result = self.fiend_service.hurl_through_hell(char_id, 'target_456')
        assert not result['success']

    def test_mystic_arcanum(self):
        """Test Mystic Arcanum feature at high levels."""
        test_levels = [
            (11, ['mystic_arcanum_6']),
            (13, ['mystic_arcanum_6', 'mystic_arcanum_7']),
            (15, ['mystic_arcanum_6', 'mystic_arcanum_7', 'mystic_arcanum_8']),
            (17, ['mystic_arcanum_6', 'mystic_arcanum_7', 'mystic_arcanum_8', 'mystic_arcanum_9'])
        ]

        for level, expected_arcanums in test_levels:
            char_id = self.create_test_warlock(level=level)
            self.warlock_service.level_up_warlock(char_id, level)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for arcanum in expected_arcanums:
                    cursor.execute("""
                        SELECT * FROM character_features
                        WHERE character_id = ? AND feature_id = ?
                    """, (char_id, arcanum))
                    assert cursor.fetchone() is not None, f"Missing {arcanum} at level {level}"

    def test_eldritch_master(self):
        """Test Eldritch Master feature at level 20."""
        char_id = self.create_test_warlock(level=20)
        self.warlock_service.level_up_warlock(char_id, 20)

        # Use all pact slots
        for _ in range(4):
            self.pact_service.use_pact_slot(char_id)

        slots, _ = self.pact_service.get_pact_slots(char_id)
        assert slots == 0

        # Use Eldritch Master
        success = self.pact_service.eldritch_master_recovery(char_id)
        assert success

        slots, _ = self.pact_service.get_pact_slots(char_id)
        assert slots == 4

    def test_spell_casting_integration(self):
        """Test that Warlock integrates with spellcasting system."""
        char_id = self.create_test_warlock(level=5)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT spellcasting_ability, cantrips_known, spell_save_dc, spell_attack_bonus
                FROM character_spellcasting
                WHERE character_id = ? AND spellcasting_class = 'warlock'
            """, (char_id,))

            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'Charisma'
            assert result[1] == 3  # Level 5 has 3 cantrips
            assert result[2] == 13  # 8 + 2 (prof) + 3 (Cha mod)
            assert result[3] == 5   # 2 (prof) + 3 (Cha mod)

    def test_can_cast_spell_with_pact_slot(self):
        """Test checking if spell can be cast with pact slot."""
        char_id = self.create_test_warlock(level=5)  # Has level 3 pact slots

        # Can cast level 1-3 spells
        assert self.pact_service.can_cast_spell_with_pact_slot(char_id, 1)
        assert self.pact_service.can_cast_spell_with_pact_slot(char_id, 2)
        assert self.pact_service.can_cast_spell_with_pact_slot(char_id, 3)

        # Cannot cast level 4+ spells yet
        assert not self.pact_service.can_cast_spell_with_pact_slot(char_id, 4)
        assert not self.pact_service.can_cast_spell_with_pact_slot(char_id, 5)

        # Use all slots
        self.pact_service.use_pact_slot(char_id)
        self.pact_service.use_pact_slot(char_id)

        # Now can't cast any spell
        assert not self.pact_service.can_cast_spell_with_pact_slot(char_id, 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])