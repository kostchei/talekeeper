import sqlite3
from pathlib import Path
import sys

import pytest

# Ensure project imports resolve when running from the test directory
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from action_cards.action_panel import ActionPanel  # noqa: E402


@pytest.fixture
def mastery_db(tmp_path):
    db_path = tmp_path / "talekeeper.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE weapon_masteries (
            name TEXT PRIMARY KEY,
            trigger_condition TEXT,
            description TEXT,
            requires_save INTEGER,
            save_ability TEXT,
            save_dc_formula TEXT,
            damage_formula TEXT,
            special_effects TEXT
        );

        CREATE TABLE equipment (
            name TEXT PRIMARY KEY,
            description TEXT,
            item_type TEXT,
            rarity TEXT,
            cost_gp REAL,
            weight_lb REAL,
            weapon_category TEXT,
            damage_dice TEXT,
            damage_type TEXT,
            weapon_properties TEXT,
            weapon_mastery TEXT,
            range_normal INTEGER,
            range_long INTEGER,
            versatile_damage TEXT,
            ammunition TEXT,
            armor_class INTEGER,
            armor_type TEXT,
            dex_bonus_max INTEGER,
            strength_requirement INTEGER,
            stealth_disadvantage INTEGER,
            is_magical INTEGER
        );
        """
    )

    cursor.execute(
        """
        INSERT INTO weapon_masteries (
            name, trigger_condition, description, requires_save,
            save_ability, save_dc_formula, damage_formula, special_effects
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Cleave",
            "on_hit",
            "Cleave through your foes",
            0,
            None,
            None,
            None,
            "extra_attack_adjacent",
        ),
    )

    cursor.execute(
        """
        INSERT INTO equipment (
            name, description, item_type, rarity, cost_gp, weight_lb,
            weapon_category, damage_dice, damage_type, weapon_properties,
            weapon_mastery, range_normal, range_long, versatile_damage,
            ammunition, armor_class, armor_type, dex_bonus_max,
            strength_requirement, stealth_disadvantage, is_magical
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Longsword",
            "A versatile martial weapon",
            "weapon",
            "uncommon",
            15,
            3,
            "martial",
            "1d8",
            "slashing",
            '["versatile"]',
            "Cleave",
            None,
            None,
            "1d10",
            None,
            None,
            None,
            None,
            None,
            0,
            0,
        ),
    )

    conn.commit()
    conn.close()
    return db_path


def test_variant_weapon_hydrates_and_applies_mastery(qtbot, mastery_db):
    panel = ActionPanel()
    qtbot.addWidget(panel)

    panel.set_character_context(
        {
            "id": "char-1",
            "class_id": "fighter",
            "db_path": str(mastery_db),
            "strength": 16,
            "dexterity": 12,
            "level": 5,
        }
    )

    panel.load_character_equipment(
        {
            "main_hand": {
                "name": "Longsword +1",
                "item_type": "weapon",
                "attack_bonus": 1,
                "damage_bonus": 1,
            }
        },
        {"strength": 16, "dexterity": 12},
    )

    main_weapon = panel.equipped_weapons["main_hand"]
    assert main_weapon["damage_dice"] == "1d8"
    assert main_weapon["damage_type"] == "slashing"
    assert "versatile" in main_weapon["weapon_properties"]
    assert main_weapon.get("weapon_mastery") == "Cleave"

    panel.load_weapon_masteries(
        ["Cleave"],
        [
            {
                "weapon_name": "Longsword +1",
                "mastery_type": "Cleave",
            }
        ],
    )

    context = {"strength": 16, "dexterity": 12}
    result = panel._apply_weapon_mastery_effects("Longsword +1", 15, 12, True, 8, context)
    assert result.get("cleave") is True

    repeat = panel._apply_weapon_mastery_effects("Longsword +1", 14, 13, True, 6, context)
    assert repeat.get("cleave") is True
