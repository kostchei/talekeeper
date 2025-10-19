# core
# core
import sqlite3
from typing import Dict, Any, List
from .dynamic_feature_manager import DynamicFeatureManager

class LevelUpIntegration:
    """Integration layer between existing level-up system and new dynamic feature system"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.feature_manager = DynamicFeatureManager(db_path)

    def handle_level_up(self, character_id: str, new_level: int) -> Dict[str, Any]:
        """Handle level up using dynamic feature system"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get character class and subclass
            cursor.execute("""
                SELECT class_id, subclass_id FROM characters WHERE id = ?
            """, (character_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Character {character_id} not found")

            class_id, subclass_id = result

            # Grant class features for this level
            class_features = self.feature_manager.grant_class_features_for_level(
                character_id, class_id, new_level
            )

            # Grant subclass features for this level (if subclass is selected)
            subclass_features = []
            if subclass_id:
                subclass_features = self.feature_manager.grant_subclass_features_for_level(
                    character_id, subclass_id, new_level
                )

            # Handle class-specific updates
            self._handle_class_specific_updates(cursor, character_id, class_id, new_level)

            # Update character level
            cursor.execute("""
                UPDATE characters SET level = ? WHERE id = ?
            """, (new_level, character_id))

            conn.commit()

            return {
                'level': new_level,
                'class_features_granted': [f.feature_name for f in class_features],
                'subclass_features_granted': [f.feature_name for f in subclass_features],
                'total_features_granted': len(class_features) + len(subclass_features)
            }

    def get_features_for_level(self, class_id: str, level: int, subclass_id: str = None) -> List[str]:
        """Get list of features that would be granted at a specific level"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            features = []

            # Get class features
            cursor.execute("""
                SELECT feature_name FROM class_features_progression
                WHERE class_id = ? AND level = ?
            """, (class_id, level))
            features.extend([row[0] for row in cursor.fetchall()])

            # Get subclass features
            if subclass_id:
                cursor.execute("""
                    SELECT feature_name FROM subclass_features_progression
                    WHERE subclass_id = ? AND level = ?
                """, (subclass_id, level))
                features.extend([row[0] for row in cursor.fetchall()])

            return features

    def is_subclass_selection_level(self, class_id: str, level: int) -> bool:
        """Check if this level requires subclass selection"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM class_features_progression
                WHERE class_id = ? AND level = ? AND mechanics LIKE '%subclass_selection%'
            """, (class_id, level))
            return cursor.fetchone() is not None

    def _handle_class_specific_updates(self, cursor, character_id: str, class_id: str, level: int):
        """Handle class-specific level up effects (HP, spell slots, etc.)"""

        # Update class-specific progression tables
        if class_id == 'rogue':
            self._update_rogue_progression(cursor, character_id, level)
        elif class_id == 'fighter':
            self._update_fighter_progression(cursor, character_id, level)
        elif class_id == 'barbarian':
            self._update_barbarian_progression(cursor, character_id, level)
        elif class_id in ['wizard', 'cleric', 'warlock', 'sorcerer', 'paladin', 'ranger', 'bard', 'druid']:
            self._update_spellcaster_progression(cursor, character_id, class_id, level)

    def _update_rogue_progression(self, cursor, character_id: str, level: int):
        """Update rogue-specific progression"""
        # Calculate sneak attack dice (levels up every 2 levels)
        sneak_attack_dice = (level + 1) // 2

        # Check what features should be available
        cunning_action = level >= 2
        uncanny_dodge = level >= 5
        evasion = level >= 7
        cunning_strike = level >= 5
        reliable_talent = level >= 11
        slippery_mind = level >= 15
        elusive = level >= 18
        stroke_of_luck_max = 1 if level >= 20 else 0

        cursor.execute("""
            INSERT OR REPLACE INTO rogue_features (
                character_id, level, sneak_attack_dice,
                cunning_action_available, uncanny_dodge_available, evasion_available,
                cunning_strike_available, reliable_talent_active, slippery_mind_active,
                elusive_active, stroke_of_luck_uses_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, level, sneak_attack_dice,
            cunning_action, uncanny_dodge, evasion,
            cunning_strike, reliable_talent, slippery_mind,
            elusive, stroke_of_luck_max
        ))

    def _update_fighter_progression(self, cursor, character_id: str, level: int):
        """Update fighter-specific progression"""
        # Extra attacks: 1 at level 5, 2 at level 11, 3 at level 20
        extra_attacks = 0
        if level >= 20:
            extra_attacks = 3
        elif level >= 11:
            extra_attacks = 2
        elif level >= 5:
            extra_attacks = 1

        # Action surge uses: 1 at level 2, 2 at level 17
        action_surge_uses = 0
        if level >= 17:
            action_surge_uses = 2
        elif level >= 2:
            action_surge_uses = 1

        # Indomitable uses: 1 at level 9, 2 at level 13, 3 at level 17
        indomitable_uses = 0
        if level >= 17:
            indomitable_uses = 3
        elif level >= 13:
            indomitable_uses = 2
        elif level >= 9:
            indomitable_uses = 1

        cursor.execute("""
            INSERT OR REPLACE INTO fighter_features (
                character_id, level, extra_attacks, action_surge_uses_max,
                indomitable_uses_max, action_surge_uses_current, indomitable_uses_current
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, level, extra_attacks, action_surge_uses,
            indomitable_uses, action_surge_uses, indomitable_uses
        ))

    def _update_barbarian_progression(self, cursor, character_id: str, level: int):
        """Update barbarian-specific progression"""
        # Rage uses per long rest
        rage_uses = 2  # Level 1-2
        if level >= 20:
            rage_uses = 999  # Unlimited
        elif level >= 17:
            rage_uses = 6
        elif level >= 12:
            rage_uses = 5
        elif level >= 6:
            rage_uses = 4
        elif level >= 3:
            rage_uses = 3

        # Rage damage bonus
        rage_damage = 2  # Levels 1-8
        if level >= 16:
            rage_damage = 4
        elif level >= 9:
            rage_damage = 3

        cursor.execute("""
            INSERT OR REPLACE INTO barbarian_features (
                character_id, level, rage_uses_max, rage_damage_bonus,
                rage_uses_current
            ) VALUES (?, ?, ?, ?, ?)
        """, (character_id, level, rage_uses, rage_damage, rage_uses))

    def _update_spellcaster_progression(self, cursor, character_id: str, class_id: str, level: int):
        """Update spell slot progression for spellcasters"""
        # This would implement spell slot tables for each spellcasting class
        # For now, just ensure the character is recognized as a spellcaster

        # Check if spell_progression table exists for this character
        cursor.execute("""
            INSERT OR IGNORE INTO spell_progression (character_id, level, class_id)
            VALUES (?, ?, ?)
        """, (character_id, level, class_id))

    def migrate_character_to_dynamic_system(self, character_id: str):
        """Migrate an existing character to use the dynamic feature system"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get character info
            cursor.execute("SELECT class_id, subclass_id, level FROM characters WHERE id = ?", (character_id,))
            result = cursor.fetchone()
            if not result:
                return

            class_id, subclass_id, level = result

            # Clear existing feature instances
            cursor.execute("DELETE FROM character_feature_instances WHERE character_id = ?", (character_id,))

            # Grant all features from level 1 to current level
            for lvl in range(1, level + 1):
                self.feature_manager.grant_class_features_for_level(character_id, class_id, lvl)
                if subclass_id and lvl >= 3:  # Most subclasses start at level 3
                    self.feature_manager.grant_subclass_features_for_level(character_id, subclass_id, lvl)

            conn.commit()

    def get_level_up_preview(self, character_id: str, target_level: int) -> Dict[str, Any]:
        """Preview what features would be gained at target level"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT class_id, subclass_id FROM characters WHERE id = ?", (character_id,))
            result = cursor.fetchone()
            if not result:
                return {}

            class_id, subclass_id = result

            preview = {
                'level': target_level,
                'class_features': self.get_features_for_level(class_id, target_level),
                'subclass_features': self.get_features_for_level(class_id, target_level, subclass_id) if subclass_id else [],
                'requires_subclass_selection': self.is_subclass_selection_level(class_id, target_level)
            }

            return preview