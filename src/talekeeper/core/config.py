# core
# category: core
"""
TaleKeeper Configuration System

Centralized configuration for performance, debug, and feature settings.
Part of Stage 4.2: Polish and Optimization.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from talekeeper.paths import get_config_path


@dataclass
class PerformanceConfig:
    """Performance-related settings"""
    enable_action_card_caching: bool = True
    condition_cache_size: int = 100
    database_connection_pool_size: int = 5
    ui_update_throttle_ms: int = 16  # 60fps max
    lazy_load_subclass_features: bool = True
    cache_monster_data: bool = True
    parallel_combat_processing: bool = False


@dataclass
class DebugConfig:
    """Debug and development settings"""
    log_database_queries: bool = False
    show_performance_metrics: bool = False
    trace_condition_applications: bool = False
    validate_action_economy: bool = True
    enable_test_commands: bool = True
    verbose_combat_logging: bool = False
    log_file_path: Optional[str] = None


@dataclass
class FeatureConfig:
    """Feature toggle settings"""
    use_enhanced_subclass_manager: bool = True
    enable_condition_immunity_optimization: bool = True
    use_cached_monster_data: bool = True
    enable_enhanced_monster_logging: bool = True
    use_action_economy_enforcer: bool = True
    enable_scalable_subclass_architecture: bool = True

    # Release subclass filtering - only show these subclasses for initial release
    release_subclass_filter: bool = True
    release_subclasses: dict = None

    def __post_init__(self):
        """Initialize default release subclasses if not set"""
        if self.release_subclasses is None:
            self.release_subclasses = {
                "cleric": ["life", "war"],
                "fighter": ["champion", "gladiator"],
                "wizard": ["evocation", "abjuration"],
                "barbarian": ["berserker"],
                "paladin": ["oath_of_devotion", "oath_of_glory", "oath_of_the_unbroken"],
                "warlock": []
            }


@dataclass
class UIConfig:
    """UI-related settings"""
    theme: str = "dark"  # "light" or "dark"
    enable_animations: bool = True
    show_advanced_tooltips: bool = True
    auto_refresh_character_sheet: bool = True
    combat_log_max_entries: int = 1000
    action_card_auto_sort: bool = True


@dataclass
class NarrativeConfig:
    """Narrative generation settings"""
    enable_audio_narration: bool = False
    enable_combat_narratives: bool = True
    enable_round_summaries: bool = True
    enable_victory_narratives: bool = True
    show_only_narratives: bool = False
    narrative_display_delay: float = 0.5
    max_narrative_cache: int = 50
    fallback_to_mechanical: bool = True


@dataclass
class AudioConfig:
    """Audio settings"""
    enable_master_audio: bool = True
    enable_music: bool = True
    enable_narration: bool = True
    master_volume: float = 1.0
    music_volume: float = 0.4
    narration_volume: float = 0.7


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_file: str = "talekeeper_config.json"):
        self.config_file = get_config_path(config_file) if not os.path.isabs(config_file) else config_file
        self.performance = PerformanceConfig()
        self.debug = DebugConfig()
        self.features = FeatureConfig()
        self.ui = UIConfig()
        self.narrative = NarrativeConfig()
        self.audio = AudioConfig()

        # Load from file if it exists
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)

                # Update configs with loaded data
                if 'performance' in config_data:
                    self.performance = PerformanceConfig(**config_data['performance'])
                if 'debug' in config_data:
                    self.debug = DebugConfig(**config_data['debug'])
                if 'features' in config_data:
                    self.features = FeatureConfig(**config_data['features'])
                if 'ui' in config_data:
                    self.ui = UIConfig(**config_data['ui'])
                if 'narrative' in config_data:
                    self.narrative = NarrativeConfig(**config_data['narrative'])
                if 'audio' in config_data:
                    self.audio = AudioConfig(**config_data['audio'])
                
                # Migration: Sync legacy narrative audio setting to new audio config if not present
                if 'audio' not in config_data and 'narrative' in config_data:
                    if 'enable_audio_narration' in config_data['narrative']:
                        self.audio.enable_narration = config_data['narrative']['enable_audio_narration']

                print(f"[CONFIG] Loaded configuration from {self.config_file}")
            except Exception as e:
                print(f"[CONFIG] Error loading config: {e}, using defaults")

    def save_config(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'performance': asdict(self.performance),
                'debug': asdict(self.debug),
                'features': asdict(self.features),
                'ui': asdict(self.ui),
                'narrative': asdict(self.narrative),
                'audio': asdict(self.audio)
            }

            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)

            print(f"[CONFIG] Saved configuration to {self.config_file}")
        except Exception as e:
            print(f"[CONFIG] Error saving config: {e}")

    def get_debug_setting(self, setting: str) -> Any:
        """Get a debug setting value"""
        return getattr(self.debug, setting, None)

    def set_debug_setting(self, setting: str, value: Any):
        """Set a debug setting value"""
        if hasattr(self.debug, setting):
            setattr(self.debug, setting, value)
            self.save_config()

    def get_performance_setting(self, setting: str) -> Any:
        """Get a performance setting value"""
        return getattr(self.performance, setting, None)

    def set_performance_setting(self, setting: str, value: Any):
        """Set a performance setting value"""
        if hasattr(self.performance, setting):
            setattr(self.performance, setting, value)
            self.save_config()

    def get_feature_setting(self, setting: str) -> Any:
        """Get a feature setting value"""
        return getattr(self.features, setting, None)

    def set_feature_setting(self, setting: str, value: Any):
        """Set a feature setting value"""
        if hasattr(self.features, setting):
            setattr(self.features, setting, value)
            self.save_config()

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.get_feature_setting(feature) is True

    def is_debug_enabled(self, debug_option: str) -> bool:
        """Check if a debug option is enabled"""
        return self.get_debug_setting(debug_option) is True

    def get_performance_profile(self) -> str:
        """Get current performance profile description"""
        profile_parts = []

        if self.performance.enable_action_card_caching:
            profile_parts.append("Caching")
        if self.performance.lazy_load_subclass_features:
            profile_parts.append("Lazy Loading")
        if self.performance.parallel_combat_processing:
            profile_parts.append("Parallel Processing")

        return "Performance: " + (", ".join(profile_parts) if profile_parts else "Standard")

    def reset_to_defaults(self):
        """Reset all configuration to defaults"""
        self.performance = PerformanceConfig()
        self.debug = DebugConfig()
        self.features = FeatureConfig()
        self.ui = UIConfig()
        self.narrative = NarrativeConfig()
        self.audio = AudioConfig()
        self.save_config()

    def enable_developer_mode(self):
        """Enable developer-friendly settings"""
        self.debug.log_database_queries = True
        self.debug.show_performance_metrics = True
        self.debug.trace_condition_applications = True
        self.debug.enable_test_commands = True
        self.debug.verbose_combat_logging = True
        self.save_config()

    def enable_performance_mode(self):
        """Enable performance-optimized settings"""
        self.performance.enable_action_card_caching = True
        self.performance.lazy_load_subclass_features = True
        self.performance.cache_monster_data = True
        self.performance.ui_update_throttle_ms = 16
        self.ui.enable_animations = False
        self.ui.combat_log_max_entries = 500
        self.save_config()


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config


def is_feature_enabled(feature: str) -> bool:
    """Quick check if a feature is enabled"""
    return config.is_feature_enabled(feature)


def is_debug_enabled(debug_option: str) -> bool:
    """Quick check if a debug option is enabled"""
    return config.is_debug_enabled(debug_option)


# Convenience functions for common checks
def use_enhanced_subclass_manager() -> bool:
    """Check if enhanced subclass manager should be used"""
    return is_feature_enabled("use_enhanced_subclass_manager")


def enable_condition_caching() -> bool:
    """Check if condition caching is enabled"""
    return config.performance.condition_cache_size > 0


def enable_action_card_caching() -> bool:
    """Check if action card caching is enabled"""
    return config.performance.enable_action_card_caching


def should_log_database_queries() -> bool:
    """Check if database queries should be logged"""
    return is_debug_enabled("log_database_queries")


def get_ui_update_throttle() -> int:
    """Get UI update throttle in milliseconds"""
    return config.performance.ui_update_throttle_ms