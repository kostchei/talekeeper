import sqlite3
from typing import Dict, List, Set, Optional, Tuple
from services.proficiency_bonus import get_proficiency_bonus


class ProficiencySystem:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def initialize_character_proficiencies(self, character_id: str, class_id: str, 
                                          background: Optional[str] = None,
                                          race_id: Optional[str] = None,
                                          conn=None) -> bool:
        try:
            # Use provided connection or create new one
            should_close = False
            if conn is None:
                conn = self._get_connection()
                should_close = True
            
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM character_proficiencies WHERE character_id = ?", (character_id,))
            
            cursor.execute("""
                SELECT weapon_type FROM class_weapon_proficiencies WHERE class_id = ?
            """, (class_id,))
            weapon_profs = cursor.fetchall()
            for prof in weapon_profs:
                cursor.execute("""
                    INSERT INTO character_proficiencies 
                    (character_id, proficiency_type, proficiency_name, source)
                    VALUES (?, 'weapon', ?, 'class')
                """, (character_id, prof[0]))
            
            cursor.execute("""
                SELECT armor_type FROM class_armor_proficiencies WHERE class_id = ?
            """, (class_id,))
            armor_profs = cursor.fetchall()
            for prof in armor_profs:
                cursor.execute("""
                    INSERT INTO character_proficiencies 
                    (character_id, proficiency_type, proficiency_name, source)
                    VALUES (?, 'armor', ?, 'class')
                """, (character_id, prof[0]))
            
            cursor.execute("""
                SELECT skill FROM class_skill_proficiencies WHERE class_id = ?
            """, (class_id,))
            skill_profs = cursor.fetchall()
            for prof in skill_profs:
                cursor.execute("""
                    INSERT OR IGNORE INTO character_proficiencies 
                    (character_id, proficiency_type, proficiency_name, source)
                    VALUES (?, 'skill', ?, 'class')
                """, (character_id, prof[0]))
            
            cursor.execute("""
                SELECT ability FROM class_saving_throws WHERE class_id = ?
            """, (class_id,))
            save_profs = cursor.fetchall()
            for prof in save_profs:
                cursor.execute("""
                    INSERT INTO character_proficiencies 
                    (character_id, proficiency_type, proficiency_name, source)
                    VALUES (?, 'saving_throw', ?, 'class')
                """, (character_id, prof[0]))
            
            # Only commit if we created our own connection
            if should_close:
                conn.commit()
                conn.close()
            
            return True
                
        except Exception as e:
            print(f"[Proficiency] Error initializing proficiencies: {e}")
            return False
    
    def get_character_proficiencies(self, character_id: str) -> Dict[str, List[str]]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT proficiency_type, proficiency_name 
                    FROM character_proficiencies 
                    WHERE character_id = ?
                """, (character_id,))
                
                proficiencies = {
                    'weapon': [],
                    'armor': [],
                    'skill': [],
                    'tool': [],
                    'language': [],
                    'saving_throw': []
                }
                
                for row in cursor.fetchall():
                    prof_type, prof_name = row
                    if prof_type in proficiencies:
                        proficiencies[prof_type].append(prof_name)
                
                return proficiencies
                
        except Exception as e:
            print(f"[Proficiency] Error getting proficiencies: {e}")
            return {'weapon': [], 'armor': [], 'skill': [], 'tool': [], 'language': []}
    
    def is_proficient_with_weapon(self, character_id: str, weapon_name: str) -> Tuple[bool, str]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT weapon_category FROM equipment 
                    WHERE name = ? AND item_type = 'weapon'
                """, (weapon_name,))
                weapon_row = cursor.fetchone()
                
                if not weapon_row:
                    return True, "Unknown weapon"
                
                weapon_category = weapon_row[0] if weapon_row[0] else 'simple_melee'
                weapon_type = 'martial' if 'martial' in weapon_category else 'simple'
                
                cursor.execute("""
                    SELECT proficiency_name FROM character_proficiencies 
                    WHERE character_id = ? AND proficiency_type = 'weapon'
                """, (character_id,))
                
                proficiencies = [row[0] for row in cursor.fetchall()]
                
                if 'martial' in proficiencies and weapon_type in ['simple', 'martial']:
                    return True, ""
                if 'simple' in proficiencies and weapon_type == 'simple':
                    return True, ""
                if weapon_name.lower() in [p.lower() for p in proficiencies]:
                    return True, ""
                if weapon_type in proficiencies:
                    return True, ""
                
                return False, f"Not proficient with {weapon_type} weapons"
                
        except Exception as e:
            print(f"[Proficiency] Error checking weapon proficiency: {e}")
            return True, ""
    
    def is_proficient_with_armor(self, character_id: str, armor_name: str) -> Tuple[bool, str]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT armor_type FROM equipment 
                    WHERE name = ? AND item_type = 'armor'
                """, (armor_name,))
                armor_row = cursor.fetchone()
                
                if not armor_row:
                    return True, "Unknown armor"
                
                armor_type = armor_row[0] if armor_row[0] else 'light'
                
                cursor.execute("""
                    SELECT proficiency_name FROM character_proficiencies 
                    WHERE character_id = ? AND proficiency_type = 'armor'
                """, (character_id,))
                
                proficiencies = [row[0] for row in cursor.fetchall()]
                
                if 'heavy' in proficiencies:
                    return True, ""
                if 'medium' in proficiencies and armor_type in ['light', 'medium']:
                    return True, ""
                if 'light' in proficiencies and armor_type == 'light':
                    return True, ""
                if armor_type in proficiencies:
                    return True, ""
                
                return False, f"Not proficient with {armor_type} armor"
                
        except Exception as e:
            print(f"[Proficiency] Error checking armor proficiency: {e}")
            return True, ""
    
    def is_proficient_with_shield(self, character_id: str) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM character_proficiencies 
                    WHERE character_id = ? 
                    AND proficiency_type = 'armor' 
                    AND proficiency_name = 'shields'
                """, (character_id,))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            print(f"[Proficiency] Error checking shield proficiency: {e}")
            return False
    
    def is_proficient_in_skill(self, character_id: str, skill_name: str) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM character_proficiencies 
                    WHERE character_id = ? 
                    AND proficiency_type = 'skill' 
                    AND LOWER(proficiency_name) = LOWER(?)
                """, (character_id, skill_name))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            print(f"[Proficiency] Error checking skill proficiency: {e}")
            return False
    
    def add_proficiency(self, character_id: str, prof_type: str, prof_name: str, source: str = 'manual', conn=None) -> bool:
        try:
            should_close = False
            if conn is None:
                conn = self._get_connection()
                should_close = True
            
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO character_proficiencies 
                (character_id, proficiency_type, proficiency_name, source)
                VALUES (?, ?, ?, ?)
            """, (character_id, prof_type, prof_name, source))
            
            if should_close:
                conn.commit()
                conn.close()
            
            return cursor.rowcount > 0
                
        except Exception as e:
            print(f"[Proficiency] Error adding proficiency: {e}")
            return False
    
    def remove_proficiency(self, character_id: str, prof_type: str, prof_name: str) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM character_proficiencies 
                    WHERE character_id = ? 
                    AND proficiency_type = ? 
                    AND proficiency_name = ?
                """, (character_id, prof_type, prof_name))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"[Proficiency] Error removing proficiency: {e}")
            return False
    
    def calculate_skill_bonus(self, character_id: str, skill_name: str, ability_mod: int) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT level FROM characters WHERE id = ?
                """, (character_id,))
                level_row = cursor.fetchone()
                
                if not level_row:
                    return ability_mod
                
                level = level_row[0]
                prof_bonus = get_proficiency_bonus(level)
                
                if self.is_proficient_in_skill(character_id, skill_name):
                    return ability_mod + prof_bonus
                else:
                    return ability_mod
                    
        except Exception as e:
            print(f"[Proficiency] Error calculating skill bonus: {e}")
            return ability_mod
    
    def get_saving_throw_bonus(self, character_id: str, ability: str) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT strength, dexterity, constitution, intelligence, wisdom, charisma, level
                    FROM characters 
                    WHERE id = ?
                """, (character_id,))
                
                row = cursor.fetchone()
                if not row:
                    return 0
                
                ability_map = {
                    'strength': row[0],
                    'dexterity': row[1],
                    'constitution': row[2],
                    'intelligence': row[3],
                    'wisdom': row[4],
                    'charisma': row[5]
                }
                
                level = row[6]
                ability_score = ability_map.get(ability.lower(), 10)
                ability_mod = (ability_score - 10) // 2
                prof_bonus = get_proficiency_bonus(level)
                
                # Check if proficient in this saving throw
                cursor.execute("""
                    SELECT COUNT(*) FROM character_proficiencies 
                    WHERE character_id = ? 
                    AND proficiency_type = 'saving_throw' 
                    AND LOWER(proficiency_name) = LOWER(?)
                """, (character_id, ability))
                
                is_proficient = cursor.fetchone()[0] > 0
                
                if is_proficient:
                    return ability_mod + prof_bonus
                else:
                    return ability_mod
                    
        except Exception as e:
            print(f"[Proficiency] Error calculating saving throw bonus: {e}")
            return 0
    
    def get_attack_bonus(self, character_id: str, weapon_name: str, ability_mod: int) -> int:
        try:
            is_proficient, _ = self.is_proficient_with_weapon(character_id, weapon_name)
            
            if not is_proficient:
                return ability_mod
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT level FROM characters WHERE id = ?
                """, (character_id,))
                
                level_row = cursor.fetchone()
                if level_row:
                    prof_bonus = get_proficiency_bonus(level_row[0])
                    return ability_mod + prof_bonus
                
                return ability_mod
                
        except Exception as e:
            print(f"[Proficiency] Error calculating attack bonus: {e}")
            return ability_mod