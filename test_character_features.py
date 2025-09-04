#!/usr/bin/env python3
"""
Test that character features display correctly in the expanded panel.
"""

import sqlite3
import json
from datetime import datetime

def test_character_features_display():
    """Test character features are loaded correctly from database."""
    
    # Connect to database
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Create test character if one doesn't exist
    test_char_id = "test-fighter-123"
    
    # Check if character exists
    cursor.execute("SELECT COUNT(*) FROM characters WHERE id = ?", (test_char_id,))
    exists = cursor.fetchone()[0] > 0
    
    if not exists:
        print("Creating test character...")
        # Create a basic fighter character for testing
        cursor.execute("""
            INSERT INTO characters (id, name, class_id, level, strength, dexterity, constitution, 
                                  intelligence, wisdom, charisma, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (test_char_id, "Test Fighter", "fighter", 1, 16, 14, 15, 10, 12, 8, datetime.now().isoformat()))
        
        # Add class features
        cursor.execute("""
            INSERT INTO character_features (character_id, feature_name, description, usage_type, level_gained)
            VALUES (?, ?, ?, ?, ?)
        """, (test_char_id, "Second Wind", "Regain 1d10 + level hit points", "short_rest", 1))
        
        # Add feats
        cursor.execute("""
            INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
            VALUES (?, ?, ?, ?)
        """, (test_char_id, "Savage Attacker", "background", 1))
        
        cursor.execute("""
            INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
            VALUES (?, ?, ?, ?)
        """, (test_char_id, "Great Weapon Fighting", "class", 1))
        
        # Add weapon masteries
        cursor.execute("""
            INSERT INTO character_weapon_masteries (character_id, weapon_name, mastery_type)
            VALUES (?, ?, ?)
        """, (test_char_id, "Greatsword", "Graze"))
        
        # Add proficiencies
        proficiencies = [
            ("skill", "Athletics"),
            ("skill", "Intimidation"),
            ("weapon", "Simple weapons"),
            ("weapon", "Martial weapons"),
            ("armor", "Light armor"),
            ("armor", "Medium armor"),
            ("armor", "Heavy armor"),
            ("armor", "Shields")
        ]
        
        for prof_type, prof_name in proficiencies:
            cursor.execute("""
                INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
                VALUES (?, ?, ?, ?)
            """, (test_char_id, prof_type, prof_name, "class"))
        
        conn.commit()
        print("✓ Test character created")
    
    # Test loading character features
    print("\nTesting character features loading:")
    
    # Test class features
    cursor.execute("""
        SELECT feature_name, description, usage_type 
        FROM character_features 
        WHERE character_id = ? 
        ORDER BY level_gained, feature_name
    """, (test_char_id,))
    
    features = cursor.fetchall()
    print(f"Class features found: {len(features)}")
    for feature_name, description, usage_type in features:
        print(f"  - {feature_name} ({usage_type}): {description}")
    
    # Test feats
    cursor.execute("""
        SELECT feat_name, feat_source 
        FROM character_feats 
        WHERE character_id = ? 
        ORDER BY feat_source, feat_name
    """, (test_char_id,))
    
    feats = cursor.fetchall()
    print(f"\nFeats found: {len(feats)}")
    for feat_name, feat_source in feats:
        print(f"  - {feat_name} (from {feat_source})")
    
    # Test weapon masteries
    cursor.execute("""
        SELECT weapon_name, mastery_type 
        FROM character_weapon_masteries 
        WHERE character_id = ?
    """, (test_char_id,))
    
    masteries = cursor.fetchall()
    print(f"\nWeapon masteries found: {len(masteries)}")
    for weapon_name, mastery_type in masteries:
        print(f"  - {weapon_name}: {mastery_type}")
    
    # Test proficiencies
    cursor.execute("""
        SELECT proficiency_type, proficiency_name 
        FROM character_proficiencies 
        WHERE character_id = ? 
        ORDER BY proficiency_type, proficiency_name
    """, (test_char_id,))
    
    proficiencies = cursor.fetchall()
    print(f"\nProficiencies found: {len(proficiencies)}")
    
    # Group by type
    prof_by_type = {}
    for prof_type, prof_name in proficiencies:
        if prof_type not in prof_by_type:
            prof_by_type[prof_type] = []
        prof_by_type[prof_type].append(prof_name)
    
    for prof_type, prof_list in prof_by_type.items():
        type_label = prof_type.replace('_', ' ').title()
        print(f"  - {type_label}: {', '.join(prof_list)}")
    
    conn.close()
    print("\n✓ Character features test completed!")

if __name__ == "__main__":
    test_character_features_display()