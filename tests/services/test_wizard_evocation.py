#test
import sqlite3
import tempfile
from pathlib import Path
import sys
import gc
import uuid
import shutil
from contextlib import contextmanager

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.wizard_abilities import WizardAbilitiesService
from services.spellcasting_service import get_spellcasting_service
from services.spell_registry import spell_registry


@contextmanager
def temp_db_path(prefix: str):
    base = Path(tempfile.gettempdir()) / f"tk_{prefix}_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=False)
    db_path = base / f"{prefix}.db"
    try:
        yield db_path
    finally:
        try:
            db_path.unlink()
        except FileNotFoundError:
            pass
        except PermissionError:
            pass
        shutil.rmtree(base, ignore_errors=True)


def _init_wizard_schema(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE characters (
            id TEXT PRIMARY KEY,
            class_id TEXT,
            subclass_id TEXT,
            level INTEGER,
            intelligence INTEGER DEFAULT 10,
            wisdom INTEGER DEFAULT 10,
            charisma INTEGER DEFAULT 10,
            proficiency_bonus INTEGER DEFAULT 2,
            hit_points_current INTEGER,
            hit_points_max INTEGER
        );

        CREATE TABLE wizard_features (
            character_id TEXT NOT NULL,
            level INTEGER NOT NULL,

            spell_slots_1_current INTEGER DEFAULT 0,
            spell_slots_1_max INTEGER DEFAULT 0,
            spell_slots_2_current INTEGER DEFAULT 0,
            spell_slots_2_max INTEGER DEFAULT 0,
            spell_slots_3_current INTEGER DEFAULT 0,
            spell_slots_3_max INTEGER DEFAULT 0,
            spell_slots_4_current INTEGER DEFAULT 0,
            spell_slots_4_max INTEGER DEFAULT 0,
            spell_slots_5_current INTEGER DEFAULT 0,
            spell_slots_5_max INTEGER DEFAULT 0,
            spell_slots_6_current INTEGER DEFAULT 0,
            spell_slots_6_max INTEGER DEFAULT 0,
            spell_slots_7_current INTEGER DEFAULT 0,
            spell_slots_7_max INTEGER DEFAULT 0,
            spell_slots_8_current INTEGER DEFAULT 0,
            spell_slots_8_max INTEGER DEFAULT 0,
            spell_slots_9_current INTEGER DEFAULT 0,
            spell_slots_9_max INTEGER DEFAULT 0,

            arcane_tradition TEXT,
            arcane_recovery_used BOOLEAN DEFAULT FALSE,
            arcane_recovery_last_reset TEXT,
            spells_prepared INTEGER DEFAULT 0,
            max_spells_prepared INTEGER DEFAULT 0,

            PRIMARY KEY (character_id)
        );

        CREATE TABLE wizard_spellbook (
            character_id TEXT NOT NULL,
            spell_id TEXT NOT NULL,
            spell_level INTEGER NOT NULL,
            learned_at_level INTEGER NOT NULL,
            source TEXT DEFAULT 'level_up',
            cost_paid INTEGER DEFAULT 0,
            time_spent INTEGER DEFAULT 0,
            notes TEXT,

            PRIMARY KEY (character_id, spell_id)
        );

        CREATE TABLE character_spells (
            character_id TEXT NOT NULL,
            spell_id TEXT NOT NULL,
            spell_level INTEGER NOT NULL,
            is_prepared BOOLEAN DEFAULT TRUE,
            source TEXT NOT NULL,
            source_level INTEGER,
            always_prepared BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (character_id, spell_id)
        );

        CREATE TABLE character_features (
            character_id TEXT NOT NULL,
            feature_id TEXT NOT NULL,
            source TEXT NOT NULL,
            source_level INTEGER,
            uses_current INTEGER DEFAULT 0,
            uses_max INTEGER DEFAULT 0,
            PRIMARY KEY (character_id, feature_id)
        );

        CREATE TABLE character_spell_slots (
            character_id TEXT NOT NULL,
            spell_level INTEGER NOT NULL,
            max_slots INTEGER DEFAULT 0,
            used_slots INTEGER DEFAULT 0,
            slot_type TEXT DEFAULT 'standard',
            PRIMARY KEY (character_id, spell_level, slot_type)
        );

        CREATE TABLE character_spellcasting (
            character_id TEXT PRIMARY KEY,
            spellcasting_ability TEXT NOT NULL,
            spell_attack_bonus INTEGER DEFAULT 0,
            spell_save_dc INTEGER DEFAULT 8,
            ritual_casting BOOLEAN DEFAULT FALSE,
            spellcasting_focus TEXT,
            spells_known INTEGER DEFAULT 0,
            spells_prepared INTEGER DEFAULT 0
        );

        CREATE TABLE character_concentration (
            character_id TEXT PRIMARY KEY,
            spell_id TEXT,
            spell_level INTEGER,
            duration_remaining INTEGER,
            save_dc INTEGER DEFAULT 10
        );

        CREATE TABLE spells (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            level INTEGER NOT NULL,
            school TEXT NOT NULL,
            casting_time TEXT NOT NULL,
            range_value TEXT NOT NULL,
            components TEXT NOT NULL,
            duration TEXT NOT NULL,
            concentration BOOLEAN DEFAULT FALSE,
            ritual BOOLEAN DEFAULT FALSE,
            description TEXT NOT NULL,
            higher_levels TEXT,
            source TEXT DEFAULT 'PHB'
        );

        -- Insert test spells
        INSERT INTO spells (id, name, level, school, casting_time, range_value, components, duration, description) VALUES
        ('magic_missile', 'Magic Missile', 1, 'evocation', '1 action', '120 feet', 'V, S', 'Instantaneous', 'Three glowing darts of magical force strike their target.'),
        ('shield', 'Shield', 1, 'abjuration', '1 reaction', 'Self', 'V, S', '1 round', 'An invisible barrier of magical force appears.'),
        ('mage_armor', 'Mage Armor', 1, 'abjuration', '1 action', 'Touch', 'V, S, M', '8 hours', 'Touch a willing creature to surround it with protective magical force.'),
        ('detect_magic', 'Detect Magic', 1, 'divination', '1 action', 'Self', 'V, S', '10 minutes', 'Sense the presence of magic within 30 feet.'),
        ('comprehend_languages', 'Comprehend Languages', 1, 'divination', '1 action', 'Self', 'V, S, M', '1 hour', 'Understand any spoken language you hear.'),
        ('burning_hands', 'Burning Hands', 1, 'evocation', '1 action', 'Self (15-foot cone)', 'V, S', 'Instantaneous', 'A thin sheet of flames shoots forth from your outstretched fingertips.'),
        ('fireball', 'Fireball', 3, 'evocation', '1 action', '150 feet', 'V, S, M', 'Instantaneous', 'A bright flash and a rolling boom of thunder.'),
        ('lightning_bolt', 'Lightning Bolt', 3, 'evocation', '1 action', 'Self (100-foot line)', 'V, S, M', 'Instantaneous', 'A stroke of lightning forming a line.');
        """
    )
    conn.commit()


def test_wizard_initialization():
    """Test basic wizard character initialization."""
    with temp_db_path("wizard_init") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_wizard_schema(conn)

            # Create test character
            conn.execute("""
                INSERT INTO characters (id, class_id, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-1", "wizard", 1, 16, 10, 10, 2))
            conn.commit()

            service = WizardAbilitiesService(str(db_path))
            result = service.initialize_wizard_character("wizard-1", "evocation")

            assert result["success"] is True
            assert result["tradition"] == "evocation"
            assert result["max_prepared_spells"] == 4  # 1 + 3 (Int modifier)
            assert len(result["spells_added"]) == 6  # Starting spells

            # Verify wizard features were created
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM wizard_features WHERE character_id = ?", ("wizard-1",))
            wizard_row = cursor.fetchone()
            assert wizard_row is not None

            # Verify spellbook entries
            cursor.execute("SELECT COUNT(*) FROM wizard_spellbook WHERE character_id = ?", ("wizard-1",))
            spellbook_count = cursor.fetchone()[0]
            assert spellbook_count == 6


def test_arcane_recovery_basic():
    """Test basic Arcane Recovery functionality."""
    with temp_db_path("arcane_recovery") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_wizard_schema(conn)

            # Create level 3 wizard with some used spell slots
            conn.execute("""
                INSERT INTO characters (id, class_id, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-3", "wizard", 3, 16, 10, 10, 2))
            conn.commit()

            conn.execute("""
                INSERT INTO wizard_features
                (character_id, level, arcane_tradition, arcane_recovery_used,
                 spell_slots_1_current, spell_slots_1_max,
                 spell_slots_2_current, spell_slots_2_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-3", 3, "evocation", False, 2, 4, 0, 2))
            conn.commit()

            service = WizardAbilitiesService(str(db_path))
            result = service.use_arcane_recovery("wizard-3")

            if not result["success"]:
                print(f"Arcane Recovery failed: {result.get('reason', 'Unknown error')}")
            assert result["success"] is True
            assert result["recovery_limit"] == 2  # (3 + 1) // 2

            # Should recover 2 1st-level slots (2 slot levels)
            assert 1 in result["slots_recovered"]
            assert result["slots_recovered"][1] == 2


def test_arcane_recovery_already_used():
    """Test Arcane Recovery when already used."""
    with temp_db_path("arcane_recovery_used") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_wizard_schema(conn)

            conn.execute("""
                INSERT INTO characters (id, class_id, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-3", "wizard", 3, 16, 10, 10, 2))
            conn.commit()

            conn.execute("""
                INSERT INTO wizard_features
                (character_id, level, arcane_tradition, arcane_recovery_used)
                VALUES (?, ?, ?, ?)
            """, ("wizard-3", 3, "evocation", True))
            conn.commit()

            service = WizardAbilitiesService(str(db_path))
            result = service.use_arcane_recovery("wizard-3")

            assert result["success"] is False
            assert "already used" in result["reason"]


def test_arcane_recovery_higher_level():
    """Test Arcane Recovery at higher levels with mixed slot usage."""
    with temp_db_path("arcane_recovery_high") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_wizard_schema(conn)

            # Level 9 wizard (recovery limit = 5)
            conn.execute("""
                INSERT INTO characters (id, class_id, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-9", "wizard", 9, 18, 10, 10, 4))
            conn.commit()

            # All spell slots used
            conn.execute("""
                INSERT INTO wizard_features
                (character_id, level, arcane_tradition, arcane_recovery_used,
                 spell_slots_1_current, spell_slots_1_max,
                 spell_slots_2_current, spell_slots_2_max,
                 spell_slots_3_current, spell_slots_3_max,
                 spell_slots_4_current, spell_slots_4_max,
                 spell_slots_5_current, spell_slots_5_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-9", 9, "evocation", False, 0, 4, 0, 3, 0, 3, 0, 3, 0, 1))
            conn.commit()

            service = WizardAbilitiesService(str(db_path))
            result = service.use_arcane_recovery("wizard-9")

            assert result["success"] is True
            assert result["recovery_limit"] == 5

            # With 5 recovery points, should prioritize lower-level slots
            # Could recover: 5 1st-level, or 2 2nd-level + 1 1st-level, or 1 3rd-level + 2 1st-level, etc.
            total_recovery = sum(level * count for level, count in result["slots_recovered"].items())
            assert total_recovery <= 5


def test_add_spell_to_spellbook():
    """Test adding spells to wizard spellbook."""
    with temp_db_path("spellbook") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_wizard_schema(conn)

            conn.execute("""
                INSERT INTO characters (id, class_id, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-1", "wizard", 1, 16, 10, 10, 2))
            conn.commit()

            service = WizardAbilitiesService(str(db_path))

            # Test adding a spell
            result = service.add_spell_to_spellbook("wizard-1", "fireball", "level_up")
            if not result["success"]:
                print(f"Add spell failed: {result.get('reason', 'Unknown error')}")
            assert result["success"] is True
            assert result["spell_name"] == "Fireball"
            assert result["spell_level"] == 3

            # Verify it's in the spellbook
            cursor = conn.cursor()
            cursor.execute("""
                SELECT spell_id, source FROM wizard_spellbook
                WHERE character_id = ? AND spell_id = ?
            """, ("wizard-1", "fireball"))
            row = cursor.fetchone()
            assert row is not None
            assert row[0] == "fireball"
            assert row[1] == "level_up"


def test_long_rest_recovery():
    """Test long rest recovery for wizards."""
    with temp_db_path("long_rest") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_wizard_schema(conn)

            conn.execute("""
                INSERT INTO characters (id, class_id, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-5", "wizard", 5, 16, 10, 10, 3))
            conn.commit()

            conn.execute("""
                INSERT INTO wizard_features
                (character_id, level, arcane_tradition, arcane_recovery_used)
                VALUES (?, ?, ?, ?)
            """, ("wizard-5", 5, "evocation", True))
            conn.commit()

            service = WizardAbilitiesService(str(db_path))
            result = service.long_rest_recovery("wizard-5")

            assert result["success"] is True
            assert result["arcane_recovery_reset"] is True

            # Verify Arcane Recovery was reset
            cursor = conn.cursor()
            cursor.execute("""
                SELECT arcane_recovery_used FROM wizard_features
                WHERE character_id = ?
            """, ("wizard-5",))
            row = cursor.fetchone()
            assert row[0] == 0  # Should be reset to False


def test_get_wizard_info():
    """Test retrieving comprehensive wizard information."""
    with temp_db_path("wizard_info") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_wizard_schema(conn)

            # Create wizard with spells in spellbook
            conn.execute("""
                INSERT INTO characters (id, class_id, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-1", "wizard", 1, 16, 10, 10, 2))
            conn.commit()

            conn.execute("""
                INSERT INTO wizard_features
                (character_id, level, arcane_tradition, max_spells_prepared)
                VALUES (?, ?, ?, ?)
            """, ("wizard-1", 1, "evocation", 4))
            conn.commit()

            # Add spells to spellbook
            conn.execute("""
                INSERT INTO wizard_spellbook
                (character_id, spell_id, spell_level, learned_at_level, source)
                VALUES (?, ?, ?, ?, ?)
            """, ("wizard-1", "magic_missile", 1, 1, "starting"))

            conn.execute("""
                INSERT INTO wizard_spellbook
                (character_id, spell_id, spell_level, learned_at_level, source)
                VALUES (?, ?, ?, ?, ?)
            """, ("wizard-1", "shield", 1, 1, "starting"))

            # Add prepared spells
            conn.execute("""
                INSERT INTO character_spells
                (character_id, spell_id, spell_level, is_prepared, source, source_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("wizard-1", "magic_missile", 1, 1, "wizard_spellbook", 1))

            service = WizardAbilitiesService(str(db_path))
            info = service.get_wizard_info("wizard-1")

            assert "wizard_features" in info
            assert "spellbook" in info
            assert "prepared_spells" in info

            assert info["wizard_features"]["arcane_tradition"] == "evocation"
            assert len(info["spellbook"]) == 2
            assert len(info["prepared_spells"]) == 1


def test_evocation_subclass_features():
    """Test that Evocation school features are properly applied."""
    with temp_db_path("evocation") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_wizard_schema(conn)

            # Create level 2 wizard (gets Sculpt Spells)
            conn.execute("""
                INSERT INTO characters (id, class_id, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-2", "wizard", 2, 16, 10, 10, 2))
            conn.commit()

            service = WizardAbilitiesService(str(db_path))
            result = service.initialize_wizard_character("wizard-2", "evocation")

            assert result["success"] is True
            assert "Sculpt Spells" in result["features_added"]

            # Verify feature was added to database
            cursor = conn.cursor()
            cursor.execute("""
                SELECT feature_id FROM character_features
                WHERE character_id = ? AND feature_id = 'sculpt_spells'
            """, ("wizard-2",))
            row = cursor.fetchone()
            assert row is not None


def test_wizard_spell_preparation_limit():
    """Test that wizard spell preparation respects Intelligence modifier + level."""
    with temp_db_path("preparation") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_wizard_schema(conn)

            # Level 5 wizard with 18 Intelligence (modifier +4)
            conn.execute("""
                INSERT INTO characters (id, class_id, level, intelligence, wisdom, charisma, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("wizard-5", "wizard", 5, 18, 10, 10, 3))
            conn.commit()

            service = WizardAbilitiesService(str(db_path))
            result = service.initialize_wizard_character("wizard-5", "evocation")

            assert result["success"] is True
            # Level 5 + Int modifier 4 = 9 prepared spells max
            assert result["max_prepared_spells"] == 9

            # Verify in database
            cursor = conn.cursor()
            cursor.execute("""
                SELECT max_spells_prepared FROM wizard_features
                WHERE character_id = ?
            """, ("wizard-5",))
            row = cursor.fetchone()
            assert row[0] == 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])