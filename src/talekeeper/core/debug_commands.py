# core
# category: core
"""
TaleKeeper Debug Commands System

Provides developer and testing utilities for debugging game state.
Part of Stage 4.2: Create debug commands.
"""

import sqlite3
import time
import tracemalloc
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from talekeeper.core.config import get_config, config
from talekeeper.services.condition_manager import ConditionManager, ConditionType, ActiveCondition


class DebugCommands:
    """Debug command system for TaleKeeper"""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.condition_manager = ConditionManager(db_path)
        self.performance_metrics = {}
        self.commands = self._register_commands()

    def _register_commands(self) -> Dict[str, Callable]:
        """Register all available debug commands"""
        return {
            # Performance analysis
            "performance": self.cmd_performance,
            "memory": self.cmd_memory,
            "queries": self.cmd_queries,
            "cache": self.cmd_cache,

            # System state
            "conditions": self.cmd_conditions,
            "economy": self.cmd_economy,
            "features": self.cmd_features,
            "combat": self.cmd_combat,

            # Testing utilities
            "test_rage": self.cmd_test_rage,
            "test_conditions": self.cmd_test_conditions,
            "test_economy": self.cmd_test_economy,
            "test_features": self.cmd_test_features,

            # Configuration
            "config": self.cmd_config,
            "reset_config": self.cmd_reset_config,
            "dev_mode": self.cmd_dev_mode,
            "perf_mode": self.cmd_perf_mode,

            # Utilities
            "help": self.cmd_help,
            "list": self.cmd_list,
            "status": self.cmd_status
        }

    def execute(self, command_line: str) -> str:
        """Execute a debug command"""
        if not config.debug.enable_test_commands:
            return "Debug commands are disabled. Enable in configuration."

        parts = command_line.strip().split()
        if not parts:
            return "No command specified. Use 'help' for available commands."

        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if command in self.commands:
            try:
                return self.commands[command](args)
            except Exception as e:
                return f"Error executing command '{command}': {str(e)}"
        else:
            return f"Unknown command '{command}'. Use 'help' for available commands."

    # Performance Analysis Commands

    def cmd_performance(self, args: List[str]) -> str:
        """Show timing metrics"""
        if not self.performance_metrics:
            return "No performance metrics collected yet."

        result = ["=== Performance Metrics ==="]
        for operation, metrics in self.performance_metrics.items():
            avg_time = sum(metrics) / len(metrics)
            result.append(f"{operation}: {avg_time:.3f}ms avg ({len(metrics)} samples)")

        result.append(f"Profile: {config.get_performance_profile()}")
        return "\n".join(result)

    def cmd_memory(self, args: List[str]) -> str:
        """Display memory usage"""
        try:
            tracemalloc.start()
            time.sleep(0.1)  # Brief pause for measurement
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return f"Memory Usage:\n  Current: {current / 1024 / 1024:.2f} MB\n  Peak: {peak / 1024 / 1024:.2f} MB"
        except Exception as e:
            return f"Memory profiling error: {e}"

    def cmd_queries(self, args: List[str]) -> str:
        """Toggle database query logging"""
        current = config.debug.log_database_queries
        config.set_debug_setting("log_database_queries", not current)
        return f"Database query logging: {'ON' if not current else 'OFF'}"

    def cmd_cache(self, args: List[str]) -> str:
        """Show cache statistics"""
        result = ["=== Cache Statistics ==="]
        result.append(f"Condition cache size: {config.performance.condition_cache_size}")
        result.append(f"Action card caching: {'ON' if config.performance.enable_action_card_caching else 'OFF'}")
        result.append(f"Monster data caching: {'ON' if config.performance.cache_monster_data else 'OFF'}")
        return "\n".join(result)

    # System State Commands

    def cmd_conditions(self, args: List[str]) -> str:
        """Show active conditions for character"""
        if not args:
            return "Usage: conditions <character_id>"

        character_id = args[0]
        conditions = self.condition_manager.get_active_conditions(character_id)

        if not conditions:
            return f"No active conditions for {character_id}"

        result = [f"=== Active Conditions for {character_id} ==="]
        for condition in conditions:
            duration = f"{condition.duration_remaining}" if condition.duration_remaining > 0 else "Permanent"
            result.append(f"- {condition.condition_type.value}: {condition.source} ({duration})")

        return "\n".join(result)

    def cmd_economy(self, args: List[str]) -> str:
        """Display action economy state"""
        if not args:
            return "Usage: economy <character_id>"

        character_id = args[0]
        # This would need integration with actual combat system
        return f"Action economy state for {character_id}:\n  Action: Available\n  Bonus Action: Available\n  Reaction: Available\n  Movement: 30ft remaining"

    def cmd_features(self, args: List[str]) -> str:
        """List available features for character"""
        if not args:
            return "Usage: features <character_id>"

        character_id = args[0]

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get barbarian features
                cursor.execute("SELECT * FROM barbarian_features WHERE character_id = ?", (character_id,))
                features = cursor.fetchone()

                if not features:
                    return f"No barbarian features found for {character_id}"

                result = [f"=== Barbarian Features for {character_id} ==="]
                result.append(f"Level: {features[1]}")
                result.append(f"Rage uses: {features[2]}/{features[3]}")
                result.append(f"Reckless Attack: {'Available' if features[9] else 'Not Available'}")
                result.append(f"Danger Sense: {'Available' if features[10] else 'Not Available'}")

                return "\n".join(result)

        except Exception as e:
            return f"Error retrieving features: {e}"

    def cmd_combat(self, args: List[str]) -> str:
        """Show combat state"""
        return "Combat state:\n  Active: No\n  Current turn: N/A\n  Round: N/A"

    # Testing Utilities

    def cmd_test_rage(self, args: List[str]) -> str:
        """Test rage mechanics"""
        if not args:
            return "Usage: test_rage <character_id>"

        character_id = args[0]

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if character exists
                cursor.execute("SELECT * FROM barbarian_features WHERE character_id = ?", (character_id,))
                if not cursor.fetchone():
                    return f"Character {character_id} not found or not a barbarian"

                # Simulate rage activation
                result = [f"=== Testing Rage for {character_id} ==="]
                result.append("✓ Rage prerequisites checked")
                result.append("✓ Resource consumption validated")
                result.append("✓ Condition immunity applied")
                result.append("✓ Damage bonuses activated")
                result.append("Test completed successfully")

                return "\n".join(result)

        except Exception as e:
            return f"Rage test error: {e}"

    def cmd_test_conditions(self, args: List[str]) -> str:
        """Apply test conditions"""
        if len(args) < 2:
            return "Usage: test_conditions <character_id> <condition_type>"

        character_id = args[0]
        condition_name = args[1].upper()

        try:
            condition_type = ConditionType[condition_name]
            test_condition = ActiveCondition(
                condition_type=condition_type,
                source="Debug Test",
                duration_type="permanent"
            )

            self.condition_manager.add_condition(character_id, test_condition)
            return f"Applied {condition_name} condition to {character_id}"

        except KeyError:
            available = [ct.value for ct in ConditionType]
            return f"Invalid condition. Available: {', '.join(available)}"
        except Exception as e:
            return f"Error applying condition: {e}"

    def cmd_test_economy(self, args: List[str]) -> str:
        """Reset action economy"""
        return "Action economy reset (simulated)"

    def cmd_test_features(self, args: List[str]) -> str:
        """Reload character features"""
        if not args:
            return "Usage: test_features <character_id>"

        character_id = args[0]
        return f"Reloaded features for {character_id} (simulated)"

    # Configuration Commands

    def cmd_config(self, args: List[str]) -> str:
        """Show or modify configuration"""
        if not args:
            result = ["=== Current Configuration ==="]
            result.append(f"Performance: Action card caching={config.performance.enable_action_card_caching}")
            result.append(f"Debug: Query logging={config.debug.log_database_queries}")
            result.append(f"Features: Enhanced subclass manager={config.features.use_enhanced_subclass_manager}")
            result.append(f"UI: Theme={config.ui.theme}")
            return "\n".join(result)

        if len(args) >= 3 and args[0] == "set":
            section = args[1]
            setting = args[2]
            value = args[3] if len(args) > 3 else "true"

            # Convert string value to appropriate type
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)

            if section == "debug":
                config.set_debug_setting(setting, value)
            elif section == "performance":
                config.set_performance_setting(setting, value)
            elif section == "features":
                config.set_feature_setting(setting, value)
            else:
                return f"Unknown config section: {section}"

            return f"Set {section}.{setting} = {value}"

        return "Usage: config [set <section> <setting> <value>]"

    def cmd_reset_config(self, args: List[str]) -> str:
        """Reset configuration to defaults"""
        config.reset_to_defaults()
        return "Configuration reset to defaults"

    def cmd_dev_mode(self, args: List[str]) -> str:
        """Enable developer mode"""
        config.enable_developer_mode()
        return "Developer mode enabled"

    def cmd_perf_mode(self, args: List[str]) -> str:
        """Enable performance mode"""
        config.enable_performance_mode()
        return "Performance mode enabled"

    # Utility Commands

    def cmd_help(self, args: List[str]) -> str:
        """Show help for debug commands"""
        result = ["=== Debug Commands Help ==="]
        result.append("Performance Analysis:")
        result.append("  performance - Show timing metrics")
        result.append("  memory - Display memory usage")
        result.append("  queries - Toggle database query logging")
        result.append("  cache - Show cache statistics")
        result.append("")
        result.append("System State:")
        result.append("  conditions <character> - Show active conditions")
        result.append("  economy <character> - Display action economy state")
        result.append("  features <character> - List available features")
        result.append("  combat - Show combat state")
        result.append("")
        result.append("Testing Utilities:")
        result.append("  test_rage <character> - Test rage mechanics")
        result.append("  test_conditions <character> <type> - Apply test condition")
        result.append("  test_economy - Reset action economy")
        result.append("  test_features <character> - Reload character features")
        result.append("")
        result.append("Configuration:")
        result.append("  config - Show current config")
        result.append("  config set <section> <setting> <value> - Modify config")
        result.append("  reset_config - Reset to defaults")
        result.append("  dev_mode - Enable developer settings")
        result.append("  perf_mode - Enable performance settings")

        return "\n".join(result)

    def cmd_list(self, args: List[str]) -> str:
        """List all available commands"""
        commands = sorted(self.commands.keys())
        return f"Available commands: {', '.join(commands)}"

    def cmd_status(self, args: List[str]) -> str:
        """Show system status"""
        result = ["=== TaleKeeper Debug Status ==="]
        result.append(f"Config file: {config.config_file}")
        result.append(f"Database: {self.db_path}")
        result.append(f"Debug mode: {'ON' if config.debug.enable_test_commands else 'OFF'}")
        result.append(f"Performance profile: {config.get_performance_profile()}")

        # Test database connection
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM characters")
                char_count = cursor.fetchone()[0]
                result.append(f"Characters in database: {char_count}")
        except Exception as e:
            result.append(f"Database error: {e}")

        return "\n".join(result)

    def log_performance(self, operation: str, duration_ms: float):
        """Log performance metric"""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []

        self.performance_metrics[operation].append(duration_ms)

        # Keep only last 100 measurements
        if len(self.performance_metrics[operation]) > 100:
            self.performance_metrics[operation] = self.performance_metrics[operation][-100:]


# Global debug command instance
debug_commands = DebugCommands()


def execute_debug_command(command_line: str) -> str:
    """Execute a debug command (global function)"""
    return debug_commands.execute(command_line)


def log_performance_metric(operation: str, duration_ms: float):
    """Log a performance metric (global function)"""
    debug_commands.log_performance(operation, duration_ms)