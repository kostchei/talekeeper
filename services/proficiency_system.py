import sqlite3
from typing import Dict, List, Set, Optional, Tuple, Any
from services.proficiency_bonus import get_proficiency_bonus

SKILL_CANONICAL_MAP = {
    'acrobatics': 'Acrobatics',
    'animal handling': 'Animal Handling',
    'arcana': 'Arcana',
    'athletics': 'Athletics',
    'deception': 'Deception',
    'history': 'History',
    'insight': 'Insight',
    'intimidation': 'Intimidation',
    'investigation': 'Investigation',
    'medicine': 'Medicine',
    'nature': 'Nature',
    'perception': 'Perception',
    'performance': 'Performance',
    'persuasion': 'Persuasion',
    'religion': 'Religion',
    'sleight of hand': 'Sleight of Hand',
    'stealth': 'Stealth',
    'survival': 'Survival'
}


class ProficiencySystem:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def initialize_character_proficiencies(self, character_id: str, class_id: str,
                                          background: Optional[str] = None,
                                          race_id: Optional[str] = None,
                                          selected_skills: List[str] = None,
                                          selected_class_skills: List[str] = None,
                                          selected_species_skills: List[str] = None,
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

            # Handle class skill selections (chosen by player, not auto-assigned)
            # Support both legacy selected_skills and new separate parameters
            class_skills_to_add = selected_class_skills if selected_class_skills is not None else selected_skills
            if class_skills_to_add:
                for skill in class_skills_to_add:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_proficiencies
                        (character_id, proficiency_type, proficiency_name, source)
                        VALUES (?, 'skill', ?, 'class')
                    """, (character_id, skill))

            # Handle species skill selections (player choices from species options)
            if selected_species_skills:
                for skill in selected_species_skills:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_proficiencies
                        (character_id, proficiency_type, proficiency_name, source)
                        VALUES (?, 'skill', ?, 'species')
                    """, (character_id, skill))

            # Add background proficiencies (fixed, not chosen)
            if background:
                cursor.execute("""
                    SELECT proficiency_type, proficiency_name
                    FROM background_proficiencies
                    WHERE background_id = ? AND proficiency_name NOT LIKE 'choice_%'
                """, (background,))
                bg_profs = cursor.fetchall()
                for prof_type, prof_name in bg_profs:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_proficiencies
                        (character_id, proficiency_type, proficiency_name, source)
                        VALUES (?, ?, ?, 'background')
                    """, (character_id, prof_type, prof_name))
            
            # Add species proficiencies (fixed ones, not choices)
            if race_id:
                cursor.execute("""
                    SELECT proficiency_type, proficiency_name 
                    FROM species_proficiencies 
                    WHERE species_id = ? AND proficiency_name IS NOT NULL
                """, (race_id,))
                species_profs = cursor.fetchall()
                for prof_type, prof_name in species_profs:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_proficiencies 
                        (character_id, proficiency_type, proficiency_name, source)
                        VALUES (?, ?, ?, 'species')
                    """, (character_id, prof_type, prof_name))
            
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
                    'saving_throw': [],
                    'skill_expertise': []
                }
                
                for row in cursor.fetchall():
                    prof_type, prof_name = row
                    if prof_type in proficiencies:
                        proficiencies[prof_type].append(prof_name)
                
                proficiencies['skill_expertise'] = self._get_skill_expertise(cursor, character_id)

                return proficiencies
                
        except Exception as e:
            print(f"[Proficiency] Error getting proficiencies: {e}")
            return {'weapon': [], 'armor': [], 'skill': [], 'tool': [], 'language': [], 'saving_throw': [], 'skill_expertise': []}
    

    def _normalize_skill_name(self, skill: Any) -> Optional[str]:
        if not isinstance(skill, str):
            return None
        cleaned = ' '.join(skill.replace('_', ' ').replace('-', ' ').split()).lower()
        if not cleaned:
            return None
        canonical = SKILL_CANONICAL_MAP.get(cleaned)
        if canonical:
            return canonical
        return skill.strip().title()

    def _parse_skill_list(self, raw: Any) -> Set[str]:
        skills: Set[str] = set()
        if raw is None:
            return skills
        if isinstance(raw, str):
            stripped = raw.strip()
            if not stripped:
                return skills
            try:
                import json
                parsed = json.loads(stripped)
            except Exception:
                tokens = stripped.replace('|', ',').replace(';', ',').split(',')
                for token in tokens:
                    normalized = self._normalize_skill_name(token)
                    if normalized:
                        skills.add(normalized)
            else:
                skills.update(self._parse_skill_list(parsed))
            return skills
        if isinstance(raw, (list, tuple, set)):
            for item in raw:
                skills.update(self._parse_skill_list(item))
            return skills
        if isinstance(raw, dict):
            for value in raw.values():
                skills.update(self._parse_skill_list(value))
        return skills

    def _get_skill_expertise(self, cursor, character_id: str) -> List[str]:
        expertise: Set[str] = set()
        try:
            cursor.execute("""
                SELECT expertise_skills
                FROM rogue_features
                WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()
            if row and row[0]:
                expertise.update(self._parse_skill_list(row[0]))
        except Exception as error:
            print(f"[Proficiency] Error loading rogue expertise: {error}")

        try:
            cursor.execute("""
                SELECT proficiency_name
                FROM character_proficiencies
                WHERE character_id = ?
                  AND proficiency_type = 'skill_expertise'
            """, (character_id,))
            for (name,) in cursor.fetchall():
                normalized = self._normalize_skill_name(name)
                if normalized:
                    expertise.add(normalized)
        except Exception as error:
            print(f"[Proficiency] Error loading proficiency expertise: {error}")

        return sorted(expertise)

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

                # Get magical saving throw bonuses
                cursor.execute("""
                    SELECT save_bonus FROM character_magical_bonuses
                    WHERE character_id = ?
                """, (character_id,))

                magical_bonus_row = cursor.fetchone()
                magical_save_bonus = magical_bonus_row[0] if magical_bonus_row and magical_bonus_row[0] else 0

                base_bonus = ability_mod + (prof_bonus if is_proficient else 0)
                total_bonus = base_bonus + magical_save_bonus

                return total_bonus
                    
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
    
    def get_class_skill_choices(self, class_id: str) -> Dict[str, Any]:
        """Get skill selection options for a class."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT skill_count, available_skills 
                    FROM class_skill_choices 
                    WHERE class_id = ?
                """, (class_id,))
                
                result = cursor.fetchone()
                if result:
                    import json
                    return {
                        'count': result[0],
                        'available': json.loads(result[1])
                    }
                return {'count': 0, 'available': []}
                
        except Exception as e:
            print(f"[Proficiency] Error getting class skill choices: {e}")
            return {'count': 0, 'available': []}
    
    def get_background_proficiencies(self, background_id: str) -> Dict[str, List[str]]:
        """Get fixed proficiencies from a background."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT proficiency_type, proficiency_name 
                    FROM background_proficiencies 
                    WHERE background_id = ?
                """, (background_id,))
                
                proficiencies = {'skill': [], 'tool': [], 'language': []}
                for prof_type, prof_name in cursor.fetchall():
                    if prof_type in proficiencies and not prof_name.startswith('choice_'):
                        proficiencies[prof_type].append(prof_name)
                
                return proficiencies
                
        except Exception as e:
            print(f"[Proficiency] Error getting background proficiencies: {e}")
            return {'skill': [], 'tool': [], 'language': []}
    
    def get_species_proficiencies(self, species_id: str) -> Dict[str, Any]:
        """Get proficiencies and choices from a species."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT proficiency_type, proficiency_name, choice_count, available_options 
                    FROM species_proficiencies 
                    WHERE species_id = ?
                """, (species_id,))
                
                fixed = {'skill': [], 'tool': [], 'language': [], 'weapon': []}
                choices = []
                
                for prof_type, prof_name, choice_count, available_options in cursor.fetchall():
                    if prof_name:  # Fixed proficiency
                        if prof_type in fixed:
                            fixed[prof_type].append(prof_name)
                    elif choice_count > 0:  # Choice
                        import json
                        choices.append({
                            'type': prof_type,
                            'count': choice_count,
                            'options': json.loads(available_options) if available_options else []
                        })
                
                return {'fixed': fixed, 'choices': choices}
                
        except Exception as e:
            print(f"[Proficiency] Error getting species proficiencies: {e}")
            return {'fixed': {'skill': [], 'tool': [], 'language': [], 'weapon': []}, 'choices': []}
    
    def add_feat_proficiencies(self, character_id: str, feat_name: str, selected_proficiencies: List[str] = None, conn=None) -> bool:
        """Add proficiencies from a feat (like Skilled)."""
        try:
            should_close = False
            if conn is None:
                conn = self._get_connection()
                should_close = True
            
            cursor = conn.cursor()
            
            # Handle known feats that grant proficiencies
            if feat_name.lower() == 'skilled':
                # Skilled feat: Choose 3 skill proficiencies
                if selected_proficiencies and len(selected_proficiencies) <= 3:
                    for skill in selected_proficiencies:
                        cursor.execute("""
                            INSERT OR IGNORE INTO character_proficiencies 
                            (character_id, proficiency_type, proficiency_name, source)
                            VALUES (?, 'skill', ?, 'feat')
                        """, (character_id, skill))
                else:
                    print(f"[Proficiency] Warning: Skilled feat requires exactly 3 skill selections")
                    
            elif feat_name.lower() == 'weapon master':
                # Weapon Master feat: Choose 4 simple or martial weapons
                if selected_proficiencies and len(selected_proficiencies) <= 4:
                    for weapon in selected_proficiencies:
                        cursor.execute("""
                            INSERT OR IGNORE INTO character_proficiencies 
                            (character_id, proficiency_type, proficiency_name, source)
                            VALUES (?, 'weapon', ?, 'feat')
                        """, (character_id, weapon))
                        
            elif feat_name.lower() == 'lightly armored':
                # Lightly Armored: Light armor proficiency
                cursor.execute("""
                    INSERT OR IGNORE INTO character_proficiencies 
                    (character_id, proficiency_type, proficiency_name, source)
                    VALUES (?, 'armor', 'light', 'feat')
                """, (character_id,))
                
            elif feat_name.lower() == 'moderately armored':
                # Moderately Armored: Medium armor and shields
                for armor_type in ['medium', 'shields']:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_proficiencies 
                        (character_id, proficiency_type, proficiency_name, source)
                        VALUES (?, 'armor', ?, 'feat')
                    """, (character_id, armor_type))
                    
            elif feat_name.lower() == 'heavily armored':
                # Heavily Armored: Heavy armor
                cursor.execute("""
                    INSERT OR IGNORE INTO character_proficiencies 
                    (character_id, proficiency_type, proficiency_name, source)
                    VALUES (?, 'armor', 'heavy', 'feat')
                """, (character_id,))
            
            if should_close:
                conn.commit()
                conn.close()
            
            return True
            
        except Exception as e:
            print(f"[Proficiency] Error adding feat proficiencies: {e}")
            return False