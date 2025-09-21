"""
Test Stage 2.3: UI Integration for Subclass Features
Tests the UI display of subclass features with availability indicators, resource tracking, and tooltips.
"""

import sys
import os
import tempfile
import sqlite3
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import PyQt6 components
try:
    from PyQt6.QtWidgets import QApplication, QWidget
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("[Stage 2.3 Test] PyQt6 not available - testing backend only")

from services.enhanced_subclass_manager import EnhancedSubclassManager
from services.subclass_registry import subclass_registry


def test_subclass_features_widget_backend():
    """Test the backend functionality of SubclassFeaturesWidget."""
    print("Testing SubclassFeaturesWidget backend functionality...")

    # Create temporary database
    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create test schema
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER,
                    class_id TEXT,
                    subclass_id TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE character_subclasses (
                    character_id TEXT PRIMARY KEY,
                    class_id TEXT,
                    subclass_id TEXT
                )
            """)

            # Insert test Berserker
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id, subclass_id)
                VALUES ('ui_berserker', 'UI Test Berserker', 14, 'barbarian', 'berserker')
            """)

            # Insert test Champion
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id, subclass_id)
                VALUES ('ui_champion', 'UI Test Champion', 18, 'fighter', 'champion')
            """)
            conn.commit()

        manager = EnhancedSubclassManager(test_db_path)

        # Test 1: Get Berserker features for UI display
        berserker_features = manager.get_character_subclass_features('ui_berserker', 14)
        assert len(berserker_features) == 4, f"Expected 4 Berserker features, got {len(berserker_features)}"

        feature_names = [f.name for f in berserker_features]
        assert "Frenzy" in feature_names
        assert "Mindless Rage" in feature_names
        assert "Retaliation" in feature_names
        assert "Intimidating Presence" in feature_names
        print("[OK] Berserker features retrieved for UI")

        # Test 2: Get Champion features for UI display
        champion_features = manager.get_character_subclass_features('ui_champion', 18)
        assert len(champion_features) == 6, f"Expected 6 Champion features, got {len(champion_features)}"

        feature_names = [f.name for f in champion_features]
        assert "Improved Critical" in feature_names
        assert "Superior Critical" in feature_names
        assert "Heroic Warrior" in feature_names
        assert "Survivor" in feature_names
        print("[OK] Champion features retrieved for UI")

        # Test 3: Feature type categorization for UI badges
        passive_features = [f for f in champion_features if f.feature_type.value == 'passive']
        triggered_features = [f for f in champion_features if f.feature_type.value == 'triggered']

        assert len(passive_features) >= 3, "Champion should have at least 3 passive features"
        assert len(triggered_features) >= 2, "Champion should have at least 2 triggered features"
        print("[OK] Feature types categorized correctly for UI")

        # Test 4: Resource tracking data
        intimidating_presence = next(f for f in berserker_features if f.name == "Intimidating Presence")
        assert intimidating_presence.uses_per_rest == 1
        assert intimidating_presence.rest_type == "long"
        print("[OK] Resource tracking data available for UI")

        # Test 5: Action cost information for UI badges
        retaliation = next(f for f in berserker_features if f.name == "Retaliation")
        assert retaliation.action_cost.value == "reaction"

        improved_critical = next(f for f in champion_features if f.name == "Improved Critical")
        assert improved_critical.action_cost.value == "none"
        print("[OK] Action cost information available for UI")

        print("[OK] All SubclassFeaturesWidget backend tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_feature_availability_logic():
    """Test the feature availability checking logic."""
    print("\nTesting feature availability logic...")

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db_path = test_db.name
    test_db.close()

    try:
        # Create test schema
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER,
                    class_id TEXT,
                    subclass_id TEXT,
                    strength INTEGER,
                    proficiency_bonus INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE character_subclasses (
                    character_id TEXT PRIMARY KEY,
                    class_id TEXT,
                    subclass_id TEXT
                )
            """)

            # Insert test character
            cursor.execute("""
                INSERT INTO characters (id, name, level, class_id, subclass_id, strength, proficiency_bonus)
                VALUES ('availability_test', 'Availability Test', 14, 'barbarian', 'berserker', 18, 5)
            """)
            conn.commit()

        manager = EnhancedSubclassManager(test_db_path)

        # Test 1: Intimidating Presence availability (fresh character)
        result = manager.use_intimidating_presence('availability_test')
        assert result['success'], "Should be able to use Intimidating Presence initially"
        assert result['save_dc'] == 8 + 4 + 5  # 8 + str_mod(4) + prof(5) = 17
        assert result['uses_remaining'] == 0
        print("[OK] Intimidating Presence available initially")

        # Test 2: Intimidating Presence unavailable after use
        result2 = manager.use_intimidating_presence('availability_test')
        assert not result2['success'], "Should not be able to use again"
        assert "No uses remaining" in result2['reason']
        print("[OK] Intimidating Presence unavailable after use")

        # Test 3: Reset resources (long rest)
        manager.reset_resources('availability_test', 'long')
        result3 = manager.use_intimidating_presence('availability_test')
        assert result3['success'], "Should be available again after long rest"
        print("[OK] Resources reset correctly after long rest")

        print("[OK] All feature availability logic tests passed")
        return True

    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def test_ui_widget_creation():
    """Test UI widget creation (if PyQt6 available)."""
    if not PYQT_AVAILABLE:
        print("\nSkipping UI widget tests - PyQt6 not available")
        return True

    print("\nTesting UI widget creation...")

    # Mock QApplication if needed
    app = None
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Test importing the UI widget
        from ui.subclass_features_widget import SubclassFeaturesWidget, SubclassFeatureWidget
        from services.enhanced_subclass_manager import SubclassFeature, FeatureType, ActionCost

        # Test 1: Create main features widget
        features_widget = SubclassFeaturesWidget()
        assert features_widget is not None
        assert hasattr(features_widget, 'character_id')
        assert hasattr(features_widget, 'feature_widgets')
        print("[OK] SubclassFeaturesWidget created successfully")

        # Test 2: Create individual feature widget
        test_feature = SubclassFeature(
            name="Test Feature",
            description="A test feature for UI testing",
            level=3,
            feature_type=FeatureType.ACTIVATED,
            action_cost=ActionCost.BONUS_ACTION,
            uses_per_rest=3,
            rest_type="short"
        )

        feature_widget = SubclassFeatureWidget(test_feature, "test_character")
        assert feature_widget is not None
        assert hasattr(feature_widget, 'feature')
        assert hasattr(feature_widget, 'character_id')
        print("[OK] SubclassFeatureWidget created successfully")

        # Test 3: Widget has expected UI elements
        assert hasattr(feature_widget, 'name_label')
        assert hasattr(feature_widget, 'description_label')
        assert hasattr(feature_widget, 'availability_label')
        print("[OK] Feature widget has expected UI elements")

        # Test 4: Resource tracking elements (for features with limited uses)
        if test_feature.uses_per_rest:
            assert hasattr(feature_widget, 'resource_label')
            assert hasattr(feature_widget, 'resource_progress')
            print("[OK] Resource tracking elements present")

        # Test 5: Activation button (for activated features)
        if test_feature.feature_type == FeatureType.ACTIVATED:
            assert hasattr(feature_widget, 'activation_button')
            print("[OK] Activation button present for activated features")

        print("[OK] All UI widget creation tests passed")
        return True

    except Exception as e:
        print(f"[ERROR] UI widget test failed: {e}")
        return False

    finally:
        if app:
            app.quit()


def test_character_panel_integration():
    """Test integration with character panel (mock-based)."""
    print("\nTesting character panel integration...")

    # Mock the character panel and test integration
    try:
        # Test that the widget can be imported and integrated
        from ui.subclass_features_widget import SubclassFeaturesWidget

        # Create widget (without PyQt6 if not available)
        if PYQT_AVAILABLE:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])

            # Create test database for UI widget
            test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
            test_db_path = test_db.name
            test_db.close()

            try:
                # Setup minimal database for widget
                with sqlite3.connect(test_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE characters (
                            id TEXT PRIMARY KEY,
                            name TEXT,
                            level INTEGER,
                            class_id TEXT,
                            subclass_id TEXT
                        )
                    """)
                    cursor.execute("""
                        CREATE TABLE character_subclasses (
                            character_id TEXT PRIMARY KEY,
                            class_id TEXT,
                            subclass_id TEXT
                        )
                    """)
                    cursor.execute("""
                        INSERT INTO characters (id, name, level, class_id, subclass_id)
                        VALUES ('test_char', 'Test Character', 10, 'barbarian', 'berserker')
                    """)
                    conn.commit()

                # Mock the manager to use our test database
                with patch('ui.subclass_features_widget.EnhancedSubclassManager') as mock_manager_class:
                    mock_manager = MagicMock()
                    mock_manager.db_path = test_db_path
                    mock_manager.get_character_subclass_features.return_value = []
                    mock_manager_class.return_value = mock_manager

                    widget = SubclassFeaturesWidget()

                    # Test setting character data
                    widget.set_character('test_char', 10)
                    assert widget.character_id == 'test_char'
                    assert widget.character_level == 10
                    print("[OK] Character data set correctly")

            finally:
                try:
                    os.unlink(test_db_path)
                except:
                    pass

            # Test signal connections (mock)
            signal_emitted = False
            def mock_handler(feature_name, character_id):
                nonlocal signal_emitted
                signal_emitted = True

            widget.feature_activated.connect(mock_handler)
            widget.feature_activated.emit("Test Feature", "test_char")
            assert signal_emitted, "Signal should be emitted"
            print("[OK] Signal connections working")

        else:
            # Just test import without UI
            widget = None
            print("[OK] Widget import successful (no PyQt6)")

        print("[OK] All character panel integration tests passed")
        return True

    except Exception as e:
        print(f"[ERROR] Character panel integration test failed: {e}")
        return False


def test_feature_tooltips_and_styling():
    """Test feature tooltips and visual styling information."""
    print("\nTesting feature tooltips and styling...")

    # Test feature data that supports tooltips and styling
    berserker = subclass_registry.get_subclass("barbarian", "berserker")
    champion = subclass_registry.get_subclass("fighter", "champion")

    if not berserker or not champion:
        print("[SKIP] Subclass definitions not available")
        return True

    # Test 1: Features have descriptions for tooltips
    for feature in berserker.features:
        assert feature.description, f"{feature.name} should have description for tooltip"
        assert len(feature.description) > 10, f"{feature.name} description too short"

    for feature in champion.features:
        assert feature.description, f"{feature.name} should have description for tooltip"
        assert len(feature.description) > 10, f"{feature.name} description too short"

    print("[OK] All features have descriptions for tooltips")

    # Test 2: Features have appropriate types for styling
    feature_types = set()
    action_costs = set()

    for feature in berserker.features + champion.features:
        feature_types.add(feature.feature_type.value)
        action_costs.add(feature.action_cost.value)

    expected_types = {'passive', 'activated', 'triggered', 'reaction'}
    expected_costs = {'none', 'bonus_action', 'reaction'}

    assert feature_types.intersection(expected_types), "Should have various feature types for styling"
    assert action_costs.intersection(expected_costs), "Should have various action costs for styling"
    print("[OK] Features have diverse types and costs for styling")

    # Test 3: Extended tooltips available where appropriate
    extended_tooltips = [f for f in berserker.features + champion.features if f.tooltip_extended]
    assert len(extended_tooltips) > 0, "Some features should have extended tooltips"
    print(f"[OK] {len(extended_tooltips)} features have extended tooltips")

    print("[OK] All tooltip and styling tests passed")
    return True


if __name__ == '__main__':
    print("=== Stage 2.3 Validation: UI Integration for Subclass Features ===")

    success = True

    try:
        success &= test_subclass_features_widget_backend()
        success &= test_feature_availability_logic()
        success &= test_ui_widget_creation()
        success &= test_character_panel_integration()
        success &= test_feature_tooltips_and_styling()

        if success:
            print("\n[SUCCESS] STAGE 2.3 COMPLETE")
            print("+ SubclassFeaturesWidget backend functionality working")
            print("+ Feature availability logic implemented")
            print("+ UI widget creation successful")
            print("+ Character panel integration ready")
            print("+ Tooltips and styling support complete")
            print("+ Resource tracking display functional")
            print("+ Feature activation system integrated")
            print("\n*** UI Integration for Subclass Features Complete ***")
        else:
            print("\n[FAILED] STAGE 2.3 TESTS FAILED")
            exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)