#!/usr/bin/env python3
"""
Test script to verify class features system.
"""

import sqlite3
from services.level_up import level_up_service

def test_class_features():
    """Test if class features are being assigned correctly."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Get first character
    cursor.execute("SELECT id, name, level, class_id FROM characters LIMIT 1")
    character = cursor.fetchone()
    
    if not character:
        print("No characters found")
        return
    
    char_id, char_name, char_level, char_class = character
    print(f"Testing character: {char_name} (Level {char_level} {char_class})")
    
    # Check existing class features
    cursor.execute("""
        SELECT feature_name, feature_type, usage_type, description 
        FROM character_features 
        WHERE character_id = ?
    """, (char_id,))
    
    existing_features = cursor.fetchall()
    print(f"\nExisting features ({len(existing_features)}):")
    for feature in existing_features:
        print(f"  - {feature[0]} ({feature[1]}, {feature[2]}): {feature[3]}")
    
    # Check available class features for this class
    cursor.execute("""
        SELECT feature_name, level_required, combat_effect
        FROM class_features_detailed
        WHERE class_name = ? AND level_required <= ?
        ORDER BY level_required
    """, (char_class, char_level))
    
    available_features = cursor.fetchall()
    print(f"\nAvailable {char_class} features for level {char_level}:")
    for feature in available_features:
        print(f"  Level {feature[1]}: {feature[0]} - {feature[2]}")
    
    # Add missing class features
    print(f"\nAdding missing class features...")
    for feature in available_features:
        feature_name = feature[0]
        
        # Check if character already has this feature
        cursor.execute("""
            SELECT 1 FROM character_features
            WHERE character_id = ? AND feature_name = ?
        """, (char_id, feature_name))
        
        if not cursor.fetchone():
            # Add the feature
            cursor.execute("""
                INSERT INTO character_features 
                (character_id, feature_name, feature_type, usage_type, level_gained, description)
                VALUES (?, ?, 'passive', 'permanent', ?, ?)
            """, (char_id, feature_name, feature[1], feature[2]))
            print(f"  Added: {feature_name}")
    
    # Check multi-class levels
    cursor.execute("""
        SELECT class_name, level 
        FROM character_class_levels 
        WHERE character_id = ?
    """, (char_id,))
    
    class_levels = cursor.fetchall()
    if class_levels:
        print(f"\nMulti-class levels:")
        for class_name, level in class_levels:
            print(f"  {class_name}: Level {level}")
    else:
        print(f"\nNo multi-class data found, adding current class...")
        cursor.execute("""
            INSERT INTO character_class_levels (character_id, class_name, level, hit_die_type)
            VALUES (?, ?, ?, ?)
        """, (char_id, char_class, char_level, 8))  # Default to d8 hit die
    
    conn.commit()
    conn.close()
    
    print(f"\nTest completed!")

if __name__ == "__main__":
    test_class_features()