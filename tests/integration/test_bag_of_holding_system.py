"""
Integration tests for the Bag of Holding system.
"""
import sys
import sqlite3
import uuid
import random
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))

from database.database_init import DatabaseInitializer  # noqa: E402
from talekeeper.core.game_engine_sqlite import GameEngineSQLite  # noqa: E402
from talekeeper.services.treasure_generator import TreasureGenerator  # noqa: E402


@pytest.fixture()
def db_path(tmp_path):
    """Create a fresh database and ensure schema upgrades run."""
    db_file = tmp_path / "bag_system.db"
    initializer = DatabaseInitializer(str(db_file))
    assert initializer.initialize(force=True)
    return str(db_file)


def _insert_character(db_path: str) -> str:
    character_id = f"char_{uuid.uuid4().hex[:8]}"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO characters (id, name, race_id, class_id, background_id)
            VALUES (?, 'Bag Tester', 'human', 'fighter', 'soldier')
            """,
            (character_id,),
        )
        conn.commit()
    return character_id


def _give_bag_of_holding(db_path: str, character_id: str):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO character_inventory
            (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp)
            VALUES (?, ?, 'Bag of Holding', 'wondrous item', 1, 15.0,
                    'A magical extradimensional storage bag.', 0)
            """,
            (str(uuid.uuid4()), character_id),
        )
        conn.commit()


def _fetch_gold_rows(db_path: str, character_id: str):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT quantity, weight_lb, stored_in_bag
            FROM character_inventory
            WHERE character_id = ? AND item_name = 'Gold Pieces'
            ORDER BY stored_in_bag DESC
            """,
            (character_id,),
        )
        return cursor.fetchall()


def test_schema_includes_bag_columns(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(character_inventory)")
        columns = {row[1] for row in cursor.fetchall()}

    assert "stored_in_bag" in columns
    assert "treasure_type" in columns
    assert "unit_value_gp" in columns


def test_gold_routes_to_bag_when_available(db_path):
    engine = GameEngineSQLite(db_path)
    character_id = _insert_character(db_path)
    _give_bag_of_holding(db_path, character_id)

    assert engine.add_gold_to_character_sync(character_id, 100)

    rows = _fetch_gold_rows(db_path, character_id)
    assert len(rows) == 1
    quantity, weight, stored_in_bag = rows[0]
    assert stored_in_bag == 1
    assert quantity == 100
    assert pytest.approx(weight, rel=1e-6) == 2.0


def test_rebalance_moves_existing_coin_into_bag(db_path):
    engine = GameEngineSQLite(db_path)
    character_id = _insert_character(db_path)

    # No bag yet; coins remain on person.
    assert engine.add_gold_to_character_sync(character_id, 400)

    _give_bag_of_holding(db_path, character_id)
    # Adding more gold should move previous coins into the bag as well.
    assert engine.add_gold_to_character_sync(character_id, 100)

    rows = _fetch_gold_rows(db_path, character_id)
    assert len(rows) == 1
    quantity, weight, stored_in_bag = rows[0]
    assert stored_in_bag == 1
    assert quantity == 500
    assert pytest.approx(weight, rel=1e-6) == 10.0


def test_bag_capacity_redirects_excess_gold(db_path):
    engine = GameEngineSQLite(db_path)
    character_id = _insert_character(db_path)
    _give_bag_of_holding(db_path, character_id)

    # Preload the bag with a heavy object (499 lb).
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO character_inventory
            (id, character_id, item_name, item_type, quantity, weight_lb, description,
             treasure_type, stored_in_bag)
            VALUES (?, ?, 'Lead Statue', 'treasure', 1, 499.0, 'Almost full bag load.',
                    'art', 1)
            """,
            (str(uuid.uuid4()), character_id),
        )
        conn.commit()

    assert engine.add_gold_to_character_sync(character_id, 200)

    rows = _fetch_gold_rows(db_path, character_id)
    assert len(rows) == 2  # One in bag, one on person

    bag_row = next(row for row in rows if row[2] == 1)
    person_row = next(row for row in rows if row[2] == 0)

    assert bag_row[0] == 50  # Only 50 coins fit (1 lb available)
    assert pytest.approx(bag_row[1], rel=1e-6) == 1.0
    assert person_row[0] == 150  # Remaining coins stay on person
    assert pytest.approx(person_row[1], rel=1e-6) == 3.0


def test_treasure_exceeding_capacity_goes_to_inventory(db_path):
    engine = GameEngineSQLite(db_path)
    character_id = _insert_character(db_path)
    _give_bag_of_holding(db_path, character_id)

    # Fill the bag close to capacity.
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO character_inventory
            (id, character_id, item_name, item_type, quantity, weight_lb, treasure_type,
             stored_in_bag)
            VALUES (?, ?, 'Stone Block', 'treasure', 1, 495.0, 'art', 1)
            """,
            (str(uuid.uuid4()), character_id),
        )
        conn.commit()

    heavy_art = {
        "name": "Marble Bust",
        "item_type": "treasure",
        "treasure_type": "art",
        "value_gp": 500,
        "unit_value_gp": 500,
        "quantity": 1,
        "weight_lb": 15.0,
        "description": "Too heavy for the bag right now."
    }

    assert engine.add_treasure_to_character_sync(character_id, heavy_art)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT stored_in_bag
            FROM character_inventory
            WHERE character_id = ? AND item_name = 'Marble Bust'
            """,
            (character_id,),
        )
        stored_flag = cursor.fetchone()[0]

        cursor.execute(
            "SELECT SUM(weight_lb) FROM character_inventory WHERE character_id = ? AND stored_in_bag = 1",
            (character_id,),
        )
        total_bag_weight = cursor.fetchone()[0]

    assert stored_flag == 0
    assert total_bag_weight <= 500.0


def test_treasure_generator_conversion_returns_tuple():
    random.seed(42)
    treasures, remaining = TreasureGenerator.convert_gold_to_treasure(2000, cr=8)

    assert isinstance(treasures, list)
    assert isinstance(remaining, int)
    total_value = sum(item["value_gp"] for item in treasures) + remaining
    assert total_value <= 2000
    for item in treasures:
        assert item["treasure_type"] in {"gem", "art"}
        assert item["weight_lb"] >= 0.0


def test_inventory_sync_reports_bag_state_and_total_weight(db_path):
    engine = GameEngineSQLite(db_path)
    character_id = _insert_character(db_path)
    _give_bag_of_holding(db_path, character_id)

    assert engine.add_gold_to_character_sync(character_id, 1500)

    inventory = engine.get_character_inventory_sync(character_id)
    coins = next(item for item in inventory if item["name"] == "Gold Pieces")

    assert coins["stored_in_bag"] == 1
    assert coins["treasure_type"] == "coins"
    assert coins["quantity"] == 1500
    assert pytest.approx(coins["weight_total_lb"], rel=1e-6) == 1500 / 50
    # weight_lb should reflect per-coin weight once normalized for UI calculations
    assert pytest.approx(coins["weight_lb"] * coins["quantity"], rel=1e-6) == coins["weight_total_lb"]
