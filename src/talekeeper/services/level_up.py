"""
Level Up Service - Handle character leveling and multi-classing
"""

import sqlite3
from typing import Dict, List, Optional, Tuple
import json
from talekeeper.services.subclass_manager import SubclassManager


class LevelUpService:
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
    
    def is_asi_level(self, character_id: str, class_choice: str) -> bool:
        """Check if next level grants ASI for the selected class."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get character's current level in the chosen class
            cursor.execute("""
                SELECT level FROM character_class_levels 
                WHERE character_id = ? AND LOWER(class_name) = LOWER(?)
            """, (character_id, class_choice))
            
            result = cursor.fetchone()
            if result:
                current_class_level = result[0]
                print(f"[LevelUp] Found existing {class_choice} level {current_class_level} in character_class_levels")
            else:
                # If no existing level in this class, check if it's their primary class
                cursor.execute("""
                    SELECT level, class_id FROM characters 
                    WHERE id = ?
                """, (character_id,))
                char_result = cursor.fetchone()
                if char_result and char_result[1] and char_result[1].lower() == class_choice.lower():
                    current_class_level = char_result[0]
                    print(f"[LevelUp] Using primary class {class_choice} level {current_class_level}")
                else:
                    current_class_level = 0
                    print(f"[LevelUp] No existing levels in {class_choice}, would be level 1")
            
            next_class_level = current_class_level + 1
            print(f"[LevelUp] Checking if {class_choice} level {next_class_level} is an ASI level")
            
            # Define ASI levels for each class (D&D 2024 SRD)
            asi_levels = {
                'fighter': [4, 6, 8, 12, 14, 16],  # Fighter gets extra ASIs
                'rogue': [4, 8, 10, 12, 16],       # Rogue gets extra ASI at 10
                'barbarian': [4, 8, 12, 16],
                'bard': [4, 8, 12, 16],
                'cleric': [4, 8, 12, 16],
                'druid': [4, 8, 12, 16],
                'monk': [4, 8, 12, 16],
                'paladin': [4, 8, 12, 16],
                'ranger': [4, 8, 12, 16],
                'sorcerer': [4, 8, 12, 16],
                'warlock': [4, 8, 12, 16],
                'wizard': [4, 8, 12, 16]
            }
            
            class_name = class_choice.lower()
            if class_name in asi_levels:
                is_asi = next_class_level in asi_levels[class_name]
                print(f"[LevelUp] {class_name} level {next_class_level}: ASI levels are {asi_levels[class_name]}, is_asi={is_asi}")
            else:
                # Default ASI levels for unknown classes
                is_asi = next_class_level in [4, 8, 12, 16, 19]
                print(f"[LevelUp] Unknown class {class_name}, using default ASI levels, is_asi={is_asi}")
            
            conn.close()
            return is_asi
            
        except Exception as e:
            print(f"Error checking ASI level: {e}")
            return False
    
    def get_available_classes(self) -> List[str]:
        """Get list of available classes for leveling."""
        return ['Barbarian', 'Cleric', 'Paladin', 'Rogue', 'Warlock', 'Wizard', 'Fighter']
    
    def get_character_class_levels(self, character_id: str) -> Dict[str, int]:
        """Get current class levels for a character."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        result = {}

        try:
            cursor.execute("""
                SELECT class_name, level
                FROM character_class_levels
                WHERE character_id = ?
            """, (character_id,))

            result = {class_name.lower(): level for class_name, level in cursor.fetchall()}
        except Exception as e:
            print(f"Error getting character class levels: {e}")
            result = {}
        finally:
            conn.close()

        return result
    
    def level_up_character(self, character_id: str, class_choice: str, subclass_choice: Optional[str] = None) -> bool:
        """Level up character in chosen class."""
        print(f"[LevelUp] level_up_character called for {character_id} in {class_choice}")
        import traceback
        print("".join(traceback.format_stack()[-6:]))  # Show last 6 stack frames

        subclass_manager = SubclassManager(self.db_path)
        class_normalized = (class_choice or '').strip().lower()
        if not class_normalized:
            print("[LevelUp] Error: class choice is required")
            return False

        existing_subclass = subclass_manager.get_character_subclass(character_id, class_normalized)

        # Also check the enhanced subclass system
        enhanced_subclass = None
        try:
            from talekeeper.services.enhanced_subclass_manager import EnhancedSubclassManager
            enhanced_manager = EnhancedSubclassManager(self.db_path)
            # Check if character has subclass in enhanced system
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT subclass_id FROM characters WHERE id = ?", (character_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    enhanced_subclass = row[0]
                    print(f"[LevelUp] Found enhanced subclass: {enhanced_subclass}")
        except Exception as e:
            print(f"[LevelUp] Could not check enhanced subclass system: {e}")

        # Use enhanced subclass if available, otherwise fall back to old system
        if enhanced_subclass:
            existing_subclass = enhanced_subclass
        pending_subclass = None
        subclass_selection_level = 3
        new_class_level = None
        new_total_level = None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT COALESCE(SUM(level), 0)
                FROM character_class_levels
                WHERE character_id = ?
            """, (character_id,))
            current_total_level = cursor.fetchone()[0]

            if current_total_level == 0:
                raise ValueError("Character not found in character_class_levels")

            new_total_level = current_total_level + 1

            cursor.execute(
                """
                SELECT MIN(selection_level)
                FROM subclasses
                WHERE LOWER(class_id) = ?
                """,
                (class_normalized,)
            )
            selection_row = cursor.fetchone()
            if selection_row and selection_row[0]:
                subclass_selection_level = selection_row[0]

            cursor.execute(
                """
                SELECT level FROM character_class_levels
                WHERE character_id = ? AND LOWER(class_name) = LOWER(?)
                """,
                (character_id, class_choice),
            )
            existing_class_level = cursor.fetchone()

            if existing_class_level:
                new_class_level = existing_class_level[0] + 1
                cursor.execute(
                    """
                    UPDATE character_class_levels
                    SET level = ?
                    WHERE character_id = ? AND LOWER(class_name) = LOWER(?)
                    """,
                    (new_class_level, character_id, class_choice),
                )
            else:
                new_class_level = 1
                cursor.execute(
                    """
                    INSERT INTO character_class_levels (character_id, class_name, level, hit_die_type)
                    VALUES (?, ?, ?, ?)
                    """,
                    (character_id, class_choice, new_class_level, self._get_hit_die_for_class(class_choice)),
                )

            if new_class_level >= subclass_selection_level and not existing_subclass:
                if not subclass_choice:
                    raise ValueError(f"Subclass selection required for {class_choice} level {new_class_level}")

                cursor.execute(
                    """
                    SELECT class_id FROM subclasses WHERE id = ?
                    """,
                    (subclass_choice,),
                )
                subclass_row = cursor.fetchone()
                if not subclass_row or (subclass_row[0] or '').strip().lower() != class_normalized:
                    raise ValueError(f"Subclass {subclass_choice} does not belong to class {class_choice}")

                pending_subclass = subclass_choice

            cursor.execute(
                """
                UPDATE characters
                SET level = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (new_total_level, character_id),
            )

            if class_normalized == 'fighter':
                cursor.execute(
                    """
                    UPDATE fighter_features
                    SET level = ?
                    WHERE character_id = ?
                    """,
                    (new_class_level, character_id),
                )
                print(f"[LevelUp] Updated fighter_features level to {new_class_level}")

            self._grant_class_features(cursor, character_id, class_choice, new_class_level)

            conn.commit()
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error leveling up character: {e}")
            return False

        conn.close()

        assigned_subclass_id = existing_subclass
        if pending_subclass:
            if subclass_manager.select_subclass(character_id, pending_subclass, new_class_level):
                assigned_subclass_id = pending_subclass
            else:
                print(f"[LevelUp] Failed to assign subclass {pending_subclass}")
                return False
        elif existing_subclass:
            assigned_subclass_id = existing_subclass

        if assigned_subclass_id:
            try:
                subclass_manager.update_features_for_class(character_id, class_normalized, new_class_level)
            except Exception as subclass_error:
                print(f"[LevelUp] Warning: Failed to update subclass features: {subclass_error}")

        hp_recalculated = self.recalculate_character_hp(character_id)
        if hp_recalculated:
            print(f"[LevelUp] HP recalculated for level {new_total_level}")

        try:
            from talekeeper.core.feature_integration import FeatureSystemIntegration
            feature_system = FeatureSystemIntegration(self.db_path)
            feature_system.initialize_character_features(character_id)
            print(f"[LevelUp] Updated feature system for {class_choice} level {new_class_level} (total level {new_total_level})")
        except Exception as e:
            print(f"[LevelUp] Warning: Failed to update new feature system: {e}")

        try:
            from talekeeper.services.character_resources import CharacterResourceService
            resource_service = CharacterResourceService(self.db_path)

            if class_normalized == 'fighter':
                result = resource_service.initialize_fighter_resources(character_id, new_total_level)
                print(f"[LevelUp] Updated Fighter resources: {result.get('resources_added', [])}")
            elif class_normalized == 'barbarian':
                result = resource_service.initialize_barbarian_resources(character_id, new_total_level)
                print(f"[LevelUp] Updated Barbarian resources: {result.get('resources_added', [])}")
        except Exception as e:
            print(f"[LevelUp] Warning: Failed to update resources: {e}")

        if assigned_subclass_id and class_normalized == 'paladin':
            try:
                from talekeeper.services.subclass_feature_manager import SubclassFeatureManager
                subclass_feature_mgr = SubclassFeatureManager(self.db_path)

                features = subclass_feature_mgr.get_subclass_features_for_level(assigned_subclass_id, new_class_level)
                for feature in features:
                    subclass_feature_mgr.grant_subclass_feature(character_id, feature['id'], new_class_level)

                new_spells = subclass_feature_mgr.grant_oath_spells_for_level(character_id, assigned_subclass_id, new_class_level)
                if new_spells:
                    print(f"[LevelUp] Granted oath spells: {', '.join(new_spells)}")

                print(f"[LevelUp] Granted {len(features)} subclass features for {assigned_subclass_id}")
            except Exception as e:
                print(f"[LevelUp] Warning: Failed to grant subclass features: {e}")

        return True
    def _get_hit_die_for_class(self, class_name: str) -> int:
        """Get hit die size for class."""
        hit_dice = {
            'Barbarian': 12, 'barbarian': 12,
            'Fighter': 10, 'fighter': 10,
            'Paladin': 10, 'paladin': 10,
            'Cleric': 8, 'cleric': 8,
            'Rogue': 8, 'rogue': 8,
            'Warlock': 8, 'warlock': 8,
            'Wizard': 6, 'wizard': 6
        }
        return hit_dice.get(class_name, 8)
    
    def _grant_class_features(self, cursor, character_id: str, class_name: str, class_level: int):
        """Grant class features for the new level."""
        print(f"[LevelUp] Granting level {class_level} features for {class_name}")
        
        # Add basic feature entry to character_features table
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO character_features 
                (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (character_id, f"{class_name} Level {class_level}", "passive", "permanent", class_level, f"Advanced to {class_name} level {class_level}", ""))
        except Exception as e:
            print(f"[LevelUp] Could not add basic feature entry: {e}")
        
        # Grant specific class features based on level
        if class_name.lower() == 'fighter':
            self._grant_fighter_features(cursor, character_id, class_level)
        elif class_name.lower() == 'rogue':
            self._grant_rogue_features(cursor, character_id, class_level)
        # Add other classes as needed
    
    def _grant_fighter_features(self, cursor, character_id: str, level: int):
        """Grant Fighter-specific features."""
        try:
            if level == 2:
                # Grant Action Surge
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features 
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Action Surge", "action", "short_rest", 2, "Take one additional action on your turn", "action_surge"))
                
                # Update fighter-specific table if it exists
                cursor.execute("""
                    UPDATE fighter_features 
                    SET action_surge_uses_max = 1, action_surge_uses_current = 1
                    WHERE character_id = ?
                """, (character_id,))
                
                print(f"[LevelUp] Granted Action Surge to Fighter")
                
            elif level == 3:
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features 
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Martial Archetype", "passive", "permanent", 3, "Choose your Fighter subclass", '{"type": "subclass_choice"}'))
                
            elif level == 5:
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features 
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Extra Attack", "passive", "permanent", 5, "Attack twice when you take the Attack action", "extra_attack"))
                
                # Update fighter table
                cursor.execute("""
                    UPDATE fighter_features 
                    SET extra_attacks = 2
                    WHERE character_id = ?
                """, (character_id,))
                
        except Exception as e:
            print(f"[LevelUp] Error granting Fighter features: {e}")
    
    def _grant_rogue_features(self, cursor, character_id: str, level: int):
        """Grant Rogue-specific features."""
        try:
            # Calculate sneak attack dice based on level (1d6 per 2 levels, rounded up)
            sneak_attack_dice = (level + 1) // 2

            # Check if rogue_features entry exists
            cursor.execute("SELECT character_id FROM rogue_features WHERE character_id = ?", (character_id,))
            exists = cursor.fetchone() is not None

            if not exists:
                # Create new entry with all defaults
                cursor.execute("""
                    INSERT INTO rogue_features
                    (character_id, level, sneak_attack_dice, cunning_action_available,
                     expertise_count, uncanny_dodge_available, evasion_available,
                     cunning_strike_available, reliable_talent_active, improved_cunning_strike,
                     slippery_mind_active, elusive_active, stroke_of_luck_uses_current, stroke_of_luck_uses_max)
                    VALUES (?, ?, ?, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                """, (character_id, level, sneak_attack_dice))
                print(f"[LevelUp] Created rogue_features entry for character {character_id}")
            else:
                # Update existing entry
                cursor.execute("""
                    UPDATE rogue_features
                    SET level = ?, sneak_attack_dice = ?
                    WHERE character_id = ?
                """, (level, sneak_attack_dice, character_id))
                print(f"[LevelUp] Updated rogue_features level={level}, sneak_attack_dice={sneak_attack_dice}")

            if level == 1:
                # Sneak Attack
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Sneak Attack", "passive", "permanent", 1, f"Deal extra {sneak_attack_dice}d6 damage when you have advantage", f'{{"sneak_attack_dice": {sneak_attack_dice}}}'))

                # Thieves' Cant
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Thieves' Cant", "passive", "permanent", 1, "Secret language of rogues and criminals", ""))

                # Expertise (1st level)
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Expertise", "passive", "permanent", 1, "Double proficiency bonus for 2 skills", '{"expertise_count": 2}'))

                print(f"[LevelUp] Granted Sneak Attack, Thieves' Cant, and Expertise to Rogue")

            elif level == 2:
                # Cunning Action
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Cunning Action", "bonus_action", "permanent", 2, "Take Dash, Disengage, or Hide as bonus action", '{"cunning_action_options": ["dash", "disengage", "hide"]}'))

                # Update rogue-specific table
                cursor.execute("""
                    UPDATE rogue_features
                    SET cunning_action_available = 1
                    WHERE character_id = ?
                """, (character_id,))

                print(f"[LevelUp] Granted Cunning Action to Rogue")

            elif level == 3:
                # Subclass selection handled separately
                print(f"[LevelUp] Level 3: Roguish Archetype selection")

            elif level == 5:
                # Uncanny Dodge
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Uncanny Dodge", "reaction", "permanent", 5, "Use reaction to halve damage from one attack", '{"damage_reduction": 0.5}'))

                cursor.execute("""
                    UPDATE rogue_features
                    SET uncanny_dodge_available = 1
                    WHERE character_id = ?
                """, (character_id,))

                # Cunning Strike
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Cunning Strike", "passive", "permanent", 5, "Forgo Sneak Attack damage to apply debuffs", '{"cunning_strike_effects": ["trip", "withdraw", "poison"]}'))

                cursor.execute("""
                    UPDATE rogue_features
                    SET cunning_strike_available = 1, cunning_strike_effects_known = '["trip", "withdraw", "poison"]'
                    WHERE character_id = ?
                """, (character_id,))

                print(f"[LevelUp] Granted Uncanny Dodge and Cunning Strike to Rogue")

            elif level == 6:
                # Expertise improvement
                cursor.execute("""
                    UPDATE character_features
                    SET mechanics = '{"expertise_count": 4}', description = "Double proficiency bonus for 4 skills"
                    WHERE character_id = ? AND feature_name = 'Expertise'
                """, (character_id,))

                cursor.execute("""
                    UPDATE rogue_features
                    SET expertise_count = 4
                    WHERE character_id = ?
                """, (character_id,))

                print(f"[LevelUp] Improved Expertise to 4 skills")

            elif level == 7:
                # Evasion
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Evasion", "passive", "permanent", 7, "Take no damage on successful DEX saves, half on failure", '{"dex_save_advantage": true}'))

                cursor.execute("""
                    UPDATE rogue_features
                    SET evasion_available = 1
                    WHERE character_id = ?
                """, (character_id,))

                print(f"[LevelUp] Granted Evasion to Rogue")

            elif level == 11:
                # Reliable Talent
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Reliable Talent", "passive", "permanent", 11, "Treat d20 rolls of 9 or lower as 10 for proficient skills", '{"minimum_roll": 10}'))

                cursor.execute("""
                    UPDATE rogue_features
                    SET reliable_talent_active = 1, reliable_talent_minimum = 10
                    WHERE character_id = ?
                """, (character_id,))

                print(f"[LevelUp] Granted Reliable Talent to Rogue")

            elif level == 14:
                # Improved Cunning Strike
                cursor.execute("""
                    UPDATE rogue_features
                    SET improved_cunning_strike = 1, cunning_strike_effects_known = '["trip", "withdraw", "poison", "daze", "knock_out", "obscure"]'
                    WHERE character_id = ?
                """, (character_id,))

                print(f"[LevelUp] Improved Cunning Strike with additional effects")

            elif level == 15:
                # Slippery Mind
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Slippery Mind", "passive", "permanent", 15, "Proficiency in Wisdom saving throws", '{"wis_save_proficiency": true}'))

                cursor.execute("""
                    UPDATE rogue_features
                    SET slippery_mind_active = 1
                    WHERE character_id = ?
                """, (character_id,))

                print(f"[LevelUp] Granted Slippery Mind to Rogue")

            elif level == 18:
                # Elusive
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Elusive", "passive", "permanent", 18, "No attack has advantage against you unless incapacitated", '{"no_advantage": true}'))

                cursor.execute("""
                    UPDATE rogue_features
                    SET elusive_active = 1
                    WHERE character_id = ?
                """, (character_id,))

                print(f"[LevelUp] Granted Elusive to Rogue")

            elif level == 20:
                # Stroke of Luck
                cursor.execute("""
                    INSERT OR REPLACE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, "Stroke of Luck", "action", "short_rest", 20, "Turn a miss into a hit, or turn a hit into a critical", '{"uses": 1}'))

                cursor.execute("""
                    UPDATE rogue_features
                    SET stroke_of_luck_uses_current = 1, stroke_of_luck_uses_max = 1
                    WHERE character_id = ?
                """, (character_id,))

                print(f"[LevelUp] Granted Stroke of Luck to Rogue")

            # Always update Sneak Attack for odd levels
            if level % 2 == 1:
                cursor.execute("""
                    UPDATE character_features
                    SET mechanics = ?, description = ?
                    WHERE character_id = ? AND feature_name = 'Sneak Attack'
                """, (f'{{"sneak_attack_dice": {sneak_attack_dice}}}', f"Deal extra {sneak_attack_dice}d6 damage when you have advantage", character_id))

                print(f"[LevelUp] Updated Sneak Attack to {sneak_attack_dice}d6")

        except Exception as e:
            print(f"[LevelUp] Error granting rogue features: {e}")
    
    def _get_species_hp_bonus(self, cursor, character_id: str) -> int:
        """Get HP bonus per level from species traits."""
        try:
            cursor.execute("SELECT race_id FROM characters WHERE id = ?", (character_id,))
            race_result = cursor.fetchone()
            if not race_result:
                return 0
                
            race_id = race_result[0].lower()
            
            # Dwarven Toughness: +1 HP per level
            if race_id in ['dwarf', 'dwarves']:
                return 1
                
            return 0
        except Exception as e:
            print(f"[LevelUp] Error getting species HP bonus: {e}")
            return 0
    
    def _get_feat_hp_bonus(self, cursor, character_id: str) -> int:
        """Get HP bonus per level from feats."""
        try:
            cursor.execute("SELECT feat_name FROM character_feats WHERE character_id = ?", (character_id,))
            feats = [row[0] for row in cursor.fetchall()]
            
            hp_bonus = 0
            
            # Tough feat: +2 HP per level
            if 'Tough' in feats:
                hp_bonus += 2
                
            return hp_bonus
        except Exception as e:
            print(f"[LevelUp] Error getting feat HP bonus: {e}")
            return 0
    
    def get_next_level_features(self, character_id: str, class_choice: str) -> List[Dict]:
        """Get features that would be gained at next level in chosen class."""
        class_levels = self.get_character_class_levels(character_id)
        current_class_level = class_levels.get(class_choice, 0)
        next_level = current_class_level + 1
        
        # Return generic level benefits for now
        # TODO: Integrate with proper feature system when available
        
        benefits = []
        
        # Universal benefits
        benefits.append({
            'name': 'Hit Points',
            'description': f'Gain hit points (1d{self._get_hit_die_for_class(class_choice)} + CON modifier)'
        })
        
        benefits.append({
            'name': 'Proficiency Bonus',
            'description': f'Your proficiency bonus may increase at level {next_level}'
        })
        
        # Class-specific benefits (basic implementation)
        if class_choice.lower() == 'fighter':
            if next_level == 2:
                benefits.append({'name': 'Action Surge', 'description': 'Take one additional action on your turn'})
            elif next_level == 3:
                benefits.append({'name': 'Martial Archetype', 'description': 'Choose your Fighter subclass'})
            elif next_level == 4:
                benefits.append({'name': 'Ability Score Improvement', 'description': 'Increase ability scores or take a feat'})
            elif next_level == 5:
                benefits.append({'name': 'Extra Attack', 'description': 'Attack twice when you take the Attack action'})
            elif next_level == 6:
                benefits.append({'name': 'Ability Score Improvement', 'description': 'Increase ability scores or take a feat'})
        
        # Add generic benefit if no specific ones
        if len(benefits) == 2:  # Only the universal ones
            benefits.append({
                'name': f'{class_choice.title()} Features',
                'description': f'Class-specific improvements and new abilities'
            })
        
        return benefits
    
    def recalculate_character_hp(self, character_id: str) -> bool:
        """Recalculate a character's HP to include species and feat bonuses that may be missing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get character data
            cursor.execute("""
                SELECT level, class_id, constitution, hit_points_max, race_id
                FROM characters WHERE id = ?
            """, (character_id,))
            char_data = cursor.fetchone()
            
            if not char_data:
                return False
                
            level, class_id, con_score, current_max_hp, race_id = char_data
            con_modifier = (con_score - 10) // 2
            
            # Calculate what HP should be
            hit_die = self._get_hit_die_for_class(class_id)
            base_hp_per_level = (hit_die // 2 + 1) + con_modifier
            base_hp_first_level = hit_die + con_modifier  # First level gets max hit die
            
            # Calculate total base HP
            if level == 1:
                total_base_hp = base_hp_first_level
            else:
                total_base_hp = base_hp_first_level + (base_hp_per_level * (level - 1))
            
            # Add species bonuses
            species_hp_bonus = 0
            if race_id.lower() in ['dwarf', 'dwarves']:
                species_hp_bonus = level  # +1 per level
                
            # Add feat bonuses
            cursor.execute("SELECT feat_name FROM character_feats WHERE character_id = ?", (character_id,))
            feats = [row[0] for row in cursor.fetchall()]
            
            feat_hp_bonus = 0
            if 'Tough' in feats:
                feat_hp_bonus = level * 2  # +2 per level
                
            # Calculate correct total HP
            correct_max_hp = max(1, total_base_hp + species_hp_bonus + feat_hp_bonus)
            
            # Update if different
            if correct_max_hp != current_max_hp:
                hp_difference = correct_max_hp - current_max_hp
                
                cursor.execute("""
                    UPDATE characters 
                    SET hit_points_max = ?,
                        max_hit_points = ?,
                        hit_points_current = hit_points_current + ?,
                        current_hit_points = current_hit_points + ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (correct_max_hp, correct_max_hp, hp_difference, hp_difference, character_id))
                
                conn.commit()
                print(f"[LevelUp] Recalculated HP for character: {current_max_hp} -> {correct_max_hp} (+{hp_difference})")
                print(f"  Base: {total_base_hp}, Species: +{species_hp_bonus}, Feats: +{feat_hp_bonus}")
                return True
            else:
                print(f"[LevelUp] Character HP already correct: {current_max_hp}")
                return False
                
        except Exception as e:
            print(f"[LevelUp] Error recalculating HP: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()


level_up_service = LevelUpService()

