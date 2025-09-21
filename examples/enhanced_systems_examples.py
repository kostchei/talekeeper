"""
Enhanced Systems Example Code for TaleKeeper

Demonstrates how to use the condition system, subclass architecture,
action economy, configuration, and debug utilities.

Part of Stage 4.3: Add example usage code.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.condition_manager import ConditionManager, ConditionType, ActiveCondition
from services.enhanced_subclass_manager import EnhancedSubclassManager
from models.action_economy import CombatActionEconomy, ActionEconomyType
from core.config import get_config, is_feature_enabled
from core.debug_commands import execute_debug_command


def example_condition_system():
    """Example: Using the condition system"""
    print("=== Condition System Example ===")

    # Initialize condition manager
    manager = ConditionManager("talekeeper.db")
    character_id = "example_barbarian"

    # 1. Apply a basic condition
    print("1. Applying poisoned condition...")
    poisoned = ActiveCondition(
        condition_type=ConditionType.POISONED,
        source="Poison dart trap",
        duration_type="permanent"
    )
    success = manager.add_condition(character_id, poisoned)
    print(f"   Applied: {success}")

    # 2. Apply a save-ends condition
    print("2. Applying stunned condition with save...")
    stunned = ActiveCondition(
        condition_type=ConditionType.STUNNED,
        source="Hold Person spell",
        duration_type="save_ends",
        save_dc=15,
        save_ability="wisdom"
    )
    manager.add_condition(character_id, stunned)

    # 3. Check for incapacitating conditions
    print("3. Checking for incapacitating conditions...")
    has_incap = manager.has_incapacitating_condition(character_id)
    print(f"   Has incapacitating condition: {has_incap}")

    # 4. Get all active conditions
    print("4. Active conditions:")
    conditions = manager.get_active_conditions(character_id)
    for condition in conditions:
        print(f"   - {condition.condition_type.value}: {condition.source}")

    # 5. Check specific effects
    print("5. Checking condition effects...")
    effects = manager.get_condition_effects(character_id)
    if effects.advantage_on:
        print(f"   Advantage on: {effects.advantage_on}")
    if effects.disadvantage_on:
        print(f"   Disadvantage on: {effects.disadvantage_on}")

    # 6. Clear all conditions
    print("6. Clearing all conditions...")
    manager.clear_all_conditions(character_id)

    print("Condition system example complete!\n")


def example_subclass_system():
    """Example: Using the subclass system"""
    print("=== Subclass System Example ===")

    # Initialize subclass manager
    manager = EnhancedSubclassManager("talekeeper.db")
    character_id = "example_berserker"

    # 1. Get character's subclass features
    print("1. Getting Berserker features...")
    features = manager.get_character_subclass_features(character_id, "barbarian")
    print(f"   Found {len(features)} features")

    for feature in features[:3]:  # Show first 3
        print(f"   - {feature.name} (Level {feature.level}): {feature.feature_type.value}")

    # 2. Check feature availability
    print("2. Checking feature availability...")
    available = manager.is_feature_available(character_id, "intimidating_presence")
    print(f"   Intimidating Presence available: {available}")

    # 3. Use a feature (if available)
    print("3. Using Intimidating Presence...")
    try:
        result = manager.use_subclass_feature(character_id, "intimidating_presence", {"target": "enemy"})
        if result.get("success"):
            print(f"   Success! DC: {result.get('dc', 'N/A')}")
        else:
            print(f"   Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   Error: {e}")

    # 4. Get features by type
    print("4. Features by type:")
    for feature_type in ["passive", "activated", "reaction"]:
        type_features = [f for f in features if f.feature_type.value == feature_type]
        print(f"   {feature_type.title()}: {len(type_features)} features")

    print("Subclass system example complete!\n")


def example_action_economy():
    """Example: Using the action economy system"""
    print("=== Action Economy Example ===")

    # 1. Create combat session
    combat = CombatActionEconomy(combat_session_id="example_combat")
    character_id = "example_fighter"

    # 2. Add combatants
    print("1. Setting up combat...")
    combat.add_combatant(character_id, "Example Fighter", "character")
    combat.add_combatant("monster_1", "Orc", "monster")
    combat.start_combat([character_id, "monster_1"])

    # 3. Check initial state
    print("2. Initial action economy state:")
    state = combat.get_combatant_state(character_id)
    print(f"   Action: {state.action_available}")
    print(f"   Bonus Action: {state.bonus_action_available}")
    print(f"   Reaction: {state.reaction_available}")
    print(f"   Movement: {state.movement_remaining}")

    # 4. Use actions
    print("3. Using actions...")

    # Use main action
    action_used = combat.use_action(character_id, ActionEconomyType.ACTION, "Attack")
    print(f"   Used main action: {action_used}")

    # Try to use another main action (should fail)
    second_action = combat.use_action(character_id, ActionEconomyType.ACTION, "Second Attack")
    print(f"   Tried second main action: {second_action}")

    # Use bonus action
    bonus_used = combat.use_action(character_id, ActionEconomyType.BONUS_ACTION, "Second Wind")
    print(f"   Used bonus action: {bonus_used}")

    # 5. Check state after actions
    print("4. State after using actions:")
    state = combat.get_combatant_state(character_id)
    print(f"   Action: {state.action_available}")
    print(f"   Bonus Action: {state.bonus_action_available}")
    print(f"   Reaction: {state.reaction_available}")

    # 6. Advance turn (resets economy)
    print("5. Advancing to next turn...")
    combat.next_turn()
    combat.next_turn()  # Back to character

    state = combat.get_combatant_state(character_id)
    print(f"   Actions reset - Action: {state.action_available}")

    print("Action economy example complete!\n")


def example_configuration():
    """Example: Using the configuration system"""
    print("=== Configuration System Example ===")

    # 1. Get configuration
    config = get_config()

    # 2. Check current settings
    print("1. Current configuration:")
    print(f"   Action card caching: {config.performance.enable_action_card_caching}")
    print(f"   Debug commands: {config.debug.enable_test_commands}")
    print(f"   Enhanced subclass manager: {config.features.use_enhanced_subclass_manager}")
    print(f"   UI theme: {config.ui.theme}")

    # 3. Use feature checks
    print("2. Feature availability:")
    print(f"   Enhanced monster logging: {is_feature_enabled('enable_enhanced_monster_logging')}")
    print(f"   Condition caching: {config.performance.condition_cache_size > 0}")

    # 4. Modify settings
    print("3. Modifying debug settings...")
    original_queries = config.debug.log_database_queries
    config.set_debug_setting("log_database_queries", True)
    print(f"   Query logging: {original_queries} -> {config.debug.log_database_queries}")

    # 5. Use preset modes
    print("4. Testing developer mode...")
    original_metrics = config.debug.show_performance_metrics
    config.enable_developer_mode()
    print(f"   Performance metrics: {original_metrics} -> {config.debug.show_performance_metrics}")

    # 6. Reset to defaults
    print("5. Resetting to defaults...")
    config.reset_to_defaults()
    print(f"   Performance metrics reset: {config.debug.show_performance_metrics}")

    print("Configuration system example complete!\n")


def example_debug_commands():
    """Example: Using debug commands"""
    print("=== Debug Commands Example ===")

    # 1. Enable debug commands
    config = get_config()
    config.set_debug_setting("enable_test_commands", True)

    # 2. Execute various debug commands
    print("1. System status:")
    result = execute_debug_command("status")
    print("   " + result.replace("\n", "\n   "))

    print("\n2. Available commands:")
    result = execute_debug_command("list")
    print("   " + result)

    print("\n3. Configuration info:")
    result = execute_debug_command("config")
    print("   " + result.replace("\n", "\n   "))

    print("\n4. Testing condition application:")
    result = execute_debug_command("test_conditions example_char POISONED")
    print("   " + result)

    print("\n5. Performance metrics:")
    result = execute_debug_command("performance")
    print("   " + result.replace("\n", "\n   "))

    print("\n6. Help information:")
    result = execute_debug_command("help")
    print("   " + result.replace("\n", "\n   ")[:200] + "...")  # Truncated

    print("\nDebug commands example complete!\n")


def example_integration():
    """Example: Integration between all systems"""
    print("=== System Integration Example ===")

    character_id = "integration_test"

    # 1. Setup all systems
    condition_manager = ConditionManager("talekeeper.db")
    subclass_manager = EnhancedSubclassManager("talekeeper.db")
    combat = CombatActionEconomy(combat_session_id="integration_test")

    combat.add_combatant(character_id, "Integration Test", "character")
    combat.start_combat([character_id])

    print("1. Initial state - all systems ready")

    # 2. Apply condition that affects actions
    print("2. Applying paralyzed condition...")
    paralyzed = ActiveCondition(
        condition_type=ConditionType.PARALYZED,
        source="Hold Person spell",
        duration_type="save_ends",
        save_dc=15
    )
    condition_manager.add_condition(character_id, paralyzed)

    # 3. Check how condition affects action economy
    print("3. Checking action restrictions...")
    has_incap = condition_manager.has_incapacitating_condition(character_id)
    print(f"   Has incapacitating condition: {has_incap}")

    # 4. Try to use actions (should be blocked by condition)
    print("4. Attempting to use actions while paralyzed...")
    action_result = combat.use_action(character_id, ActionEconomyType.ACTION, "Attack")
    print(f"   Attack action: {action_result}")

    # 5. Clear condition and try again
    print("5. Clearing condition and retrying...")
    condition_manager.clear_all_conditions(character_id)
    action_result = combat.use_action(character_id, ActionEconomyType.ACTION, "Attack")
    print(f"   Attack action after clearing: {action_result}")

    # 6. Use subclass feature
    print("6. Using subclass feature...")
    try:
        rage_result = subclass_manager.use_subclass_feature(character_id, "frenzy")
        print(f"   Frenzy result: {rage_result.get('success', False)}")
    except Exception as e:
        print(f"   Frenzy error: {e}")

    print("System integration example complete!\n")


def main():
    """Run all examples"""
    print("TaleKeeper Enhanced Systems Examples")
    print("=" * 50)

    try:
        example_condition_system()
        example_subclass_system()
        example_action_economy()
        example_configuration()
        example_debug_commands()
        example_integration()

        print("All examples completed successfully!")

    except Exception as e:
        print(f"Example execution error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()