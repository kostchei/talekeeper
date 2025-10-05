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

from services.paladin_abilities import PaladinAbilitiesService
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


def _init_paladin_schema(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE characters (
            id TEXT PRIMARY KEY,
            class_id TEXT,
            subclass_id TEXT,
            level INTEGER,
            charisma INTEGER DEFAULT 10,
            wisdom INTEGER DEFAULT 10,
            intelligence INTEGER DEFAULT 10,
            proficiency_bonus INTEGER DEFAULT 2,
            hit_points_current INTEGER,
            hit_points_max INTEGER
        );

        CREATE TABLE paladin_features (
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

            sacred_oath TEXT,
            lay_on_hands_pool_current INTEGER DEFAULT 0,
            lay_on_hands_pool_max INTEGER DEFAULT 0,
            channel_divinity_uses_current INTEGER DEFAULT 0,
            channel_divinity_uses_max INTEGER DEFAULT 1,
            channel_divinity_last_reset TEXT,
            divine_smite_uses_today INTEGER DEFAULT 0,
            oath_spells_known TEXT,
            spells_prepared INTEGER DEFAULT 0,
            max_spells_prepared INTEGER DEFAULT 0,

            PRIMARY KEY (character_id)
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
        ('protection_from_evil_and_good', 'Protection from Evil and Good', 1, 'abjuration', '1 action', 'Touch', 'V, S, M', '10 minutes', 'Protect a creature from aberrations, celestials, elementals, fey, fiends, and undead.'),
        ('sanctuary', 'Sanctuary', 1, 'abjuration', '1 bonus action', '30 feet', 'V, S, M', '1 minute', 'You ward a creature against attack.'),
        ('lesser_restoration', 'Lesser Restoration', 2, 'abjuration', '1 action', 'Touch', 'V, S', 'Instantaneous', 'You touch a creature and can end one disease or condition.'),
        ('zone_of_truth', 'Zone of Truth', 2, 'enchantment', '1 action', '60 feet', 'V, S', '10 minutes', 'You create a magical zone that guards against deception.'),
        ('cure_wounds', 'Cure Wounds', 1, 'evocation', '1 action', 'Touch', 'V, S', 'Instantaneous', 'A creature you touch regains hit points.'),
        ('bless', 'Bless', 1, 'enchantment', '1 action', '30 feet', 'V, S, M', '1 minute', 'You bless up to three creatures.');
        """
    )
    conn.commit()


def test_paladin_initialization():
    """Test basic paladin character initialization."""
    with temp_db_path("paladin_init") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_paladin_schema(conn)

            # Create test character (level 3 to get oath features)
            conn.execute("""
                INSERT INTO characters (id, class_id, level, charisma, wisdom, intelligence, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-3", "paladin", 3, 16, 10, 10, 2))
            conn.commit()

            service = PaladinAbilitiesService(str(db_path))
            result = service.initialize_paladin_character("paladin-3", "devotion")

            assert result["success"] is True
            assert result["oath"] == "devotion"
            assert result["max_prepared_spells"] == 4  # 1 + 3 (Cha modifier)
            assert result["lay_on_hands_pool"] == 15  # 5 x level
            assert result["channel_divinity_uses"] == 1

            # Verify paladin features were created
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM paladin_features WHERE character_id = ?", ("paladin-3",))
            paladin_row = cursor.fetchone()
            assert paladin_row is not None

            # Verify oath spells were added
            cursor.execute("SELECT COUNT(*) FROM character_spells WHERE character_id = ? AND source = 'oath'", ("paladin-3",))
            oath_spell_count = cursor.fetchone()[0]
            assert oath_spell_count == 2  # protection_from_evil_and_good, sanctuary


def test_lay_on_hands():
    """Test Lay on Hands healing feature."""
    with temp_db_path("lay_on_hands") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_paladin_schema(conn)

            # Create level 5 paladin
            conn.execute("""
                INSERT INTO characters (id, class_id, level, charisma, wisdom, intelligence, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-5", "paladin", 5, 16, 10, 10, 3))
            conn.commit()

            # Initialize with full Lay on Hands pool
            conn.execute("""
                INSERT INTO paladin_features
                (character_id, level, sacred_oath, lay_on_hands_pool_current, lay_on_hands_pool_max)
                VALUES (?, ?, ?, ?, ?)
            """, ("paladin-5", 5, "devotion", 25, 25))
            conn.commit()

            service = PaladinAbilitiesService(str(db_path))

            # Test healing 5 points
            result = service.use_lay_on_hands("paladin-5", 5)
            assert result["success"] is True
            assert result["healing_done"] == 5
            assert result["pool_remaining"] == 20

            # Test healing more than maximum (should cap at 5)
            result = service.use_lay_on_hands("paladin-5", 10)
            assert result["success"] is True
            assert result["healing_done"] == 5
            assert result["pool_remaining"] == 15


def test_lay_on_hands_empty_pool():
    """Test Lay on Hands when pool is empty."""
    with temp_db_path("lay_on_hands_empty") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_paladin_schema(conn)

            conn.execute("""
                INSERT INTO characters (id, class_id, level, charisma, wisdom, intelligence, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-5", "paladin", 5, 16, 10, 10, 3))
            conn.commit()

            # Initialize with empty pool
            conn.execute("""
                INSERT INTO paladin_features
                (character_id, level, sacred_oath, lay_on_hands_pool_current, lay_on_hands_pool_max)
                VALUES (?, ?, ?, ?, ?)
            """, ("paladin-5", 5, "devotion", 0, 25))
            conn.commit()

            service = PaladinAbilitiesService(str(db_path))
            result = service.use_lay_on_hands("paladin-5", 5)

            assert result["success"] is False
            assert "No healing points available" in result["reason"]


def test_divine_smite_calculation():
    """Test Divine Smite damage calculation."""
    with temp_db_path("divine_smite") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_paladin_schema(conn)

            service = PaladinAbilitiesService(str(db_path))

            # Test 1st level slot vs normal enemy
            result = service.divine_smite("paladin-1", 1, False)
            assert result["success"] is True
            assert result["damage_dice"] == 2  # 2d8 base
            assert result["spell_slot_consumed"] == 1

            # Test 3rd level slot vs normal enemy
            result = service.divine_smite("paladin-1", 3, False)
            assert result["success"] is True
            assert result["damage_dice"] == 4  # 2d8 + 2d8 for higher levels

            # Test 1st level slot vs undead/fiend
            result = service.divine_smite("paladin-1", 1, True)
            assert result["success"] is True
            assert result["damage_dice"] == 3  # 2d8 + 1d8 vs undead/fiend
            assert result["extra_vs_undead_fiend"] is True

            # Test maximum damage (should cap at 5d8)
            result = service.divine_smite("paladin-1", 5, True)
            assert result["success"] is True
            assert result["damage_dice"] == 5  # Capped at 5d8


def test_channel_divinity():
    """Test Channel Divinity usage."""
    with temp_db_path("channel_divinity") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_paladin_schema(conn)

            conn.execute("""
                INSERT INTO characters (id, class_id, level, charisma, wisdom, intelligence, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-3", "paladin", 3, 16, 10, 10, 2))
            conn.commit()

            # Initialize with 1 Channel Divinity use
            conn.execute("""
                INSERT INTO paladin_features
                (character_id, level, sacred_oath, channel_divinity_uses_current, channel_divinity_uses_max)
                VALUES (?, ?, ?, ?, ?)
            """, ("paladin-3", 3, "devotion", 0, 1))
            conn.commit()

            service = PaladinAbilitiesService(str(db_path))

            # Test using Channel Divinity
            result = service.use_channel_divinity("paladin-3", "Sacred Weapon")
            assert result["success"] is True
            assert result["ability_used"] == "Sacred Weapon"
            assert result["uses_remaining"] == 0

            # Test using when no uses left
            result = service.use_channel_divinity("paladin-3", "Turn the Unholy")
            assert result["success"] is False
            assert "No Channel Divinity uses remaining" in result["reason"]


def test_long_rest_recovery():
    """Test long rest recovery for paladins."""
    with temp_db_path("long_rest") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_paladin_schema(conn)

            conn.execute("""
                INSERT INTO characters (id, class_id, level, charisma, wisdom, intelligence, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-5", "paladin", 5, 16, 10, 10, 3))
            conn.commit()

            # Initialize with depleted resources
            conn.execute("""
                INSERT INTO paladin_features
                (character_id, level, sacred_oath, lay_on_hands_pool_current, lay_on_hands_pool_max,
                 channel_divinity_uses_current, channel_divinity_uses_max)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-5", 5, "devotion", 5, 25, 1, 1))
            conn.commit()

            service = PaladinAbilitiesService(str(db_path))
            result = service.long_rest_recovery("paladin-5")

            assert result["success"] is True
            assert result["lay_on_hands_reset"] is True
            assert result["channel_divinity_reset"] is True

            # Verify resources were reset
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lay_on_hands_pool_current, channel_divinity_uses_current
                FROM paladin_features WHERE character_id = ?
            """, ("paladin-5",))
            row = cursor.fetchone()
            assert row[0] == 25  # Lay on Hands pool restored
            assert row[1] == 0   # Channel Divinity uses reset


def test_get_paladin_info():
    """Test retrieving comprehensive paladin information."""
    with temp_db_path("paladin_info") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_paladin_schema(conn)

            # Create paladin with features
            conn.execute("""
                INSERT INTO characters (id, class_id, level, charisma, wisdom, intelligence, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-3", "paladin", 3, 16, 10, 10, 2))
            conn.commit()

            conn.execute("""
                INSERT INTO paladin_features
                (character_id, level, sacred_oath, lay_on_hands_pool_current, lay_on_hands_pool_max)
                VALUES (?, ?, ?, ?, ?)
            """, ("paladin-3", 3, "devotion", 15, 15))
            conn.commit()

            # Add oath spells
            conn.execute("""
                INSERT INTO character_spells
                (character_id, spell_id, spell_level, is_prepared, source, source_level, always_prepared)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-3", "protection_from_evil_and_good", 1, 1, "oath", 3, 1))

            conn.execute("""
                INSERT INTO character_spells
                (character_id, spell_id, spell_level, is_prepared, source, source_level, always_prepared)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-3", "sanctuary", 1, 1, "oath", 3, 1))

            service = PaladinAbilitiesService(str(db_path))
            info = service.get_paladin_info("paladin-3")

            assert "paladin_features" in info
            assert "prepared_spells" in info
            assert "oath_spells" in info

            assert info["paladin_features"]["sacred_oath"] == "devotion"
            assert len(info["oath_spells"]) == 2
            assert len(info["prepared_spells"]) == 2  # All prepared spells including oath


def test_devotion_oath_features():
    """Test that Oath of Devotion features are properly applied."""
    with temp_db_path("devotion") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_paladin_schema(conn)

            # Create level 3 paladin (gets oath features)
            conn.execute("""
                INSERT INTO characters (id, class_id, level, charisma, wisdom, intelligence, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-3", "paladin", 3, 16, 10, 10, 2))
            conn.commit()

            service = PaladinAbilitiesService(str(db_path))
            result = service.initialize_paladin_character("paladin-3", "devotion")

            assert result["success"] is True
            assert "Sacred Weapon" in result["features_added"]
            assert "Turn the Unholy" in result["features_added"]

            # Verify features were added to database
            cursor = conn.cursor()
            cursor.execute("""
                SELECT feature_id FROM character_features
                WHERE character_id = ? AND source = 'oath_devotion'
            """, ("paladin-3",))
            features = [row[0] for row in cursor.fetchall()]
            assert "sacred_weapon" in features
            assert "turn_the_unholy" in features


def test_half_caster_spell_progression():
    """Test that paladins get appropriate spell slots as half-casters."""
    with temp_db_path("half_caster") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_paladin_schema(conn)

            # Level 1 paladin (no spells yet)
            conn.execute("""
                INSERT INTO characters (id, class_id, level, charisma, wisdom, intelligence, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-1", "paladin", 1, 16, 10, 10, 2))
            conn.commit()

            service = PaladinAbilitiesService(str(db_path))
            result = service.initialize_paladin_character("paladin-1", "devotion")

            assert result["success"] is True
            assert result["max_prepared_spells"] == 0  # No spellcasting at level 1

            # Level 2 paladin (gets spellcasting)
            conn.execute("""
                INSERT INTO characters (id, class_id, level, charisma, wisdom, intelligence, proficiency_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("paladin-2", "paladin", 2, 16, 10, 10, 2))
            conn.commit()

            result = service.initialize_paladin_character("paladin-2", "devotion")
            assert result["success"] is True
            assert result["max_prepared_spells"] == 4  # 1 + 3 (Cha modifier)

            # Verify spell slots for level 2 half-caster (2 1st-level slots)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT spell_level, max_slots FROM character_spell_slots
                WHERE character_id = ? ORDER BY spell_level
            """, ("paladin-2",))
            slots = cursor.fetchall()
            assert len(slots) == 1  # Only 1st level
            assert slots[0] == (1, 2)  # 2 first-level slots


if __name__ == "__main__":
    pytest.main([__file__, "-v"])