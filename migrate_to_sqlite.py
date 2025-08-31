#!/usr/bin/env python3
"""
TaleKeeper Database Migration: IndexedDB → SQLite

This script migrates all character data from the IndexedDB JSON format
to a proper SQLite database for better data integrity and performance.

Usage:
    python migrate_to_sqlite.py
    
The script will:
1. Read existing talekeeper.idb JSON file
2. Create new talekeeper.db SQLite database
3. Migrate all characters, save slots, and game states
4. Preserve all existing data
5. Create backup of original file
"""

import json
import sqlite3
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import ast

def log(message: str):
    """Simple logging with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def backup_original_database():
    """Create backup of original IndexedDB file"""
    original_file = "talekeeper.idb"
    if os.path.exists(original_file):
        backup_file = f"talekeeper.idb.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(original_file, backup_file)
        log(f"Created backup: {backup_file}")
        return True
    else:
        log("No existing database file found")
        return False

def load_indexeddb_data() -> Optional[Dict]:
    """Load and parse IndexedDB JSON data"""
    try:
        with open("talekeeper.idb", "r") as f:
            data = json.load(f)
        log(f"Loaded IndexedDB data with {len(data.get('stores', {}))} stores")
        return data
    except FileNotFoundError:
        log("No existing IndexedDB file found - creating fresh database")
        return None
    except json.JSONDecodeError as e:
        log(f"Error parsing IndexedDB JSON: {e}")
        return None

def create_sqlite_database():
    """Create SQLite database with schema"""
    # Read schema file
    with open("database_schema.sql", "r") as f:
        schema_sql = f.read()
    
    # Create database
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Execute schema
    cursor.executescript(schema_sql)
    conn.commit()
    
    log(" Created SQLite database with schema")
    return conn

def repair_corrupted_characters_data(characters_data: Dict) -> Dict:
    """Repair corrupted characters data that was stored as strings"""
    repaired_data = {}
    
    for key, value in characters_data.items():
        if isinstance(value, str) and value.startswith("{'") and value.endswith("'}"):
            log(f"WARNING: Repairing corrupted character data: {key}")
            try:
                # Parse the string as Python literal
                parsed_data = ast.literal_eval(value)
                if isinstance(parsed_data, dict):
                    # Extract individual character objects
                    for char_id, char_data in parsed_data.items():
                        if isinstance(char_data, dict):
                            repaired_data[char_id] = char_data
                            log(f"   Restored character: {char_data.get('name', char_id)}")
                else:
                    log(f"  ERROR: Could not parse corrupted data for {key}")
            except Exception as e:
                log(f"  ERROR: Error repairing corrupted data: {e}")
        else:
            # Normal data
            repaired_data[key] = value
    
    return repaired_data

def migrate_characters(conn: sqlite3.Connection, characters_data: Dict):
    """Migrate character data to SQLite"""
    cursor = conn.cursor()
    migrated_count = 0
    
    # Repair any corrupted data first
    characters_data = repair_corrupted_characters_data(characters_data)
    
    # Now collect all valid character data from mixed entries
    clean_characters = {}
    
    for key, value in characters_data.items():
        if isinstance(value, dict) and 'id' in value:
            # Standard format: character_id -> character_dict
            clean_characters[key] = value
        elif isinstance(value, str):
            log(f"  WARNING: Skipping string value for key {key[:50]}...")
        elif isinstance(key, dict):
            # Special case: the key itself is a dictionary containing character data
            log(f"  Found character data stored as key, extracting...")
            if all(isinstance(v, dict) and 'id' in v for v in key.values()):
                for char_id, char_data in key.items():
                    clean_characters[char_id] = char_data
                    log(f"    Extracted character: {char_data.get('name', char_id)}")
    
    log(f"  Found {len(clean_characters)} valid characters to migrate")
    characters_data = clean_characters
    
    for char_id, char_data in characters_data.items():
            
        try:
            # Insert main character record
            cursor.execute("""
                INSERT INTO characters (
                    id, save_slot_id, name, race_id, class_id, subclass_id, background_id,
                    level, experience_points, strength, dexterity, constitution, 
                    intelligence, wisdom, charisma, armor_class, hit_points_max, 
                    hit_points_current, hit_points_temporary, max_hit_points, 
                    current_hit_points, hit_dice_max, hit_dice_current, 
                    death_saves_successes, death_saves_failures, equipment_main_hand,
                    equipment_off_hand, equipment_armor, equipment_shield,
                    last_short_rest, last_long_rest, created_at, updated_at, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                char_id,
                char_data.get('save_slot_id'),
                char_data.get('name', 'Unknown'),
                char_data.get('race_id', ''),
                char_data.get('class_id', ''),
                char_data.get('subclass_id'),
                char_data.get('background_id', ''),
                char_data.get('level', 1),
                char_data.get('experience_points', 0),
                char_data.get('strength', 10),
                char_data.get('dexterity', 10),
                char_data.get('constitution', 10),
                char_data.get('intelligence', 10),
                char_data.get('wisdom', 10),
                char_data.get('charisma', 10),
                char_data.get('armor_class', 10),
                char_data.get('hit_points_max', 8),
                char_data.get('hit_points_current', 8),
                char_data.get('hit_points_temporary', 0),
                char_data.get('max_hit_points', 8),
                char_data.get('current_hit_points', 8),
                char_data.get('hit_dice_max', 1),
                char_data.get('hit_dice_current', 1),
                char_data.get('death_saves_successes', 0),
                char_data.get('death_saves_failures', 0),
                char_data.get('equipment_main_hand'),
                char_data.get('equipment_off_hand'),
                char_data.get('equipment_armor'),
                char_data.get('equipment_shield'),
                char_data.get('last_short_rest'),
                char_data.get('last_long_rest'),
                char_data.get('created_at'),
                char_data.get('updated_at'),
                char_data.get('notes', '')
            ))
            
            # Migrate feats
            feats = char_data.get('feats', [])
            if feats:
                for feat_name in feats:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_feats (character_id, feat_name, feat_source, level_acquired)
                        VALUES (?, ?, ?, ?)
                    """, (char_id, feat_name, 'unknown', char_data.get('level', 1)))
            
            # Migrate proficiencies  
            proficiencies = char_data.get('proficiencies', [])
            if proficiencies:
                for prof in proficiencies:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
                        VALUES (?, ?, ?, ?)
                    """, (char_id, 'unknown', prof, 'unknown'))
            
            # Migrate weapon masteries
            weapon_masteries = char_data.get('weapon_masteries', [])
            if weapon_masteries:
                for weapon in weapon_masteries:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_weapon_masteries (character_id, weapon_name, mastery_type)
                        VALUES (?, ?, ?)
                    """, (char_id, weapon, 'unknown'))
            
            # Migrate features
            features = char_data.get('features', {})
            if features:
                for feature_name, feature_data in features.items():
                    if isinstance(feature_data, dict):
                        cursor.execute("""
                            INSERT INTO character_features (
                                character_id, feature_name, feature_type, usage_type,
                                level_gained, description, mechanics
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            char_id,
                            feature_name,
                            feature_data.get('type', 'passive'),
                            feature_data.get('usage', 'permanent'),
                            feature_data.get('level_gained', 1),
                            feature_data.get('description', ''),
                            json.dumps(feature_data.get('mechanics', {}))
                        ))
            
            migrated_count += 1
            log(f"   Migrated character: {char_data.get('name', char_id)}")
            
        except Exception as e:
            log(f"  ERROR: Error migrating character {char_id}: {e}")
    
    conn.commit()
    log(f" Migrated {migrated_count} characters")

def migrate_save_slots(conn: sqlite3.Connection, save_slots_data: Dict):
    """Migrate save slot data to SQLite"""
    cursor = conn.cursor()
    migrated_count = 0
    
    for slot_id, slot_data in save_slots_data.items():
        if not isinstance(slot_data, dict):
            continue
            
        try:
            cursor.execute("""
                INSERT INTO save_slots (
                    id, slot_number, is_occupied, save_name, last_played,
                    play_time_minutes, character_name, character_level,
                    current_location, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                slot_id,
                slot_data.get('slot_number', 0),
                slot_data.get('is_occupied', False),
                slot_data.get('save_name'),
                slot_data.get('last_played'),
                slot_data.get('play_time_minutes', 0),
                slot_data.get('character_name'),
                slot_data.get('character_level'),
                slot_data.get('current_location'),
                slot_data.get('created_at'),
                slot_data.get('updated_at')
            ))
            migrated_count += 1
            
        except Exception as e:
            log(f"  ERROR: Error migrating save slot {slot_id}: {e}")
    
    conn.commit()
    log(f" Migrated {migrated_count} save slots")

def migrate_game_states(conn: sqlite3.Connection, game_states_data: Dict):
    """Migrate game state data to SQLite"""
    cursor = conn.cursor()
    migrated_count = 0
    
    for state_id, state_data in game_states_data.items():
        if not isinstance(state_data, dict):
            continue
            
        try:
            cursor.execute("""
                INSERT INTO game_states (
                    id, character_id, current_location, game_time, weather,
                    notes, state_data, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state_id,
                state_data.get('character_id'),
                state_data.get('current_location', 'Starting Town'),
                state_data.get('game_time', datetime.now().isoformat()),
                state_data.get('weather', 'clear'),
                state_data.get('notes', ''),
                json.dumps(state_data.get('additional_data', {})),
                state_data.get('created_at'),
                state_data.get('updated_at')
            ))
            migrated_count += 1
            
        except Exception as e:
            log(f"  ERROR: Error migrating game state {state_id}: {e}")
    
    conn.commit()
    log(f" Migrated {migrated_count} game states")

def verify_migration(conn: sqlite3.Connection):
    """Verify migration success"""
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM characters")
    char_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM character_feats")
    feat_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM save_slots")
    slot_count = cursor.fetchone()[0]
    
    log(f" Migration verification:")
    log(f"  - Characters: {char_count}")
    log(f"  - Character feats: {feat_count}")
    log(f"  - Save slots: {slot_count}")
    
    # Test a sample query
    cursor.execute("""
        SELECT c.name, GROUP_CONCAT(cf.feat_name, ', ') as feats 
        FROM characters c
        LEFT JOIN character_feats cf ON c.id = cf.character_id
        GROUP BY c.id
        LIMIT 3
    """)
    
    results = cursor.fetchall()
    if results:
        log(f" Sample character data:")
        for name, feats in results:
            feats_display = feats if feats else "No feats"
            log(f"  - {name}: {feats_display}")

def main():
    """Main migration process"""
    log("Starting TaleKeeper Database Migration (IndexedDB to SQLite)")
    
    # Step 1: Backup original
    backup_original_database()
    
    # Step 2: Load IndexedDB data
    indexeddb_data = load_indexeddb_data()
    
    # Step 3: Create SQLite database
    conn = create_sqlite_database()
    
    try:
        # Step 4: Migrate data if it exists (save slots first due to foreign key constraints)
        if indexeddb_data and 'stores' in indexeddb_data:
            stores = indexeddb_data['stores']
            
            # Migrate save slots first (referenced by characters)
            if 'save_slots' in stores and 'data' in stores['save_slots']:
                log(" Migrating save slots...")
                migrate_save_slots(conn, stores['save_slots']['data'])
            
            # Migrate characters (after save slots)
            if 'characters' in stores and 'data' in stores['characters']:
                log(" Migrating characters...")
                migrate_characters(conn, stores['characters']['data'])
            
            # Migrate game states
            if 'game_states' in stores and 'data' in stores['game_states']:
                log(" Migrating game states...")
                migrate_game_states(conn, stores['game_states']['data'])
        
        # Step 5: Verify migration
        verify_migration(conn)
        
        log("Migration completed successfully!")
        log("New database: talekeeper.db")
        log("You can inspect the database with: sqlite3 talekeeper.db")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()