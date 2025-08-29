"""
Check what characters are saved in the database and their abilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to initialize the database properly first
    from core.database import DatabaseSession, init_database
    from models.character import Character
    from models.items import Item
    from models.game import SaveSlot
    
    print("=== Checking Database Characters ===\n")
    
    # Initialize database if needed
    try:
        init_database()
        print("[+] Database initialized successfully")
    except Exception as e:
        print(f"[!] Database init warning: {e}")
    
    with DatabaseSession() as db:
        # Check save slots
        save_slots = db.query(SaveSlot).all()
        print(f"\nSave Slots: {len(save_slots)}")
        for slot in save_slots:
            print(f"  - Slot {slot.slot_number}: {slot.character_name or 'Empty'}")
            if slot.last_played:
                print(f"    Last played: {slot.last_played}")
        
        # Check characters
        characters = db.query(Character).all()
        print(f"\nCharacters: {len(characters)}")
        for char in characters:
            print(f"\n--- {char.name} ---")
            print(f"  Level: {char.level}")
            print(f"  Race: {char.race.name if char.race else 'Unknown'}")
            print(f"  Class: {char.character_class.name if char.character_class else 'Unknown'}")
            print(f"  HP: {char.current_hit_points}/{char.max_hit_points}")
            print(f"  AC: {char.armor_class}")
            print(f"  Stats: STR {char.strength}, DEX {char.dexterity}, CON {char.constitution}")
            print(f"  Equipped Main Hand: {char.equipment_main_hand or 'None'}")
            if char.equipment_main_hand:
                weapon = db.query(Item).filter_by(id=char.equipment_main_hand).first()
                if weapon:
                    print(f"    Weapon: {weapon.name} ({weapon.damage_dice} {weapon.damage_type})")
        
        # Check available weapons in database
        weapons = db.query(Item).filter_by(item_type='weapon').all()
        print(f"\nAvailable Weapons: {len(weapons)}")
        for weapon in weapons[:5]:  # Show first 5
            print(f"  - {weapon.name}: {weapon.damage_dice} {weapon.damage_type}")
            
except Exception as e:
    print(f"Database error: {e}")
    print("\nTrying alternative approach without relationships...")
    
    # Try simpler approach without problematic relationships
    try:
        import sqlite3
        
        db_path = "talekeeper.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Database tables: {[t[0] for t in tables]}")
            
            # Check characters table
            if 'characters' in [t[0] for t in tables]:
                cursor.execute("SELECT COUNT(*) FROM characters")
                char_count = cursor.fetchone()[0]
                print(f"Characters in database: {char_count}")
                
                if char_count > 0:
                    cursor.execute("SELECT id, name, level, strength, dexterity, constitution, armor_class, current_hit_points, max_hit_points FROM characters LIMIT 3")
                    chars = cursor.fetchall()
                    for char in chars:
                        print(f"  - {char[1]} (Level {char[2]}): STR {char[3]}, DEX {char[4]}, CON {char[5]}")
                        print(f"    HP: {char[7]}/{char[8]}, AC: {char[6]}")
            
            # Check items table
            if 'items' in [t[0] for t in tables]:
                cursor.execute("SELECT COUNT(*) FROM items WHERE item_type='weapon'")
                weapon_count = cursor.fetchone()[0]
                print(f"Weapons in database: {weapon_count}")
                
            conn.close()
        else:
            print(f"Database file {db_path} not found")
            
    except Exception as e2:
        print(f"SQLite error: {e2}")