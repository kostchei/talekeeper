#test
"""
Test UI Action Card Integration

Tests the enhanced action card system with visual states and economy awareness.
Stage 3.4: Visual testing for action card generation and states.
"""

import sys
sys.path.append('..')

import tempfile
import sqlite3
import os
from models.action_economy import ActionEconomyState
from services.action_card_generator import (
    ActionCardGenerator, EnhancedActionCard,
    generate_action_cards_for_character, get_action_cards_by_availability
)


class TestUIActionCards:
    """Test enhanced action card system"""

    def setup_method(self):
        """Setup test database and generator"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Initialize database schema
        self._setup_test_database()

        # Create generator
        self.generator = ActionCardGenerator(self.db_path)

    def teardown_method(self):
        """Cleanup test database"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _setup_test_database(self):
        """Setup minimal database schema for testing"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Characters table
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    class_id TEXT,
                    level INTEGER DEFAULT 1
                )
            """)

            # Character subclasses table
            cursor.execute("""
                CREATE TABLE character_subclasses (
                    character_id TEXT,
                    class_id TEXT,
                    subclass_id TEXT,
                    PRIMARY KEY (character_id, class_id)
                )
            """)

            # Barbarian features table
            cursor.execute("""
                CREATE TABLE barbarian_features (
                    character_id TEXT PRIMARY KEY,
                    level INTEGER,
                    rage_uses_current INTEGER DEFAULT 2,
                    rage_uses_max INTEGER DEFAULT 2,
                    brutal_strike_uses_current INTEGER DEFAULT 0,
                    brutal_strike_uses_max INTEGER DEFAULT 0,
                    intimidating_presence_uses_current INTEGER DEFAULT 0,
                    intimidating_presence_uses_max INTEGER DEFAULT 0,
                    is_raging BOOLEAN DEFAULT FALSE,
                    reckless_attack_available BOOLEAN DEFAULT FALSE
                )
            """)

            # Combat state table
            cursor.execute("""
                CREATE TABLE character_combat_state (
                    character_id TEXT PRIMARY KEY,
                    reckless_attack_active BOOLEAN DEFAULT FALSE,
                    raging BOOLEAN DEFAULT FALSE
                )
            """)

            conn.commit()

    def _create_test_character(self, character_id="test_char", class_name="barbarian",
                              level=1, subclass="berserker", rage_uses=2):
        """Create a test character"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert character
            cursor.execute("""
                INSERT INTO characters (id, name, class_id, level)
                VALUES (?, ?, ?, ?)
            """, (character_id, f"Test {class_name.title()}", class_name, level))

            # Insert subclass if specified
            if subclass:
                cursor.execute("""
                    INSERT INTO character_subclasses (character_id, class_id, subclass_id)
                    VALUES (?, ?, ?)
                """, (character_id, class_name, subclass))

            # Insert class features
            if class_name == "barbarian":
                cursor.execute("""
                    INSERT INTO barbarian_features (
                        character_id, level, rage_uses_current, rage_uses_max,
                        brutal_strike_uses_current, brutal_strike_uses_max,
                        intimidating_presence_uses_current, intimidating_presence_uses_max,
                        reckless_attack_available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    character_id, level, rage_uses, rage_uses,  # rage
                    1 if level >= 9 else 0, 1 if level >= 9 else 0,  # brutal strike
                    1 if level >= 14 else 0, 1 if level >= 14 else 0,  # intimidating presence
                    level >= 2  # reckless attack
                ))

            conn.commit()

    def test_action_card_generation(self):
        """Test generating action cards from registry"""
        # Create high-level berserker
        self._create_test_character("card_test", "barbarian", level=20, subclass="berserker")

        # Generate action cards
        cards = self.generator.generate_character_action_cards("card_test")

        # Should have multiple cards
        assert len(cards) > 0, "Should generate action cards"

        # Check for specific barbarian actions
        card_names = [card.name for card in cards]
        assert "Rage" in card_names, "Should have Rage card"
        assert "Reckless Attack" in card_names, "Should have Reckless Attack card"
        assert "Intimidating Presence" in card_names, "Should have Intimidating Presence card"

        # Check card properties
        rage_card = next(card for card in cards if card.name == "Rage")
        assert rage_card.action_id == "barbarian_rage"
        assert rage_card.economy_type == "bonus_action"
        assert rage_card.available, "Rage should be available"

    def test_economy_state_awareness(self):
        """Test that cards reflect action economy state"""
        # Create character
        self._create_test_character("economy_test", "barbarian", level=5)

        # Create combat state with bonus action used
        combat_state = ActionEconomyState(
            combatant_id="economy_test",
            combatant_name="Test",
            action_available=True,
            bonus_action_available=False  # Bonus action used
        )

        # Generate cards with combat state
        cards = self.generator.generate_character_action_cards("economy_test", combat_state)

        # Find rage card (uses bonus action)
        rage_card = next((card for card in cards if card.name == "Rage"), None)
        assert rage_card is not None, "Should have Rage card"

        # Rage should be unavailable due to bonus action being used
        assert not rage_card.available, "Rage should be unavailable when bonus action is used"
        assert "bonus action" in rage_card.reason_unavailable.lower(), "Should mention bonus action in reason"

    def test_resource_cost_display(self):
        """Test that resource costs are displayed correctly"""
        # Create character
        self._create_test_character("resource_test", "barbarian", level=5)

        # Generate cards
        cards = self.generator.generate_character_action_cards("resource_test")

        # Find rage card
        rage_card = next((card for card in cards if card.name == "Rage"), None)
        assert rage_card is not None, "Should have Rage card"

        # Check resource cost display
        assert len(rage_card.resource_costs) > 0, "Rage should have resource costs"
        assert "Rage Uses" in rage_card.resource_costs, "Should show rage uses cost"

        # Check cost display
        assert "Bonus" in rage_card.cost_display, "Should show bonus action cost"
        assert "Rage Uses" in rage_card.cost_display, "Should show rage uses cost"

    def test_disabled_states_with_reasons(self):
        """Test disabled card states with detailed reasons"""
        # Create low-level character with no resources
        self._create_test_character("disabled_test", "barbarian", level=1, rage_uses=0)

        # Generate cards
        cards = self.generator.generate_character_action_cards("disabled_test")

        # Find unavailable cards
        unavailable_cards = [card for card in cards if not card.available]
        assert len(unavailable_cards) > 0, "Should have unavailable cards"

        # Check specific failures
        rage_card = next((card for card in cards if card.name == "Rage"), None)
        if rage_card:
            assert not rage_card.available, "Rage should be unavailable with no uses"
            assert "rage" in rage_card.reason_unavailable.lower(), "Should mention rage in reason"

        reckless_card = next((card for card in cards if card.name == "Reckless Attack"), None)
        if reckless_card:
            assert not reckless_card.available, "Reckless Attack should be unavailable at level 1"
            assert "level" in reckless_card.reason_unavailable.lower(), "Should mention level in reason"

    def test_grouped_by_economy_type(self):
        """Test grouping cards by economy type"""
        # Create character
        self._create_test_character("grouped_test", "barbarian", level=20, subclass="berserker")

        # Get cards grouped by economy type
        grouped_cards = self.generator.get_action_cards_by_economy_type("grouped_test")

        # Should have cards in different economy categories
        assert "bonus_action" in grouped_cards, "Should have bonus action cards"
        assert "reaction" in grouped_cards, "Should have reaction cards"

        # Check specific placements
        bonus_action_names = [card.name for card in grouped_cards["bonus_action"]]
        reaction_names = [card.name for card in grouped_cards["reaction"]]

        assert "Rage" in bonus_action_names, "Rage should be in bonus action group"
        assert "Intimidating Presence" in bonus_action_names, "Intimidating Presence should be in bonus action group"
        assert "Retaliation" in reaction_names, "Retaliation should be in reaction group"

    def test_enhanced_description(self):
        """Test enhanced descriptions with cost and availability info"""
        # Create character
        self._create_test_character("desc_test", "barbarian", level=5)

        # Generate cards
        cards = self.generator.generate_character_action_cards("desc_test")

        # Find rage card
        rage_card = next((card for card in cards if card.name == "Rage"), None)
        assert rage_card is not None, "Should have Rage card"

        # Check enhanced description
        enhanced_desc = rage_card.get_enhanced_description()
        assert "Cost:" in enhanced_desc, "Should include cost information"
        assert "Bonus" in enhanced_desc, "Should mention bonus action cost"

    def test_warning_badges(self):
        """Test warning badge system"""
        # Create character with some limitations
        self._create_test_character("warning_test", "barbarian", level=1, rage_uses=1)

        # Create combat state with bonus action used
        combat_state = ActionEconomyState(
            combatant_id="warning_test",
            bonus_action_available=False
        )

        # Generate cards
        cards = self.generator.generate_character_action_cards("warning_test", combat_state)

        # Find cards with warnings
        warning_cards = [card for card in cards if card.warning_badges]
        assert len(warning_cards) > 0, "Should have cards with warnings"

        # Check badge types
        all_badges = []
        for card in warning_cards:
            all_badges.extend(card.warning_badges)

        # Should have various warning types
        badge_text = " ".join(all_badges)
        assert any("Prerequisites" in badge or "Economy" in badge or "Resources" in badge for badge in all_badges), \
            f"Should have warning badges, got: {all_badges}"

    def test_legacy_integration(self):
        """Test integration with legacy ActionCard system"""
        # Create character
        self._create_test_character("legacy_test", "barbarian", level=5)

        # Generate enhanced cards
        enhanced_cards = self.generator.generate_character_action_cards("legacy_test")

        # Convert to legacy format
        for enhanced_card in enhanced_cards[:3]:  # Test first 3 cards
            try:
                legacy_card = self.generator.create_legacy_action_card(enhanced_card)

                # Check legacy card properties
                assert legacy_card.name == enhanced_card.name
                assert legacy_card.available == enhanced_card.available

                # Check enhanced data is preserved
                assert hasattr(legacy_card, 'enhanced_data')
                assert legacy_card.enhanced_data == enhanced_card

            except ImportError:
                # PyQt6 not available in test environment - skip visual test
                print("Skipping legacy integration test (PyQt6 not available)")
                break

    def test_resource_summary(self):
        """Test resource summary generation"""
        # Create character
        self._create_test_character("resource_summary_test", "barbarian", level=5)

        # Get resource summary
        summary = self.generator.get_resource_summary("resource_summary_test")

        # Should have resource information
        assert len(summary) > 0, "Should have resource summary"

        # Check rage uses if present
        if "rage_uses" in summary:
            rage_info = summary["rage_uses"]
            assert "display_name" in rage_info
            assert "current" in rage_info
            assert rage_info["display_name"] == "Rage Uses"


def test_ui_action_cards():
    """Main test function as specified in roadmap"""

    # Test global functions
    from services.action_card_generator import generate_action_cards_for_character, get_action_cards_by_availability

    # Test with mock character (will fail gracefully)
    cards = generate_action_cards_for_character("nonexistent")
    assert isinstance(cards, list), "Should return list even for nonexistent character"

    # Test availability split
    available, unavailable = get_action_cards_by_availability("nonexistent")
    assert isinstance(available, list), "Should return available list"
    assert isinstance(unavailable, list), "Should return unavailable list"

    print("UI action card integration test passed!")


if __name__ == "__main__":
    test_ui_action_cards()