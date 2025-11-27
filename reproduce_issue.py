
import sys
import os
import json
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(os.getcwd())
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from talekeeper.core.game_engine_sqlite import GameEngineSQLite
from talekeeper.services.unified_level_up import UnifiedLevelUpService
from scripts.character_tools.programmatic_character_creator import ProgrammaticCharacterCreator

def reproduce():
    db_path = "talekeeper_repro.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    # Initialize DB
    engine = GameEngineSQLite(db_path)
    
    # Create a Warlock template
    template = {
        "name": "Zagor_Repro",
        "class": "Warlock",
        "level": 1,
        "background": "Acolyte",
        "species": "Human",
        "ability_scores": {
            "strength": 8,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 16
        },
        "invocations": ["agonizing_blast", "devil_s_sight"],
        "cantrips": ["eldritch_blast", "mage_hand"],
        "spells_known": ["hex", "charm_person"]
    }
    
    print("Creating character...")
    creator = ProgrammaticCharacterCreator(db_path)
    character = creator.create_from_dict(template)
    character_id = character['id']
    print(f"Character created with ID: {character_id}")
    
    # Check invocations in DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\nChecking warlock_invocations table...")
    try:
        cursor.execute("SELECT * FROM warlock_invocations WHERE character_id = ?", (character_id,))
        rows = cursor.fetchall()
        print(f"Rows in warlock_invocations: {len(rows)}")
        for row in rows:
            print(row)
    except sqlite3.OperationalError:
        print("warlock_invocations table does not exist yet.")
        
    print("\nChecking character_features table for invocations...")
    cursor.execute("SELECT feature_name, feature_type FROM character_features WHERE character_id = ?", (character_id,))
    features = cursor.fetchall()
    for f in features:
        if "invocation" in f[0].lower() or "invocation" in f[1].lower():
            print(f"Found feature: {f}")
            
    # Level up to 2
    print("\nLeveling up to 2...")
    level_up_service = UnifiedLevelUpService(db_path)
    result = level_up_service.level_up_character(character_id)
    
    print("\nLevel up result:")
    print(json.dumps(result, indent=2))
    
    if result.get("choices_required"):
        print("\nChoices required!")
        # Here is where we would want to supply choices if we could
    
    conn.close()

if __name__ == "__main__":
    reproduce()
