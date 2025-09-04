"""
Level Up Service - Handle character leveling and multi-classing
"""

import sqlite3
from typing import Dict, List, Optional, Tuple
import json


class LevelUpService:
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
    
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
            
            result = {class_name: level for class_name, level in cursor.fetchall()}
            
            # If no multi-class data exists, get from main character table
            if not result:
                cursor.execute("SELECT class_id, level FROM characters WHERE id = ?", (character_id,))
                row = cursor.fetchone()
                if row:
                    result[row[0]] = row[1]
        except Exception as e:
            print(f"Error getting character class levels: {e}")
            result = {}
        finally:
            conn.close()
        
        return result
    
    def level_up_character(self, character_id: str, class_choice: str) -> bool:
        """Level up character in chosen class."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current total level
            cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
            current_total_level = cursor.fetchone()[0]
            new_total_level = current_total_level + 1
            
            # Check if character already has levels in this class (case-insensitive)
            cursor.execute("""
                SELECT level FROM character_class_levels 
                WHERE character_id = ? AND LOWER(class_name) = LOWER(?)
            """, (character_id, class_choice))
            
            existing_class_level = cursor.fetchone()
            
            if existing_class_level:
                # Level up existing class
                new_class_level = existing_class_level[0] + 1
                cursor.execute("""
                    UPDATE character_class_levels 
                    SET level = ? 
                    WHERE character_id = ? AND LOWER(class_name) = LOWER(?)
                """, (new_class_level, character_id, class_choice))
            else:
                # Add new class at level 1
                cursor.execute("""
                    INSERT INTO character_class_levels (character_id, class_name, level, hit_die_type)
                    VALUES (?, ?, 1, ?)
                """, (character_id, class_choice, self._get_hit_die_for_class(class_choice)))
                new_class_level = 1
            
            # Calculate hit point increase (use average for now: (die_size / 2) + 1 + CON modifier)
            hit_die = self._get_hit_die_for_class(class_choice)
            
            # Get character's CON modifier
            cursor.execute("SELECT constitution FROM characters WHERE id = ?", (character_id,))
            con_score = cursor.fetchone()[0]
            con_modifier = (con_score - 10) // 2
            
            # Calculate HP increase (average + CON mod)
            base_hp_increase = (hit_die // 2 + 1) + con_modifier
            base_hp_increase = max(1, base_hp_increase)  # Minimum 1 HP per level
            
            # Add species bonuses
            species_hp_bonus = self._get_species_hp_bonus(cursor, character_id)
            
            # Add feat bonuses  
            feat_hp_bonus = self._get_feat_hp_bonus(cursor, character_id)
            
            total_hp_increase = base_hp_increase + species_hp_bonus + feat_hp_bonus
            
            print(f"[LevelUp] HP increase: {total_hp_increase} (d{hit_die} average + {con_modifier} CON + {species_hp_bonus} species + {feat_hp_bonus} feats)")
            
            # Update main character table with level and HP
            cursor.execute("""
                UPDATE characters 
                SET level = ?, 
                    hit_points_max = hit_points_max + ?,
                    hit_points_current = hit_points_current + ?,
                    current_hit_points = current_hit_points + ?,
                    max_hit_points = max_hit_points + ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (new_total_level, total_hp_increase, total_hp_increase, total_hp_increase, total_hp_increase, character_id))
            
            # Grant new class features (old system)
            self._grant_class_features(cursor, character_id, class_choice, new_class_level)
            
            conn.commit()
            conn.close()
            
            # Update features using new feature system (after closing main connection)
            try:
                from core.feature_integration import FeatureSystemIntegration
                feature_system = FeatureSystemIntegration(self.db_path)
                
                # Refresh character features for new level
                feature_system.initialize_character_features(character_id)
                print(f"[LevelUp] Updated feature system for {class_choice} level {new_class_level} (total level {new_total_level})")
            except Exception as e:
                print(f"[LevelUp] Warning: Failed to update new feature system: {e}")
            
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error leveling up character: {e}")
            return False
    
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
                """, (character_id, "Martial Archetype", "passive", "permanent", 3, "Choose your Fighter subclass", "subclass_choice"))
                
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
        # Add rogue features as needed
        pass
    
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