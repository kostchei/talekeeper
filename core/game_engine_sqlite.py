"""
SQLite-based Game Engine for TaleKeeper Desktop

Replacement for IndexedDB-based engine using direct SQLite queries.
Provides the same interface and DTOs that the UI expects.
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from core.dtos import CharacterDTO, SaveSlotDTO
from models.character_indexeddb import Character


class GameEngineSQLite:
    def __init__(self, db_path: str = "talekeeper.db"):
        """Initialize SQLite game engine."""
        self.db_path = db_path
        self.current_character = None
        self.settings = {}
        self._load_settings()
        self._ensure_tables_exist()
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn
    
    def _safe_get_row_value(self, row: sqlite3.Row, key: str, default=None):
        """Safely get a value from sqlite3.Row with default fallback."""
        try:
            return row[key]
        except (IndexError, KeyError):
            return default
    
    def _load_settings(self):
        """Load application settings from SQLite or file."""
        try:
            # For now, use a simple file-based settings system
            settings_file = Path("settings.json")
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {}
        except Exception:
            self.settings = {}
    
    def save_settings(self):
        """Save application settings."""
        try:
            with open("settings.json", 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass
    
    def _ensure_tables_exist(self):
        """Ensure all required tables exist in the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create character_inventory table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_inventory (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                item_name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                weight_lb REAL NOT NULL DEFAULT 0.0,
                description TEXT,
                value_gp REAL NOT NULL DEFAULT 0,
                equipped INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        """)
        
        # Create index if it doesn't exist
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_character_inventory_character_id 
            ON character_inventory(character_id)
        """)
        
        conn.commit()
        conn.close()
    
    def load_character_sync(self, save_slot: int) -> Optional[CharacterDTO]:
        """Load character from save slot."""
        try:
            print(f"[SQLite] Loading character from slot {save_slot}")
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # First get the character data with save slot info
                cursor.execute("""
                    SELECT c.*, s.save_name, s.current_location, s.last_played
                    FROM characters c
                    JOIN save_slots s ON c.save_slot_id = s.id
                    WHERE s.slot_number = ?
                """, (save_slot,))
                
                character_row = cursor.fetchone()
                print(f"[SQLite] Found character row: {character_row is not None}")
                
                if not character_row:
                    print(f"[SQLite] No character found in slot {save_slot}")
                    # Check if save slot exists at all
                    cursor.execute("SELECT * FROM save_slots WHERE slot_number = ?", (save_slot,))
                    slot_row = cursor.fetchone()
                    print(f"[SQLite] Save slot {save_slot} exists: {slot_row is not None}")
                    if slot_row:
                        print(f"[SQLite] Slot data: occupied={slot_row['is_occupied']}, name={slot_row['character_name']}")
                    return None
                
                character_id = character_row['id']
                
                # Get character feats
                cursor.execute("""
                    SELECT feat_name, feat_source, level_acquired
                    FROM character_feats 
                    WHERE character_id = ?
                    ORDER BY level_acquired, feat_name
                """, (character_id,))
                feats_rows = cursor.fetchall()
                feats = [row['feat_name'] for row in feats_rows]
                
                # Get character proficiencies
                cursor.execute("""
                    SELECT proficiency_name, proficiency_type, source
                    FROM character_proficiencies
                    WHERE character_id = ?
                """, (character_id,))
                prof_rows = cursor.fetchall()
                proficiencies = [row['proficiency_name'] for row in prof_rows]
                
                # Get character features
                cursor.execute("""
                    SELECT feature_name, feature_type, usage_type, level_gained, description, mechanics
                    FROM character_features
                    WHERE character_id = ?
                """, (character_id,))
                feature_rows = cursor.fetchall()
                features = {}
                for row in feature_rows:
                    features[row['feature_name']] = {
                        'type': row['feature_type'],
                        'usage': row['usage_type'],
                        'level_gained': row['level_gained'],
                        'description': row['description'],
                        'mechanics': json.loads(row['mechanics']) if row['mechanics'] else {}
                    }
                
                # Get weapon masteries
                cursor.execute("""
                    SELECT weapon_name, mastery_type
                    FROM character_weapon_masteries
                    WHERE character_id = ?
                """, (character_id,))
                mastery_rows = cursor.fetchall()
                weapon_masteries = [row['weapon_name'] for row in mastery_rows]
                
                # Helper function to calculate ability modifier
                def calc_modifier(score):
                    return (score - 10) // 2
                
                # Parse datetime fields
                created_at = datetime.fromisoformat(character_row['created_at']) if character_row['created_at'] else datetime.now()
                updated_at = datetime.fromisoformat(character_row['updated_at']) if character_row['updated_at'] else None
                
                # Convert to CharacterDTO format expected by UI
                character_dto = CharacterDTO(
                    # Core Identity
                    id=character_row['id'],
                    name=character_row['name'],
                    level=character_row['level'],
                    experience_points=character_row['experience_points'],
                    
                    # Character Build
                    race_id=character_row['race_id'],
                    race_name=self._get_race_name(character_row['race_id']),
                    class_id=character_row['class_id'],
                    class_name=self._get_class_name(character_row['class_id']),
                    subclass_id=character_row['subclass_id'],
                    subclass_name=None,  # Not implemented yet
                    background_id=character_row['background_id'],
                    background_name=self._get_background_name(character_row['background_id']),
                    
                    # Ability scores
                    strength=character_row['strength'],
                    dexterity=character_row['dexterity'],
                    constitution=character_row['constitution'],
                    intelligence=character_row['intelligence'],
                    wisdom=character_row['wisdom'],
                    charisma=character_row['charisma'],
                    
                    # Ability modifiers (calculated)
                    strength_modifier=calc_modifier(character_row['strength']),
                    dexterity_modifier=calc_modifier(character_row['dexterity']),
                    constitution_modifier=calc_modifier(character_row['constitution']),
                    intelligence_modifier=calc_modifier(character_row['intelligence']),
                    wisdom_modifier=calc_modifier(character_row['wisdom']),
                    charisma_modifier=calc_modifier(character_row['charisma']),
                    
                    # Combat stats
                    armor_class=character_row['armor_class'],
                    hit_points_max=character_row['hit_points_max'],
                    hit_points_current=character_row['hit_points_current'],
                    hit_points_temporary=character_row['hit_points_temporary'],
                    hit_dice_max=character_row['hit_dice_max'],
                    hit_dice_current=character_row['hit_dice_current'],
                    death_saves_successes=character_row['death_saves_successes'],
                    death_saves_failures=character_row['death_saves_failures'],
                    conditions=[],  # Empty for now
                    
                    # Saving throw proficiencies (handle missing columns gracefully)
                    str_save_proficient=self._safe_get_row_value(character_row, 'str_save_proficient', 0),
                    dex_save_proficient=self._safe_get_row_value(character_row, 'dex_save_proficient', 0),
                    con_save_proficient=self._safe_get_row_value(character_row, 'con_save_proficient', 0),
                    int_save_proficient=self._safe_get_row_value(character_row, 'int_save_proficient', 0),
                    wis_save_proficient=self._safe_get_row_value(character_row, 'wis_save_proficient', 0),
                    cha_save_proficient=self._safe_get_row_value(character_row, 'cha_save_proficient', 0),
                    
                    # Character features from our migration
                    proficiencies=proficiencies,
                    features=features,
                    feats=feats,
                    weapon_masteries=weapon_masteries,
                    
                    # Resource tracking - initialize empty for now
                    spell_slots_current={},
                    spell_slots_max={},
                    class_resources={},
                    class_resources_max={},
                    
                    # Rest tracking
                    last_short_rest=character_row['last_short_rest'],
                    last_long_rest=character_row['last_long_rest'],
                    
                    # Ability usage - initialize empty for now
                    ability_uses={},
                    ability_uses_max={},
                    
                    # Equipment
                    equipment_main_hand=character_row['equipment_main_hand'],
                    equipment_off_hand=character_row['equipment_off_hand'],
                    equipment_armor=character_row['equipment_armor'],
                    equipment_shield=character_row['equipment_shield'],
                    
                    # Metadata
                    created_at=created_at,
                    updated_at=updated_at,
                    notes=character_row['notes'] or '',
                    
                    # Save Slot Info
                    save_slot_id=character_row['save_slot_id'],
                    save_slot_number=save_slot
                )
                
                # Feat effects should already be applied and stored in database during character creation
                # No need to apply them again during loading to avoid double application
                
                # Set current character
                self.current_character = character_dto
                return character_dto
                
        except Exception as e:
            print(f"Error loading character from slot {save_slot}: {e}")
            return None
    
    def get_save_slots_sync(self) -> List[SaveSlotDTO]:
        """Get all save slots."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM save_slots
                    ORDER BY slot_number
                """)
                
                slots = []
                for row in cursor.fetchall():
                    # Convert timestamp strings to datetime objects if needed
                    last_played = None
                    if row['last_played']:
                        try:
                            last_played = datetime.fromisoformat(row['last_played'])
                        except:
                            last_played = None
                    
                    created_at = None
                    if row['created_at']:
                        try:
                            created_at = datetime.fromisoformat(row['created_at'])
                        except:
                            created_at = datetime.now()
                    
                    slot_dto = SaveSlotDTO(
                        id=row['id'],
                        slot_number=row['slot_number'],
                        is_occupied=bool(row['is_occupied']),
                        save_name=row['save_name'],
                        last_played=last_played,
                        play_time_hours=row['play_time_minutes'] // 60,  # Convert minutes to hours
                        character_name=row['character_name'],
                        character_level=row['character_level'],
                        current_location=row['current_location'],
                        created_at=created_at
                    )
                    slots.append(slot_dto)
                
                return slots
                
        except Exception as e:
            print(f"Error loading save slots: {e}")
            return []
    
    def get_character_fighting_styles(self, character_id: str) -> List[str]:
        """Get character's fighting styles from character_features table."""
        try:
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT feature_name FROM character_features 
                WHERE character_id = ? AND feature_type = 'fighting_style'
            """, (character_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [row[0] for row in results]
            
        except Exception as e:
            print(f"Error getting fighting styles for character {character_id}: {e}")
            return []

    def get_character_inventory_sync(self, character_id: str) -> List[Dict[str, Any]]:
        """Get inventory items for a character."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT item_name, item_type, quantity, weight_lb, description, value_gp
                    FROM character_inventory
                    WHERE character_id = ?
                    ORDER BY item_type, item_name
                """, (character_id,))
                
                inventory = []
                for row in cursor.fetchall():
                    inventory.append({
                        'name': row['item_name'],
                        'type': row['item_type'],
                        'quantity': row['quantity'],
                        'weight_lb': row['weight_lb'],
                        'description': row['description'],
                        'value_gp': row['value_gp']
                    })
                
                return inventory
                
        except Exception as e:
            print(f"Error loading inventory for character {character_id}: {e}")
            return []
    
    def get_equipment_item_sync(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get equipment item data by name from database."""
        from services.equipment import equipment_service
        return equipment_service.get_item(item_name)
    
    def create_new_character_sync(self, character_data: Dict, save_slot: int) -> CharacterDTO:
        """Create a new character and save to database."""
        try:
            import uuid
            
            character_id = str(uuid.uuid4())
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if save slot exists and get its ID
                cursor.execute("SELECT id, is_occupied FROM save_slots WHERE slot_number = ?", (save_slot,))
                slot_row = cursor.fetchone()
                
                if slot_row:
                    # Slot exists - update it
                    save_slot_id = slot_row['id']
                    if slot_row['is_occupied']:
                        # Delete existing character first
                        cursor.execute("DELETE FROM characters WHERE save_slot_id = ?", (save_slot_id,))
                    
                    cursor.execute("""
                        UPDATE save_slots 
                        SET is_occupied = ?, save_name = ?, character_name = ?,
                            character_level = ?, current_location = ?, updated_at = ?
                        WHERE slot_number = ?
                    """, (
                        True, f"{character_data['name']}'s Adventure",
                        character_data['name'], character_data.get('level', 1),
                        'Starting Town', datetime.now().isoformat(), save_slot
                    ))
                else:
                    # Slot doesn't exist - create new one
                    save_slot_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO save_slots (
                            id, slot_number, is_occupied, save_name, character_name,
                            character_level, current_location, play_time_minutes,
                            created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        save_slot_id, save_slot, True, f"{character_data['name']}'s Adventure",
                        character_data['name'], character_data.get('level', 1),
                        'Starting Town', 0, datetime.now().isoformat()
                    ))
                
                # Debug equipment before saving
                print(f"[SQLite] Creating character with equipment:")
                print(f"  Main hand: {character_data.get('equipment_main_hand')}")
                print(f"  Armor: {character_data.get('equipment_armor')}")  
                print(f"  AC: {character_data.get('armor_class')}")
                
                # Create character
                cursor.execute("""
                    INSERT INTO characters (
                        id, save_slot_id, name, race_id, class_id, background_id, level,
                        experience_points, strength, dexterity, constitution, intelligence,
                        wisdom, charisma, armor_class, hit_points_max, hit_points_current,
                        hit_points_temporary, max_hit_points, current_hit_points,
                        hit_dice_max, hit_dice_current, death_saves_successes,
                        death_saves_failures, equipment_main_hand, equipment_off_hand,
                        equipment_armor, equipment_shield, str_save_proficient,
                        dex_save_proficient, con_save_proficient, int_save_proficient,
                        wis_save_proficient, cha_save_proficient, created_at, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    character_id, save_slot_id, character_data['name'],
                    character_data['race_id'], character_data['class_id'], character_data['background_id'],
                    character_data.get('level', 1), character_data.get('experience_points', 0),
                    character_data['strength'], character_data['dexterity'], character_data['constitution'],
                    character_data['intelligence'], character_data['wisdom'], character_data['charisma'],
                    character_data.get('armor_class', 10), character_data['hit_points_max'],
                    character_data['hit_points_current'], character_data.get('hit_points_temporary', 0),
                    character_data['hit_points_max'], character_data['hit_points_current'],
                    character_data.get('hit_dice_max', 1), character_data.get('hit_dice_current', 1),
                    0, 0,  # death saves
                    character_data.get('equipment_main_hand'), character_data.get('equipment_off_hand'),
                    character_data.get('equipment_armor'), character_data.get('equipment_shield'),
                    character_data.get('str_save_proficient', 0), character_data.get('dex_save_proficient', 0),
                    character_data.get('con_save_proficient', 0), character_data.get('int_save_proficient', 0),
                    character_data.get('wis_save_proficient', 0), character_data.get('cha_save_proficient', 0),
                    datetime.now().isoformat(), character_data.get('notes', '')
                ))
                
                # Insert feats
                for feat_name in character_data.get('feats', []):
                    cursor.execute("""
                        INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
                        VALUES (?, ?, ?, ?)
                    """, (character_id, feat_name, 'character_creation', character_data.get('level', 1)))
                
                # Insert proficiencies
                for prof in character_data.get('proficiencies', []):
                    cursor.execute("""
                        INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
                        VALUES (?, ?, ?, ?)
                    """, (character_id, 'skill', prof, 'character_creation'))
                
                # Insert features
                for feature_name, feature_data in character_data.get('features', {}).items():
                    cursor.execute("""
                        INSERT INTO character_features (
                            character_id, feature_name, feature_type, usage_type,
                            level_gained, description, mechanics
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        character_id, feature_name,
                        feature_data.get('type', 'passive'),
                        feature_data.get('usage', 'permanent'),
                        feature_data.get('level_gained', 1),
                        feature_data.get('description', ''),
                        json.dumps(feature_data.get('mechanics', {}))
                    ))
                    
                    # Extract weapon masteries from Weapon Mastery feature
                    if feature_name == 'Weapon Mastery' and 'selected_weapons' in feature_data:
                        selected_weapons = feature_data['selected_weapons']
                        weapon_mastery_map = {
                            "Dagger": "Nick", "Handaxe": "Vex", "Javelin": "Slow",
                            "Light Hammer": "Nick", "Scimitar": "Nick", "Shortsword": "Vex",
                            "Battleaxe": "Topple", "Flail": "Sap", "Glaive": "Graze",
                            "Greataxe": "Cleave", "Greatsword": "Graze", "Halberd": "Cleave",
                            "Lance": "Topple", "Longsword": "Sap", "Maul": "Topple",
                            "Morningstar": "Sap", "Pike": "Push", "Rapier": "Vex",
                            "Trident": "Topple", "War Pick": "Sap", "Warhammer": "Push", "Whip": "Slow"
                        }
                        
                        for weapon_name in selected_weapons:
                            mastery_type = weapon_mastery_map.get(weapon_name)
                            if mastery_type:
                                cursor.execute("""
                                    INSERT INTO character_weapon_masteries (character_id, weapon_name, mastery_type)
                                    VALUES (?, ?, ?)
                                """, (character_id, weapon_name, mastery_type.lower()))
                                print(f"[SQLite] Added weapon mastery: {weapon_name} -> {mastery_type}")
                
                # Add starting equipment from class and background
                self._add_starting_equipment(cursor, character_id, character_data)
                
                conn.commit()
                print(f"[SQLite] Created new character '{character_data['name']}' in slot {save_slot}")
            
            # Load and return the created character (with a fresh connection after commit)
            import time
            time.sleep(0.1)  # Brief delay to ensure transaction is fully committed
            
            created_character = self.load_character_sync(save_slot)
            if created_character is None:
                raise RuntimeError(f"Failed to load character after creation in slot {save_slot}")
            
            return created_character
                
        except Exception as e:
            print(f"Error creating character: {e}")
            raise e
    
    def save_game_sync(self):
        """Save current game state."""
        # Placeholder for saving game state
        if self.current_character:
            print(f"Would save game state for {self.current_character.name}")
    
    def delete_character_sync(self, save_slot: int) -> bool:
        """Delete character from save slot."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Find the character in this slot
                cursor.execute("""
                    SELECT c.id FROM characters c
                    JOIN save_slots s ON c.save_slot_id = s.id
                    WHERE s.slot_number = ?
                """, (save_slot,))
                
                character_row = cursor.fetchone()
                if not character_row:
                    return False
                
                character_id = character_row['id']
                
                # Delete character (cascade will handle related records)
                cursor.execute("DELETE FROM characters WHERE id = ?", (character_id,))
                
                # Update save slot to mark as unoccupied
                cursor.execute("""
                    UPDATE save_slots 
                    SET is_occupied = 0, character_name = NULL, character_level = NULL
                    WHERE slot_number = ?
                """, (save_slot,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error deleting character from slot {save_slot}: {e}")
            return False
    
    def _get_race_name(self, race_id: str) -> str:
        """Get display name for race."""
        # Map race IDs to display names
        race_names = {
            'Human': 'Human',
            'human': 'Human',
            'Elf': 'Elf',
            'elf': 'Elf',
            'Dwarf': 'Dwarf',
            'dwarf': 'Dwarf',
            'Halfling': 'Halfling',
            'halfling': 'Halfling'
        }
        return race_names.get(race_id, race_id)
    
    def _get_class_name(self, class_id: str) -> str:
        """Get display name for class."""
        # Map class IDs to display names
        class_names = {
            'fighter': 'Fighter',
            'Fighter': 'Fighter',
            'rogue': 'Rogue',
            'Rogue': 'Rogue',
            'wizard': 'Wizard',
            'Wizard': 'Wizard',
            'cleric': 'Cleric',
            'Cleric': 'Cleric'
        }
        return class_names.get(class_id, class_id.title())
    
    def _get_background_name(self, background_id: str) -> str:
        """Get display name for background from database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM backgrounds WHERE name = ? COLLATE NOCASE", (background_id,))
            row = cursor.fetchone()
            conn.close()
            return row['name'] if row else background_id
        except:
            return background_id
    
    # Placeholder methods for compatibility with existing UI code
    def get_available_races_sync(self):
        """Get available races - placeholder."""
        return []
    
    def get_available_classes_sync(self):
        """Get available classes - placeholder."""
        return []
    
    def get_available_backgrounds_sync(self):
        """Get available backgrounds from database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM backgrounds ORDER BY name")
            backgrounds = []
            for row in cursor.fetchall():
                # Create a simple object with name and id attributes
                class BackgroundInfo:
                    def __init__(self, name):
                        self.name = name
                        self.id = name
                backgrounds.append(BackgroundInfo(row['name']))
            conn.close()
            return backgrounds
        except Exception as e:
            print(f"Error loading backgrounds: {e}")
            return []
    
    def get_class_equipment_choices_sync(self, class_id: str):
        """Get equipment choices for a specific class from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT choice_group, choice_name, options
                FROM class_equipment_choices
                WHERE class_id = ?
                ORDER BY choice_group
            """, (class_id.lower(),))
            
            choices = []
            for choice_group, choice_name, options_json in cursor.fetchall():
                choices.append({
                    'group': choice_group,
                    'name': choice_name,
                    'options': json.loads(options_json)
                })
            
            conn.close()
            return choices
            
        except Exception as e:
            print(f"[SQLite] Error getting equipment choices for {class_id}: {e}")
            return []
    
    def apply_equipment_choices_sync(self, character_data, equipment_choices):
        """Apply equipment choices made during character creation."""
        print(f"[SQLite] apply_equipment_choices_sync called with: {equipment_choices}")
        if not equipment_choices:
            print("[SQLite] No equipment choices provided")
            return
        
        # Process all equipment choices dynamically
        for choice_key, item_name in equipment_choices.items():
            print(f"[SQLite] Processing choice '{choice_key}': {item_name}")
            
            # Handle weapon choices
            if 'weapon' in choice_key.lower() or choice_key in ['Martial Weapon', 'Primary Weapon', 'Simple Weapon']:
                # Check if it's a secondary weapon
                if 'secondary' in choice_key.lower():
                    character_data['equipment_off_hand'] = item_name
                    print(f"[SQLite] Applied secondary weapon: {item_name}")
                else:
                    character_data['equipment_main_hand'] = item_name
                    print(f"[SQLite] Applied primary weapon: {item_name}")
            
            # Handle armor choices
            elif 'armor' in choice_key.lower() or choice_key == 'Armor':
                character_data['equipment_armor'] = item_name
                print(f"[SQLite] Applied armor choice: {item_name}")
                # AC will be calculated when the armor is equipped in the UI
    
    def _apply_feat_effects_to_character(self, character_dto: CharacterDTO, feats: List[str]) -> CharacterDTO:
        """Apply mechanical effects of feats to character stats."""
        modified_dto = character_dto
        
        for feat_name in feats:
            if feat_name == "Tough":
                # Tough feat: +2 HP per level
                bonus_hp = 2 * modified_dto.level
                modified_dto.hit_points_max += bonus_hp
                modified_dto.hit_points_current += bonus_hp  # Also increase current if at max
                print(f"[SQLite] Applied Tough feat: +{bonus_hp} HP to {modified_dto.name}")
            
            elif feat_name == "Linguist":
                # Linguist feat: +1 Intelligence
                modified_dto.intelligence += 1
                modified_dto.intelligence_modifier = (modified_dto.intelligence - 10) // 2
                print(f"[SQLite] Applied Linguist feat: +1 INT to {modified_dto.name}")
            
            # Note: Fighting style feats like "Great Weapon Fighting" are passive and 
            # don't modify base stats - they're handled by the action system
            elif feat_name in ["Great Weapon Fighting", "Dueling", "Archery", "Defense"]:
                print(f"[SQLite] Fighting style feat '{feat_name}' noted (passive effect)")
        
        return modified_dto
    
    def _add_starting_equipment(self, cursor, character_id: str, character_data: Dict):
        """Add starting equipment based on class and background."""
        import uuid
        
        class_id = character_data.get('class_id', '').lower()
        background_id = character_data.get('background_id', '').lower()
        equipment_choices = character_data.get('equipment_choices', {})
        
        print(f"[SQLite] Adding starting equipment for class '{class_id}' background '{background_id}'")
        
        # First, add equipment from character creation choices
        if equipment_choices:
            print(f"[SQLite] Adding equipment from character creation choices: {equipment_choices}")
            
            # Use equipment service instead of hardcoded data
            from services.equipment import equipment_service
            
            # Process each equipment choice
            for choice_key, item_name in equipment_choices.items():
                equipment_data = equipment_service.get_item(item_name)
                if equipment_data:
                    # Get item properties from database
                    item_type = equipment_data['item_type']
                    weight_lb = equipment_data['weight_lb']
                    description = equipment_data['description'] or ''
                    value_gp = equipment_data['cost_gp']
                    
                    # Determine if equipped based on choice type
                    equipped = 1 if any(key in choice_key.lower() for key in ['weapon', 'armor', 'shield']) else 0
                    
                    cursor.execute("""
                        INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (str(uuid.uuid4()), character_id, item_name, item_type, 1, weight_lb, description, value_gp, equipped))
                    print(f"[SQLite] Added {item_name} to inventory (from {choice_key}) - equipped: {equipped}")
                    
                    # Handle shield separately if it's part of a weapon choice
                    if 'Shield' in item_name and item_type != 'shield':
                        shield_data = equipment_service.get_item('Shield')
                        if shield_data:
                            cursor.execute("""
                                INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (str(uuid.uuid4()), character_id, 'Shield', 'shield', 1, shield_data['weight_lb'], shield_data['description'], shield_data['cost_gp'], 1))
                            print(f"[SQLite] Also added Shield from {item_name}")
                else:
                    print(f"[SQLite] Warning: Equipment '{item_name}' not found in database")
        
        # Fighter Class Starting Equipment
        if class_id in ['fighter']:
            equipment_items = [
                # Combat gear
                ('Javelin', 'weapon', 4, 2.0, 'Simple thrown weapon (range 30/120)', 5),
                ('Handaxe', 'weapon', 2, 2.0, 'Light, thrown weapon (range 20/60)', 5),
                # Adventuring gear
                ('Dungeoneer\'s Pack', 'gear', 1, 61.0, 'Includes backpack, crowbar, hammer, 10 pitons, 10 torches, tinderbox, 10 days rations, waterskin, 50 ft hemp rope', 12),
                ('Explorer\'s Pack', 'gear', 1, 59.0, 'Includes backpack, bedroll, mess kit, tinderbox, 10 torches, 10 days rations, waterskin, 50 ft hemp rope', 10),
            ]
            
            for item_name, item_type, quantity, weight_lb, description, value_gp in equipment_items:
                cursor.execute("""
                    INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), character_id, item_name, item_type, quantity, weight_lb, description, value_gp))
        
        # Background Equipment (direct database query)
        print(f"[SQLite] Loading background equipment for '{background_id}'")
        
        # Query background directly from database
        cursor.execute("""
            SELECT equipment_option_a, equipment_option_a_gold FROM backgrounds WHERE name = ? COLLATE NOCASE
        """, (background_id,))
        
        background_row = cursor.fetchone()
        if background_row:
            background_equipment = json.loads(background_row['equipment_option_a'])
            background_gold = background_row['equipment_option_a_gold']
            
            print(f"[SQLite] Adding {len(background_equipment)} items from {background_id} background")
            
            # Use equipment service to get proper item data
            from services.equipment import equipment_service
            
            for equipment_name in background_equipment:
                # Try to get item data from equipment database
                equipment_data = equipment_service.get_item(equipment_name)
                
                if equipment_data:
                    # Use database equipment data
                    item_type = equipment_data['item_type']
                    weight_lb = equipment_data['weight_lb'] 
                    description = equipment_data['description'] or ''
                    value_gp = equipment_data['cost_gp']
                    quantity = 1
                    
                    # Handle special quantity items (like arrows_20, rations_5)
                    if '_' in equipment_name and equipment_name.split('_')[-1].isdigit():
                        quantity = int(equipment_name.split('_')[-1])
                        equipment_name = equipment_name.rsplit('_', 1)[0]  # Remove quantity suffix
                    
                else:
                    # Fallback for items not in equipment database
                    item_type = 'gear'
                    weight_lb = 1.0
                    description = f'{equipment_name} (background equipment)'
                    value_gp = 1
                    quantity = 1
                    print(f"[SQLite] Warning: '{equipment_name}' not found in equipment database, using fallback")
                
                cursor.execute("""
                    INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), character_id, equipment_name, item_type, quantity, weight_lb, description, value_gp))
                print(f"[SQLite] Added background item: {equipment_name} (x{quantity})")
            
            # Add starting gold from background
            if background_gold > 0:
                cursor.execute("""
                    INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), character_id, 'Gold Pieces', 'treasure', background_gold, 0.02, 'Starting money from background', 1))
                print(f"[SQLite] Added {background_gold} gold pieces from {background_id} background")
        else:
            print(f"[SQLite] Warning: Background '{background_id}' not found in database")
        
        # Universal starting equipment (everyone gets these)
        universal_equipment = [
            ('Rations (1 day)', 'gear', 2, 2.0, 'One day worth of travel rations', 2),
            ('Waterskin', 'gear', 1, 5.0, 'Holds 4 pints of liquid', 2),
        ]
        
        for item_name, item_type, quantity, weight_lb, description, value_gp in universal_equipment:
            cursor.execute("""
                INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), character_id, item_name, item_type, quantity, weight_lb, description, value_gp))
        
        print(f"[SQLite] Added starting equipment for {class_id} {background_id}")
    
    def _get_weapon_stats(self, weapon_name: str) -> Dict[str, Any]:
        """Get weapon stats for inventory."""
        weapon_stats = {
            'Longsword': {'weight': 3.0, 'description': 'Versatile (1d8/1d10), martial weapon', 'value': 15},
            'Greatsword': {'weight': 6.0, 'description': 'Two-handed (2d6), martial weapon', 'value': 50},
            'Rapier': {'weight': 2.0, 'description': 'Finesse (1d8), martial weapon', 'value': 25},
            'Scimitar': {'weight': 3.0, 'description': 'Finesse, light (1d6), martial weapon', 'value': 25},
            'Shortsword': {'weight': 2.0, 'description': 'Finesse, light (1d6), martial weapon', 'value': 10},
            'Handaxe': {'weight': 2.0, 'description': 'Light, thrown (1d6), simple weapon', 'value': 5},
            'Javelin': {'weight': 2.0, 'description': 'Thrown (1d6), simple weapon', 'value': 5},
            'Dagger': {'weight': 1.0, 'description': 'Finesse, light, thrown (1d4)', 'value': 2},
        }
        return weapon_stats.get(weapon_name, {'weight': 1.0, 'description': 'Weapon', 'value': 1})
    
    def _get_armor_stats(self, armor_name: str) -> Dict[str, Any]:
        """Get armor stats for inventory."""
        armor_stats = {
            'Chain Mail': {'weight': 55.0, 'description': 'Heavy armor, AC 16', 'value': 75},
            'Breastplate': {'weight': 20.0, 'description': 'Medium armor, AC 14 + Dex mod (max 2)', 'value': 400},
            'Studded Leather': {'weight': 13.0, 'description': 'Light armor, AC 11 + Dex mod', 'value': 45},
            'Leather Armor': {'weight': 10.0, 'description': 'Light armor, AC 11 + Dex mod', 'value': 10},
        }
        return armor_stats.get(armor_name, {'weight': 10.0, 'description': 'Armor', 'value': 10})
    
    def update_character_hp_sync(self, current_hp: int, max_hp: int = None):
        """Update character's HP in database."""
        if not self.current_character:
            print("[SQLite] No current character to update HP")
            return
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Update HP values
                if max_hp is not None:
                    # Update both current and max HP
                    cursor.execute("""
                        UPDATE characters 
                        SET hit_points_current = ?, hit_points_max = ?, max_hit_points = ?, updated_at = ?
                        WHERE id = ?
                    """, (current_hp, max_hp, max_hp, datetime.now().isoformat(), self.current_character.id))
                    
                    # Also update the current character DTO
                    self.current_character.hit_points_current = current_hp
                    self.current_character.hit_points_max = max_hp
                    
                    print(f"[SQLite] Updated {self.current_character.name} HP: {current_hp}/{max_hp}")
                else:
                    # Update only current HP
                    cursor.execute("""
                        UPDATE characters 
                        SET hit_points_current = ?, updated_at = ?
                        WHERE id = ?
                    """, (current_hp, datetime.now().isoformat(), self.current_character.id))
                    
                    # Update the current character DTO
                    self.current_character.hit_points_current = current_hp
                    
                    print(f"[SQLite] Updated {self.current_character.name} current HP: {current_hp}/{self.current_character.hit_points_max}")
                
                conn.commit()
                
        except Exception as e:
            print(f"[SQLite] Error updating character HP: {e}")