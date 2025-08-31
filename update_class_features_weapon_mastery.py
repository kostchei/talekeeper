#!/usr/bin/env python3
"""
Update class features to add Weapon Mastery feature for D&D 2024 classes.
"""

import sqlite3

def update_class_features():
    """Add Weapon Mastery feature to classes that get it at level 1."""
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # D&D 2024 classes that get Weapon Mastery at level 1
    weapon_mastery_classes = [
        'Fighter',
        'Barbarian', 
        'Rogue',
        'Paladin'
    ]
    
    for class_name in weapon_mastery_classes:
        # Get class ID
        cursor.execute("SELECT id FROM classes WHERE name = ?", (class_name,))
        class_row = cursor.fetchone()
        
        if not class_row:
            print(f"Warning: Class '{class_name}' not found")
            continue
            
        class_id = class_row[0]
        
        # Add Weapon Mastery feature at level 1
        cursor.execute("""
            INSERT OR IGNORE INTO class_features (class_id, level, feature_name)
            VALUES (?, 1, 'Weapon Mastery')
        """, (class_id,))
        
        print(f"Added Weapon Mastery to {class_name} (class_id: {class_id})")
    
    # Also add other core level 1 features while we're here
    class_features_data = {
        'Fighter': [
            'Fighting Style',
            'Second Wind'
        ],
        'Barbarian': [
            'Rage',
            'Unarmored Defense'
        ],
        'Rogue': [
            'Expertise', 
            'Sneak Attack',
            "Thieves' Cant"
        ],
        'Paladin': [
            'Divine Sense',
            'Lay on Hands'
        ]
    }
    
    for class_name, features in class_features_data.items():
        cursor.execute("SELECT id FROM classes WHERE name = ?", (class_name,))
        class_row = cursor.fetchone()
        
        if not class_row:
            continue
            
        class_id = class_row[0]
        
        for feature in features:
            cursor.execute("""
                INSERT OR IGNORE INTO class_features (class_id, level, feature_name)
                VALUES (?, 1, ?)
            """, (class_id, feature))
            
        print(f"Added core features to {class_name}: {', '.join(features)}")
    
    conn.commit()
    conn.close()
    print("\nClass features updated successfully!")

if __name__ == "__main__":
    update_class_features()