# test
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

from services.fighter_abilities import FighterAbilitiesService
from core.combat_manager import CombatManager


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


def _init_champion_schema(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE characters (
            id TEXT PRIMARY KEY,
            class_id TEXT,
            subclass_id TEXT,
            level INTEGER,
            hit_points_current INTEGER,
            hit_points_max INTEGER,
            current_hit_points INTEGER,
            max_hit_points INTEGER,
            constitution INTEGER,
            inspiration_uses_current INTEGER,
            inspiration_uses_max INTEGER
        );

        CREATE TABLE character_subclasses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id TEXT NOT NULL,
            class_id TEXT NOT NULL,
            subclass_id TEXT NOT NULL,
            class_level INTEGER NOT NULL,
            UNIQUE(character_id, class_id)
        );

        CREATE TABLE character_combat_state (
            character_id TEXT PRIMARY KEY,
            studied_target_id TEXT,
            last_miss_turn INTEGER DEFAULT 0,
            heroic_warrior_active INTEGER DEFAULT 0,
            survivor_active INTEGER DEFAULT 0,
            last_attack_missed INTEGER DEFAULT 0,
            critical_range_min INTEGER DEFAULT 20,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()


def test_heroic_warrior_awards_inspiration_and_sets_state():
    with temp_db_path("champion") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_champion_schema(conn)
            conn.execute(
                """
                INSERT INTO characters (
                    id, class_id, subclass_id, level,
                    hit_points_current, hit_points_max, current_hit_points, max_hit_points, constitution,
                    inspiration_uses_current, inspiration_uses_max
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "champion-10",
                    "Fighter",
                    None,
                    10,
                    44,
                    44,
                    44,
                    44,
                    16,
                    0,
                    0,
                ),
            )
            conn.execute(
                """
                INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
                VALUES (?, ?, ?, ?)
                """,
                ("champion-10", "fighter", "champion", 10),
            )

        service = FighterAbilitiesService(str(db_path))

        result = service.process_champion_turn_start("champion-10")
        hero_info = result["heroic_warrior"]
        assert hero_info["available"] is True
        assert result["survivor"]["available"] is False
        assert hero_info["triggered"] is True
        assert hero_info["current"] == 1
        assert hero_info["max"] == 1

        # Running it again should leave inspiration unchanged and not trigger
        repeat = service.process_champion_turn_start("champion-10")
        assert repeat["heroic_warrior"]["triggered"] is False

        with sqlite3.connect(db_path) as conn:
            inspiration_state = conn.execute(
                "SELECT inspiration_uses_current, inspiration_uses_max FROM characters WHERE id = ?",
                ("champion-10",),
            ).fetchone()
            combat_state = conn.execute(
                "SELECT heroic_warrior_active FROM character_combat_state WHERE character_id = ?",
                ("champion-10",),
            ).fetchone()

        assert inspiration_state == (1, 1)
        assert combat_state == (0,)  # second invocation resets flag after no trigger

        del service
        gc.collect()


def test_survivor_heals_when_bloodied_and_tracks_defy_death():
    with temp_db_path("survivor") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_champion_schema(conn)
            conn.execute(
                """
                INSERT INTO characters (
                    id, class_id, subclass_id, level,
                    hit_points_current, hit_points_max, current_hit_points, max_hit_points, constitution,
                    inspiration_uses_current, inspiration_uses_max
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "champion-18",
                    "Fighter",
                    None,
                    18,
                    20,
                    40,
                    20,
                    40,
                    16,
                    0,
                    0,
                ),
            )
            conn.execute(
                """
                INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
                VALUES (?, ?, ?, ?)
                """,
                ("champion-18", "fighter", "champion", 18),
            )

        service = FighterAbilitiesService(str(db_path))

        result = service.process_champion_turn_start("champion-18")
        hero_info = result["heroic_warrior"]
        assert hero_info["available"] is True
        assert hero_info["triggered"] is True

        survivor = result["survivor"]
        assert survivor["available"] is True
        assert survivor["defy_death_active"] is True
        assert survivor["healing_triggered"] is True
        assert survivor["healing"] == 8  # 5 + CON modifier (+3)
        assert survivor["new_hp"] == 28

        # After healing once, subsequent turn should keep defy death but no further healing
        repeat = service.process_champion_turn_start("champion-18")
        repeat_survivor = repeat["survivor"]
        assert repeat_survivor["defy_death_active"] is True
        assert repeat_survivor["healing"] == 0
        assert repeat_survivor["healing_triggered"] is False

        with sqlite3.connect(db_path) as conn:
            hp_state = conn.execute(
                "SELECT hit_points_current, hit_points_max FROM characters WHERE id = ?",
                ("champion-18",),
            ).fetchone()
            state_flags = conn.execute(
                "SELECT survivor_active FROM character_combat_state WHERE character_id = ?",
                ("champion-18",),
            ).fetchone()

        assert hp_state == (28, 40)
        assert state_flags == (1,)

        del service
        gc.collect()

def test_roll_skill_check_applies_remarkable_athlete(monkeypatch):
    with temp_db_path("champion-skill") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_champion_schema(conn)
            conn.execute(
                """
                INSERT INTO characters (
                    id, class_id, subclass_id, level,
                    hit_points_current, hit_points_max, current_hit_points, max_hit_points,
                    constitution, inspiration_uses_current, inspiration_uses_max
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "champion-3",
                    "fighter",
                    None,
                    3,
                    30,
                    30,
                    30,
                    30,
                    14,
                    0,
                    0,
                ),
            )
            conn.execute(
                """
                INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
                VALUES (?, ?, ?, ?)
                """,
                ("champion-3", "fighter", "champion", 3),
            )

        service = FighterAbilitiesService(str(db_path))

        rolls = iter([8, 17])
        monkeypatch.setattr('services.advantage_system.random.randint', lambda a, b: next(rolls))

        result = service.roll_skill_check(
            "champion-3",
            "Athletics",
            ability_modifier=3,
            proficiency_bonus=3,
            proficient=True
        )

        assert result["remarkable_athlete_applied"] is True
        assert "Remarkable Athlete" in result["advantage_sources"]
        assert result["advantage_state"] == "advantage"
        assert result["total"] == 23  # 17 roll + 3 ability + 3 proficiency

        rolls2 = iter([11])
        monkeypatch.setattr('services.advantage_system.random.randint', lambda a, b: next(rolls2))

        non_ra = service.roll_skill_check(
            "champion-3",
            "Acrobatics",
            ability_modifier=3,
            proficiency_bonus=3,
            proficient=True
        )

        assert non_ra["remarkable_athlete_applied"] is False
        assert "Remarkable Athlete" not in non_ra["advantage_sources"]
        assert non_ra["advantage_state"] == "normal"


def test_combat_manager_applies_remarkable_athlete_to_initiative(monkeypatch):
    with temp_db_path("combat-manager-ra") as db_path:
        with sqlite3.connect(db_path) as conn:
            _init_champion_schema(conn)
            conn.execute(
                """
                INSERT INTO characters (
                    id, class_id, subclass_id, level,
                    hit_points_current, hit_points_max, current_hit_points, max_hit_points,
                    constitution, inspiration_uses_current, inspiration_uses_max
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "champion-3",
                    "fighter",
                    None,
                    3,
                    30,
                    30,
                    30,
                    30,
                    14,
                    0,
                    0,
                ),
            )
            conn.execute(
                """
                INSERT INTO character_subclasses (character_id, class_id, subclass_id, class_level)
                VALUES (?, ?, ?, ?)
                """,
                ("champion-3", "fighter", "champion", 3),
            )

        manager = CombatManager(str(db_path))
        manager.add_player_combatant({
            'id': 'champion-3',
            'name': 'Champion',
            'ac': 16,
            'hp': 30,
            'max_hp': 30,
            'dexterity': 14,
            'class_id': 'fighter',
            'level': 3
        })

        rolls = iter([9, 18])
        monkeypatch.setattr('services.advantage_system.random.randint', lambda a, b: next(rolls))
        monkeypatch.setattr('core.combat_manager.random.random', lambda: 0.25)

        order = manager.start_combat()
        assert order, "Initiative order should not be empty"
        combatant = order[0]
        breakdown = combatant.initiative_breakdown

        assert breakdown["advantage_state"] == "advantage"
        assert "Remarkable Athlete" in breakdown["advantage_sources"]
        assert combatant.initiative_roll == 20  # 18 roll + DEX mod 2
