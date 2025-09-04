#!/usr/bin/env python3
"""Debug character loading and feature display."""

import sqlite3

def debug_dwari_character():
    """Debug Dwari's character data loading."""
    
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    # Find Dwari
    cursor.execute('SELECT id, name, class_id, level FROM characters WHERE name="Dwari"')
    char = cursor.fetchone()
    
    if not char:
        print("Dwari character not found")
        return
        
    char_id, name, class_id, level = char
    print(f"Character: {name}")
    print(f"ID: {char_id}")
    print(f"Class: {class_id}")
    print(f"Level: {level}")
    print()
    
    # Check character_data that would be passed to character panel
    print("=== CHARACTER DATA STRUCTURE ===")
    cursor.execute("""
        SELECT id, name, class_id as class_name, level, 
               strength, dexterity, constitution, intelligence, wisdom, charisma
        FROM characters WHERE id = ?
    """, (char_id,))
    
    char_data = cursor.fetchone()
    if char_data:
        columns = [desc[0] for desc in cursor.description]
        char_dict = dict(zip(columns, char_data))
        print("Character data keys:", list(char_dict.keys()))
        print(f"Has 'id' key: {'id' in char_dict}")
        print(f"ID value: {char_dict.get('id')}")
        print()
    
    # Test what the character panel would see
    print("=== FEATURES FROM BOTH TABLES ===")
    
    # Check character_features table (legacy)
    cursor.execute("""
        SELECT feature_name, description, usage_type 
        FROM character_features 
        WHERE character_id = ? 
        ORDER BY level_gained, feature_name
    """, (char_id,))
    
    legacy_features = cursor.fetchall()
    print(f"Legacy character_features: {len(legacy_features)} found")
    for feature in legacy_features:
        print(f"  - {feature[0]}: {feature[1]} ({feature[2]})")
    
    # Check feature_states table (new)
    cursor.execute("""
        SELECT feature_name, feature_type
        FROM feature_states 
        WHERE character_id = ? 
        ORDER BY feature_name
    """, (char_id,))
    
    new_features = cursor.fetchall()
    print(f"\nNew feature_states: {len(new_features)} found")
    for feature in new_features:
        print(f"  - {feature[0]} ({feature[1]})")
    
    # Test the actual lookup logic from character panel
    print("\n=== TESTING CHARACTER PANEL LOGIC ===")
    
    # Simulate the character panel's feature loading
    cursor.execute("""
        SELECT feature_name, description, usage_type 
        FROM character_features 
        WHERE character_id = ? 
        ORDER BY level_gained, feature_name
    """, (char_id,))
    
    class_features = cursor.fetchall()
    print(f"First query (character_features): {len(class_features)} features")
    
    # If empty, check feature_states (like the panel does)
    if not class_features:
        print("No legacy features found, checking feature_states...")
        cursor.execute("""
            SELECT feature_name, feature_type, '' as description
            FROM feature_states 
            WHERE character_id = ? 
            ORDER BY feature_name
        """, (char_id,))
        
        feature_states = cursor.fetchall()
        print(f"Feature_states query: {len(feature_states)} features")
        
        if feature_states:
            print("Would call _get_feature_description() for each:")
            for name, ftype, _ in feature_states:
                print(f"  - {name} ({ftype})")
    
    conn.close()

if __name__ == "__main__":
    debug_dwari_character()