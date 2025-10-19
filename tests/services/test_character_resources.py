#test
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.character_resources import CharacterResourceService


@pytest.fixture
def resource_db(tmp_path: Path) -> str:
    db_path = tmp_path / "character_resources.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE characters (
            id TEXT PRIMARY KEY,
            race_id TEXT,
            inspiration_uses_current INTEGER DEFAULT 0,
            inspiration_uses_max INTEGER DEFAULT 0,
            lucky_uses_current INTEGER DEFAULT 0,
            lucky_uses_max INTEGER DEFAULT 0
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE character_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id TEXT NOT NULL,
            resource_name TEXT NOT NULL,
            current_uses INTEGER NOT NULL,
            max_uses INTEGER NOT NULL,
            rest_type TEXT NOT NULL,
            source_class TEXT,
            source_level INTEGER
        )
        """
    )
    conn.commit()
    conn.close()
    return str(db_path)


def test_human_long_rest_grants_inspiration(resource_db: str):
    service = CharacterResourceService(resource_db)
    conn = sqlite3.connect(resource_db)
    conn.execute(
        "INSERT INTO characters (id, race_id, inspiration_uses_current, inspiration_uses_max) VALUES (?, ?, ?, ?)",
        ("char-human", "human", 0, 0),
    )
    conn.commit()
    conn.close()

    result = service.restore_resources_by_rest_type("char-human", "long_rest")
    assert result["success"] is True

    conn = sqlite3.connect(resource_db)
    row = conn.execute(
        "SELECT inspiration_uses_current, inspiration_uses_max FROM characters WHERE id = ?",
        ("char-human",),
    ).fetchone()
    conn.close()

    assert row == (1, 1)
    hero_entries = [
        resource
        for resource in result.get("restored_resources", [])
        if resource.get("resource_name") == "Heroic Inspiration"
    ]
    assert hero_entries, "Heroic Inspiration should be reported for human long rests"
    assert hero_entries[0]["gained"] == 1


def test_non_human_long_rest_does_not_grant_inspiration(resource_db: str):
    service = CharacterResourceService(resource_db)
    conn = sqlite3.connect(resource_db)
    conn.execute(
        "INSERT INTO characters (id, race_id, inspiration_uses_current, inspiration_uses_max) VALUES (?, ?, ?, ?)",
        ("char-elf", "elf", 0, 0),
    )
    conn.commit()
    conn.close()

    result = service.restore_resources_by_rest_type("char-elf", "long_rest")
    assert result["success"] is True

    conn = sqlite3.connect(resource_db)
    row = conn.execute(
        "SELECT inspiration_uses_current, inspiration_uses_max FROM characters WHERE id = ?",
        ("char-elf",),
    ).fetchone()
    conn.close()

    assert row == (0, 0)
    assert all(
        resource.get("resource_name") != "Heroic Inspiration"
        for resource in result.get("restored_resources", [])
    )
