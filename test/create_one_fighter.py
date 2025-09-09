import sqlite3
import uuid

conn = sqlite3.connect('talekeeper.db')
cursor = conn.cursor()

character_id = str(uuid.uuid4())
print(f"Creating Fighter_1 with ID: {character_id}")

try:
    # Create save slot
    cursor.execute("""
        INSERT OR REPLACE INTO save_slots (id, slot_number, is_occupied, character_name, character_level)
        VALUES (?, ?, 1, ?, ?)
    """, ('21', '21', 'Fighter_1', 1))
    
    # Create character
    cursor.execute("""
        INSERT INTO characters (
            id, name, race_id, class_id, subclass_id, background_id, level, experience_points,
            strength, dexterity, constitution, intelligence, wisdom, charisma,
            hit_points_max, hit_points_current, max_hit_points, current_hit_points, armor_class,
            equipment_main_hand, equipment_off_hand, equipment_armor,
            save_slot_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        character_id, 'Fighter_1', 'human', 'fighter', 'champion', 'soldier',
        1, 0, 16, 14, 14, 10, 12, 8,
        12, 12, 12, 12, 16,
        'Longsword', 'Shield', 'Chain Mail', '21'
    ))
    
    conn.commit()
    print("[OK] Created Fighter_1 successfully")
    
except Exception as e:
    print(f"[FAIL] Error: {e}")
    conn.rollback()
    
finally:
    conn.close()