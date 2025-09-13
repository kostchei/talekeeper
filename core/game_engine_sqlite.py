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
from services.proficiency_system import ProficiencySystem

# DTOs no longer needed - using direct dictionaries from SQL queries


class GameEngineSQLite:
    def __init__(self, db_path: str = "talekeeper.db"):
        """Initialize SQLite game engine."""
        self.db_path = db_path
        self.current_character = None
        self.settings = {}
        self._load_settings()
        self._ensure_tables_exist()
        self.proficiency_system = ProficiencySystem(db_path)
        
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
    
    def load_character_sync(self, save_slot: int) -> Optional[Dict[str, Any]]:
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
                    # Parse mechanics JSON safely
                    mechanics = {}
                    if row['mechanics']:
                        try:
                            mechanics = json.loads(row['mechanics'])
                        except json.JSONDecodeError:
                            print(f"[Warning] Invalid JSON in mechanics for feature {row['feature_name']}: {row['mechanics']}")
                            mechanics = {}
                    
                    features[row['feature_name']] = {
                        'type': row['feature_type'],
                        'usage': row['usage_type'],
                        'level_gained': row['level_gained'],
                        'description': row['description'],
                        'mechanics': mechanics
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
                
                # Recalculate AC to ensure it's current (handles existing characters created before AC fix)
                current_ac = self._calculate_armor_class(
                    character_id,
                    character_row['strength'],
                    character_row['dexterity'], 
                    character_row['constitution'],
                    character_row['class_id']
                )
                
                # Update database if AC has changed
                if current_ac != character_row['armor_class']:
                    cursor.execute("""
                        UPDATE characters SET armor_class = ?, updated_at = ?
                        WHERE id = ?
                    """, (current_ac, datetime.now().isoformat(), character_id))
                    conn.commit()
                    print(f"[SQLite] Updated AC for {character_row['name']}: {character_row['armor_class']} -> {current_ac}")
                
                # Parse datetime fields
                created_at = datetime.fromisoformat(character_row['created_at']) if character_row['created_at'] else datetime.now()
                updated_at = datetime.fromisoformat(character_row['updated_at']) if character_row['updated_at'] else None
                
                # Convert to dictionary format expected by UI
                character_dict = {
                    # Core Identity
                    'id': character_row['id'],
                    'name': character_row['name'],
                    'level': character_row['level'],
                    'experience_points': character_row['experience_points'],
                    
                    # Character Build
                    'race_id': character_row['race_id'],
                    'race_name': self._get_race_name(character_row['race_id']),
                    'class_id': character_row['class_id'],
                    'class_name': self._get_class_name(character_row['class_id']),
                    'subclass_id': character_row['subclass_id'],
                    'subclass_name': None,  # Not implemented yet
                    'background_id': character_row['background_id'],
                    'background_name': self._get_background_name(character_row['background_id']),
                    
                    # Ability scores
                    'strength': character_row['strength'],
                    'dexterity': character_row['dexterity'],
                    'constitution': character_row['constitution'],
                    'intelligence': character_row['intelligence'],
                    'wisdom': character_row['wisdom'],
                    'charisma': character_row['charisma'],
                    
                    # Ability modifiers (calculated)
                    'strength_modifier': calc_modifier(character_row['strength']),
                    'dexterity_modifier': calc_modifier(character_row['dexterity']),
                    'constitution_modifier': calc_modifier(character_row['constitution']),
                    'intelligence_modifier': calc_modifier(character_row['intelligence']),
                    'wisdom_modifier': calc_modifier(character_row['wisdom']),
                    'charisma_modifier': calc_modifier(character_row['charisma']),
                    
                    # Combat stats
                    'armor_class': current_ac,
                    'hit_points_max': character_row['hit_points_max'],
                    'hit_points_current': character_row['hit_points_current'],
                    'hit_points_temporary': character_row['hit_points_temporary'],
                    'hit_dice_max': character_row['hit_dice_max'],
                    'hit_dice_current': character_row['hit_dice_current'],
                    'death_saves_successes': character_row['death_saves_successes'],
                    'death_saves_failures': character_row['death_saves_failures'],
                    'conditions': [],  # Empty for now
                    
                    # Saving throw proficiencies (handle missing columns gracefully)
                    'str_save_proficient': self._safe_get_row_value(character_row, 'str_save_proficient', 0),
                    'dex_save_proficient': self._safe_get_row_value(character_row, 'dex_save_proficient', 0),
                    'con_save_proficient': self._safe_get_row_value(character_row, 'con_save_proficient', 0),
                    'int_save_proficient': self._safe_get_row_value(character_row, 'int_save_proficient', 0),
                    'wis_save_proficient': self._safe_get_row_value(character_row, 'wis_save_proficient', 0),
                    'cha_save_proficient': self._safe_get_row_value(character_row, 'cha_save_proficient', 0),
                    
                    # Character features from our migration
                    'proficiencies': proficiencies,
                    'features': features,
                    'feats': feats,
                    'weapon_masteries': weapon_masteries,
                    
                    # Resource tracking - initialize empty for now
                    'spell_slots_current': {},
                    'spell_slots_max': {},
                    'class_resources': {},
                    'class_resources_max': {},
                    
                    # Lucky/Inspiration resources (new advantage system)
                    'lucky_uses_current': self._safe_get_row_value(character_row, 'lucky_uses_current', 0),
                    'lucky_uses_max': self._safe_get_row_value(character_row, 'lucky_uses_max', 0),
                    'inspiration_uses_current': self._safe_get_row_value(character_row, 'inspiration_uses_current', 0),
                    'inspiration_uses_max': self._safe_get_row_value(character_row, 'inspiration_uses_max', 0),
                    
                    # Rest tracking
                    'last_short_rest': character_row['last_short_rest'],
                    'last_long_rest': character_row['last_long_rest'],
                    
                    # Ability usage - initialize empty for now
                    'ability_uses': {},
                    'ability_uses_max': {},
                    
                    # Equipment
                    'equipment_main_hand': character_row['equipment_main_hand'],
                    'equipment_off_hand': character_row['equipment_off_hand'],
                    'equipment_armor': character_row['equipment_armor'],
                    'equipment_shield': character_row['equipment_shield'],
                    
                    # Metadata
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'notes': character_row['notes'] or '',
                    
                    # Save Slot Info
                    'save_slot_id': character_row['save_slot_id'],
                    'save_slot_number': save_slot
                }
                
                # Feat effects should already be applied and stored in database during character creation
                # No need to apply them again during loading to avoid double application
                
                # Check and initialize character resources if missing (for existing characters)
                try:
                    from services.character_resources import CharacterResourceService
                    resource_service = CharacterResourceService(self.db_path)
                    
                    # Check if character has resources
                    existing_resources = resource_service.get_character_resources(character_id)
                    
                    # If no resources exist, initialize them based on class
                    if not existing_resources:
                        level = character_dict.get('level', 1)
                        class_name = character_dict.get('class_name', '')
                        
                        if class_name == 'Fighter':
                            result = resource_service.initialize_fighter_resources(character_id, level)
                            print(f"[SQLite] Initialized missing Fighter resources for existing character: {result['resources_added']}")
                        elif class_name == 'Barbarian':
                            result = resource_service.initialize_barbarian_resources(character_id, level)
                            print(f"[SQLite] Initialized missing Barbarian resources for existing character: {result['resources_added']}")
                    
                except Exception as e:
                    print(f"[SQLite] Warning: Failed to check/initialize character resources: {e}")
                
                # Set current character
                self.current_character = character_dict
                return character_dict
                
        except Exception as e:
            print(f"Error loading character from slot {save_slot}: {e}")
            return None
    
    def get_character_by_id_sync(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Load character by character ID."""
        try:
            print(f"[SQLite] Loading character by ID: {character_id}")
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get the character data with save slot info
                cursor.execute("""
                    SELECT c.*, s.save_name, s.current_location, s.last_played, s.slot_number
                    FROM characters c
                    JOIN save_slots s ON c.save_slot_id = s.id
                    WHERE c.id = ?
                """, (character_id,))
                
                character_row = cursor.fetchone()
                if not character_row:
                    print(f"[SQLite] No character found with ID {character_id}")
                    return None
                
                # Get the save slot and reload using the existing method
                slot_number = character_row['slot_number']
                return self.load_character_sync(slot_number)
                
        except Exception as e:
            print(f"[SQLite] Error loading character by ID {character_id}: {e}")
            return None
    
    def get_save_slots_sync(self) -> List[Dict[str, Any]]:
        """Get all save slots."""
        try:
            # Clean up orphaned slots first
            self._cleanup_orphaned_slots()
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.*, c.class_id, c.level as actual_level
                    FROM save_slots s
                    LEFT JOIN characters c ON s.id = c.save_slot_id
                    ORDER BY s.slot_number
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
                    
                    slot_dict = {
                        'id': row['id'],
                        'slot_number': row['slot_number'],
                        'is_occupied': bool(row['is_occupied']),
                        'save_name': row['save_name'],
                        'last_played': last_played,
                        'play_time_hours': row['play_time_minutes'] // 60,  # Convert minutes to hours
                        'character_name': row['character_name'],
                        'character_level': row['actual_level'] if row['actual_level'] is not None else row['character_level'],
                        'character_class': row['class_id'] if row['class_id'] else '',
                        'current_location': row['current_location'],
                        'created_at': created_at
                    }
                    slots.append(slot_dict)
                
                return slots
                
        except Exception as e:
            print(f"Error loading save slots: {e}")
            return []
    
    def _cleanup_orphaned_slots(self):
        """Clean up save slots that are marked as occupied but have no character."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Update orphaned slots to be unoccupied
                cursor.execute("""
                    UPDATE save_slots 
                    SET is_occupied = 0, character_name = NULL, character_level = NULL 
                    WHERE is_occupied = 1 
                    AND id NOT IN (SELECT DISTINCT save_slot_id FROM characters WHERE save_slot_id IS NOT NULL)
                """)
                
                orphaned_count = cursor.rowcount
                if orphaned_count > 0:
                    print(f"[SQLite] Cleaned up {orphaned_count} orphaned save slots")
                
                conn.commit()
                
        except Exception as e:
            print(f"Error cleaning up orphaned slots: {e}")
    
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
    
    def create_new_character_sync(self, character_data: Dict, save_slot: int) -> Dict[str, Any]:
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
                
                # Calculate proper AC based on class features and equipment
                calculated_ac = self._calculate_armor_class(
                    character_id, 
                    character_data['strength'], 
                    character_data['dexterity'], 
                    character_data['constitution'], 
                    character_data['class_id']
                )
                print(f"  Calculated AC: {calculated_ac}")
                
                # Create character
                cursor.execute("""
                    INSERT INTO characters (
                        id, save_slot_id, name, race_id, class_id, background_id, level,
                        experience_points, strength, dexterity, constitution, intelligence,
                        wisdom, charisma, armor_class, hit_points_max, hit_points_current,
                        hit_points_temporary, max_hit_points, current_hit_points,
                        hit_dice_max, hit_dice_current, death_saves_successes,
                        death_saves_failures, equipment_main_hand, equipment_off_hand,
                        equipment_armor, equipment_shield, created_at, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    character_id, save_slot_id, character_data['name'],
                    character_data['race_id'], character_data['class_id'], character_data['background_id'],
                    character_data.get('level', 1), character_data.get('experience_points', 0),
                    character_data['strength'], character_data['dexterity'], character_data['constitution'],
                    character_data['intelligence'], character_data['wisdom'], character_data['charisma'],
                    calculated_ac, character_data['hit_points_max'],
                    character_data['hit_points_current'], character_data.get('hit_points_temporary', 0),
                    character_data['hit_points_max'], character_data['hit_points_current'],
                    character_data.get('hit_dice_max', 1), character_data.get('hit_dice_current', 1),
                    0, 0,  # death saves
                    character_data.get('equipment_main_hand'), character_data.get('equipment_off_hand'),
                    character_data.get('equipment_armor'), character_data.get('equipment_shield'),
                    datetime.now().isoformat(), character_data.get('notes', '')
                ))
                
                # Insert feats
                for feat_name in character_data.get('feats', []):
                    cursor.execute("""
                        INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
                        VALUES (?, ?, ?, ?)
                    """, (character_id, feat_name, 'character_creation', character_data.get('level', 1)))
                
                # Initialize proficiencies using the proficiency system (pass the connection)
                selected_class_skills = character_data.get('selected_class_skills', [])
                selected_species_skills = character_data.get('selected_species_skills', [])
                
                # Combine all selected skills
                all_selected_skills = selected_class_skills + selected_species_skills
                
                self.proficiency_system.initialize_character_proficiencies(
                    character_id, 
                    character_data['class_id'],
                    character_data.get('background_id'),
                    character_data.get('race_id'),
                    selected_skills=all_selected_skills,
                    conn=conn
                )
                
                # Add any additional skill proficiencies from character creation
                for prof in character_data.get('proficiencies', []):
                    self.proficiency_system.add_proficiency(character_id, 'skill', prof, 'character_creation', conn=conn)
                
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
                
                # Initialize class-specific features table (old system)
                self._initialize_class_features(cursor, character_id, character_data)
                
                # Initialize features using new feature system
                try:
                    from core.feature_integration import FeatureSystemIntegration
                    feature_system = FeatureSystemIntegration(self.db_path)
                    feature_system.initialize_character_features(character_id)
                    print(f"[SQLite] Initialized new feature system for character {character_id}")
                except Exception as e:
                    print(f"[SQLite] Warning: Failed to initialize new feature system: {e}")
                
                # Initialize character resources (Second Wind, Action Surge, etc.)
                try:
                    from services.character_resources import CharacterResourceService
                    resource_service = CharacterResourceService(self.db_path)
                    
                    # Initialize resources based on class
                    if character_data['class_id'] == 'fighter':
                        result = resource_service.initialize_fighter_resources(character_id, character_data.get('level', 1))
                        print(f"[SQLite] Initialized Fighter resources: {result['resources_added']}")
                    elif character_data['class_id'] == 'barbarian':
                        result = resource_service.initialize_barbarian_resources(character_id, character_data.get('level', 1))
                        print(f"[SQLite] Initialized Barbarian resources: {result['resources_added']}")
                    # Add other class resource initialization here as needed
                    
                except Exception as e:
                    print(f"[SQLite] Warning: Failed to initialize character resources: {e}")
                
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
        if self.current_character:
            success = self.save_character_sync()
            if success:
                print(f"[SQLite] Saved game state for {self.current_character['name']}")
                return True
            else:
                print(f"[SQLite] Failed to save game state for {self.current_character['name']}")
                return False
        else:
            print("[SQLite] No current character to save")
            return False
    
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
                    # Silently return False for empty slots (no error logging)
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
                print(f"[SQLite] Deleted character from slot {save_slot}")
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
        """Get available races from database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM races ORDER BY display_order, name")
        races = []
        for row in cursor.fetchall():
            # Create a simple race-like object with id and name
            class RaceData:
                def __init__(self, id, name):
                    self.id = id
                    self.name = name
            races.append(RaceData(row['id'], row['name']))
        conn.close()
        
        if not races:
            raise ValueError("No races found in database - check races table")
        
        return races
    
    def get_available_classes_sync(self):
        """Get available classes from database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM classes ORDER BY name")
            classes = []
            for row in cursor.fetchall():
                # Create a simple class-like object with id and name
                class ClassData:
                    def __init__(self, id, name):
                        self.id = id
                        self.name = name
                classes.append(ClassData(row['id'], row['name']))
            conn.close()
            return classes
        except Exception as e:
            print(f"Error loading classes: {e}")
            return []
    
    def get_available_backgrounds_sync(self):
        """Get available backgrounds from database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM backgrounds ORDER BY name")
            backgrounds = []
            for row in cursor.fetchall():
                # Create a simple object with name and id attributes
                class BackgroundInfo:
                    def __init__(self, id, name):
                        self.name = name
                        self.id = id
                backgrounds.append(BackgroundInfo(row['id'], row['name']))
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
        
        # Initialize inventory if not exists
        if 'inventory' not in character_data:
            character_data['inventory'] = []
        
        # Process all equipment choices - frontend now sends individual items
        for choice_key, item_name in equipment_choices.items():
            print(f"[SQLite] Processing choice '{choice_key}': {item_name}")
            
            # Get item data from equipment JSON to determine type
            item_data = self.get_equipment_item_sync(item_name)
            if not item_data:
                print(f"[SQLite] Warning: Item '{item_name}' not found in equipment database")
                continue
            
            item_type = item_data.get('item_type', '')
            
            # Add to inventory first
            character_data['inventory'].append({
                'name': item_name,
                'quantity': 1,
                'weight': item_data.get('weight_lb', 0)
            })
            print(f"[SQLite] Added '{item_name}' to inventory")
            
            # Auto-equip based on item type
            if item_type == 'weapon':
                if not character_data.get('equipment_main_hand'):
                    character_data['equipment_main_hand'] = item_name
                    print(f"[SQLite] Equipped '{item_name}' as main hand weapon")
                elif not character_data.get('equipment_off_hand') and 'light' in item_data.get('weapon_properties', []):
                    character_data['equipment_off_hand'] = item_name
                    print(f"[SQLite] Equipped '{item_name}' as off hand weapon")
                    
            elif item_type == 'armor':
                character_data['equipment_armor'] = item_name
                print(f"[SQLite] Equipped '{item_name}' as armor")
                
            elif item_type == 'shield':
                character_data['equipment_off_hand'] = item_name
                print(f"[SQLite] Equipped '{item_name}' as shield")
                
            elif item_type in ['spellcasting_focus', 'spellbook']:
                # Add to inventory but don't auto-equip focuses/spellbooks
                print(f"[SQLite] Added '{item_name}' ({item_type}) to inventory")
                
            elif item_type == 'helmet':
                character_data['equipment_helmet'] = item_name
                print(f"[SQLite] Equipped '{item_name}' as helmet")
    
    def _apply_feat_effects_to_character(self, character_dict: Dict[str, Any], feats: List[str]) -> Dict[str, Any]:
        """Apply mechanical effects of feats to character stats."""
        if not feats:
            return character_dict

        try:
            # Create a working copy for processing
            char_data = {
                'level': character_dict['level'],
                'hit_points_max': character_dict['hit_points_max'],
                'hit_points_current': character_dict['hit_points_current'],
                'strength': character_dict['strength'],
                'dexterity': character_dict['dexterity'],
                'constitution': character_dict['constitution'],
                'intelligence': character_dict['intelligence'],
                'wisdom': character_dict['wisdom'],
                'charisma': character_dict['charisma'],
                'proficiencies': character_dict.get('proficiencies', [])
            }

            # Apply all feat effects using shared processor
            from services.feat_effects import FeatEffectsProcessor

            processor = FeatEffectsProcessor()
            modified = processor.apply_feat_effects_to_character(char_data, feats)

            # Update dictionary with any modified values, clamping ability scores at 20
            character_dict['hit_points_max'] = modified.get('hit_points_max', character_dict['hit_points_max'])
            character_dict['hit_points_current'] = modified.get('hit_points_current', character_dict['hit_points_current'])
            character_dict['strength'] = min(20, modified.get('strength', character_dict['strength']))
            character_dict['dexterity'] = min(20, modified.get('dexterity', character_dict['dexterity']))
            character_dict['constitution'] = min(20, modified.get('constitution', character_dict['constitution']))
            character_dict['intelligence'] = min(20, modified.get('intelligence', character_dict['intelligence']))
            character_dict['wisdom'] = min(20, modified.get('wisdom', character_dict['wisdom']))
            character_dict['charisma'] = min(20, modified.get('charisma', character_dict['charisma']))
            character_dict['proficiencies'] = modified.get('proficiencies', character_dict.get('proficiencies', []))

            return character_dict

        except Exception as e:
            print(f"[SQLite] Error applying feat effects: {e}")
            return character_dict
    
    def _add_starting_equipment(self, cursor, character_id: str, character_data: Dict):
        """Add starting equipment based on class and background."""
        import uuid
        
        # Check if character already has equipment
        cursor.execute("SELECT COUNT(*) FROM character_inventory WHERE character_id = ?", (character_id,))
        existing_items = cursor.fetchone()[0]
        
        if existing_items > 0:
            print(f"[SQLite] Character already has {existing_items} items in inventory, skipping starting equipment")
            return
        
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
                ('Potion of Healing', 'consumable', 1, 0.5, 'This potion is a magic item. As a Bonus Action, you can drink it or administer it to another creature within 5 feet of yourself. The creature that drinks the magical red fluid in this vial regains 2d4 + 2 Hit Points.', 50),
                ('Backpack', 'gear', 1, 5.0, 'A leather backpack that can hold up to 30 pounds of gear.', 2),
                ('Rations (1 day)', 'consumable', 5, 2.0, 'These are required to gain the benefits of a long rest. Each day\'s ration provides enough sustenance for one creature for 24 hours.', 1),
            ]
            
            for item_name, item_type, quantity, weight_lb, description, value_gp in equipment_items:
                cursor.execute("""
                    INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), character_id, item_name, item_type, quantity, weight_lb, description, value_gp))
        
        # Barbarian Class Starting Equipment
        elif class_id in ['barbarian']:
            equipment_items = [
                # Adventuring gear
                ('Explorer\'s Pack', 'gear', 1, 59.0, 'Includes backpack, bedroll, mess kit, tinderbox, 10 torches, 10 days rations, waterskin, 50 ft hemp rope', 10),
                # Javelins stack since they're thrown weapons
                ('Javelin', 'weapon', 4, 2.0, 'Simple thrown weapon (range 30/120)', 5),
            ]
            
            # Add 2 scimitars separately for dual-wielding (not stacked)
            for i in range(2):
                cursor.execute("""
                    INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), character_id, 'Scimitar', 'weapon', 1, 3.0, 'Finesse, light martial weapon (1d6 slashing)', 25, 1 if i == 0 else 0))
                
            print(f"[SQLite] Added 2 individual scimitars for dual-wielding (first equipped)")
            
            # Check equipment choices for greataxe vs scale mail choice
            # The choice has already been added from equipment_choices above, so we only add if no choice was made
            barbarian_choice = equipment_choices.get('barbarian_choice', '')
            if not barbarian_choice:
                # No choice made, default to greataxe
                equipment_items.append(('Greataxe', 'weapon', 1, 7.0, 'Heavy, two-handed martial weapon (1d12 slashing)', 30))
                print(f"[SQLite] Barbarian defaulted to Greataxe (no choice made)")
            elif 'scale' in barbarian_choice.lower() or 'mail' in barbarian_choice.lower():
                # Choice was scale mail, already added above
                print(f"[SQLite] Barbarian chose Scale Mail")
            else:
                # Choice was greataxe, already added above
                print(f"[SQLite] Barbarian chose Greataxe")
            
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
    
    def _initialize_class_features(self, cursor, character_id: str, character_data: Dict):
        """Initialize class-specific features table based on character's class."""
        class_id = character_data.get('class_id', '').lower()
        level = character_data.get('level', 1)
        
        print(f"[SQLite] Initializing {class_id} class features for level {level}")
        
        if class_id == 'fighter':
            self._initialize_fighter_features(cursor, character_id, character_data)
        elif class_id == 'barbarian':
            self._initialize_barbarian_features(cursor, character_id, character_data)
        elif class_id == 'wizard':
            self._initialize_wizard_features(cursor, character_id, character_data)
        elif class_id == 'warlock':
            self._initialize_warlock_features(cursor, character_id, character_data)
        elif class_id == 'cleric':
            self._initialize_cleric_features(cursor, character_id, character_data)
        elif class_id == 'rogue':
            self._initialize_rogue_features(cursor, character_id, character_data)
        else:
            print(f"[SQLite] Warning: No class-specific features defined for '{class_id}'")
    
    def _initialize_fighter_features(self, cursor, character_id: str, character_data: Dict):
        """Initialize Fighter-specific features."""
        level = character_data.get('level', 1)
        
        # Extract fighting style from feats (fighting styles are stored as feats during character creation)
        selected_feats = character_data.get('selected_feats', [])
        fighting_style = None
        for feat in selected_feats:
            if feat in ['Archery', 'Defense', 'Dueling', 'Great Weapon Fighting', 'Protection', 'Two-Weapon Fighting']:
                fighting_style = feat.lower()
                break
        
        cursor.execute("""
            INSERT INTO fighter_features (
                character_id, level, fighting_style, action_surge_uses_max, 
                second_wind_used, indomitable_uses_max, extra_attacks, weapon_masteries_known
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, level, fighting_style,
            1 if level >= 2 else 0,  # Action Surge at level 2
            False,  # Second Wind available
            1 if level >= 9 else 0,  # Indomitable at level 9
            2 if level >= 5 else 1,  # Extra Attack at level 5
            3 + (level // 4)  # 3 base, +1 every 4 levels
        ))
        print(f"[SQLite] Initialized Fighter features - Fighting Style: {fighting_style}")
    
    def _initialize_barbarian_features(self, cursor, character_id: str, character_data: Dict):
        """Initialize Barbarian-specific features."""
        level = character_data.get('level', 1)
        
        # Calculate rage uses by level (2 at 1st, 3 at 3rd, 4 at 6th, 5 at 12th, 6 at 17th, unlimited at 20th)
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
        else:
            rage_uses = 2
        
        # Calculate rage damage by level (+2 at 1st, +3 at 9th, +4 at 16th)
        if level >= 16:
            rage_damage = 4
        elif level >= 9:
            rage_damage = 3
        else:
            rage_damage = 2
        
        cursor.execute("""
            INSERT INTO barbarian_features (
                character_id, level, rage_uses_max, rage_damage_bonus, 
                unarmored_defense_active, reckless_attack_available, danger_sense_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, level, rage_uses, rage_damage,
            True,  # Unarmored Defense always available
            level >= 2,  # Reckless Attack at level 2
            level >= 2   # Danger Sense at level 2
        ))
        print(f"[SQLite] Initialized Barbarian features - {rage_uses} rages, +{rage_damage} damage")
    
    def _initialize_wizard_features(self, cursor, character_id: str, character_data: Dict):
        """Initialize Wizard-specific features (full spellcaster)."""
        level = character_data.get('level', 1)
        
        # Calculate spell slots by level (full caster progression)
        spell_slots = self._get_full_caster_spell_slots(level)
        
        cursor.execute("""
            INSERT INTO wizard_features (
                character_id, level,
                spell_slots_1_max, spell_slots_2_max, spell_slots_3_max, spell_slots_4_max, spell_slots_5_max,
                spell_slots_6_max, spell_slots_7_max, spell_slots_8_max, spell_slots_9_max,
                spell_slots_1_current, spell_slots_2_current, spell_slots_3_current, spell_slots_4_current, spell_slots_5_current,
                spell_slots_6_current, spell_slots_7_current, spell_slots_8_current, spell_slots_9_current,
                arcane_school, arcane_recovery_used, spellbook_spells_known
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, level,
            # Max slots
            spell_slots[1], spell_slots[2], spell_slots[3], spell_slots[4], spell_slots[5],
            spell_slots[6], spell_slots[7], spell_slots[8], spell_slots[9],
            # Current slots (start full)
            spell_slots[1], spell_slots[2], spell_slots[3], spell_slots[4], spell_slots[5],
            spell_slots[6], spell_slots[7], spell_slots[8], spell_slots[9],
            # Features
            None,  # Arcane school chosen later
            False,  # Arcane recovery available
            6 + (level - 1) * 2  # 6 starting + 2 per level
        ))
        print(f"[SQLite] Initialized Wizard features - Level {level} spell slots")
    
    def _initialize_warlock_features(self, cursor, character_id: str, character_data: Dict):
        """Initialize Warlock-specific features (pact magic)."""
        level = character_data.get('level', 1)
        
        # Warlock pact magic progression (different from full casters)
        if level >= 17:
            pact_slots_max = 4
            pact_slot_level = 5
        elif level >= 15:
            pact_slots_max = 3
            pact_slot_level = 5
        elif level >= 11:
            pact_slots_max = 3
            pact_slot_level = 5
        elif level >= 9:
            pact_slots_max = 2
            pact_slot_level = 5
        elif level >= 7:
            pact_slots_max = 2
            pact_slot_level = 4
        elif level >= 5:
            pact_slots_max = 2
            pact_slot_level = 3
        elif level >= 3:
            pact_slots_max = 2
            pact_slot_level = 2
        else:
            pact_slots_max = 1
            pact_slot_level = 1
        
        cursor.execute("""
            INSERT INTO warlock_features (
                character_id, level, pact_slots_max, pact_slots_current, pact_slot_level,
                patron, pact_boon, eldritch_invocations, patron_feature_uses_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, level, pact_slots_max, pact_slots_max, pact_slot_level,
            None,  # Patron chosen during character creation
            None if level < 3 else 'chain',  # Pact Boon at level 3
            '[]',  # JSON array of invocations
            1 if level >= 1 else 0  # Patron feature uses
        ))
        print(f"[SQLite] Initialized Warlock features - {pact_slots_max} level {pact_slot_level} pact slots")
    
    def _initialize_cleric_features(self, cursor, character_id: str, character_data: Dict):
        """Initialize Cleric-specific features (full spellcaster + divine)."""
        level = character_data.get('level', 1)
        
        # Calculate spell slots by level (same as wizard - full caster)
        spell_slots = self._get_full_caster_spell_slots(level)
        
        # Calculate channel divinity uses (1 at level 2, +1 at 6th and 18th)
        if level >= 18:
            channel_divinity_max = 3
        elif level >= 6:
            channel_divinity_max = 2
        elif level >= 2:
            channel_divinity_max = 1
        else:
            channel_divinity_max = 0
        
        cursor.execute("""
            INSERT INTO cleric_features (
                character_id, level,
                spell_slots_1_max, spell_slots_2_max, spell_slots_3_max, spell_slots_4_max, spell_slots_5_max,
                spell_slots_6_max, spell_slots_7_max, spell_slots_8_max, spell_slots_9_max,
                spell_slots_1_current, spell_slots_2_current, spell_slots_3_current, spell_slots_4_current, spell_slots_5_current,
                spell_slots_6_current, spell_slots_7_current, spell_slots_8_current, spell_slots_9_current,
                divine_domain, channel_divinity_uses_max, domain_spells_known
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, level,
            # Max slots
            spell_slots[1], spell_slots[2], spell_slots[3], spell_slots[4], spell_slots[5],
            spell_slots[6], spell_slots[7], spell_slots[8], spell_slots[9],
            # Current slots (start full)
            spell_slots[1], spell_slots[2], spell_slots[3], spell_slots[4], spell_slots[5],
            spell_slots[6], spell_slots[7], spell_slots[8], spell_slots[9],
            # Features
            None,  # Divine domain chosen during character creation
            channel_divinity_max,
            '[]'   # JSON array of domain spells
        ))
        print(f"[SQLite] Initialized Cleric features - Level {level} spells, {channel_divinity_max} channel divinity")
    
    def _initialize_rogue_features(self, cursor, character_id: str, character_data: Dict):
        """Initialize Rogue-specific features."""
        level = character_data.get('level', 1)
        
        # Calculate sneak attack dice (1d6 at 1st, +1d6 every 2 levels)
        sneak_attack_dice = 1 + ((level - 1) // 2)
        
        cursor.execute("""
            INSERT INTO rogue_features (
                character_id, level, sneak_attack_dice, expertise_skills,
                cunning_action_available, uncanny_dodge_available, evasion_available, archetype
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, level, sneak_attack_dice, '[]',  # JSON array of expertise skills
            level >= 2,  # Cunning Action at level 2
            level >= 5,  # Uncanny Dodge at level 5
            level >= 7,  # Evasion at level 7
            None  # Archetype chosen at level 3
        ))
        print(f"[SQLite] Initialized Rogue features - {sneak_attack_dice}d6 sneak attack")
    
    def _get_full_caster_spell_slots(self, level: int) -> Dict[int, int]:
        """Get spell slot progression for full casters (Wizard, Cleric)."""
        # D&D 5e full caster spell slot table
        spell_slot_table = {
            1: {1: 2, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            2: {1: 3, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            3: {1: 4, 2: 2, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            4: {1: 4, 2: 3, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            5: {1: 4, 2: 3, 3: 2, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            6: {1: 4, 2: 3, 3: 3, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            7: {1: 4, 2: 3, 3: 3, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            8: {1: 4, 2: 3, 3: 3, 4: 2, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1, 6: 0, 7: 0, 8: 0, 9: 0},
            10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 0, 7: 0, 8: 0, 9: 0},
            11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 0, 8: 0, 9: 0},
            12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 0, 8: 0, 9: 0},
            13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 0, 9: 0},
            14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 0, 9: 0},
            15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 0},
            16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 0},
            17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
            18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
            19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
            20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1}
        }
        return spell_slot_table.get(min(level, 20), spell_slot_table[1])

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
                    """, (current_hp, max_hp, max_hp, datetime.now().isoformat(), self.current_character['id']))
                    
                    # Also update the current character dictionary
                    self.current_character['hit_points_current'] = current_hp
                    self.current_character['hit_points_max'] = max_hp
                    
                    print(f"[SQLite] Updated {self.current_character['name']} HP: {current_hp}/{max_hp}")
                else:
                    # Update only current HP
                    cursor.execute("""
                        UPDATE characters 
                        SET hit_points_current = ?, updated_at = ?
                        WHERE id = ?
                    """, (current_hp, datetime.now().isoformat(), self.current_character['id']))
                    
                    # Update the current character dictionary
                    self.current_character['hit_points_current'] = current_hp
                    
                    print(f"[SQLite] Updated {self.current_character['name']} current HP: {current_hp}/{self.current_character['hit_points_max']}")
                
                conn.commit()
                
        except Exception as e:
            print(f"[SQLite] Error updating character HP: {e}")
    
    def _calculate_armor_class(self, character_id: str, strength: int, dexterity: int, constitution: int, class_id: str) -> int:
        """Calculate AC based on equipped armor and class features like Unarmored Defense."""
        print(f"[SQLite] _calculate_armor_class called for character {character_id}")
        try:
            # Get equipped armor information from characters table
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get equipment directly from characters table
                cursor.execute("""
                    SELECT equipment_armor, equipment_shield, equipment_off_hand
                    FROM characters 
                    WHERE id = ?
                """, (character_id,))
                
                equipment_row = cursor.fetchone()
                
                # Extract equipped items (using dict-like access since _get_connection sets row_factory)
                equipped_armor = equipment_row['equipment_armor'] if equipment_row else None
                equipped_shield = equipment_row['equipment_shield'] if equipment_row else None
                equipped_off_hand = equipment_row['equipment_off_hand'] if equipment_row else None
                
                # Check if off-hand item is a shield
                if equipped_off_hand and not equipped_shield:
                    # Check if the off-hand item is a shield by looking it up in equipment table
                    cursor.execute("""
                        SELECT item_type FROM equipment WHERE name = ?
                    """, (equipped_off_hand,))
                    item_type_row = cursor.fetchone()
                    if item_type_row and item_type_row['item_type'] == 'shield':
                        equipped_shield = equipped_off_hand
                        print(f"[SQLite] Found shield in off-hand slot: {equipped_shield}")
            
            # Calculate modifiers
            dex_mod = (dexterity - 10) // 2
            con_mod = (constitution - 10) // 2
            
            # Base AC calculation
            if equipped_armor:
                # Character is wearing armor - use equipment service for proper AC calculation
                # Import and use the equipment service
                from services.equipment import equipment_service
                ac = equipment_service.get_armor_ac(equipped_armor, dex_mod)
                print(f"[SQLite] AC calculation: {equipped_armor} with Dex {dex_mod} = {ac}")
                
            else:
                # No armor equipped - check for class features
                if class_id == 'barbarian':
                    # Barbarian Unarmored Defense: 10 + Dex + Con
                    ac = 10 + dex_mod + con_mod
                    print(f"[SQLite] Barbarian Unarmored Defense: 10 + Dex {dex_mod} + Con {con_mod} = {ac}")
                else:
                    # Standard unarmored AC: 10 + Dex
                    ac = 10 + dex_mod
                    print(f"[SQLite] Standard unarmored AC: 10 + Dex {dex_mod} = {ac}")
            
            # Add shield bonus
            if equipped_shield:
                from services.equipment import equipment_service
                shield_bonus = equipment_service.get_shield_ac_bonus(equipped_shield)
                ac += shield_bonus
                print(f"[SQLite] Added shield {equipped_shield}: +{shield_bonus} AC")
            
            # Apply Defense fighting style bonus (+1 AC when wearing armor)
            if equipped_armor:  # Only applies when wearing armor
                print(f"[SQLite] Checking for Defense fighting style for character {character_id}")
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT feat_name FROM character_feats 
                        WHERE character_id = ? AND feat_name = 'Defense'
                    """, (character_id,))
                    has_defense = cursor.fetchone()
                
                print(f"[SQLite] Defense check result: {has_defense}")
                if has_defense:
                    ac += 1
                    print(f"[SQLite] Defense fighting style: +1 AC (total now {ac})")
                else:
                    print(f"[SQLite] No Defense fighting style found")
            
            return ac
            
        except Exception as e:
            print(f"[SQLite] Error calculating AC: {e}")
            # Fallback to basic calculation
            return 10 + ((dexterity - 10) // 2)
    
    def get_monsters_by_cr_sync(self, min_cr: float, max_cr: float) -> List[Dict[str, Any]]:
        """Get monsters within CR range from JSON data files."""
        try:
            import json
            import glob
            monsters = []
            
            # Load monster data from JSON files
            monster_files = glob.glob("data/monsters*.json")
            for file_path in monster_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        monster_data = json.load(f)
                        
                    # Handle different JSON structures
                    if isinstance(monster_data, list):
                        monsters.extend(monster_data)
                    elif isinstance(monster_data, dict):
                        if 'monsters' in monster_data:
                            monsters.extend(monster_data['monsters'])
                        else:
                            monsters.append(monster_data)
                            
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
                    continue
            
            # Filter by CR range
            matching_monsters = []
            for monster in monsters:
                cr = monster.get('challenge_rating', 0)
                
                # Handle different CR formats ("1/4", "1/2", etc.)
                if isinstance(cr, str):
                    if '/' in cr:
                        numerator, denominator = cr.split('/')
                        cr = float(numerator) / float(denominator)
                    else:
                        try:
                            cr = float(cr)
                        except ValueError:
                            cr = 0
                elif not isinstance(cr, (int, float)):
                    cr = 0
                
                if min_cr <= cr <= max_cr:
                    matching_monsters.append(monster)
            
            print(f"[SQLite] Found {len(matching_monsters)} monsters with CR {min_cr}-{max_cr}")
            return matching_monsters
            
        except Exception as e:
            print(f"[SQLite] Error loading monsters: {e}")
            return []
    
    def update_character_equipment_sync(self, character_id: str, equipment_slot: str, item_name: Optional[str] = None):
        """Update character equipment in database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Update the equipment slot
                if equipment_slot == 'main_hand':
                    cursor.execute("UPDATE characters SET equipment_main_hand = ? WHERE id = ?", 
                                 (item_name, character_id))
                elif equipment_slot == 'off_hand':
                    cursor.execute("UPDATE characters SET equipment_off_hand = ? WHERE id = ?", 
                                 (item_name, character_id))
                elif equipment_slot == 'armor':
                    cursor.execute("UPDATE characters SET equipment_armor = ? WHERE id = ?", 
                                 (item_name, character_id))
                elif equipment_slot == 'shield':
                    cursor.execute("UPDATE characters SET equipment_shield = ? WHERE id = ?", 
                                 (item_name, character_id))
                else:
                    print(f"[SQLite] Unknown equipment slot: {equipment_slot}")
                    return False
                
                # Get character data for AC recalculation
                cursor.execute("""
                    SELECT strength, dexterity, constitution, class_id 
                    FROM characters WHERE id = ?
                """, (character_id,))
                char_row = cursor.fetchone()
                
                if char_row:
                    # Recalculate AC with new equipment
                    new_ac = self._calculate_armor_class(
                        character_id, 
                        char_row['strength'], 
                        char_row['dexterity'], 
                        char_row['constitution'], 
                        char_row['class_id']
                    )
                    
                    # Update AC and timestamp
                    cursor.execute("""
                        UPDATE characters 
                        SET armor_class = ?, updated_at = ?
                        WHERE id = ?
                    """, (new_ac, datetime.now().isoformat(), character_id))
                
                conn.commit()
                
                action = "equipped" if item_name else "unequipped"
                item_text = item_name if item_name else "nothing"
                print(f"[SQLite] Character {action} {item_text} in {equipment_slot}, AC recalculated")
                return True
                
        except Exception as e:
            print(f"[SQLite] Error updating equipment: {e}")
            return False
    
    def update_character_resources_sync(self, character_id: str, resource_updates: Dict[str, Any]):
        """Update character resources in database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                updates = []
                params = []
                
                # Handle JSON resource fields
                json_fields = ['spell_slots_current', 'spell_slots_max', 'class_resources', 
                              'class_resources_max', 'ability_uses', 'ability_uses_max']
                
                for field in json_fields:
                    if field in resource_updates:
                        updates.append(f"{field} = ?")
                        params.append(json.dumps(resource_updates[field]))
                
                # Handle simple numeric fields
                simple_fields = ['hit_points_current', 'hit_points_max', 'hit_points_temporary',
                                'hit_dice_current', 'death_saves_successes', 'death_saves_failures']
                
                for field in simple_fields:
                    if field in resource_updates:
                        updates.append(f"{field} = ?")
                        params.append(resource_updates[field])
                
                if updates:
                    updates.append("updated_at = ?")
                    params.append(datetime.now().isoformat())
                    params.append(character_id)
                    
                    sql = f"UPDATE characters SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(sql, params)
                    conn.commit()
                    
                    print(f"[SQLite] Updated resources for character: {list(resource_updates.keys())}")
                    return True
                else:
                    print(f"[SQLite] No valid resource updates provided")
                    return False
                    
        except Exception as e:
            print(f"[SQLite] Error updating resources: {e}")
            return False
    
    def add_feat_to_character_sync(self, character_id: str, feat_name: str) -> bool:
        """Add a new feat to a character."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if feat already exists
                cursor.execute("""
                    SELECT COUNT(*) FROM character_feats 
                    WHERE character_id = ? AND feat_name = ?
                """, (character_id, feat_name))
                
                if cursor.fetchone()[0] > 0:
                    print(f"[SQLite] Character already has feat: {feat_name}")
                    return False
                
                # Get character level for feat acquisition
                cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
                char_row = cursor.fetchone()
                level = char_row['level'] if char_row else 1
                
                # Add the feat
                cursor.execute("""
                    INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
                    VALUES (?, ?, 'manual', ?)
                """, (character_id, feat_name, level))
                
                # Apply feat effects if needed (e.g., Tough increases HP)
                if feat_name == 'Tough':
                    cursor.execute("""
                        UPDATE characters 
                        SET hit_points_max = hit_points_max + (level * 2),
                            hit_points_current = hit_points_current + (level * 2)
                        WHERE id = ?
                    """, (character_id,))
                
                conn.commit()
                print(f"[SQLite] Added feat '{feat_name}' to character")
                return True
                
        except Exception as e:
            print(f"[SQLite] Error adding feat: {e}")
            return False
    
    def recalculate_character_stats_sync(self, character_id: str) -> bool:
        """Recalculate character stats including AC and feat effects."""
        print(f"[SQLite] recalculate_character_stats_sync called for character {character_id}")
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get character data
                cursor.execute("""
                    SELECT strength, dexterity, constitution, class_id, level
                    FROM characters WHERE id = ?
                """, (character_id,))
                
                char_row = cursor.fetchone()
                if not char_row:
                    print(f"[SQLite] Character {character_id} not found")
                    return False
                
                # Recalculate AC
                new_ac = self._calculate_armor_class(
                    character_id,
                    char_row['strength'],
                    char_row['dexterity'],
                    char_row['constitution'],
                    char_row['class_id']
                )
                
                # Update AC and timestamp
                cursor.execute("""
                    UPDATE characters 
                    SET armor_class = ?, updated_at = ?
                    WHERE id = ?
                """, (new_ac, datetime.now().isoformat(), character_id))
                
                conn.commit()
                print(f"[SQLite] Recalculated stats for character, new AC: {new_ac}")
                return True
                
        except Exception as e:
            print(f"[SQLite] Error recalculating stats: {e}")
            return False
    
    def can_equip_item(self, character_id: str, item_name: str) -> tuple[bool, str]:
        """Check if character can equip a specific item. Returns (can_equip, reason)."""
        try:
            # Load item data from JSON
            item_data = self.get_equipment_item_sync(item_name)
            if not item_data:
                return False, f"Item '{item_name}' not found"
            
            item_type = item_data.get('item_type', '')
            
            # Get character data for proficiency checks
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT class_id, strength FROM characters WHERE id = ?
                """, (character_id,))
                
                char_row = cursor.fetchone()
                if not char_row:
                    return False, "Character not found"
                
                if item_type == 'armor':
                    # Check armor proficiency using proficiency system
                    armor_name = item_data.get('name', '')
                    is_proficient, message = self.proficiency_system.is_proficient_with_armor(character_id, armor_name)
                    if not is_proficient:
                        return False, message
                    
                    # Check Strength requirement
                    strength_req = item_data.get('strength_requirement', 0)
                    if strength_req and char_row['strength'] < strength_req:
                        return False, f"Requires Strength {strength_req} (you have {char_row['strength']})"
                        
                elif item_type == 'shield':
                    # Check shield proficiency using proficiency system
                    if not self.proficiency_system.is_proficient_with_shield(character_id):
                        return False, "Not proficient with shields"
                
                elif item_type == 'weapon':
                    # Check weapon proficiency using proficiency system
                    weapon_name = item_data.get('name', '')
                    is_proficient, message = self.proficiency_system.is_proficient_with_weapon(character_id, weapon_name)
                    if not is_proficient:
                        return False, message
            
            return True, ""
            
        except Exception as e:
            print(f"[SQLite] Error checking equipment proficiency: {e}")
            return False, "Error checking proficiency"
    
    def auto_save(self):
        """Perform automatic save (just calls save_game_sync)."""
        self.save_game_sync()
    
    def update_character_xp_sync(self, character_id: str, new_xp: int) -> bool:
        """Update character's experience points in the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE characters 
                    SET experience_points = ?, updated_at = datetime('now')
                    WHERE id = ?
                """, (new_xp, character_id))
                
                success = cursor.rowcount > 0
                if success:
                    print(f"[SQLite] Updated character {character_id} XP to {new_xp}")
                    
                    # Also update the current character in memory if it's the same one
                    if self.current_character and self.current_character['id'] == character_id:
                        self.current_character['experience_points'] = new_xp
                        
                return success
                
        except Exception as e:
            print(f"[SQLite] Error updating character XP: {e}")
            return False
    
    def add_gold_to_character_sync(self, character_id: str, gold_amount: int) -> bool:
        """Add gold to character's inventory in the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if character already has gold in inventory
                cursor.execute("""
                    SELECT quantity FROM character_inventory 
                    WHERE character_id = ? AND item_name = 'Gold Pieces'
                """, (character_id,))
                
                result = cursor.fetchone()
                
                if result:
                    # Update existing gold quantity
                    old_quantity = result[0]
                    new_quantity = old_quantity + gold_amount
                    
                    cursor.execute("""
                        UPDATE character_inventory 
                        SET quantity = ?
                        WHERE character_id = ? AND item_name = 'Gold Pieces'
                    """, (new_quantity, character_id))
                    
                    print(f"[SQLite] Updated character {character_id} gold: {old_quantity} -> {new_quantity} (+{gold_amount})")
                else:
                    # Create new gold entry
                    cursor.execute("""
                        INSERT INTO character_inventory 
                        (id, character_id, item_name, item_type, quantity, weight_lb, value_gp) 
                        VALUES (?, ?, 'Gold Pieces', 'currency', ?, 0.0, 1.0)
                    """, (f"{character_id}_gold", character_id, gold_amount))
                    
                    print(f"[SQLite] Added {gold_amount} gold pieces to character {character_id}")
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"[SQLite] Error adding gold to character: {e}")
            return False
    
    def save_character_sync(self, character_id: str = None) -> bool:
        """Save current character or specified character to database."""
        try:
            character = None
            if character_id:
                # Load specific character (not implemented for now)
                return False
            elif self.current_character:
                character = self.current_character
            else:
                return False
                
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE characters SET
                        name = ?, level = ?, experience_points = ?,
                        strength = ?, dexterity = ?, constitution = ?,
                        intelligence = ?, wisdom = ?, charisma = ?,
                        armor_class = ?, hit_points_max = ?, hit_points_current = ?,
                        hit_points_temporary = ?, updated_at = datetime('now')
                    WHERE id = ?
                """, (
                    character['name'], character['level'], character['experience_points'],
                    character['strength'], character['dexterity'], character['constitution'],
                    character['intelligence'], character['wisdom'], character['charisma'],
                    character['armor_class'], character['hit_points_max'], character['hit_points_current'],
                    character['hit_points_temporary'], character['id']
                ))
                
                conn.commit()
                success = cursor.rowcount > 0
                if success:
                    print(f"[SQLite] Saved character {character['name']} (ID: {character['id']})")
                return success
                
        except Exception as e:
            print(f"[SQLite] Error saving character: {e}")
            return False

    def shutdown(self):
        """Clean shutdown of game engine."""
        try:
            # Save settings before shutting down
            self.save_settings()
            print("[SQLite] Game engine shut down cleanly")
        except Exception as e:
            print(f"[SQLite] Error during shutdown: {e}")