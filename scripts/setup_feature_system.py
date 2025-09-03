#!/usr/bin/env python3
"""
Feature System Setup Script

Sets up the new feature system tables and initializes the system.
No migration needed - fresh start for clean implementation.
"""

import sqlite3
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from core
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.feature_integration import FeatureSystemIntegration


def setup_feature_system(db_path: str = "talekeeper.db"):
    """Set up the new feature system tables."""
    print("Setting up feature system...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create unified feature state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_states (
                character_id TEXT NOT NULL,
                feature_name TEXT NOT NULL,
                feature_type TEXT NOT NULL,
                is_active BOOLEAN DEFAULT FALSE,
                uses_current INTEGER,
                uses_max INTEGER,
                configuration TEXT,  -- JSON for feature-specific config
                last_used TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                PRIMARY KEY (character_id, feature_name),
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        """)
        
        # Create feature progression tracking (optional - for analytics/debugging)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_progression (
                character_id TEXT NOT NULL,
                class_name TEXT NOT NULL,
                subclass TEXT,
                level INTEGER NOT NULL,
                features_gained TEXT,  -- JSON list of feature names
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feature_states_character_id 
            ON feature_states(character_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feature_states_type 
            ON feature_states(feature_type)
        """)
        
        conn.commit()
        print("Success: Feature system tables created successfully!")
        
        # Initialize the integration system
        integration = FeatureSystemIntegration(db_path)
        print("Success: Feature system integration initialized!")
        
        return True
        
    except Exception as e:
        print(f"Error setting up feature system: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()


def test_feature_system(db_path: str = "talekeeper.db"):
    """Test the feature system with a mock character."""
    print("\nTesting feature system...")
    
    integration = FeatureSystemIntegration(db_path)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Check if we have any characters
        cursor.execute("SELECT COUNT(*) as count FROM characters")
        count = cursor.fetchone()['count']
        
        if count == 0:
            print("No characters found - feature system ready for new characters!")
            return True
        
        # Test with existing characters
        cursor.execute("""
            SELECT id, name, class_id, level
            FROM characters
            LIMIT 3
        """)
        
        characters = cursor.fetchall()
        
        for char in characters:
            character_id = char['id']
            name = char['name']
            class_name = char['class_id']
            level = char['level']
            
            print(f"\nTesting with {name} (Level {level} {class_name})...")
            
            # Initialize features for this character
            success = integration.initialize_character_features(character_id)
            
            if success:
                print(f"  Success: Features initialized")
                
                # Get available features
                features = integration.get_available_features(character_id)
                print(f"  Success: {len(features)} features available")
                
                if features:
                    print(f"  Features: {', '.join([f['name'] for f in features[:3]])}")
                    if len(features) > 3:
                        print(f"    + {len(features) - 3} more...")
            else:
                print(f"  Failed to initialize features")
        
        print("\nFeature system testing completed!")
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return False
    
    finally:
        conn.close()


def create_sample_characters(db_path: str = "talekeeper.db"):
    """Create sample characters to test the feature system."""
    print("\nCreating sample characters for testing...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Sample characters for testing
        sample_chars = [
            {
                'id': 'test_fighter_1',
                'name': 'Test Fighter',
                'class_id': 'Fighter',
                'level': 5,
                'subclass_id': 'Champion'
            },
            {
                'id': 'test_barbarian_1', 
                'name': 'Test Barbarian',
                'class_id': 'Barbarian',
                'level': 3,
                'subclass_id': None
            },
            {
                'id': 'test_rogue_1',
                'name': 'Test Rogue', 
                'class_id': 'Rogue',
                'level': 4,
                'subclass_id': None
            }
        ]
        
        # Check if we have a save slot
        cursor.execute("SELECT id FROM save_slots LIMIT 1")
        save_slot = cursor.fetchone()
        
        if not save_slot:
            # Create a test save slot
            cursor.execute("""
                INSERT INTO save_slots (id, slot_number, is_occupied, character_name)
                VALUES ('test_slot', 1, 1, 'Test Characters')
            """)
            save_slot_id = 'test_slot'
        else:
            save_slot_id = save_slot[0]
        
        for char_data in sample_chars:
            # Check if character already exists
            cursor.execute("SELECT id FROM characters WHERE id = ?", (char_data['id'],))
            if cursor.fetchone():
                print(f"  {char_data['name']} already exists, skipping...")
                continue
            
            # Create the character with basic stats
            cursor.execute("""
                INSERT INTO characters (
                    id, save_slot_id, name, class_id, subclass_id, level,
                    strength, dexterity, constitution, intelligence, wisdom, charisma,
                    hit_points_max, hit_points_current, armor_class
                ) VALUES (?, ?, ?, ?, ?, ?, 15, 14, 13, 12, 11, 10, 30, 30, 15)
            """, (
                char_data['id'], save_slot_id, char_data['name'], 
                char_data['class_id'], char_data['subclass_id'], char_data['level']
            ))
            
            print(f"  Success: Created {char_data['name']}")
        
        conn.commit()
        print("Success: Sample characters created!")
        
        # Initialize features for the sample characters
        integration = FeatureSystemIntegration(db_path)
        
        for char_data in sample_chars:
            success = integration.initialize_character_features(char_data['id'])
            if success:
                features = integration.get_available_features(char_data['id'])
                print(f"  Success: {char_data['name']}: {len(features)} features initialized")
        
        return True
        
    except Exception as e:
        print(f"Error creating sample characters: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up the new feature system")
    parser.add_argument("--db", default="talekeeper.db", help="Database file path")
    parser.add_argument("--setup", action="store_true", help="Set up feature system tables")
    parser.add_argument("--test", action="store_true", help="Test the feature system")
    parser.add_argument("--sample", action="store_true", help="Create sample test characters")
    parser.add_argument("--all", action="store_true", help="Do setup, sample creation, and testing")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db):
        print(f"Error: Database file '{args.db}' not found.")
        print("Make sure you're in the TaleKeeper directory with talekeeper.db")
        sys.exit(1)
    
    success = True
    
    if args.all or args.setup:
        success &= setup_feature_system(args.db)
    
    if args.all or args.sample:
        success &= create_sample_characters(args.db)
    
    if args.all or args.test:
        success &= test_feature_system(args.db)
    
    if not any([args.setup, args.test, args.sample, args.all]):
        print("Usage:")
        print("  python setup_feature_system.py --all")
        print("  python setup_feature_system.py --setup --sample --test")
        print("  python setup_feature_system.py --setup")
    
    if success:
        print("\nFeature system is ready to use!")
        print("\nNext steps:")
        print("1. Run your application")
        print("2. Create new characters - they'll automatically get features")
        print("3. Use the feature system in combat/gameplay")
    else:
        print("\nSetup encountered errors. Check the output above.")
        sys.exit(1)