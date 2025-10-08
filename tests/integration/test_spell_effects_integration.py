"""
Integration tests for spell effects in combat/AC/attack systems.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'src')))

import sqlite3
import tempfile
from talekeeper.services.spell_effects_service import SpellEffectsService
from talekeeper.core.game_engine_sqlite import GameEngineSQLite
from talekeeper.services.weapon_attack_service import WeaponAttackService


def test_shield_of_faith_ac_integration():
    """Test that Shield of Faith bonus appears in AC calculation."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                name TEXT,
                class_id TEXT,
                level INTEGER,
                strength INTEGER,
                dexterity INTEGER,
                constitution INTEGER,
                armor_class INTEGER,
                equipment_armor TEXT,
                equipment_shield TEXT,
                equipment_off_hand TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE active_spell_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                spell_id TEXT NOT NULL,
                spell_name TEXT NOT NULL,
                spell_level_cast INTEGER NOT NULL,
                effect_type TEXT NOT NULL,
                effect_data TEXT,
                duration_type TEXT NOT NULL,
                duration_remaining INTEGER,
                rounds_remaining INTEGER,
                concentration BOOLEAN DEFAULT FALSE,
                caster_id TEXT,
                target_id TEXT,
                applied_at TEXT DEFAULT (datetime('now')),
                expires_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE character_magical_bonuses (
                character_id TEXT PRIMARY KEY,
                ac_bonus INTEGER DEFAULT 0
            )
        """)

        character_id = 'test-char-1'
        cursor.execute("""
            INSERT INTO characters (id, name, class_id, level, strength, dexterity, constitution, armor_class)
            VALUES (?, 'Test Paladin', 'paladin', 2, 16, 12, 14, 13)
        """, (character_id,))
        conn.commit()
        conn.close()

        spell_effects = SpellEffectsService(db_path)
        spell_effects.apply_buff(
            character_id,
            {'type': 'ac_bonus', 'value': 2, 'source': 'shield_of_faith'},
            duration_rounds=100
        )

        engine = GameEngineSQLite(db_path)
        ac = engine._calculate_armor_class(character_id, 16, 12, 14, 'paladin')

        print(f"AC calculation result: {ac}")
        assert ac == 13, f"Expected AC 13 (11 base + 2 Shield of Faith), got {ac}"

        print("[PASS] Shield of Faith AC integration test")

    finally:
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except:
            pass


def test_bless_attack_integration():
    """Test that Bless bonus appears in attack rolls."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE active_spell_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                spell_id TEXT NOT NULL,
                spell_name TEXT NOT NULL,
                spell_level_cast INTEGER NOT NULL,
                effect_type TEXT NOT NULL,
                effect_data TEXT,
                duration_type TEXT NOT NULL,
                duration_remaining INTEGER,
                rounds_remaining INTEGER,
                concentration BOOLEAN DEFAULT FALSE,
                caster_id TEXT,
                target_id TEXT,
                applied_at TEXT DEFAULT (datetime('now')),
                expires_at TEXT
            )
        """)
        conn.commit()
        conn.close()

        character_id = 'test-char-2'

        spell_effects = SpellEffectsService(db_path)
        spell_effects.apply_buff(
            character_id,
            {
                'type': 'attack_and_save_bonus',
                'bonus_dice': '1d4',
                'applies_to': ['attack_rolls', 'saving_throws'],
                'source': 'bless'
            },
            duration_rounds=10
        )

        weapon_service = WeaponAttackService(db_path)
        weapon = {
            'name': 'Longsword',
            'damage_dice': '1d8',
            'weapon_properties': 'versatile'
        }
        character = {
            'id': character_id,
            'level': 2,
            'strength': 16,
            'dexterity': 12
        }

        result = weapon_service.calculate_attack_damage(weapon, character)

        assert any('Bless' in mod for mod in result['modifiers_applied']), \
            f"Expected Bless in modifiers, got: {result['modifiers_applied']}"

        print("[PASS] Bless attack integration test")

    finally:
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except:
            pass


def test_divine_favor_damage_integration():
    """Test that Divine Favor adds radiant damage."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE active_spell_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                spell_id TEXT NOT NULL,
                spell_name TEXT NOT NULL,
                spell_level_cast INTEGER NOT NULL,
                effect_type TEXT NOT NULL,
                effect_data TEXT,
                duration_type TEXT NOT NULL,
                duration_remaining INTEGER,
                rounds_remaining INTEGER,
                concentration BOOLEAN DEFAULT FALSE,
                caster_id TEXT,
                target_id TEXT,
                applied_at TEXT DEFAULT (datetime('now')),
                expires_at TEXT
            )
        """)
        conn.commit()
        conn.close()

        character_id = 'test-char-3'

        spell_effects = SpellEffectsService(db_path)
        spell_effects.apply_buff(
            character_id,
            {
                'type': 'damage_bonus_per_hit',
                'damage_dice': '1d4',
                'damage_type': 'radiant',
                'source': 'divine_favor'
            },
            duration_rounds=10
        )

        weapon_service = WeaponAttackService(db_path)
        weapon = {
            'name': 'Longsword',
            'damage_dice': '1d8',
            'weapon_properties': 'versatile'
        }
        character = {
            'id': character_id,
            'level': 2,
            'strength': 16,
            'dexterity': 12
        }

        result = weapon_service.calculate_attack_damage(weapon, character)

        assert any('Divine Favor' in mod or 'radiant' in mod for mod in result['modifiers_applied']), \
            f"Expected Divine Favor in modifiers, got: {result['modifiers_applied']}"

        print("[PASS] Divine Favor damage integration test")

    finally:
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except:
            pass


if __name__ == '__main__':
    print("Running spell effects integration tests...")
    print()

    test_shield_of_faith_ac_integration()

    print()
    print("[SUCCESS] AC integration test passed!")
    print("Note: Full weapon attack tests require complete database schema.")
