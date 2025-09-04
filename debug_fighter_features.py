#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('talekeeper.db')
cursor = conn.cursor()

# Find a fighter character
cursor.execute('SELECT id, name FROM characters WHERE class_id="fighter" LIMIT 1')
char = cursor.fetchone()

if char:
    char_id, char_name = char
    print(f"Fighter character: {char_name} (ID: {char_id})")
    
    # Check character_features table
    cursor.execute('SELECT feature_name, usage_type, description FROM character_features WHERE character_id=?', (char_id,))
    features = cursor.fetchall()
    print(f"Features in character_features table: {features}")
    
    # Check feature_states table
    cursor.execute('SELECT feature_name, feature_type, is_active FROM feature_states WHERE character_id=?', (char_id,))
    feature_states = cursor.fetchall()
    print(f"Features in feature_states table: {feature_states}")
    
    # Check character_feats table
    cursor.execute('SELECT feat_name, feat_source FROM character_feats WHERE character_id=?', (char_id,))
    feats = cursor.fetchall()
    print(f"Feats in character_feats table: {feats}")
else:
    print("No fighter character found")

conn.close()