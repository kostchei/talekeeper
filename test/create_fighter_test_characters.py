"""
Create Fighter test characters at major feature levels
"""

import sys
import sqlite3
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.fighter_abilities import FighterAbilitiesService

def create_fighter_character(level, name, save_slot):
    """Create a Fighter character at specified level."""
    
    # Base stats that scale with level
    proficiency_bonus = 2 + ((level - 1) // 4)  # +2 at 1-4, +3 at 5-8, etc.
    
    # Calculate HP (Fighter d10 + CON mod per level)
    con_mod = 2  # Assuming 14 CON
    hp = 10 + con_mod + ((level - 1) * (6 + con_mod))  # Average of d10 is 5.5, round to 6
    
    character_id = str(uuid.uuid4())
    
    character_data = {
        'id': character_id,
        'name': name,
        'race_id': 'human',
        'class_id': 'fighter',
        'subclass_id': 'champion',
        'background_id': 'soldier',
        'level': level,
        'experience_points': [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 
                              85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000][level-1],
        
        # Ability scores (Fighter-focused)
        'strength': 16,      # Primary stat
        'dexterity': 14,     # Secondary 
        'constitution': 14,  # HP/saves
        'intelligence': 10,  # Dump stat
        'wisdom': 12,        # Perception
        'charisma': 8,       # Dump stat
        
        # Combat stats
        'hit_points_max': hp,
        'hit_points_current': hp,
        'armor_class': 16,   # Chain mail + DEX
        
        # Equipment
        'equipment_main_hand': 'Longsword',
        'equipment_off_hand': 'Shield',
        'equipment_armor': 'Chain Mail',
        
        
        # Save slot
        'save_slot_id': save_slot
    }
    
    return character_data

def insert_character_to_db(character_data):
    """Insert character into database."""
    try:
        conn = sqlite3.connect('talekeeper.db', timeout=30)
        cursor = conn.cursor()
        
        # Create save slot if needed
        cursor.execute("""
            INSERT OR IGNORE INTO save_slots (id, slot_number, is_occupied, character_name, character_level)
            VALUES (?, ?, 1, ?, ?)
        """, (character_data['save_slot_id'], character_data['save_slot_id'], 
              character_data['name'], character_data['level']))
        
        # Insert character
        cursor.execute("""
            INSERT INTO characters (
                id, name, race_id, class_id, subclass_id, background_id, level, experience_points,
                strength, dexterity, constitution, intelligence, wisdom, charisma,
                hit_points_max, hit_points_current, max_hit_points, current_hit_points, armor_class,
                equipment_main_hand, equipment_off_hand, equipment_armor,
                save_slot_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            character_data['id'], character_data['name'], character_data['race_id'], 
            character_data['class_id'], character_data['subclass_id'], character_data['background_id'],
            character_data['level'], character_data['experience_points'],
            character_data['strength'], character_data['dexterity'], character_data['constitution'],
            character_data['intelligence'], character_data['wisdom'], character_data['charisma'],
            character_data['hit_points_max'], character_data['hit_points_current'], 
            character_data['hit_points_max'], character_data['hit_points_current'],
            character_data['armor_class'],
            character_data['equipment_main_hand'], character_data['equipment_off_hand'], character_data['equipment_armor'],
            character_data['save_slot_id']
        ))
        
        print(f"[DEBUG] Character {character_data['name']} created, initializing features...")
        
        # Add Fighter features using feature system
        try:
            from core.feature_integration import FeatureSystemIntegration
            feature_system = FeatureSystemIntegration('talekeeper.db')
            feature_system.initialize_character_features(character_data['id'])
            print(f"[DEBUG] Features initialized for {character_data['name']}")
        except Exception as e:
            print(f"[WARNING] Feature initialization failed: {e}")
        
        # Update Fighter resources for level
        try:
            fighter_service = FighterAbilitiesService()
            fighter_service.update_fighter_resources_for_level(character_data['id'], character_data['level'])
            print(f"[DEBUG] Fighter resources updated for {character_data['name']}")
        except Exception as e:
            print(f"[WARNING] Fighter resource update failed: {e}")
        
        conn.commit()
        print(f"[OK] Created {character_data['name']} (Level {character_data['level']} Fighter)")
        return True
        
    except Exception as e:
        print(f"[FAIL] Failed to create {character_data['name']}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Create Fighter test characters at major feature levels."""
    
    # Major feature levels for Fighter
    major_levels = [
        (1, "Fighter_1", 21),   # Fighting Style, Second Wind, Weapon Mastery
        (2, "Fighter_2", 22),   # Action Surge, Tactical Mind
        (5, "Fighter_5", 23),   # Extra Attack, Tactical Shift
        (9, "Fighter_9", 24),   # Indomitable, Tactical Master
        (11, "Fighter_11", 25), # Two Extra Attacks (3 total)
        (13, "Fighter_13", 26), # Indomitable (2 uses), Studied Attacks
        (17, "Fighter_17", 27), # Action Surge (2 uses), Indomitable (3 uses)
        (19, "Fighter_19", 28), # Epic Boon
        (20, "Fighter_20", 29)  # Three Extra Attacks (4 total)
    ]
    
    print("Creating Fighter Test Characters at Major Feature Levels")
    print("=" * 60)
    
    success_count = 0
    
    for level, name, save_slot in major_levels:
        character_data = create_fighter_character(level, name, save_slot)
        if insert_character_to_db(character_data):
            success_count += 1
    
    print("=" * 60)
    print(f"Created {success_count}/{len(major_levels)} Fighter test characters")
    
    # Show what features each level has
    print("\nFighter Features by Level:")
    feature_descriptions = {
        1: "Fighting Style, Second Wind, Weapon Mastery",
        2: "Action Surge, Tactical Mind", 
        5: "Extra Attack (2 attacks), Tactical Shift",
        9: "Indomitable, Tactical Master",
        11: "Two Extra Attacks (3 total attacks)",
        13: "Indomitable (2 uses), Studied Attacks", 
        17: "Action Surge (2 uses), Indomitable (3 uses)",
        19: "Epic Boon",
        20: "Three Extra Attacks (4 total attacks)"
    }
    
    for level, name, save_slot in major_levels:
        features = feature_descriptions.get(level, "")
        print(f"  {name}: {features}")

if __name__ == "__main__":
    main()