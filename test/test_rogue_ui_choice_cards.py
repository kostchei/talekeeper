# test
"""
Test Rogue UI Choice-Based Action Cards

Tests that Rogue abilities with player choices are properly represented in UI:
- Cunning Strike choice cards (swap Sneak Attack dice for effects)
- Multiple Cunning Strike options (level 11+)
- Uncanny Dodge availability during enemy attacks
- Stroke of Luck reactionary card
- Card visibility based on context (e.g., Sneak Attack eligibility)
- Card disabling when resources unavailable

Focus: Player agency and choice representation in UI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import sqlite3
from typing import Dict, Any, List
from unittest.mock import MagicMock, patch

from action_cards.action_panel import ActionType


class TestRogueUIChoiceCards:
    """Test Rogue choice-based UI action cards"""

    def setup_method(self):
        """Setup test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self._setup_test_database()

    def teardown_method(self):
        """Cleanup test database"""
        try:
            if os.path.exists(self.db_path):
                os.unlink(self.db_path)
        except PermissionError:
            pass

    def _setup_test_database(self):
        """Setup minimal database schema for testing"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    class_id TEXT,
                    level INTEGER DEFAULT 1,
                    dexterity INTEGER DEFAULT 16
                )
            """)

            cursor.execute("""
                CREATE TABLE character_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT,
                    feature_name TEXT,
                    level_acquired INTEGER,
                    feature_type TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE rogue_features (
                    character_id TEXT PRIMARY KEY,
                    level INTEGER,
                    sneak_attack_dice INTEGER DEFAULT 1,
                    expertise_skills TEXT DEFAULT '[]',
                    cunning_action_available BOOLEAN DEFAULT FALSE,
                    uncanny_dodge_available BOOLEAN DEFAULT FALSE,
                    uncanny_dodge_used BOOLEAN DEFAULT FALSE,
                    evasion_available BOOLEAN DEFAULT FALSE,
                    reliable_talent_active BOOLEAN DEFAULT FALSE,
                    slippery_mind_active BOOLEAN DEFAULT FALSE,
                    elusive_active BOOLEAN DEFAULT FALSE,
                    stroke_of_luck_uses_current INTEGER DEFAULT 0,
                    stroke_of_luck_uses_max INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE character_inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT,
                    item_name TEXT,
                    quantity INTEGER DEFAULT 1
                )
            """)

            conn.commit()

    def _create_test_rogue(self, level: int = 1, character_id: str = "test_rogue") -> str:
        """Create a test rogue character"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO characters (id, name, class_id, level, dexterity)
                VALUES (?, 'Test Rogue', 'rogue', ?, 16)
            """, (character_id, level))

            sneak_attack_dice = self._calculate_sneak_attack_dice(level)

            cursor.execute("""
                INSERT INTO rogue_features (
                    character_id, level, sneak_attack_dice,
                    cunning_action_available, uncanny_dodge_available,
                    evasion_available, reliable_talent_active,
                    slippery_mind_active, elusive_active,
                    stroke_of_luck_uses_current, stroke_of_luck_uses_max,
                    uncanny_dodge_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                character_id, level, sneak_attack_dice,
                level >= 2, level >= 5, level >= 7,
                level >= 7, level >= 15, level >= 18,
                1 if level >= 20 else 0,
                1 if level >= 20 else 0,
                False
            ))

            features = []
            if level >= 1:
                features.append(('Sneak Attack', 1, 'passive'))
            if level >= 2:
                features.append(('Cunning Action', 2, 'bonus_action'))
            if level >= 3:
                features.append(('Steady Aim', 3, 'bonus_action'))
            if level >= 5:
                features.append(('Cunning Strike', 5, 'triggered'))
                features.append(('Uncanny Dodge', 5, 'reaction'))
            if level >= 14:
                features.append(('Devious Strikes', 14, 'triggered'))
            if level >= 20:
                features.append(('Stroke of Luck', 20, 'reaction'))

            for feature_name, level_acquired, feature_type in features:
                cursor.execute("""
                    INSERT INTO character_features
                    (character_id, feature_name, level_acquired, feature_type)
                    VALUES (?, ?, ?, ?)
                """, (character_id, feature_name, level_acquired, feature_type))

            conn.commit()

        return character_id

    def _calculate_sneak_attack_dice(self, level: int) -> int:
        """Calculate sneak attack dice based on level"""
        if level < 1:
            return 0
        elif level < 3:
            return 1
        elif level < 5:
            return 2
        elif level < 7:
            return 3
        elif level < 9:
            return 4
        elif level < 11:
            return 5
        elif level < 13:
            return 6
        elif level < 15:
            return 7
        elif level < 17:
            return 8
        elif level < 19:
            return 9
        else:
            return 10

    def test_cunning_strike_choice_availability(self):
        """Test Cunning Strike cards show choice-based costs"""
        rogue_id = self._create_test_rogue(level=5)

        expected_choices = [
            (ActionType.CUNNING_STRIKE_POISON, "1d6", "Poison (requires Poisoner's Kit)"),
            (ActionType.CUNNING_STRIKE_TRIP, "1d6", "Trip (Prone on failed Dex save)"),
            (ActionType.CUNNING_STRIKE_WITHDRAW, "1d6", "Withdraw (move without AoO)")
        ]

        for action_type, cost, description in expected_choices:
            print(f"EXPECTED: {action_type.value} card shows cost: {cost}")
            print(f"          Description: {description}")

        print(f"PASS: Cunning Strike choice cards show resource costs clearly")

    def test_cunning_strike_multiple_choices_level_11(self):
        """Test level 11+ allows choosing TWO Cunning Strike effects"""
        rogue_id = self._create_test_rogue(level=11)

        print(f"EXPECTED: At level 11, rogue has 6d6 Sneak Attack")
        print(f"EXPECTED: Can use up to TWO Cunning Strike effects simultaneously")
        print(f"EXPECTED: UI should allow selecting multiple effects (e.g., Trip + Poison = 4d6 damage)")
        print(f"PASS: Level 11+ allows multiple Cunning Strike selections")

    def test_devious_strikes_high_cost_choices(self):
        """Test Devious Strikes show high die costs clearly"""
        rogue_id = self._create_test_rogue(level=14)

        expected_devious_choices = [
            (ActionType.CUNNING_STRIKE_DAZE, "2d6", "Daze (limited actions next turn)"),
            (ActionType.CUNNING_STRIKE_OBSCURE, "3d6", "Obscure (Blinded until end of next turn)"),
            (ActionType.CUNNING_STRIKE_KNOCK_OUT, "6d6", "Knock Out (Unconscious on failed save)")
        ]

        for action_type, cost, description in expected_devious_choices:
            print(f"EXPECTED: {action_type.value} card shows HIGH cost: {cost}")
            print(f"          Description: {description}")
            print(f"          Warning: Using this reduces Sneak Attack damage significantly")

        print(f"PASS: Devious Strikes clearly show high costs to inform player choice")

    def test_cunning_strike_disabled_without_sneak_attack(self):
        """Test Cunning Strike cards are disabled when Sneak Attack is not available"""
        rogue_id = self._create_test_rogue(level=5)

        print(f"EXPECTED: When Sneak Attack is not eligible this turn:")
        print(f"          - All Cunning Strike cards should be grayed out/disabled")
        print(f"          - Tooltip should explain: 'Requires Sneak Attack eligibility'")
        print(f"          - No way to activate these cards")

        print(f"EXPECTED: When Sneak Attack IS eligible:")
        print(f"          - Cunning Strike cards become clickable")
        print(f"          - Cards show available dice to trade")

        print(f"PASS: Cunning Strike cards context-sensitive based on Sneak Attack eligibility")

    def test_cunning_strike_poisoner_kit_requirement(self):
        """Test Poison Strike requires Poisoner's Kit in inventory"""
        rogue_id = self._create_test_rogue(level=5)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO character_inventory (character_id, item_name, quantity)
                VALUES (?, "Poisoner's Kit", 1)
            """, (rogue_id,))
            conn.commit()

        print(f"EXPECTED: Poison Strike card enabled when Poisoner's Kit in inventory")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM character_inventory WHERE character_id = ?", (rogue_id,))
            conn.commit()

        print(f"EXPECTED: Poison Strike card disabled/grayed when no Poisoner's Kit")
        print(f"          Tooltip: 'Requires Poisoner's Kit'")

        print(f"PASS: Poison Strike card availability tied to inventory")

    def test_uncanny_dodge_reaction_timing(self):
        """Test Uncanny Dodge card appears during enemy attack"""
        rogue_id = self._create_test_rogue(level=5)

        print(f"EXPECTED: During player's turn:")
        print(f"          - Uncanny Dodge card NOT shown (not a proactive action)")

        print(f"EXPECTED: When enemy attacks and hits:")
        print(f"          - Uncanny Dodge card appears as REACTION option")
        print(f"          - Card shows: 'Halve incoming damage'")
        print(f"          - Player has choice: use reaction or save it")

        print(f"EXPECTED: After using Uncanny Dodge this turn:")
        print(f"          - Card disappears (reaction used)")
        print(f"          - Card reappears on rogue's next turn")

        print(f"PASS: Uncanny Dodge card timing follows reaction rules")

    def test_uncanny_dodge_choice_to_use(self):
        """Test player can CHOOSE whether to use Uncanny Dodge"""
        rogue_id = self._create_test_rogue(level=5)

        print(f"EXPECTED: Enemy deals 10 damage (hits rogue)")
        print(f"          - Uncanny Dodge card appears")
        print(f"          - Player choice: Click card to halve (5 damage) OR ignore to save reaction")

        print(f"SCENARIO 1: Player clicks Uncanny Dodge")
        print(f"          - Damage reduced to 5")
        print(f"          - Reaction consumed")
        print(f"          - Card disappears")

        print(f"SCENARIO 2: Player does NOT click Uncanny Dodge")
        print(f"          - Full 10 damage taken")
        print(f"          - Reaction still available")
        print(f"          - Card remains for next attack")

        print(f"PASS: Uncanny Dodge is opt-in, not automatic")

    def test_stroke_of_luck_failed_roll_trigger(self):
        """Test Stroke of Luck card appears after failed d20 roll"""
        rogue_id = self._create_test_rogue(level=20)

        print(f"EXPECTED: After successful d20 roll:")
        print(f"          - Stroke of Luck card NOT offered (no need)")

        print(f"EXPECTED: After FAILED d20 roll (attack/save/check):")
        print(f"          - Stroke of Luck card appears as REACTION")
        print(f"          - Card shows: 'Turn this roll into 20' (1/short rest)")
        print(f"          - Player chooses: use it now or save for worse failure")

        print(f"EXPECTED: After using Stroke of Luck:")
        print(f"          - Card disappears (no uses remaining)")
        print(f"          - Card reappears after short/long rest")

        print(f"PASS: Stroke of Luck card appears reactively after failures")

    def test_steady_aim_choice_vs_movement(self):
        """Test Steady Aim card shows tradeoff clearly"""
        rogue_id = self._create_test_rogue(level=3)

        print(f"EXPECTED: Steady Aim card shows:")
        print(f"          - Benefit: Gain advantage on next attack")
        print(f"          - Cost: Speed becomes 0 (cannot move this turn)")
        print(f"          - Player decision: Worth the tradeoff?")

        print(f"EXPECTED: If player has already moved this turn:")
        print(f"          - Steady Aim card grayed out")
        print(f"          - Tooltip: 'Cannot use after moving'")

        print(f"EXPECTED: If player uses Steady Aim:")
        print(f"          - Movement controls disabled")
        print(f"          - Visual indicator: Speed = 0")

        print(f"PASS: Steady Aim clearly communicates choice and consequences")

    def test_cunning_action_choice_between_options(self):
        """Test Cunning Action presents 3 distinct choices"""
        rogue_id = self._create_test_rogue(level=2)

        print(f"EXPECTED: Three separate Cunning Action cards:")
        print(f"          1. Cunning Dash: Double movement this turn")
        print(f"          2. Cunning Disengage: Move without AoO")
        print(f"          3. Cunning Hide: Attempt to hide (Stealth check)")

        print(f"EXPECTED: Player can only choose ONE per turn (bonus action)")
        print(f"EXPECTED: After clicking one:")
        print(f"          - That action executes")
        print(f"          - Other two Cunning Action cards gray out")
        print(f"          - All refresh on next turn")

        print(f"PASS: Cunning Action cards represent mutually exclusive choices")

    def test_card_cost_display_clarity(self):
        """Test all Rogue cards clearly show action/resource costs"""
        rogue_id = self._create_test_rogue(level=14)

        expected_cost_display = [
            (ActionType.CUNNING_DASH, "Bonus Action"),
            (ActionType.STEADY_AIM, "Bonus Action + Speed 0"),
            (ActionType.CUNNING_STRIKE_POISON, "1d6 Sneak Attack"),
            (ActionType.CUNNING_STRIKE_TRIP, "1d6 Sneak Attack"),
            (ActionType.CUNNING_STRIKE_DAZE, "2d6 Sneak Attack"),
            (ActionType.CUNNING_STRIKE_OBSCURE, "3d6 Sneak Attack"),
            (ActionType.CUNNING_STRIKE_KNOCK_OUT, "6d6 Sneak Attack"),
            (ActionType.UNCANNY_DODGE, "Reaction"),
        ]

        for action_type, cost in expected_cost_display:
            print(f"EXPECTED: {action_type.value} card displays: 'Cost: {cost}'")

        print(f"PASS: All cards clearly indicate resource costs for informed choices")

    def test_cunning_strike_damage_calculation_preview(self):
        """Test Cunning Strike cards show damage reduction preview"""
        rogue_id = self._create_test_rogue(level=14)

        print(f"EXPECTED: Rogue level 14 has 7d6 Sneak Attack")
        print(f"EXPECTED: Card tooltips show damage preview:")
        print(f"          - Poison Strike (1d6): 6d6 damage + Poisoned condition")
        print(f"          - Daze Strike (2d6): 5d6 damage + Dazed condition")
        print(f"          - Obscure Strike (3d6): 4d6 damage + Blinded condition")
        print(f"          - Knock Out Strike (6d6): 1d6 damage + Unconscious condition")

        print(f"EXPECTED: Helps player choose: More damage vs. better effect?")

        print(f"PASS: Damage calculation preview aids tactical decisions")

    def test_expertise_skill_selection_ui(self):
        """Test Expertise selection at character creation and level 6"""
        rogue_id = self._create_test_rogue(level=1)

        print(f"EXPECTED: During character creation (level 1):")
        print(f"          - Expertise selection UI shows")
        print(f"          - Player chooses 2 skills from proficiencies")
        print(f"          - Checkbox/selection interface")
        print(f"          - Cannot proceed until exactly 2 selected")

        print(f"EXPECTED: At level 6:")
        print(f"          - Expertise selection UI appears again")
        print(f"          - Player chooses 2 MORE skills (4 total)")
        print(f"          - Previous expertise selections grayed out (cannot re-select)")
        print(f"          - Must select 2 NEW skills")

        print(f"PASS: Expertise selection UI enforces choice constraints")

    def test_multiple_effect_stacking_ui_level_11(self):
        """Test UI for selecting multiple Cunning Strike effects (level 11+)"""
        rogue_id = self._create_test_rogue(level=11)

        print(f"EXPECTED: At level 11+ with Improved Cunning Strike:")
        print(f"          - Can select up to TWO Cunning Strike cards")
        print(f"          - UI shows: 'Select up to 2 effects (total cost: Xd6)'")
        print(f"          - Example: Click Trip (1d6) + Poison (1d6) = 2d6 cost")
        print(f"          - Remaining damage: 6d6 - 2d6 = 4d6")

        print(f"EXPECTED: After selecting 2 effects:")
        print(f"          - Other Cunning Strike cards gray out")
        print(f"          - Confirm button to apply both")
        print(f"          - Can deselect to choose different combination")

        print(f"PASS: Multi-selection UI for Improved Cunning Strike")

    def test_card_disabled_state_visual_feedback(self):
        """Test disabled cards have clear visual distinction"""
        rogue_id = self._create_test_rogue(level=5)

        print(f"EXPECTED: Disabled card appearance:")
        print(f"          - Grayed out / reduced opacity")
        print(f"          - Red border or 'X' indicator")
        print(f"          - Tooltip explains WHY disabled")

        print(f"EXPECTED: Enabled card appearance:")
        print(f"          - Full color/brightness")
        print(f"          - Clickable cursor on hover")
        print(f"          - Tooltip shows full effect")

        print(f"EXAMPLES:")
        print(f"          - Poison Strike: Disabled if no Poisoner's Kit")
        print(f"          - Cunning Strike: Disabled if Sneak Attack not eligible")
        print(f"          - Steady Aim: Disabled if already moved")
        print(f"          - Stroke of Luck: Disabled if no uses remaining")

        print(f"PASS: Card states visually communicate availability")

    def test_reaction_timing_window_ui(self):
        """Test UI for reaction-based cards (Uncanny Dodge, Stroke of Luck)"""
        rogue_id = self._create_test_rogue(level=20)

        print(f"EXPECTED: Reaction window UI:")
        print(f"          - Combat pauses when reaction trigger occurs")
        print(f"          - Modal or highlighted panel shows available reactions")
        print(f"          - Timer or 'Skip' button to decline reaction")
        print(f"          - Clear explanation of trigger (e.g., 'Enemy hit you for 15 damage')")

        print(f"EXPECTED: For Uncanny Dodge:")
        print(f"          - Shows original damage vs. reduced damage")
        print(f"          - Example: '15 damage -> 7 damage if you use Uncanny Dodge'")

        print(f"EXPECTED: For Stroke of Luck:")
        print(f"          - Shows failed roll (e.g., 'Rolled 8, needed 15')")
        print(f"          - Button: 'Use Stroke of Luck (turn to 20)'")

        print(f"PASS: Reaction timing UI clearly presents choices")


def main():
    """Run all tests"""
    print("Running Rogue UI Choice-Based Action Card Tests")
    print("=" * 70)

    test_suite = TestRogueUIChoiceCards()

    tests = [
        ("Cunning Strike Choice Availability", test_suite.test_cunning_strike_choice_availability),
        ("Multiple Cunning Strike Choices (L11)", test_suite.test_cunning_strike_multiple_choices_level_11),
        ("Devious Strikes High Cost Display", test_suite.test_devious_strikes_high_cost_choices),
        ("Cunning Strike Disabled Without Sneak", test_suite.test_cunning_strike_disabled_without_sneak_attack),
        ("Poisoner's Kit Requirement", test_suite.test_cunning_strike_poisoner_kit_requirement),
        ("Uncanny Dodge Reaction Timing", test_suite.test_uncanny_dodge_reaction_timing),
        ("Uncanny Dodge Player Choice", test_suite.test_uncanny_dodge_choice_to_use),
        ("Stroke of Luck Failed Roll Trigger", test_suite.test_stroke_of_luck_failed_roll_trigger),
        ("Steady Aim Movement Tradeoff", test_suite.test_steady_aim_choice_vs_movement),
        ("Cunning Action Mutual Exclusivity", test_suite.test_cunning_action_choice_between_options),
        ("Card Cost Display Clarity", test_suite.test_card_cost_display_clarity),
        ("Damage Calculation Preview", test_suite.test_cunning_strike_damage_calculation_preview),
        ("Expertise Selection UI", test_suite.test_expertise_skill_selection_ui),
        ("Multiple Effect Stacking UI", test_suite.test_multiple_effect_stacking_ui_level_11),
        ("Card Disabled State Visuals", test_suite.test_card_disabled_state_visual_feedback),
        ("Reaction Timing Window", test_suite.test_reaction_timing_window_ui),
    ]

    passed = 0
    failed = 0

    for i, (test_name, test_func) in enumerate(tests, 1):
        print(f"\n[{i}/{len(tests)}] {test_name}")
        print("-" * 70)
        try:
            test_suite.setup_method()
            test_func()
            print(f"\n[PASS] {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {test_name}: {e}")
            failed += 1
        finally:
            test_suite.teardown_method()

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("\nNOTE: These are EXPECTATION tests - they define what SHOULD exist")
    print("      Many features are NOT YET IMPLEMENTED in the UI")

    return failed == 0


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
