import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.fighter_abilities import FighterAbilitiesService

def update_all_fighter_resources():
    # Get all Fighter characters
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, level FROM characters WHERE class_id = 'fighter'")
    fighters = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(fighters)} Fighter characters to update:")
    
    # Update each one's resources
    for fighter_id, name, level in fighters:
        print(f"Updating {name} (Level {level})...")
        try:
            # Create separate connection for service
            service = FighterAbilitiesService()
            service.update_fighter_resources_for_level(fighter_id, level)
            print(f"[OK] Updated {name}")
        except Exception as e:
            print(f"[FAIL] Failed to update {name}: {e}")

if __name__ == "__main__":
    update_all_fighter_resources()