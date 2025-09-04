#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('talekeeper.db')
cursor = conn.cursor()

# Find Dwari character
cursor.execute('SELECT id, name FROM characters WHERE name="Dwari"')
char = cursor.fetchone()

if char:
    char_id, char_name = char
    print(f"Character: {char_name} (ID: {char_id})")
    
    # Check character_feats table
    cursor.execute('SELECT feat_name, feat_source FROM character_feats WHERE character_id=?', (char_id,))
    feats = cursor.fetchall()
    print(f"Feats: {feats}")
    
    # Check feature_states table
    cursor.execute('SELECT feature_name, feature_type FROM feature_states WHERE character_id=?', (char_id,))
    features = cursor.fetchall()
    print(f"Features: {features}")
else:
    print("Dwari character not found")

conn.close()