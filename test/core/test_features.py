import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import sqlite3
import tempfile

import pytest
from PyQt6.QtWidgets import QApplication

from action_cards.action_panel import ActionPanel, ActionType
from services.character_resources import CharacterResourceService

from core.class_features import FeatureManager
from core.feature_integration import FeatureSystemIntegration


@pytest.fixture
def fighter_feature_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "fighter_features.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                class_id TEXT NOT NULL,
                level INTEGER NOT NULL,
                subclass_id TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE fighter_features (
                character_id TEXT PRIMARY KEY,
                level INTEGER,
                fighting_style TEXT,
                action_surge_uses_max INTEGER,
                action_surge_uses_current INTEGER,
                second_wind_used INTEGER,
                indomitable_uses_max INTEGER,
                indomitable_uses_current INTEGER,
                extra_attacks INTEGER,
                weapon_masteries_known INTEGER
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE character_features (
                character_id TEXT,
                feature_name TEXT,
                feature_type TEXT,
                description TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE character_feats (
                character_id TEXT,
                feat_name TEXT
            )
            """
        )
        conn.commit()
        conn.close()
        yield str(db_path)


@pytest.fixture
def integration_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "integration.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                class_id TEXT NOT NULL,
                level INTEGER NOT NULL,
                subclass_id TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE fighter_features (
                character_id TEXT PRIMARY KEY,
                level INTEGER,
                fighting_style TEXT,
                action_surge_uses_max INTEGER,
                action_surge_uses_current INTEGER,
                second_wind_used INTEGER,
                indomitable_uses_max INTEGER,
                indomitable_uses_current INTEGER,
                extra_attacks INTEGER,
                weapon_masteries_known INTEGER
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE character_features (
                character_id TEXT,
                feature_name TEXT,
                feature_type TEXT,
                description TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE character_feats (
                character_id TEXT,
                feat_name TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE character_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                current_uses INTEGER NOT NULL,
                max_uses INTEGER NOT NULL,
                rest_type TEXT NOT NULL,
                source_class TEXT,
                source_level INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(character_id, resource_name)
            )
            """
        )
        conn.commit()
        conn.close()
        yield str(db_path)


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

def test_feature_manager_loads_fighter_progression(fighter_feature_db):
    character_id = "fighter-9"
    conn = sqlite3.connect(fighter_feature_db)
    conn.execute(
        "INSERT INTO characters (id, class_id, level, subclass_id) VALUES (?, ?, ?, ?)",
        (character_id, "Fighter", 9, None)
    )
    conn.execute(
        "INSERT INTO fighter_features VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (character_id, 9, "defense", 1, 1, 0, 1, 1, 2, 4)
    )
    conn.commit()
    conn.close()

    manager = FeatureManager(fighter_feature_db)
    manager.load_character_features(character_id)

    feature_keys = set(manager.features.keys())
    expected_keys = {
        "second_wind",
        "fighting_style",
        "weapon_mastery",
        "action_surge",
        "tactical_mind",
        "tactical_shift",
        "extra_attack",
        "indomitable",
        "tactical_master",
    }
    assert expected_keys.issubset(feature_keys)

    second_wind = manager.features["second_wind"]
    action_surge = manager.features["action_surge"]
    indomitable = manager.features["indomitable"]

    assert second_wind.resource.maximum == 3
    assert second_wind.resource.current == 3
    assert action_surge.resource.maximum == 1
    assert indomitable.resource.maximum == 1




def test_initialize_character_features_seeds_resources(integration_db):
    character_id = "fighter-9"
    conn = sqlite3.connect(integration_db)
    conn.execute(
        "INSERT INTO characters (id, class_id, level, subclass_id) VALUES (?, ?, ?, ?)",
        (character_id, "Fighter", 9, None)
    )
    conn.commit()
    conn.close()

    integration = FeatureSystemIntegration(integration_db)
    assert integration.initialize_character_features(character_id) is True

    conn = sqlite3.connect(integration_db)
    state_rows = conn.execute(
        "SELECT feature_name FROM feature_states WHERE character_id = ?",
        (character_id,)
    ).fetchall()
    feature_names = {row[0] for row in state_rows}
    assert {"Second Wind", "Action Surge", "Indomitable"}.issubset(feature_names)

    resource_rows = conn.execute(
        "SELECT resource_name, current_uses, max_uses FROM character_resources WHERE character_id = ?",
        (character_id,)
    ).fetchall()
    resources = {name: (current, maximum) for name, current, maximum in resource_rows}
    assert resources.get("Second Wind") == (3, 3)
    assert resources.get("Action Surge") == (1, 1)
    assert resources.get("Indomitable") == (1, 1)
    conn.close()

def test_action_panel_uses_resource_service(qt_app, integration_db):
    character_id = "fighter-ui"
    conn = sqlite3.connect(integration_db)
    conn.execute(
        "INSERT INTO characters (id, class_id, level, subclass_id) VALUES (?, ?, ?, ?)",
        (character_id, "Fighter", 9, None)
    )
    conn.commit()
    conn.close()

    integration = FeatureSystemIntegration(integration_db)
    assert integration.initialize_character_features(character_id) is True

    features = integration.get_available_features(character_id)
    feature_map = {feature["name"]: feature for feature in features}

    panel = ActionPanel()
    panel._resource_service = CharacterResourceService(integration_db)
    panel.set_character_context({'id': character_id, 'class_id': 'fighter', 'level': 9})

    panel.load_character_features(feature_map)

    assert ActionType.SECOND_WIND in panel.action_cards
    assert panel._get_ability_uses_remaining('Second Wind') == 3

    panel._use_ability('Second Wind')

    assert panel._get_ability_uses_remaining('Second Wind') == 2

    panel.deleteLater()
    qt_app.processEvents()


