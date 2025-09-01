"""
Test the feat and feature visibility from database.
"""

import sqlite3
import sys
from PyQt6.QtWidgets import QApplication
from character_sheet.character_panel import CharacterPanel

def test_feat_loading():
    """Test that feats and features load correctly from database."""
    # Get a character with feats
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    # Find a character with feats
    cursor.execute("""
        SELECT DISTINCT c.id, c.name 
        FROM characters c 
        JOIN character_feats cf ON c.id = cf.character_id 
        LIMIT 1
    """)
    result = cursor.fetchone()
    
    if not result:
        print("No characters with feats found in database")
        return False
    
    char_id, char_name = result
    print(f"Testing with character: {char_name} (ID: {char_id})")
    
    # Create a minimal Qt app for testing
    app = QApplication(sys.argv)
    panel = CharacterPanel()
    
    # Test the database loading method directly
    feats, features = panel._load_feats_and_features_from_db(char_id)
    
    print(f"Loaded {len(feats)} feats: {feats}")
    print(f"Loaded {len(features)} features: {list(features.keys()) if features else 'None'}")
    
    # Verify feats were loaded
    cursor.execute(
        "SELECT COUNT(*) FROM character_feats WHERE character_id = ?",
        (char_id,)
    )
    expected_feat_count = cursor.fetchone()[0]
    
    conn.close()
    
    if len(feats) == expected_feat_count:
        print(f"[PASS] Feat count matches database ({expected_feat_count})")
        return True
    else:
        print(f"[FAIL] Feat count mismatch - Expected: {expected_feat_count}, Got: {len(feats)}")
        return False

if __name__ == "__main__":
    success = test_feat_loading()
    sys.exit(0 if success else 1)